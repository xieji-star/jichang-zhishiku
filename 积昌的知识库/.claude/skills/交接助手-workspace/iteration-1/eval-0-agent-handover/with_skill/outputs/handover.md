---
项目: 矩阵内容雷达（全自动爬取短视频、推文爆款程序）
交接对象: AI 智能体（Claude Code）
交接日期: 2026-08-17
---

# 矩阵内容雷达 交接文档（给 AI 版）

## 0. 交接摘要（启动包）

> 本项目是**矩阵内容雷达**——一套本地部署的短视频/推文爆款采集与分析系统：基于 MediaCrawler fork 在本地采集抖音数据，按 S/A/B/C 评分标准识别爆款，供华哥/七哥/鱼哥 3 组共 12 个矩阵账号做选题与竞品分析。采集结果统一同步到妙搭云端（唯一前端），飞书为唯一对外出口。

**当前进度**：风控/对抗组件已全部接入生产（10 轮测试零封锁）、多账号并发池与 Edge/Firefox 登录态已落地、速度专项优化完成（单账号 542s→~480s）、云端 BUG 已修复。**测试暂停期**——上一任停在 0817 速度优化批 + 云端修复收官，**10 轮验收测试尚未跑完**（并发模式被抖音新设备验证阻断，需按串行模式重跑）。

**最关键三件事**：
1. ✅ 已完成：风控组件接线 + 对抗组件投产 + 多账号并发池 + Edge 一次登录 + 速度优化批（详见 §3）
2. 🛑 卡在哪：抖音对"新 profile 的 Edge/多开"做环境验证要求扫码，并发免登录被平台阻断；当前已切 **Firefox 默认引擎**（`MEDIACRAWLER_BROWSER_ENGINE=firefox-system`）定版
3. 🚀 下一步第一件事：串行模式（`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`）重跑 **10 轮验收测试**（每轮随机 10 账号 × 20 视频），再按 §6 逐项推进

