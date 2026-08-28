---
title: 全自动爬取短视频、推文爆款程序 — 交接文档
type: 项目交接文档
date: 2026-08-17
project: 矩阵内容雷达（全自动爬取短视频、推文爆款程序）
status: 持续开发中
tags:
  - 交接文档
  - MediaCrawler
  - 抖音采集
  - GPU-ASR
  - 妙搭
  - 多账号并发
  - 风控对抗
  - Claude Code 接手
---

# 全自动爬取短视频、推文爆款程序 — 交接文档

> [!summary] 给下一个 Claude 智能体的一句话
> 本项目是**本地部署的抖音爆款采集与分析系统**：基于 MediaCrawler fork 采集抖音数据，GPU ASR（faster-whisper，端口 8765）生成口播稿，妙搭（Feishu MiaoDa）做云端前端与数据库。**本地核心链路已基本闭环（约 95%）**，代码在 D 盘，知识库文档在 F 盘；换到 Claude Code 接手后，请先读本文档「下一步行动计划」，从「10 轮验收测试（串行）」开始。

---

## 1. 项目总览

- **一句话定位**：面向华哥组、七哥组、鱼哥组 12 个自有抖音账号的低成本数据工作台 —— 自动采集作品元数据 + 生成口播稿 + 按 S/A/B/C 爆款标准排序，供矩阵账号选题与对标分析。
- **技术底座**：MediaCrawler（抖音采集，已 fork 增强）＋ faster-whisper GPU-ASR（口播稿）＋ 飞书妙搭（前端/数据库/发布）＋ pyvideotrans `.venv-stt`（Python 3.10 CPU 转录兜底）。
- **成本**：本地部署 + 自建采集，全月约 **¥0.5/月**（主要为云应急节点）。
- **整体完成度**：本地核心链路约 **95%**；计入飞书导出/封面 OCR/涨粉差分/妙搭口播稿同步等全范围约 **85%**（估算）。
- **合规状态（重要）**：2026-08-16 用户决策突破原合规红线，①类对抗组件投入使用，**风险自担**；详见第 10 节。

---

## 2. 文件地图（关键路径，已实测存在）

### 2.1 代码（D 盘，唯一正式工作目录）

