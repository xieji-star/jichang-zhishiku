"""
飞书消息监听服务 v2.0.0 (Lark Message Listener)
================================================
通过 lark-cli event consume 监听飞书 IM 消息，
支持多轮对话、会话状态管理、智能意图理解。

主要改进：
- 接收文件后不立即处理，先询问用户意图和存放位置
- 通过多轮对话厘清用户需求，支持追问
- 支持自然语言控制知识库操作（创建/编辑笔记、搜索、调用 skill 等）

架构:
  飞书 → lark-cli event consume → 本服务 → Claude CLI → Obsidian Vault
                                        ↓
                                 lark-cli im send (回复用户)

会话状态机:
  IDLE → (收到文件) → AWAITING_INSTRUCTION → (用户说明意图) → CLARIFYING/PROCESSING
  IDLE → (已知命令) → PROCESSING → IDLE
  AWAITING_INSTRUCTION → (取消) → IDLE
  CLARIFYING → (信息齐全) → PROCESSING → IDLE
  CLARIFYING → (取消) → IDLE
  PROCESSING → (用户新消息) → 提示等待
"""

import json
import logging
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

# ★ 按需导入 PyMuPDF（PDF 预提取），加速后续处理
try:
    import fitz
    HAS_PDF_SUPPORT = True
except ImportError:
    HAS_PDF_SUPPORT = False
    pass

# ============================================================
# 配置加载
# ============================================================

def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        print(f"[错误] 配置文件不存在: {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()

# ============================================================
# 双机自适应路径解析（公司电脑 / 私人电脑并存）
# 配置文件保留原电脑(asus)路径；本机若不存在则自动查找替代路径，
# 两套环境互不干扰，任一台电脑均可直接启动服务。
# ============================================================

def _resolve_vault_root() -> str:
    """Vault 根目录：优先使用配置路径，否则遍历所有盘符查找同名目录"""
    cfg_root = CONFIG.get("vault", {}).get("root_path", "")
    if cfg_root and os.path.isdir(cfg_root):
        return cfg_root
    vault_name = os.path.basename(cfg_root) if cfg_root else "积昌的知识库 - 副本"
    if hasattr(os, "listdrives"):
        for drive in os.listdrives():  # Windows: ['C:\\', 'D:\\', ...]
            cand = os.path.join(drive, vault_name)
            if os.path.isdir(cand):
                return cand
    return cfg_root


def _resolve_lark_cli() -> str:
    """lark-cli 可执行文件：旧电脑路径 → 本机 npm 全局目录 → PATH"""
    legacy = r"C:\Users\asus\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
    candidates = [legacy]
    npm_dir = Path.home() / "AppData" / "Roaming" / "npm"
    candidates.append(str(npm_dir / "node_modules" / "@larksuite" / "cli" / "bin" / "lark-cli.exe"))
    for c in candidates:
        if os.path.isfile(c):
            return c
    found = shutil.which("lark-cli")
    if found:
        return found
    return legacy  # 兜底返回原路径，报错信息更明确


def _resolve_claude_cli() -> str:
    """claude CLI 可执行文件：配置路径 → PATH 中的 claude"""
    cfg_path = CONFIG.get("claude", {}).get("cli_path", "")
    if cfg_path and os.path.isfile(cfg_path):
        return cfg_path
    found = shutil.which("claude")
    if found:
        return found
    return cfg_path or "claude"


# 启动时解析一次，全局生效
LARK_CLI_PATH = _resolve_lark_cli()
CONFIG.setdefault("vault", {})["root_path"] = _resolve_vault_root()
CONFIG.setdefault("claude", {})["cli_path"] = _resolve_claude_cli()

# ============================================================
# 部署角色标记（公司电脑 / 自用电脑）
# 自动检测当前机器身份，并同步维护「部署标记.txt」。
# 知识库在两台电脑间自动同步，标记文件内容会被互相同步覆盖，
# 因此每次启动时根据本机身份自动纠正，保证每台电脑看到的
# 标记永远是「当前这台电脑」对应的角色。
# ============================================================

def _detect_deployment() -> str:
    """检测当前机器部署角色: 自用电脑(asus) → '自己用'，公司电脑(PC) → '公司用'"""
    username = os.environ.get("USERNAME", "").lower()
    if username == "asus":
        return "自己用"
    if username == "pc":
        return "公司用"
    # 兜底：旧电脑用户目录存在则视为自用电脑
    if os.path.isdir(r"C:\Users\asus"):
        return "自己用"
    return "公司用"


DEPLOY_ROLE = _detect_deployment()
DEPLOY_TAG_FILE = Path(__file__).parent / "部署标记.txt"


def sync_deploy_tag() -> None:
    """同步部署标记文件（本机身份优先，覆盖同步过来的异机标记）"""
    content = f"本机部署角色：{DEPLOY_ROLE}\n"
    try:
        if not DEPLOY_TAG_FILE.exists() or DEPLOY_TAG_FILE.read_text(encoding="utf-8") != content:
            DEPLOY_TAG_FILE.write_text(content, encoding="utf-8")
            logger.info(f"📌 部署标记已更新: {DEPLOY_ROLE}")
        else:
            logger.info(f"📌 当前部署: {DEPLOY_ROLE}")
    except Exception as e:
        logger.warning(f"部署标记写入失败: {e}")

# ============================================================
# 日志配置
# ============================================================

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "lark-service.log", encoding="utf-8"),
        logging.StreamHandler(stream=sys.stdout),
    ],
)
logger = logging.getLogger("lark-service")

# ============================================================
# 全局状态
# ============================================================

task_queue: queue.Queue = queue.Queue()
is_processing = False
processing_lock = threading.Lock()
last_received_file: Optional[dict] = None
event_consumer_process: Optional[subprocess.Popen] = None
event_consumer_ready = threading.Event()
processed_message_ids: set = set()
processed_ids_lock = threading.Lock()
watchdog_stop_event = threading.Event()
admin_stop_event = threading.Event()

# ★ 管理员指令文件路径（供 admin.py 远程控制）
ADMIN_STATE_PATH = Path(__file__).parent / "admin_state.json"

# ★ 接管模式内存缓存（防止因文件损坏/并发写入导致模式"丢失"）
_cached_mode = "manual"
_mode_cache_lock = threading.Lock()

# ============================================================
# 会话管理（多轮对话）
# ============================================================

sessions: dict = {}
sessions_lock = threading.Lock()
SESSION_TIMEOUT = 30 * 60       # 30 分钟无活动自动清理
SESSION_CLEANUP_INTERVAL = 300  # 清理检查间隔（5分钟）


