# 全自动爬取短视频、推文爆款程序 交接文档（给 Codex 版）

> [!note] 文档元信息
> - **项目名**：全自动爬取短视频、推文爆款程序（抖音达人数据采集，用户简称"知识库自动化整理项目"）
> - **交接对象**：Codex（L1 自治型续作智能体）
> - **交接日期**：2026-08-17
> - **数据保留声明**：⚠️ **平台内现有数据一律保留、不得清理**——视频/评论/口播稿/达人主页数据是第 4 轮测试的成果，Codex 需在此基础上继续完成本轮测试。

---

## 0. 交接摘要（启动包）

**项目做什么**：批量采集抖音指定达人（对标账号）的视频数据、评论、达人主页资料与**口播稿**（语音转文字），入库本地 SQLite，供前端面板查看与导出。当前正执行**第 4 轮测试**：10 个对标达人 × 每人 15 条视频，评论+主页+口播稿全量采集。

**当前做到哪一步**：
- ✅ 前 4 个账号已采完（投哥不请自来、秋芝2046、九筒电话亭、小Lin说，各 15 条视频）
- 🔄 第 5 个账号「老师好我叫何同学」采集中，剩余 5 个（影视飓风、老方创业手册、心中之城、毒舌电影、疯狂小杨哥）排队
- ✅ 三浏览器线路（Firefox 首选 → Edge → Chrome 兜底）+ 口播稿下载修复全部落地，全量测试 279 passed / 2 skipped

**最关键三件事**：
1. **已完成**：三浏览器线路、系统 Firefox 驱动、登录态同步、口播稿下载链路、图文跳过、前端线路显示修复。
2. **A 没做完的接力棒**：①第 4 轮剩余 6 账号采集；②28 条失败口播稿补采；③Chrome 线路扫码实测；④Edge 线路恢复验证；⑤临时文件清理。
3. **Codex 下一步第一件事**：**验证后端在线 → 查询第 4 轮任务（a57a3049…）状态 → 若中断则 resume 继续**。

**最省力入口**：任务已通过 resume 接口在跑（客户端脚本轮询中）。先跑进度查询脚本看任务是否还活着，再决定继续监控或重新 resume。

---

## 1. 项目总览与验收标准

**一句话定位**：D:\全自动爬取短视频、推文爆款程序 是本地运行的抖音达人数据采集平台（后端 FastAPI + MediaCrawler 采集 fork + 本地前端）。

**最终目标（第 4 轮验收标准）**：
- 10 个对标账号全部完成：每人 15 条视频 + 评论（每条≤20）+ 达人主页资料 + 口播稿
- 视频/评论/主页入库 data\radar.sqlite3，前端面板可见
- 口播稿成功率尽可能高（当前 33 成功 / 28 失败；失败为历史网络抖动，线路已恢复，需补采）
- 全量 pytest 保持 279 passed / 2 skipped 零回归

**对标账号清单**（✅已采 / 🔄采集中 / ⏳排队）：
| 账号 | 状态 |
|---|---|
| 投哥不请自来 | ✅ 完成 |
| 秋芝2046 | ✅ 完成 |
| 九筒电话亭 | ✅ 完成 |
| 小Lin说 | ✅ 完成 |
| 老师好我叫何同学 | 🔄 采集中 |
| 影视飓风 | ⏳ 排队 |
| 老方创业手册 | ⏳ 排队 |
| 心中之城 | ⏳ 排队 |
| 毒舌电影 | ⏳ 排队 |
| 疯狂小杨哥 | ⏳ 排队 |

---

## 2. 文件地图（精确路径）

> 项目根目录：D:\全自动爬取短视频、推文爆款程序（下文相对路径均以此为基准）