| 内容 | 路径 | 说明 |
|------|------|------|
| **项目根目录** | `D:\全自动爬取短视频、推文爆款程序` | 唯一源目录；**根目录本身不是 git 仓库** |
| **启动脚本** | `D:\全自动爬取短视频、推文爆款程序\start.ps1` | 唯一启动入口（拉起后端 8000 / ASR 8765 / 前端 3000）；`-Install` 首次装依赖 |
| **环境配置** | `D:\全自动爬取短视频、推文爆款程序\.env.local` | ⚠️ 含密钥，**禁止提交/外发**；模板见 `.env.example` |
| **后端应用** | `D:\全自动爬取短视频、推文爆款程序\backend\app` | `config.py`、`db.py`、`main.py`、`risk_control.py`、`providers/`、`services/` |
| 采集调度 | `...\backend\app\services\collection.py` | 账号循环→run_accounts、采集-转录流水线（批线程） |
| 云端同步 | `...\backend\app\services\sync.py` | 妙搭同步 + runtime_settings 持久化（黑名单降噪） |
| 多账号并发池 | `...\backend\app\services\multi_account\` | `account_pool.py` / `browser_profiles.py` / `edge_cleanup.py` / `global_limiter.py` / `retry.py` / `runner.py` / `wal_queue.py` / `sync_firefox_login.py` |
| ASR/字幕服务 | `...\backend\app\services\asr_service.py`、`douyin_subtitles.py`、`platform_subtitles.py` | 口播稿 / 字幕直取（默认关） |
| **GPU-ASR 服务** | `D:\全自动爬取短视频、推文爆款程序\_asr_8765.py` | faster-whisper GPU 转录，端口 **8765**，同步 endpoint + 超时 240s + `vad_filter` 静音过滤 |
| **MediaCrawler fork** | `D:\全自动爬取短视频、推文爆款程序\MediaCrawler` | 独立 `.venv`；fork 4 env 注入 `MEDIACRAWLER_CDP_PORT/USER_DATA_DIR/CDP_CONNECT_EXISTING/ACCOUNT_DB`；浏览器线路 Firefox→Edge→Chrome |
| **pyvideotrans 兜底** | `D:\全自动爬取短视频、推文爆款程序\pyvideotrans\.venv-stt` | Python 3.10.19，`small` 模型，官方 `cli.py --task stt`；生产转录主走 GPU-ASR |
| 插件/工具 | `D:\全自动爬取短视频、推文爆款程序\runtime\plugins\` | douyin-mcp / evil0ctal-api / f2 / yt-dlp / funasr / speaches / videolingo 等独立 venv |
| **妙搭主仓库（git）** | `D:\全自动爬取短视频、推文爆款程序\deployments\miaoda-matrix-radar` | 分支 `sprint/default`，HEAD `c88a1e7`（2026-08-17）；云端前端+接口 |

### 2.2 知识库文档（F 盘，只读参考）

| 内容 | 路径 |
|------|------|
| 项目笔记总目录 | `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\` |
| 开发日志（0809→0817） | 同目录下 `开发日志\0809-爬虫开发日志.md`、`0810-*.md`、`0811-开发日志.md`、`0814-还没配置好的内容.md`、`0815-项目测试.md`、`0815-风控组件接入生产.md`、`0816-多账号并发与Edge登录态.md`、`0816-对抗组件全面启用.md`、`0817-速度优化批与云端修复.md` |
| 报错修复日志 | `报错修复日志\0815-多账号采集与缺链接报错修复.md` |
| Wiki 汇总页（推荐先读） | `F:\积昌的知识库 - 副本\自动维护知识库\wiki\自媒体运营\短视频爆款采集系统.md` |
| 迁移方案模板（13 项交接结构出处） | `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\技能\AI\Codex\Codex对话迁移方案.md` |

### 2.3 端口与运行地址

| 服务 | 端口 | 地址 |
|------|------|------|
| 业务后端 | 8000 | `http://127.0.0.1:8000` |
| GPU-ASR | 8765 | 仅本机回环 |
| 妙搭前端（本地 dev） | 3000 / 3100 | `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/` |
| 妙搭生产 | — | `https://ncn5iae3ocvu.feishuapp.com/app/app_17bkk0a8pt8` |

> 交接时以上服务通常已在前台运行（本次核查 8000 / 8765 / 3000 均在监听）。

---

## 3. 环境与配置现状（.env.local 键位，值已脱敏）

- 转录/ASR：`TRANSCRIPTION_ENABLED`、`PYVIDEOTRANS_ROOT/PYTHON/MODEL/FAST_MODE`、`ASR_SERVICE_BASE_URL`（8765）、`ASR_SERVICE_MODEL`、`ASR_SERVICE_TIMEOUT_SECONDS=240`、`FFPROBE_PATH=D:\ffmpeg\bin`
- 多账号：`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`（**默认串行**；>1 才启用并发池隔离）
- 风控开关（0816 决策后保留投产）：`RISK_CIRCUIT_BREAKER`、`RISK_STAGGER_ENABLED`、`RISK_CURL_CFFI`、`RISK_EVIDENCE_SCREENSHOT`、`RISK_STAGGER_MIN/MAX_SECONDS=15/30`
- 浏览器线路：`RISK_BROWSER_ROUTE=patchright`；`MEDIACRAWLER_BROWSER_ENGINE_CHAIN=firefox-system → Edge → Chrome`；`MEDIACRAWLER_SKIP_QRCODE_DISPLAY=true`；`YTDLP_COOKIE_FILE`（采集前由后端自动从 Firefox 登录态刷新）
- **已停用/已删组件**：`RISK_NOPECHA_ENABLED=false`（NopeCHA 已卸载）、`RISK_PROXY_ENABLED=false`（代理池运行时已停，源码目录保留）
- 目录迁移：`HF_HOME` / `UV_CACHE_DIR` / `PIP_CACHE_DIR` / `MEDIACRAWLER_BROWSER_DATA_DIR` 全部指向 D 盘
- 密钥类：`SPIDERHUBS_API_KEY`、`MIAODA_API_KEY`、`SYNC_TOKEN`、`SITES_BYPASS_TOKEN`、`EVIL0CTAL_API_BASE_URL` 等 —— **值只在 `.env.local`，请勿外发**

