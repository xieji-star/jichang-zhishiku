# 矩阵内容雷达 交接文档（给 Claude Code 版）

> **项目名**：矩阵内容雷达（Matrix Content Radar）
> **交接对象**：Claude Code（模式 B，按智能体习性定制）
> **交接方向**：A（DeepSeek）→ B（Claude Code）
> **交接日期**：2026-08-17
> **项目唯一正式目录**：`D:\全自动爬取短视频、推文爆款程序`（Windows 11，PowerShell 环境）

---

## 0. 交接摘要（启动包）

本项目是一个**面向 12 个自有抖音账号的低成本数据工作台**：本地按需采集抖音视频 → SQLite 本地入库（视频元数据 + ASR 口播转写稿）→ 通过同步队列推送「妙搭」云端数据库 → 网页端（矩阵内容雷达）展示与导出 Excel。

**A（DeepSeek）已完成**：抖音视频采集、12 账号主页映射、ASR 口播转写、本地入库、云端同步、Excel 导出的基础链路全部打通，并有真实抖音作品验收记录（2026-08-06 起）。

**A 没做完的（接力棒，4 件）**：
1. 爆款评分模型层未落地（backend 中无评分代码，前端导航已禁用）
2. 采集任务未接全自动调度（后端仅有一个临时媒体清理的定时任务）
3. 10 轮真实批量验收未跑完（计划 10 轮，实际完成 6 轮，`is_final=False`）
4. 根目录尚无 git 基线（无 `.git`，`.gitignore` 已存在）

**B（Claude Code）下一步第一件事**：在项目根建 git 基线（`git init` + 初始 commit），并跑一次 `.\start.ps1` + `pytest` 确认环境还原成功。

**最省力的续作入口**：从 `backend/app/main.py` 的 `lifespan()`（第 250 行起，后台任务创建于 271 行）与 `backend/app/services/` 目录看起——新的评分模型与自动调度都围绕这两处扩展。

---

## 1. 项目总览与验收标准

### 一句话定位
为华哥组、七哥组、鱼哥组共 12 个自有抖音账号提供「本地采集 + 云端展示」的低成本数据工作台，产出爆款视频/口播素材的运营数据。

### 架构（可替换结构）
`本地按需采集（MediaCrawler）→ SQLite 待同步队列 → 妙搭云端数据库查询与导出`，不要求电脑长期在线。

### 最终目标（产品面）
- 采集：12 个抖音账号主页视频全量采集 + 口播 ASR 转写，全部入库
- 爆款：对已采集内容给出可解释的爆款评分（特征加权），落库、可查、可导出
- 调度：采集/同步任务按周期自动运行，无需人工逐条触发
- 展示：妙搭云端页面展示视频、快照、互动数据、口播稿

### 验收标准（做到什么算完成，可检验）
| 维度 | 完成信号 |
|------|---------|
| git 基线 | `git log` 存在初始 commit，`.env.local` / `.venv` / `data` / `models` 未被纳入版本库 |
| 环境还原 | `.\start.ps1` 后 `http://127.0.0.1:8000/api/health` 返回 ok；`pytest` 全绿 |
| 爆款评分模型层 | 新增 `backend/app/services/scoring/` 模块 + 评分表（SQLite）+ `/api/scoring/...` 接口 + 单测，能对已入库视频输出评分并写库 |
| 全自动调度 | 新增采集周期任务，按配置自动触发批量采集/同步；失败自动重试/告警；有开关可停 |
| 10 轮验收 | `runtime/reports/real-batch-10-rounds.json` 的 `summary.is_final=True`，且各轮完成率达标（目标 ≥ 90%） |

---

## 2. 文件地图（精确路径）

> 排序原则：入口 → 配置 → 服务 → 产出。路径均为项目根 `D:\全自动爬取短视频、推文爆款程序` 下。