| 文件/目录 | 作用 | 当前状态 |
|---|---|---|
| backend\app\main.py | FastAPI 入口；/api/videos 返回 mediaKind（第 733 行附近） | ✅ 已改（mediaKind 字段） |
| backend\app\services\collection.py | 采集流水线：_collect_account_isolated（三线路循环）、_collect_account（图文跳过、口播稿批次） | ✅ 已改 |
| backend\app\services\multi_account\runner.py | 多账号调度+账号级重试（模块级 RETRY_MAX_ATTEMPTS 等） | ✅ 已改 |
| backend\app\services\multi_account\sync_firefox_login.py | 用户 Firefox 登录态同步到采集 profile + 导出 ytdlp_cookies.txt | ✅ 已改 |
| backend\app\services\multi_account\edge_cleanup.py | 浏览器进程清理（支持 -profile 参数匹配 Firefox） | ✅ 已改 |
| backend\app\providers\mediacrawler.py | MC 子进程启动、三引擎注入、[diag] 诊断日志 | ✅ 已改（含临时诊断日志） |
| backend\app\services\creator_profiles.py | 达人主页 hook 子进程（引擎注入） | ✅ 已改 |
| backend\app\services\transcription.py | 口播稿管线：优先 video_url、图文防御跳过 | ✅ 已改 |
| backend\app\services\plugin_routes.py | 下载线路：evil0ctal/f2/yt-dlp、HTML 嗅探 | ✅ 已改 |
| backend\app\config.py | BROWSER_ENGINE_CHAIN 三线路配置 | ✅ 已改 |
| backend\app\db.py | save_account_task 兼容 None profile；get_videos_for_transcription media_url 笔误修复 | ✅ 已改 |
| backend\app\services\export.py | 导出查询加 media_kind 列 | ✅ 已改 |
| MediaCrawler\config\base_config.py | BROWSER_ENGINE 默认 firefox-system；ENABLE_CDP_MODE 排除 firefox 系 | ✅ 已改 |
| MediaCrawler\media_platform\douyin\core.py | start() 重构 + firefox-system gecko 分支；launch_browser channel=firefox | ✅ 已改 |
| MediaCrawler\risk_browser_shim.py | firefox 系绕过 patchright（_ROUTE=""） | ✅ 已改 |
| MediaCrawler\tools\gecko_adapter.py | geckodriver 驱动系统 Firefox 的 Playwright 兼容适配器 | ✅ 已改 |
| deployments\miaoda-matrix-radar\shared\api.interface.ts | RadarVideoRow 加 mediaKind | ✅ 已改 |
| deployments\miaoda-matrix-radar\client\src\api\local-radar.ts | LocalVideo 类型加 mediaKind | ✅ 已改 |
| deployments\miaoda-matrix-radar\client\src\pages\DashboardPage\VideoDetailDialog.tsx | 图文显示"图文不采集" | ✅ 已改 |
| deployments\miaoda-matrix-radar\client\src\pages\DashboardPage\collection-task-visual.ts | 线路状态聚合判定（修"4条线路全挂"误显示） | ✅ 已改 |
| .env.local | 引擎链/cookie 文件路径等环境配置 | ✅ 已改（⚠️ 曾出反斜杠被吞事故） |
| start.ps1 | 启动脚本（Firefox 模式跳过克隆/9222） | ✅ 已改 |
| scripts\clone-browser-profiles.ps1 | B++++ 克隆（Edge 备用方案，51 账号已重建） | ✅ 完好 |
| data\radar.sqlite3 | 业务数据库（videos/comments/transcriptions 等） | 🔄 数据保留 |
| data\browser_data\ff_dy_user_data_dir | Firefox 采集 profile（含用户登录态） | ✅ 有效 |
| data\browser_data\cdp_dy_user_data_dir | Edge 共享源（用户已重新扫码） | ✅ 保留 |
| data\browser_data\cdp_<账号>_user_data_dir ×51 | Edge 克隆 profile（备用方案） | ✅ 已重建 |
| data\browser_data\ytdlp_cookies.txt | yt-dlp 下载用 cookie（Netscape 格式，176 条） | ✅ 有效 |

**关键代码片段（自包含）**：

backend\app\config.py（三线路配置）：
```python
BROWSER_ENGINE_CHAIN = [
    item.strip().lower()
    for item in os.getenv(
        "MEDIACRAWLER_BROWSER_ENGINE_CHAIN", "firefox-system,edge,chrome"
    ).split(",")
    if item.strip()
] or ["firefox-system"]
```

