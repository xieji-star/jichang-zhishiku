#!/usr/bin/env python3
"""
MediaCrawler → pyvideotrans 口播稿批量转写对接脚本
====================================================

一句话：
    把 MediaCrawler 采集到的短视频链接，批量转录成口播稿（纯文本）。

链路：
    MediaCrawler 导出（CSV / JSON / JSONL / TXT 链接列表）
        → 本脚本解析链接
        → yt-dlp 下载视频/音频到本地
        → pyvideotrans cli.py --task stt 转录成 SRT 字幕
        → 转成纯文本口播稿 + 汇总 results.csv

用法示例：
    # 处理 MediaCrawler 导出的 CSV（自动识别 video_url / audio_url 字段）
    python mediacrawler_to_pyvideotrans.py -i mediacrawler.csv -o ./koubo_out --pv-root "E:/pyvideotrans"

    # 处理 JSONL
    python mediacrawler_to_pyvideotrans.py -i mediacrawler.jsonl -o ./koubo_out --pv-root "E:/pyvideotrans"

    # 处理纯链接列表 txt（每行一个链接）
    python mediacrawler_to_pyvideotrans.py -i links.txt -o ./koubo_out --pv-root "E:/pyvideotrans"

    # 服务器有 GPU：用中号模型 + 标点恢复 + 中文 + 降噪
    python mediacrawler_to_pyvideotrans.py -i mediacrawler.csv -o ./koubo_out --pv-root /opt/pyvideotrans --model-name medium --cuda --fix-punc

    # 只下载视频不转写（下载完用 pyvideotrans WebUI 手动处理，适合先用小批验证）
    python mediacrawler_to_pyvideotrans.py -i links.txt -o ./koubo_out --pv-root "E:/pyvideotrans" --download-only

依赖：
    - Python 3.8+
    - yt-dlp        （pip install yt-dlp）
    - pyvideotrans  （官方安装包，需已配置好识别渠道，如 Faster-Whisper）

说明：
    - 幂等 / 断点续跑：已处理过的链接记录在 <out>/results.csv，重复运行自动跳过。
    - pyvideotrans 命令行脚本名为 cli.py，任务 --task stt（语音转录）。参数请按你的版本核对：
      python cli.py --task stt --name "<音视频绝对路径>" --model_name <模型> --detect_language zh-cn [--cuda] [--fix_punc]
    - 默认识别渠道 recogn_type=0（Faster-Whisper），模型默认 small（无 GPU 时快；有 GPU 建议 medium / large-v3）。
    - 防风控：默认每条之间休眠 1 秒，可用 --delay 调整。
"""

import argparse
import csv
import hashlib
import json
import logging
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

log = logging.getLogger("mc2pv")

# MediaCrawler 导出中常见的链接 / 本地路径字段（按优先级）
URL_FIELDS = ("video_url", "audio_url", "video_download_url", "download_url", "url", "video", "audio")
LOCAL_FIELDS = ("video_path", "local_path", "file_path", "path")

# ---------- 输入解析 ----------

def load_records(input_path: Path) -> list:
    """读取 MediaCrawler 导出的 CSV / JSON / JSONL / 纯 txt 链接列表。"""
    suffix = input_path.suffix.lower()
    records = []
    if suffix == ".csv":
        with open(input_path, encoding="utf-8-sig") as f:
            records = list(csv.DictReader(f))
    elif suffix == ".json":
        data = json.loads(input_path.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict):
            for k in ("list", "data", "records", "items"):
                if isinstance(data.get(k), list):
                    data = data[k]
                    break
        if isinstance(data, list):
            records = data
        else:
            raise ValueError("JSON 内容不是列表或包含列表的对象")
    elif suffix in (".jsonl", ".ndjson"):
        for line in input_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
    elif suffix == ".txt":
        for line in input_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line.startswith("http"):
                records.append({"video_url": line})
    else:
        raise ValueError(f"不支持的文件类型: {suffix}")
    log.info("读取到 %d 条记录", len(records))
    return records


def extract_target(record) -> tuple:
    """从一条记录里提取 (类型, 目标)。类型: url / file / None。"""
    if not isinstance(record, dict):
        return None, None
    for f in URL_FIELDS:
        v = record.get(f)
        if v and isinstance(v, str) and v.startswith("http"):
            return "url", v.strip()
    for f in LOCAL_FIELDS:
        v = record.get(f)
        if v and isinstance(v, str):
            p = Path(v)
            if p.exists():
                return "file", str(p)
    return None, None


