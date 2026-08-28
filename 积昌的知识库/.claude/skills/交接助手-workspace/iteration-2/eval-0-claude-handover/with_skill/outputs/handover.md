---
项目名：全自动爬取短视频、推文爆款程序
交接对象：Claude Code（Anthropic 命令行智能体）
交接日期：2026-08-17
交接方向：DeepSeek → Claude Code
生成方式：交接助手 skill（模式 B · 按 Claude Code 习性档案定制）
---

# 全自动爬取短视频、推文爆款程序 交接文档（给 Claude Code 版）

> [!summary] 一句话定位
> 一套**本地部署 + 云端应急**的短视频/推文爆款采集与分析系统：基于 MediaCrawler fork 抓取抖音数据，S/A/B/C 爆款评分、GPU ASR 口播稿转录，飞书为唯一对外出口。**但按 2026-08-16 深度审视，当前实际能力是"采集 + 口播稿转录工作台"，爆款评分层尚未落地。**

> [!note] 证据分级说明
> 本文档所有**文件路径、配置项、命令**均在本机（D 盘）实测核实（✅）；少数无法核实项标注 **❓需人工确认**；关键结论标注来源文档。

---

## 0. 交接摘要（启动包）

- **项目做什么**：服务公司 12 个抖音矩阵号（科研论文辅导方向），自动采集账号/关键词/单链接视频 → 清洗落库 → GPU ASR 生成口播稿 → 妙搭云端展示 + 飞书同步。
- **当前做到哪**：采集管线、转录管线、多账号并发池、Edge 一次登录、对抗组件、云端前端全部落地；**P0 待办积压**（字幕直取上线缺陷、商用许可、云端鉴权、风控接线、版本控制）。
- **最关键三件事**：
  1. **已完成**：采集 + 转录闭环可用（10 轮实测采集成功率 100%、149/150 口播稿达标）；
  2. **卡在哪**：多账号并发"免登录"被抖音新环境验证阻断（平台策略，非 BUG）；10 轮验收测试仅跑 1 轮即被终止；爆款评分零落地；
  3. **下一步第一件事**：修「字幕直取成功被误判失败」缺陷（🔴3，必改项），再按 0816 交接清单做串行 10 轮验收。
- **从哪继续最省力**：读 `总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0816-多账号并发与Edge登录态.md` 第 8 节交接清单 + `项目深度审视报告-20260816.md` 第 7 节 P0/P1 路线图，然后直接开工。

---

## 1. 项目总览与验收标准

### 1.1 架构分层（实测）

| 层 | 位置 | 说明 |
|------|------|------|
| **backend**（FastAPI 核心自研） | `backend/app/` | providers 多线路 + services 业务服务；db.py 1467 行、main.py ~900 行、risk_control.py；28 个测试文件 ~250 用例 |
| **采集内核**（第三方深 fork） | `MediaCrawler/` | 2.5G、无 git、深度本地修改（字幕直取、多账号 env、隐私列迁移、pyproject 镜像源） |
| **转录内核**（第三方） | `pyvideotrans/` | v4.05、GPL-3.0、独立 `.venv-stt`（Py3.10） |
| **GPU ASR 服务** | 根目录 `_asr_8765.py` | faster-whisper、127.0.0.1:8765、OpenAI 兼容、同步 endpoint + 超时 240s + VAD 过滤 |
| **云端前端** | `deployments/miaoda-matrix-radar/` | NestJS + React，妙搭托管，已发布（commit b0aff55） |
| **数据** | `data/radar.sqlite3` | WAL 模式，业务主库 |
| **运行时** | `runtime/` | 打包产物：asr-service、plugins 隔离 venv、browser_data 登录态 |

### 1.2 验收标准（做到什么程度算完成）

- **短期（接手验收）**：`pytest` 全量通过（离线基线 ≥247 用例）；`start.ps1` 一键启动后 backend health 200、ASR 8765 /docs 可访问、妙搭前端可开。
- **中期（P0 闭环）**：字幕直取开启后真实命中且不再误判失败；风控三件套（熔断/错峰/请求层限速）有真实生产调用点；云端 openapi 鉴权确认并加固；根目录 git init 完成。
- **长期（业务闭环）**：S/A/B/C 评分公式落地（字段已齐：点赞/评论/收藏/分享）；选题、脚本生产两环接通；12 账号真实验收（现仅 2 账号有数据）。

---