backend\app\services\transcription.py（图文跳过，process() 入口）：
```python
if str(video.get("media_kind") or "") == "image_text":
    return TranscriptionResult("skipped", error_code="image_text_skipped",
                               error_message="图文笔记无口播音频，跳过")
```

---

## 3. 已完成工作（全量清单）

### 模块一：三浏览器线路（Firefox 首选 → Edge → Chrome 兜底）
- **做了什么**：单线路失败自动切换下一线路；每条线路独立共享源目录。
- **产出物**：backend\app\config.py（链配置）、collection.py（循环）、providers\mediacrawler.py（引擎→目录映射）、MediaCrawler\media_platform\douyin\core.py（gecko 分支）。
- **怎么验证**：任务日志出现"共享源登录态：ff_dy_user_data_dir（引擎 firefox-system）"；失败时出现"切换到浏览器线路 2/3"。
- **关键数据**：线路目录映射 firefox-system→ff_dy_user_data_dir、edge→cdp_dy_user_data_dir、chrome→chrome_dy_user_data_dir。

### 模块二：系统 Firefox 驱动（geckodriver）
- **做了什么**：Playwright 无法驱动系统 Store 版 Firefox（无 Juggler 协议），改用 geckodriver(WebDriver) + Selenium 包装出 Playwright 兼容适配器。
- **产出物**：MediaCrawler\tools\gecko_adapter.py（find_system_firefox/launch_system_firefox/GeckoPage.evaluate 箭头函数归一化）。
- **怎么验证**：MediaCrawler\_adapter_e2e.py 输出 HasUserLogin: 1。
- **关键数据**：系统 Firefox 153.0.4 路径 C:\Program Files\WindowsApps\Mozilla.Firefox_153.0.4.0_x64__n80bbvh6b1yt2\VFS\ProgramFiles\Firefox Package Root\firefox.exe。

### 模块三：登录态同步（零扫码）
- **做了什么**：采集前把用户日常 Firefox（%APPDATA%\Mozilla\Firefox\Profiles\53w7d75e.default-release）的抖音登录态（cookies+localStorage）复制到采集 profile，并导出 yt-dlp 可用的 Netscape cookie 文件。
- **产出物**：sync_firefox_login.py；调用点 collection.py 任务启动后。
- **怎么验证**：任务日志"已同步用户 Firefox 登录态到采集 profile：cookies.sqlite, ytdlp_cookies.txt, …"。
- **关键数据**：176 条 douyin 系 cookie；关键登录 cookie（sessionid/sid_guard/uid_tt）全在。

### 模块四：口播稿下载修复（三个 bug）
- **做了什么**：①下载优先 video_url（作品页）而非 media_url 直链（三个 provider 都不支持直链，报 page_url_required）；②yt-dlp 注入登录 cookie；③下载文件 HTML 内容嗅探。
- **产出物**：transcription.py（URL 选择）、sync_firefox_login.py（cookie 导出）、plugin_routes.py::_new_media_file（HTML 嗅探）、db.py（media_url 笔误修复）。
- **怎么验证**：直接跑 yt-dlp 命令成功下载（95.7MB/190MB 实测）；provider 端到端下载 24MB/5.8s。
- **关键数据**：修复后单账号验证 1 条口播稿成功；第 4 轮累计 33 条成功。

### 模块五：图文跳过口播稿
- **做了什么**：图文笔记（aweme_type 2/163）跳过口播稿采集（三层防御），前端口播稿栏显示"图文不采集"。
- **产出物**：collection.py（两处跳过）、transcription.py（process 入口防御）、main.py/export.py（mediaKind API）、前端三文件（类型+展示）。
- **怎么验证**：前端打开图文视频详情，口播稿栏徽章和内容均显示"图文不采集"。

