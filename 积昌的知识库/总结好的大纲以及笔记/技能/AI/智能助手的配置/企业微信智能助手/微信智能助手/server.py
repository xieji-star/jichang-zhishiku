"""
企业微信消息回调服务 (WeCom Callback Service)
==============================================
接收企业微信推送的消息和文件，自动调用 Claude CLI 处理，
将处理结果写入 Obsidian Vault，并通过企业微信回复用户。

架构:
  微信 → 企业微信 → LocalTunnel → 本服务 → Claude CLI → Obsidian Vault
"""

import asyncio
import hashlib
import json
import logging
import os
import queue
import re
import subprocess
import sys
import threading
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import PlainTextResponse, Response
from wechatpy.enterprise import WeChatClient
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import WeChatException

# ============================================================
# 配置加载
# ============================================================

def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        print(f"[错误] 配置文件不存在: {config_path}")
        print("请复制 config.json 并填入你的企业微信配置")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 验证必要字段
    wecom = config.get("wecom", {})
    required_fields = ["corp_id", "secret", "token", "encoding_aes_key"]
    missing = [f for f in required_fields if wecom.get(f, "").startswith("YOUR_")]
    if missing:
        print(f"[警告] 以下企业微信配置尚未填写: {missing}")
        print("请在企业微信管理后台获取这些信息，填入 wecom-service/config.json")
        # 不退出，允许先启动服务再配置

    return config


CONFIG = load_config()

# ============================================================
# 日志配置
# ============================================================

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "wecom-service.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("wecom-service")

# ============================================================
# 全局状态
# ============================================================

# 任务队列：确保 Claude CLI 单实例运行，避免并发冲突
task_queue: queue.Queue = queue.Queue()
is_processing = False
processing_lock = threading.Lock()

# 最近接收到的文件（用于关联后续文字命令）
last_received_file: Optional[dict] = None

# ============================================================
# 初始化 WeChat 加密和客户端
# ============================================================

wecom_config = CONFIG["wecom"]

# 注意：wechatpy 的 WeChatClient 使用 corp_id 作为 appid 参数
# 企业微信的 secret 是应用的 secret
is_configured = not wecom_config.get("corp_id", "").startswith("YOUR_")

# 加密模块：仅在配置完整时初始化
if is_configured:
    try:
        crypto = WeChatCrypto(
            token=wecom_config["token"],
            encoding_aes_key=wecom_config["encoding_aes_key"],
            corp_id=wecom_config["corp_id"],
        )
        logger.info("企业微信加密模块初始化成功")
    except Exception as e:
        logger.error(f"企业微信加密模块初始化失败: {e}")
        crypto = None
        is_configured = False
else:
    crypto = None
    logger.warning("企业微信未配置，加密模块暂不可用")

if is_configured:
    try:
        wecom_client = WeChatClient(
            corp_id=wecom_config["corp_id"],
            secret=wecom_config["secret"],
        )
        logger.info("企业微信客户端初始化成功")
    except Exception as e:
        logger.error(f"企业微信客户端初始化失败: {e}")
        wecom_client = None
else:
    logger.warning("企业微信未配置，API 功能（发送消息、下载文件）暂不可用")
    wecom_client = None

# ============================================================
# HTTP 客户端（用于下载媒体文件）
# ============================================================

http_client = httpx.Client(timeout=httpx.Timeout(60.0))

# ============================================================
# FastAPI 应用
# ============================================================

app = FastAPI(
    title="WeCom Callback Service",
    description="企业微信消息回调服务 - 连接微信与 Claude/Obsidian",
    version="1.0.0",
)


# ============================================================
# 辅助函数
# ============================================================

def get_access_token() -> Optional[str]:
    """获取企业微信 access_token"""
    if not wecom_client:
        return None
    try:
        # wechatpy 自动管理 token 缓存和刷新
        token = wecom_client.access_token
        return token
    except Exception as e:
        logger.error(f"获取 access_token 失败: {e}")
        return None


