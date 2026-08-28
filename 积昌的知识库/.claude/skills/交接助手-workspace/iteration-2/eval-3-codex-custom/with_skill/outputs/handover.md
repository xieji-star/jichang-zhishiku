---
title: 短视频爆款采集系统 交接文档（给 Codex 版）
project: 全自动爬取短视频、推文爆款程序（MediaCrawler 本地部署）
handover_to: Codex（OpenAI 命令行智能体）
handover_from: DeepSeek（已完成 2026-08-14 ~ 08-17 迭代）
date: 2026-08-17
---

# 短视频爆款采集系统 交接文档（给 Codex 版）

> 目标智能体：**Codex**。本文档按 Codex 习性定制：PowerShell 命令、续接位置精确到函数、含 config.toml 与会话迁移提醒、每个验证步骤给出可跑命令与成功信号。
> 交接背景：项目由 DeepSeek 完成 0815-0817 迭代（风控组件、多账号并发池、Edge 登录态、速度优化、云端修复），现转交 Codex 继续。

---

## 0. 交接摘要（启动包）

- **项目**：本地部署的抖音爆款采集/分析系统，基于开源 MediaCrawler fork，配自研 backend（FastAPI）做清洗、S/A/B/C 爆款评分、口播稿转录（GPU ASR）、飞书/妙搭同步。
- **项目根目录**：`D:\全自动爬取短视频、推文爆款程序`（✅ 已实测存在）。
- **当前进度**：主链路已闭环，全量回归 264 passed；0817 速度优化批 + 云端 BUG 修复已完成（妙搭已部署 commit b0aff55）。
- **卡在哪**：① 10 轮验收测试只开了个头（并发模式被抖音"新设备验证"阻断，串行重跑被用户终止）；② 抖音号→sec_uid 自动解析未做；③ 字幕直取经实测**web 端无字幕数据源**，替代方案 X-Gorgon APP 签名待用户拍板。
- **下一步第一件事**：读 `start.ps1` → 确认服务启动 → 串行模式（`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`）重跑 10 轮验收测试。
- **一句话续作提示**：不要从零重构，先在 `D:\全自动爬取短视频、推文爆款程序` 上按第 6 节命令级步骤接着干。

---

## 1. 项目总览与验收标准

- **一句话定位**：用 MediaCrawler 免费采集 13 个矩阵账号的抖音数据，按统一 S/A/B/C 评分找爆款，口播稿走 GPU ASR，结果同步到妙搭前端/飞书，月度成本约 ¥0.5。
- **最终目标**：矩阵号每日全量追踪 + 爆款评分 + 口播稿转录 + 云端应急兜底，全自动、零人工。
- **验收标准**（"做完"的定义）：
  - [ ] 串行模式 10 轮验收测试全过（每轮随机 10 账号 × 20 视频，成功率 100%，详见第 6 节）
  - [ ] 缺 `creator_url` 的账号能自动解析抖音号→sec_uid，不再被跳过
  - [ ] 采集、转录、同步全链路一次开机补采跑通，妙搭前端数字正确
  - [ ] `python -m pytest` 全绿（基线 264 passed）

---

## 2. 文件地图（精确路径，均已实测）

> 根目录 = `D:\全自动爬取短视频、推文爆款程序`。以下路径均为实测存在。