### 模块六：前端"线路全挂"误显示修复
- **做了什么**：collection-task-visual.ts 线路状态从"取最新单条 job 状态"改为聚合判定（有进行中→running；全成功→succeeded；全失败→failed；混合→partial），文案显示"成功 X 条，失败 Y 条（可补采）"。
- **怎么验证**：前端刷新后并行线路不再全红；混合线路显示部分完成。
- **关键数据**：真实数据为混合状态（如线路1：8 成功 + 7 失败）。

### 模块七：账号级失败重试
- **做了什么**：runner 内每账号失败重试最多 3 次（退避 5-10s），熔断跳过不重试不重复记账，风控/登录类信号仅重试 1 次 fail-fast。
- **产出物**：runner.py（RETRY_MAX_ATTEMPTS 模块级可配置）。
- **怎么验证**：全量 pytest 279 passed / 2 skipped。

### 模块八：Edge 备用方案恢复
- **做了什么**：误删 54 个 Edge 克隆 profile 后，用 clone-browser-profiles.ps1 -Force 从共享源重建 51/51；Edge 共享源（cdp_dy_user_data_dir）由用户重新扫码登录。
- **怎么验证**：data\browser_data 下 53 个目录（1 共享源 + 51 克隆 + ff_dy），克隆 Cookies 81920 bytes 与共享源一致。

### 模块九：测试与前端构建
- **做了什么**：后端全量测试零回归；前端 TypeScript 零错误并构建成功。
- **怎么验证**：pytest backend\tests -q → 279 passed, 2 skipped；前端 vite build 完成（28.49s）。

---

## 4. 当前精确进度

**最后一步有效操作**：通过 resume 接口恢复第 4 轮任务（a57a3049432441649211b27be6a909e0），客户端 _resume_run.py 在后台轮询。

**当前具体状态**：
- 后端运行中（端口 8000）
- 任务状态：running，current_account=老师好我叫何同学（第 5 个账号）
- 数据快照：videos≈61、comments≈1275、transcriptions=61（33 succeeded / 28 failed）、creators≥3
- 各账号：投哥不请自来 16、秋芝2046 15、九筒电话亭 15、小Lin说 15

**⚠️ 中断风险提示**：上一任对话结束时正在后台轮询。Codex 接手后**先跑进度查询**确认任务是否仍在运行。

---

## 5. A 没做完的事（接力棒，全量）

### 遗留 1：第 4 轮剩余 6 账号采集 【紧急】
- **还差什么**：老师好我叫何同学（进行中）、影视飓风、老方创业手册、心中之城、毒舌电影、疯狂小杨哥 的 15 条视频+评论+主页+口播稿。
- **为什么没做完**：任务运行中被上一任重启后端打断过一次（已 resume 恢复）；每账号约 20-25 分钟，10 账号串行总时长数小时，尚未跑完。
- **前置条件**：后端在线；三线路可用；Firefox 登录态有效。
- **做到什么算完成**：10 账号全部 status=completed，videos 表每账号 ≥15 条。
- **从哪开始**：查询任务 a57a3049… 状态；running 则继续等，paused/failed 则 POST resume。
- **验证信号**：select author_name,count(*) from videos group by author_name 出现全部 10 个账号。

### 遗留 2：28 条失败口播稿补采 【重要】
- **还差什么**：video_transcriptions 表 28 条 failed 记录的重转（历史网络抖动，当前线路已恢复）。
- **为什么没做完**：失败发生在约 1-2 小时前的网络抖动时段；线路修复后尚未统一补采。
- **前置条件**：第 4 轮任务结束（或至少新账号采完，避免并发争抢）。
- **做到什么算完成**：failed 数降到接近 0（允许偶发网络失败）。
- **从哪开始**：重跑失败视频的转录（resume 任务时 failed 记录会自动重试；或单独写补采脚本）。
- **验证信号**：select status,count(*) from video_transcriptions group by status 中 succeeded 占比显著上升。

