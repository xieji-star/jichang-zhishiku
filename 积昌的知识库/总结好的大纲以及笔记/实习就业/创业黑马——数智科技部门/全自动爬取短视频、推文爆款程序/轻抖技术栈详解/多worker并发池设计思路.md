---
title: "多worker并发池设计思路"
type: 技术方案落地
date: 2026-08-13
tags:
  - 多worker并发池
  - 任务队列
  - 受控并发
  - 限流
  - 重试
  - 缓存
  - 断点续跑
  - 稳定性
  - 技术栈
  - 轻抖
source: 自研平台批量化处理路线.md / 0811开发日志.md / GitHub 公开调研
---

# 🏗️ 多worker并发池设计思路：把"受控并发+限速队列+缓存+断点续跑"落地成稳定优先的生产线

> [!summary] 概要
> **一句话结论：用"1 个调度器 + N 个受限 worker + 限速器 + 重试器 + SQLite 持久化队列 + 缓存"把批量化口播稿做成一条稳定优先的生产线。** 本文把上一份方案评审 [[自研平台批量化处理路线]] 中的核心结论（**受控并发 2~3 路 + 限速 + 指数退避重试 + 缓存 + 断点续跑**，而不是"复制 10 路并联"）落实成**可直接照着做的设计文档**：先给整体架构与六个核心组件，再逐层给出技术栈选型（每个都附 GitHub 高 Star 项目源地址），最后给出"从零到上线"的分步实施清单（每步做什么、怎么做、验收标准、代码骨架）。
>
> 🔥 **<span style="color:#e74c3c">核心约束：稳定 > 速度。</span>** 宁可一次跑慢一点，也绝不允许：批量失败、任务丢失、中途断电从头再来、被平台限流封号。**所有参数一律保守起步，验证稳定后再逐步放开。**

## 相关笔记

- [[自研平台批量化处理路线]] — 本文的方案评审姊妹篇（为什么不能"复制 10 路并联"、瓶颈定性、三组定位实验）
- [[轻抖VS我们的项目]] — 需求来源：自家"下载+ASR" vs 轻抖"字幕直取+缓存"的差距分析
- [[轻抖-如何快速实现口播稿件的抓取]] — 轻抖"四板斧"原理（字幕直取/缓存/云端/前后端分工）
- [[口播稿转录]] — 口播稿产业链全景与"链接直出"三路径
- [[mediacrawler_to_pyvideotrans.py]] — 现成参考脚本：MediaCrawler 导出 → yt-dlp 下载 → pyvideotrans 批量转写（含断点续跑雏形）
- [[本地部署短视频分析程序介绍文档（改良版）]] — 自家系统全貌（MediaCrawler + SenseVoice + SQLite + 飞书出口）
- [[0811-开发日志]] — 当前实证：单条 30~98s、120s 硬上限、批量 0% 成功、RTX 5060 / 31GB 内存

## 索引

