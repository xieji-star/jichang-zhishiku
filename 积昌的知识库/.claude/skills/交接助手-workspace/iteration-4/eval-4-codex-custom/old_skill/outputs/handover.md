# 短视频爬虫项目 交接文档（给 Codex 版）

> 元信息
> - **项目名**：shortvideo-crawler（短视频爬虫，抓取抖音 / 快手视频元数据）
> - **交接对象**：Codex（OpenAI 智能体，模式 B 专属定制）
> - **交接方向**：A（DeepSeek 构建的旧会话）→ B（Codex 续作）
> - **交接日期**：2026-08-18
> - **生成方式**：由「交接助手」skill 旧版快照 + `references/agent-profiles.md` 中 Codex 习性档案生成

---

## 0. 交接摘要（启动包）

- **项目**：`D:\shortvideo-crawler`，Python 短视频爬虫，抓取抖音 / 快手的视频元数据（标题、作者、点赞/评论/播放量、发布时间、链接），落库 SQLite 供数据分析。
- **当前状态**：整体约 **65%**。抖音列表抓取链路已通，快手仅列表页通；验证码、去重断点续爬、调度、导出、代理池均为未完成接力棒。
- **最关键三件事**：
  1. **已完成**：抖音爬虫主链路（签名→请求→解析→入库）可跑通，测试 12 条通过。
  2. **A 没做完的（接力棒）**：① 抖音滑块验证码空实现；② 快手详情页解析只写了 `return None`；③ 去重 / 断点续爬未实现（另见接力总览 #4-#7）。
  3. **B 下一步第一件事**：实现 `crawlers\douyin_crawler.py` 中 `_handle_slider_captcha()`（`# L210`），跑通反爬后连续抓取 3 次不触发即完成。
- **最省力接续点**：不重建环境——沿用现有 `.venv` 与 `data\videos.db`，直接从 `#6 接力总览` 的第 1 行动手。

---

## 1. 项目总览与验收标准

- **一句话定位**：按关键词批量抓取抖音 / 快手视频元数据，存 SQLite，供后续内容分析 / 报表使用。
- **最终目标**：两条平台（抖音、快手）都能稳定批量抓取，数据去重、支持断点续爬与定时调度，可一键导出 CSV。
- **验收标准（可检验）**：
  - 抖音 / 快手各跑 `--limit 100` 连续 3 轮，日志出现 `[INFO] 本次抓取入库 N 条` 且 `data\videos.db` 行数单调递增、无重复。
  - `python -m pytest tests\ -v` 通过 **≥ 25 条**。
  - `python main.py --export csv` 生成 `data\export\videos.csv`，行数与库一致。

---

## 2. 文件地图（精确路径）