### 遗留 3：Chrome 线路扫码实测 【重要】
- **还差什么**：chrome_dy_user_data_dir 尚无登录态；Chrome 线路作为最后兜底未实测。
- **为什么没做完**：Firefox 首选已够用，Chrome 线路优先级最低，未安排扫码。
- **前置条件**：用户在 Chrome 内核浏览器扫码一次（或从现有登录态导出 cookie）。
- **做到什么算完成**：三线路中 chrome 也能采集（日志"引擎 chromium"且 accepted>0）。
- **从哪开始**：参照 Edge 线路恢复流程；chrome 用 Playwright chromium 内核（data\browser_data\chrome_dy_user_data_dir）。
- **验证信号**：chrome 线路采集 accepted>0。

### 遗留 4：Edge 线路登录态恢复验证 【一般】
- **还差什么**：用户已在 Edge 共享源重新扫码，但扫码后未做 5 次独立测试确认"验证码中间页"消失。
- **为什么没做完**：扫码后立即转向第 4 轮测试，验证被搁置。
- **前置条件**：无（扫码已完成）。
- **做到什么算完成**：Edge 共享源打开抖音显示正常页面（非验证码中间页）。
- **从哪开始**：用 MediaCrawler\_edge_probe.py（playwright msedge + cdp_dy_user_data_dir）跑探测。
- **验证信号**：title 不是"验证码中间页"，HasUserLogin=1。

### 遗留 5：临时脚本与诊断日志清理 【一般】
- **还差什么**：项目根与 MediaCrawler 下一批 _*.py 临时脚本（_round10.py、_resume_run.py、_p5.py、_p6.py、_diag*.py、_fix*.py、_patch*.py、_kill*.py、_probe*.py 等）以及 providers\mediacrawler.py 里的 [diag] MC child env 诊断日志待清理。
- **为什么没做完**：测试还在进行，脚本正在使用；诊断日志用于排障暂未移除。
- **前置条件**：⚠️ **删除任何文件前必须先向用户确认**（上一任曾误删 54 个 Edge 克隆 profile 造成事故——永久删除无法恢复）。
- **做到什么算完成**：临时脚本清理完毕；[diag] 日志行移除后全量 pytest 仍 279/2。
- **从哪开始**：先列清单给用户确认，再删。
- **验证信号**：pytest 零回归。

### 遗留 6：前端 vitest 测试环境修复 【一般】
- **还差什么**：collection-task-visual.spec.ts 跑不起来（describe is not defined，vitest 环境配置问题，非本次代码改动导致）。
- **为什么没做完**：不影响构建（vite build 成功），优先级低。
- **前置条件**：无。
- **做到什么算完成**：vitest 能跑通该 spec。
- **从哪开始**：检查 vitest 配置（globals: true 或 import { describe } from 'vitest'）。
- **验证信号**：npx vitest run 该 spec 通过。

---

## 6. A→B 接力总览表

| # | A 没做完的（接力棒） | Codex 要做什么 | 从哪开始（关键内容） | 做到什么算完成 |
|---|---|---|---|---|
| 1 | 第 4 轮剩余 6 账号未采 | 继续第 4 轮任务至 10 账号全完成 | 查任务：GET http://127.0.0.1:8000/api/collections/a57a3049432441649211b27be6a909e0；paused 则 POST /api/collections/<id>/resume；running 则等待（轮询脚本 _resume_run.py 已存在，可直接复用） | 用户代跑：python _p6.py 看到 10 个账号各 ≥15 条视频 |
| 2 | 28 条口播稿 failed 待补采 | 任务跑完后补采失败口播稿 | failed 记录在 video_transcriptions 表（status='failed'）；resume 会重试 failed，或单独写补采脚本遍历 failed 的 video_id 重新走转录管线 | 用户代跑：select status,count(*) from video_transcriptions group by status 中 failed 接近 0 |
| 3 | Chrome 线路未实测 | 给 Chrome 线路准备登录态并实测 | chrome 线路 = Playwright chromium 内核 + data\browser_data\chrome_dy_user_data_dir；参照 Edge 恢复流程（打开浏览器扫码或导出 cookie） | 用户代跑：强制 chrome 线路采集 accepted>0 |
| 4 | Edge 线路扫码后未验证 | 跑 5 次探测确认验证码页消失 | 复用 MediaCrawler\_edge_probe.py（playwright msedge + cdp_dy_user_data_dir） | 用户代跑：title 非"验证码中间页" |
| 5 | 临时脚本+诊断日志待清理 | 列清单→用户确认→清理 | 清单：项目根/MediaCrawler 下 _*.py；providers\mediacrawler.py 的 [diag] MC child env 日志块 | 用户代跑：pytest 279/2 零回归 |
| 6 | 前端 vitest spec 环境问题 | 修 vitest 配置跑通 spec | deployments\miaoda-matrix-radar 下 vitest 配置（globals 选项） | 用户代跑：npx vitest run spec 通过 |

