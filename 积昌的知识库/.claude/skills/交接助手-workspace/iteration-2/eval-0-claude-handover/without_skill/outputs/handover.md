---
项目名: 矩阵内容雷达（全自动爬取短视频、推文爆款程序）
交接对象: Claude Code（智能体）
交接日期: 2026-08-17
前作者: DeepSeek（此前由 DeepSeek 迭代，现转入 Claude Code 续作）
---

# 矩阵内容雷达 — 交接文档（给 Claude Code 版）

> [!summary] 一句话定位
> 本地部署的短视频/推文爆款采集分析系统：基于开源 MediaCrawler 抓取抖音数据，按 S/A/B/C 四档自动识别"爆款"，服务 12 个自有矩阵账号（七哥组 5 / 鱼哥组 3 / 华哥组 5 / 外部对标 2）的内容选题与竞品分析；采集结果经妙搭云端展示，飞书为唯一对外出口。

> [!note] 本项目由 DeepSeek 主导开发至 2026-08-17，现整体移交 Claude Code 继续。**所有路径、命令、状态均为我在沙箱环境中逐条核实过的真实信息**（能核实的已核实；个别需在本机复核的标了 ❓）。

---

## 0. 交接摘要（启动包）

- **项目做什么**：本地抓取抖音短视频数据 → S/A/B/C 爆款评分 → 生成口播稿 → 同步妙搭云端，供矩阵账号选爆款选题。
- **当前进度**：核心采集/转录/风控/多账号并发/前端已全部落地；最近一天（0817）完成速度专项优化、Edge 窗口卫生、云端 BUG 修复。**处于"上线前验收"阶段**——10 轮批量验收测试尚未跑完（曾因抖音新环境验证阻断，改串行重跑被用户中途终止）。
- **最关键三件事**：
  1. 已完成：采集-转录-评分-云端全链路 100% 正确率（修正口径），风控组件投产，多账号并发池落地；
  2. 卡在哪：10 轮验收测试没跑完；抖音号→sec_uid 自动解析未做（缺 creator_url 账号只能跳过）；字幕直取 web 端无数据源（已改走 GPU ASR，闭环 149/150 达标）；
  3. 下一步第一件事：**串行模式（`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`）重跑 10 轮验收测试**，按 0816 开发日志 §7 重写测试脚本（原脚本已删）。
- **从哪继续最省力**：先读 `D:\全自动爬取短视频、推文爆款程序\README.md` + 本知识库开发日志 `0816-多账号并发与Edge登录态.md` 的「§8 交接清单：未完成事项」，然后跑 `.\start.ps1` 拉起整套服务。

---

## 1. 项目总览与验收标准

### 一句话定位与最终目标

矩阵内容雷达 = "低成本抖音爆款数据工作台"。最终目标：**每天自动采集 12 个矩阵账号的新作品 → 打 S/A/B/C 分 → 生成口播稿 → 同步妙搭云端，运营人员打开网页即可看爆款并复用选题**。

### 验收标准（做到什么程度算完成）

| 验收项 | 判定标准 | 当前状态 |
|---|---|---|
| 批量采集正确率 | 20 条/轮 ≥ 95% | ✅ 100%（10 轮 200/200，修正口径） |
| 口播稿正确率 | 可转录视频 ≥ 95% | ✅ 100%（第 6-10 轮连续 5 轮全绿） |
| 单轮耗时 | 20 条含口播稿 ≤ 4 分钟 | ✅ 2.3~2.5 分钟（约 7 秒/条） |
| 风控稳定性 | 10 轮零账号封锁 | ✅ 十轮实测 argus/429/403 全被消化，blocked=0 |
| **10 轮验收测试** | 每轮随机 10 账号 × 20 视频，统计成功率与耗时 | ❌ **未跑完**（见 §5） |
| 回归测试 | `pytest` 全绿 | ✅ 279 passed / 2 skipped（0816 终审口径） |

---