## 2. 文件地图（精确路径）

> 项目根目录：**`D:\全自动爬取短视频、推文爆款程序\`**（✅ 实测存在；注意 0805 文档写作 E:\，0816 审视为 D:\，以 D:\ 为准）。
> ⚠️ 本项目**无 git**（根目录 `git rev-parse` 失败），改代码前建议先建基线（见 §6 P0.5）。

### 2.1 入口 / 配置（最先读）

| 路径 | 作用 | 状态 |
|------|------|------|
| `D:\全自动爬取短视频、推文爆款程序\start.ps1` | **唯一启动入口**（backend + 前端守卫 + Edge 登录态克隆）；第 95 行设 `COLLECTION_PROVIDER=mediacrawler` | 已完成 |
| `...\.env.local` | 全部运行配置（转录 / ASR / MediaCrawler / RISK 风控 / SYNC 同步 / 妙搭 Key） | 在用（gitignore 正确，但无 git 库） |
| `...\backend\app\config.py` | 环境变量读取层（✅ 实测：`COLLECTION_TRANSCRIPT_WORKERS` 默认 6、`MEDIACRAWLER_CONCURRENT_ACCOUNTS` 默认 1 上限 4、`SUBTITLE_DIRECT_ENABLED` 默认 false） | 已完成 |
| `...\README.md` | 项目自述（部分内容已与代码漂移，见 §10） | 需修订 |
| `...\pytest.ini` | pytest 配置 | 在用 |

### 2.2 backend（核心自研）

| 路径 | 作用 | 备注 |
|------|------|------|
| `backend\app\main.py` | FastAPI 入口，~900 行（过重，P2 建议拆 APIRouter） | 版本 0.3.0 |
| `backend\app\db.py` | SQLite 数据层（1467 行）：videos/video_snapshots/collection_tasks/collection_logs/video_transcriptions/account_tasks | 含同步幂等闭环 |
| `backend\app\models.py` | ORM 模型 | — |
| `backend\app\risk_control.py` | 风控：RiskCircuitBreaker / random_stagger / 代理预检 | 🔴2 **record_failure 无生产调用点（空转）** |
| `backend\app\providers\` | `mediacrawler.py`（主，含 collect_account profile 支持）/ `mediacrawler_profile_hook.py` / `demo.py` / `douyin.py`（未开通桩）/ `apizero.py`（未配置桩）/ `base.py` | 采集线路仅 MediaCrawler 一条活跃 |
| `backend\app\services\collection.py` | 采集流水线（账号循环 → run_accounts、采集-转录流水线化、互斥锁、media_url 落库） | 600+ 行 |
| `backend\app\services\transcription.py` | 转录（pyvideotrans CLI 隔离、租约、TTL janitor、recover 死代码） | — |
| `backend\app\services\transcript_router.py` | 转录 5 级降级路由（字幕直取→接口→GPU→CPU） | 含字幕熔断逻辑 |
| `backend\app\services\douyin_subtitles.py` | 字幕直取（fork detail 接口 subtitles） | 🔴3 缺陷所在 |
| `backend\app\services\platform_subtitles.py` | yt-dlp 平台字幕 | 🟠 stderr PIPE 死锁风险 |
| `backend\app\services\asr_service.py` | 对接 127.0.0.1:8765 GPU ASR | — |
| `backend\app\services\sync.py` | 云端同步（SQLite→妙搭），rejected 队列 | SYNC_PATH 默认值陷阱 |
| `backend\app\services\export.py` | Excel 导出（README 声称 3 sheet，实际 2） | — |
| `backend\app\services\multi_account\` | 并发池 7 模块：`browser_profiles`（端口自增）/ `global_limiter`（漏桶）/ `retry`（指数退避）/ `account_pool`（线程池）/ `wal_queue`（串行写）/ `runner`（调度）/ `edge_cleanup`（三层窗口清理） | 核心新增 |
| `backend\tests\` | 28 个测试文件、~250 用例（离线可跑 ≥247） | 最强环节 |

### 2.3 第三方内核（只读基准）

| 路径 | 说明 |
|------|------|
| `MediaCrawler\` | 深 fork 无 git；关键补丁：4 处账号级 env 注入（`MEDIACRAWLER_CDP_PORT / USER_DATA_DIR / CDP_CONNECT_EXISTING / ACCOUNT_DB`）、字幕直取 4 文件、隐私列迁移、pyproject 清华镜像 |
| `MediaCrawler\config\base_config.py`（或对应配置） | 采集参数；`MEDIACRAWLER_BUDGET_*` **grep 零命中（预算未被上游执行）** |
| `MediaCrawler\media_platform\douyin\login.py` | 登录（`MEDIACRAWLER_LOGIN_SETTLE/REDIRECT_SECONDS`） |
| `MediaCrawler\media_platform\douyin\crawler_util.py` | 二维码弹图开关 `MEDIACRAWLER_SKIP_QRCODE_DISPLAY` |
| `pyvideotrans\` | 转录引擎（独立 venv，升级前需核对 FAST_MODE 参数契约） |
| `integrations\social-media-toolkit\` | Apache-2.0，git 干净，未接入业务链路 |

### 2.4 数据 / 运行产物

| 路径 | 状态 |
|------|------|
| `data\radar.sqlite3` | 主库，WAL 模式（含 -shm/-wal） |
| `data\matrix_radar.db` | ❓ 0 字节废文件（可删，需确认） |
| `data\browser_data\` | Edge 登录态目录（25 账号克隆成功） |
| `data\temp_media\` | 转录临时 job 目录（实测 57 目录 ~490MB 滞留，janitor 需后端运行时才清） |
| `data\imports\` / `data\appdata\` | 导入 / 应用数据 |
| `backups\` | 50+ 备份文件 ~122MB（batch-reset-round-* 带 manifest 可校验；radar_rN/mc_rN 无 manifest） |
| `runtime\` | 27 万文件打包产物（asr-service / plugins venv / browser_data） |
| `backend_backup_20260806_phase1\` | 旧备份目录（P2 建议归档） |
| 根目录大量 `_*.py` / `_*.json` | 历史诊断/临时脚本（P2 清理项，勿直接删需确认） |
| 根目录 `app.log` | 日志（无轮转） |
| `抖音运营工具箱\` `剩下的插件\` | 未签名 exe 120MB + 冗余插件（KrillinAI/VideoLingo/DouK-Downloader 等，均未接入链路） |

### 2.5 云端（妙搭）

| 路径 | 说明 |
|------|------|
| `deployments\miaoda-matrix-radar\server\src\radar\radar.openapi.controller.ts` | 云端 openapi 控制器（🔴4 **无守卫 + AuthN fail-open + RLS 敞开**） |
| `deployments\miaoda-matrix-radar\server\src\radar\radar.service.ts` | importRows 不校验 token |
| `deployments\miaoda-matrix-radar\client\src\...\radar-selection.ts` | 前端达人选择初始化（0817 已修：URL>当前选择>全选兜底） |
| `deployments\miaoda-matrix-radar\client\vite.config.ts` | 应用 ID 硬编码 `/app/app_17bkk0a8pt8/` |

---

## 3. 已完成工作（全量逐条）

| # | 事项 | 产出物 / 验证 | 来源 |
|:-:|------|------|------|
| 1 | **MediaCrawler 三模式采集**（detail / creator / search） | 采集免费 ¥0，SQLite 去重 | 改良版介绍文档 |
| 2 | **本地主力 + 云端应急双架构** | 仅 `.env` `RUN_MODE` 切换，代码零改动 | 改良版介绍文档 |
| 3 | **多账号并发池** | `multi_account/` 6 模块（现 7 模块）；fork 4 处 env 注入；5 轮测试全过、全量回归 264 passed | 0816 并发日志 |
| 4 | **Edge 一次登录**（不加装 CookieCloud，登录态不出本机） | 克隆原子化 + robocopy 自动刷新 + 三级登录态探测；**25/25 账号目录克隆成功**；代码总监 5 轮评审 62/70 定稿 | 0816 并发日志 |
| 5 | **对抗/风控组件投产** | 保留：熔断/随机错峰/全局限速/指数退避/curl_cffi/mss 截图/patchright/CloakBrowser/fingerprintjs 自测页；**10 轮实测零账号封锁**；新增服务只监听 127.0.0.1 | 0816 对抗日志 |
| 6 | **组件清理**（付费/无法投产） | 卸载 NopeCHA/代理池运行时/nodriver/Botright/haipproxy，释放 ~60MB+ | 0816 对抗日志 |
| 7 | **速度专项优化**（0817） | 转录工作线 4→6（+50%）；错峰收窄 15-30s（省 ~2.5min/轮）；采集-转录流水线化（单账号 542s→~480s）；VAD 过滤（长视频提速 30-50%）；media_url 落库（官方直链）；主页资料并入采集（省 ~20s/账号）；登录等待 env 化；云端同步黑名单降噪；二维码弹图根治 | 0817 速度日志 |
| 8 | **图文笔记识别** | aweme_type=163/2 只采数据不转录（避免 BGM 歌词当口播稿） | 0816 并发日志 |
| 9 | **字幕直取结论** | 抖音 web 端无字幕数据源（多轮实测）→ 口播稿走"下载 + GPU ASR"已闭环 **149/150 达标**；`SUBTITLE_DIRECT_ENABLED` 默认关 | 0816/0817 日志 |
| 10 | **前端切换** | 删除旧 vinext 前端（780M），妙搭为唯一前端；start.ps1 守卫升级 | 0816 并发日志 |
| 11 | **云端 BUG 修复** | 账号页查看视频固定指向同一达人 → 修复 radar-selection.ts 初始化优先级 + 达人 ID 大小写不敏感；**已部署（commit b0aff55）**；前端测试 12 通过、tsc 零错误 | 0817 速度日志 |
| 12 | **转录 5 级降级** | 字幕直取→接口→GPU→CPU 多级兜底（采集侧 Failover 未做） | 深度审视报告 |
| 13 | **数据层严谨** | 同步幂等闭环（唯一索引 + DO UPDATE + imported 核对）；备份带 sha256 manifest；转录租约防覆盖；WAL + busy_timeout=15000 | 深度审视报告 |
| 14 | **安全基线** | SSRF 白名单、日志凭据脱敏、验证码自动求解硬禁用（后 0816 突破）、密钥集中 .env.local | 深度审视报告 |

---

## 4. 当前精确进度

- **最后一次有效操作（0817）**：速度优化批 + Edge 窗口卫生定版（`edge_cleanup.py` 三层清理）+ 云端 BUG 修复已部署（commit b0aff55）+ 云端账号映射补建（+db-execute 批量 INSERT 28 个对标账号）。
- **代码状态**：根目录**无 .git**；`.env.local` 中 `MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`（串行）、`EVIL0CTAL_API_BASE_URL` 已配、`RISK_*` 开关按 0816 决策已设（NopeCHA/代理池已关）。
- **数据状态（0816 只读实测）**：videos=45、video_snapshots=96（synced=80 / **rejected=16** / pending=0）、collection_tasks=116、collection_logs=9336、video_transcriptions=33（成功 23 / 失败 10）；MediaCrawler 库 douyin_aweme=66、评论=947；**12 个 internal 账号仅 2 个有真实数据（华哥 21、鱼哥 8）；播放量 96/96 全 NULL**。
- **前端**：妙搭 `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/`（dev:server 3100 + dev:client 3000）。

---

## 5. 未完成事项（全量逐条）

> 优先级：**P0**（接手后立即）＞ 0816 交接清单 ＞ **P1**（两周内）＞ **P2**（月度）。源自 `项目深度审视报告-20260816.md` §7 与 `0816-多账号并发与Edge登录态.md` §8。

### P0（立即，一周内）

| # | 事项 | 阻塞 / 前置 | 做到什么程度算完成 |
|:-:|------|------|------|
| P0.1 | **字幕直取成功被误判失败**（🔴3） | 无 | `SUBTITLE_DIRECT_ENABLED=true` 下真实命中计为成功、口播稿落库；补端到端测试 |
| P0.2 | **MediaCrawler 商用合规决策**（🔴1） | 需用户书面拍板：书面授权 / 切 Evil0ctal 接口 / 默认改 demo 三选一 | 形成书面记录；启动默认不再"开机即侵权" |
| P0.3 | **云端同步零鉴权**（🔴4） | ❓ 需向妙搭平台确认 openapi 网关策略 | OpenAPI 控制器补 token 校验；确认 FORCE_AUTHN_TOKEN |
| P0.4 | **风控三件套接线**（🔴2） | 无 | `record_failure` 有真实调用点；stagger 传入 run_accounts；漏桶下沉到请求层 |
| P0.5 | **版本控制落地**（🔴5） | 无 | 根目录 `git init` + 补 .gitignore（排除 .env.local/data/backups/runtime/MediaCrawler）+ MediaCrawler 建 git 基线 |

### 0816 交接清单（原优先级 1>2>3）

| # | 事项 | 现状 | 建议做法 |
|:-:|------|------|---------|
| 6 | **10 轮验收测试** | 第 1 轮并发模式被抖音新环境验证阻断；串行重跑被用户终止 | 串行（CONCURRENT=1）重跑 10 轮，每轮随机 10 账号×20 视频；测试脚本已删需重写 |
| 7 | **抖音号→sec_uid 自动解析** | 缺 creator_url 账号目前只能跳过 | fork search hook（USER 频道搜索）+ 后端三层缓存回填 |
| 8 | **字幕直取 Phase 0 实测** | 覆盖率未验证 | fork client 有界采样 300 条 detail，统计 video.subtitles 存在率（≥20% 才投产） |
| 9 | **字幕直取灰度** | `SUBTITLE_DIRECT_ENABLED` 默认关 | Phase 0 达标后 20%→50%→100%，每级 3 天 |
| 10 | **多账号并发登录态** | 克隆 Cookie 对新 Edge 无效（抖音环境验证） | 现实路径：串行验收；或每账号首次人工扫码后 profile 持久 |
| 11 | **clone 脚本自动刷新验证** | start.ps1 mtime 比对已实施 | 需一次真实"共享重登→启动→自动克隆"场景验证 |

### P1（两周内）

| # | 事项 | 说明 |
|:-:|------|------|
| 12 | 恢复 16 条 rejected 快照 | `POST /api/sync/retry-rejected`；修正 `SYNC_PATH` 默认值（当前指向旧 Sites 契约） |
| 13 | 备份回收策略 | backups 无保留/回收（线性膨胀）；radar_rN 补 manifest；云端恢复后自动补发 |
| 14 | 转录健壮性 | 全局封顶；字幕"预期缺失"不计熔断；yt-dlp stderr drain；ASR 路径补 BGM 闸门 |
| 15 | 本地 API 安全 | 写操作加本机 token；异常回显收敛（main.py:293-304 回显 str(exc)）；.env 移出 git；xlsx 升级（CVE-2023-30533） |
| 16 | 文档-代码漂移修订 | 修正默认转录数（文档 10 代码 2）、导出 sheet 数、账号口径 12/13/25、人机验证判定描述 |
| 17 | 采集侧 FailoverProvider | 复用转录 5 级降级模式，实现多线路降级 |

### P2（月度）

| # | 事项 |
|:-:|------|
| 18 | 爆款评分公式落地（S/A/B/C，先静态阈值版再动态校准）——字段已齐 |
| 19 | 冗余插件归档、模型下载自动化、登录态 ACL 收紧 + 加密备份、索引与日志保留策略 |
| 20 | 12 账号逐账号真实验收 + 播放量口径决策（接受 NULL / 换数据源，需用户拍板） |
| 21 | 云端 video 表加 transcript 列，打通口播稿上云 |

---

## 6. 下一步行动计划（命令级）

> 全部命令在 PowerShell 执行。**首次接手顺序：先验证环境（§6.1）→ 修 P0.1 → 清理 0816 清单 → 推进 P0.2-P0.5。**

### 6.1 第一步：验证"续上了"（必做）

```powershell
cd "D:\全自动爬取短视频、推文爆款程序"