**接力开工第一步**：Codex 先执行
```
python -c "import json,urllib.request; r=json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/collections/a57a3049432441649211b27be6a909e0',timeout=15).read().decode()); print(r['status'], r['stage'], r.get('current_account'))"
```
看到 running + 当前账号名 = 正式接上；看到 paused = 先跑 resume；看到后端拒绝连接 = 先重启后端（见第 12 节）。

---

## 7. 下一步行动计划（命令级）

### 立即做

**步骤 1：验证后端在线**
```powershell
Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 5
```
预期：HTTP 200 + JSON（含 accounts=51）。

**步骤 2：查第 4 轮任务状态**
```powershell
cd 'D:\全自动爬取短视频、推文爆款程序'
.\.venv\Scripts\python.exe _p6.py
```
预期输出：TASK 行显示 status/running 或 paused + current_account。
- running → 跳到步骤 4 持续监控
- paused → 步骤 3 resume
- 后端没跑 → 第 12 节重启后端后再查

**步骤 3：resume 任务（仅 paused 时）**
```powershell
cd 'D:\全自动爬取短视频、推文爆款程序'
.\\.venv\Scripts\python.exe _resume_run.py
```
预期：resume: 200，随后每 15s 打印任务状态；任务从断点继续（已采账号重采会去重）。

**步骤 4：持续监控至任务终态**
每隔几分钟跑 _p6.py，重点看：
- videos= 增长（每新账号 +15）
- 日志出现"导入 15 条作品数据"
- 最终 status=completed

**步骤 5：任务完成后补采失败口播稿（遗留 2）**
写补采脚本：查 video_transcriptions 中 failed 的 video_id_fk → 对应 videos 行 → 重新调转录管线。或直接重跑一次仅转录模式任务（content_mode='transcript'）覆盖失败视频。

### 之后做
- 遗留 3/4：Chrome 扫码实测、Edge 5 次探测验证
- 遗留 5：临时文件清理（⚠️ 先问用户）
- 遗留 6：vitest 配置修复

---

## 8. 环境与配置依赖

**服务与端口**：
| 服务 | 端口 | 说明 |
|---|---|---|
| 后端 FastAPI | 8000 | uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 |
| GPU ASR（faster-whisper） | 8765 | 口播稿转写 |
| evil0ctal API | 18081 | 下载线路 route1 |

**Python 环境**：
- 后端：.venv\Scripts\python.exe（项目根）
- MediaCrawler：MediaCrawler\.venv\Scripts\python.exe（playwright 1.62 + patchright 1.61.2 + selenium 4.47.0）

**浏览器**：
- 系统 Firefox 153.0.4（Store 版）：C:\Program Files\WindowsApps\Mozilla.Firefox_153.0.4.0_x64__n80bbvh6b1yt2\VFS\ProgramFiles\Firefox Package Root\firefox.exe
- Playwright Firefox 内核 firefox-1538：MediaCrawler\.playwright-browsers\firefox-1538
- Edge 151.0.4129.86：C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe

**关键环境变量**（.env.local）：
```
MEDIACRAWLER_BROWSER_ENGINE_CHAIN=firefox-system,edge,chrome
MEDIACRAWLER_BROWSER_ENGINE=firefox-system
YTDLP_COOKIE_FILE=D:\全自动爬取短视频、推文爆款程序\data\browser_data\ytdlp_cookies.txt
MEDIACRAWLER_BROWSER_DATA_DIR=D:\全自动爬取短视频、推文爆款程序\data\browser_data
MEDIACRAWLER_LOGIN_CHECK_ATTEMPTS=25
MEDIACRAWLER_LOGIN_SETTLE_SECONDS=2
MEDIACRAWLER_LOGIN_REDIRECT_SECONDS=2
MEDIACRAWLER_SKIP_QRCODE_DISPLAY=1
```