## 2. 文件地图（精确路径）

> 唯一正式工作目录（README 明确）：`D:\全自动爬取短视频、推文爆款程序`
> ⚠️ 知识库文档中有个别旧条目写 `E:\`，但 0815-0817 开发日志已统一为 **D:\**；**以 D:\ 为准**（见 §10 ❓1）。

### 入口层（启动 / 配置 / 仓库说明）

| 路径 | 作用 | 状态 |
|---|---|---|
| `D:\全自动爬取短视频、推文爆款程序\start.ps1` | **唯一启动入口**。拉起 backend(:8000) / GPU ASR(:8765) / 妙搭 dev:server(:3100) / dev:client(:3000) / Edge或Firefox 登录态；`-Install` 做首次全量安装 | 主入口 |
| `D:\全自动爬取短视频、推文爆款程序\README.md` | 项目总览、日常使用、当前限制（必读） | 已完成 |
| `D:\全自动爬取短视频、推文爆款程序\.env.local` | **全部运行时配置**（密钥只在这里，勿外发/勿提交） | 生产在用 |
| `D:\全自动爬取短视频、推文爆款程序\.env.example` | 配置模板 | 参考 |
| `D:\全自动爬取短视频、推文爆款程序\pytest.ini` | pytest 配置 | 在用 |
| `D:\全自动爬取短视频、推文爆款程序\CLAUDE.md` | **不存在**（建议补建，见 §12） | ❌ 待建 |

### 后端层（FastAPI，端口 127.0.0.1:8000）

| 路径 | 作用 | 状态 |
|---|---|---|
| `backend\app\main.py` | FastAPI 入口 `/api/health`、`/api/risk-control/health` | 已完成 |
| `backend\app\config.py` | 全量配置（含 `COLLECTION_TRANSCRIPT_WORKERS`、`RISK_*`、`MEDIACRAWLER_*`） | 0817 改动 |
| `backend\app\db.py` | SQLite 数据层（`data\radar.sqlite3`；videos 表加 media_url 列 + 迁移） | 0817 改动 |
| `backend\app\risk_control.py` | 风控适配层：熔断器 / curl_cffi / 随机错峰 / 代理预检 / 证据截图 | 已投产 |
| `backend\app\services\collection.py` | 采集主逻辑（账号循环、转录组装、批线程流水线） | 0817 改动 |
| `backend\app\services\sync.py` | 妙搭云端同步（runtime_settings 黑名单持久化） | 0817 改动 |
| `backend\app\services\multi_account\` | 多账号并发池：`browser_profiles.py`(端口分配) / `global_limiter.py`(漏桶) / `retry.py`(指数退避) / `account_pool.py`(线程池) / `wal_queue.py`(串行写) / `runner.py`(调度) | 已落地 |
| `backend\app\services\multi_account\edge_cleanup.py` | **Edge/Firefox 窗口卫生**（任务结束杀干净，三层清理） | 0817 新增 |
| `backend\app\services\asr_service.py` | GPU ASR 服务客户端 | 已完成 |
| `backend\app\services\transcript_router.py` | 口播稿线路路由（下载+ASR；字幕直取第 0 顺位，默认关） | 已完成 |
| `backend\app\services\platform_subtitles.py` / `douyin_subtitles.py` | 字幕直取插件（web 端已判定无数据源） | 保留待灰度 |
| `backend\app\providers\mediacrawler.py` | MediaCrawler 子进程封装（环境透传、代理预检、`_read_changed` 读 aweme_type、save_creator 落库） | 已完成 |
| `backend\tests\` | **28 个测试文件**（test_risk_control / test_multi_account / test_plugin_routes 等） | 279 passed |

### 采集内核（MediaCrawler fork，含独立 venv）

| 路径 | 作用 | 状态 |
|---|---|---|
| `MediaCrawler\` | 上游 fork（三模式：detail/creator/search） | 已 fork |
| `MediaCrawler\main.py` | 采集命令行入口 | fork 4 处 env 注入 |
| `MediaCrawler\login.py` | 登录（qrcode），`MEDIACRAWLER_LOGIN_SETTLE/REDIRECT_SECONDS` env 化 | 0817 改动 |
| `MediaCrawler\crawler_util.py` | `MEDIACRAWLER_SKIP_QRCODE_DISPLAY` 二维码弹图开关 | 0817 改动 |
| `MediaCrawler\risk_browser_shim.py` | 风控浏览器垫片（patchright 路由） | 已投产 |
| `MediaCrawler\.venv` | fork 专用 Python 环境 | 在用 |

### 转录/ASR 层

| 路径 | 作用 | 状态 |
|---|---|---|
| `pyvideotrans\` + `pyvideotrans\.venv-stt`（Python 3.10 CPU/STT-only） | 口播稿 STT 官方 `cli.py --task stt`；`small` 模型（int8, beam1） | 已完成 |
| `runtime\asr-service\app.py` + `runtime\.venv-asr` | **GPU ASR 服务（:8765）**，对应知识库所称 `_asr_8765.py`；VAD 静音过滤 + 同步 endpoint + 240s 超时 | 0817 改动 |
| `_asr_8765.py`（项目根） | GPU ASR 相关辅助脚本 | 0817 改动 |

### 前端层（妙搭为唯一前端）

| 路径 | 作用 | 状态 |
|---|---|---|
| `deployments\miaoda-matrix-radar\` | 妙搭应用仓库（dev:server :3100 / dev:client :3000） | 唯一前端 |
| `deployments\miaoda-matrix-radar\src\...\radar-selection.ts` | 云端 BUG 修复处（初始化优先级 URL>当前选择>全选；达人 ID 大小写不敏感） | 0817 已部署 |
| 访问入口 | `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/` | 本地 |
| 公网站点 | `https://ncn5iae3ocvu.feishuapp.com/app/app_17bkk0a8pt8` | 云端 |