### 入口 / 启动
| 路径 | 作用 | 状态 |
|------|------|------|
| `start.ps1` | 唯一启动入口：拉起后端(:8000)、妙搭前端(:3000/:3100)、Firefox 登录态、可选 ASR(:8765)；`-Install` 做首次安装 | 已完成（2026-08-17 更新 Firefox 引擎定版） |
| `backend/app/main.py` | FastAPI 应用入口，`uvicorn backend.app.main:app`；含 `lifespan()`（第 250 行起）与后台任务（第 271 行 `_run_temp_media_janitor`） | 已完成，**这是续作主战场** |

### 配置
| 路径 | 作用 | 状态 |
|------|------|------|
| `.env.local` | 生产密钥/开关（NopeCHA、代理、风控开关等）。**值已脱敏，不提交** | 存在（勿读值外泄） |
| `.env.example` | 环境变量模板，含全部键名与注释 | 已完成 |
| `pytest.ini` | `pythonpath=., backend`；`testpaths=backend/tests` | 已完成 |
| `.gitignore` | 已存在（git init 后要核对是否忽略 `.env.local`/`.venv`/`data`/`models`/`runtime`） | 已存在，git 基线未建 |
| `backend/requirements.txt` | 后端 Python 依赖 | 已完成 |
| `deployments/miaoda-matrix-radar/.env.local` | 云端前端环境变量（start.ps1 会一并加载） | 存在 |

### 后端核心代码（`backend/app/`）
| 路径 | 作用 |
|------|------|
| `backend/app/main.py` | FastAPI 入口 + 路由 + 后台任务 |
| `backend/app/config.py` | 配置加载（含 `DATABASE_PATH`） |
| `backend/app/db.py` | SQLite 连接/初始化 |
| `backend/app/models.py` | 数据模型 |
| `backend/app/accounts.py` | 账号白名单/映射 |
| `backend/app/risk_control.py` | 风控组件开关 |
| `backend/app/providers/` | 采集提供方：`base.py`、`mediacrawler.py`、`douyin.py`、`apizero.py`、`demo.py`、`mediacrawler_profile_hook.py` |
| `backend/app/services/collection.py` | 采集任务编排 |
| `backend/app/services/transcription.py` | 口播 ASR 转写（pyvideotrans 官方 CLI） |
| `backend/app/services/transcript_router.py` | 转录路由（inline 队列后端） |
| `backend/app/services/asr_service.py` | 可选 GPU ASR 服务客户端 |
| `backend/app/services/douyin_subtitles.py` / `platform_subtitles.py` | 字幕/口播稿获取 |
| `backend/app/services/sync.py` | 妙搭云端同步 |
| `backend/app/services/export.py` | xlsx 导出 |
| `backend/app/services/temp_media.py` | 临时媒体工作区清理 |
| `backend/app/services/creator_profiles.py` | 主页映射 |
| `backend/app/services/runtime.py` | 运行设置 |
| `backend/app/services/external_calls.py` | 外部 HTTP（限速/重试） |
| `backend/app/services/socialkit_resolver.py` | 可选 socialkit 解析器 |
| `backend/app/services/plugin_integrations.py` / `plugin_routes.py` | 插件集成 |
| `backend/app/services/multi_account/` | 多账号：`runner.py`、`account_pool.py`、`browser_profiles.py`、`retry.py`、`wal_queue.py`、`global_limiter.py`、`edge_cleanup.py`、`sync_firefox_login.py` |
| `backend/tests/` | 测试目录（**28 个 `test_*.py` 文件**） |

### 依赖/工具子项目（第三方，勿动）
| 路径 | 作用 |
|------|------|
| `MediaCrawler/` | 抖音采集器（有独立 `.venv`；上游许可证限非商业学习用途） |
| `MediaCrawler/database/sqlite_tables.db` | 采集器本地库（与 `data/radar.sqlite3` 是两回事） |
| `pyvideotrans/` | 口播转写（**必须用 `.venv-stt`，Python 3.10 CPU-only**；用 `cli.py --task stt`，禁用旧 `.venv`） |
| `deployments/miaoda-matrix-radar/` | 妙搭云端前端（npm；dev:server :3100、dev:client :3000） |
| `integrations/.venv-socialkit/` | 可选 socialkit 解析器 |
| `runtime/asr-service/` + `.venv-asr/` | 可选 GPU ASR 服务（:8765） |