| 路径（相对根目录） | 作用 | 状态 |
|---|---|---|
| `start.ps1` | **入口**：Start-Process uvicorn(8000) + npm(3000) | 已完成，唯一启动方式 |
| `backend/app/main.py` | FastAPI 主应用，含 `/api/health`、`/api/risk-control/health` | 已完成 |
| `backend/app/config.py` | 全部配置，环境变量可覆盖 | 持续修改 |
| `backend/app/db.py` | SQLite；`videos` 表、`account_tasks` 表、账号库 | 已完成 |
| `backend/app/services/collection.py` | **任务编排**：账号循环 → `run_accounts()`；含随机错峰、熔断 | 已完成，核心接续点 |
| `backend/app/services/multi_account/` | 并发池 8 模块：`runner.py`(调度器)、`account_pool.py`、`browser_profiles.py`(端口自增分配)、`global_limiter.py`(漏桶)、`retry.py`(指数退避)、`wal_queue.py`(串行写)、`edge_cleanup.py`(三层清理)、`sync_firefox_login.py` | 已完成 |
| `backend/app/providers/base.py` | `class Provider(Protocol): collect_account(account, range_key)`——统一采集接口 | 已完成，**新 Provider 必须走它** |
| `backend/app/providers/mediacrawler.py` | MediaCrawlerProvider（子进程拉起 MediaCrawler，`_read_changed` 读库） | 已完成，活跃 |
| `backend/app/providers/mediacrawler_profile_hook.py` | fork 环境注入（CDP 端口 / 登录态目录 / 账号库） | 已完成 |
| `backend/app/risk_control.py` | 熔断器 / curl_cffi / 错峰 / 代理预检 / 探针 / 截图 | 已完成 |
| `backend/app/services/` | `transcript_router.py`、`transcription.py`、`asr_service.py`、`platform_subtitles.py`、`douyin_subtitles.py`、`sync.py`(云端同步黑名单) | 已完成 |
| `MediaCrawler/` | 上游 fork（main.py 子进程入口），fork 内含签名/环境变量注入 | 已完成，勿整目录改 |
| `_asr_8765.py` | GPU ASR 服务 endpoint（faster-whisper，CUDA） | 已完成，0817 修复异步阻塞 |
| `.env.local` | **密钥 + 运行配置**，只读键名不读值，禁止提交/外发 | 活跃，0817 17:00 有改动 |
| `__pycache__/`、`*.pyc` | 临时产物，勿改 | 忽略 |
| 根目录 `_*.py` 一批 | DeepSeek 遗留的一次性调试脚本（`_check_*.py`、`_cancel*.py` 等） | ⚠️ 临时脚本，可清理，勿当作正式模块 |