### 数据/日志/资源

| 路径 | 作用 |
|---|---|
| `data\radar.sqlite3` | 主业务库（videos / account_tasks / runtime_settings 等 9 表） |
| `data\browser_data\` | 登录态目录（`ff_dy_user_data_dir` 为 Firefox 共享登录态；`cdp_dy_user_data_dir` 为 Edge CDP） |
| `data\temp_media\job-<job-id>\` | 受控临时媒体工作区（下载视频/WAV/SRT，成功后即删） |
| `logs\` | `backend.out.log` / `backend.err.log` / `asr-service.out.log` / `miaoda-*.log` |
| `backups\` | 测试轮次备份（`backups\radar_r{1-9}_*.sqlite3`） |
| `runtime\plugins\` | 插件清单（deployment-manifest.json）与支持插件 |
| `scripts\` | `clone-browser-profiles.ps1`、`install-support-plugins.ps1` 等 |

---

## 3. 已完成工作（全量逐条）

> 时间线由新到旧。每个条目标注"产出物路径 + 验证方式"。

### 2026-08-17（最近一天）
1. **速度专项优化**（详见 `开发日志\0817-速度优化批与云端修复.md`）：
   - 转录工作线 4→6（`config.py` `COLLECTION_TRANSCRIPT_WORKERS`，env 可配）→ 口播稿并行度 +50%
   - 错峰收窄 20-60s→15-30s（`.env.local` `RISK_STAGGER_MIN/MAX_SECONDS`）→ 整轮省 ~2.5 分钟
   - 采集-转录流水线化（`collection.py` 批线程，batch=工作线数）→ 单账号 542s→~480s
   - 转录异步修复（`_asr_8765.py` 同步 endpoint + 超时 240s）→ 消除 timed out
   - VAD 静音过滤（`_asr_8765.py` vad_filter）→ 长视频转录提速 30-50%
   - media_url 落库（`db.py` videos 表加列 + 迁移）→ 转录下载走官方直链
   - 主页资料并入采集进程（`save_creator` 落库 douyin_creator + backend `prefer_mc_db`）→ 每账号省 ~20s
   - 登录固定等待 env 化（`login.py` `MEDIACRAWLER_LOGIN_SETTLE/REDIRECT_SECONDS`）→ 每账号省 ~7s
   - 云端同步黑名单降噪（`sync.py` runtime_settings 持久化）→ 消除每轮 150 条无效重试
   - 二维码弹图根治（`crawler_util.py` `MEDIACRAWLER_SKIP_QRCODE_DISPLAY`）→ 自动化不再弹图
2. **Edge 窗口卫生**（`backend\app\services\multi_account\edge_cleanup.py`）：账号级/hook级/任务级三层清理；唯一保留边界 = cmdline 无项目目录的用户日常 Edge。
3. **云端 BUG 修复**（`radar-selection.ts`）：账号页查看视频固定指向同一达人 → 初始化优先级 URL>当前选择>全选兜底 + 达人 ID 大小写不敏感；已构建部署妙搭（commit b0aff55）；前端 12 测试通过、tsc 零错误；云端补建 28 个对标账号映射。

### 2026-08-16（多账号并发 + 对抗组件定版）
4. **多账号并发池落地**（`services\multi_account\` 6 模块）：账号级受控并发（独立 CDP 端口/登录态目录/采集库）；默认 `MEDIACRAWLER_CONCURRENT_ACCOUNTS=1` 串行零变化；5 次测试全过、全量回归 264 passed。
5. **图文笔记识别**（`aweme_type=163/2` → `media_kind=image_text`）：图文只采数据不生成口播稿，杜绝 BGM 歌词假成功。
6. **字幕直取插件**（A+C 整合，代码总监 56/70 终审）：fork 4 文件 + backend 5 处；`SUBTITLE_DIRECT_ENABLED` 默认关（未灰度）。
7. **前端切换**：删除旧 vinext 前端（780M），妙搭为唯一前端。
8. **Edge 一次登录**（B++++ 62/70 定稿）：克隆原子化（staging→.trash→切换→回滚）+ robocopy 自动刷新 + 三级登录态探测；25/25 账号目录克隆成功。
9. **对抗组件定版**（用户 2026-08-16 决策：突破红线、风险自担）：保留投产熔断器/随机错峰/全局限速/指数退避/curl_cffi/mss 截图/patchright/CloakBrowser/fingerprintjs；删除 NopeCHA（无 Key）/代理池（缺 HTTPS 源）/nodriver/Botright/haipproxy；十轮测试零账号封锁。
10. **十轮风控测试终审**（0815-16）：成功率 76%→100%（+24pct）；argus 稳定 1~2 次/轮零封锁。

### 2026-08-15 及以前
11. **10 轮批量化测试**（`0815-项目测试.md`）：视频采集 200/200（100%）、修正口径口播稿第 6-10 轮 100%、平均 3.9 分钟/轮（提速 ~8 倍）；修复转录 420s 长尾、Evil0ctal 未启动、图文笔记假成功。
12. **风控组件接入生产**（`0815-风控组件接入生产.md`）：新建 `risk_control.py`、config `RISK_*`、`/api/risk-control/health`；248→279 tests。
13. **真实闭环验证**（0810 前，见 `README.md`）："科研华哥"最近 7 天导入同步 9 条作品；补齐 12 账号 `sec_user_id` 映射；口播转录恢复 pyvideotrans 官方 CLI（Python 3.10 `.venv-stt`）。

---

## 4. 当前精确进度

- **最后一批有效改动**：2026-08-17 速度优化批 + Edge 窗口卫生 + 云端 `radar-selection.ts` BUG 修复（妙搭已部署 commit b0aff55）。
- **当前运行配置**（`.env.local` 已核实）：
  - `MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`（**串行**，多账号并发代码就绪但未启用）
  - `MEDIACRAWLER_BROWSER_ENGINE=firefox-system`（**Firefox 为默认引擎**，登录态落 `data\browser_data\ff_dy_user_data_dir`，首次需人工扫码一次）
  - `TRANSCRIPTION_ENABLED=true`；`ASR_SERVICE_BASE_URL=http://127.0.0.1:8765`；`EVIL0CTAL_API_BASE_URL=http://127.0.0.1:18081`
  - `RISK_STAGGER_MIN/MAX_SECONDS=15/30`；`RISK_BROWSER_ROUTE=patchright`；`RISK_NOPECHA_ENABLED=false`；`RISK_PROXY_ENABLED=false`