### 产出 / 数据
| 路径 | 作用 |
|------|------|
| `data/radar.sqlite3` | **本地主库**（WAL 模式；视频、快照、评论、口播稿、运行设置） |
| `data/matrix_radar.db` | 早期库（历史，勿当主库） |
| `data/temp_media/job-<job-id>/` | 受控临时媒体工作区（成功落库后删除） |
| `data/browser_data/` | 浏览器登录态（`ff_dy_user_data_dir` = Firefox 登录态，`cdp_dy_user_data_dir` = Edge 共享态） |
| `data/imports/` | CSV 导入区 |
| `runtime/reports/` | **验收报告**（见第 4 节） |
| `logs/` | `backend.out.log` / `backend.err.log` / `miaoda-*.log` / `asr-service.*.log` |
| `docs/` | `architecture.md`、`PROJECT_AUDIT_20260806.md`、`MIGRATION_D_DRIVE_20260806.md`、`TECHNICAL_STACK_CONFIGURATION.md`、`plans/2026-08-06-data-closure-{design,implementation}.md` |

> ⚠️ 根目录有大量 `_*.py` 临时调试脚本（如 `_round10.py`、`_diag*.py`、`_fix_*.py` 等）与 `backend_backup_20260806_phase1/`、`backups/` 备份目录——属历史产物，交接期**先保留不动**，确认无引用后再清理（需用户确认）。

---

## 3. 已完成工作（全量逐条）

| # | 做了什么 | 产出物位置 | 如何验证有效 |
|---|---------|-----------|-------------|
| 1 | MediaCrawler 本地采集任务、进度轮询、SQLite 视频快照、失败重试队列 | `backend/app/services/collection.py`、`multi_account/`、`data/radar.sqlite3` | 真实采集任务能跑通并写库 |
| 2 | 12 账号抖音主页 `sec_user_id` 映射（8-10 补齐 11 个） | `backend/app/accounts.py`、`creator_profiles.py` | 12 账号均有映射；**新增 11 个仍需逐一真实采集验收** |
| 3 | 口播 ASR 转写（pyvideotrans 官方 `cli.py --task stt`，`.venv-stt` Python 3.10，`small` 模型，CPU int8） | `backend/app/services/transcription.py`、`transcript_router.py`、`pyvideotrans/` | 官方 CLI 已用中文 WAV + 真实抖音视频验收；落库后删工作副本 |
| 4 | 转录缓存（SQLite，7 天 TTL）+ 临时媒体工作区管理（`data/temp_media/job-<id>`，成功删/失败留 24h） | `services/temp_media.py`、`services/transcript_router.py` | 定时 janitor 清理 + 启动对账 |
| 5 | 妙搭云端数据库：账号白名单、视频去重、历史快照、真实健康检查 | `services/sync.py`、`deployments/miaoda-matrix-radar/` | 公开站点可访问：https://ncn5iae3ocvu.feishuapp.com/app/app_17bkk0a8pt8 |
| 6 | CSV 导入与本地同步共用同一套校验/标准化/写入逻辑 | `services/sync.py`、`data/imports/` | 导入→同步链路一致 |
| 7 | 按账号导出原生 `.xlsx`（最新视频 / 历史快照 / 账号汇总 三 sheet） | `services/export.py` | 导出文件三 sheet 齐全 |
| 8 | 2026-08-06 真实闭环验收：「科研华哥」最近 7 天导入并同步 9 条作品，云端显示 9 视频 + 9 快照 + 非零互动 | 云端页面 | README 有验收记录 |
| 9 | 风控/合规决策落地：NopeCHA 自动验证码、代理轮换、Firefox 引擎定版（登录态持久） | `.env.local`、`start.ps1`、`risk_control.py`、`browser_profiles.py` | 生产 `.env.local` 已置 true；start.ps1 默认 Firefox |
| 10 | 单条视频 120 秒硬截止；默认仅处理前 10 条口播稿；成功落库后清理视频/WAV/SRT | `services/transcription.py`、`collection.py` | 批量任务不会无限运行 |

