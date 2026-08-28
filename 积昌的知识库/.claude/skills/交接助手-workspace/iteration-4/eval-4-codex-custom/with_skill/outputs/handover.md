# 短视频爬虫项目 交接文档（给 Codex 版）

> **目标智能体：Codex（OpenAI 智能体）｜能力层级：L1 自治型**
> **交接人（A）**：DeepSeek（DeepSeek Harness 阶段）｜**接手人（B）**：Codex
> **交接日期**：2026-08-18
> **一句话定位**：抖音短视频去水印下载 CLI 工具——粘贴分享链接 → 抓取元数据 → 去水印 → 下载无水印视频 → 落 SQLite。单条链路已跑通，批量/重试/代理/导出未完成。
> **交接方式**：模式 B（给 AI 看），非通用模板，按 Codex 习性档案（`references/agent-profiles.md` §2）从零定制。

---

## 0. 交接摘要（启动包）

- **项目在做什么**：`short_video_spider`，抖音短视频抓取+去水印+下载+入库的本地 CLI 工具，单条下载全链路已通。
- **已完成到什么程度**：核心抓取/去水印/存储/单条 CLI/测试全部完成，**15 条单测全绿，SQLite 已存 128 条记录，实测下载 3 个无水印视频成功**。
- **A 没做完的（接力棒，你要接的活）**：① 批量调度（`core/batch.py` 是空壳）② 失败重试与断点续爬 ③ 代理池/反爬 ④ 数据导出 ⑤ 风控/验证码提示。
- **B（你）下一步第一件事**：先环境还原（§12），确认 `pytest 15 passed`；再按接力总览 #1 从 `core/batch.py::BatchRunner.run()`（第 22 行）开工。
- **从哪继续最省力**：环境已就绪、数据库已有真实数据、单条链路稳定——你不需要重写任何已存在的东西，直接给 `BatchRunner.run()` 填空即可。

---

## 1. 项目总览与验收标准

- **一句话定位**：输入一条抖音分享链接，命令行输出无水印 MP4 并存入本地 SQLite，可离线回溯。
- **最终目标**：支持「批量下载」——读一个 urls.txt，并发抓取+去水印+下载+入库，失败自动重试，数据可导出 CSV。
- **验收标准（做到什么算整体完成）**：
  1. `python cli.py batch .\urls.txt --concurrency 5` 能并发跑完 100+ 条不崩、不重复入库；
  2. 中途断网后恢复，任务自动重试补齐，不丢条；
  3. 单测全绿（`pytest` 无 `FAILED`）；
  4. `python cli.py export --format csv` 导出的行数 = SQLite 记录数。

---

## 2. 文件地图（精确路径）

> 项目根目录：`D:\projects\short_video_spider`（Codex 可直接读文件，只给路径+作用+状态即可；关键文件再给函数级定位）

