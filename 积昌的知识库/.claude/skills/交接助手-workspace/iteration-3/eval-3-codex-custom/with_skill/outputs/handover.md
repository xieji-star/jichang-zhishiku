# 全自动爬取短视频、推文爆款程序 — 交接文档（给 Codex 版）

> **元信息**：项目名＝全自动爬取短视频、推文爆款程序 ｜ 交接对象＝**Codex（OpenAI 智能体）** ｜ 交接方向＝A（DeepSeek）→ B（Codex） ｜ 交接日期＝2026-08-17
>
> **给 Codex 的一句话**：A（DeepSeek）已把采集核心 `backend/app/services/collection.py`、ASR 转写 `_asr_8765.py`、本地入库跑通（health：账号 12 / 主页映射 12，pytest 264 passed）。**你的开工第一件事＝在项目根跑一遍 `pytest -q`，看到 `264 passed` 就算接上了**，然后按第 6 节接力总览逐条接 A 的活。

---

## 0. 交接摘要（启动包）

- **项目做什么**：Windows 本机全自动爬取短视频（抖音等）+ 推文爆款素材，含采集 → ASR 转写 → 字段补全 → 爆款评分 → 入库 → 前端展示的完整链路。
- **A 已完成（DeepSeek）**：
  1. 采集核心 `backend/app/services/collection.py`（多账号执行、转写批次、入库），链路已通；
  2. 多账号入口 `run_accounts()` 位于 `backend/app/services/multi_account/runner.py:26`；平台采集 `collect_account(account, range_key)` 位于 `backend/app/providers/`（`base.py:5` 定义接口，`douyin.py:8`、`mediacrawler.py:423` 实现）；
  3. ASR 转写服务 `_asr_8765.py`（本地 faster-whisper，`127.0.0.1:8765`）；
  4. 基础链路验证通过：`/api/health` 返回 `status: ok`（账号 12、主页映射 12），`pytest -q` → `264 passed`。
- **A 没做完（接力棒，B 要接 4 根）**：① `field.py:28` 字段补全逻辑未完成；② 爆款评分层未落地；③ 调度未接全自动；④ 根目录无 git。
- **B 第一件事（从这开工最省力）**：`cd "D:\全自动爬取短视频、推文爆款程序"` 后跑 `& ".\.venv\Scripts\python.exe" -m pytest -q`，确认 `264 passed`，再按第 6 节接力总览 #1 动手。

---

## 1. 项目总览与验收标准

- **一句话定位**：本地自动采集短视频/推文素材 → 转写文案 → 补全字段 → 打爆款评分 → 入库展示的运营工具链。
- **最终目标（验收）**：全自动跑通「采集→ASR→字段补全→爆款评分→入库→前端可看」，无需人工干预。
- **可检验的验收标准**：
  - `pytest -q` → `264 passed`（全量测试绿）；
  - `GET /api/health` → `status: ok`，账号 12 / 主页映射 12；
  - 采集任务最终状态为 `completed`，前端（`deployments\miaoda-matrix-radar`）非空且有数据渲染；
  - 4 根接力棒全部闭合（见第 6 节验证信号列）。

---

## 2. 文件地图（精确路径）

> 所有路径均相对于项目根 `D:\全自动爬取短视频、推文爆款程序`。