---

## 4. 当前精确进度

- **最后有效操作**：2026-08-17 在 `start.ps1` 定版 Firefox 引擎（登录态落 `data\browser_data\ff_dy_user_data_dir`，见 start.ps1 第 105-147 行）；2026-08-16 定版启用 NopeCHA 与代理轮换。
- **验收状态**：`runtime/reports/` 下有两份 10 轮真实批量采集报告——
  - `real-batch-10-rounds.json`（2026-08-14 04:56）：`rounds_captured=5, completed=4, blocked=1, pending=5`；video 保存率 100%，转录率 60%。
  - `per-round-reset-20260814-152119-421ce23f/summary.json`（2026-08-14 22:02）：`rounds_captured=6, completed=6, pending=4`；video 保存率 100%，转录率 77.78%，严格双达标率 77.78%，**`is_final=False`**。
  - 结论：**计划 10 轮，实际完成 6 轮，剩 4 轮 pending，报告未收尾（`is_final=False`）。**
- **代码/数据当前状态**：后端 `backend/app/main.py` 可启动；`data/radar.sqlite3` 为当前主库（WAL）；`pytest` 未跑（交接后 B 应先跑一遍建立基线）。
- **git**：根目录无 `.git`（从未 `git init`），`.gitignore` 已存在。
- **爆款评分**：无任何实现代码（`models/` 目录只有 `hf_cache` 与 `ms-playwright` 缓存，非评分模型）；前端导航已禁用该入口。

---

## 5. A 没做完的事（接力棒，全量逐条）

> 以下 4 项是 A（DeepSeek）留给 B（Claude Code）的接力棒，是 B 的起点，不是 B 的过错。每项标注阻塞原因、前置条件、优先级、完成定义。

| # | 没做完的事 | 为什么没做完（阻塞） | 前置条件 | 优先级 | 做到什么算完成 |
|---|-----------|---------------------|---------|--------|---------------|
| 1 | **爆款评分模型层未落地** | DeepSeek 阶段聚焦采集链路，评分属于规划中的下一阶段；README 明示"飞书同步、爆款评分和口播分析属于下一阶段，导航已禁用" | 先有稳定入库数据（已有） | 高 | 可解释评分：对已采集视频+口播稿输出评分，落 SQLite，有 `/api/scoring/...` 接口 + 单测 |
| 2 | **部分采集任务未接全自动调度** | 后端仅实现 `_run_temp_media_janitor`（临时媒体清理+转录对账，main.py:236-247/271）；没有采集任务的定时触发 | 采集链路稳定（已有） | 中 | 周期自动触发批量采集/同步，可配开关，失败自动重试，日志可查 |
| 3 | **10 轮验收未完成** | 计划 10 轮真实批量采集，实际完成 6 轮即中断（报告 `is_final=False`，剩余 4 轮 pending） | 采集环境可运行 | 中 | 跑完 10 轮，`real-batch-10-rounds.json` `summary.is_final=True`，转录/严格完成率 ≥ 90% |
| 4 | **根目录尚无 git 基线** | DeepSeek 阶段未做版本管理 | 无（`.gitignore` 已存在） | 高（接手第一步） | `git init` + 初始 commit；`.env.local`/`.venv`/`data`/`models` 等未入库 |

---

## 6. A→B 接力总览（读到就能开工，核心）

> 这张表就是 B 的开工清单：A 的每个遗留项 ↔ B 的接力任务一一对应。直接照"从哪开始"执行，无需再问人。