def get_or_create_session(sender_id: str, chat_id: str) -> dict:
    """获取或创建用户的会话记录"""
    with sessions_lock:
        now = time.time()
        if sender_id not in sessions:
            sessions[sender_id] = {
                "sender_id": sender_id,
                "chat_id": chat_id,
                "state": "IDLE",
                "pending_file": None,        # {"path": str, "name": str, "message_id": str}
                "context": {
                    "storage_path": None,    # 存放路径
                    "note_name": None,       # 笔记名称
                    "intent": None,          # organize / summarize / extract / search / skill
                    "custom_instruction": None,  # 用户原始指令
                    "skill_name": None,      # 指定的 skill 名称
                },
                "awaiting_field": None,      # 当前正在追问的字段名
                "conversation_count": 0,     # 当前对话轮次
                "last_activity": now,
            }
            logger.info(f"🆕 创建新会话: sender={sender_id}")
        else:
            sessions[sender_id]["last_activity"] = now
            sessions[sender_id]["chat_id"] = chat_id
        return sessions[sender_id]


def update_session_activity(sender_id: str):
    """更新会话活动时间戳"""
    with sessions_lock:
        if sender_id in sessions:
            sessions[sender_id]["last_activity"] = time.time()


def reset_session(sender_id: str):
    """将会话重置为 IDLE 状态，清除临时数据"""
    with sessions_lock:
        if sender_id in sessions:
            sessions[sender_id].update({
                "state": "IDLE",
                "pending_file": None,
                "context": {
                    "storage_path": None,
                    "note_name": None,
                    "intent": None,
                    "custom_instruction": None,
                    "skill_name": None,
                },
                "awaiting_field": None,
                "conversation_count": 0,
                "last_activity": time.time(),
            })
            logger.info(f"🔄 重置会话: sender={sender_id}")


def cleanup_stale_sessions():
    """后台线程：定期清理过期会话"""
    logger.info("🧹 会话清理线程已启动")
    while True:
        time.sleep(SESSION_CLEANUP_INTERVAL)
        now = time.time()
        stale_count = 0
        with sessions_lock:
            stale_ids = [
                sid for sid, s in sessions.items()
                if now - s["last_activity"] > SESSION_TIMEOUT
            ]
            for sid in stale_ids:
                del sessions[sid]
                stale_count += 1
        if stale_count > 0:
            logger.info(f"🧹 清理了 {stale_count} 个过期会话（剩余 {len(sessions)} 个）")


def get_session_state(sender_id: str) -> str:
    """获取会话状态（线程安全）"""
    with sessions_lock:
        if sender_id in sessions:
            return sessions[sender_id]["state"]
        return "IDLE"


# ============================================================
# 辅助函数
# ============================================================

def lark_cli(args: list, timeout: int = 120, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    """运行 lark-cli 命令并返回结果"""
    # ★ 直接使用 lark-cli.exe 而非 .cmd 批处理，
    #   避免 Windows cmd.exe 解析 --content 参数时截断或错误解析
    #   路径由 LARK_CLI_PATH 自适应解析（兼容双机环境）
    cmd_path = LARK_CLI_PATH
    cmd = [cmd_path] + args
    logger.debug(f"执行: {' '.join(str(a) for a in cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
        )
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"lark-cli 命令超时: {' '.join(cmd)}")
        raise
    except FileNotFoundError:
        logger.error("找不到 lark-cli 命令")
        raise


def send_lark_message(chat_id: str, content: str) -> bool:
    """通过飞书 API 发送文本消息

    ★ 使用 --content 传递 JSON 而非 --text，
      避免 Windows cmd 处理换行符/特殊字符时截断内容的问题。
    """
    try:
        # 用 json.dumps 正确编码换行和特殊字符
        content_json = json.dumps({"text": content}, ensure_ascii=False)
        result = lark_cli([
            "im", "+messages-send",
            "--chat-id", chat_id,
            "--content", content_json,
            "--as", "bot",
        ])
        if result.returncode == 0:
            logger.info(f"已发送回复消息到 chat_id={chat_id}")
            return True
        else:
            logger.error(f"发送消息失败: {result.stderr[:200]}")
            return False
    except Exception as e:
        logger.error(f"发送消息异常: {e}")
        return False


def download_lark_file(message_id: str, file_key: str,
                       vault_root: str, relative_dir: str, file_name: str) -> Optional[str]:
    """通过 lark-cli 下载文件

    ★ lark-cli 不接受绝对路径的 --output 参数，
      因此改为从 Vault 根目录传入相对路径，并设置 cwd=vault_root。
    """
    try:
        # 确保保存目录存在
        save_dir = Path(vault_root) / relative_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        # 使用相对路径（lark-cli 禁止绝对路径）
        relative_path = str(Path(relative_dir) / file_name)

        result = lark_cli(
            [
                "im", "+messages-resources-download",
                "--message-id", message_id,
                "--file-key", file_key,
                "--type", "file",
                "--output", relative_path,
                "--as", "bot",
            ],
            cwd=vault_root,
        )
        if result.returncode == 0:
            full_path = str(save_dir / file_name)
            # 检查文件是否已下载（先用预期路径）
            if Path(full_path).exists():
                logger.info(f"文件已下载: {full_path}")
                return full_path
            # 可能 lark-cli 用了 Content-Disposition 的文件名
            for f in save_dir.iterdir():
                if f.is_file():
                    logger.info(f"文件已下载(自动命名): {f}")
                    return str(f)
            return full_path
        else:
            logger.error(f"下载文件失败: {result.stderr[:300]}")
            return None
    except Exception as e:
        logger.error(f"下载文件异常: {e}")
        return None


# ============================================================
# Prompt 生成
# ============================================================

def generate_claude_prompt(msg_type: str, msg_data: dict,
                           file_path: Optional[str] = None,
                           file_name: Optional[str] = None) -> str:
    """生成 Claude CLI 的 prompt（用于 IDLE 状态的已知命令）"""
    vault_config = CONFIG["vault"]
    default_dir = vault_config["default_output_dir"]
    content = msg_data.get("content", "").strip()
    from_user = msg_data.get("sender_id", "未知用户")
    chat_id = msg_data.get("chat_id", "")

    if msg_type == "text":
        # ======== 整理笔记 ========
        if content.startswith("整理笔记") or content.startswith("整理文件"):
            parts = content.replace("整理笔记", "").replace("整理文件", "").strip().split()
            path = parts[0] if len(parts) > 0 else default_dir
            name = parts[1] if len(parts) > 1 else "未命名笔记"

            if file_path:
                return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

请使用 meeting-summary skill 处理以下文件：
- 文件路径: {file_path}
- 存储路径: {default_dir}/{path}/
- 笔记名称: {name}
- 内容来源: 飞书文件