| 路径 | 作用 | 状态 |
|------|------|------|
| `D:\projects\short_video_spider\cli.py` | 命令行入口（click），含 `download` 子命令 | ✅ 已完成 |
| `D:\projects\short_video_spider\core\fetcher.py` | 核心抓取：`fetch_video(url)` → `VideoMeta` | ✅ 已完成（待加重试） |
| `D:\projects\short_video_spider\core\watermark.py` | 去水印：`strip_watermark(play_url)` → 无水印直链 | ✅ 已完成 |
| `D:\projects\short_video_spider\core\batch.py` | 批量调度：`BatchRunner` 类 | 🔶 空壳骨架（`run()` 第 22 行为空） |
| `D:\projects\short_video_spider\core\proxy.py` | 代理池：`get_proxy()` | 🔶 占位（第 8 行返回 None） |
| `D:\projects\short_video_spider\models\video.py` | 数据类 `VideoMeta` / `Video` | ✅ 已完成 |
| `D:\projects\short_video_spider\storage\sqlite_store.py` | SQLite 存储：`save_video`/`get_video`/`stats` | ✅ 已完成 |
| `D:\projects\short_video_spider\storage\exporter.py` | CSV/Excel 导出 | ❌ 不存在（需新建） |
| `D:\projects\short_video_spider\config\settings.py` | 常量配置（DB 路径、输出目录、UA） | ✅ 已完成 |
| `D:\projects\short_video_spider\config\.env.example` | 环境变量模板（含可选 PROXY_LIST） | ✅ 已完成 |
| `D:\projects\short_video_spider\tests\` | `test_fetcher.py`/`test_watermark.py`/`test_store.py` | ✅ 15 条用例全绿 |
| `D:\projects\short_video_spider\data\spider.db` | SQLite 数据库（128 条已抓元数据） | ✅ 有真实数据 |
| `D:\projects\short_video_spider\output\` | 下载输出目录（已含 3 个无水印 mp4） | ✅ 已产出 |
| `D:\projects\short_video_spider\requirements.txt` | 依赖：`requests`、`click`、`pytest` | ✅ 已完成 |
| `D:\projects\short_video_spider\README.md` | 使用说明 | 🔶 只写了单条用法，未写 batch/export |

**入口文件**：`cli.py`（所有子命令从这里进）。
**关键函数定位**：`core/fetcher.py::fetch_video`（第 45 行）、`core/watermark.py::strip_watermark`（第 12 行）、`storage/sqlite_store.py::save_video`（第 30 行）、`core/batch.py::BatchRunner.run`（第 22 行，空）。

---

## 3. 已完成工作（全量逐条）

> 每条含：做了什么 / 产出物路径 / 怎么验证有效 / 关键数据。

### 3.1 核心抓取 `core/fetcher.py`
- **做了什么**：`fetch_video(url)` 实现——解析分享文案 → 提取视频 ID → 请求抖音接口 → 返回 `VideoMeta`（id/title/author/play_url/cover_url/source/fetched_at）。
- **产出物**：`core/fetcher.py`（`fetch_video` 在第 45 行）。
- **怎么验证**：`python -c "from core.fetcher import fetch_video; print(fetch_video('https://v.douyin.com/<分享码>/'))"` 输出完整 VideoMeta JSON。
- **关键数据**：单条链路实测成功解析 **128 条**分享链接，接口返回结构稳定。

### 3.2 去水印 `core/watermark.py`
- **做了什么**：`strip_watermark(play_url)` 把带水印播放地址改写为无水印直链（基于 watermark_type/url 参数替换逻辑）。
- **产出物**：`core/watermark.py`（函数在第 12 行）。
- **怎么验证**：用 3.1 拿到的直链下载，`ffprobe -v error -show_entries stream_tags=title -of default=noprint_wrappers=1 "输出文件"` 或人工播放确认无播放水印。
- **关键数据**：**3/3** 视频下载后无水印。

### 3.3 数据模型 `models/video.py`
- **做了什么**：定义 `VideoMeta`（元数据）与 `Video`（meta + local_path + status）两个 dataclass。
- **产出物**：`models/video.py`。
- **怎么验证**：`pytest tests/test_store.py` 覆盖字段与序列化，全绿。
- **关键数据**：字段 8 个，覆盖抓取+下载全链路所需字段。

### 3.4 SQLite 存储 `storage/sqlite_store.py`
- **做了什么**：`save_video()`（按 video_id 幂等去重）、`get_video()`、`stats()`。
- **产出物**：`storage/sqlite_store.py`（`save_video` 在第 30 行）。
- **怎么验证**：`python -c "from storage.sqlite_store import stats; print(stats())"` 返回 `{'total': 128, ...}`；重复 `save_video` 同一条记录不新增行。
- **关键数据**：`data/spider.db` 已有 **128 条**元数据，无重复。

### 3.5 单条下载 CLI `cli.py`
- **做了什么**：`python cli.py download <url>` 串起 抓取→去水印→下载→入库 全链路，下载到 `output/`。
- **产出物**：`cli.py`（`download` 命令）。
- **怎么验证**：`python cli.py download "https://v.douyin.com/<分享码>/"` 结束出现 `已保存: output/<id>.mp4`，且 `stats()` 计数 +1。
- **关键数据**：实测下载 **3 个** mp4 成功落盘。

### 3.6 测试 `tests/`
- **做了什么**：3 个测试文件覆盖抓取解析、去水印改写、存储幂等。
- **产出物**：`tests/test_fetcher.py`、`test_watermark.py`、`test_store.py`。
- **怎么验证**：`.\.venv\Scripts\python.exe -m pytest -q` → `15 passed`。
- **关键数据**：**15/15 通过**。

---

## 4. 当前精确进度

- **最后一步有效操作**：`python cli.py download "https://v.douyin.com/<某条实测链接>/"` 成功下载第 3 个视频并落库，`data/spider.db` 计数到 **128**。
- **当前代码状态**：单条链路闭环、测试全绿；`core/batch.py` 的 `BatchRunner` 只有类声明与注释（`run()` 第 22 行为 `pass`）；`core/proxy.py::get_proxy` 第 8 行直接 `return None`；`storage/exporter.py` **不存在**。
- **当前数据状态**：`data/spider.db` 128 条元数据；`output/` 3 个无水印 mp4；`data/spider.db` 无失败/重试状态字段。
- **还没动的部分**：batch 调度、重试、代理池、导出、风控提示、README 的 batch 文档。

---

## 5. A 没做完的事（接力棒，全量逐条）

> 以下每条都是你（B）要接的活，是 A 留给你的接力棒——不是你造成的欠账，而是继续前进的起点。

### 接力棒 #1：批量调度（`core/batch.py`）
- **还差什么**：`BatchRunner` 无并发控制、无任务队列、无进度日志、无去重跳过（已抓过的 video_id 应跳过）。
- **为什么没做完**：DeepSeek 阶段只聚焦打通单条链路，批量是明确的下一个里程碑，尚未动工。
- **前置条件**：单条链路稳定（✅ 已满足）；需要从 `data/spider.db` 判断哪些 video_id 已抓过（用 `get_video()` 现成接口）。
- **优先级**：重要（下一个里程碑核心）。
- **做到什么算完成**：`python cli.py batch .\urls.txt --concurrency 5` 能并发下载全部 urls 且不重复入库；进度日志逐条可见。
- **从哪开始**：`core/batch.py::BatchRunner.run`（第 22 行）。
- **验证信号**：批量跑完日志出现 `全部完成: N 成功 / M 失败`，`stats()` 计数增加量 = 新抓条数。

### 接力棒 #2：失败重试与断点续爬（`core/fetcher.py`）
- **还差什么**：`fetch_video` 无重试；网络抖动即抛异常；数据库无失败状态字段，无法续爬。
- **为什么没做完**：单条场景不触发，批量场景（#1）必须依赖重试。
- **前置条件**：接入批量调度（#1）后再做，或并行做。
- **优先级**：重要（批量可用性的前提）。
- **做到什么算完成**：断网-恢复场景下 `fetch_video` 自动重试 3 次（指数退避）最终成功；失败条在库里标记 `status='failed'`。
- **从哪开始**：`core/fetcher.py::fetch_video`（第 45 行）外层包重试装饰器/循环。
- **验证信号**：手动断网跑单条，恢复后日志出现 `第 2 次重试...` 并成功返回；`sqlite_store` 增加 status 字段查询。

### 接力棒 #3：代理池 / 反爬（`core/proxy.py`）
- **还差什么**：`get_proxy()` 返回 None，无代理列表读取、无轮询、无失效剔除。
- **为什么没做完**：本地直连够用，尚未触发风控阈值。
- **前置条件**：无（可独立做）。
- **优先级**：一般（触发 429/风控时再启用）。
- **做到什么算完成**：从环境变量 `PROXY_LIST`（逗号分隔）读入代理，轮询返回；失效代理自动剔除；批量跑不报 429。
- **从哪开始**：`core/proxy.py::get_proxy`（第 8 行）。
- **验证信号**：日志打印 `使用代理: http://<ip>:<port>`，批量请求状态码全 200。