> ❓ **需人工确认**：知识库文档中该项目根出现过 `E:\`、`F:\`、`D:\` 三个说法；本次实测**唯一真实存在的活动根目录是 `D:\`**。接手后请先 `cd D:\全自动爬取短视频、推文爆款程序` 确认，如机器上另有 `E:\`/`F:\` 旧副本，勿混用。

---

## 3. 已完成工作（全量逐条）

### 3.1 采集主链路（0815 及之前）
- MediaCrawler 三模式（detail / creator / search）接入，`creator` 模式全量扫 13 个矩阵号主页。
- 数据清洗 + S/A/B/C 评分（点赞 35 / 评论 25 / 收藏 25 / 分享 15，每账号 ≥30 条后切自身中位数阈值）。
- 口播稿转录：SenseVoice/faster-whisper GPU ASR（`_asr_8765.py`），仅 S/A 级转写、转写后删音视频。
- SQLite 去重落库（video_id 唯一索引）、`collection_logs` 统计表。
- 妙搭前端为唯一前端（`http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/`），旧 vinext 前端已删（780M）。

### 3.2 风控组件接入生产（0815）
- 新建 `backend/app/risk_control.py`；账号级熔断 + 随机错峰 + curl_cffi TLS 指纹 + 代理预检 + 验证码证据截图 + 探针。
- 20 条全量实测：任务成功率 **76% → 100%**（argus 风控触发 1 次仍 20/20 完成）；248 passed / 2 skipped。
- 0816 用户决策：①类对抗组件全面投产、风险自担；删 NopeCHA/代理池运行时/nodriver（释放磁盘），保留免费组件（熔断/错峰/限速/退避/curl_cffi/mss/patchright/CloakBrowser/fingerprintjs）。

### 3.3 多账号并发池 + Edge 一次登录（0816）
- fork 注入 4 环境变量（`MEDIACRAWLER_CDP_PORT` / `MEDIACRAWLER_USER_DATA_DIR` / `MEDIACRAWLER_CDP_CONNECT_EXISTING` / `MEDIACRAWLER_ACCOUNT_DB`），每账号独立端口/登录态目录/采集库。
- 单账号特例：`len(accounts) > 1` 才分配 profile，默认 `MEDIACRAWLER_CONCURRENT_ACCOUNTS=1` 行为零变化。
- 修 8 处 `USER_DATA_DIR % config.PLATFORM` 格式化崩溃 + 缺 creator_url 优雅跳过；5 轮测试 100%。
- Edge 一次登录（不加 CookieCloud）：克隆原子化（staging→.trash→切换→回滚）+ robocopy 自动刷新 + 三级登录态探测；25/25 账号目录克隆成功。
- 5 次测试全过 + 全量回归 264 passed。

### 3.4 速度专项优化 + 云端修复（0817，最新）
- 转录工作线 4→6（+50%）；错峰 20-60s→15-30s（省 ~2.5 分钟）；采集-转录流水线化（542s→~480s）；VAD 静音过滤（长视频提速 30-50%）；转录异步修复（消除 timed out）；media_url 落库（转录下载走官方直链）；主页资料并入采集进程（每账号省 ~20s）；登录等待 env 化；云端同步黑名单降噪（消 150 条无效重试）；二维码弹图根治（`MEDIACRAWLER_SKIP_QRCODE_DISPLAY`）。
- 云端 BUG：账号页查看视频固定指向同一达人——根因是 Route 重挂载"无条件全选"覆盖用户点击；修复后**已部署妙搭（commit b0aff55）**，前端测试 12 通过、tsc 零错误。
- 云端账号映射补建：`+db-execute` 批量 INSERT 28 个对标账号（internal 12 + benchmark 28）。
- 字幕直取结论：**抖音 web 端无字幕数据源**（多轮实测）；口播稿走"下载 + GPU ASR"已闭环（149/150 达标）。

---

## 4. 当前精确进度（从哪继续）

- **最后一次有效操作**（0817）：速度优化批落地 + 云端妙搭部署（commit b0aff55）+ 28 账号映射补建 + 三浏览器线路链（Firefox→Edge→Chrome，`MEDIACRAWLER_BROWSER_ENGINE_CHAIN`）。
- **当前代码状态**：
  - `.env.local` 含 `MEDIACRAWLER_CONCURRENT_ACCOUNTS`（串行=1）、`RISK_*` 风控开关、`MEDIACRAWLER_BROWSER_ENGINE_CHAIN`、`YTDLP_COOKIE_FILE`（从 Firefox 登录态导出，每次采集前自动刷新）。
  - 后端跑在项目 `.venv`（Python 3.12），**不是** Anaconda python（0815 已切换）。
  - 妙搭前端已部署最新构建；`start.ps1` 为唯一启动入口。
- **停下来的位置**：10 轮验收测试只跑完第 1 轮（并发模式，抖音新环境验证失败）→ 回退串行重跑 → **被用户终止**。测试脚本已删，需按 0816 日志第 7 节重写。

---

## 5. 未完成事项（全量逐条）

| # | 事项 | 阻塞原因/背景 | 前置条件 | 优先级 | "算完成"的标准 |
|:-:|---|---|---|---|---|
| 1 | **10 轮验收测试重跑** | 并发模式被抖音"新设备要求扫码"阻断；串行重跑被终止；测试脚本已删 | 串行模式（CONCURRENT=1），每轮随机 10 账号×20 视频，90 分钟/轮上限，轮间冷却 30s | 🔴 紧急 | 10 轮全过、成功率 100% |
| 2 | **抖音号→sec_uid 自动解析** | 缺 creator_url 账号目前只能跳过 | 按方案：fork search hook（USER 频道搜索）+ 后端三层缓存回填 | 🟠 重要 | 所有账号都有 creator_url，无账号被跳过 |
| 3 | **X-Gorgon APP 签名直取**（字幕直取替代路线） | web 端无字幕数据源（已实测定论） | 用户拍板是否接入；参考 douyin-sign nightly CI | 🟡 待定 | 用户决策后评估工程接入 |
| 4 | **多账号并发登录态免扫码** | 克隆 Cookie 对新 Edge 环境不保证免验证（平台策略） | 现实路径：串行验收；或每账号首次人工扫码后保持 profile | 🟠 重要 | 串行全自动免扫码跑通 |
| 5 | **clone 脚本自动刷新验证** | start.ps1 mtime 比对已实施未验证 | 一次真实"共享重登→启动→自动克隆"场景 | 🟡 一般 | 该场景实测通过 |
| 6 | **代理 HTTPS 隧道** | 缺 HTTPS 代理源，正效果未验证 | 有 HTTPS 代理源 | 🟡 一般 | 接入后代理预检正效果实证 |
| 7 | **三目录分离迁移（Phase 3）** | 增量更新地基，涉及 DEPLOY_ROOT 迁移 | 按《关于爬虫项目的后续优化迭代与升级》Phase 1→2 先行 | 🟡 一般 | migrate_3dir.ps1 迁移成功、登录态不丢 |

---

## 6. 下一步行动计划（命令级，PowerShell）

> 前置：确认工作目录。全部命令在 **PowerShell** 中执行。

### 立即做

**STEP 1 — 确认服务未占用 / 看当前状态**
```powershell
cd "D:\全自动爬取短视频、推文爆款程序"
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue   # backend 占用?
Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue   # 前端占用?
tasklist | findstr /I "python node"                                               # 看解释器来源
```
预期：若 8000 有进程，确认它是本项目 `.venv` 的 python（`Get-CimInstance Win32_Process -Filter "ProcessId=...` 看 ExecutablePath）；若是 Anaconda，先杀再走 start.ps1。