# 1) 全量测试（离线基线 ≥247 用例；0816 基线 279 passed / 2s）
python -m pytest backend/tests -q

# 2) 启动整套系统（唯一入口；注意 PowerShell 5.1 按 GBK 解析，脚本内新加逻辑用纯 ASCII）
powershell -ExecutionPolicy Bypass -File ".\start.ps1"

# 3) 确认各服务就绪
curl.exe http://127.0.0.1:8000/api/health      # backend → 200
# ASR 服务独立启动（如未随 start.ps1 拉起）：
python _asr_8765.py                            # 127.0.0.1:8765，浏览器开 /docs 可访问
# 前端：浏览器打开 http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/

# 4) 数据快照比对（应接近 §4 数字）
python -c "import sqlite3;c=sqlite3.connect('data/radar.sqlite3');print(c.execute('select count(*) from videos').fetchone(), c.execute(\"select count(*) from video_snapshots where sync_status='rejected'\").fetchone() if c.execute(\"PRAGMA table_info(video_snapshots)\").fetchall() else '')"
```

**✅ 续上了的信号**：测试通过 + health 200 + ASR /docs 可访问 + 前端可开 + videos≈45/rejected≈16。

### 6.2 第二步：修 P0.1 字幕直取缺陷（最高优先）

根因链：`douyin_subtitles.py:29`（persists_result=True）+ `:41-44`（成功返回 `srt_text=""`）→ `collection.py:154-162`（持久化回调失败抛 RuntimeError）→ `db.py:1087-1090`（srt_text 非空校验 return False）→ 命中即误判失败、口播稿丢失。

```powershell
cd "D:\全自动爬取短视频、推文爆款程序"