- 🎯 [[#1. 目标与设计约束]] — 要什么、不要什么：稳定优先的三条铁律
- 🏗️ [[#2. 整体架构：调度器 + 受限 Worker 池]] — 六个核心组件与数据流
- 🧰 [[#3. 技术栈选型（含 GitHub 高 Star 源地址）]] — 八层技术选型表 + 每层推荐理由
- 🌟 [[#4. GitHub 高 Star 项目清单（可直接下载）]] — 采集/ASR/队列/限流重试/一站式分类速查
- 🪜 [[#5. 逐步实施：每一步做什么、怎么做]] — 六步从串行到受控并发，附代码骨架与验收标准
- 🛡️ [[#6. 稳定性设计清单（对照自检）]] — 断点/幂等/隔离/限速/监控 14 条红线
- 📚 [[#7. 参考来源]] — 各项目源地址与调研来源
- ✅ [[#8. 总结与落地路线]] — 一句话结论 + 分阶段排期

---

## 1. 目标与设计约束

### 1.1 目标

| 需求 | 说明 |
|------|------|
| **输入** | 一次提交 10~20 条抖音/短视频链接 |
| **输出** | 每条返回口播稿文本 + 成功/失败/跳过清单 + 进度 |
| **速度** | 不追求极限，20 条在可接受时间内完成即可（命中缓存秒回；需抓字幕约 1~2s/条；无字幕走本地 ASR 约 30~90s/条） |
| **体验** | 像"提交一个任务"，提交后能看到进度，中断后能接着跑 |

### 1.2 硬性约束：稳定优先的三条铁律

> 🔥 **<span style="color:#e74c3c">铁律一：宁可慢，不可挂。</span>** 任何时刻不允许 10 路同时打平台接口，瞬时请求数必须受控。
>
> 🔥 **<span style="color:#e74c3c">铁律二：宁可重试，不可丢。</span>** 每条任务状态落盘，进程被杀/断电/断网都能从断点接着跑，绝不重复下载，也绝不跳过。
>
> 🔥 **<span style="color:#e74c3c">铁律三：宁可失败单条，不可拖垮整批。</span>** 单条失败标记 `failed` 并记录原因，其余任务继续，最后汇总。

### 1.3 为什么不上 Celery 全家桶（先泼冷水）

- 你现在是**单机 + 个人电脑 + 一次 10~20 条**的小规模场景，Celery 需要常驻 worker 进程 + Redis/RabbitMQ 服务，运维负担远大于收益
- **推荐路线：先用"纯 Python 脚本 + asyncio + SQLite"把管线跑稳**，只有未来多机/团队协作/定时海量任务时，再升级到 RQ 或 Celery（第 5.7 节给升级路径）
- 这条"先轻后重"的路线，正是你在 [[mediacrawler_to_pyvideotrans.py]] 里已经走对的方向（脚本化 + results.csv 断点），本文把它系统化

---

## 2. 整体架构：调度器 + 受限 Worker 池

### 2.1 架构图

```
用户一次提交 10~20 条链接
        ↓
① 任务入队（SQLite tasks 表，状态 pending）
        ↓
② 调度器（主循环，从 pending 取任务）
        ↓
③ 受限 Worker 池（asyncio.Semaphore(2~3)）
   Worker 内部分 4 段，每段都有 限速+重试 保护：
   ├─ 先查缓存（video_id → 命中直接秒回，不消耗平台请求）
   ├─ 解析链接（短链 → 无水印直链；失败 → 指数退避重试）
   ├─ 字幕直取（优先；限速间隔 0.3~1s，失败退避）
   │    └─ 无字幕 → 下载+ASR 兜底（ffmpeg 抽音频 → SenseVoice/faster-whisper）
   └─ 结果写缓存 + 落库（status → done/failed）
        ↓
④ 全部处理完 → 汇总（成功/失败/跳过清单 + 耗时）
```

### 2.2 六个核心组件

| # | 组件 | 职责 | 关键设计 |
|:-:|------|------|---------|
| ① | **任务队列（SQLite tasks 表）** | 承接 10~20 条链接，记录每条状态 | `pending → doing → done/failed`，断点续跑的唯一依据 |
| ② | **调度器（主循环）** | 从 pending 取任务、交给 worker、收结果 | 单线程取任务即可，不必复杂 |
| ③ | **受限 Worker 池** | 真正干活：解析/字幕直取/ASR | `asyncio.Semaphore(2~3)` 钉死并发度 |
| ④ | **限速器** | 控制对平台接口的请求频率 | `aiolimiter` 漏桶，默认 1 请求/秒起步 |
| ⑤ | **重试器** | 429/403/超时自动退避重试 | `tenacity` 指数退避 `1s→2s→4s`，最多 3 次 |
| ⑥ | **缓存（SQLite cache 表）** | `video_id → 口播稿`，命中秒回 | 与 tasks 表同库或 Redis，是"看似秒出"的关键 |

### 2.3 数据流（单条任务的生命周期）

```
url → video_id = md5(url)[:12]
  1. check_cache(video_id)      → 命中 → done（0.3s，零请求）
  2. status=doing 落盘
  3. parse_link(url)            → 直链（限速+重试）
  4. fetch_subtitle(直链)       → 有字幕 → 文本（限速+重试）
  5. 无字幕 → download+ASR      → 文本（慢，但稳定）
  6. write_cache(video_id, 文本) + status=done 落盘
失败任一步 → status=failed + error 落盘 → 继续下一条
```

---

## 3. 技术栈选型（含 GitHub 高 Star 源地址）

### 3.1 技术栈总览表

> 📌 **<span style="color:#2980b9">Star 数据截至 2026-08 公开调研，以仓库实际为准；"★"为约数。</span>**

| 层 | 选型（方案） | GitHub 项目 | Star | 为什么是它 |
|----|-------------|-------------|:---:|-----------|
| ① 语言/运行时 | Python 3.10+ | - | - | 你已有 3.13，pyvideotrans 需 3.10 隔离环境 |
| ② 异步 HTTP | **httpx** | [encode/httpx](https://github.com/encode/httpx) | ~15K | 同步/异步双 API，连接池，超时可控 |
| ③ 并发控制 | `asyncio.Semaphore` | 标准库 | - | 受控并发 2~3 路，零依赖最稳 |
| ④ 限速 | **aiolimiter** | [mjpieters/aiolimiter](https://github.com/mjpieters/aiolimiter) | ~775 | asyncio 漏桶限速的事实标准（Microsoft GraphRAG 也在用） |
| ⑤ 重试 | **tenacity** | [jd/tenacity](https://github.com/jd/tenacity) | ~8.7K | 指数退避/重试条件/最大次数，最成熟的 Python 重试库 |
| ⑥ 任务队列（轻） | **APScheduler** | [agronholm/apscheduler](https://github.com/agronholm/apscheduler) | ~7.4K | 轻量任务调度，支持 SQLite 持久化，无需常驻服务 |
| ⑦ 任务队列（重/多机） | **RQ / Celery** | [rq/rq](https://github.com/rq/rq) / [celery/celery](https://github.com/celery/celery) | ~8-10K / ~22-28K | 多机/团队协作时再升级（第 5.7 节） |
| ⑧ 存储/缓存 | **SQLite（WAL 模式）** | 标准库 | - | 单机零成本，断点续跑；并发写用 WAL 减少锁 |
| ⑨ 采集/下载 | **yt-dlp** | [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | ~147K | 全平台视频/音频下载，自带签名解析 |
| ⑩ ASR 转写 | **faster-whisper / SenseVoice** | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) / [FunAudioLLM/SenseVoice](https://github.com/FunAudioLLM/SenseVoice) | ~24.8K / ~9K | 中文口播稿：SenseVoice/FunASR 更优；通用则 faster-whisper |
| ⑪ 一站式转写（可选） | **pyvideotrans** | [jianchang512/pyvideotrans](https://github.com/jianchang512/pyvideotrans) | ~18.6K | 你已接入，CLI 批量 `--task stt`，含多引擎 |

### 3.2 并发控制层（核心中的核心）

**选型：`asyncio.Semaphore(2)` 或 `concurrent.futures.ThreadPoolExecutor(max_workers=2~3)`**

- 你的闭环现在是**字幕直取（API 请求型）**，最怕瞬时并发——所以并发度**宁可小不可大**，从 `2` 起步
- asyncio 单线程 + 协程，天然避免"共享 Session 竞态"；如果你要复用**同步的 pyvideotrans 子进程调用**，则用线程池（ThreadPoolExecutor）更省事
- 📊 **<span style="color:#e67e22">并发度怎么定：先做 [[自研平台批量化处理路线]] 第 3 节的"10 条串行测安全 QPS"实验，拿到"单位时间最多安全发几条"，再反推并发度。</span>**

### 3.3 限流层

**选型：`aiolimiter.AsyncLimiter`**

```python
from aiolimiter import AsyncLimiter
rate = AsyncLimiter(1, 1)      # 每秒最多 1 次（保守起步）
# 用法：async with rate:  await 请求...
```

- 漏桶算法，天然支持"每秒 N 次"或"每 N 秒 1 次"
- ⚠️ 它 Star 不高（~775），但**这是 asyncio 限流唯一的事实标准**，连 Microsoft GraphRAG 都在用——**选型看"是不是事实标准"，不完全看 Star**
- 备选：`httpx-limiter`（基于 httpx 的限速 transport），适合喜欢声明式配置的场景

### 3.4 重试层

**选型：`tenacity`**

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(stop=stop_after_attempt(3),                     # 最多 3 次
       wait=wait_exponential(multiplier=1, max=8),     # 1s→2s→4s→8s 退避
       retry=retry_if_exception_type((httpx.TimeoutException,
                                      httpx.HTTPStatusError)))
async def safe_request(...):
    ...
```

- 429/403/超时才重试，**业务性失败（如"链接无效"）不重试**，直接标记 failed
- 退避加**抖动**（`wait_random`）可进一步降低同时重试的撞车概率（可选）

### 3.5 任务队列层

| 场景 | 选型 | 说明 |
|------|------|------|
| **单机、个人电脑、10~20 条（你现在）** | **自研 asyncio 主循环 + SQLite 状态表** | 零依赖、最稳，见第 5 节代码骨架 |
| 需要定时调度/稍重一点 | **APScheduler** | 支持 SQLite 持久化、cron/interval 触发，无需常驻队列服务 |
| 多机/团队协作/海量任务（未来） | **RQ（简单）→ Celery（重但最成熟）** | RQ 只依赖 Redis，Celery 功能最全但运维重 |
| 全异步 + Redis | **arq** | asyncio 原生，轻量，适合纯异步栈 |

> 💡 **<span style="color:#2980b9">本文主推"自研 asyncio 主循环 + SQLite"，因为你的场景足够小，复杂度越低越稳定。</span>** 队列库是"当复杂度真的超过手写范围"时的升级项，不是必需品。

### 3.6 存储/缓存层

**选型：SQLite，开启 WAL 模式**

```sql
PRAGMA journal_mode=WAL;   -- 并发读友好，减少 database is locked
PRAGMA busy_timeout=5000;  -- 写锁等待 5s，避免立即报错
```

- **tasks 表**：`id / url / status / attempts / result / error / ts`（断点续跑）
- **cache 表**：`video_id / result / ts`（命中秒回）
- 所有 SQLite 写入**只由主循环串行执行**（或集中到一个写入队列），worker 不直接写库——彻底避免写锁冲突

### 3.7 采集/下载层

| 项目 | Star | 用途 | 源地址 |
|------|:---:|------|--------|
| **yt-dlp** | ~147K | 通用下载，你已在用 | https://github.com/yt-dlp/yt-dlp |
| **MediaCrawler** | ~60K | 全平台采集（creator/search/detail），你已在用 | https://github.com/NanmiCoder/MediaCrawler |
| **Douyin_TikTok_Download_API** | ~19K | 抖音/快手异步高性能下载+API | https://github.com/Evil0ctal/Douyin_TikTok_Download_API |
| **f2** | ~2.6K | 抖音/快手/小红书多平台下载 | https://github.com/Johnserf-Seed/f2 |

### 3.8 转写层（ASR）

| 项目 | Star | 中文口播稿表现 | 源地址 |
|------|:---:|------|--------|
| **faster-whisper** | ~24.8K | 通用强、快 4 倍省内存，可用 | https://github.com/SYSTRAN/faster-whisper |
| **SenseVoice** | ~9K | 中文口语/语气词/标点更贴短视频（**你已在用**） | https://github.com/FunAudioLLM/SenseVoice |
| **FunASR** | ~19.7K | 阿里达摩院，中文 SOTA，含标点恢复 | https://github.com/modelscope/FunASR |
| **pyvideotrans** | ~18.6K | 一站式封装多引擎，CLI 可批量（**你已在用**） | https://github.com/jianchang512/pyvideotrans |
| Whisper | ~107K | 事实标准，中文可用但不如阿里系 | https://github.com/openai/whisper |

> 📊 **<span style="color:#e67e22">选型口诀：有字幕走"字幕直取"（零算力秒级）；无字幕中文口播稿走 SenseVoice/FunASR；要通用多语言走 faster-whisper。</span>** ASR 只做兜底，永远不是主力。

---

## 4. GitHub 高 Star 项目清单（可直接下载）

> 🔥 **<span style="color:#e74c3c">这一节专门给你"下载地址"，按层分类，全部可 `git clone` 或去仓库页下载。</span>** Star 数据截至 2026-08。

### 4.1 采集 / 下载层

| 项目 | Star | 一句话 | 源地址 |
|------|:---:|--------|--------|
| **yt-dlp** | ~147K | 全平台视频/音频下载，自带解析 | https://github.com/yt-dlp/yt-dlp |
| **MediaCrawler** | ~60K | 小红书/抖音/B站/快手全平台采集王者 | https://github.com/NanmiCoder/MediaCrawler |
| **Douyin_TikTok_Download_API** | ~19K | 抖音/快手异步高性能下载+API | https://github.com/Evil0ctal/Douyin_TikTok_Download_API |
| **f2** | ~2.6K | 抖音/快手/小红书多平台高速下载 | https://github.com/Johnserf-Seed/f2 |

### 4.2 ASR 转写层

| 项目 | Star | 一句话 | 源地址 |
|------|:---:|--------|--------|
| **Whisper** | ~107K | 语音识别事实标准 | https://github.com/openai/whisper |
| **faster-whisper** | ~24.8K | Whisper 加速版（CTranslate2，快 4 倍省内存） | https://github.com/SYSTRAN/faster-whisper |
| **FunASR** | ~19.7K | 阿里中文语音工具箱（SOTA，标点/热词） | https://github.com/modelscope/FunASR |
| **SenseVoice** | ~9K | 中/粤/英/日/韩 ASR + 情绪识别（你已用） | https://github.com/FunAudioLLM/SenseVoice |

### 4.3 任务队列 / 调度层

| 项目 | Star | 一句话 | 源地址 |
|------|:---:|--------|--------|
| **Celery** | ~22-28K | 最成熟分布式任务队列（重） | https://github.com/celery/celery |
| **RQ** | ~8-10K | 简单任务队列（Redis） | https://github.com/rq/rq |
| **APScheduler** | ~7.4K | 轻量任务调度（SQLite 持久化，无需常驻服务） | https://github.com/agronholm/apscheduler |
| **Dramatiq** | ~3.5-5K | "更好的 Celery"，快而可靠 | https://github.com/Bogdanp/dramatiq |
| **Huey** | ~4-6K | 轻量任务队列（Redis） | https://github.com/coleifer/huey |
| **arq** | ~3K | asyncio 原生异步队列 | https://github.com/python-arq/arq |

### 4.4 限流 / 重试 / HTTP 层

| 项目 | Star | 一句话 | 源地址 |
|------|:---:|--------|--------|
| **httpx** | ~15K | 下一代 Python HTTP 客户端（同步/异步） | https://github.com/encode/httpx |
| **tenacity** | ~8.7K | 最成熟的重试库（指数退避） | https://github.com/jd/tenacity |
| **aiolimiter** | ~775 | asyncio 漏桶限速事实标准 | https://github.com/mjpieters/aiolimiter |

### 4.5 一站式（下载+转写一体，可选）

| 项目 | Star | 一句话 | 源地址 |
|------|:---:|--------|--------|
| **pyvideotrans** | ~18.6K | 视频翻译配音一体化，内置多 ASR 引擎，CLI 可批量 | https://github.com/jianchang512/pyvideotrans |
| **VideoLingo** | ~18K | Netflix 级字幕对齐流水线 | https://github.com/Huanshere/VideoLingo |
| **KrillinAI** | ~10.7K | 下载→转录→翻译→配音，面向 Agent 有 API | https://github.com/krillinai/KrillinAI |
| **douyin-creator-toolkit** | ~689 | 抖音运营工具箱：**本地视频批量转写最多 50 个** + 链接批量提取 + 批量无水印下载 + AI 分析，**桌面免部署、MIT 开源免费** | https://github.com/lid664951-crypto/douyin-creator-toolkit |

> 💡 **<span style="color:#2980b9">安装建议：全部用 `pip install 包名`（httpx/tenacity/aiolimiter 等）或 `git clone 地址`（项目型如 MediaCrawler/pyvideotrans），并用独立 venv 隔离，避免污染其他项目环境。</span>**

> 🖥️ **<span style="color:#2980b9">douyin-creator-toolkit 补充说明（2026-08 核实）：** MIT License 完全免费可商用；技术栈 Tauri 2 + React + Rust，打包成 Windows 桌面 exe（`抖音运营工具箱_x64-setup.exe` 安装版或 `.zip` 绿色版）。**下载方式二选一：** ① GitHub Releases → https://github.com/lid664951-crypto/douyin-creator-toolkit/releases/latest ；② 百度网盘 → https://pan.baidu.com/s/1ZlUrG2yC18sklHc71cIMOA （提取码 `8888`，国内推荐）。**定位提醒：** 它是"桌面软件"，适合人工丢一批链接手动批量出稿，做**应急/一次性大批量**；但**不能嵌进自家平台后端做自动化调度**——自动化仍走本文第 5 节的 asyncio 管线（或对接 TikHub/火山 ASR 的 API）。</span>**

---

## 5. 逐步实施：每一步做什么、怎么做

> 🔥 **<span style="color:#e74c3c">铁律：每一小步跑稳了、验收过了，才进下一步。永远不要"一次性写满并发"。这是稳定优先的落地方式。</span>**

### 5.1 第一步：搭骨架（单 worker 串行，先跑通）

**做什么：** 把现有闭环（字幕直取/缓存 或 下载+ASR）包装成 `async def process_one(url) -> dict`，用最简单的 for 循环串行处理全部链接，**先不加任何并发**。

**怎么做：**

```python
import asyncio, hashlib, sqlite3
from pathlib import Path

DB = Path("koubo.db")

def init_db():
    con = sqlite3.connect(DB)
    con.executescript("""
        PRAGMA journal_mode=WAL;
        PRAGMA busy_timeout=5000;
        CREATE TABLE IF NOT EXISTS tasks(
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            status TEXT DEFAULT 'pending',   -- pending/doing/done/failed
            attempts INT DEFAULT 0,
            result TEXT, error TEXT, ts TEXT
        );
        CREATE TABLE IF NOT EXISTS cache(
            video_id TEXT PRIMARY KEY, result TEXT, ts TEXT
        );
    """)
    con.commit()
    return con

def video_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]

async def process_one(url: str) -> dict:
    """单条闭环：解析→字幕直取→无字幕则下载+ASR。复用你现有逻辑。"""
    vid = video_id(url)
    # ① 查缓存
    # ② 解析链接（短链→直链）
    # ③ 字幕直取（成功→text）
    # ④ 无字幕 → ffmpeg 抽音频 → SenseVoice/faster-whisper
    # ⑤ 返回 {"id":vid,"status":"ok","text":...} 或 {"status":"failed","error":...}
    ...

async def main(links: list[str]):
    con = init_db()
    for url in links:
        r = await process_one(url)          # 串行，先求稳
        # 写库：INSERT OR REPLACE INTO tasks ...
        print(r)

asyncio.run(main(LINKS))
```

**✅ 验收标准：** 10 条链接串行跑完，成功 9~10 条；失败的单条有 `error` 记录；缓存命中路径秒回。

---

### 5.2 第二步：加持久化队列 + 断点续跑

**做什么：** 任务状态落 SQLite，进程中断后从 `pending` 接着跑，**已 `done` 的自动跳过，不重复下载**。

**怎么做：** 把"取任务"和"存结果"改成走数据库：

```python
def claim_pending(con, limit=5):
    """取出 limit 条 pending 任务，标记 doing（串行阶段 limit=1）。"""
    rows = con.execute(
        "SELECT id, url FROM tasks WHERE status='pending' ORDER BY rowid LIMIT ?",
        (limit,)).fetchall()
    con.executemany("UPDATE tasks SET status='doing' WHERE id=?", [(r[0],) for r in rows])
    con.commit()
    return rows

def mark_done(con, task_id, text):
    con.execute("UPDATE tasks SET status='done', result=?, ts=datetime('now') WHERE id=?", (text, task_id))
    con.commit()

def mark_failed(con, task_id, err):
    con.execute("UPDATE tasks SET status='failed', error=?, ts=datetime('now') WHERE id=?", (err[:300], task_id))
    con.commit()
```

**✅ 验收标准：** 处理到一半按 Ctrl+C 杀掉，重跑后只处理剩下的；已 done 的秒跳。

---

### 5.3 第三步：加缓存

**做什么：** `video_id` 做键，结果落 `cache` 表，二次命中秒回（不消耗平台请求）。

**怎么做：**

```python
def check_cache(con, vid):
    row = con.execute("SELECT result FROM cache WHERE video_id=?", (vid,)).fetchone()
    return row[0] if row else None

def write_cache(con, vid, text):
    con.execute("INSERT OR REPLACE INTO cache(video_id, result, ts) VALUES(?,?,datetime('now'))",
                (vid, text))
    con.commit()
```

**✅ 验收标准：** 同一批链接第二次跑，命中的秒回（0.3s 内），且日志显示"cache hit"。

---

### 5.4 第四步：加限速 + 重试

**做什么：** 所有对平台接口的请求包上 `aiolimiter`（限速）+ `tenacity`（指数退避重试），防止被封、防瞬时 429。

**怎么做：**

```python
import httpx
from aiolimiter import AsyncLimiter
from tenacity import (retry, stop_after_attempt, wait_exponential,
                      retry_if_exception_type)

rate = AsyncLimiter(1, 1)   # 每秒 1 次（保守起步；测过安全 QPS 后再调）

@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, max=8),
       retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)))
async def safe_get_json(client: httpx.AsyncClient, url: str):
    async with rate:
        resp = await client.get(url, timeout=15)
        resp.raise_for_status()          # 429/5xx 会抛 HTTPStatusError → 触发重试
        return resp.json()
```

> ⚠️ **<span style="color:#e74c3c">注意：只有"可重试的瞬态错误"（超时/429/5xx）才重试；"业务性失败"（链接无效、视频不存在）不重试，直接 failed，避免浪费时间。</span>**

**✅ 验收标准：** 连续 20 条串行，全程无 403/封禁；偶发 429 自动退避后成功。

---

### 5.5 第五步：加并发（受控 Worker 池）

**做什么：** 用 `asyncio.Semaphore(2)` 把并发钉死在 2 路（先 2，稳了再试 3，**不建议超过 3**）。

**怎么做：**

```python
import asyncio

sem = asyncio.Semaphore(2)          # 受控并发 2 路，稳定优先

async def worker(url: str, con):
    async with sem:
        return await process_one(url)   # 内部已有限速+重试+缓存

async def main(links: list[str]):
    con = init_db()
    pending = [url for url in links if not is_done(con, video_id(url))]
    results = await asyncio.gather(*(worker(u, con) for u in pending))
    # 汇总写库
```

**关键点：**
- **SQLite 写入仍由主循环串行做**（worker 只算，不写库）——彻底避免 `database is locked`
- 每个 worker 内部仍受 `aiolimiter` 全局限速（漏桶是全局的，天然公平分配）
- 每任务独立临时目录 `job-<id>/`，SRT/TXT 用 `video_id` 命名，避免文件覆盖

**✅ 验收标准：** 20 条在 2 路并发下全部跑完，无 403、无锁冲突、无文件覆盖；耗时约为串行的 1.5~1.8 倍提速（**稳定优先，不追求 2 倍**）。

---

### 5.6 第六步：稳定性加固 + 监控 + 验收

**做什么：** 按第 6 节红线逐条过一遍，加进度日志与完成通知。

**怎么做：**
1. **单会话 + 令牌互斥**：全局只用一个 `httpx.AsyncClient`；Token/Cookie 刷新用 `asyncio.Lock()` 保护（防并发把 Token 顶掉）
2. **每任务隔离**：`job-<id>/` 临时目录，处理完删除
3. **失败隔离**：单条 failed 不中断整批；用 `return_exceptions=True` 包 `gather`
4. **进度日志**：`asyncio.gather` 收一条打一条：`[3/20] done 1.2s`
5. **完成汇总**：`成功 X / 失败 Y / 跳过 Z` + 总耗时，可选飞书群通知
6. **GC/内存**：长跑注意释放大对象（SRT/音频），用后即删

**✅ 验收标准：** 连续跑 3 批（每批 20 条）零崩溃；中断恢复 3 次全部接续；累计 60 条无封禁。

---

### 5.7 可选进阶：升级到 RQ / Celery（多机/团队协作时）

| 触发条件 | 升级到 | 说明 |
|---------|--------|------|
| 需要常驻服务 + 网页看进度 | **RQ** + rq-dashboard | 只依赖 Redis，`worker` 命令行即起 |
| 多机横向扩展 / 定时海量任务 | **Celery** + beat | 最成熟，支持定时/重试/结果后端，但运维重 |
| 纯异步栈 + Redis | **arq** | asyncio 原生，轻量 |

> 💡 **<span style="color:#2980b9">升级不是重写：你第 5.1~5.6 步的 `process_one` 保持不变，只是把"主循环调度"换成"队列消费"。</span>** 这就是把核心逻辑与调度解耦的价值。

---

## 6. 稳定性设计清单（对照自检）

> 📋 **<span style="color:#e67e22">上线前逐条打勾，缺一条都算"未达标"。</span>**

| # | 红线 | 实现方式 | 违反后果 |
|:-:|------|---------|---------|
| 1 | **并发度受控** | `asyncio.Semaphore(2~3)`，不裸开 10 路 | 10 倍瞬时请求 → 全 403/封号 |
| 2 | **全局限速** | `aiolimiter` 每秒 1 次起步 | 被平台风控 |
| 3 | **指数退避重试** | `tenacity` 1s→2s→4s，最多 3 次 | 偶发 429 直接丢任务 |
| 4 | **只重试瞬态错误** | 仅 Timeout/429/5xx；业务失败直接 failed | 无效链接反复重试浪费时间 |
| 5 | **状态落盘** | tasks 表 pending/doing/done/failed | 断电丢任务/重复下载 |
| 6 | **断点续跑** | 重跑只处理 pending | 从头再来，浪费算力 |
| 7 | **幂等缓存** | `video_id` 键，命中秒回 | 重复请求，被封 |
| 8 | **SQLite WAL + 串行写** | `PRAGMA journal_mode=WAL`；写库只在主循环 | `database is locked` |
| 9 | **每任务隔离** | 独立临时目录 `job-<id>/`，用完删除 | 文件覆盖/磁盘占满 |
| 10 | **单会话 + 令牌互斥** | 全局一个 Client；刷新用 `asyncio.Lock()` | 并发刷新把 Token 顶掉，全 401 |
| 11 | **失败隔离** | `gather(..., return_exceptions=True)` | 一条失败拖垮整批 |
| 12 | **日志与进度** | 每条 `[n/total] status 耗时` | 出问题无法定位 |
| 13 | **超时兜底** | 每个请求 `timeout=15`，子进程超时杀掉 | 单条卡死挂住整批 |
| 14 | **保守参数起步** | 并发 2、限速 1/s、重试 3 次，全绿后再放宽 | 一步到位 → 翻车 |

> 🔥 **<span style="color:#e74c3c">一句话：这 14 条全部满足，你的管线就"稳"了。速度不够是后话——先稳，再快。</span>**

---

## 7. 参考来源

> 📌 本文第 3、4 节项目数据来自 2026-08 公开网络调研，关键来源如下（点击直达下载页）：

### 任务队列 / 调度
- [Celery](https://github.com/celery/celery) — 最成熟分布式任务队列
- [RQ](https://github.com/rq/rq) — 简单 Redis 队列
- [APScheduler](https://github.com/agronholm/apscheduler) — 轻量调度器（SQLite 持久化）
- [Dramatiq](https://github.com/Bogdanp/dramatiq) — "更好的 Celery"
- [Huey](https://github.com/coleifer/huey) — 轻量 Redis 队列
- [arq](https://github.com/python-arq/arq) — asyncio 原生队列

### 限流 / 重试 / HTTP
- [httpx](https://github.com/encode/httpx) — 下一代 Python HTTP 客户端
- [tenacity](https://github.com/jd/tenacity) — 指数退避重试库
- [aiolimiter](https://github.com/mjpieters/aiolimiter) — asyncio 漏桶限速

### 采集 / 下载
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — 全平台视频下载
- [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) — 全平台采集王者（你已在用）
- [Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API) — 抖音异步下载
- [f2](https://github.com/Johnserf-Seed/f2) — 多平台下载

### ASR 转写
- [Whisper](https://github.com/openai/whisper) — 语音识别事实标准
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Whisper 加速版
- [FunASR](https://github.com/modelscope/FunASR) — 阿里中文语音工具箱
- [SenseVoice](https://github.com/FunAudioLLM/SenseVoice) — 中文多语 ASR（你已用）

### 一站式
- [pyvideotrans](https://github.com/jianchang512/pyvideotrans) — 视频翻译配音一体化（你已接入）
- [VideoLingo](https://github.com/Huanshere/VideoLingo) — Netflix 级字幕流水线
- [KrillinAI](https://github.com/krillinai/KrillinAI) — 面向 Agent 的翻译配音
- [douyin-creator-toolkit](https://github.com/lid664951-crypto/douyin-creator-toolkit) — 抖音运营工具箱：本地视频批量转写（最多 50 个），MIT 开源免费桌面工具（v1.2.0；百度网盘提取码 `8888`）

### 内部关联文档
- [[自研平台批量化处理路线]] — 方案评审与瓶颈定性（本文的设计依据）
- [[0811-开发日志]] — 当前实证数据（耗时/失败率/硬件）

---

## 8. 总结与落地路线

> 🔥 **<span style="color:#e74c3c">一句话总结：把"批量"做成"一个排队作业流"——SQLite 持久化队列 + asyncio.Semaphore(2~3) 受控并发 + aiolimiter 全局限速 + tenacity 指数退避 + video_id 缓存 + 14 条稳定性红线，这就是稳定优先的多 worker 并发池。</span>**

### 8.1 分阶段排期

| 阶段 | 内容 | 耗时 | 验收 |
|:---:|------|:---:|------|
| **第 1 步** | 骨架：串行跑通 10 条 | 半天 | 10 条成功 9~10 条 |
| **第 2 步** | SQLite 队列 + 断点续跑 | 半天 | 中断重跑只处理剩余 |
| **第 3 步** | 缓存命中秒回 | 2 小时 | 二次跑全部 hit |
| **第 4 步** | 限速 + 指数退避重试 | 半天 | 20 条无封禁、429 自动恢复 |
| **第 5 步** | 受控并发 2~3 路 | 半天 | 20 条全跑完无锁冲突 |
| **第 6 步** | 稳定性加固 + 14 条红线自检 | 1 天 | 3 批 × 20 条零崩溃 |
| **进阶（可选）** | RQ/Celery 多机扩展 | 按需 | 保持 process_one 不变 |

### 8.2 给同事的直白版

> 别让 20 个人同时去柜台办业务（并联 10 路），那样会把柜台挤爆（平台限流）。正确做法是**排号叫号（SQLite 队列）+ 一次放 2~3 个进去（Semaphore 受控并发）+ 办过的留档（缓存）+ 叫号单不丢（断点续跑）**。慢一点没关系，柜台永远不会爆、号永远不会丢——这就是"稳定优先"。

> 📌 **<span style="color:#e67e22">下一步行动：按第 5 节第 1 步开始，把你现有闭环先包装成 `process_one`，跑通 10 条串行，再逐步加队列、缓存、限速、并发。每一步都验收通过再前进。</span>**