**STEP 2 — 启动服务（唯一入口）**
```powershell
cd "D:\全自动爬取短视频、推文爆款程序"
.\start.ps1
```
预期（成功信号）：
- 8000 端口有 uvicorn 监听；
- `Invoke-RestMethod http://127.0.0.1:8000/api/health` 返回 `status=ok`；
- `Invoke-RestMethod http://127.0.0.1:8000/api/risk-control/health` 返回各开关 true/false（CIRCUIT_BREAKER=true 等）；
- 妙搭前端 `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/` 可打开。

**STEP 3 — 确认配置快照**
```powershell
Get-Content "D:\全自动爬取短视频、推文爆款程序\.env.local" | Where-Object { $_ -match '^[A-Z]' }
```
预期：`MEDIACRAWLER_CONCURRENT_ACCOUNTS` 值为 `1`（串行）；`RISK_CIRCUIT_BREAKER`/`RISK_STAGGER_ENABLED`/`RISK_CURL_CFFI` 为 true。值缺失先补（不要改动密钥值）。

**STEP 4 — 跑回归测试**
```powershell
cd "D:\全自动爬取短视频、推文爆款程序"
.\.venv\Scripts\python.exe -m pytest -q
```
预期（成功信号）：**264 passed**（与 0816 基线一致）；新增改动后应 >= 264。

**STEP 5 — 重写并执行 10 轮验收测试（串行）**
按 0816 日志第 7 节重写测试脚本（脚本已删）：每轮随机 10 账号 × 20 视频，串行（`CONCURRENT=1`），90 分钟/轮上限，轮间冷却 30s，统计成功率与平均耗时，逐轮复盘、抹数据再下一轮。测试数据清理用 SQL（videos 等 9 表 + douyin_aweme 2 表）。
预期：10 轮全过、成功率 100%、零账号封锁。

### 之后做
- 抖音号→sec_uid 自动解析（未完成事项 #2）。
- 向用户确认 X-Gorgon APP 签名直取是否立项（未完成事项 #3）。
- 三目录分离 + 增量更新（Phase 1→2→3，见第 9 节踩坑与蓝图文档）。

---

## 7. 环境与配置依赖（完整清单）

### 7.1 Codex 本体与 config.toml（Codex 专属提醒）

- Codex 会话/配置目录：`C:\Users\asus\.codex\`。
- **`config.toml`（已实测存在）**：当前 `model = "gpt-5.6-sol"`、`model_provider = "openai"`、`sandbox = "elevated"`。项目本身不依赖某个固定模型，gpt-5.6-sol 可直接续作。
- ⚠️ 若你想让 Codex 走 **DeepSeek 供应商**：需在 Codex++ 管理工具配置 Provider（名称 `DeepSeek`、Base URL `https://api.deepseek.com`、上游协议 Chat Completions、`deepseek-chat`/`deepseek-v4-flash`），并确认 `config.toml` 的 `model`/`model_provider` 已指向它，否则可能提示模型不可用（见知识库 [[wiki/AI与技术工具/Codex模型配置]]）。
- **网络提醒**：Codex 桌面端连 ChatGPT 依赖代理/分流。若遇 `stream disconnected` / `403 Forbidden`（cf-ray 带 `-HKG`），是**节点被风控**不是网坏——用 `curl -x http://127.0.0.1:7897 -I https://chatgpt.com` 验证（403=切节点，401=放行）；固定节点 🇺🇸 美国-IEPL 02；详见 [[wiki/AI与技术工具/Codex模型配置]] 网络故障排查。