- **代码状态**：可直接 `.\start.ps1` 启动；后端 279 测试全绿；前端 12 测试通过 + tsc 零错误。
- **测试脚本缺口**：10 轮验收测试的临时脚本已被用户终止并删除（`0816-多账号并发与Edge登录态.md` §7），需按该节重写。

---

## 5. 未完成事项（全量逐条，按优先级）

| # | 事项 | 阻塞原因 | 前置条件 | 优先级 | 做到什么程度算完成 |
|:-:|------|---------|---------|:---:|------|
| 1 | **10 轮验收测试重跑** | 并发模式被抖音"新环境验证"阻断（克隆 Cookie 不保证免验证）；串行重跑被用户中途终止 | 测试脚本按 0816 日志 §7 重写 | 🔴 紧急 | 每轮随机 10 账号 × 20 视频，串行模式，统计成功率与耗时；10 轮完成且有总结 |
| 2 | **抖音号→sec_uid 自动解析** | 缺 creator_url 账号目前只能跳过（13 个矩阵账号中有缺链接者） | 方案见 `0815-多账号采集与缺链接报错修复.md` §5（fork search hook + 后端三层缓存回填） | 🟠 重要 | 任务启动前自动补齐 sec_uid，无账号再被跳过 |
| 3 | **字幕直取 Phase 0 实测** | web 端已判定无字幕数据源；APP 签名（X-Gorgon）方案待用户拍板 | 用户确认是否走 X-Gorgon 直取（中等工程） | 🟠 重要 | 有界采样统计 video.subtitles 存在率 ≥20% 才投产 |
| 4 | **字幕直取灰度** | `SUBTITLE_DIRECT_ENABLED` 默认关，未灰度 | 先完成 #3 | 🟡 一般 | 20%→50%→100% 三级灰度，每级 3 天 |
| 5 | **多账号并发登录态现实路径** | 克隆 Cookie 对全新 Edge 环境无效（平台策略） | 用户决策：串行验收 or 每账号首登扫码一次 | 🟡 一般 | 选定方案并验证多账号并发可长期免扫码 |
| 6 | **clone 脚本自动刷新验证** | start.ps1 mtime 比对已实施但未实测 | 一次真实"共享重登→启动→自动克隆"场景 | 🟡 一般 | 实测通过 |
| 7 | **NopeCHA Key 未配** | 付费、无 Key；已被用户删除（卸载+wheel 删除+开关 false） | 用户购买/提供 Key | 🟡 一般 | 接入后验证码自动求解链路通 |
| 8 | **patchright 浏览器内核下载** | 接线完成待下载内核 | 下载内核后验证无检测启动 | 🟡 一般 | `RISK_BROWSER_ROUTE=patchright` 实际采集通过 |
| 9 | **代理 HTTPS 隧道缺失** | 无 HTTPS 代理源，正效果待验证 | 优质 HTTPS 代理源 | ⚪ 待触发 | 代理预检真实转发而非回退直连 |
| 10 | **探针总预算 deadline 未设 / 熔断器故障演练** | 仅单测覆盖，未注入式演练 | — | ⚪ 可选 | 设探针总预算；做一次注入式熔断演练 |
| 11 | **飞书同步、爆款评分、口播分析（下一阶段）** | README 明示当前导航已禁用 | 属于后续产品阶段 | ⏳ 后续 | 需求明确后单独立项 |