# 1) 定位（先读代码确认行号仍准确）
Get-Content .\backend\app\services\douyin_subtitles.py | Select-Object -First 60
Get-Content .\backend\app\services\transcript_router.py | Select-Object -Skip 690 -First 30

# 2) 修复二选一（建议 A）：
#    A. 将 douyin_subtitle 从 _persisted_provider_names 排除（正文已存 videos.subtitle_text）
#    B. 对 douyin_subtitle 来源做 SRT 空值容忍
# 3) 补端到端测试：SUBTITLE_DIRECT_ENABLED=true 真实命中场景
# 4) 回归 + 提交基线（先 git init 见 6.5，或临时 cp 备份）
```

### 6.3 第三步：0816 清单 — 串行 10 轮验收

```powershell
# 确认串行：.env.local 中 MEDIACRAWLER_CONCURRENT_ACCOUNTS=1
# 重写 10 轮验收脚本（原脚本已删）：每轮随机 10 账号×20 视频，串行模式，90 分钟/轮上限，轮间冷却 30s
# 统计：成功率 + 平均耗时；逐轮复盘迭代；抹数据再下一轮（SQL 清 videos 等 9 表 + douyin_aweme 2 表）
# 每轮结束时清理所有项目打开的 Edge 窗口（edge_cleanup.py 三层清理已就绪）
```

### 6.4 第四步：P0.2-P0.5（需用户参与项标注 ❓）

```powershell
# P0.2 商用合规：先向用户提交三选项书面记录（授权/切源/改demo），未拍板前可临时把 start.ps1 默认 provider 改 demo
# P0.3 云端鉴权：先向妙搭平台确认 /openapi/* 网关策略（❓）；随后在 radar.openapi.controller.ts 补守卫
# P0.4 风控接线：在 runner.py 失败路径 + mediacrawler.py 风险信号处接 record_failure；run_accounts 传 stagger；漏桶下沉请求层
# P0.5 版本控制：
git init
# 创建 .gitignore，至少排除：.env.local / data/ / backups/ / runtime/ / MediaCrawler/ / pyvideotrans/ / app.log / backend_backup_*/
git add -A; git commit -m "initial baseline 2026-08-17"
# MediaCrawler 单独建基线：cd MediaCrawler; git init; git add -A; git commit -m "MC fork baseline"; git remote add upstream <官方源>
```

### 6.5 后续（P1/P2 分批）

```powershell
# P1-12 恢复 rejected：
curl.exe -X POST http://127.0.0.1:8000/api/sync/retry-rejected
# 先修 backend/app/config.py 的 SYNC_PATH 默认值（当前 /api/sync 旧契约，云端真实 /openapi/radar/sync）