### 7.2 会话迁移（Codex 专属提醒）

- Codex 本地会话在 `C:\Users\asus\.codex\sessions\*.jsonl`（已实测存在，如 `2026/08/14/rollout-*.jsonl`）。**换号/换机续作：拷 sessions + session_index.jsonl + config.toml，绝不拷 `auth.json`**（那是登录令牌，拷了会顶号）。
- 本项目 0816-0817 的 DeepSeek 工作没有对应 Codex 会话——**本交接文档即续作依据**，不要指望翻 Codex 历史会话。

### 7.3 运行时依赖

| 项 | 说明 |
|---|---|
| Python | 项目 `.venv`（Python 3.12.4），**禁止用 Anaconda python** 跑 backend |
| GPU ASR | faster-whisper 1.2.1 + CTranslate2 4.8.1（CUDA 12.8, RTX 5060），服务在 `_asr_8765.py`（同步 endpoint + 240s 超时） |
| 浏览器 | Edge（CDP 登录态）+ Firefox（`MEDIACRAWLER_BROWSER_ENGINE_CHAIN` 首选）三线路链 |
| ffmpeg | `FFPROBE_PATH`（.env.local 已配） |
| 前端 | 妙搭（`MIAODA_API_KEY` 在 .env.local）；`http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/` |
| 云端同步 | `SYNC_BASE_URL` / `SYNC_PATH` / `SYNC_TOKEN`（.env.local）；云端黑名单已持久化 |

### 7.4 密钥/敏感项（脱敏）

- 全部密钥只在 `.env.local`（`SPIDERHUBS_API_KEY`、`MIAODA_API_KEY`、`SYNC_TOKEN`、`SITES_BYPASS_TOKEN`、`EVIL0CTAL_API_BASE_URL`、`NOPECHA_API_KEY` 等）。**值一律 `<已脱敏>`，禁止提交 Git / 上传 / 粘贴进工单**。
- 登录态唯一落点：`MEDIACRAWLER_BROWSER_DATA_DIR` 指向的 D 盘目录（迁移前 `%LOCALAPPDATA%\MediaCrawler\browser_data`）。禁止提交、禁止外发。

---

## 8. 数据与状态快照

- 业务库：`data/radar.sqlite3`（+wal/shm）；`videos` 表含 `media_url` 列（0817 落库）；`account_tasks` 表（并发池闭环）。
- 采集主库：`MediaCrawler/database/*.db`（含账号独立库 `<key>_sqlite_tables.db`）。
- 云端账号映射：28 个对标账号已补建（internal 12 + benchmark 28）。
- 根目录 `_*.py` 调试脚本（`_check_*`、`_cancel*`、`_add_r4.py` 等）是 DeepSeek 遗留临时产物——可清理，但**清理前确认没有正在跑的采集任务**。

---

## 9. 关键决策与踩坑记录（Codex 必读，避免重踩）

1. **抖音 web 端无字幕数据源**（0817 实测定论）：detail 接口无字幕字段、播放器无字幕请求、分享页无 videoInfoRes——别再花时间找 web 字幕，口播稿走"下载 + GPU ASR"（149/150 达标）。
2. **并发模式"免登录"在抖音不成立**：新 Edge profile 克隆 Cookie 仍被识别为新设备要求扫码（平台策略，非 BUG）。现实路径：串行（CONCURRENT=1，共享登录态免扫码）。
3. **`start.ps1` 编码坑**：PowerShell 5.1 按 GBK 解析无 BOM UTF-8，中文注释会乱码/语法错——新加逻辑**注释用纯 ASCII**。
4. **8 处 `USER_DATA_DIR % config.PLATFORM` 崩溃**：注入绝对路径时 `TypeError: not all arguments converted`——统一 `isabs` 守卫（绝对路径跳过格式化）。
5. **backend 8000 端口偶现 Anaconda python 实例**：功能一致但排查注意解释器来源；正式环境统一项目 `.venv`。
6. **图文笔记（aweme_type=163/2）**：只采数据不转录——硬转录会把 BGM 歌词当口播稿（假成功教训）。
7. **合规红线已由用户 2026-08-16 决策放宽**（个人使用、风险自担，①类对抗组件投产）。但 `security/verify.ps1` 与 `runtime/plugins/deployment-manifest.json` 仍守护断言，改组件须同步更新。
8. **零新增 pip 依赖**（并发池用标准库；依赖走 wheelhouse 离线），新 Provider 必须实现 `Provider.collect_account(account, range_key)`。