| # | A 没做完的（接力棒） | B 要做什么 | 从哪开始（文件/函数/命令） | 做到什么算完成（验证信号） |
|---|--------------------|-----------|---------------------------|---------------------------|
| 1 | 根目录无 git 基线 | 建 git 基线：init + 核对 `.gitignore` + 初始 commit | `cd D:\全自动爬取短视频、推文爆款程序` → `git init` → 检查 `.gitignore` 已忽略 `.env.local/.venv/data/models/runtime/backups` → `git add -A` → `git commit -m "初始基线：DeepSeek 阶段完成 6/10 轮验收后交接"` | `git log` 有 commit；`git status` 干净；`git ls-files | findstr env.local` 无输出 |
| 2 | 环境还原未验证（B 接手前提） | 启动服务 + 跑测试建立基线 | `.\start.ps1` → 开 `http://127.0.0.1:8000/api/health`；再 `.\.venv\Scripts\python.exe -m pytest -q` | health 返回 `{"status":"ok",...}`；pytest 全绿（`logs\backend.out.log` 无 ERROR） |
| 3 | 爆款评分模型层未落地 | 实现评分模型层 | 新建 `backend/app/services/scoring/__init__.py`（参照 `services/sync.py` 的依赖注入/DB 写库风格）；在 `backend/app/models.py`/`db.py` 加评分表迁移；在 `main.py` 注册 `/api/scoring/...` 路由 | 接口能对任意 `video_id` 返回评分+特征明细并写 `data/radar.sqlite3`；`pytest` 新增 scoring 单测通过 |
| 4 | 采集任务未接全自动调度 | 实现周期调度 | 参照 `_run_temp_media_janitor`（main.py:236-247）再写一个 `_run_collection_scheduler` 协程，在 `lifespan()`（main.py:271 附近）`asyncio.create_task`；开关放 `runtime_settings` / `.env.local`（如 `COLLECTION_AUTO_SCHEDULE=true`）；可复用 `scripts/report-real-batch.py` 的批量流程 | 到点自动创建采集任务，`data/radar.sqlite3` 的 `collection_job_items` 出现新任务；关闭开关后不再触发；`logs\backend.out.log` 有调度日志 |
| 5 | 10 轮验收未收尾 | 续跑剩余 4 轮并收尾报告 | 按 `runtime/reports/real-batch-10-rounds.json` 的 `execution_plan`（10 项数组）与 `scripts/report-real-batch.py` 用法续跑第 7-10 轮，复算 `summary` | 报告 `summary.is_final=True`、`rounds_pending=0`、转录/严格完成率 ≥ 90% |

> **接力开工第一步**：在项目根执行 `git init` 并完成初始 commit（接力棒 #1）→ 紧接着跑 `.\start.ps1` 后访问 `http://127.0.0.1:8000/api/health` 看到 `ok`，即**正式接上**。出现该信号后即可按上表 #3-#5 逐项推进。

---

## 7. 下一步行动计划（命令级）

> 环境：Windows PowerShell。命令均在项目根 `D:\全自动爬取短视频、推文爆款程序` 执行。

### A. 立即做（接手前 30 分钟）
```powershell
cd D:\全自动爬取短视频、推文爆款程序

# 1) 建 git 基线（先核对 .gitignore 已忽略敏感/大目录）
notepad .gitignore   # 确认含 .env.local、.venv、data、models、runtime、backups、__pycache__
git init
git add -A
git commit -m "初始基线：DeepSeek 阶段完成 6/10 轮验收后交接"

# 2) 还原环境并验证
.\start.ps1
# 打开浏览器访问 http://127.0.0.1:8000/api/health ，应返回 {"status":"ok",...}
# 检查日志：Get-Content .\logs\backend.out.log -Tail 20

# 3) 跑测试建立基线
.\.venv\Scripts\python.exe -m pytest -q
# 预期：backend\tests 下 28 个 test_*.py 全部通过
```
> 若 `start.ps1` 报 "Run .\start.ps1 -Install first" 或 "MediaCrawler virtual environment is missing"：说明虚拟环境未就绪，先跑 `.\start.ps1 -Install`（一次性，需联网；pyvideotrans 环境需要 `uv`，见 start.ps1 第 44-62 行）。
> 若端口被占：`:8000` 后端、`:3000`/`:3100` 前端、`:8765` ASR、`:9222` Edge CDP（仅非 Firefox 模式）、`:5010` proxy_pool。`Get-NetTCPConnection -LocalPort 8000 -State Listen` 可排查。