| 文件/目录 | 作用 | 状态 |
|---|---|---|
| `backend/app/services/collection.py` | **采集核心**：`CollectionService` 类，`start/pause/resume/cancel/_run`、`_collect_account`(:534)、`_collect_account_isolated`(:725)、转写批次（`_transcribe_one` :837 等） | ✅ 已完成，链路已通 |
| `backend/app/services/multi_account/runner.py` | **多账号执行入口**：`run_accounts(task_id, accounts, payload, ...)` 在 **:26** | ✅ 已完成 |
| `backend/app/providers/base.py` / `douyin.py` / `mediacrawler.py` | 平台采集 provider：`collect_account(account, range_key)`（base.py:5 定义、douyin.py:8、mediacrawler.py:423 实现） | ✅ 已完成 |
| `backend/app/main.py` | FastAPI 主入口；`GET /api/health` 在 **:307**（含 transcription/cache/risk_control/plugin_integrations 子健康检查） | ✅ 已完成 |
| `backend/app/risk_control.py` | 风控/健康检查模块（可作评分层代码风格参考） | ✅ 已完成 |
| `_asr_8765.py` | 本地 OpenAI 兼容 ASR 服务（faster-whisper，`127.0.0.1:8765`） | ✅ 已完成（重建于 2026-08-16） |
| `MediaCrawler/media_platform/*/field.py` | 各平台字段定义（douyin/xhs/weibo/bilibili/kuaishou/zhihu/tieba 共 7 个） | ⚠️ **`field.py:28` 字段补全逻辑未完成（接力棒 #1）** |
| `deployments/miaoda-matrix-radar` | 前端（NestJS + React，含 dist/node_modules/package.json） | ⚠️ 已可构建，需数据非空验证 |
| `start.ps1` | 一键启动脚本：后端 python、MediaCrawler、pyvideotrans、ASR、前端 | ✅ 已完成（启动入口） |
| `scripts/` | 辅助脚本：`clone-browser-profiles.ps1`、`start-evil0ctal-api.ps1`、`backend_preflight.py`、`batch-data-cycle.py` 等 | ✅ 部分完成 |
| `pytest.ini` | pytest 配置（`testpaths=backend/tests`） | ✅ 已完成 |
| `backups/` | 数据库备份（`batch-reset-round-*.sqlite3` + manifest，20260814 起多轮） | ✅ 已有 |
| `data/` | 运行数据（含 `radar.sqlite3`） | ✅ 已有 |
| `.git` | 版本控制 | ❌ **根目录无 git（接力棒 #4）** |

---

## 3. 已完成工作（全量逐条）

1. **采集核心（collection.py）**：多账号采集、控制指令（start/pause/resume/cancel）、隔离采集 `_collect_account_isolated`、转写批次与入库持久化。产出物：`backend/app/services/collection.py`。验证：链路 E2E 跑通，采集任务能到 `completed`。
2. **多账号执行入口（runner.py）**：`run_accounts(task_id, accounts, payload, ...)`（runner.py:26）串联账号集合。
3. **平台采集 provider**：`collect_account(account, range_key)` 接口与 douyin/mediacrawler 实现（providers/douyin.py:8、mediacrawler.py:423）。
4. **ASR 转写（_asr_8765.py）**：本地 OpenAI 兼容 faster-whisper 服务（`127.0.0.1:8765`）。关键细节：2026-08-16 重建——原服务无源码且被会话恢复杀死（口播稿 10061 根因）；RTX 5060 CUDA 提速（ct2 4.8.1 检测 1 设备，float16 GPU 推理），CUDA 不可用时自动回退 CPU int8。
5. **本地入库 + 基础链路**：转写结果/采集记录落库（sqlite）。验证：`GET /api/health` → `status: ok`，**账号 12、主页映射 12**；`pytest -q` → **264 passed**。
6. **健康检查体系**：`backend/app/main.py:307` 的 `/api/health`，聚合 transcription/cache/risk_control/plugin_integrations 子检查。
7. **启动脚本 start.ps1**：一键拉起后端 python、MediaCrawler、pyvideotrans、ASR（`Get-NetTCPConnection -LocalPort 8765` 检测）、前端；加载 `.env.local`。

---

## 4. 当前精确进度

- **最后一次有效状态**：基础链路跑通——健康检查 `status: ok`（账号 12 / 主页映射 12），测试全量 `264 passed`，采集任务能完成到 `completed`。
- **当前代码状态**：`collection.py`、`runner.py`、providers、ASR、健康检查、前端骨架均已就位；`pytest.ini` 已配置（`pythonpath=. + backend`，`testpaths=backend/tests`）。
- **卡在哪**：4 个遗留项未闭合——字段补全、爆款评分、全自动调度、git 初始化（详见第 5 节）。

---

## 5. A 没做完的事（接力棒，全量逐条）

> 以下是 A（DeepSeek）留给你的接力棒，是**你的起点，不是你的过错**。每条都是你要接的活，做到第 6 节验证信号列的标准即算闭合。