| 文件/目录 | 作用 | 当前状态 |
|-----------|------|---------|
| `D:\shortvideo-crawler\main.py` | CLI 入口（`--platform` / `--keyword` / `--limit` / `--resume` / `--export`） | 已实现基础；`--resume`（约 `#L120`）、`--export` 未实现 |
| `D:\shortvideo-crawler\crawlers\base_crawler.py` | 基类 `BaseCrawler`：`fetch_page()`（约 `#L45`）、`parse_list()`、`run()` | 已实现；未读代理配置 |
| `D:\shortvideo-crawler\crawlers\douyin_crawler.py` | `DouyinCrawler`：`_sign_params()` 签名、`_handle_slider_captcha()`（约 `#L210`） | `_sign_params()` 可用；`_handle_slider_captcha()` 为空 `pass` |
| `D:\shortvideo-crawler\crawlers\kuaishou_crawler.py` | `KuaishouCrawler`：`parse_list()`（已完成）、`parse_detail()`（约 `#L88`） | 列表页通；`parse_detail()` 只写 `return None` |
| `D:\shortvideo-crawler\parsers\video_parser.py` | `extract_video_meta(html)` 从 HTML 提取元数据 | 已实现，抖音可用 |
| `D:\shortvideo-crawler\storage\db.py` | SQLite 存取：`insert_video()`、`get_by_video_id()` | 已实现；缺 `is_duplicate()` / 唯一索引 |
| `D:\shortvideo-crawler\config\config.yaml` | 平台、关键词、频率、`proxy:` 占位、`schedule:` 占位 | `proxy:`、`schedule:` 段仅占位，代码未读取 |
| `D:\shortvideo-crawler\requirements.txt` | 依赖清单（requests、beautifulsoup4、pyyaml、pytest 等） | 已冻结 |
| `D:\shortvideo-crawler\run_crawl.ps1` | PowerShell 启动脚本 | 已有，可直接用 |
| `D:\shortvideo-crawler\.venv\` | Python 虚拟环境 | 已创建，可用 |
| `D:\shortvideo-crawler\data\videos.db` | SQLite 库，表 `videos(id, platform, video_id, title, author, play_count, like_count, comment_count, publish_time, url, raw_html, created_at)` | 已有抖音测试数据约 37 行 |
| `D:\shortvideo-crawler\data\export\` | CSV 导出目录 | 空（导出未实现） |
| `D:\shortvideo-crawler\logs\crawler.log` | 运行日志 | 有近期抓取记录，可作验证参考 |
| `D:\shortvideo-crawler\tests\test_storage.py`、`test_parser.py` | 单测，共 12 条 | 全部通过 |
| `D:\shortvideo-crawler\.env` | Cookie / 请求头（值已脱敏） | 存在，仅本机有效 |

> 状态标记：`未实现` = 接力棒；`占位` = 有配置没代码。

---

## 3. 已完成工作（全量逐条）

1. **项目脚手架与虚拟环境**：`D:\shortvideo-crawler\` 目录、`.venv`、`requirements.txt` 已就绪。验证：`.\.venv\Scripts\Activate.ps1` 可激活。
2. **CLI 入口 `main.py`**：支持 `--platform douyin|kuaishou`、`--keyword`、`--limit`。验证：`python main.py --help` 正常列出参数。
3. **抖音抓取主链路**：`crawlers\douyin_crawler.py` 的 `_sign_params()`（签名）→ `fetch_page()` → `parse_list()` 已通，`extract_video_meta()` 可提取标题/作者/点赞等字段。验证：实测入库 37 行。
4. **快手列表页解析 `parse_list()`**：`crawlers\kuaishou_crawler.py` 列表页可解析出视频 ID 与链接。验证：`logs\crawler.log` 有 kuaishou 列表页成功行。
5. **存储层 `storage\db.py`**：`insert_video()`、`get_by_video_id()` 可用，含 `created_at` 时间戳。验证：`tests\test_storage.py` 通过。
6. **配置管理 `config\config.yaml`**：可加载平台与关键词；`pyyaml` 读取正常。验证：`python -c "import yaml; print(yaml.safe_load(open('config/config.yaml',encoding='utf-8')))"` 输出正常。
7. **PowerShell 启动脚本 `run_crawl.ps1`**：激活 venv 并调 `main.py`。验证：`.\run_crawl.ps1 -Keyword "美食" -Limit 10` 可跑。
8. **基础测试 12 条**：`tests\test_storage.py`（8 条）+ `tests\test_parser.py`（4 条）全绿。验证：`python -m pytest tests\ -v`。

---

## 4. 当前精确进度

- **最后一步有效操作**：在 `crawlers\douyin_crawler.py` 完成 `_sign_params()` 与 `parse_list()` 联调，`python main.py --platform douyin --keyword "美食" --limit 50` 成功入库 37 条，随后触发平台滑块验证码，程序在 `_handle_slider_captcha()`（空实现）处 `pass` 后因无验证码处理逻辑而中断。
- **当前代码状态**：
  - `crawlers\douyin_crawler.py#L210` 的 `_handle_slider_captcha()` 为 `pass` 占位——这是抖音链路当前最直接断点。
  - `crawlers\kuaishou_crawler.py#L88` 的 `parse_detail()` 为 `return None` 占位——快手数据只到列表层。
  - `storage\db.py` 无唯一约束，重复抓取会重复入库。
  - `main.py --resume` / `--export` 两个参数已在 argparse 注册但未实现。
- **数据状态**：`data\videos.db` 中 `videos` 表 37 行，全部为抖音测试数据，`platform='douyin'`；`raw_html` 字段有存原始 HTML。

---

## 5. A 没做完的事（接力棒，全量逐条）

> 以下每一项都是 A 留给 B 的**接力棒**，是 B 的起点，不是 B 的过错。