### 接力棒 #4：数据导出（`storage/exporter.py`）
- **还差什么**：整个文件不存在；`cli.py` 无 `export` 子命令。
- **为什么没做完**：用户未要求，属加分项。
- **前置条件**：批量跑通后数据才有导出价值（也可先做）。
- **优先级**：一般。
- **做到什么算完成**：`python cli.py export --format csv` 生成 `output/spider.csv`，行数 = `stats()['total']`。
- **从哪开始**：新建 `storage/exporter.py`；在 `cli.py` 注册 `export` 命令。
- **验证信号**：CSV 首行表头 `id,title,author,play_url,local_path,fetched_at`，行数与 db 一致。

### 接力棒 #5：风控 / 验证码提示（`core/fetcher.py`）
- **还差什么**：遇滑块/验证码响应时静默失败，无人工介入提示。
- **为什么没做完**：单条低频未触发。
- **前置条件**：无。
- **优先级**：一般（触发才做）。
- **做到什么算完成**：识别风控响应（状态码/内容特征），日志明确输出 `需人工验证: <url>` 并记录 `status='blocked'`，不静默吞错。
- **从哪开始**：`core/fetcher.py` 异常处理分支（当前 `except` 在第 60 行附近）。
- **验证信号**：构造风控响应 mock，日志出现 `需人工验证` 且任务不中断。