def download_media(media_id: str) -> Optional[bytes]:
    """通过企业微信 API 下载媒体文件"""
    token = get_access_token()
    if not token:
        logger.error("无法获取 access_token，跳过文件下载")
        return None

    url = f"https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={token}&media_id={media_id}"

    try:
        response = http_client.get(url)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                # 返回了错误 JSON
                error_data = response.json()
                logger.error(f"下载媒体文件失败: {error_data}")
                return None
            logger.info(f"成功下载媒体文件，大小: {len(response.content)} bytes")
            return response.content
        else:
            logger.error(f"下载媒体文件 HTTP 错误: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"下载媒体文件异常: {e}")
        return None


def send_text_message(user_id: str, content: str) -> bool:
    """通过企业微信 API 发送文本消息给用户"""
    if not wecom_client:
        logger.warning("企业微信客户端未配置，无法发送消息")
        return False

    try:
        agent_id = int(wecom_config.get("agent_id", 0))
        if not agent_id:
            logger.error("agent_id 未配置")
            return False

        wecom_client.message.send_text(
            agent_id=agent_id,
            user_ids=[user_id],
            content=content,
        )
        logger.info(f"已发送回复消息给用户 {user_id}")
        return True
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return False


def parse_xml_message(xml_str: str) -> dict:
    """解析解密后的 XML 消息为字典"""
    try:
        root = ET.fromstring(xml_str)
        msg = {}
        for child in root:
            msg[child.tag] = child.text or ""
        return msg
    except ET.ParseError as e:
        logger.error(f"XML 解析失败: {e}")
        return {}


def generate_claude_prompt(msg_type: str, msg_data: dict, file_path: Optional[str] = None) -> str:
    """
    根据消息类型生成 Claude CLI 的 prompt
    """
    vault_config = CONFIG["vault"]
    default_dir = vault_config["default_output_dir"]

    content = msg_data.get("Content", "").strip()
    from_user = msg_data.get("FromUserName", "未知用户")

    if msg_type == "text":
        # 检查是否是已知命令
        if content.startswith("整理笔记"):
            parts = content.replace("整理笔记", "").strip().split()
            path = parts[0] if len(parts) > 0 else default_dir
            name = parts[1] if len(parts) > 1 else "未命名笔记"

            if file_path:
                return f"""🔴 自动化任务 — 来自企业微信（用户: {from_user}）

请使用 meeting-summary skill 处理以下文件：
- 文件路径: {file_path}
- 存储路径: {default_dir}/{path}/
- 笔记名称: {name}
- 内容来源: 企业微信文件

Step 0 的三个前置问题已由用户在企业微信消息中回答，请直接使用上述信息，无需再询问。
处理完成后请将文件写入磁盘，并简要回复处理结果（100字以内）。"""
            else:
                return f"""🔴 自动化任务 — 来自企业微信（用户: {from_user}）

用户发送了"整理笔记"命令但没有附带文件。最近也没有收到文件。
请回复用户：请先发送需要整理的文件（PDF/文档），然后再发送"整理笔记 [文件夹名] [笔记名称]"命令。
回复时要简短（50字以内）。"""

        elif content == "/帮助" or content == "帮助" or content == "help":
            return f"""🔴 自动化任务 — 来自企业微信（用户: {from_user}）

用户请求帮助。请生成企业微信机器人的帮助信息，说明支持的命令：
1. 发送文件 → 自动保存
2. 发送"整理笔记 [文件夹] [名称]" → 整理最近收到的文件
3. 发送"/搜索 [关键词]" → 搜索知识库
4. 发送"/帮助" → 显示此帮助
5. 直接发送自然语言指令也可以

回复要简洁清晰（150字以内），格式适合微信阅读。"""

        elif content.startswith("/搜索") or content.startswith("搜索"):
            keyword = content.replace("/搜索", "").replace("搜索", "").strip()
            return f"""🔴 自动化任务 — 来自企业微信（用户: {from_user}）

用户搜索关键词: {keyword}
请在 Vault 中搜索相关内容（使用 Grep 工具搜索 "总结好的大纲以及笔记/" 目录），
将搜索结果整理成简要列表回复给用户。每项附带文件路径。回复在 200 字以内。"""

        else:
            # 自然语言指令，直接交给 Claude 处理
            return f"""🔴 自动化任务 — 来自企业微信（用户: {from_user}）

用户消息: {content}

请理解用户意图并执行。如果涉及文件处理，请告知用户需要先发送文件。
处理完成后简要回复结果（200字以内），并将任何生成的笔记写入 Vault。"""

    elif msg_type == "file":
        # 纯文件消息，无文字说明
        file_name = msg_data.get("Title", "未命名文件")
        return f"""🔴 自动化任务 — 来自企业微信（用户: {from_user}）

收到文件: {file_name}
文件路径: {file_path}

用户未提供额外说明。请分析文件内容，然后询问用户：
1. 是否需要整理为笔记？
2. 如需整理，存放在哪个文件夹？叫什么名字？

注意：这是通过企业微信的回复，请用简洁的文字回复（100字以内）。"""

    return f"收到来自企业微信的未知类型消息: {msg_type}"


def run_claude_task(prompt: str) -> str:
    """
    调用 Claude CLI 执行任务
    返回 Claude 的输出文本
    """
    vault_root = CONFIG["vault"]["root_path"]
    claude_config = CONFIG["claude"]
    settings_path = Path(__file__).parent / "claude-settings.json"

    cmd = [
        claude_config.get("cli_path", "claude"),
        "-p", prompt,
        "--settings", str(settings_path),
        "--output-format", "text",
        "--max-budget-usd", str(claude_config["max_budget_usd"]),
        "--no-session-persistence",  # 不保存会话，避免积累
    ]

    logger.info(f"执行 Claude CLI: cd {vault_root} && claude -p ...")
    logger.debug(f"Prompt 内容: {prompt[:200]}...")

    # 构造环境变量：继承当前进程环境 + 添加 Claude/DeepSeek 认证配置
    # 注：nssm 服务以 LocalSystem 运行，无法读取用户目录下的 settings.json
    # 因此从 config.json 中读取 API 配置作为环境变量传递
    env = os.environ.copy()
    claude_env = claude_config.get("env", {})
    for key, value in claude_env.items():
        env[key] = value
        # 模糊日志输出，隐藏完整 token
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
            env=env,  # 传递自定义环境变量
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


def process_task(task: dict):
    """
    在后台线程中处理任务（文件下载 + Claude 调用 + 发送回复）
    """
    global is_processing, last_received_file

    with processing_lock:
        is_processing = True

    try:
        msg_type = task["msg_type"]
        msg_data = task["msg_data"]
        from_user = msg_data.get("FromUserName", "")

        file_path = None

        # 如果是文件消息，先下载文件
        if msg_type == "file" or (msg_type == "text" and last_received_file):
            media_id = msg_data.get("MediaId", "")
            if not media_id and last_received_file:
                media_id = last_received_file.get("MediaId", "")
                file_path = last_received_file.get("local_path", "")

            if media_id and not file_path:
                # 下载文件
                logger.info(f"下载媒体文件: {media_id}")
                send_text_message(from_user, "⏳ 正在下载文件...")

                file_data = download_media(media_id)
                if file_data:
                    # 保存文件
                    file_name = msg_data.get("Title", f"wecom_file_{int(time.time())}")
                    resources_dir = Path(CONFIG["vault"]["root_path"]) / CONFIG["vault"]["resources_dir"]
                    resources_dir.mkdir(exist_ok=True)

                    file_path = str(resources_dir / file_name)
                    with open(file_path, "wb") as f:
                        f.write(file_data)

                    logger.info(f"文件已保存: {file_path}")
                    send_text_message(from_user, f"✅ 文件已接收: {file_name}\n⏳ 正在调用 AI 处理...")
                else:
                    send_text_message(from_user, "❌ 文件下载失败，请稍后重试。")
                    return

        # 如果有文件，先更新 last_received_file 引用
        if file_path:
            task["file_path"] = file_path

        # 生成 prompt 并调用 Claude
        prompt = task.get("prompt") or generate_claude_prompt(
            msg_type, msg_data, task.get("file_path")
        )

        send_text_message(from_user, "🤖 AI 正在处理，请稍候（可能需要1-3分钟）...")

        claude_output = run_claude_task(prompt)

        # 截断过长输出
        max_reply_length = 1500
        if len(claude_output) > max_reply_length:
            claude_output = claude_output[:max_reply_length] + "\n\n... (内容过长已截断，完整结果请查看 Obsidian Vault)"

        # 发送回复
        reply = f"📋 处理完成:\n\n{claude_output}"
        send_text_message(from_user, reply)

        # 清理 last_received_file
        if last_received_file and task.get("file_path") == last_received_file.get("local_path"):
            last_received_file = None

    except Exception as e:
        logger.error(f"任务处理异常: {e}\n{traceback.format_exc()}")
        from_user = task.get("msg_data", {}).get("FromUserName", "")
        if from_user:
            send_text_message(from_user, f"❌ 处理出错: {str(e)[:200]}")

    finally:
        with processing_lock:
            is_processing = False


def task_worker():
    """
    后台任务工作线程，从队列中取任务并处理
    """
    logger.info("任务工作线程已启动")
    while True:
        try:
            task = task_queue.get(timeout=1)
            logger.info(f"开始处理任务: {task.get('msg_type')} from {task.get('msg_data', {}).get('FromUserName', 'unknown')}")
            process_task(task)
            logger.info("任务处理完成")
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"任务工作线程异常: {e}")