### B. 之后做（按接力总览 #3→#4→#5 顺序）
```powershell
# 4) 爆款评分模型层（新建 backend/app/services/scoring/）
#    - scoring 特征建议：播放/点赞/评论/收藏/转发率、互动密度、完播信号、口播稿关键词命中
#    - 落表：data/radar.sqlite3 新增 video_scores(id, video_id, score, features_json, created_at)
#    - 路由：backend/app/main.py 注册 /api/scoring/score/{video_id} 与 /api/scoring/list
#    写完跑：.\.venv\Scripts\python.exe -m pytest -q

# 5) 全自动调度
#    - 在 backend/app/main.py 仿 _run_temp_media_janitor（236-247 行）新增 _run_collection_scheduler
#    - 在 lifespan()（271 行）asyncio.create_task 启动
#    - 开关：.env.local 加 COLLECTION_AUTO_SCHEDULE=false（默认关，联调通过后再开）
#    验证：开关开→ 观察 data/radar.sqlite3 的 collection_job_items 自动出现任务

# 6) 续跑 10 轮验收剩余 4 轮
#    - 读 runtime/reports/real-batch-10-rounds.json 的 execution_plan 数组，确认第 7-10 轮参数
#    - 复用 scripts/report-real-batch.py 与 per-round-reset 的跑法续跑，重写报告 summary
#    验证：报告 is_final=True、rounds_pending=0
```
> 若任务量大（评分+调度+验收并行），可用子代理并行推进（Claude Code 支持多子代理），但改 `backend/app/main.py` 与 DB schema 需串行避免冲突。

### 通用命令速查
| 需求 | 命令 |
|------|------|
| 启动全栈 | `.\start.ps1` |
| 首次安装 | `.\start.ps1 -Install` |
| 单跑后端 | `.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`（工作目录=项目根） |
| 跑测试 | `.\.venv\Scripts\python.exe -m pytest -q` |
| 看后端日志 | `Get-Content .\logs\backend.out.log -Tail 50` / `backend.err.log` |
| 查主库 | `.\.venv\Scripts\python.exe -c "import sqlite3;con=sqlite3.connect(r'D:\全自动爬取短视频、推文爆款程序\data\radar.sqlite3');print([r[0] for r in con.execute(\"select name from sqlite_master where type='table'\")])"` |
| 查端口 | `Get-NetTCPConnection -LocalPort 8000,3000,3100,8765,9222,5010 -State Listen` |

---

## 8. 环境与配置依赖（完整清单）

| 项 | 详情 |
|----|------|
| OS | Windows 11 Pro（本机开发；CLAUDE.md 为 Windows 环境） |
| Python（后端） | `.venv\Scripts\python.exe`（项目根 venv，Python 3.12，见 pyc 目录 cpython-312） |
| Python（MediaCrawler） | `MediaCrawler\.venv\Scripts\python.exe` |
| Python（转写） | `pyvideotrans\.venv-stt\Scripts\python.exe`（**必须 3.10，CPU/STT-only，禁旧 `.venv`**） |
| Python（ASR 服务） | `runtime\.venv-asr\Scripts\python.exe`（可选，:8765，`fastapi`+`uvicorn`） |
| Python（socialkit） | `integrations\.venv-socialkit\Scripts\socialkit.exe`（可选） |
| 前端 | Node/npm + `deployments\miaoda-matrix-radar`（`npm ci` 后 `dev:server`/`dev:client`） |
| 数据库 | SQLite：主库 `data/radar.sqlite3`（WAL）；采集库 `MediaCrawler\database\sqlite_tables.db` |
| 外部依赖 | `D:\ffmpeg\bin\ffprobe.exe`（媒体探测）；`uv`（转写环境构建）；Playwright/Firefox（登录态，落 `data/browser_data`） |
| 端口 | 8000 后端 / 3000 client / 3100 server / 8765 ASR / 9222 Edge CDP（非 Firefox 模式）/ 5010 proxy_pool |
| 密钥/Token | 存放于 `.env.local`（**值已脱敏，勿提交/勿外发**）：`MIAODA_API_KEY`、`SITES_BYPASS_TOKEN`、`SYNC_TOKEN`、`NOPECHA_API_KEY`、代理池配置 |
| 关键环境变量 | `COLLECTION_PROVIDER=mediacrawler`、`MEDIACRAWLER_LOGIN_TYPE=qrcode`、`TRANSCRIPTION_ENABLED`、`PYVIDEOTRANS_*`、`TEMP_MEDIA_*`、`RISK_*`（风控/代理/验证码开关）、`FFPROBE_PATH` |