---

## 4. 当前进度（截至 2026-08-17）

### 4.1 已完成并验证

- **采集链路**：MediaCrawler 三模式（detail/creator/search）+ 缺 creator_url 账号优雅跳过 + 图文笔记（aweme_type=163/2）只采数据不转录（避免把 BGM 当口播稿）。
- **口播稿闭环**：下载→GPU-ASR（8765）→校验→写库→删临时媒体；**149/150 达标**；长视频 VAD 静音过滤提速 30-50%；`small` 模型为生产默认。
- **多账号并发池**：账号级受控并发（每账号独立 CDP 端口/登录态目录/采集库），默认 `CONCURRENT_ACCOUNTS=1` 行为零变化；5 次测试全过。
- **Edge 一次登录**：本地克隆原子化（staging→.trash→回滚）+ robocopy 自动刷新 + 三级登录态探测；**25/25 账号目录克隆成功**（含 Cookie）。⚠️ 但克隆 Cookie 对**新 Edge 环境不保证免验证**（抖音识别新设备要求扫码）。
- **风控/对抗组件**（0816 决策启用）：十轮测试全部通过、成功率 100%、**十轮真实采集零账号封锁**；保留投产：熔断器/随机错峰/全局限速/指数退避/curl_cffi/patchright/CloakBrowser/mss 截图/fingerprintjs；付费组件（NopeCHA/代理池/nodriver）已按用户指令删除释放硬盘。
- **速度优化批**（0817）：转录工作线 4→6、错峰收窄 15-30s、采集-转录流水线化（单账号 542s→~480s）、media_url 落库、主页资料并入采集、登录等待 env 化、云端同步黑名单降噪、二维码弹图根治。
- **Edge 窗口卫生**：`edge_cleanup.py` 三层清理（账号/hook/任务终态），任务结束一律杀窗口。
- **云端（妙搭）**：删除旧 vinext 前端（780M），妙搭为唯一前端；修复"账号页查看视频固定指向同一达人"（commit `b0aff55` 已部署）；最新 `c88a1e7`（紧凑数字显示+分页硬上限）。

### 4.2 测试基线

- 后端 pytest：**279 项，约 2s 通过**（根目录 `pytest.ini`，`testpaths = backend/tests`）。
- 前端（miaoda repo）：Jest + `tsc` 零错误（0817 记录前端 12 通过）。

---

## 5. 未完成事项（按优先级）

| # | 事项 | 背景 | 阻塞原因 | 建议做法 |
|:-:|------|------|---------|---------|
| 1 | **10 轮验收测试** | 并发模式被抖音"新环境验证"阻断；串行重跑被用户终止 | 抖音平台策略，非 BUG | **串行模式（CONCURRENT=1）重跑 10 轮**，每轮随机 10 账号×20 视频；测试脚本已删，按 0816 日志第 7 节重写 |
| 2 | **抖音号→sec_uid 自动解析** | 缺 creator_url 账号目前只能跳过 | 需 fork search hook + 后端三层缓存回填 | 按 0815 报错修复日志第 5 节架构 Agent 方案实施 |
| 3 | **字幕直取 Phase 0 实测** | `SUBTITLE_DIRECT_ENABLED` 默认关，覆盖率未验证 | 无 | fork client 有界采样 300 条 detail，统计 `video.subtitles` 存在率（**≥20% 才投产**） |
| 4 | **字幕直取灰度** | 达标后可开 | 依赖 #3 | 20%→50%→100%，每级 3 天 |
| 5 | **多账号并发登录态** | 克隆 Cookie 对新 Edge 无效 | 平台策略 | 现实路径：串行验收；或每账号首次人工扫码一次后 profile 持久 |
| 6 | **clone 自动刷新验证** | start.ps1 mtime 比对已实施 | 无 | 做一次真实"共享重登→启动→自动克隆"场景验证 |
| 7 | **APP 签名（X-Gorgon）直取** | 抖音 web 端无字幕数据源已确认 | 待用户拍板 | 开源 douyin-sign / TikTok-Encryption 可支撑，中等工程 |
| 8 | **代理 HTTPS 隧道** | 缺 HTTPS 代理源 | 待代理源 | — |
| 9 | **云端采集节点** | 常驻 Linux CPU 节点未搭建 | 后续阶段 | 低配 CPU + 持久任务队列 + 登录恢复，先 1-2 账号实采基准 |
| 10 | **飞书导出 / 封面 OCR / 涨粉差分 / 妙搭口播稿同步** | 功能待办 | 后续阶段 | 各自独立增强，各约 1-2 次对话 |