---

## 6. A→B 接力总览（读到就能开工，核心）

> 每条「A 没做完的」对应一条「B 要做的」，入口列全部给 **PowerShell 命令 + 函数级定位**，验证列给 **Codex 可直接执行的判定信号**。

| # | A 没做完的（接力棒） | B（Codex）要做什么 | 从哪开始（PowerShell 命令 + 函数级定位） | 做到什么算完成（验证信号） |
|---|--------------------|-------------------|----------------------------------------|---------------------------|
| 1 | 批量调度空壳 | 实现 `BatchRunner.run()`：并发下载 + 去重跳过 + 进度日志 | `core\batch.py::BatchRunner.run`（第 22 行）；在 `cli.py` 加 `batch` 子命令；完成后跑 `cd D:\projects\short_video_spider; .\.venv\Scripts\python.exe cli.py batch .\urls.txt --concurrency 5` | 日志出现 `全部完成: N 成功 / M 失败`；`stats()` 计数增加 = 新抓条数 |
| 2 | 无失败重试/断点续爬 | 给 `fetch_video` 加指数退避重试（3 次）；db 加 `status` 字段 | `core\fetcher.py::fetch_video`（第 45 行）外层包重试；`storage\sqlite_store.py` 加 status 字段；跑 `.\.venv\Scripts\python.exe -m pytest -q` | 断网-恢复日志出现 `第 2 次重试...` 最终成功；pytest 全绿 |
| 3 | 代理池占位 | 读 `PROXY_LIST` 环境变量，轮询返回代理，失效剔除 | `core\proxy.py::get_proxy`（第 8 行）；设 `$env:PROXY_LIST="http://a:1,http://b:2"` 后跑单条下载 | 日志打印 `使用代理: http://<ip>:<port>`；请求状态码全 200 |
| 4 | 导出未实现 | 新建 `storage\exporter.py`，在 `cli.py` 加 `export` 子命令 | 新建 `storage\exporter.py`；`cli.py` 注册 `export`；跑 `python cli.py export --format csv` | 生成 `output\spider.csv`，行数 = `stats()['total']`（128） |
| 5 | 风控静默失败 | 识别风控响应并输出 `需人工验证`，标记 `status='blocked'` | `core\fetcher.py` 的 `except` 分支（第 60 行附近） | mock 风控响应后日志出现 `需人工验证: <url>` 且任务不中断 |

> **🎯 接力开工第一步**：在 PowerShell 执行：
> `cd D:\projects\short_video_spider; .\.venv\Scripts\python.exe -m pytest -q`
> 看到 **`15 passed`** → 环境已接上，可直接按 #1 从 `core\batch.py::BatchRunner.run()` 动工。若 pytest 报依赖缺失，先跑 `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` 再重试。

---

## 7. 下一步行动计划（命令级）

> 按优先级分「立即做 / 之后做」。每条给可执行命令与预期产出。

### 立即做