**⚠️ 启动后端时必须先加载 .env.local**（用 start.ps1 或手动 foreach 注入），否则 MC 子进程拿不到引擎配置。

**密钥/token**：SPIDERHUBS_API_KEY、SYNC_TOKEN、MIAODA_API_KEY 等存于 .env.local，值为 <已脱敏>，勿外传。

---

## 9. 数据与状态快照

- data\radar.sqlite3：业务数据（**保留，不清**）。当前 videos≈61、comments≈1275、transcriptions=61、creators≥3。
- data\browser_data\：登录态目录（**保留**）。ff_dy（Firefox 采集用）、cdp_dy（Edge 共享源）、cdp_*×51（Edge 克隆备用）、ytdlp_cookies.txt。
- MediaCrawler\database\：MC 各账号采集库（临时，MC 启动重建）。
- 残留进程：⚠️ 重启后端后建议先清理残留（MC python 子进程/geckodriver/采集 Firefox），否则会争抢 profile 锁导致新任务卡死。清理脚本 _cleanup_all.py 只杀采集特征进程（用户日常 Firefox 的 -osint 特征进程绝不触碰）。

**保留清单**：以上全部保留。临时脚本（_*.py）清理前必须问用户。

---

## 10. 关键决策与踩坑记录

| 决策/踩坑 | 内容 | 影响与规避 |
|---|---|---|
| 弃用 B++++ 克隆方案 | 同一登录态多 profile 轮番使用触发抖音服务端会话互斥踢出，本地"有登录态"是假象 | 回退共享源单会话（P0）；Edge 克隆仅作备用 |
| Playwright 无法驱动系统 Firefox | Store 版无 Juggler 自动化协议 | 改用 geckodriver（WebDriver 标准协议） |
| patchright 不支持 Firefox | stealth 注入报 _client undefined | firefox 系绕过 shim（_ROUTE=""） |
| shim 判断 == "firefox" 漏 firefox-system | 导致 patchright 仍加载、走 CDP 分支 | 改 in ("firefox","firefox-system") |
| base_config != "firefox" 使 firefox-system 误开 CDP | 走 Edge/patchright 报 TargetClosedError | 改 not in ("firefox","firefox-system") |
| collection.py 相对导入多一个点 | from ...config import ImportError | 改 from ..config import |
| 残留进程堆积 | 9 MC+5 geckodriver+12 Firefox 争抢 profile 锁，任务卡 15 分钟 | 重启后先清残留进程 |
| yt-dlp 需登录 cookie | "Fresh cookies needed" | 从用户 Firefox 导出 Netscape 格式 cookie |
| media_url 直链三 provider 都不支持 | page_url_required 全部失败 | 下载优先 video_url（作品页） |
| db.py media_url 误赋 video_url | 字段错位 | 修复笔误 |
| .env.local 反斜杠被 edit 吞掉 | YTDLP_COOKIE_FILE 路径损坏 | 用 Python 脚本逐行修复；改 env 后全文件扫描 |
| 误删 54 个 Edge 克隆 profile | Remove-Item 永久删除无法恢复 | **铁律：删除前必须问用户**；已用克隆脚本重建 51/51 |
| 测试 mock iter() 与三线路循环冲突 | 循环多调 provider 耗尽 iter | autouse fixture 把 BROWSER_ENGINE_CHAIN 固定单元素 |
| Selenium 无 return 前缀不执行 JS | evaluate 返回 None | 箭头函数归一化为 return 语句 |
| FirefoxProfile 复制丢 localStorage | HasUserLogin=None | 用 -profile 参数直接指向目录 |
| WindowsApps Python 无法 listdir | PermissionError | 用 PowerShell Appx 查询定位 Store 版路径 |

---

## 11. 风险与待确认项