---

## 6. 下一步行动计划（具体命令）

### 0) 接手第一步（必做）

1. 先读两份最新日志确认现场：
   - `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\开发日志\0816-多账号并发与Edge登录态.md`（**第 8 节交接清单**）
   - `...\开发日志\0817-速度优化批与云端修复.md`
2. 确认服务在跑：访问 `http://127.0.0.1:8000/health` 和 `http://127.0.0.1:8000/api/risk-control/health`，应返回 ready/开关状态。
3. 确认当前 git 现场：
   ```powershell
   cd D:\全自动爬取短视频、推文爆款程序\deployments\miaoda-matrix-radar
   git log --oneline -5
   git status
   ```

### 1) 启动 / 重启项目（日常）

```powershell
# 前台启动（后端 8000 + ASR 8765 + 前端 3000）
cd D:\全自动爬取短视频、推文爆款程序
.\start.ps1

# 首次安装/补依赖时才用：
.\start.ps1 -Install
```

### 2) 跑测试（每轮改动后回归）

```powershell
cd D:\全自动爬取短视频、推文爆款程序
.\.venv\Scripts\python.exe -m pytest        # 279 项，约 2s

# 前端（妙搭 repo）
cd deployments\miaoda-matrix-radar
npm test
npm run build
npx tsc --noEmit
```

### 3) 任务一：10 轮验收测试（串行，优先级最高）

> 测试脚本已删除，需按 0816 日志第 7 节重写。用户口径：**每轮随机 10 账号 × 20 视频全采集，统计成功率与平均耗时，逐轮复盘迭代、清数据再下一轮**。

```powershell
cd D:\全自动爬取短视频、推文爆款程序
# 1) 确认串行模式（.env.local 中 MEDIACRAWLER_CONCURRENT_ACCOUNTS=1）
# 2) 通过后端 API 发起采集任务：账号从 12 个矩阵号中随机取 10，video_limit=20，
#    content_mode=transcript, transcription_mode=all, range=all
# 3) 每轮结束读 collection_logs / error_logs / collection_job_items 分析失败明细
# 4) 优化后：备份 backups/ → 清业务库 9 表 + MediaCrawler 2 表 → 进入下一轮
# 5) 10 轮跑完输出成功率 / 平均耗时 / 风控信号（argus/429/403/verification）汇总
```

### 4) 任务二：抖音号→sec_uid 自动解析（次优先级）

> 按 `0815-多账号采集与缺链接报错修复.md` 第 5 节方案：fork 加 search hook（USER 频道搜索）+ 后端三层缓存回填；落地后缺 creator_url 的账号不再跳过。

### 5) 任务三：字幕直取 Phase 0 实测

```powershell
cd D:\全自动爬取短视频、推文爆款程序
# 用 fork client 有界采样 300 条 detail 接口数据，统计 video.subtitles 存在率
# 存在率 ≥20% → 打开 SUBTITLE_DIRECT_ENABLED → 再按 20%→50%→100% 灰度
```

### 6) 云端发布（妙搭 repo，git 仓库在此）

```powershell
cd D:\全自动爬取短视频、推文爆款程序\deployments\miaoda-matrix-radar
git checkout sprint/default
git add -A && git commit -m "feat(radar): ..."
# 构建后经妙搭 CLI/页面发布；发布 ID 记录到开发日志（参考 b0aff55 / c88a1e7）
```