# 启动后台工作线程
worker_thread = threading.Thread(target=task_worker, daemon=True, name="TaskWorker")
worker_thread.start()


# ============================================================
# API 端点
# ============================================================

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "wecom-callback-service",
        "wecom_configured": is_configured,
        "tasks_queued": task_queue.qsize(),
        "is_processing": is_processing,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/wecom/callback")
async def wecom_verify(
    msg_signature: str = Query(..., alias="msg_signature"),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...),
):
    """
    企业微信 URL 验证（GET 请求）
    企业微信在配置回调 URL 时会发送 GET 请求验证
    """
    logger.info(f"收到 URL 验证请求: timestamp={timestamp}, nonce={nonce}")

    if crypto is None:
        logger.error("企业微信未配置，无法处理 URL 验证")
        return PlainTextResponse(content="服务未配置", status_code=503)

    try:
        # wechatpy 的 check_signature 返回解密后的 echo_str
        decrypted = crypto.check_signature(msg_signature, timestamp, nonce, echostr)
        logger.info("URL 验证成功")
        return PlainTextResponse(content=decrypted)
    except WeChatException as e:
        logger.error(f"URL 验证失败: {e}")
        return PlainTextResponse(content=f"验证失败: {e}", status_code=403)
    except Exception as e:
        logger.error(f"URL 验证异常: {e}")
        return PlainTextResponse(content=f"验证异常: {e}", status_code=500)