---

## 9. 数据与状态快照

- **主库** `data/radar.sqlite3`：当前数据源。表含 `collection_job_items`、`videos`、`video_snapshots`、`video_comments`、`video_transcriptions`、`transcript_cache`、`runtime_settings`、`accounts` 等（`sqlite_master` 可查全表）。
- **采集库** `MediaCrawler\database\sqlite_tables.db`：MediaCrawler 中间产物库。
- **临时数据**：`data/temp_media/job-<id>/` 由 janitor 自动清理；失败材料保留 24h 后清理（`TEMP_MEDIA_TTL_HOURS=24`）。
- **登录态** `data/browser_data/`：Firefox 登录态（`ff_dy_user_data_dir`）为当前默认；Edge 共享态（`cdp_dy_user_data_dir`）仅非 Firefox 模式使用。**首次 Firefox 使用需手动扫码一次。**
- **测试库** `backend/test-contract.sqlite3`：测试契约库，`pytest` 会用到。
- **报告** `runtime/reports/`：10 轮验收数据（见第 4 节），续跑前**保留**。
- **可清理（交接期勿动，确认后再删）**：根目录 `_*.py` 临时脚本、`backups/`、`backend_backup_20260806_phase1/`、`runtime/{e2e-test,e2e-test2,yt-dlp-test,yt-test2}` 测试残留。

---

## 10. 关键决策与踩坑记录

| 决策/坑 | 说明 |
|--------|------|
| 唯一正式目录 = D 盘 | `D:\全自动爬取短视频、推文爆款程序` 为唯一源目录（见 `docs/MIGRATION_D_DRIVE_20260806.md`）；F 盘旧项目不再修改 |
| 转写用 pyvideotrans 官方 CLI | 恢复 `cli.py --task stt` + `.venv-stt`(Py3.10)；**不要用旧全功能 `.venv`**（GUI/TTS/CUDA 依赖冲突）；CPU 快速模式 int8/beam1/best-of1；`small` 模型生产默认、`tiny` 仅烟测 |
| 单条 120 秒硬截止 | 每条视频下载→校验→ASR 共 120s；超时终止子进程、记失败、继续后续。**不承诺任意视频 2 分钟内成功** |
| 默认仅处理前 10 条口播稿 | 防止单任务无限运行；"获取全部/自定义数量"需前端风险弹窗确认，后端拒绝无确认请求 |
| Firefox 引擎定版（2026-08-17） | 登录态持久、不反复扫码；登录态落 `data\browser_data\ff_dy_user_data_dir`。非 Firefox 分支的 B++++ 克隆逻辑已回退共享源单会话（见 start.ps1 第 105-147 行注释） |
| 合规红线突破（2026-08-16） | 用户决策启用 NopeCHA 自动验证码、代理轮换（`RISK_PROXY_ENABLED`/`RISK_NOPECHA_ENABLED`），生产 `.env.local` 已置 true，**风险自担** |
| 三目录分离 | 浏览器登录态默认落 D 盘 `data\browser_data`（不再用 C 盘 LOCALAPPDATA）；Playwright 浏览器隔离在 `MediaCrawler\.playwright-browsers` |
| 妙搭前端 | 唯一的正式前端是 `deployments\miaoda-matrix-radar` 的 app_17bkk0a8pt8；旧 `frontend/` 目录会被 start.ps1 启动时自动删除（勿恢复）；3000 端口仅归妙搭 client，其他进程会被驱逐 |
| 上游许可 | MediaCrawler 限非商业学习用途；正式商业运营前需确认许可或替换采集适配器 |
| 抖音风控 | 验证码/Argus 风控可能要求人工处理；新增 11 个映射仍需逐一真实采集验收，不能描述为"12 账号全部稳定通过" |