---

## 6. 下一步行动计划（命令级）

> 以下命令全部在 `D:\全自动爬取短视频、推文爆款程序` 目录下以 PowerShell 执行。**先做 1，再做 2、3。**

### 立即做（P0）

1. **启动整套服务并验证健康**
   ```powershell
   cd D:\全自动爬取短视频、推文爆款程序
   .\start.ps1
   ```
   - 成功信号：终端打印 `Started: NEW frontend http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/   local collector http://127.0.0.1:8000/api/health`
   - 验证：
     ```powershell
     (Invoke-WebRequest http://127.0.0.1:8000/api/health).StatusCode          # 期望 200
     (Invoke-WebRequest http://127.0.0.1:8000/api/risk-control/health).Content # 查看风控开关
     Get-NetTCPConnection -LocalPort 8765,8000,3100,3000 -State Listen        # 四端口都在监听
     ```

2. **跑回归测试确认基线**
   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q
   ```
   - 成功信号：`279 passed, 2 skipped`（0816 终审基线）；如有失败先修到全绿再动手。

3. **重写并执行 10 轮验收测试（串行）**
   - 依据 `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\开发日志\0816-多账号并发与Edge登录态.md` §7 重写测试脚本（原脚本已删）。
   - 规则：`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1`（串行，免扫码）；每轮随机 10 账号 × 20 视频；每轮开始前清数据（**先备份**）；轮间冷却 30s；90 分钟/轮上限。
   - 清数据 SQL（每次先备份 `backups/`）：
     ```sql
     -- 业务库 9 表（data\radar.sqlite3）
     DELETE FROM videos; DELETE FROM account_tasks; DELETE FROM collection_job_items;
     DELETE FROM collection_logs; DELETE FROM error_logs; DELETE FROM transcription_results;
     DELETE FROM runtime_settings; DELETE FROM douyin_creator; DELETE FROM transcript_jobs;
     -- MediaCrawler 2 表（MediaCrawler\data\ 采集库）
     DELETE FROM douyin_aweme; DELETE FROM douyin_aweme_detail;
     ```
   - 成功信号：10 轮全部 `completed`，采集成功率与口播稿正确率均 ≥95%，且记录耗时。

### 之后做（P1）

4. **抖音号→sec_uid 自动解析**：按 `0815-多账号采集与缺链接报错修复.md` §5 方案实现（fork search hook + 三层缓存回填），验证"无 creator_url 账号不再被跳过"。
5. **字幕直取 Phase 0**：先向用户确认是否投入 X-Gorgon（APP 签名）中等工程；若做，按 `0816` 日志 §3 的 A+C 方案实现并做覆盖率采样。
6. **补建 `CLAUDE.md`**：在项目根目录写一份 CLAUDE.md（见 §12 模板），把启动命令、测试命令、环境约束固化。

---

## 7. 环境与配置依赖（完整清单）

| 项 | 值/位置 |
|---|---|
| 操作系统 | Windows（PowerShell 5.1 注意：无 BOM UTF-8 脚本的中文注释会被 GBK 误读 → 新脚本建议纯 ASCII） |
| 后端 Python | `D:\全自动爬取短视频、推文爆款程序\.venv\Scripts\python.exe`（3.12） |
| MediaCrawler Python | `D:\全自动爬取短视频、推文爆款程序\MediaCrawler\.venv\Scripts\python.exe` |
| STT Python | `D:\全自动爬取短视频、推文爆款程序\pyvideotrans\.venv-stt`（Python 3.10.19，CPU/STT-only，`small` 模型） |
| GPU ASR Python | `D:\全自动爬取短视频、推文爆款程序\runtime\.venv-asr`（服务 :8765） |
| 端口 | 8000 backend / 8765 ASR / 3100 妙搭 server / 3000 妙搭 client / 18081 Evil0ctal（转录兜底）/ 9222 Edge CDP（Edge 引擎时） |
| 数据库 | `data\radar.sqlite3`（业务） + `MediaCrawler\data\`（采集库） |
| 浏览器 | 默认 **Firefox**（`MEDIACRAWLER_BROWSER_ENGINE=firefox-system`）；Edge 引擎为备选 |
| 密钥/token | 仅存于 `.env.local`（值已脱敏，**绝不外发/不提交**）：`SPIDERHUBS_API_KEY` / `MIAODA_API_KEY` / `SYNC_TOKEN` / `SITES_BYPASS_TOKEN` / `NOPECHA_API_KEY`(空) |
| 未安装/待配 | NopeCHA Key（空）、patchright 浏览器内核（待下载）、HTTPS 代理源（缺） |

---

## 8. 数据与状态快照

- **数据量**：12 个账号已完成 sec_user_id 映射；对标账号云端已补 28 个；单轮 20 条视频样本已多次跑通。
- **备份**：`backups\radar_r{1-9}_*.sqlite3` 保留各轮测试备份；轮次结果在 `logs\round_results.jsonl`。
- **临时数据**：`data\temp_media\job-<job-id>\` 受控临时区，成功即删、失败保留 24h 巡检清理；`_*.py` 根目录遗留大量一次性诊断脚本（DeepSeek 时代产物，可审后清理）。
- **需保留的中间产物**：MediaCrawler 各账号登录态目录（删除需重登）；`runtime\plugins\deployment-manifest.json`（插件状态）。

---

## 9. 关键决策与踩坑记录

| 决策/坑 | 内容 | 规避方案 |
|---|---|---|
| 合规红线变更 | 2026-08-16 用户决策：突破原红线，①类对抗组件全部投产，风险自担 | 保留熔断/错峰/退避/curl_cffi 等免费组件；付费/无法投产的已删除 |
| 抖音新环境验证 | 克隆 Cookie 对全新 Edge/新设备**不保证免验证**（平台策略，非 BUG） | 串行模式（共享登录态）可全自动免扫码；多账号并发需每账号首登扫码一次 |
| 图文笔记假成功 | `aweme_type=163` 无音频，硬转录会把 BGM 歌词当口播稿 | 识别 media_kind=image_text → 明确跳过并记日志；正确率按"可转录视频数"统计 |
| 转录 420s 长尾 | route2 下载三 provider 依次尝试最坏 420s+ | DownloadRouter 总预算 75s + 直链 HTML 快速预检 |
| start.ps1 中文乱码 | PowerShell 5.1 按 GBK 解析无 BOM UTF-8 | 新加逻辑纯 ASCII |
| backend 解释器混淆 | 8000 端口偶现 Anaconda python 实例 | 统一用 `.venv`；排查时先确认解释器来源 |
| web 端无字幕 | detail 接口无字幕字段/播放器无字幕请求/分享页无 videoInfoRes（多轮实测） | 口播稿走"下载 + GPU ASR"（149/150 达标）；APP 签名 X-Gorgon 待拍板 |
| 旧前端残留 | 若有人拷回旧 `frontend/` 会干扰 | start.ps1 启动时自动删除 + 3000 端口非妙搭进程自动清退 |
| % 格式化崩溃 | fork 8 处 `USER_DATA_DIR % config.PLATFORM` 注入绝对路径必崩 | 8 处统一 isabs 守卫（绝对路径跳过格式化） |

---

## 10. 风险与待确认项（❓）

> 接手后如遇以下不确定，先向用户确认，不要擅自决定。

- ❓1 **驱动器盘符**：本沙箱环境里知识库在 `F:\积昌的知识库 - 副本`，但正式环境配置写的是 `E:\积昌的知识库 - 副本`；项目代码当前确认在 `D:\全自动爬取短视频、推文爆款程序`。开工前请先确认知识库盘符（E: 还是 F:），避免读错笔记。
- ❓2 **用户是否要投入 X-Gorgon（APP 签名）字幕直取**：中等工程量，涉及平台对抗升级，需用户拍板。
- ❓3 **多账号并发是否要"每账号首次人工扫码一次"**：决定 #5 未完成事项的走向。
- ❓4 **NopeCHA / patchright / 代理源**是否继续投入（付费项）：默认保持禁用/不配，等用户指令。
- ❓5 **根目录大量 `_*.py` 一次性脚本**可否清理（需用户确认，见 CLAUDE.md 临时文件规则）。

---

## 11. 续作启动手册（从零恢复）

1. **确认环境**：
   ```powershell
   Test-Path 'D:\全自动爬取短视频、推文爆款程序\.venv\Scripts\python.exe'   # True 则环境在位
   ```
   若缺失：`cd D:\全自动爬取短视频、推文爆款程序; .\start.ps1 -Install`（首次全量安装，需 uv）。
2. **启动**：`.\start.ps1` → 见 §6 步骤 1 的验证信号。
3. **Firefox 首登**（默认引擎）：首次需手动打开 Firefox 用共享登录态目录扫码一次（`data\browser_data\ff_dy_user_data_dir`）。
4. **如何验证"续上了"**：
   - backend：`http://127.0.0.1:8000/api/health` 返回 200；
   - 风控开关：`/api/risk-control/health` 显示 `CIRCUIT_BREAKER=true / CURL_CFFI=true / STAGGER=true / PROXY=false / NOPECHA=false / BROWSER_ROUTE=patchright`；
   - ASR：`:8765` 端口在监听；
   - 回归：`pytest` 输出 `279 passed, 2 skipped`；
   - 真实采集：新建任务后 `logs\backend.out.log` 出现 `collection_job` 完成日志，`data\radar.sqlite3` 的 `videos` 表新增行。