| # | 还差什么 | 为什么没做完（阻塞原因） | 前置条件 | 优先级 | 做到什么程度算完成 |
|---|---------|------------------------|---------|--------|-------------------|
| 1 | 抖音滑块验证码处理 `_handle_slider_captcha()` 空实现 | A 在 DeepSeek 会话中未接入打码/验证码服务，且无代理池可绕，触发反爬即中断 | 一个可用打码服务账号或代理池 | 🔴 紧急 | 连续 3 轮 `--limit 50` 抓取不触发反爬；日志出现 `[INFO] captcha handled` |
| 2 | 快手详情页解析 `parse_detail()` 只返回 None | A 时间只够做列表页，详情页反爬规则未研究 | 能拿到详情页 HTML 的会话/Cookie | 🟠 重要 | `parse_detail()` 返回含播放量/点赞/评论/发布时间的 dict 并入库，库中 kuaishou 行 `like_count` 等非空 |
| 3 | 数据去重 / 断点续爬未实现 | 未到做数据工程这一步，当前测试规模小看不出来 | 无 | 🟠 重要 | `videos` 表建 `UNIQUE(video_id, platform)`；重跑同一关键词入库数不重复增长；`--resume` 能从上次游标继续 |
| 4 | 定时调度未实现 | 需求优先级低于把单次抓取做通 | 无 | 🟡 一般 | `python main.py --schedule` 按 `config.yaml` 的 `schedule:` 间隔自动抓取，日志有定时触发记录 |
| 5 | CSV/Excel 导出未实现 | 数据分析方还没提格式要求 | 数据去重（#3）先完成 | 🟡 一般 | `python main.py --export csv` 生成 `data\export\videos.csv`，行数与库一致 |
| 6 | 代理池未集成 | A 用本机直连够用，未考虑多账号/封禁 | 代理源列表 | 🟡 一般 | `fetch_page()` 读取 `config.yaml` 的 `proxy:`，单代理失败自动切换，日志出现 `[WARN] 切换代理` |
| 7 | 测试覆盖低（仅 12 条） | 一直优先功能实现，未补测试 | 前 6 项随改随测 | 🔵 收尾 | `python -m pytest tests\ -v` 通过 ≥ 25 条 |

---

## 6. A→B 接力总览（读到就能开工，核心）

> 这张表就是 Codex 的开工清单：每行「从哪开始」列是可直接执行的入口（PowerShell 命令 / 文件:行号 / 函数名），「做到什么算完成」列是可观察的验证信号。按 #1 逐行做，无需再问人。

| # | A 没做完的（接力棒） | B（Codex）要做什么 | 从哪开始（PowerShell 命令 + 函数级定位） | 做到什么算完成（验证信号） |
|---|--------------------|-------------------|-----------------------------------------|---------------------------|
| 1 | 抖音滑块验证码空实现 | 实现验证码处理：接入打码服务或滑块识别；增强代理绕过；触发检测 + 重试 | 打开 `crawlers\douyin_crawler.py`，改 `_handle_slider_captcha()`（`#L210`）；改后跑 `cd D:\shortvideo-crawler; .\.venv\Scripts\Activate.ps1; python main.py --platform douyin --keyword "美食" --limit 50` | 日志 `logs\crawler.log` 出现 `[INFO] captcha handled`；`[INFO] 本次抓取入库 N 条` 连续 3 轮 |
| 2 | 快手详情页解析返回 None | 实现 `parse_detail()`：解析播放量/点赞/评论/发布时间并写库 | 打开 `crawlers\kuaishou_crawler.py`，改 `parse_detail()`（`#L88`）；跑 `python main.py --platform kuaishou --keyword "美食" --limit 20` | `python -c "import sqlite3;c=sqlite3.connect('data/videos.db');print(c.execute('select count(*) from videos where platform=\'kuaishou\' and like_count is not null').fetchone())"` 输出 >0 |
| 3 | 去重 / 断点续爬未实现 | 加 `UNIQUE(video_id, platform)` 索引与 `is_duplicate()`；实现 `--resume` 游标记录 | 改 `storage\db.py`（`insert_video()` 附近）+ `main.py` 的 `--resume` 分支（`#L120`） | 重跑同关键词 `python main.py --platform douyin --keyword "美食" --limit 50`，库中总行数不再增长；`--resume` 日志显示从上次游标继续 |
| 4 | 定时调度未实现 | 用 `schedule` 库实现 `--schedule`，按 `config.yaml` 间隔触发 | 改 `main.py` 新增 `--schedule` 分支 + 填 `config\config.yaml` 的 `schedule:` 段 | `python main.py --schedule` 后按间隔自动触发，日志出现多条定时触发时间戳 |
| 5 | CSV 导出未实现 | 实现 `storage\export.py`（新建）与 `--export csv` | 新建 `storage\export.py` + 改 `main.py`；跑 `python main.py --export csv` | `Get-ChildItem data\export\*.csv` 出现文件，且 `(Get-Content data\export\videos.csv | Measure-Object -Line).Lines - 1` 等于库行数 |
| 6 | 代理池未集成 | 让 `fetch_page()` 读取 `config.yaml` 的 `proxy:` 列表，轮换 + 失败重试 | 改 `crawlers\base_crawler.py` 的 `fetch_page()`（`#L45`） | 停掉默认出口后日志出现 `[WARN] 切换代理`，且抓取不中断 |
| 7 | 测试覆盖低 | 补验证码、详情解析、去重用例，目标 ≥ 25 条 | 改 `tests\test_parser.py`、新建 `tests\test_dedupe.py`；跑 `python -m pytest tests\ -v` | 控制台输出 `=== 25 passed (或更多) ===` |