**Step 1 — 环境确认（5 分钟）**
1. `cd D:\projects\short_video_spider`
2. `.\.venv\Scripts\python.exe -m pytest -q`
3. 预期：`15 passed in 0.xx s`。
4. 若报 `ModuleNotFoundError` → `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` 后重跑。
5. ✅ 通过 = 环境接上。

**Step 2 — 实现批量调度（接力棒 #1）**
1. 打开 `core\batch.py`，读 `BatchRunner` 现有骨架（`run()` 第 22 行）。
2. 实现：读入 urls.txt → 用 `concurrent.futures.ThreadPoolExecutor(max_workers=concurrency)` 并发调 `fetch_video` → `save_video` → 下载到 `output/`；每条开头先 `get_video(video_id)` 判重跳过。
3. 在 `cli.py` 注册 `batch` 子命令（参考已有 `download` 命令写法，第 40 行附近）。
4. 验证：`python cli.py batch .\urls.txt --concurrency 5`。
5. 预期信号：逐条进度日志 → 结尾 `全部完成: N 成功 / M 失败`；重复跑同批 urls 不新增 db 记录。

**Step 3 — 失败重试（接力棒 #2）**
1. 在 `core\fetcher.py` 给 `fetch_video` 外层加重试循环（3 次，`time.sleep(2 ** attempt)` 指数退避）。
2. 在 `storage\sqlite_store.py` 的建表 DDL 加 `status TEXT DEFAULT 'done'`；`save_video` 增加 status 参数。
3. 验证：跑 `.\.venv\Scripts\python.exe -m pytest -q`，并手动断网-恢复跑单条，日志出现 `第 2 次重试...`。
4. 预期信号：pytest 全绿；断网恢复后最终成功。

### 之后做

**Step 4 — 代理池（接力棒 #3）**：`core\proxy.py::get_proxy` 读 `$env:PROXY_LIST` 轮询返回。
**Step 5 — 导出（接力棒 #4）**：新建 `storage\exporter.py` + `cli.py export` 子命令，输出 `output\spider.csv`。
**Step 6 — 风控提示（接力棒 #5）**：`core\fetcher.py` 识别风控响应输出 `需人工验证`。

---

## 8. 环境与配置依赖（完整清单）

- **Python**：3.11（`.venv` 虚拟环境，路径 `D:\projects\short_video_spider\.venv`）。
- **依赖库**：`requests`、`click`、`pytest`（见 `requirements.txt`）。
- **DB**：SQLite，文件 `data\spider.db`（无需单独安装）。
- **环境变量**：
  - `PROXY_LIST`（可选，逗号分隔代理列表，供 #3 使用）——**当前未设置**，值脱敏为 `<未设置>`。
  - `DOUYIN_COOKIE`（可选，登录 cookie，用于高优先级抓取）——**当前未设置**，值脱敏为 `<未设置>`。
- **网络/代理注意（Codex 特有）**：抖音为国内服务，**直连即可**。若你的 Codex 环境开了全局代理，需把 `*.douyin.com` 加入直连白名单，否则抓取会超时/被风控。
- **Codex 模型配置（config.toml）**：⚠️ 若你（Codex）之前的 `C:\Users\asus\.codex\config.toml` 被配置过第三方模型（如 deepseek 供应商），接续本项目前确认当前模型可用——否则启动即报 `model_not_found`。若不确定，❓ 打开该文件核对 `model` 字段，并确认对应 API key 有效（密钥脱敏，不在此文档记录）。
- **会话迁移说明（Codex 特有）**：若需跨机/跨账号迁移，只拷会话文件 `C:\Users\asus\.codex\sessions\*.jsonl`，**不要拷 `auth.json`**（含登录凭证）。

---

## 9. 数据与状态快照

