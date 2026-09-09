"""
飞书智能助手 - 管理员 CLI（Claude Code 远程控制）
=================================================
允许 Claude Code 接入飞书进行信息的查看和操控。

★ 纯接收模式：飞书助手不自动处理任何消息，
  所有消息排队等待管理员通过 Claude Code 处理。

用法：
  python admin.py <命令> [参数]

命令：
  status                 查看服务状态和当前消息
  send <chat_id> <消息>   通过机器人发送消息给指定会话
  reply <消息>            回复最近一个发消息的用户
  recent [行数]           查看最近的飞书消息记录
  pending                查看待处理的消息列表
  process <ID> [指令]     处理指定待处理消息（可附加指令）
  cancel                 取消当前正在处理的任务
  override <指令>         以管理员身份覆盖执行指令（最高优先级）
  help                   显示此帮助信息

管理员权限说明：
  - admin.py 可以直接调用 lark-cli 发送消息
  - 通过 admin_state.json 与服务进程通信，实现任务取消和覆盖
  - 管理员指令的优先级高于飞书用户的自动处理
"""

import io
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Windows 控制台编码修复 ──
if sys.stdout.encoding.lower() in ("gbk", "gb2312", "cp936"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 路径配置 ──────────────────────────────────────────────────
SERVICE_DIR = Path(__file__).parent
VAULT_ROOT = (SERVICE_DIR / "..").resolve()
LOG_DIR = SERVICE_DIR / "logs"
CONFIG_PATH = SERVICE_DIR / "config.json"
ADMIN_STATE_PATH = SERVICE_DIR / "admin_state.json"
def _resolve_lark_cli() -> str:
    """lark-cli 路径自适应（双机并存）：旧电脑路径 → 本机 npm 全局目录 → PATH"""
    legacy = r"C:\Users\asus\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
    npm_dir = Path.home() / "AppData" / "Roaming" / "npm"
    candidates = [
        legacy,
        str(npm_dir / "node_modules" / "@larksuite" / "cli" / "bin" / "lark-cli.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    found = shutil.which("lark-cli")
    if found:
        return found
    return legacy  # 兜底返回原路径，报错信息更明确


LARK_CLI = _resolve_lark_cli()


# ── 部署角色标记（公司电脑 / 自用电脑）──────────────────
# 自动检测本机身份，并同步维护「部署标记.txt」。
# 知识库在两台电脑间自动同步，标记文件会被互相同步覆盖，
# 因此每次执行时根据本机身份自动纠正。

def _detect_deployment() -> str:
    """检测当前机器部署角色: 自用电脑(asus) → '自己用'，公司电脑(PC) → '公司用'"""
    username = os.environ.get("USERNAME", "").lower()
    if username == "asus":
        return "自己用"
    if username == "pc":
        return "公司用"
    if os.path.isdir(r"C:\Users\asus"):
        return "自己用"
    return "公司用"


DEPLOY_ROLE = _detect_deployment()
DEPLOY_TAG_FILE = SERVICE_DIR / "部署标记.txt"


def sync_deploy_tag() -> None:
    """同步部署标记文件（本机身份优先，覆盖同步过来的异机标记）"""
    content = f"本机部署角色：{DEPLOY_ROLE}\n"
    try:
        if not DEPLOY_TAG_FILE.exists() or DEPLOY_TAG_FILE.read_text(encoding="utf-8") != content:
            DEPLOY_TAG_FILE.write_text(content, encoding="utf-8")
    except Exception:
        pass


# ── 辅助函数 ──────────────────────────────────────────────────

def load_config() -> dict:
    """加载服务配置"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def lark_cli(args: list, timeout: int = 30) -> subprocess.CompletedProcess:
    """调用 lark-cli.exe 执行命令"""
    cmd = [LARK_CLI] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"❌ 命令超时: {' '.join(cmd)}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ 找不到 lark-cli.exe: {LARK_CLI}")
        sys.exit(1)


def get_service_pid() -> int:
    """获取正在运行的 server.py 进程 PID"""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='python.exe' AND CommandLine LIKE '%server.py%'\" | Select-Object -ExpandProperty ProcessId"],
            capture_output=True, text=True, timeout=10,
        )
        pid_str = result.stdout.strip()
        if pid_str:
            return int(pid_str.split('\n')[0])
    except Exception:
        pass
    return 0


def get_default_chat_id() -> str:
    """从日志中获取最近发消息的用户 chat_id"""
    log_file = LOG_DIR / "lark-service.log"
    if not log_file.exists():
        return ""
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                if "chat_id=oc_" in line:
                    idx = line.index("chat_id=oc_")
                    return line[idx:idx + 36]  # oc_ + 32 chars
    except Exception:
        pass
    return ""


# ── 命令实现 ──────────────────────────────────────────────────

def cmd_status():
    """查看服务状态"""
    pid = get_service_pid()
    config = load_config()
    model = config.get("claude", {}).get("env", {}).get("ANTHROPIC_MODEL", "unknown")
    sync_deploy_tag()

    print("=" * 50)
    print("  🤖 飞书智能助手 - 管理状态")
    print("=" * 50)
    print(f"  📌 当前部署: {DEPLOY_ROLE}")

    if pid:
        print(f"  ✅ 服务进程: 运行中 (PID: {pid})")
    else:
        print(f"  ⚠️  服务进程: 未运行")

    print(f"  📦 模型: {model}")
    print(f"  ⏱  超时: {config.get('claude', {}).get('timeout_seconds', '?')}s")
    print(f"  💰 Budget: ${config.get('claude', {}).get('max_budget_usd', '?')}")
    print()

    # 读取 admin_state
    state = {}
    if ADMIN_STATE_PATH.exists():
        try:
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    mode = state.get("mode", "manual")
    mode_cn = "🔴 纯接收模式（由 Claude Code 控制）"
    pending_count = len(state.get("pending_messages", []))

    print(f"  📋 管理员状态:")
    print(f"    接管模式: {mode_cn}")
    print(f"    待处理消息: {'📬 ' + str(pending_count) + ' 条' if pending_count else '📭 无'}")
    print(f"    暂停处理: {'✅ 是' if state.get('paused') else '❌ 否'}")
    print(f"    待执行覆盖: {'✅ 有' if state.get('override_pending') else '❌ 无'}")
    print(f"    最近活跃时间: {state.get('last_active', '未知')}")
    print()

    # 查看日志最近的消息
    log_file = LOG_DIR / "lark-service.log"
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            recent_msgs = [l for l in lines if "收到飞书事件" in l or "已发送回复" in l or "执行 Claude" in l]
            if recent_msgs:
                print(f"  📝 最近活动 ({min(5, len(recent_msgs))} 条):")
                for line in recent_msgs[-5:]:
                    ts = line[:19] if len(line) > 19 else ""
                    msg = line.strip()
                    print(f"    {ts} {msg}")
        except Exception:
            pass

    print("=" * 50)


def cmd_send(chat_id: str, message: str):
    """通过机器人发送消息"""
    if not chat_id:
        print("❌ 请指定 chat_id，或使用 'reply' 命令回复最近用户")
        return

    content_json = json.dumps({"text": message}, ensure_ascii=False)
    result = lark_cli([
        "im", "+messages-send",
        "--chat-id", chat_id,
        "--content", content_json,
        "--as", "bot",
    ])

    if result.returncode == 0:
        print(f"✅ 消息已发送到 {chat_id}")
        print(f"   内容: {message[:100]}{'...' if len(message) > 100 else ''}")
    else:
        print(f"❌ 发送失败: {result.stderr[:200]}")


def cmd_reply(message: str):
    """回复最近发送消息的用户"""
    chat_id = get_default_chat_id()
    if not chat_id:
        print("❌ 无法从日志中找到最近的消息发送者，请使用 send 命令并指定 chat_id")
        return
    cmd_send(chat_id, message)


def cmd_recent(lines_count: int = 20):
    """查看最近的飞书消息记录"""
    log_file = LOG_DIR / "lark-service.log"
    if not log_file.exists():
        print("❌ 日志文件不存在")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # 筛选关键日志
    key_lines = []
    for line in all_lines:
        if any(kw in line for kw in [
            "收到飞书事件", "已发送回复", "执行 Claude",
            "文本消息:", "文件消息:", "事件处理完成",
            "创建新会话", "重置会话", "本地命令已处理",
            "文件已下载", "开始处理事件",
            "Claude CLI 执行", "处理超时", "处理失败",
        ]):
            key_lines.append(line.strip())

    print(f"📋 最近 {min(lines_count, len(key_lines))} 条消息记录:")
    print("-" * 60)
    for line in key_lines[-lines_count:]:
        print(f"  {line}")
    print("-" * 60)
    print(f"  共 {len(key_lines)} 条关键记录，显示最后 {lines_count} 条")


def cmd_sessions():
    """查看活跃会话"""
    state = {}
    if ADMIN_STATE_PATH.exists():
        try:
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    sessions = state.get("sessions", {})
    if not sessions:
        print("📋 当前无活跃会话")
        return

    print(f"📋 活跃会话 ({len(sessions)} 个):")
    print("-" * 60)
    for sid, s in sessions.items():
        print(f"  用户: {sid[:20]}...")
        print(f"  状态: {s.get('state', '?')}")
        print(f"  文件: {s.get('pending_file', {}).get('name', '无')}")
        print(f"  意图: {s.get('context', {}).get('intent', '?')}")
        print()


def cmd_cancel():
    """取消当前正在处理的任务"""
    pid = get_service_pid()
    if not pid:
        print("❌ 服务未运行")
        return

    # 写入取消信号到 admin_state
    state = {}
    if ADMIN_STATE_PATH.exists():
        try:
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    state["command"] = "cancel"
    state["command_time"] = datetime.now().strftime("%H:%M:%S")
    ADMIN_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print("✅ 取消信号已发送，等待服务响应...")
    print("   如果 Claude CLI 正在执行，可能需要等待其超时退出")


def cmd_override(instruction: str):
    """以管理员身份覆盖执行指令（最高优先级）"""
    pid = get_service_pid()
    if not pid:
        print("❌ 服务未运行")
        return

    # 写入覆盖指令到 admin_state
    state = {}
    if ADMIN_STATE_PATH.exists():
        try:
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    state["command"] = "override"
    state["override_instruction"] = instruction
    state["override_time"] = datetime.now().strftime("%H:%M:%S")
    ADMIN_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ 管理员覆盖指令已发送（最高优先级）:")
    print(f"   {instruction[:100]}")
    print(f"   服务将在当前任务完成后（或中断后）执行此指令")
    print()
    print("提示: 你也可以直接发送 'cancel' 先取消当前任务")


def cmd_mode(args: list = None):
    """查看或切换接管模式"""
    state = {}
    if ADMIN_STATE_PATH.exists():
        try:
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    current = state.get("mode", "manual")

    if not args:
        # 查看当前模式
        print(f"📋 当前模式: 🔴 纯接收模式（{current}）")
        print()
        print("说明:")
        print("  飞书智能助手已配置为纯接收模式:")
        print("  - 不会自动处理或回复任何消息")
        print("  - 所有消息排队等待管理员通过 Claude Code 处理")
        print("  - 处理任务需使用 override 指令")
        return

    print("⚠️ 纯接收模式已固定，不支持在运行时切换模式。")
    print("   如需修改请编辑 server.py 或更新配置文件。")


def cmd_pending():
    """查看待处理的待办消息（人工接管模式下暂存）"""
    state = {}
    if ADMIN_STATE_PATH.exists():
        try:
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    pending = state.get("pending_messages", [])
    if not pending:
        print("📭 当前没有待处理的消息")
        return

    print(f"📬 待处理消息 ({len(pending)} 条):")
    print("-" * 70)
    for i, msg in enumerate(pending):
        msg_type = "📝 文本" if msg.get("message_type") == "text" else "📎 文件"
        file_info = ""
        if msg.get("file_path"):
            file_info = f"\n      文件: {msg.get('file_path', '')}"
        print(f"  [{i}] {msg_type} | {msg.get('time', '?')} | {msg.get('sender_id', '')[:16]}...")
        print(f"      内容: {msg.get('summary', '')[:80]}{file_info}")
        print(f"      ID: {msg.get('id', '')}")
        print()


def cmd_process(pending_id: str, instruction: str):
    """处理一条待处理的消息"""
    state = {}
    if ADMIN_STATE_PATH.exists():
        try:
            state = json.loads(ADMIN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    pending = state.get("pending_messages", [])
    target = None
    for msg in pending:
        if msg.get("id") == pending_id:
            target = msg
            break

    if not target:
        # 也支持用序号
        try:
            idx = int(pending_id)
            if 0 <= idx < len(pending):
                target = pending[idx]
        except ValueError:
            pass

    if not target:
        print(f"❌ 未找到待处理消息: {pending_id}")
        print(f"   使用 'python admin.py pending' 查看可用的消息列表")
        return

    print(f"📋 处理消息: {target.get('summary', '')[:80]}")
    print(f"   用户: {target.get('sender_id', '')}")
    print(f"   类型: {target.get('message_type', '')}")

    # 构建处理指令
    full_instruction = instruction if instruction else target.get("content", "")
    print(f"   指令: {full_instruction[:100]}")

    # 使用 override 机制注入任务
    state["command"] = "override"
    state["override_instruction"] = full_instruction
    state["override_time"] = datetime.now().strftime("%H:%M:%S")
    ADMIN_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    # 从待处理列表中移除
    pending = [m for m in pending if m.get("id") != target.get("id")]
    # 如果用序号匹配的，按序号移除
    if target in pending:
        pending.remove(target)
    state["pending_messages"] = pending
    if not pending:
        state["has_pending"] = False
    ADMIN_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ 指令已发送到服务执行")
    print(f"   剩余待处理消息: {len(pending)} 条")


def cmd_help():
    """显示帮助信息"""
    help_text = """飞书智能助手 - 管理员 CLI（Claude Code 远程控制）
=================================================
允许 Claude Code 接入飞书进行信息的查看和操控。

★ 纯接收模式：飞书助手不自动处理任何消息，
  所有消息排队等待管理员通过 Claude Code 处理。

用法：
  python admin.py <命令> [参数]

消息处理（你作为管理员）：
  pending                 查看待处理的消息列表（用户发送的）
  process <ID> [指令]     处理指定待处理消息（可附加指令）
  send <chat_id> <消息>   通过机器人发送消息给指定会话
  reply <消息>            回复最近一个发消息的用户

任务管理：
  cancel                  取消当前正在处理的任务
  override <指令>         以管理员身份覆盖执行指令（最高优先级）

信息查看：
  status                  查看服务状态和当前消息
  recent [行数]           查看最近的飞书消息记录
  sessions                查看所有活跃会话
  help                    显示此帮助信息

管理员权限说明：
  - admin.py 是唯一可以向飞书用户发送消息的途径
  - 所有用户消息静默排队，等待管理员通过 admin.py 处理
  - 管理员通过 override 指令触发处理（调用 Claude CLI）
  - 管理员通过 send/reply 指令回复用户
"""
    print(help_text)


# ── 主入口 ──────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        cmd_help()
        return

    command = sys.argv[1]

    if command == "status":
        cmd_status()

    elif command == "mode":
        cmd_mode(sys.argv[2:])

    elif command == "pending":
        cmd_pending()

    elif command == "process":
        if len(sys.argv) < 3:
            print("❌ 用法: python admin.py process <ID> [指令]")
            return
        pending_id = sys.argv[2]
        instruction = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        cmd_process(pending_id, instruction)

    elif command == "send":
        if len(sys.argv) < 4:
            print("❌ 用法: python admin.py send <chat_id> <消息>")
            return
        chat_id = sys.argv[2]
        message = " ".join(sys.argv[3:])
        cmd_send(chat_id, message)

    elif command == "reply":
        if len(sys.argv) < 3:
            print("❌ 用法: python admin.py reply <消息>")
            return
        message = " ".join(sys.argv[2:])
        cmd_reply(message)

    elif command == "recent":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        cmd_recent(lines)

    elif command == "sessions":
        cmd_sessions()

    elif command == "cancel":
        cmd_cancel()

    elif command == "override":
        if len(sys.argv) < 3:
            print("❌ 用法: python admin.py override <指令>")
            return
        instruction = " ".join(sys.argv[2:])
        cmd_override(instruction)

    else:
        print(f"❌ 未知命令: {command}")
        cmd_help()


if __name__ == "__main__":
    main()