---

## 11. 风险与待确认项

- ❓ **12 账号稳定性**：仅"科研华哥"完成过真实闭环验收；其余 11 账号映射已补齐但未逐一真实采集验收——续跑 10 轮验收前建议先各账号烟测一轮。
- ❓ **10 轮验收口径**：`real-batch-10-rounds.json` 与 `per-round-reset-20260814` 两份报告口径不同（一为 5 轮 captured/4 completed，一为 6 completed）。续跑前先与用户确认**以哪份为准、剩余轮次怎么记**，避免重复或漏跑。
- ❓ **评分特征口径**：爆款评分特征（播放/点赞/评论/收藏/转发/完播/文本关键词）权重由用户业务确定，落库前先与用户对齐口径。
- ❓ **自动调度粒度**：按账号？按天？跑几轮？需用户确认调度策略后再实现。
- ❓ **git 基线内容**：`.gitignore` 需覆盖 `.env.local`、`.venv*`、`data/`、`models/`、`runtime/`、`backups/`、`MediaCrawler/.venv*`、`pyvideotrans/.venv*`；核对后再 `git add -A`，避免密钥/大目录入库。
- ❓ **上游许可**：MediaCrawler 非商业许可——商业运营前需替换采集适配器或获授权。
- ⚠️ **敏感信息**：`.env.local` 含真实密钥，**禁止提交、禁止外发**；交接文档中一律脱敏。
- ⚠️ **大量临时脚本**：根目录 `_*.py` 与备份目录体积大，清理前需用户确认。

---

## 12. 续作启动手册（从零恢复）

1. **读代码入口**：`D:\全自动爬取短视频、推文爆款程序\backend\app\main.py`（尤其 `lifespan()` 第 250 行起）→ `backend/app/services/collection.py`（采集编排）→ `backend/app/services/transcription.py`（转录）。
2. **还原环境**：`cd D:\全自动爬取短视频、推文爆款程序` → `.\start.ps1`（首次装则 `.\start.ps1 -Install`）。
3. **验证续上了（关键信号）**：
   - `http://127.0.0.1:8000/api/health` → `{"status":"ok",...}`
   - `http://localhost:3000` → 妙搭前端可打开
   - `.\.venv\Scripts\python.exe -m pytest -q` → 全绿
   - `logs\backend.out.log` 无异常堆栈
   - `git log` → 初始 commit 存在
4. **然后**：按第 6 节接力总览 #3（评分）→ #4（调度）→ #5（验收）逐项推进。
5. **第 6 节是"开工清单"（接 A 的活），本节是"环境还原"（把 A 的环境跑起来）——先本节后第 6 节。**

---

## 13. 按 Claude Code 定制的附加内容

- **建议在项目根写 `CLAUDE.md`**（Claude Code 会自动加载并遵守），至少写入：
  - 唯一正式目录 = 项目根；`.env.local` 只读且不提交；
  - 转写必须用 `pyvideotrans\.venv-stt`（Python 3.10）+ 官方 `cli.py`，禁旧 `.venv`；
  - 默认 Firefox 引擎，登录态在 `data\browser_data\ff_dy_user_data_dir`，首次需手动扫码；
  - 单条 120s 硬截止、默认前 10 条口播稿；
  - 端口占用约定（8000/3000/3100/8765/9222/5010）；
  - 涉及 DB schema 变更前先在 `data/radar.sqlite3` 备份。
- **可并行子代理**：评分模型（#3）与自动调度（#4）模块相对独立，可派子代理并行；但改 `main.py` 路由与 DB 迁移串行。
- **遇到不确定主动确认**：抖音风控/账号登录/验收口径/评分口径/许可问题，先问用户再动手（见第 11 节 ❓ 项）。
- **验证一律可跑**：每步改动配 `pytest` 或用 health/日志验证，不靠肉眼判断。

---

*本文档由「交接助手」skill 生成。全部路径/命令/状态均基于项目实况核实；未核实或需用户确认处已标 ❓。*