**从哪继续最省力**：先读知识库交接清单 [[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0816-多账号并发与Edge登录态#8. 交接清单：未完成事项]]（优先级 1 > 2 > 3），项目启动一律用 `.\start.ps1`，测试数据清理用 SQL（videos 等 9 表 + douyin_aweme 2 表）。

---

## 1. 项目总览与验收标准

- **一句话定位**：本地按需采集抖音短视频/推文数据，自动识别爆款（S/A/B/C 四档评分），供矩阵账号内容选题。
- **最终目标**：全自动"爬取 → 转录口播稿 → 爆款评分 → 云端展示"流水线，覆盖 12 个自有账号 + 28 个对标账号，成本约 ¥0.5/月。
- **整体完成度估算**：约 75%。核心采集/转录/风控/前端已闭环，剩验收测试、sec_uid 自动解析、字幕直取灰度、12 账号逐账号真实采集验收。

**验收标准（做到什么程度算完成）**：
1. 10 轮验收测试全过：每轮随机 10 账号 × 20 视频，串行模式，账号级成功率达标、零账号封锁（参考 0816 第 10 轮：279/2s pytest、成功率 100%）。
2. 12 个自有账号各完成一次真实采集验收（新增的 11 个 sec_user_id 映射仍需逐账号实测）。
3. 全量回归 `pytest` 281 collected（279 passed + 2 skipped）全绿。
4. 字幕直取 Phase 0 实测通过（video.subtitles 存在率 ≥20%）后灰度 20%→50%→100%。
5. 爆款评分（S/A/B/C）各账号基准线校准完成，飞书同步、爆款评分、口播分析导航可用（当前前端已禁用）。

---

## 2. 文件地图（精确路径）

> ⚠️ **项目唯一正式工作目录是 D 盘**（README 明示：D:\ 是唯一源目录；F 盘旧项目不再修改，仅历史备份/知识库只读参考）。知识库笔记在 F 盘 vault。

### 项目代码（D 盘，真实路径）

| 路径 | 作用 | 状态 |
|------|------|------|
| `D:\全自动爬取短视频、推文爆款程序` | 项目根（唯一源目录） | ✅ 当前 |
| `D:\全自动爬取短视频、推文爆款程序\start.ps1` | **唯一启动入口**（含安装/守护/登录态克隆/Firefox 引擎判断） | ✅ 已改（0817 Firefox 定版） |
| `D:\全自动爬取短视频、推文爆款程序\.env.local` | 全部配置与密钥（**密钥已脱敏，勿外发**） | ✅ 当前生效 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\main.py` | FastAPI 入口（uvicorn，端口 8000；含 `/api/risk-control/health`） | ✅ |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\config.py` | 配置中心（全 env 可配） | ✅ 已改 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\db.py` | SQLite 库连接 + 迁移（videos 加列、account_tasks 表等） | ✅ 已改 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\risk_control.py` | 风控/对抗组件（熔断器、随机错峰、全局限速、curl_cffi、代理预检、mss 截图、broker_env） | ✅ 已投产 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\providers\mediacrawler.py` | MediaCrawler fork 子进程调度（env 注入、代理预检、风控信号富化、证据截图） | ✅ 已改 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\services\collection.py` | 采集流水线（账号循环、错峰、熔断、采集-转录流水线化） | ✅ 已改 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\services\multi_account\` | 多账号并发池（browser_profiles / global_limiter / retry / account_pool / wal_queue / runner）+ **edge_cleanup.py**（0817 新增窗口卫生） | ✅ 已落地 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\services\transcription.py` | 口播稿转录流水线（pyvideotrans STT + GPU ASR 双通道） | ✅ |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\services\transcript_router.py` | 转录路由 | ✅ |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\services\sync.py` | 云端同步（妙搭，含黑名单降噪持久化） | ✅ 已改 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\services\plugin_routes.py` | 插件路由/探针（curl_cffi 优先 + with_retry + 异常回退） | ✅ 已改 |
| `D:\全自动爬取短视频、推文爆款程序\backend\app\services\douyin_subtitles.py` | 字幕直取 provider（SUBTITLE_DIRECT_ENABLED 默认关） | ⏸ 未灰度 |
| `D:\全自动爬取短视频、推文爆款程序\backend\tests\` | pytest 测试（约 27 个测试文件） | ✅ 281 collected |
| `D:\全自动爬取短视频、推文爆款程序\MediaCrawler\` | MediaCrawler fork（含独立 .venv；env 注入 `MEDIACRAWLER_CDP_PORT`/`USER_DATA_DIR`/`CDP_CONNECT_EXISTING`/`ACCOUNT_DB`） | ✅ fork 4 处 |
| `D:\全自动爬取短视频、推文爆款程序\pyvideotrans\` | pyvideotrans STT（官方 `cli.py --task stt`；`.venv-stt` Python 3.10；model=small） | ✅ |
| `D:\全自动爬取短视频、推文爆款程序\runtime\asr-service\_asr_8765.py` | GPU ASR 服务（端口 8765；0817 改同步 endpoint + 超时 240s + VAD 静音过滤） | ✅ 已改 |
| `D:\全自动爬取短视频、推文爆款程序\runtime\.venv-asr\` | GPU ASR 专属 venv | ✅ |
| `D:\全自动爬取短视频、推文爆款程序\deployments\miaoda-matrix-radar\` | 妙搭前端（**唯一前端**；dev:server 3100 + dev:client 3000） | ✅ 已部署 commit b0aff55 |
| `D:\全自动爬取短视频、推文爆款程序\data\radar.sqlite3` | 主业务库（SQLite） | ✅ 当前 |
| `D:\全自动爬取短视频、推文爆款程序\data\browser_data\` | 登录态目录（Firefox: `ff_dy_user_data_dir`；Edge: `cdp_dy_user_data_dir`） | ✅ 已迁 D 盘 |
| `D:\全自动爬取短视频、推文爆款程序\scripts\clone-browser-profiles.ps1` | Edge 登录态克隆脚本（robocopy 原子化） | ✅ |
| `D:\全自动爬取短视频、推文爆款程序\pytest.ini` | pytest 配置（pythonpath = . + backend；testpaths = backend/tests） | ✅ |

### 知识库文档（F 盘 vault，只读参考）

| 路径 | 内容 |
|------|------|
| `F:\积昌的知识库 - 副本\自动维护知识库\wiki\自媒体运营\短视频爆款采集系统.md` | 项目 wiki 总页（采集架构/评分标准/演进史） |
| `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\开发日志\` | 开发日志（0809/0810/0811/0814/0815×2/0816×2/**0817**） |
| `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\报错修复日志\0815-多账号采集与缺链接报错修复.md` | 报错修复（% 格式化崩溃 + 缺 creator_url） |
| `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\风控接线技术方案-20260816.md` | 风控接线技术方案（A→B'' 全程记录） |
| `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\本地部署短视频分析程序介绍文档（改良版）.md` | 项目介绍文档 |
| `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\矩阵号爆款数据分析与标准定义.md` | S/A/B/C 评分标准定义 |

---

## 3. 已完成工作（全量逐条）

**0815 — 风控组件接入生产**（[[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0815-风控组件接入生产]]）
- 新建 `backend/app/risk_control.py`，熔断器/curl_cffi/随机错峰/代理预检/mss 截图全接线；`collection.py`/`providers/mediacrawler.py`/`main.py` 改接线；`/api/risk-control/health` 新接口。
- 实测：5 次全过（含端到端真实采集 videos=2）；20 条全量采集成功率 **76% → 100%**（argus 风控触发 1 次仍 20/20 完成，blocked=0）；248 passed + 新增 21 个 `test_risk_control.py` 单测。

**0816 — 多账号并发池 + 登录态 + 对抗组件**（[[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0816-多账号并发与Edge登录态]] / [[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0816-对抗组件全面启用]]）
- **多账号并发池**：MediaCrawler fork 4 处 env 注入（每账号独立端口/登录态目录/采集库）；`multi_account` 包 6 模块零依赖；单账号特例走老路径；5 次测试 + 全量回归 264 passed。
- **图文笔记识别**：aweme_type=163 图文/2 图集只采数据不生成口播稿（避免 BGM 歌词当口播稿），`_read_changed` → media_kind → videos 加列 → 转录两处跳过。
- **字幕直取插件**：A+C 整合方案（代码总监终审 56/70），fork 4 文件 + backend 5 处接线；`SUBTITLE_DIRECT_ENABLED` **默认关闭**，Phase 0 实测未做。
- **前端切换**：物理删除旧 vinext 前端（780M），妙搭 `app_17bkk0a8pt8` 为唯一前端；start.ps1 守卫升级（旧目录自动清除 + 3000 端口清退）。
- **多账号报错修复**：8 处 `USER_DATA_DIR % config.PLATFORM` 绝对路径必崩（isabs 守卫修复）；缺 creator_url 账号任务启动前过滤跳过；5 轮测试 100%。
- **Edge 一次登录**：B++++ 62/70 定稿（不加装 CookieCloud，本地零依赖）；克隆原子化（staging→.trash→切换→回滚）+ robocopy 自动刷新 + 三级登录态探测；25/25 账号目录克隆成功。
- **对抗组件全面启用（2026-08-16 用户决策，个人使用无红线，风险自担）**：curl_cffi/熔断/错峰/限速/证据截图保留投产；NopeCHA 卸载（无 Key）、代理池运行时删除、nodriver 卸载、Botright/haipproxy 回滚；patchright/CloakBrowser/fingerprintjs 保留。
- **10 轮测试**（串行）：全部通过，成功率 100%，**十轮真实采集零账号封锁**（blocked=0/429=0/403=0/verification=0）。

**0817 — 速度优化批 + 云端修复**（[[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0817-速度优化批与云端修复]]）
- 转录工作线 4→6（+50%）；错峰收窄 20-60s→15-30s（省 ~2.5 分钟/轮）；采集-转录流水线化（542s→~480s）；VAD 静音过滤（长视频提速 30-50%）；转录异步修复（`_asr_8765.py` 同步 endpoint + 超时 240s，消除 timed out）；media_url 落库（转录走官方直链）；主页资料并入采集进程（省 ~20s/账号）；登录固定等待 env 化（省 ~7s/账号）；云端同步黑名单降噪（消除每轮 150 条无效重试）；二维码弹图根治（`MEDIACRAWLER_SKIP_QRCODE_DISPLAY`）。
- **Edge 窗口卫生**：新增 `multi_account/edge_cleanup.py` 三层清理（账号级/hook级/任务级终态）；唯一保留边界=cmdline 无项目目录。
- **云端 BUG 修复**：账号页→视频页固定指向同一达人，根因=独立 Route 组件重挂载时"无条件全选"覆盖用户点击；修复 `radar-selection.ts` 初始化优先级 **URL 指定 > 当前选择 > 全选兜底** + 达人 ID 大小写不敏感；已部署妙搭（commit b0aff55）；前端测试 12 通过、tsc 零错误；云端账号映射补建 28 个对标账号。
- **字幕直取结论**：抖音 **web 端无字幕数据源**（detail 接口无 subtitles 字段等多轮实测）→ 口播稿走 **下载 + GPU ASR**（已闭环 149/150 达标）；APP 签名（X-Gorgon）直取待用户拍板。
- **Firefox 默认引擎定版**（start.ps1）：`MEDIACRAWLER_BROWSER_ENGINE=firefox-system`；登录态落 `data\browser_data\ff_dy_user_data_dir`（Playwright 自启 Firefox 复用，首次手动扫码一次）；不再启动 9222 CDP Edge、不做 B++++ 克隆。

---

## 4. 当前精确进度

- **最后一步有效操作**：0817 收官——速度优化批落地 + Edge 窗口卫生 + 云端 BUG 修复（妙搭已部署 commit b0aff55）+ Firefox 默认引擎定版。
- **当前代码/配置状态**：
  - `.env.local` 关键现值：`TRANSCRIPTION_ENABLED=true`；`PYVIDEOTRANS_MODEL=small`；`ASR_SERVICE_BASE_URL=http://127.0.0.1:8765`；`ASR_SERVICE_MODEL=Systran/faster-whisper-small`；`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`（**串行**）；`MEDIACRAWLER_BROWSER_ENGINE=firefox-system`（链路 `firefox-system,edge,chrome`）；`MEDIACRAWLER_SKIP_QRCODE_DISPLAY=1`；`MEDIACRAWLER_LOGIN_SETTLE/REDIRECT_SECONDS=2`；`RISK_CIRCUIT_BREAKER=true`；`RISK_STAGGER_ENABLED=true`（15-30s）；`RISK_CURL_CFFI=true`；`RISK_EVIDENCE_SCREENSHOT=true`；`RISK_BROWSER_ROUTE=patchright`；`RISK_PROXY_ENABLED=false`；`RISK_NOPECHA_ENABLED=false`（`NOPECHA_API_KEY` 空）；`EVIL0CTAL_API_BASE_URL` 已配（值脱敏）。
  - 数据库 `data\radar.sqlite3`：videos/accounts/account_tasks/douyin_creator/douyin_aweme/runtime_settings 等表在库。
  - 前端唯一入口：`http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/`。
- **测试基线**：pytest 281 collected（279 passed + 2 skipped，0 failed）。

---

## 5. 未完成事项（全量逐条）

| # | 事项 | 阻塞原因 | 前置条件 | 优先级 | 完成标准 |
|:-:|------|---------|---------|:--:|---------|
| 1 | **10 轮验收测试重跑** | 并发模式被抖音"新 profile 首次环境验证"阻断（要求扫码）；串行重跑被用户中途终止 | 串行（CONCURRENT=1）、Firefox 引擎已登录一次 | 🔴 最高 | 每轮随机 10 账号×20 视频，成功率达标、零封锁；脚本已删需按 0816 日志 §7 重写 |
| 2 | **抖音号→sec_uid 自动解析** | 缺 creator_url 账号只能跳过 | fork search hook（USER 频道搜索）+ 后端三层缓存回填 | 🔴 高 | 所有账号自动解析，无手动补映射 |
| 3 | **字幕直取 Phase 0 实测** | 覆盖率未验证 | 风控解除后 fork client 有界采样 300 条 detail | 🟠 中 | video.subtitles 存在率 ≥20% 才投产 |
| 4 | **字幕直取灰度** | `SUBTITLE_DIRECT_ENABLED` 默认关 | Phase 0 达标 | 🟠 中 | 开 20%→50%→100%，每级 3 天无回归 |
| 5 | **12 账号逐账号真实采集验收** | 新增 11 个 sec_user_id 映射未逐个实测 | 各账号登录态就绪 | 🟠 中 | 每账号一次真实采集成功入库 |
| 6 | **NopeCHA API Key 配置** | Key 为空，守卫未生效 | 用户提供 Key | 🟠 中 | 填 Key 后验证码链路生效 |
| 7 | **代理 HTTPS 隧道缺失** | 正效果待 HTTPS 代理源 | 配置 `RISK_PROXY_POOL_URL` | 🟡 一般 | 代理预检+轮换真实生效 |
| 8 | **探针总预算 deadline** | 未设硬预算（最坏 ~40s+） | — | 🟡 一般 | 探针总耗时设 deadline |
| 9 | **爆款评分基准线校准** | 各账号 S/A/B/C 基准线未校准 | 采集数据积累 | 🟡 一般 | 13 账号各有基准线数值 |
| 10 | **飞书同步/爆款评分/口播分析** | 下一阶段功能，前端导航已禁用 | 采集与评分就绪 | 🟡 一般 | 前端导航启用 |

> ❓ **待人工确认**：① APP 签名（X-Gorgon）字幕直取是否立项；② NopeCHA Key / 代理源是否提供；③ 是否仍维持"个人使用无红线"定版。

---

## 6. 下一步行动计划（命令级）

**第一步（立即）：验证服务能起 + 跑基线测试**

```powershell
cd D:\全自动爬取短视频、推文爆款程序

# 1. 启动全部服务（后端 8000 / GPU ASR 8765 / 妙搭 3100+3000 / 浏览器引擎）
.\start.ps1

# 2. 确认三个健康端点
#   浏览器打开 http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/   （前端）
#   浏览器打开 http://127.0.0.1:8000/api/health                                    （后端）
#   浏览器打开 http://127.0.0.1:8000/api/risk-control/health                       （风控开关）

# 3. 跑全量回归（期望 281 collected = 279 passed + 2 skipped）
.venv\Scripts\python.exe -m pytest -q
```

**第二步（立即）：Firefox 引擎首次登录**

```powershell
# 首次需手动打开 Firefox 扫码一次（登录态持久化到 data\browser_data\ff_dy_user_data_dir）
# start.ps1 启动后按提示打开对应 Firefox 窗口扫码；之后自动采集免扫码
```

**第三步（最高优先）：重跑 10 轮验收测试（串行）**

```powershell
# 1. 确认串行模式
#    .env.local 中 MEDIACRAWLER_CONCURRENT_ACCOUNTS=1（当前已是）

# 2. 按 0816 日志 §7 重写验收测试脚本（测试脚本此前已删）：
#    每轮：随机 10 账号 × 20 视频 → 采集 → 统计账号级成功率与平均耗时 → 复盘 → 抹数据 → 下一轮
#    轮间冷却 30s，单轮上限 90 分钟

# 3. 抹数据用 SQL（videos 等 9 表 + douyin_aweme 2 表），注意先备份 data\radar.sqlite3
```

**第四步（随后）：sec_uid 自动解析 + 字幕直取 Phase 0**

```powershell
# sec_uid 解析：按架构 Agent 方案，fork search hook（USER 频道搜索）+ 后端三层缓存回填
# Phase 0：有界采样 300 条 detail 统计 video.subtitles 存在率（≥20% 才投产）
# 开关：.env.local 设 SUBTITLE_DIRECT_ENABLED=true（当前默认关）
```

**验证"续上了"的现象**：`start.ps1` 输出 `Started: NEW frontend ... local collector http://127.0.0.1:8000/api/health`；前端页面能打开；`/api/risk-control/health` 返回 `CIRCUIT_BREAKER=true / CURL_CFFI=true / STAGGER=true / EVIDENCE_SCREENSHOT=true / PROXY=false / NOPECHA=false / BROWSER_ROUTE=patchright`；pytest 全绿。

---

## 7. 环境与配置依赖（完整清单）

| 项 | 值 / 位置 |
|----|----------|
| 操作系统 | Windows 11 Pro（PowerShell 5.1，脚本注意 GBK/ASCII 编码坑） |
| Python 后端 venv | `D:\全自动爬取短视频、推文爆款程序\.venv\` |
| MediaCrawler venv | `D:\全自动爬取短视频、推文爆款程序\MediaCrawler\.venv\` |
| pyvideotrans venv | `D:\全自动爬取短视频、推文爆款程序\pyvideotrans\.venv-stt\`（**Python 3.10.19**，STT-only，model=small，CPU int8） |
| GPU ASR venv | `D:\全自动爬取短视频、推文爆款程序\runtime\.venv-asr\`（uvicorn app:app :8765） |
| 前端 | Node/npm，`deployments\miaoda-matrix-radar\`（dev:server 3100 + dev:client 3000） |
| 浏览器引擎 | Firefox system 默认（链路 firefox-system,edge,chrome），首次手动扫码 |
| ASR 模型 | `Systran/faster-whisper-small`；pyvideotrans `small`（`tiny` 仅烟测） |
| 依赖关键库 | curl_cffi 0.16.0、mss 10.2.0、patchright（driver 已装）、uv、pyvideotrans 官方 cli |
| 端口 | 8000（后端）、8765（GPU ASR）、9222（Edge CDP，Firefox 模式不启动）、3100/3000（妙搭） |
| 配置/密钥 | 全在 `.env.local`；**`SPIDERHUBS_API_KEY`/`MIAODA_API_KEY`/`SYNC_TOKEN`/`SITES_BYPASS_TOKEN`/`EVIL0CTAL_API_BASE_URL`/`NOPECHA_API_KEY` 值已脱敏**，绝不外发 |
| 云端 | 妙搭应用 `app_17bkk0a8pt8`（`https://ncn5iae3ocvu.feishuapp.com/app/app_17bkk0a8pt8`）；同步接口仅授权 API Key |

> ⚠️ **start.ps1 编码坑**：PowerShell 5.1 按 GBK 解析无 BOM UTF-8，脚本内中文注释有乱码风险，新加逻辑建议纯 ASCII。

---

## 8. 数据与状态快照

- **主库** `data\radar.sqlite3`（含 -shm/-wal）：videos（含 media_url/media_kind 列）、accounts、account_tasks、douyin_creator、douyin_aweme（2 表）、runtime_settings（last_clone / 黑名单）。另 `data\matrix_radar.db`。
- **登录态目录** `data\browser_data\`：Firefox `ff_dy_user_data_dir`（当前引擎）、Edge `cdp_dy_user_data_dir`（Edge 模式用）；目录已迁 D 盘（原 C 盘旧路径已删）。
- **临时媒体** `data\temp_media\job-<job-id>`：采集下载的临时视频/WAV/SRT，转录提交 SQLite 后自动删除；失败材料保留 24h 供诊断。
- **待清理**：项目根有大量历史 `_*.py` 诊断脚本（如 `_round10.py`、`_diag*.py`、`_check_*.py` 等，属上次调试遗留），确认无用后可清；`backend_backup_20260806_phase1`、`backups/`、`runtime/backups/` 为备份可酌情归档。
- **保留的中间产物**：GPU ASR 模型目录（长期保留）；`.playwright-browsers`（Playwright 回退浏览器）。

---

## 9. 关键决策与踩坑记录

| 决策/踩坑 | 根因 | 规避方案 |
|----------|------|---------|
| **并发免登录被平台阻断** | 抖音识别新 profile Edge 为新设备，克隆 Cookie 不保证免验证，要求扫码 | 回退串行（CONCURRENT=1，共享登录态免扫码）；已定版 **Firefox 默认引擎**（登录态持久不反复重登） |
| **Edge 一次登录选型** | 多账号每账号独立 Edge 都要重登 | 不加装 CookieCloud，本地 B++++ 方案：克隆原子化 + robocopy 自动刷新 + 三级登录态探测（25/25 成功） |
| **字幕直取不可行** | 抖音 web 端 detail 接口/播放器/分享页均无字幕数据源 | 走"下载 + GPU ASR"，已闭环 149/150 达标；APP 签名（X-Gorgon）待拍板 |
| **图文笔记假成功** | aweme_type 163/2 无音频，硬转录把 BGM 歌词当口播稿 | 只采数据不转录（宁可真跳过，不要假成功） |
| **多账号 % 格式化崩溃** | 8 处 `USER_DATA_DIR % config.PLATFORM` 注入绝对路径必崩（TypeError） | 统一 isabs 守卫（绝对路径跳过格式化） |
| **探针异常逃逸** | probe_via_cffi 调用 curl_cffi_fetch 无 try，3 次退避耗尽抛 OSError 中断下载链 | try/except → return None 回退 urlopen + 回归测试（test_quick_media_probe_cffi_exception_falls_back） |
| **429 误杀直链** | _classify_probe 把 429（瞬态限流）归 html 确定性失败 | 429/5xx → unknown 保守放行 |
| **信号标记口径分叉** | 两份风控信号标记表重复定义且漂移 | 单一来源 RISK_SIGNAL_MARKERS + `is` 同一对象断言 |
| **start.ps1 中文乱码** | PowerShell 5.1 按 GBK 解析无 BOM UTF-8 | 新加逻辑纯 ASCII（守卫段已改） |
| **旧前端/端口冲突** | 旧 vinext 前端 780M 与 3000 端口隐患 | 物理删除 + start.ps1 守卫（重现自动清除 + 非妙搭进程清退） |
| **对抗组件取舍** | 付费/无法稳定投产组件 | 删除 NopeCHA（无 Key）/代理池运行时/nodriver/Botright/haipproxy 释放硬盘；保留全部免费实测可用组件 |

---

## 10. 风险与待确认项

- ❓ **账号风控/法律风险**：2026-08-16 用户定版"个人使用无红线"，对抗组件（patchright/curl_cffi/截图）已投产且十轮零封锁；但自动化高频行为仍可能加速账号风控升级——持续监控熔断器与 blocked/argus 信号，必要时回退开关。
- ❓ **NopeCHA Key**：当前为空，验证码求解链路实际未生效（守卫要求 key 非空）；F1 施工后需代码总监复审。
- ❓ **代理 HTTPS 隧道缺失**：`RISK_PROXY_ENABLED=false`，代理正效果未验证。
- ❓ **APP 签名（X-Gorgon）字幕直取**：web 无源，签名方案是否立项待用户拍板。
- ❓ **12 账号逐账号真实采集验收**：新增 11 个 sec_user_id 映射未全部实测。
- ❓ **后端 8000 端口实例来源**：偶现 Anaconda python 实例在跑（功能一致但解释器来源需排查时注意）。
- ⚠️ **合规**：MediaCrawler 上游许可证限定非商业学习用途，正式商业运营前需确认许可或替换采集适配器。

---

## 11. 续作启动手册

1. **读文档**：先读知识库 [[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0816-多账号并发与Edge登录态#8. 交接清单：未完成事项]] → 再读 [[总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/开发日志/0817-速度优化批与云端修复]]。
2. **起服务**：`cd D:\全自动爬取短视频、推文爆款程序 && .\start.ps1`（首次安装用 `.\start.ps1 -Install`）。
3. **验证续上**：前端 `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/` 可开；`http://127.0.0.1:8000/api/health` 返回 ok；`http://127.0.0.1:8000/api/risk-control/health` 开关符合预期；`.venv\Scripts\python.exe -m pytest -q` 281 collected 全绿。
4. **首次扫码**：Firefox 引擎首次需手动打开对应窗口扫一次抖音二维码，登录态持久化后自动采集免扫码。
5. **进入开发**：按 §6 顺序推进（10 轮验收测试 → sec_uid 解析 → 字幕直取 Phase 0/灰度 → 12 账号逐个验收）。
6. **回滚要点**：所有对抗开关 `.env.local` 显式开启、默认关闭行为与改造前一致；`runtime/backups/` 与 `backend_backup_20260806_phase1` 可回滚。