> **🚀 接力开工第一步（正式接上信号）**：
> 在 PowerShell 执行：
> ```powershell
> cd D:\shortvideo-crawler
> .\.venv\Scripts\Activate.ps1
> python main.py --platform douyin --keyword "美食" --limit 10
> ```
> 若 `logs\crawler.log` 出现 `[INFO] 本次抓取入库 N 条`（N ≥ 1），且 `Get-Content logs\crawler.log -Tail 20` 无 `Traceback`——即证明环境已还原、A 的工作已接上，可以开始做接力总览 #1。

---

## 7. 下一步行动计划（命令级，PowerShell）

### 🔥 立即做
1. **环境还原自检**（不做任何修改）：
   ```powershell
   cd D:\shortvideo-crawler
   .\.venv\Scripts\Activate.ps1
   python --version      # 应输出 3.11.x
   python -m pytest tests\ -v   # 应 12 passed
   ```
2. **接力 #1 抖音验证码**：改 `crawlers\douyin_crawler.py` 的 `_handle_slider_captcha()`（`#L210`）。建议先接入打码服务（如固定用第三方 HTTP API），失败则回退代理重试。每步改完跑 `python main.py --platform douyin --keyword "美食" --limit 50` 看日志。
3. **接力 #2 快手详情页**：抓一个详情页 HTML 存到 `tests\fixtures\kuaishou_detail.html`，先写解析再入库，`python main.py --platform kuaishou --keyword "美食" --limit 20` 验证。

### ⏳ 之后做
4. 接力 #3 去重/断点续爬 → 接力 #4 定时调度 → 接力 #5 CSV 导出 → 接力 #6 代理池 → 接力 #7 补测试。
5. 全部完成后跑全量验证（见「11 续作启动手册」的验收命令）。

---

## 8. 环境与配置依赖（完整清单）

| 项 | 值 / 位置 | 说明 |
|----|----------|------|
| Python | 3.11.x（`.venv` 内） | 用 `.\.venv\Scripts\Activate.ps1` 激活，勿用全局 Python |
| 依赖 | `D:\shortvideo-crawler\requirements.txt` | 含 requests、beautifulsoup4、pyyaml、pytest；装齐用 `pip install -r requirements.txt` |
| 配置文件 | `D:\shortvideo-crawler\config\config.yaml` | 平台/关键词/频率 + `proxy:` `schedule:` 占位段 |
| Cookie/请求头 | `D:\shortvideo-crawler\.env`（值已脱敏） | 仅本机有效，失效需人工更换 |
| SQLite | `D:\shortvideo-crawler\data\videos.db` | 无需单独装，Python 自带 `sqlite3` |
| Codex 模型配置 | `C:\Users\asus\.codex\config.toml` | ⚠️ 本工程不依赖第三方模型，但开工前确认 `model` 值可用，避免 Codex 报模型不可用 |
| 密钥/token | 均在 `.env`，值已脱敏为 `<已脱敏>` | 交接文档中不出现明文 |

---

## 9. 数据与状态快照