- **`data\spider.db`**：128 条已抓元数据，字段 `id,title,author,play_url,cover_url,source,fetched_at`；**无 status 字段**（#2 需加）。
- **`output\`**：3 个无水印 mp4（命名 `<video_id>.mp4`）。
- **`output\` 与 db 的关系**：`local_path` 尚未回填 db（`Video.local_path` 字段存在但批量回填未做）——❓ 接续时确认是否需要回填。
- **测试数据**：`tests\` 用 mock 响应，无真实请求，无需清理。
- **临时产物**：无。

---

## 10. 关键决策与踩坑记录

- **选型：requests + click + SQLite**。理由：零框架、单文件可读、SQLite 免运维，适合本地小工具。**不要中途引入 scrapy**（重、学习成本高，当前规模不划算）。
- **去水印实现**：改写播放地址参数而非调第三方 API——免费、稳定、不依赖外部服务。坑：抖音接口偶发返回签名参数变化，`fetch_video` 对返回结构做了宽容解析（缺字段给默认值）。
- **幂等入库**：`save_video` 按 video_id 去重，避免批量重复抓取写脏数据——批量调度必须复用这个接口。
- **踩坑：接口频率限制**。短时间高频请求会返回 风控/滑块 响应。当前单条场景没事，批量场景务必接 #3 代理 + #2 重试。
- **放弃的方案**：早期试过 selenium 渲染抓取，太慢且被检测率高，已弃，改用纯 requests 解析分享文案。

---

## 11. 风险与待确认项

- ❓ **`C:\Users\asus\.codex\config.toml` 当前模型配置**：不确定是否仍为可用模型，接续前核对。
- ❓ **`data\spider.db` 中 128 条是否包含已下载的 3 条**：`local_path` 字段当前可能为空，批量前确认是否需要回填路径。
- ❓ **`output\spider.csv` 导出的确切列**：字段建议 `id,title,author,play_url,local_path,fetched_at`，若用户有额外要求再调。
- ⚠️ **风控风险**：批量高频抓取可能触发验证码，属预期内（#5）。
- ⚠️ **PROXY_LIST 未设置**：若直连稳定，可暂缓 #3。

---

## 12. 续作启动手册（环境还原 + 如何验证「续上了」）

> 第 6 节是「开工清单」（接 A 的活），本节是「环境还原」（把 A 的环境跑起来）。**先还原环境，再开工。**

**从零恢复步骤：**
1. `cd D:\projects\short_video_spider`
2. 若 `.venv` 不存在：`python -m venv .venv`，然后 `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
3. 跑测试确认环境健康：`.\.venv\Scripts\python.exe -m pytest -q`
4. 跑一次真实单条链路确认全链路可用：
   `.\.venv\Scripts\python.exe cli.py download "https://v.douyin.com/<取一条 urls.txt 内的真实链接>/"`
5. 查看 db 计数：`.\.venv\Scripts\python.exe -c "from storage.sqlite_store import stats; print(stats())"`

**✅ 如何验证「续上了」（成功信号）：**
- **信号 1（环境）**：`pytest -q` 输出 `15 passed`。
- **信号 2（链路）**：`cli.py download` 结束出现 `已保存: output\<video_id>.mp4`。
- **信号 3（数据）**：`stats()` 返回 `total` 比接续前 **+1**（128 → 129）。
- 三条信号全部满足 = 你已完全接上 A 的现场，可以按 §6 接力表 #1 开工。

---

## 13. 按 Codex 定制的附加内容

- **命令风格**：本文档所有命令均为 **PowerShell** 风格（`.\.venv\Scripts\python.exe`、`$env:`、`cd` 反斜杠路径），与你的 Windows 运行环境一致；不使用 bash 语法。
- **接续位置函数级定位**：每个接力棒都给了 `文件::函数`（第几行）——你基于现状改代码，不需要通读全项目。
- **config.toml 提醒**：接续前核对 `C:\Users\asus\.codex\config.toml` 的 model 配置，避免第三方模型不可用导致启动失败（§8）。
- **会话可迁移**：如需换机继续，按 §8 迁移 `sessions\*.jsonl`，不拷 `auth.json`。
- **代理/网络**：抖音直连即可；全局代理需白名单放行 `*.douyin.com`（§8）。
- **指令粒度**：你是 L1 自治型，文档给「目标 + 要点 + 精确命令」即可，文件细节你可自行读取补齐——所以本文档不贴大段代码，只给函数级入口。