# P1 各项均以 "改→pytest backend/tests -q→单接口冒烟" 循环；大任务可用子代理并行（见 §12）
# P2-18 爆款评分：在 db.py 落 SQL 视图/服务函数，字段点赞/评论/收藏/分享已齐
```

---

## 7. 环境与配置依赖（完整清单）

### 7.1 软件栈

| 依赖 | 版本 / 说明 |
|------|------|
| Python | 3.11+（backend）；pyvideotrans 独立 `.venv-stt` Py3.10 |
| 包管理 | uv（部分 venv）；MediaCrawler requirements 混合锁定 |
| 采集 | MediaCrawler（深 fork）+ Playwright + Edge/CDP |
| 转录 | pyvideotrans v4.05（GPL-3.0）+ GPU faster-whisper（`_asr_8765.py`，127.0.0.1:8765） |
| 云端 | 妙搭应用 `app_17bkk0a8pt8`（NestJS + React） |
| 数据库 | SQLite（WAL） |

### 7.2 关键环境变量（`.env.local` 实测）

| 组 | 变量 | 当前值 |
|----|------|--------|
| 并发 | `MEDIACRAWLER_CONCURRENT_ACCOUNTS` | `1`（串行） |
| 登录 | `MEDIACRAWLER_LOGIN_SETTLE_SECONDS` / `MEDIACRAWLER_LOGIN_REDIRECT_SECONDS` / `MEDIACRAWLER_SKIP_QRCODE_DISPLAY` | 已配 |
| 浏览器 | `MEDIACRAWLER_BROWSER_DATA_DIR`（D 盘项目内路径）/ `MEDIACRAWLER_BROWSER_ENGINE` / `MEDIACRAWLER_BROWSER_ENGINE_CHAIN` | 已配 |
| 风控 | `RISK_CIRCUIT_BREAKER` / `RISK_STAGGER_ENABLED` / `RISK_STAGGER_MIN/MAX_SECONDS` / `RISK_CURL_CFFI` / `RISK_EVIDENCE_SCREENSHOT` / `RISK_BROWSER_ROUTE` | 已配（`RISK_NOPECHA_ENABLED=false`、`RISK_PROXY_ENABLED=false`，组件已卸载） |
| 转录 | `TRANSCRIPTION_ENABLED` / `PYVIDEOTRANS_*` / `TRANSCRIPTION_TIMEOUT_SECONDS` / `ASR_SERVICE_BASE_URL` / `ASR_SERVICE_MODEL` | 已配 |
| 同步 | `SYNC_BASE_URL` / `SYNC_PATH`（⚠️ 默认值陷阱）/ `SYNC_TOKEN` / `MIAODA_API_KEY` / `SITES_BYPASS_TOKEN` | 已配 |
| 其他 | `EVIL0CTAL_API_BASE_URL`（已配）/ `HF_HOME` / `UV_CACHE_DIR` / `PIP_CACHE_DIR` / `SPIDERHUBS_API_KEY`（遗留未用） | — |

> 🔑 **密钥脱敏**：token/Key 均在 `.env.local`，不写入本文档。改 `.env.local` 后需重启 backend 生效。

---

## 8. 数据与状态快照

- **主库**：`data/radar.sqlite3`（WAL），见 §4 数据状态。
- **临时数据**：`data/temp_media/` ~490MB 滞留（后端未运行时 janitor 不跑）；`data/matrix_radar.db` 0 字节废文件（❓ 待确认可删）。
- **需保留**：`backups/`、`runtime/browser_data`（登录态）、`MediaCrawler` fork 补丁（无 git 备份）。
- **清理注意**：根目录大量 `_*.py`/`_*.json` 诊断脚本属中间产物，**删除前需逐条确认**（涉及登录态探测、Cookie 导出等可能仍有用）。

---

## 9. 关键决策与踩坑记录

| 决策 / 踩坑 | 结论 | 规避 |
|------|------|------|
| 抖音字幕直取 | web 端无字幕数据源（detail 无 cla_info/subtitles、播放器无字幕请求、分享页无 videoInfoRes 多轮实测）→ 弃直取，走下载+GPU ASR | 勿再投入 web 直取；APP 签名 X-Gorgon 方案待用户拍板 |
| 多账号并发免登录 | 克隆 Cookie 对**新 Edge 环境**不保证免验证（抖音识别新设备要求扫码）→ 串行共享登录态全自动免扫码 | 验收走串行；并发需每账号首次人工扫码 + profile 持久 |
| 图文笔记转录 | aweme_type=163/2 硬转录会把 BGM 歌词当口播稿（第 5 轮历史假成功教训）→ 只采数据不转录 | 转录前判 media_kind |
| Edge 一次登录 | 不加装 CookieCloud（登录态不出本机）；克隆原子化 staging→.trash→切换→回滚 + robocopy /R:2 /W:2 + 三级登录态探测 | 25/25 克隆成功 |
| 对抗组件 | 2026-08-16 用户决策突破合规红线，①类组件全部投产、风险自担；付费/无法投产的删除释放硬盘 | 只留免费实测可用的 8 项 |
| start.ps1 编码坑 | PowerShell 5.1 按 GBK 解析无 BOM UTF-8 → 中文注释曾致语法错误 | 新加逻辑一律纯 ASCII |
| 多账号 8 处崩溃 | fork `USER_DATA_DIR % config.PLATFORM` 注入绝对路径必崩（TypeError）→ isabs 守卫跳过格式化 | 绝对路径注入处统一守卫 |
| backend 实例混淆 | 8000 端口偶现 Anaconda python 实例（有守护进程）——功能一致但排查时注意解释器来源 | 看 tasklist 确认解释器 |
| 云端"无条件全选"BUG | 独立 Route 重挂载覆盖用户点击 → 初始化优先级 URL>当前选择>全选兜底 | 已部署 b0aff55 |
| 熔断"空转"教训 | 0815 声称"熔断器已接入生产"经 0816 代码核验为**空实现**（record_failure 无生产调用） | 后续引用测试结论以 0816 审视报告为准 |

---

## 10. 风险与待确认项（❓）

| # | 风险 / 待确认 | 等级 | 说明 |
|:-:|------|:---:|------|
| 1 | MediaCrawler 非商用许可 + 默认商用启用正面冲突 | 🔴 | 商用侵权风险"开机即发生"；需 P0.2 决策 |
| 2 | 云端 openapi 零鉴权（数据投毒） | 🔴 | 依赖妙搭网关策略假设，❓ 需向平台确认 |
| 3 | 风控三件套空转（封号风险放大） | 🔴 | 并发放量前必接 |
| 4 | 字幕直取上线即误判失败 | 🔴 | 灰度/上线必踩，先修 |
| 5 | 无版本控制 | 🔴 | 误改/损坏恢复证据弱；MediaCrawler 补丁不可 diff |
| 6 | 本地 API 无鉴权（/api/collections 可触发真实采集） | 🟠 | 仅 127.0.0.1 绑定兜底 |
| 7 | 播放量口径（96/96 全 NULL） | 🟠 | ❓ 用户拍板：接受缺失 / 换数据源 |
| 8 | 项目代码根目录在 D:，但 0805 文档写作 E: | 🟡 | 以 D: 为准（实测存在） |
| 9 | 抖音平台风控/法律风险 | 🟡 | 用户 0816 已书面自担；持续监控风控信号 |
| 10 | rejected=16 快照是否需恢复 | 🟡 | ❓ 视业务需要；重跑 retry-rejected 可恢复 |

**遇到问题找谁**：本知识库 `总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/`（全部开发日志 + 深度审视报告 + 方案文档）；决策项找用户拍板。

---

## 11. 续作启动手册

**从零恢复完整步骤**：

```powershell
# 1) 读规则（本项目若建 CLAUDE.md 会自动加载；无则先读本文档）
# 2) 验证环境（§6.1 四连）
cd "D:\全自动爬取短视频、推文爆款程序"
python -m pytest backend/tests -q
powershell -ExecutionPolicy Bypass -File ".\start.ps1"
# 3) 确认 health/ASR/前端
# 4) 修 P0.1 → 跑 P0.2-P0.5 → 串行 10 轮验收
```

**如何验证"续上了"（成功信号）**：
- `pytest backend/tests -q` → **≥247 通过（0816 基线 279 passed / 2s）**
- `curl.exe http://127.0.0.1:8000/api/health` → **HTTP 200**
- `http://127.0.0.1:8765/docs` → **ASR 服务文档页可开**
- `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/` → **妙搭前端可开**
- 手动触发一轮采集 `POST /api/collections/trigger` → **videos 表行数增加、飞书收到通知**

---

## 12. 按 Claude Code 定制的附加内容

1. **建议建项目 `CLAUDE.md`**（放在 `D:\全自动爬取短视频、推文爆款程序\CLAUDE.md`），写入三条硬规则：① 启动一律 `start.ps1`；② 改代码前后必跑 `pytest backend/tests`；③ 涉及 `.env.local`/登录态/对抗组件的变更须先与用户确认（风险项）。本交接文档可直接作为项目 CLAUDE.md 的"项目现状"附录。
2. **可并行派生子代理**：P0/P1 中跨模块任务（如风控接线涉及 collection.py/runner.py/risk_control.py、云端鉴权涉及前后端）可拆子代理并行；**P0.5 建 git 基线是其他改造的前置，先串行做完**。
3. **任务执行节奏**：每项按"定位文件（grep 确认行号，勿信文档行号）→ 改 → pytest 回归 → 单接口冒烟"循环；文档中所有 `文件:行号` 证据均来自 0816 静态审视，**接手时以实际代码为准**。
4. **提问入口**：§5 中所有 ❓ 项、§10 待确认项、以及"先本地验证→联系作者商用授权"等合规决策，遇到不确定立即向用户确认，不要自行假设。