# ---------- 下载 ----------

def download_with_ytdlp(url: str, media_dir: Path, file_id: str, cookies: Optional[str]) -> Optional[str]:
    """用 yt-dlp 下载视频/音频到 media_dir，返回文件路径。"""
    out_tpl = str(media_dir / f"{file_id}.%(ext)s")
    cmd = [
        "yt-dlp", "-f", "bv*+ba/b",
        "-o", out_tpl, "--no-playlist", "--no-overwrites",
        "--retries", "3", "--socket-timeout", "30",
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    cmd.append(url)
    log.info("下载: %s", url)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=600)
    except FileNotFoundError:
        log.error("未找到 yt-dlp，请先安装：pip install yt-dlp")
        return None
    except subprocess.TimeoutExpired:
        log.error("下载超时(600s): %s", url)
        return None
    if proc.returncode != 0:
        log.error("下载失败: %s\n%s", url, proc.stderr[-600:])
        return None
    for f in media_dir.glob(f"{file_id}.*"):
        if f.is_file() and f.suffix.lower() in (
            ".mp4", ".mkv", ".webm", ".mov", ".flv",
            ".mp3", ".m4a", ".wav", ".aac", ".opus", ".wma",
        ):
            return str(f)
    log.warning("未找到下载产物: %s", url)
    return None


# ---------- 转写（调用 pyvideotrans） ----------

def run_pyvideotrans_stt(video_path: str, pv_cli: Path, model: str, lang: str,
                         cuda: bool, fix_punc: bool, remove_noise: bool) -> Optional[Path]:
    """调用 pyvideotrans cli.py --task stt 转录，返回生成的 srt 路径。"""
    cmd = [
        sys.executable, str(pv_cli), "--task", "stt", "--name", str(video_path),
        "--model_name", model, "--detect_language", lang, "--recogn_type", "0",
    ]
    if cuda:
        cmd.append("--cuda")
    if fix_punc:
        cmd.append("--fix_punc")
    if remove_noise:
        cmd.append("--remove_noise")
    log.info("转录: %s", video_path)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=3600)
    except subprocess.TimeoutExpired:
        log.error("转录超时(3600s): %s", video_path)
        return None
    if proc.returncode != 0:
        log.error("pyvideotrans 转录失败: %s\n%s", video_path, proc.stderr[-800:])
        return None
    # 查找生成的 srt：优先视频同目录同名 → 视频目录/tmp → pyvideotrans 根目录/tmp/<stem>，按文件名匹配避免错配
    video = Path(video_path)
    stem = video.stem
    search_dirs = [video.parent, video.parent / "tmp", pv_cli.parent / "tmp"]
    for d in search_dirs:
        if not d.is_dir():
            continue
        exact = d / f"{stem}.srt"
        if exact.exists():
            return exact
        sub = d / stem
        if sub.is_dir() and (sub / f"{stem}.srt").exists():
            return sub / f"{stem}.srt"
        for f in d.glob("*.srt"):
            if stem in f.name:
                return f
    log.warning("未找到转录生成的 srt: %s", video_path)
    return None


def srt_to_text(srt_path: Path) -> str:
    """把 SRT 字幕转成纯文本口播稿（去掉序号、时间轴、空行、常见标签）。"""
    lines = srt_path.read_text(encoding="utf-8-sig").splitlines()
    texts = []
    for line in lines:
        line = line.strip()
        # 跳过空行、序号行、时间轴行
        if not line or line.isdigit() or "-->" in line:
            continue
        # 去掉 <font> 等内联标签与 {\an8} 定位标签
        line = re.sub(r"<[^>]+>|{\\an\d+}", "", line).strip()
        if line:
            texts.append(line)
    return "\n".join(texts)


# ---------- 主流程 ----------