---

## 10. 风险与待确认项

- ❓ **项目根目录多副本**：文档出现 E:\/F:\/D:\ 三处；实测活动根为 `D:\`，请接手机确认，勿混用旧副本（`E:\aaa\3_23日晚最终版本项目代码` 3.2G 旧版仅演练用）。
- ❓ **X-Gorgon APP 签名直取**是否立项，等用户拍板。
- ❓ **10 轮验收测试**测试脚本已删，需重写；抖音平台策略可能继续阻断并发模式。
- ⚠️ **合规风险自担**：对抗组件可能违反抖音服务条款，持续观察风控信号（argus/blocked/429/403/verification）。
- ⚠️ **`.env.local` 安全**：含真实密钥，任何输出/截图/工单都不得带出。
- ⚠️ **磁盘空间**：`.yolov8m-seg.pt.*.part`、`_test_*.pdf` 等历史临时大文件在知识库根目录，与项目无关，可另议清理。

---

## 11. 续作启动手册（从零恢复 + 如何验证"续上了"）

**从零恢复完整步骤**：
1. `cd "D:\全自动爬取短视频、推文爆款程序"`；
2. 检查 8000/3000 端口占用 → 杀掉非本项目实例；
3. `.\start.ps1` 启动 backend + 前端；
4. 确认 `/api/health` = ok；
5. 触发一次采集：前端"立即采集"或命令行 `--run-now`，观察任务状态 completed；
6. 跑 `python -m pytest` 确认 264 基线。

**如何验证"续上了"（Codex 完成接续的硬信号）**：
- ✅ `.\start.ps1` 后 `Invoke-RestMethod http://127.0.0.1:8000/api/health` 返回 `status: ok`；
- ✅ `python -m pytest -q` 输出 **264 passed**（或 >= 264）；
- ✅ 真实采集一次：任务 `status=completed`、`videos=N`、`accounts_succeeded=1`、`blocked=0`；
- ✅ 妙搭前端打开 `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/`，视频列表非空、账号筛选不指向固定达人；
- ✅ 一次开机补采跑通：缺日期的数据自动补齐、无账号被跳过。

---

## 12. 按 Codex 定制的附加内容（本次交接专属）

- **命令一律 PowerShell**：上文所有命令为 PS 风格（`Get-NetTCPConnection` / `Invoke-RestMethod` / `Get-Content` / `tasklist`），与 Codex 运行环境匹配。若你用 bash，等价替换（`curl 127.0.0.1:8000/api/health`、`netstat -ano | findstr 8000`）。
- **从哪个函数续改代码**：
  - 并发/任务流 → `backend/app/services/collection.py` 的 `run_accounts()` 与账号循环；
  - 新采集线路 → `backend/app/providers/` 新增类实现 `collect_account(account, range_key)`（先读 `base.py` Protocol），不要改 `collection.py`；
  - 转录链路 → `_asr_8765.py`（GPU ASR endpoint）+ `backend/app/services/transcript_router.py`；
  - 前端 → 妙搭工程（不在本仓库），只改 `backend` 侧 `radar-selection.ts` 相关逻辑时注意 Route 重挂载初始化优先级。
- **config.toml / 会话迁移**：见第 7.1 / 7.2 节，接手机先 `Get-Content C:\Users\asus\.codex\config.toml` 确认模型可用。
- **网络分流**：涉及外网（DeepSeek 周报 API、代理源）时，参考知识库 Codex 网络故障档案（青旅环境 `mode: direct` 陷阱：先 `curl http://127.0.0.1:39798/configs` 看 mode 是否 rule）。

---

> **给 Codex 的收尾提示**：本项目的坑大多已写在知识库开发日志（0815/0816/0817）与[[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序]]系列笔记中，先读再改。祝续作顺利。
