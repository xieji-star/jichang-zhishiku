#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF 压缩+拆分脚本：修复 Read 工具读取超限（Request too large）的 PDF。
流程: 备份原文件 -> 重渲染(默认 1120px / JPEG q90) -> 按页拆分成 原名_第N部分.pdf -> 验证每卷渲染体积。
用法: python pdf_fix_split.py <pdf路径> [--width 1120] [--quality 90] [--pages 7] [--backup-dir <目录>]
安全线: 单卷 1x 渲染 PNG <= 10MB (base64 后 <= 13MB, 对 32MB 请求上限留足余量)。
依赖: PyMuPDF (pip install pymupdf)
"""
import sys
import os
import shutil
import argparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import fitz  # PyMuPDF

MB = 1048576
DEFAULT_BACKUP = r"已整理好的文件/知识库报错日志/原始文件备份"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="源 PDF 路径")
    ap.add_argument("--width", type=int, default=1120, help="重渲染目标宽度 px (默认 1120)")
    ap.add_argument("--quality", type=int, default=90, help="JPEG 质量 (默认 90)")
    ap.add_argument("--pages", type=int, default=7, help="每卷页数 (默认 7)")
    ap.add_argument("--backup-dir", default=DEFAULT_BACKUP, help="备份目录")
    ap.add_argument("--no-backup", action="store_true", help="跳过备份（不推荐）")
    args = ap.parse_args()

    src = args.src
    if not os.path.exists(src):
        print(f"文件不存在: {src}")
        sys.exit(1)

    # 1) 备份原文件
    if args.no_backup:
        print("[1/4] 跳过备份 (--no-backup)")
    else:
        os.makedirs(args.backup_dir, exist_ok=True)
        bak = os.path.join(args.backup_dir, os.path.basename(src))
        if not os.path.exists(bak):
            shutil.copy2(src, bak)
            print(f"[1/4] 备份原文件 -> {bak}")
        else:
            print(f"[1/4] 备份已存在，跳过: {bak}")

    # 2) 重渲染全部页面
    doc = fitz.open(src)
    zoom = args.width / doc[0].rect.width
    pages = []
    for page in doc:
        pix = page.get_pixmap(
            matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB, alpha=False
        )
        pages.append((pix.tobytes("jpeg", jpg_quality=args.quality), page.rect))
    n = len(pages)
    print(f"[2/4] 重渲染完成: {n} 页, 宽 {args.width}px, JPEG 质量 {args.quality}")

    # 3) 拆分并输出
    base, _ = os.path.splitext(src)
    chunks = [range(i, min(i + args.pages, n)) for i in range(0, n, args.pages)]
    out_files = []
    for i, rng in enumerate(chunks, 1):
        out = fitz.open()
        for idx in rng:
            jpg, rect = pages[idx]
            np_ = out.new_page(width=rect.width, height=rect.height)
            np_.insert_image(rect, stream=jpg)
        out_path = f"{base}_第{i}部分.pdf"
        out.save(out_path, garbage=4, deflate=True)
        out.close()
        out_files.append(out_path)
    print(f"[3/4] 拆分完成: {len(chunks)} 卷")

    # 4) 验证每卷渲染体积
    print("[4/4] 分卷验证 (安全线: 1x 渲染 PNG <= 10MB):")
    ok = True
    for p in out_files:
        d = fitz.open(p)
        t1 = sum(
            len(d[j].get_pixmap(matrix=fitz.Matrix(1, 1)).tobytes("png"))
            for j in range(len(d))
        )
        mb = t1 / MB
        b64 = mb * 4 / 3
        flag = "✅" if mb <= 10 else "❌ 超安全线, 需减小 --pages"
        if mb > 10:
            ok = False
        print(
            f"  {os.path.basename(p)}: {len(d)}页, {os.path.getsize(p)/MB:.1f}MB, "
            f"1x渲染 {mb:.1f}MB (base64 ~{b64:.1f}MB) {flag}"
        )
        d.close()
    doc.close()

    print("完成。")
    if ok:
        print("✅ 所有分卷在安全线内，Read 工具可正常读取。")
    else:
        print("⚠️ 存在超安全线的分卷，请减小 --pages 后重跑。")
    print("如需还原原文件，从备份目录复制回原位置。")


if __name__ == "__main__":
    main()