---

## 7. 关键决策与踩坑记录（速查）

- **字幕直取不可行（web 端）**：抖音 detail 接口无字幕字段、播放器无字幕请求、分享页无 videoInfoRes（多轮实测）→ 口播稿走"下载 + GPU ASR"。
- **图文笔记假成功教训**：aweme_type=163/2 无音频，硬转录会把 BGM 当口播稿 → 只采数据不转录，正确率按"可转录视频数"统计。
- **多账号 Cookie 串味红线**：每账号独立 CDP 端口/登录态目录/采集库；单账号走共享登录态老路径。
- **账号名称不能作主键**：改用稳定 UUID `accountId`；显示名称只作可变信息。
- **F 盘写入慢 → 全部迁 D 盘**；F 盘只存知识库文档。
- **pyvideotrans 不接受 URL**：只接受本地文件 → 先受控下载到 `data\temp_media\job-<id>`，转录入库后删除。
- **Python 版本隔离**：pyvideotrans 需 3.10（`.venv-stt`）；主 venv 与 MediaCrawler venv 为 3.12.4。
- **start.ps1 编码坑**：PowerShell 5.1 按 GBK 解析无 BOM UTF-8 → 新加逻辑用纯 ASCII。
- **pytest 集成测试**：`npm run test:radar:db` 才跑真实数据库用例，普通测试默认跳过（防假绿）。
- **妙搭发布分阶段**：Expand → Backfill → Contract 三段式，Contract 收紧（NOT NULL/FK）已上线（commit `d89c20d`）。

---

## 8. 数据与数据库状态

- **业务库**（本地 SQLite + 妙搭云端 PostgreSQL）：12 个矩阵账号（华哥 5/七哥 5 中 3 未收录名单见日志/鱼哥 3）；另有云端补建 internal 12 + benchmark 28 对标账号。
- **采集库**：MediaCrawler 库存 126+ 条作品，均含 `video_download_url`；口播稿转录后临时媒体自动删除。
- **清理口径**：媒体文件零长期保留（成功即删，失败保留 6-24h）；模型目录长期保留（不删，避免重复下载）。
- ⚠️ 线上曾经的"数据 0"是字段未映射/未采集，**不得把未知伪装成 0**（页面已按 none/partial/complete 区分）。

---

## 9. 风险与待确认项

- ❓ **10 轮验收测试**：并发模式被抖音"新设备验证"阻断，串行重跑需用户确认时机与账号范围。
- ❓ **APP 签名（X-Gorgon）直取**：是否投入中等工程量，**待用户拍板**。
- ❓ **代理 HTTPS 源**：正效果待 HTTPS 代理源就绪。
- ⚠️ **合规/法律风险**：对抗组件已按 2026-08-16 用户决策启用，账号可能被封、IP 封锁或法律纠纷；运行期间持续监控风控信号（熔断器持续统计）。
- ⚠️ **抖音登录态**：克隆 Cookie 不保证新环境免验证；串行模式（共享登录态）可全自动免扫码。
- ⚠️ **`.env.local`** 含密钥，禁止提交 Git 或外发。

---

## 10. 如何验证"接手成功"

1. `.\start.ps1` 启动后，`http://127.0.0.1:8000/health` 返回 ready；`/api/risk-control/health` 显示 CIRCUIT_BREAKER/CURL_CFFI/STAGGER/EVIDENCE_SCREENSHOT=true、BROWSER_ROUTE=patchright、PROXY=false。
2. 后端 pytest 279 项全过；前端 tsc 零错误。
3. 发起一轮小采集（1 账号 × 5 条，含口播稿）能闭环：元数据入库 → 口播稿非空 → 临时媒体删除。
4. 对照开发日志的 git 提交（`b0aff55`、`c88a1e7` 等）与妙搭线上发布状态一致。

---

> 📌 **续作入口**：从 `开发日志\0816-多账号并发与Edge登录态.md` 第 8 节「交接清单」开始，优先级 **1 > 2 > 3**；项目启动一律用 `start.ps1`；测试数据清理用 SQL（videos 等 9 表 + douyin_aweme 2 表）。