- ❓ 上一任结束时的后台 job（后端 / resume 轮询）在 Codex 接手时是否仍在运行？需先按第 7 节步骤 1-2 验证。
- ❓ Edge 共享源重新扫码后，服务端会话是否真正恢复（未做 5 次探测验证）？
- ❓ Chrome 线路登录态如何获得（用户扫码 or 从 ff_dy 导出 cookie 转换格式）？Chrome 是 chromium 内核，cookie 格式与 Firefox 不同，不能直接复用 ytdlp_cookies.txt。
- ❓ 28 条失败口播稿中"不支持的媒体类型 text/html"部分，是否全部是网络抖动导致，还是个别视频本身被限制？
- ❓ _resume_run.py 的 max_wait=10800s（3 小时）是否够跑完剩余 6 账号（每账号 20-25 分钟，约 2-2.5 小时，应够但边际小）？

---

## 12. 续作启动手册（从零恢复完整步骤）

1. **清理残留进程**（防 profile 锁）：
```powershell
cd 'D:\全自动爬取短视频、推文爆款程序'
.\.venv\Scripts\python.exe _cleanup_all.py
```
预期：mc_python/geckodriver/firefox 各 killed N 个（用户日常 Firefox 不动）。

2. **启动后端**：
```powershell
cd 'D:\全自动爬取短视频、推文爆款程序'
$root = (Get-Location).Path
foreach ($line in Get-Content -LiteralPath '.env.local' -Encoding UTF8) {
  $t = $line.Trim()
  if (-not $t -or $t.StartsWith('#') -or -not $t.Contains('=')) { continue }
  $parts = $t.Split('=', 2)
  [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
}
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

3. **验证续上了**：请用户代跑
```powershell
Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing
```
看到 HTTP 200 + accounts=51 即成功。

4. **继续第 4 轮**：按第 7 节步骤 2-4 查询/resume/监控。

---

## 13. 按 Codex 定制的附加内容

- **无第三方模型 API 配置**：项目用本地 ASR（faster-whisper @8765）+ yt-dlp/f2/evil0ctal 下载。
- **外网访问**：yt-dlp 下载视频需要能访问 douyin.com/CDN（当前网络环境已验证可达）；ASR 模型已缓存于 D:\全自动爬取短视频、推文爆款程序\models\hf_cache（env 变量 HF_HOME 已指向）。
- **跨机迁移提示**：本项目单机运行（Windows），浏览器登录态在 data\browser_data 各 profile 目录；换机器需重新扫码登录。
- **代理**：RISK_PROXY_ENABLED=false（当前直连）。

---

## 遗留不确定项（❓）汇总

1. ❓ 后台 job（后端/resume 轮询）在 Codex 接手时的存活状态
2. ❓ Edge 扫码后服务端会话是否已恢复（未验证）
3. ❓ Chrome 线路登录态获取方式
4. ❓ 28 条失败口播稿中 HTML 类失败的根因分布（网络抖动 vs 视频限制）
5. ❓ _resume_run.py 3 小时超时是否够剩余 6 账号跑完

## 请用户核对的清单

1. 请确认：D:\全自动爬取短视频、推文爆款程序\data\radar.sqlite3 数据是否**保留不清**（交接要求）
2. 请代跑：Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing 是否返回 200
3. 请代跑：cd 'D:\全自动爬取短视频、推文爆款程序'; .\.venv\Scripts\python.exe _p6.py 查看任务状态输出并告知
4. 请确认：临时脚本清理清单（_round10.py、_resume_run.py、_p*.py、_diag*.py、_fix*.py、_patch*.py、_kill*.py、_probe*.py、_check*.py、_export_cookies.py、_cleanup_all.py、_ff_e2e.py、_e2e_dl*.py、_yt_*.py、_edge_5rounds.py、_adapter_e2e.py 等）是否同意在第 4 轮完成后清理
5. 请确认：providers\mediacrawler.py 中的 [diag] MC child env 诊断日志是否同意移除
6. 请确认：Chrome 线路（第三兜底）是否需要现在准备登录态，还是暂时只保 Firefox+Edge 两线路