---

## 12. 按 Claude Code 定制的附加内容

### 12.1 建议在项目根补建 `CLAUDE.md`（模板）

```markdown
# CLAUDE.md — 矩阵内容雷达

## 唯一工作目录
- 项目根：`D:\全自动爬取短视频、推文爆款程序`（README 明示唯一源目录）

## 常用命令（PowerShell）
- 启动：`.\start.ps1`
- 首次安装：`.\start.ps1 -Install`（需 uv）
- 后端回归：`.\.venv\Scripts\python.exe -m pytest -q`（基线 279 passed / 2 skipped）
- 健康检查：http://127.0.0.1:8000/api/health ；风控开关 /api/risk-control/health

## 硬约束
- 密钥只在 `.env.local`，绝不外发/不提交
- start.ps1 内新增逻辑保持纯 ASCII（PowerShell 5.1 GBK 会误读中文注释）
- 每次改动后跑 pytest 保持全绿；前端改动跑 dev:client 的 12 测试 + tsc
- 测试前先备份 `backups/`，清数据用 §6 步骤 3 的 SQL
- 图文笔记（aweme_type=163）只采数据不生成口播稿
```

### 12.2 子代理使用提示
- 本任务适合派生子代理并行：例如一个子代理跑 10 轮验收测试并采集指标，另一个子代理并行实现抖音号→sec_uid 解析（二者互不依赖）。
- 若做 X-Gorgon（APP 签名）等跨模块改动，可派"代码总监"式子代理做设计评审（与 DeepSeek 时代的做法一致）。

### 12.3 验证方法必须可跑
- 所有"下一步"都给了可执行命令与成功信号；遇到 pytest 红色或端口不通，先修基线再继续，不要带病开发。

---

> 📎 关联知识库文档（沙箱路径）：
> - 项目笔记目录：`F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\`
> - Wiki 总览：`F:\积昌的知识库 - 副本\自动维护知识库\wiki\自媒体运营\短视频爆款采集系统.md`
> - 必读交接清单：`...\开发日志\0816-多账号并发与Edge登录态.md` §8、`0817-速度优化批与云端修复.md`