Step 0 的三个前置问题已由用户在飞书消息中回答，请直接使用上述信息，无需再询问。
处理完成后请将文件写入磁盘，并简要回复处理结果（100字以内）。"""
            else:
                return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

用户发送了"整理笔记"命令但没有附带文件。最近也没有收到文件。
请回复用户：请先发送需要整理的文件（PDF/文档），然后再发送"整理笔记 [文件夹名] [笔记名称]"命令。
回复时要简短（50字以内）。"""

        # ======== 帮助 ========
        elif content in ("/帮助", "帮助", "help", "/help"):
            return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

用户请求帮助。请生成飞书机器人的帮助信息，说明支持的能力：
1. 📎 发送文件 → 自动保存到知识库
2. 📝 "整理笔记 [文件夹] [名称]" → 整理最近收到的文件
3. 🔍 "/搜索 [关键词]" → 搜索知识库
4. 📋 "总结 [内容]" → 直接总结一段文字
5. 💬 直接发送自然语言指令（例如"帮我把这个PDF整理成笔记"）
6. 🎯 支持调用各种 skill

回复要简洁清晰（200字以内），格式适合飞书阅读。"""

        # ======== 搜索 ========
        elif content.startswith("/搜索") or content.startswith("搜索"):
            keyword = content.replace("/搜索", "").replace("搜索", "").strip()
            if not keyword:
                return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

用户搜索关键词为空。
请回复用户：请在"搜索"后面附带要搜索的关键词，例如"搜索 面试技巧"。
回复要简短（50字以内）。"""
            return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

用户搜索关键词: {keyword}
请在 Vault 中搜索相关内容（使用 Grep 工具搜索 "{default_dir}/" 目录），
将搜索结果整理成简要列表回复给用户。每项附带文件路径。回复在 200 字以内。"""

        # ======== 总结 ========
        elif content.startswith("总结") or content.startswith("总结："):
            text_content = content.replace("总结", "").replace("总结：", "").strip()
            if text_content:
                return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

用户要求总结以下内容：
{text_content}

请用简洁的语言总结这段内容（200字以内），直接回复给用户。不需要写入 Vault。"""
            else:
                return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

用户发送了"总结"命令但没有附带内容。
请回复用户：请在"总结"后面附带需要总结的文字内容。
回复要简短（50字以内）。"""

        else:
            # ======== 自然语言指令 ========
            return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

用户消息: {content}

请理解用户意图并执行。用户可能想要：
- 整理笔记 / 处理文件（如果最近有上传文件）
- 搜索知识库
- 创建或编辑笔记
- 调用某个 skill
- 询问关于知识库的问题

处理完成后简要回复结果（200字以内），并将任何生成的笔记写入 Vault。"""

    elif msg_type == "file":
        # ======== 文件消息（用于 IDLE 状态下收到文件后的直接处理，现在已转由会话管理） ========
        origin_name = file_name or msg_data.get("content", "未命名文件")
        note_name = Path(origin_name).stem

        return f"""🔴 自动化任务 — 来自飞书（用户: {from_user}）

收到文件: {origin_name}
文件路径: {file_path}

用户未提供额外说明。请自动处理此文件：
1. 使用 Read 工具读取文件内容
2. 使用 meeting-summary skill 整理为结构化笔记
3. 笔记存储路径: {default_dir}/{note_name}/
4. 笔记名称: {note_name}

直接执行，无需询问用户。处理完成后写入磁盘并简要回复结果（100字以内）。"""

    return f"收到来自飞书的未知类型消息: {msg_type}"


def build_session_prompt(session: dict, user_message: str = "") -> str:
    """从会话上下文中构建执行 prompt（用于多轮对话后执行）"""
    sender_id = session["sender_id"]
    pending_file = session.get("pending_file")
    context = session.get("context", {})
    vault_config = CONFIG["vault"]
    default_dir = vault_config["default_output_dir"]

    msg = user_message or context.get("custom_instruction", "")

    lines = [f"🔴 自动化任务 — 来自飞书（用户: {sender_id}）"]

    if pending_file:
        file_path = pending_file['path']
        file_name = pending_file['name']
        lines.append(f"\n收到文件: {file_name}")
        lines.append(f"文件路径: {file_path}")

        # ★ 预提取 PDF 文本，大幅加速处理（避免 Claude CLI 启动后花时间读 PDF）
        pdf_extracted_text = ""
        if file_name.lower().endswith('.pdf') and HAS_PDF_SUPPORT:
            try:
                doc = fitz.open(file_path)
                texts = []
                for i in range(doc.page_count):
                    text = doc[i].get_text('text')
                    if text.strip():
                        texts.append(f"=== Page {i+1} ===\n{text}")
                doc.close()
                if texts:
                    pdf_extracted_text = "\n\n".join(texts)
                    if len(pdf_extracted_text) > 80000:
                        pdf_extracted_text = pdf_extracted_text[:80000] \
                            + "\n\n...（内容过长已截断，保留前 80000 字符）"
                    logger.info(f"📄 PDF 预提取完成: {file_name}, "
                                f"{len(texts)} 页, {len(pdf_extracted_text)} 字符")
            except Exception as e:
                logger.warning(f"PDF 预提取失败（将交给 Claude 处理）: {e}")

        if pdf_extracted_text:
            lines.append(f"\n以下是 PDF 文件内容（预提取）：\n\n{pdf_extracted_text}")

    if msg:
        lines.append(f"\n用户指令: {msg}")

    storage_path = context.get("storage_path")
    note_name = context.get("note_name")
    intent = context.get("intent")
    skill_name = context.get("skill_name")

    if storage_path:
        # 如果是相对路径，拼上 default_dir
        if not storage_path.startswith(default_dir):
            storage_path = f"{default_dir}/{storage_path}"
        lines.append(f"存储路径: {storage_path}")
    if note_name:
        lines.append(f"笔记名称: {note_name}")
    if intent:
        intent_desc = {
            "organize": "整理成结构化笔记（使用 meeting-summary skill）",
            "summarize": "总结内容并回复",
            "extract": "提取关键信息",
            "search": "搜索相关笔记",
        }
        lines.append(f"意图: {intent_desc.get(intent, intent)}")
    if skill_name:
        lines.append(f"指定 Skill: {skill_name}")

    if pending_file:
        has_pdf_text = "以下是 PDF 文件内容（预提取）" in lines[-1] if lines else False
        if has_pdf_text:
            lines.append("""
用户通过飞书聊天控制知识库。请根据以上信息处理此文件。
⚠️ 文件内容已在上方预提取，直接使用即可，无需再用 Read 工具。
- 如为整理笔记，使用 meeting-summary skill（直接使用已提取的文本）
- 如为总结/提取，直接处理并回复结果
- 如为其他操作，按用户指令执行

完成后将生成的笔记写入磁盘，简要回复用户（200字以内）。""")
        else:
            lines.append("""
用户通过飞书聊天控制知识库。请根据以上信息处理此文件。
- 使用 Read 工具读取文件内容
- 如为整理笔记，使用 meeting-summary skill
- 如为总结/提取，直接处理并回复结果
- 如为其他操作，按用户指令执行

完成后将生成的笔记写入磁盘，简要回复用户（200字以内）。""")
    else:
        lines.append("""
用户通过飞书聊天控制知识库。请根据以上指令执行操作。
可能包括：创建/编辑笔记、搜索内容、调用 skill、回答知识库问题等。

完成后将结果写入磁盘（如需），简要回复用户（200字以内）。""")

    return "\n".join(lines)