- **数据库**：`data\videos.db` 的 `videos` 表 37 行（全为 `platform='douyin'`）。表结构见文件地图。
- **日志**：`logs\crawler.log` 保留最近 3 次运行，可作行为基准。
- **临时数据**：`data\` 下抓取的 `raw_html` 字段暂无需清理，是后续解析调试的素材。
- **需保留的中间产物**：`tests\fixtures\`（建议新建，放快手详情页 HTML 样本）。
- **测试数据**：37 行抖音数据可保留作回归基准；导出 CSV 后如需交付再清。

---

## 10. 关键决策与踩坑记录

- **技术选型**：
  - **requests + beautifulsoup4**（不用 scrapy）：项目规模小、反爬点靠手动签名，轻量方案上手快。若后期规模大再迁 scrapy。
  - **SQLite**（不用 MySQL）：单机数据分析场景足够，免运维。
  - **yaml 配置**：关键词/频率常改，放配置便于改不动码。
- **踩坑与规避**：
  - **抖音签名 `_sign_params()`**：签名算法在响应 HTML 的 JS 里，A 通过正则提取后本地重算；改签名参数名会导致 403，规避：参数名统一走 `config.yaml`。
  - **请求频率过高触发滑块**：之前试过无延迟抓取，触发率 100%；规避：`config.yaml` 加 `request_interval`，当前建议 ≥ 2s。
  - **编码问题**：平台返回 UTF-8 但偶发 GBK 头，`extract_video_meta()` 已做 `resp.encoding` 兜底，勿删。
- **试错放弃的方案**：直接改请求头伪装浏览器 → 仅对快手有效、对抖音无效，已放弃，改为 Cookie 会话方案。

---

## 11. 风险与待确认项

- ❓ **打码服务账号**：接力 #1 需要第三方打码/滑块识别账号（密钥在 `.env`，当前为占位 `<已脱敏>`），无账号则只能走代理池绕过，请确认是否有可用服务。
- ❓ **`.env` Cookie 有效期**：抖音 Cookie 可能已过期，抓取若返回登录跳转，需人工重新登录获取。
- ❓ **代理源**：接力 #6 需要代理 IP 列表，来源待确认。
- ❓ **CSV 交付格式**：接力 #5 的字段顺序/编码（UTF-8 BOM 供 Excel 直开）需与数据消费方确认。
- ❓ **快手详情页反爬**：A 未研究详情页反爬规则，可能需要新的 Cookie 会话（同上）。

---

## 12. 续作启动手册（环境还原 + 如何验证续上了）

从零（新机器/新会话）恢复完整步骤：

```powershell
# 1) 进入项目
cd D:\shortvideo-crawler

# 2) 激活虚拟环境（若不存在：python -m venv .venv）
.\.venv\Scripts\Activate.ps1

# 3) 装依赖
pip install -r requirements.txt

# 4) 确认配置与 Cookie 就位
Get-Content config\config.yaml        # 检查 proxy/schedule 占位
Get-Content .env                      # 确认 Cookie 已填（值脱敏）

# 5) 跑一遍单测，确认基线
python -m pytest tests\ -v            # 期望 12 passed

# 6) 冒烟抓取，确认主链路通
python main.py --platform douyin --keyword "美食" --limit 10
Get-Content logs\crawler.log -Tail 20 # 期望出现 [INFO] 本次抓取入库 N 条，无 Traceback
```

**✅ 如何验证"续上了"**：第 6 步日志出现 `[INFO] 本次抓取入库 N 条`（N ≥ 1）且无 `Traceback`，即 A 的环境已完整还原、可以开始做接力 #1。此信号与「第 6 节 接力总览」的开工第一步一致——第 6 节是"开工清单"（接 A 的活），本节是"环境还原"（把 A 的环境跑起来）。

---

## 13. 按 Codex 定制的附加内容

> 依据 `references/agent-profiles.md` 的 Codex 习性档案，额外强调以下定制点——这是与通用模板 / 给人版最大的区别所在。

1. **命令风格 = PowerShell**：本机环境为 Windows，所有命令均写成 PowerShell 风格（`.\.venv\Scripts\Activate.ps1`、`Get-Content`、`Get-ChildItem`），不用 bash / `source`。Codex 可直接执行，无需翻译。
2. **接续位置 = 函数 + 行号级**：Codex 强在"基于现状续改代码"，故接力总览与行动计划都给了精确到 `文件:行号` + 函数名（如 `douyin_crawler.py#L210` `_handle_slider_captcha()`），打开即见断点。
3. **先查 `config.toml`**：Codex 的模型配置在 `C:\Users\asus\.codex\config.toml`。开工前确认 `model` 可用，避免因模型配置问题无法响应（本项目不依赖第三方模型，仅作例行检查）。
4. **会话可迁移性**：若需跨账号/跨机器迁移，Codex 会话在 `C:\Users\asus\.codex\sessions\*.jsonl`——只拷贝 sessions 文件，**不要拷 `auth.json`**（含凭据）。本交接文档本身可作为新会话的完整上下文导入。
5. **网络/代理注意**：抖音/快手反爬会依赖外网访问，若 Codex 环境有代理/分流规则，先确认 OpenAI 与目标站点的分流是否就绪（参考知识库 Codex 网络故障档案）。抓包验证签名时注意别走错节点。
6. **接力表入口 = PowerShell 命令 + 函数级定位**：第 6 节「从哪开始」列全部用 PowerShell 命令与函数定位填写；「验证信号」列用 `Get-Content logs`、`python -c "...sqlite3..."`、`Get-ChildItem`、`pytest` 输出等 Codex 可直接执行的判定手段。