@app.post("/wecom/callback")
async def wecom_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    msg_signature: str = Query(..., alias="msg_signature"),
    timestamp: str = Query(...),
    nonce: str = Query(...),
):
    """
    企业微信消息回调（POST 请求）
    接收用户发送的消息和文件
    """
    global last_received_file

    # 获取原始 XML 请求体
    raw_body = await request.body()
    xml_str = raw_body.decode("utf-8")

    logger.info(f"收到消息回调: timestamp={timestamp}, nonce={nonce}, body_len={len(raw_body)}")
    logger.info(f"原始 XML (前300字): {xml_str[:300]}")
    logger.info(f"请求头: content-type={request.headers.get('content-type', 'unknown')}, ip={request.client.host if request.client else 'unknown'}")

    if crypto is None:
        logger.error("企业微信未配置，无法解密消息")
        return PlainTextResponse(content="success")

    try:
        # 解密消息
        decrypted_xml = crypto.decrypt_message(xml_str, msg_signature, timestamp, nonce)
        logger.info(f"解密后完整 XML: {decrypted_xml}")

        # 解析消息
        msg_data = parse_xml_message(decrypted_xml)
        if not msg_data:
            logger.error("消息解析失败")
            return PlainTextResponse(content="success")  # 仍返回 success 避免重试

        msg_type = msg_data.get("MsgType", "")
        from_user = msg_data.get("FromUserName", "")
        msg_id = msg_data.get("MsgId", msg_data.get("MsgID", ""))

        logger.info(f"消息类型: {msg_type}, MsgId: {msg_id}, 来自: {from_user}")

        # 打印所有字段（用于调试）
        logger.info(f"消息所有字段: {dict(msg_data.items())}")

        if msg_type == "text":
            content = msg_data.get("Content", "")
            logger.info(f"文本消息: {content[:200]}")

            # 加入任务队列
            task = {
                "msg_type": msg_type,
                "msg_data": msg_data,
                "timestamp": time.time(),
            }

            # 如果有最近接收的文件，关联到任务
            if last_received_file:
                task["file_path"] = last_received_file.get("local_path", "")
                task["file_info"] = last_received_file
                logger.info(f"关联最近文件: {last_received_file.get('title', '')}")

            task_queue.put(task)

        elif msg_type == "file":
            title = msg_data.get("Title", "未知文件")
            media_id = msg_data.get("MediaId", "")
            file_key = msg_data.get("FileKey", msg_data.get("Filekey", ""))
            logger.info(f"📎 文件消息: {title}")
            logger.info(f"   MediaId={media_id[:30] if media_id else '空'}...")
            logger.info(f"   FileKey={file_key[:30] if file_key else '空'}...")
            logger.info(f"   所有字段: {dict(list(msg_data.items())[:10])}")

            # 保存文件信息
            last_received_file = {
                "media_id": media_id,
                "title": title,
                "from_user": from_user,
                "timestamp": time.time(),
                "local_path": None,  # 会在处理时下载
            }

            # 加入任务队列（先下载并保存文件）
            task = {
                "msg_type": msg_type,
                "msg_data": msg_data,
                "timestamp": time.time(),
            }
            task_queue.put(task)

        elif msg_type == "event":
            event_type = msg_data.get("Event", "")
            logger.info(f"事件消息: Event={event_type}, 完整数据: {dict(msg_data.items())}")
            # 暂不处理事件，返回 success

        else:
            logger.warning(f"不支持的消息类型: {msg_type}, 完整数据: {dict(msg_data.items())}")

        # 重要：必须返回 "success" 字符串，否则企业微信会重试
        return PlainTextResponse(content="success")

    except WeChatException as e:
        logger.error(f"消息解密失败: {e}")
        return PlainTextResponse(content="success")  # 仍返回 success
    except Exception as e:
        logger.error(f"消息处理异常: {e}\n{traceback.format_exc()}")
        return PlainTextResponse(content="success")  # 仍返回 success


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    import argparse
    import signal
    import uvicorn

    parser = argparse.ArgumentParser(description="企业微信消息回调服务")
    parser.add_argument("--with-tunnel", action="store_true", help="自动启动 Cloudflare Tunnel")
    args = parser.parse_args()

    server_config = CONFIG["server"]

    logger.info("=" * 60)
    logger.info("企业微信消息回调服务 v1.0.0")
    logger.info(f"监听地址: {server_config['host']}:{server_config['port']}")
    logger.info(f"Vault 路径: {CONFIG['vault']['root_path']}")
    logger.info(f"企业微信配置: {'已配置' if is_configured else '未配置 - 请编辑 config.json'}")

    tunnel_process = None
    tunnel_url = None
    if args.with_tunnel:
        # 使用 LocalTunnel（基于 Node.js 的隧道工具）替代 Cloudflare Tunnel
        # Cloudflare WARP 会劫持 cloudflared 的 DNS/流量导致无法连接
        # LocalTunnel 通过 HTTPS WebSocket 连接，不受 WARP 影响
        lt_path = r"C:\Users\asus\AppData\Roaming\npm\lt.cmd"
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        tunnel_log = log_dir / "tunnel.log"

        # 生成唯一子域名：基于 CorpID 的哈希，确保每次重启 URL 不变
        corp_id = wecom_config.get("corp_id", "default")
        subdomain_hash = hashlib.sha256(corp_id.encode()).hexdigest()[:10]
        desired_subdomain = f"jichang-vault-{subdomain_hash}"

        logger.info(f"期望子域名: {desired_subdomain}")

        # 先杀掉旧的 lt/node 进程，释放子域名
        try:
                subprocess.run(
                        ["taskkill", "/F", "/IM", "node.exe"],
                        capture_output=True, timeout=5
                )
                time.sleep(2)
        except Exception:
                pass

        logger.info(f"启动 LocalTunnel (via: {lt_path})")
        # 清空旧日志，避免匹配到之前的 URL
        with open(tunnel_log, "w") as f:
            f.write("")
        tunnel_process = subprocess.Popen(
            [lt_path, "--port", str(server_config['port']),
             "--subdomain", desired_subdomain],  # 固定子域名，重启后 URL 不变
            stdout=open(tunnel_log, "a"),
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        logger.info(f"Tunnel 进程 PID: {tunnel_process.pid}")

        # 等待 Tunnel URL 出现（最长等 60 秒）
        for i in range(60):
            time.sleep(1)
            try:
                with open(tunnel_log, "r") as f:
                    content = f.read()
                    for line in content.split("\n"):
                        if "your url is:" in line.lower():
                            match = re.search(r"https://[a-zA-Z0-9-]+\.loca\.lt", line)
                            if match:
                                tunnel_url = match.group(0)
                                logger.info(f"检测到 Tunnel URL: {tunnel_url}")
                                if desired_subdomain not in tunnel_url:
                                    logger.warning(f"子域名 {desired_subdomain} 被占用，将使用随机子域名")
                                break
                if tunnel_url:
                    break
            except Exception:
                pass

        # 保存 URL 到文件以便用户查看
        url_file = Path(__file__).parent / "current-tunnel-url.txt"
        if tunnel_url:
            with open(url_file, "w") as f:
                f.write(tunnel_url)
            callback_url = f"{tunnel_url}/wecom/callback"
            logger.info("=" * 60)
            logger.info(f"当前 Tunnel URL: {tunnel_url}")
            logger.info(f"回调 URL: {callback_url}")
            logger.info("请将此 URL 手动更新到企业微信管理后台:")
            logger.info(f"   应用管理 -> 知识库助手 -> 接收消息 -> 设置API接收")
            logger.info(f"   URL: {callback_url}")
            logger.info("=" * 60)
        else:
            logger.error("未能获取 Tunnel URL，请检查 localtunnel 是否正常启动")
            with open(url_file, "w") as f:
                f.write("ERROR: 未能获取 Tunnel URL")

    logger.info("=" * 60)

    # 注册退出清理
    def cleanup():
        logger.info("正在关闭服务...")
        if tunnel_process:
            tunnel_process.terminate()
            logger.info("Tunnel 进程已终止")

    signal.signal(signal.SIGTERM, lambda s, f: cleanup())
    signal.signal(signal.SIGINT, lambda s, f: cleanup())

    try:
        uvicorn.run(
            app,
            host=server_config["host"],
            port=server_config["port"],
            log_level="info",
        )
    finally:
        cleanup()