# ============================================================
# Claude CLI 执行
# ============================================================

def run_claude_task(prompt: str) -> str:
    """调用 Claude CLI 执行任务"""
    vault_root = CONFIG["vault"]["root_path"]
    claude_config = CONFIG["claude"]
    settings_path = Path(__file__).parent / "claude-settings.json"

    cmd = [
        claude_config.get("cli_path", "claude"),
        "-p", prompt,
        "--settings", str(settings_path),
        "--output-format", "text",
        "--max-budget-usd", str(claude_config["max_budget_usd"]),
        "--no-session-persistence",
    ]

    logger.info(f"执行 Claude CLI: cd {vault_root} && claude -p ...")

    env = os.environ.copy()
    claude_env = claude_config.get("env", {})
    for key, value in claude_env.items():
        env[key] = value
        if "TOKEN" in key or "SECRET" in key or "KEY" in key:
            logger.info(f"  设置环境变量: {key}=***{value[-4:]}")
        else:
            logger.info(f"  设置环境变量: {key}={value}")

    try:
        result = subprocess.run(
            cmd,
            cwd=vault_root,
            capture_output=True,
            text=True,
            timeout=claude_config["timeout_seconds"],
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Claude CLI 执行成功，输出长度: {len(output)}")
            return output
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "未知错误"
            logger.error(f"Claude CLI 执行失败 (code={result.returncode}): {error_msg}")
            return f"处理失败: {error_msg[:500]}"

    except subprocess.TimeoutExpired:
        logger.error(f"Claude CLI 执行超时 ({claude_config['timeout_seconds']}s)")
        return "处理超时，请稍后重试或尝试处理更小的文件。"
    except FileNotFoundError:
        logger.error("找不到 claude 命令，请确认 Claude CLI 已安装并在 PATH 中")
        return "系统错误: 找不到 Claude CLI"
    except Exception as e:
        logger.error(f"Claude CLI 执行异常: {e}")
        return f"处理异常: {str(e)[:500]}"


# ============================================================
# 意图/上下文提取
# ============================================================

def extract_context_from_text(session: dict, content: str):
    """从用户文本消息中提取会话上下文（路径、名称、意图等）"""
    context = session["context"]

    # ----- 路径提取 -----
    path_patterns = [
        r'(?:放在|存到|保存到|路径|目录|文件夹)[：:]?\s*["《]?([^"》\s，。,]+)["》]?',
        r'(?:路径|目录|文件夹)[：:]?\s*(\S+)',
    ]
    for pat in path_patterns:
        m = re.search(pat, content)
        if m:
            candidate = m.group(1).rstrip("。，, ")
            if not context["storage_path"]:
                context["storage_path"] = candidate
                logger.info(f"提取路径: {candidate}")
            break

    # ----- 名称提取 -----
    name_patterns = [
        r'(?:名字|名称|文件名|标题|叫|命名为)[：:]?\s*["《]?([^"》\s，。,]+(?:\.md)?)["》]?',
        r'(?:笔记名|文件名)[：:]?\s*(\S+)',
    ]
    for pat in name_patterns:
        m = re.search(pat, content)
        if m:
            candidate = m.group(1).rstrip("。，, ")
            if not context["note_name"]:
                context["note_name"] = candidate
                logger.info(f"提取名称: {candidate}")
            break

    # 如果内容是"就叫XXX吧"或"是XXX"等简单句式，视为回答当前追问
    awaiting = session.get("awaiting_field")
    if awaiting and not any(keyword in content for keyword in ["放在", "存到", "路径", "目录", "文件夹", "叫", "名字", "名称", "标题"]):
        simple_name = re.sub(r'^(?:就?是?|叫|就?叫|用|就?用)\s*', '', content)
        simple_name = re.sub(r'[吧嘛嗯呢。，！]+\s*$', '', simple_name).strip()
        if simple_name and len(simple_name) < 50:
            if awaiting == "storage_path" and not context["storage_path"]:
                context["storage_path"] = simple_name
                logger.info(f"提取路径(简单回答): {simple_name}")
            elif awaiting == "note_name" and not context["note_name"]:
                context["note_name"] = simple_name
                logger.info(f"提取名称(简单回答): {simple_name}")

    # ----- 意图提取 -----
    intent_map = {
        "summarize": ["总结", "摘要", "归纳", "概括", "提炼"],
        "organize": ["整理", "笔记", "归档", "结构化", "存放"],
        "extract": ["提取", "摘录", "关键", "要点", "精华"],
        "search": ["搜索", "查找", "找到", "查询", "搜一下"],
        "skill": ["用skill", "使用skill", "调用skill", "运行skill"],
    }
    for intent_kw in ["summarize", "organize", "extract", "search", "skill"]:
        if context["intent"]:
            break
        for kw in intent_map[intent_kw]:
            if kw in content:
                context["intent"] = intent_kw
                logger.info(f"提取意图: {intent_kw} (关键词: {kw})")
                break

    # ----- Skill 名称提取 -----
    skill_pattern = r'(?:用|使用|调用|运行)\s*(?:skill[:：]?\s*)?(\S+)'
    m = re.search(skill_pattern, content)
    if m:
        context["skill_name"] = m.group(1)
        logger.info(f"提取 skill: {m.group(1)}")

    # ----- 完整指令记录 -----
    context["custom_instruction"] = content
    session["conversation_count"] += 1
    update_session_activity(session["sender_id"])


def is_session_ready_to_execute(session: dict) -> list:
    """检查会话是否已收集足够信息来执行，返回缺失字段列表"""
    context = session["context"]
    pending_file = session.get("pending_file")
    intent = context.get("intent")
    missing = []

    if pending_file:
        # 有文件待处理
        if not intent:
            missing.append("intent")
        elif intent == "organize":
            if not context["storage_path"]:
                missing.append("storage_path")
            if not context["note_name"]:
                missing.append("note_name")
        # summarize/extract 不需要路径和名称
    else:
        # 无文件，纯指令 — 有 custom_instruction 即可
        if not context.get("custom_instruction"):
            missing.append("instruction")

    return missing


# ============================================================
# 消息处理器
# ============================================================

def execute_and_reply(chat_id: str, prompt: str, sender_id: str):
    """执行 Claude CLI 并回复，完成后重置会话"""
    with processing_lock:
        global is_processing
        is_processing = True

    try:
        session = get_or_create_session(sender_id, chat_id)
        session["state"] = "PROCESSING"

        send_lark_message(chat_id, "🤖 AI 正在处理，请稍候（可能需要1-3分钟）...")

        claude_output = run_claude_task(prompt)

        max_reply_length = 1500
        if len(claude_output) > max_reply_length:
            claude_output = claude_output[:max_reply_length] + \
                "\n\n...（内容过长已截断，完整结果请查看 Obsidian Vault）"

        reply = f"📋 处理完成:\n{claude_output}"
        logger.info(f"Claude 输出长度: {len(claude_output)}")
        logger.info(f"回复内容预览(前100字): {reply[:100]}")
        send_lark_message(chat_id, reply)

    except Exception as e:
        logger.error(f"执行异常: {e}\n{traceback.format_exc()}")
        send_lark_message(chat_id, f"❌ 处理出错: {str(e)[:200]}")
    finally:
        reset_session(sender_id)
        with processing_lock:
            is_processing = False


def handle_file_message(session: dict, event: dict):
    """
    处理文件消息：
    1. 下载文件到资源目录
    2. 将会话状态设为 AWAITING_INSTRUCTION
    3. 询问用户意图
    """
    chat_id = session["chat_id"]
    sender_id = session["sender_id"]
    content = event.get("content", "")
    message_id = event.get("message_id", "")

    logger.info(f"📎 文件消息: {content}")

    # 从 content XML 解析 file_key 和文件名
    file_key = event.get("file_key", "")
    file_origin_name = "未知文件"
    if not file_key:
        key_match = re.search(r'key="([^"]+)"', content)
        if key_match:
            file_key = key_match.group(1)
            logger.info(f"从 content 解析到 file_key: {file_key}")
        else:
            logger.warning(f"无法解析 file_key, content={content}")
            send_lark_message(chat_id, "❌ 无法获取文件标识，下载失败。")
            return

    name_match = re.search(r'name="([^"]*)"', content)
    if name_match:
        file_origin_name = name_match.group(1)

    # 使用原始文件名
    file_name = file_origin_name or f"lark_file_{int(time.time())}"
    vault_root = CONFIG["vault"]["root_path"]
    resources_dir = CONFIG["vault"]["resources_dir"]

    # 发送"正在下载"通知
    send_lark_message(chat_id, "⏳ 正在下载文件...")

    downloaded = download_lark_file(
        message_id, file_key,
        vault_root, resources_dir, file_name,
    )

    if not downloaded:
        send_lark_message(chat_id, "❌ 文件下载失败，请稍后重试。")
        return

    # 保存到会话
    session["pending_file"] = {
        "path": downloaded,
        "name": file_origin_name,
        "message_id": message_id,
    }
    session["state"] = "AWAITING_INSTRUCTION"
    update_session_activity(sender_id)

    # 同时更新全局 last_received_file（兼容旧版整理笔记命令）
    global last_received_file
    last_received_file = {
        "message_id": message_id,
        "title": content,
        "sender_id": sender_id,
        "local_path": downloaded,
        "timestamp": time.time(),
    }

    logger.info(f"文件已保存，会话状态: AWAITING_INSTRUCTION, file={file_origin_name}")

    # 询问用户意图
    msg = (
        f"✅ 已接收文件: {file_origin_name}\n\n"
        f"请问你想怎么处理这个文件？例如：\n\n"
        f"📝 **整理成笔记** — 告诉我存放路径和笔记名称\n"
        f'   例："整理成笔记放在 AI 目录，名字叫学习笔记"\n\n'
        f"📋 **总结内容** — 直接总结文件要点\n\n"
        f"🔍 **提取关键信息** — 提取你认为重要的内容\n\n"
        f"🎯 **调用 Skill** — 用指定 skill 处理\n\n"
        f"❌ 回复「取消」可放弃操作"
    )
    send_lark_message(chat_id, msg)


# ============================================================
# 接管模式管理（自动接管 / 人工接管）
# ============================================================

def _get_mode() -> str:
    """获取当前接管模式: 'manual'（纯接收模式）"""
    global _cached_mode
    try:
        if ADMIN_STATE_PATH.exists():
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
            mode = state.get("mode", "auto")
            # ★ 同步更新内存缓存
            with _mode_cache_lock:
                _cached_mode = mode
            return mode
    except Exception:
        logger.warning(f"⚠️ 读取 admin_state.json 失败，使用内存缓存: {_cached_mode}")
    # ★ 文件读取失败时回退到内存缓存，而非硬编码 "auto"
    with _mode_cache_lock:
        return _cached_mode


def _set_mode(mode: str):
    """设置接管模式: manual=纯接收模式（所有消息排队等待 Claude Code 处理）"""
    global _cached_mode
    try:
        state = {}
        if ADMIN_STATE_PATH.exists():
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        state["mode"] = mode
        ADMIN_STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        # ★ 同步更新内存缓存
        with _mode_cache_lock:
            _cached_mode = mode
        # ★ 切换到人工接管时，重置所有活跃会话（避免旧的 PROCESSING 状态干扰）
        if mode == "manual":
            with sessions_lock:
                for sid in list(sessions.keys()):
                    sessions[sid].update({
                        "state": "IDLE",
                        "pending_file": None,
                        "context": {k: None for k in ("storage_path", "note_name", "intent", "custom_instruction", "skill_name")},
                        "awaiting_field": None,
                        "conversation_count": 0,
                        "last_activity": time.time(),
                    })
            logger.info(f"🔄 [人工接管] 已重置 {len(sessions)} 个活跃会话")
        logger.info(f"🔄 接管模式已切换: {mode}")
    except Exception as e:
        logger.error(f"切换模式失败: {e}")


def _save_pending_message(event: dict, file_path: str = ""):
    """在纯接收模式下，将消息保存为待处理状态，等待 Claude Code 通过 admin.py 处理"""
    try:
        state = {}
        if ADMIN_STATE_PATH.exists():
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        if "pending_messages" not in state:
            state["pending_messages"] = []
        summary = event.get("content", "")[:80]
        if file_path:
            summary = f"[文件] {Path(file_path).name}"
        pending = {
            "id": str(int(time.time() * 1000)),
            "time": datetime.now().strftime("%H:%M:%S"),
            "sender_id": event.get("sender_id", ""),
            "chat_id": event.get("chat_id", ""),
            "message_type": event.get("message_type", "unknown"),
            "content": event.get("content", ""),
            "file_path": file_path,
            "summary": summary,
        }
        state["pending_messages"].append(pending)
        # 最多保留 50 条待处理消息
        if len(state["pending_messages"]) > 50:
            state["pending_messages"] = state["pending_messages"][-50:]
        state["has_pending"] = True
        ADMIN_STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        logger.info(f"⏸️ [人工接管] 消息已暂存: {pending['summary']}")
    except Exception as e:
        logger.error(f"保存待处理消息失败: {e}")


# ============================================================
# 本地命令处理器（快速响应，无需调用 Claude CLI）
# ============================================================

def handle_local_command(content: str, chat_id: str, session: dict) -> bool:
    """已禁用：纯接收模式下飞书助手不处理任何本地命令，全部静默排队等待 Claude Code"""
    return False


def handle_text_in_idle(session: dict, event: dict):
    """
    处理 IDLE 状态下的文本消息：
    - 已知命令（整理笔记、帮助、搜索、总结）→ 使用结构化 prompt
    - 自然语言 → 直接交给 Claude CLI 执行
    """
    content = event.get("content", "").strip()
    chat_id = session["chat_id"]
    sender_id = session["sender_id"]

    # ======== 本地命令快速响应（无需调用 Claude CLI） ========
    if handle_local_command(content, chat_id, session):
        logger.info(f"⚡ 本地命令已处理: {content[:50]}")
        return

    # ======== 整理笔记（关联最近文件） ========
    if (content.startswith("整理笔记") or content.startswith("整理文件")) and last_received_file:
        file_path = last_received_file.get("local_path", "")
        prompt = generate_claude_prompt("text", event, file_path)
        execute_and_reply(chat_id, prompt, sender_id)
        return

    # ======== 整理笔记（无文件） ========
    elif content.startswith("整理笔记") or content.startswith("整理文件"):
        prompt = generate_claude_prompt("text", event)
        execute_and_reply(chat_id, prompt, sender_id)
        return

    # ======== 搜索 ========
    elif content.startswith("/搜索") or content.startswith("搜索"):
        prompt = generate_claude_prompt("text", event)
        execute_and_reply(chat_id, prompt, sender_id)
        return

    # ======== 总结 ========
    elif content.startswith("总结") or content.startswith("总结："):
        prompt = generate_claude_prompt("text", event)
        execute_and_reply(chat_id, prompt, sender_id)
        return

    # ======== 自然语言 ========
    logger.info(f"💬 自然语言指令: {content[:200]}")

    # 先回复"已收到"，让用户知道机器人在处理
    send_lark_message(chat_id, "🤔 让我理解你的需求...")

    prompt = f"""🔴 自动化任务 — 来自飞书（用户: {sender_id}）

用户消息: {content}

请理解用户意图并执行。用户可以通过对话控制 Obsidian 知识库：
- 📝 整理笔记/处理文件
- 🔍 搜索知识库内容
- ✏️ 创建或编辑笔记
- 🛠️ 调用某个 skill
- 💬 回答关于知识库的问题

根据指令执行操作，完成后简要回复结果（200字以内）。将任何生成的笔记写入 Vault。"""

    execute_and_reply(chat_id, prompt, sender_id)


def handle_conversation_text(session: dict, event: dict):
    """
    处理 AWAITING_INSTRUCTION / CLARIFYING 状态下的文本消息：
    1. 尝试从用户消息中提取上下文（路径、名称、意图）
    2. 如果信息齐全，执行任务
    3. 如果缺少信息，追问用户
    """
    content = event.get("content", "").strip()
    chat_id = session["chat_id"]
    sender_id = session["sender_id"]

    # ---- 取消操作 ----
    if content in ("取消", "不用了", "算了", "不要了", "cancel", "退出", "结束", "跳过"):
        # 文件已下载到资源目录，不用删除
        send_lark_message(chat_id,
            "❌ 已取消操作。\n"
            "文件已保存到知识库资源目录，你可以随时再找我处理。\n"
            "有其他需要随时说~")
        reset_session(sender_id)
        return

    # ---- 提取上下文 ----
    extract_context_from_text(session, content)
    context = session["context"]

    # ---- 检查是否足够执行 ----
    missing = is_session_ready_to_execute(session)

    if not missing:
        # 信息齐全，执行
        logger.info(f"信息齐全，开始执行任务: intent={context.get('intent')}, "
                    f"path={context.get('storage_path')}, name={context.get('note_name')}")
        session["state"] = "PROCESSING"
        prompt = build_session_prompt(session, content)
        execute_and_reply(chat_id, prompt, sender_id)
        return

    # ---- 追问缺失信息 ----
    session["state"] = "CLARIFYING"
    intent = context.get("intent")

    if "intent" in missing:
        # 意图不明确 → 给用户选项
        msg = (
            "🤔 我还是不太确定你想怎么处理这个文件。请告诉我：\n\n"
            "1️⃣ **整理成笔记** — 我会用 meeting-summary skill 整理\n"
            "2️⃣ **总结内容** — 直接总结文件要点\n"
            "3️⃣ **提取关键信息** — 提取你认为重要的内容\n"
            "4️⃣ **其他用途** — 直接描述你的需求"
        )
        send_lark_message(chat_id, msg)

    elif intent == "organize":
        # 整理笔记，可能缺路径或名称
        if not context["storage_path"] and not context["note_name"]:
            msg = (
                "📁 请问这个笔记要存放在哪个文件夹？笔记名称是什么？\n\n"
                "💡 你可以一次性告诉我，例如：\n"
                '"放在 AI/学习笔记 文件夹，名字叫 知识点总结"'
            )
            session["awaiting_field"] = "storage_path"
        elif not context["storage_path"]:
            msg = "📁 请问这个笔记要存放在哪个文件夹？\n  例：`AI/学习笔记` 或 `项目/实习`"
            session["awaiting_field"] = "storage_path"
        elif not context["note_name"]:
            msg = "📝 请问笔记的标题叫什么名字？\n  例：`知识点总结` 或 `面试技巧`"
            session["awaiting_field"] = "note_name"

        send_lark_message(chat_id, msg)

    elif intent == "search":
        # 搜索 — 需要有关键词
        msg = "🔍 请问你想搜索什么内容？请输入关键词。"
        send_lark_message(chat_id, msg)

    elif intent == "skill":
        msg = "🎯 请问你想调用哪个 skill？例如：`meeting-summary`"
        send_lark_message(chat_id, msg)

    else:
        # 通用追问
        msg = (
            "🤔 请告诉我你具体想怎么做？\n\n"
            "💡 例如：\n"
            '- "整理成笔记放在 AI 目录，名字叫学习笔记"\n'
            '- "总结一下这个文件"\n'
            '- "提取关键信息"'
        )
        send_lark_message(chat_id, msg)


# ============================================================
# 事件处理
# ============================================================

def process_event(event: dict):
    """处理单个飞书事件 — 纯接收模式
    所有消息静默排队，不回复不处理，等待 Claude Code 通过 admin.py 处理"""

    message_type = event.get("message_type", "")
    content = event.get("content", "")
    chat_id = event.get("chat_id", "")
    sender_id = event.get("sender_id", "")
    message_id = event.get("message_id", "")
    chat_type = event.get("chat_type", "")

    logger.info(f"处理消息: type={message_type}, chat_type={chat_type}, sender={sender_id}")

    # 只处理 P2P 消息（私聊机器人的消息）
    if chat_type != "p2p":
        logger.info(f"跳过非 P2P 消息: {chat_type}")
        return

    # ⭐ 消息去重
    with processed_ids_lock:
        if message_id in processed_message_ids:
            logger.info(f"跳过重复消息: {message_id}")
            return
        processed_message_ids.add(message_id)
        if len(processed_message_ids) > 1000:
            # 滑动剔除：移除最旧的 200 个 ID，避免清空后出现去重盲区
            excess = sorted(processed_message_ids)[:200]
            processed_message_ids.difference_update(excess)

    # ★ [纯接收模式] 所有消息静默排队等待 Claude Code 处理
    #    飞书助手已禁用自动发信和自动处理功能：
    #    - 不回复任何消息（保持完全静默）
    #    - 不处理任何本地命令
    #    - 所有消息排队等待 Claude Code 通过 admin.py 处理
    #    - 文件静默下载到资源目录供后续使用

    # 文件消息需先静默下载到资源目录
    file_downloaded = ""
    if message_type == "file":
        try:
            file_key = event.get("file_key", "")
            if not file_key:
                key_match = re.search(r'key="([^"]+)"', content)
                if key_match:
                    file_key = key_match.group(1)
            name_match = re.search(r'name="([^"]*)"', content)
            file_name = name_match.group(1) if name_match else f"lark_file_{int(time.time())}"
            if file_key:
                vault_root = CONFIG["vault"]["root_path"]
                resources_dir = CONFIG["vault"]["resources_dir"]
                saved = download_lark_file(
                    message_id, file_key,
                    vault_root, resources_dir, file_name,
                )
                if saved:
                    file_downloaded = saved
                    logger.info(f"📎 文件已静默下载: {file_downloaded}")
        except Exception as e:
            logger.warning(f"文件静默下载失败: {e}")

    # 所有消息排队等待管理员通过 Claude Code 处理
    # ⚠️ 不回复任何消息，保持完全静默
    _save_pending_message(event, file_path=file_downloaded)
    logger.info(f"⏸️ [纯接收模式] 消息已暂存: type={message_type}, sender={sender_id}")
    return


# ============================================================
# 后台线程
# ============================================================

def watchdog():
    """
    看门狗线程：定期检查 lark-cli 子进程健康状况
    如果进程意外退出且事件消费者未自动恢复，则触发日志告警
    """
    logger.info("看门狗线程已启动（每60秒检查一次）")
    last_known_pid = None

    while not watchdog_stop_event.is_set():
        watchdog_stop_event.wait(60)
        if watchdog_stop_event.is_set():
            break

        global event_consumer_process
        proc = event_consumer_process

        if proc is None:
            logger.warning("看门狗: event_consumer_process 为 None，可能正在重启")
            continue

        pid = proc.pid
        poll = proc.poll()

        if poll is None:
            if pid != last_known_pid:
                logger.info(f"看门狗: lark-cli 进程正常运行中 (PID: {pid})")
                last_known_pid = pid
        else:
            logger.warning(f"看门狗: lark-cli 进程已退出 (PID: {pid}, code={poll})")
            last_known_pid = None


def admin_monitor():
    """
    管理员监控线程：监听 admin_state.json 中的远程指令
    支持指令:
      - cancel   : 取消当前任务（设置处理锁定超时）
      - override : 以管理员身份覆盖执行指令（最高优先级）
      - pause    : 暂停自动处理
    管理员指令优先级高于飞书用户的自动处理。

    ★ 在纯接收模式下，飞书助手不自动处理任何消息，
      所有任务必须由管理员通过 admin.py 触发（override 指令）。
    """
    logger.info("管理员监控线程已启动（每2秒轮询指令）")
    last_state = {}

    while not admin_stop_event.is_set():
        admin_stop_event.wait(2)
        if admin_stop_event.is_set():
            break

        try:
            if not ADMIN_STATE_PATH.exists():
                continue

            with open(ADMIN_STATE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)

            if state == last_state:
                continue  # 无变化

            command = state.get("command")
            if not command:
                last_state = state
                continue

            # ── 读取后立即清除指令，避免重复执行 ──
            state["command"] = None
            with open(ADMIN_STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            # ── cancel：取消当前任务 ──
            if command == "cancel":
                logger.warning("🔴 [管理员] 收到取消指令，正在中断当前任务...")
                # 通过缩短超时时间的方让执行中的任务快速退出
                global is_processing
                with processing_lock:
                    is_processing = False

            # ── override：管理员覆盖指令（最高优先级） ──
            elif command == "override":
                instruction = state.get("override_instruction", "")
                logger.warning(f"🔴 [管理员] 收到覆盖指令（最高优先级）: {instruction[:100]}")

                # 管理员消息直接注入任务队列，作为最高优先级事件
                admin_event = {
                    "type": "admin_override",
                    "content": instruction,
                    "time": datetime.now().isoformat(),
                    "priority": 999,  # 最高优先级
                }
                task_queue.put(admin_event)
                logger.info(f"管理员覆盖指令已注入任务队列")

            # ── pause/resume：暂停/恢复自动处理 ──
            elif command == "pause":
                logger.warning("🔴 [管理员] 暂停自动处理")
                state["paused"] = True
                with open(ADMIN_STATE_PATH, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)

            elif command == "resume":
                logger.warning("🟢 [管理员] 恢复自动处理")
                state["paused"] = False
                with open(ADMIN_STATE_PATH, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)

            last_state = state

        except Exception as e:
            logger.debug(f"管理员监控线程异常: {e}")


def event_consumer():
    """
    主线程：启动 lark-cli event consume 并处理事件
    使用 readline + poll 双检测机制:
      - readline 阻塞等待新事件
      - 每行读取最多等 30 秒，然后检查进程状态
    当进程意外退出时自动重启
    """
    global event_consumer_process
    logger.info("飞书事件监听线程已启动")

    while True:
        try:
            logger.info("启动 lark-cli event consume（持久连接模式）...")
            exe_path = LARK_CLI_PATH
            consume_cmd = [exe_path, "event", "consume", "im.message.receive_v1", "--as", "bot"]
            logger.info(f"启动命令: {' '.join(consume_cmd)}")

            process = subprocess.Popen(
                consume_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            event_consumer_process = process
            event_consumer_ready.set()
            logger.info(f"lark-cli 进程 PID: {process.pid}，等待事件...")

            # 逐行读取 stdout（NDJSON 格式），同时轮询进程状态
            stdout_fd = process.stdout

            while True:
                line = stdout_fd.readline()
                if not line:
                    poll = process.poll()
                    if poll is not None:
                        logger.warning(f"lark-cli 进程已退出 (code={poll})")
                        stderr_output = process.stderr.read()
                        if stderr_output:
                            logger.warning(f"stderr: {stderr_output[:300]}")
                    else:
                        logger.warning("stdout 返回空但进程仍在运行，可能连接已断开")
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                    logger.info(f"收到飞书事件: message_id={event.get('message_id', '')}, "
                                f"type={event.get('message_type', '')}")
                    logger.info(f"事件内容: sender={event.get('sender_id', '')}, "
                                f"chat_type={event.get('chat_type', '')}, "
                                f"content={event.get('content', '')[:100]}")

                    task_queue.put(event)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析失败: {e}, line={line[:200]}")

        except FileNotFoundError:
            logger.error("找不到 lark-cli 命令，请确认已安装")
            time.sleep(30)
        except Exception as e:
            logger.error(f"事件消费异常: {e}")
            time.sleep(5)

        event_consumer_process = None
        logger.info("3秒后重新连接飞书事件流...")
        time.sleep(3)


def task_worker():
    """
    后台任务工作线程，从队列中取事件并处理
    单线程模型保证事件顺序处理
    支持管理员覆盖指令（最高优先级）
    """
    logger.info("任务工作线程已启动")
    while True:
        try:
            event = task_queue.get(timeout=1)

            # ★ 管理员覆盖指令检查
            if isinstance(event, dict) and event.get("type") == "admin_override":
                instruction = event.get("content", "")
                logger.warning(f"🔴 执行管理员覆盖指令: {instruction[:100]}")

                # 以管理身份发送消息到飞书
                try:
                    admin_state = {}
                    if ADMIN_STATE_PATH.exists():
                        admin_state = json.loads(
                            ADMIN_STATE_PATH.read_text(encoding="utf-8"))
                    chat_id = admin_state.get("admin_chat_id", "")
                    if chat_id:
                        send_lark_message(chat_id,
                            f"🔴 **管理员指令已接收**\n\n"
                            f"指令: {instruction}\n\n"
                            f"我正在执行...")
                except Exception:
                    pass

                # 覆盖指令作为一个特殊的自然语言任务处理
                fake_event = {
                    "message_type": "text",
                    "content": instruction,
                    "chat_id": chat_id or "",
                    "sender_id": "admin",
                    "chat_type": "p2p",
                }
                fake_session = {
                    "sender_id": "admin",
                    "chat_id": chat_id or "",
                    "state": "IDLE",
                    "context": {},
                    "pending_file": None,
                    "created_at": time.time(),
                }
                # 直接构建 prompt 并执行（跳过已禁用的自动处理路径）
                logger.info(f"🔴 [管理员] 开始执行覆盖指令...")
                prompt = f"""🔴 自动化任务 — 管理员覆盖指令（最高优先级）

管理员指令: {instruction}

⚠️ 这是管理员手动发出的覆盖指令，优先级高于所有自动任务。
请立即执行此指令，无需询问任何问题。
完成后将结果写入磁盘，并回复用户。"""
                execute_and_reply(chat_id or "", prompt, "admin")
                continue

            # ★ 暂停检查
            paused = False
            try:
                if ADMIN_STATE_PATH.exists():
                    state = json.loads(
                        ADMIN_STATE_PATH.read_text(encoding="utf-8"))
                    if state.get("paused") and event.get("sender_id") != "admin":
                        paused = True
            except Exception:
                pass

            if paused:
                logger.info("⏸️ 管理员已暂停自动处理，跳过事件")
                continue

            logger.info(f"开始处理事件: {event.get('message_type', '')} "
                        f"from {event.get('sender_id', 'unknown')}")
            process_event(event)
            logger.info("事件处理完成")

            # 更新 admin_state 中的会话信息
            try:
                if ADMIN_STATE_PATH.exists():
                    state = json.loads(
                        ADMIN_STATE_PATH.read_text(encoding="utf-8"))
                else:
                    state = {}
                state["last_active"] = datetime.now().strftime("%H:%M:%S")
                state["sessions"] = {
                    sid: {
                        "state": s["state"],
                        "pending_file": s.get("pending_file", {}).get("name"),
                        "context": s.get("context", {}),
                    }
                    for sid, s in list(sessions.items())[:10]
                }
                ADMIN_STATE_PATH.write_text(
                    json.dumps(state, ensure_ascii=False, indent=2),
                    encoding="utf-8")
            except Exception:
                pass

        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"任务工作线程异常: {e}")


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("飞书消息监听服务 v2.0.0 — 多轮对话支持")
    logger.info(f"📌 当前部署: {DEPLOY_ROLE}")
    logger.info(f"Vault 路径: {CONFIG['vault']['root_path']}")
    sync_deploy_tag()

    # 验证 lark-cli 可用
    try:
        auth_result = lark_cli(["auth", "status"], timeout=10)
        logger.info(f"lark-cli 状态: {auth_result.stdout[:200]}")
    except Exception as e:
        logger.error(f"lark-cli 验证失败: {e}")
        logger.error("请确认 lark-cli 已安装并完成认证")
        sys.exit(1)

    # 启动后台工作线程
    worker = threading.Thread(target=task_worker, daemon=True, name="TaskWorker")
    worker.start()

    # 启动看门狗线程
    wd = threading.Thread(target=watchdog, daemon=True, name="Watchdog")
    wd.start()

    # 启动会话清理线程
    cleaner = threading.Thread(target=cleanup_stale_sessions, daemon=True, name="SessionCleaner")
    cleaner.start()

    # 启动管理员监控线程（远程控制）
    admin_thread = threading.Thread(target=admin_monitor, daemon=True, name="AdminMonitor")
    admin_thread.start()
    logger.info("管理员监控线程已启动（远程控制就绪）")

    # 初始化 admin_state.json
    try:
        if not ADMIN_STATE_PATH.exists():
            initial_state = {
                "command": None,
                "mode": "manual",  # ★ 纯接收模式：所有消息静默排队，由 Claude Code 通过 admin.py 处理
                "paused": False,
                "override_pending": False,
                "pending_messages": [],
                "has_pending": False,
                "last_active": datetime.now().strftime("%H:%M:%S"),
                "sessions": {},
                "admin_chat_id": "",
            }
            ADMIN_STATE_PATH.write_text(
                json.dumps(initial_state, ensure_ascii=False, indent=2),
                encoding="utf-8")
            logger.info("管理员状态文件已初始化")
    except Exception as e:
        logger.warning(f"管理员状态文件初始化失败: {e}")

    # 启动事件消费（主线程阻塞）
    logger.info("=" * 60)
    logger.info("开始监听飞书消息...")
    logger.info("=" * 60)
    event_consumer()