def main():
    parser = argparse.ArgumentParser(description="MediaCrawler → pyvideotrans 口播稿批量转写")
    parser.add_argument("-i", "--input", required=True, help="MediaCrawler 导出的 CSV/JSON/JSONL/TXT 链接列表")
    parser.add_argument("-o", "--output", default="koubo_out", help="输出目录（默认 koubo_out）")
    parser.add_argument("--pv-root", default=None, help="pyvideotrans 安装根目录（含 cli.py）；--download-only 模式可省略")
    parser.add_argument("--model-name", default="small", help="ASR 模型：tiny/small/base/medium/large-v2/large-v3（默认 small）")
    parser.add_argument("--detect-language", default="zh-cn", help="源语言（默认 zh-cn）")
    parser.add_argument("--cuda", action="store_true", help="启用 GPU (CUDA) 加速")
    parser.add_argument("--fix-punc", action="store_true", help="恢复标点符号")
    parser.add_argument("--remove-noise", action="store_true", help="启用音频降噪")
    parser.add_argument("--download-only", action="store_true", help="只下载视频，不转写")
    parser.add_argument("--cookies", default=None, help="yt-dlp cookies 文件（可选，处理需登录的视频时用）")
    parser.add_argument("--limit", type=int, default=0, help="最多处理 N 条（0=不限，默认 0）")
    parser.add_argument("--delay", type=float, default=1.0, help="每条之间休眠秒数（默认 1.0，防风控）")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    input_path = Path(args.input)
    out_dir = Path(args.output)
    media_dir = out_dir / "media"
    sub_dir = out_dir / "subtitles"
    script_dir = out_dir / "scripts"
    results_csv = out_dir / "results.csv"
    for d in (media_dir, sub_dir, script_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 校验 pyvideotrans 环境（--download-only 模式不需要）
    pv_cli = None
    if not args.download_only:
        if not args.pv_root:
            parser.error("非 --download-only 模式必须提供 --pv-root")
        pv_cli = Path(args.pv_root) / "cli.py"
        if not pv_cli.exists():
            parser.error(f"找不到 pyvideotrans cli.py: {pv_cli}")

    records = load_records(input_path)

    # 断点续跑：读取已处理 id
    done = set()
    if results_csv.exists():
        with open(results_csv, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                if "id" in row:
                    done.add(row["id"])

    processed = 0
    with open(results_csv, "a", encoding="utf-8", newline="") as rf:
        writer = csv.writer(rf)
        if results_csv.stat().st_size == 0:
            writer.writerow(["id", "kind", "target", "title", "status", "script_path", "error"])

        for idx, rec in enumerate(records, 1):
            kind, target = extract_target(rec)
            if not target:
                log.warning("[%d] 跳过（无可用链接/路径）: %s", idx, str(rec)[:80])
                continue
            file_id = hashlib.md5(target.encode("utf-8")).hexdigest()[:12]
            if file_id in done:
                log.info("[%d] 已处理，跳过: %s", idx, target)
                continue
            title = str(rec.get("title", ""))[:60] if isinstance(rec, dict) else ""

            status, script_path, err = "ok", "", ""
            try:
                if kind == "url":
                    video_path = download_with_ytdlp(target, media_dir, file_id, args.cookies)
                else:
                    video_path = target
                if not video_path:
                    status, err = "download_failed", "yt-dlp 未返回文件"
                elif args.download_only:
                    status = "downloaded"
                else:
                    srt = run_pyvideotrans_stt(
                        video_path, pv_cli, args.model_name,
                        args.detect_language, args.cuda, args.fix_punc, args.remove_noise,
                    )
                    if srt:
                        txt_path = script_dir / f"{file_id}.txt"
                        txt_path.write_text(srt_to_text(srt), encoding="utf-8")
                        srt_target = sub_dir / f"{file_id}.srt"
                        if srt_target.exists():
                            srt_target.unlink()
                        shutil.move(str(srt), str(srt_target))
                        script_path = str(txt_path)
                    else:
                        status, err = "stt_failed", "pyvideotrans 未生成 srt"
            except Exception as e:  # noqa: BLE001
                status, err = "error", str(e)[:200]

            writer.writerow([file_id, kind, target, title, status, script_path, err])
            rf.flush()
            done.add(file_id)
            processed += 1
            log.info("[%d] %s: %s -> %s", idx, status, target, script_path or err or "")
            if args.limit and processed >= args.limit:
                log.info("达到 --limit %d，停止。", args.limit)
                break
            if idx < len(records) and args.delay:
                time.sleep(args.delay)

    log.info("完成。处理 %d 条新记录，结果见 %s", processed, results_csv)


if __name__ == "__main__":
    main()