| # | 接力棒 | 为什么没做完（阻塞原因） | 优先级 |
|---|---|---|---|
| 1 | **`field.py:28` 字段补全逻辑未完成**：采集到的原始数据到标准字段（如标题/文案/互动数/发布时间）的映射补全未收尾 | 采集主链路优先打通，字段映射属收尾细化，未及完成 | 🔴 高（影响入库字段完整性） |
| 2 | **爆款评分层未落地**：给已入库内容打"爆款指数"评分的模块尚未实现 | 评分规则/权重未定稿，属业务决策依赖 | 🟡 中 |
| 3 | **调度未接全自动**：采集仍是手动/半自动触发，未接定时全自动（Windows 计划任务或常驻调度） | 自动化触发方式未选型 | 🟡 中 |
| 4 | **根目录无 git**：项目未纳入版本控制，改代码无回滚保障 | 早期迭代未初始化仓库 | 🟢 一般（建议立即补，防丢） |

---

## 6. A→B 接力总览（读到就能开工，核心）

> 每一行＝一根接力棒。**"从哪开始"列已按 Codex 习性写成 PowerShell 命令 + 函数级定位，直接执行即可，无需问人。**

| # | A 没做完的（接力棒） | B（Codex）要做什么 | 从哪开始（PowerShell 命令 / 函数级定位） | 做到什么算完成（验证信号） |
|---|---|---|---|---|
| 1 | `field.py:28` 字段补全逻辑未完成 | 补全字段映射逻辑 | 先定位目标文件：`Get-ChildItem "MediaCrawler\media_platform" -Recurse -Filter field.py`；打开对应平台 `field.py` 第 **28** 行补齐字段补全（❓ 见第 10 节，需确认是哪个平台） | `pytest -q` 仍 **264 passed**（含新增字段用例）；采集出的 record 字段齐全（标题/文案/互动数/发布时间非空） |
| 2 | 爆款评分层未落地 | 实现爆款评分模块 | 在 `backend\app\services\` 新建 `score.py`；代码风格参考 `backend\app\risk_control.py`（健康检查写法） | `pytest -q` 通过（含评分单测）；任务输出/接口返回出现 `score` 字段 |
| 3 | 调度未接全自动 | 接 Windows 全自动调度 | 方案 A：`scripts\` 新增 `schedule-run.ps1` + `schtasks /create /tn "AutoCollect" /tr "powershell -File ..." /sc daily /st 02:00`；方案 B：`backend\app\services\` 加常驻定时调度（参考 runner.py 入口） | `schtasks /query /tn AutoCollect` 出现任务；到点自动触发，采集任务状态变 `completed` |
| 4 | 根目录无 git | 初始化 git + 首次提交 | `cd "D:\全自动爬取短视频、推文爆款程序"` → `git init` → 写 `.gitignore`（排除 `.venv/`、`node_modules/`、`backups/`、`data/*.sqlite3`、日志）→ `git add -A` → `git commit -m "init"` | `git status` 显示 clean；`git log --oneline` 有 `init` 提交 |

**接力开工第一步（先验证环境接上了，再动手）：**

```powershell
cd "D:\全自动爬取短视频、推文爆款程序"
& ".\.venv\Scripts\python.exe" -m pytest -q
```

→ 出现 **`264 passed`** 即视为环境正式续上；之后按 #1 的"从哪开始"直接开工。

---

## 7. 下一步行动计划（命令级）

### 立即做（按顺序）

1. **验证环境续上**：
   ```powershell
   cd "D:\全自动爬取短视频、推文爆款程序"
   & ".\.venv\Scripts\python.exe" -m pytest -q        # 期望：264 passed
   ```
2. **接力棒 #1 字段补全**：定位并读 `field.py`（`Get-ChildItem MediaCrawler\media_platform -Recurse -Filter field.py`），看第 28 行附近缺什么映射，补齐后跑 `pytest` + 手工采一条验证字段。
3. **接力棒 #2 爆款评分**：在 `backend\app\services\score.py` 实现评分函数，接入采集管道（`collection.py` 内 `_persist_platform_result` 附近写入 score），加单测。
4. **接力棒 #3 自动调度**：选方案 A（`schtasks` 计划任务）最省事——写好 `scripts\schedule-run.ps1` 再注册任务。
5. **接力棒 #4 git 初始化**：`git init` + `.gitignore` + 首次提交（**建议最先做，防止改崩无法回滚**）。

### 之后做

- 前端 `deployments\miaoda-matrix-radar` 联调：确认有数据渲染（`npm run start` 后页面非空）。
- 观察 ASR 转写稳定性（`127.0.0.1:8765`），口播稿链路回归。

---

## 8. 环境与配置依赖（完整清单）

> Codex 特有提醒：**先查 `config.toml` 再开工**，第三方模型/供应商不可用时本会话可能跑不动。

- **Codex 配置**：`C:\Users\asus\.codex\config.toml`（可配第三方模型，如 deepseek）。检查命令：
  ```powershell
  Get-Content "$env:USERPROFILE\.codex\config.toml"
  ```
  若文档指向第三方模型/供应商 key，确认其有效性；**key 值勿明文写入交接文档（已脱敏为 `<已脱敏>`）**。
- **Codex 本地会话（可跨机迁移）**：`C:\Users\asus\.codex\sessions\*.jsonl`。跨机迁移时**只拷 sessions 目录，不拷 `auth.json`**（auth.json 绑定本机登录）。
  ```powershell
  Get-ChildItem "C:\Users\asus\.codex\sessions\*.jsonl"
  ```
- **运行环境**：Windows 11 Pro；Python 虚拟环境见各子项目：backend `.venv\Scripts\python.exe`、MediaCrawler `.venv\`、pyvideotrans `.venv-stt\`、ASR `runtime\.venv-asr\`。
- **依赖库**：FastAPI、uvicorn、faster-whisper（ct2 4.8.1）、sqlite3（数据落盘）、pytest。版本以各 `.venv` 实装为准。
- **端口**：ASR `127.0.0.1:8765`；后端 HTTP 端口从 `.env.local` 读取（❓ 见第 10 节，启动后以 `Get-NetTCPConnection` 确认实际监听端口）。
- **环境变量**：`.env.local`（根目录），`start.ps1` 通过 `Import-DotEnv` 加载；含后端端口、ASR base url、供应商 key（脱敏）。
- **密钥/token**：存放于 `.env.local` 与 `config.toml`，本文档不落值。

---

## 8. 数据与状态快照

- **数据库**：`data\radar.sqlite3`（运行数据），`backups\` 下多轮 `batch-reset-round-*.sqlite3` + manifest（20260814 起）。改动数据前建议先备份。
- **日志**：`logs\`（`start.ps1` 会建目录；ASR 日志 `asr-service.out/err.log`）。
- **测试数据**：`backend/tests/`（pytest 264 条）。**无需清理**。
- **需保留的中间产物**：`backups\`、`logs\`、`data\` 均保留；勿删各 `.venv`。
- **可清理**：根目录大量 `_*.py` 调试脚本（`_diag*.py`、`_probe*.py`、`_check*.py`、`_patch*.py` 等）与 `__pycache__/`——接棒确认链路稳定后可整理，但**先问用户再删**。

---

## 9. 关键决策与踩坑记录

- **ASR 服务重建（2026-08-16）**：原 ASR 服务无源码且被会话恢复杀死（口播稿 10061 根因）→ 重建为 `_asr_8765.py` 本地 OpenAI 兼容服务（`127.0.0.1:8765`）。后续不要用"会话恢复/杀 python"方式误杀该服务。
- **GPU 提速**：RTX 5060 + ct2 4.8.1，ASR 走 float16 GPU 推理；CUDA 不可用自动回退 CPU int8（保证口播稿链路不阻塞）。
- **网络风控**：爬虫对目标站点（如抖音）可能触发 **403 风控**。代理/分流走 `127.0.0.1:7897`，验证命令：
  ```powershell
  curl.exe -x 127.0.0.1:7897 -I "https://www.douyin.com/"
  # 期望 HTTP 200；若 403/被墙 → 代理/分流未生效
  ```
- **启动方式**：用 `start.ps1` 一键启动，内部用 `Get-NetTCPConnection -LocalPort 8765 -State Listen` 检测 ASR 是否已监听。
- **浏览器/风控清理**：`scripts\clone-browser-profiles.ps1`（克隆浏览器指纹）、`cleanup_browsers` 系列脚本处理浏览器会话。

---

## 10. 风险与待确认项（❓）

- ❓ **`field.py:28` 具体指哪个平台**：`MediaCrawler\media_platform\` 下有 7 个 `field.py`（douyin/xhs/weibo/bilibili/kuaishou/zhihu/tieba），接棒 #1 需先用 `Get-ChildItem` 定位实际要改的那个，或询问用户。
- ❓ **后端 HTTP 端口**：未在本次核对确认；从 `.env.local` 读取，启动后用 `Get-NetTCPConnection -State Listen` 实测。
- ❓ **爆款评分层/调度是否有半成品**：`backend\app\services\` 与 `scripts\` 下可能存在未收录的骨架，接棒 #2/#3 前先 `Get-ChildItem` 扫一眼，有则续写、无则新建。
- ❓ **前端非空的判定口径**：`deployments\miaoda-matrix-radar` 需有数据渲染（非空页面），具体以哪个页面/接口为准需人工确认。
- ❓ **爬虫账号可用性**：health 显示账号 12 / 主页映射 12，但账号 cookie/风控状态随时间变化，接棒后若采集失败先查 cookie/代理。

---

## 11. 续作启动手册（如何验证"续上了"）

**从零把 A 的环境跑起来 + 验证信号：**

1. **跑测试（最快验证环境）**：
   ```powershell
   cd "D:\全自动爬取短视频、推文爆款程序"
   & ".\.venv\Scripts\python.exe" -m pytest -q
   ```
   ✅ 信号：**`264 passed`**
2. **启动服务**：
   ```powershell
   .\start.ps1
   ```
   （或按需单独起后端/ASR/前端）
3. **验证后端健康**：
   ```powershell
   $port = (Get-Content ".env.local" | Select-String "PORT").Line.Split("=")[1].Trim()
   Invoke-RestMethod "http://127.0.0.1:$port/api/health" | ConvertTo-Json -Depth 5
   ```
   ✅ 信号：返回 `status: ok`，含 **账号 12 / 主页映射 12**
4. **验证 ASR 监听**：
   ```powershell
   Get-NetTCPConnection -LocalPort 8765 -State Listen
   ```
   ✅ 信号：存在 Listen 状态的 8765 连接
5. **验证前端非空**：
   ```powershell
   Get-ChildItem "deployments\miaoda-matrix-radar\dist" | Measure-Object
   ```
   ✅ 信号：dist 目录非空（已构建产物存在）

> 第 6 节接力总览＝**开工清单**（接 A 的 4 根棒）；本节＝**环境还原**（先把 A 的环境跑起来）。两者都绿，才算真正"续上了"。

---

## 12. 按 Codex 定制的附加说明

- **命令风格**：全文档已按 Windows/PowerShell 编写（`& ".\.venv\Scripts\python.exe" -m pytest`、`Get-NetTCPConnection`、`Get-ChildItem`、`curl.exe -x 代理`、`schtasks`）。在 Codex 内执行 PowerShell 时注意**中文路径加引号**。
- **接续位置**：核心接续点均给到**函数/行号**——`runner.py:26`、`providers/douyin.py:8`、`mediacrawler.py:423`、`collection.py:534/:725`、`main.py:307`、`field.py:28`。
- **config.toml 检查**：若本会话模型不可用，先查 `C:\Users\asus\.codex\config.toml` 确认第三方模型/供应商配置与 key（脱敏）。
- **会话迁移**：本交接文档对应 Codex 本地会话 `C:\Users\asus\.codex\sessions\*.jsonl`；跨机迁移只拷 sessions、不拷 auth.json。
- **网络代理**：目标站点 403 风控时走 `curl.exe -x 127.0.0.1:7897` 验证/分流（见第 9 节）。
