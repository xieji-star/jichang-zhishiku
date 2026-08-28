# 自动爬取短视频爆款程序 交接文档（给人版）

> **元信息**
> - 项目名：自动爬取短视频爆款程序（Auto Viral Short-Video Crawler，内部代号 `AVC`）
> - 交接对象：**人**（接手同事 / 领导 / 未来的自己）；文末附「给 Claude Code 版」供智能体无缝续作
> - 交接人（A）：谢积昌
> - 交接日期：2026-08-18
> - 当前整体完成度：**约 65%**（抓取链路已跑通，评分/导出/自动化还差半程）

> **一句话定位**：这是一个每天自动去抖音、快手、小红书"捞"爆款短视频的爬虫程序，捞回来的视频标题、点赞数、爆点关键词会被整理成 Markdown 选题素材，直接喂给「华哥脚本撰写」流程的选题库用。
>
> **阅读指引**：想快速上手干活，直接看 **第 8 节「A→B 接力总览」+ 第 9 节「下一步怎么做」**，照着 #1 动手即可；想把来龙去脉摸清，从第 2-5 节顺读；想避坑，看第 10 节；交接给 AI 继续干，把文末「附」那份直接丢给它。

---

## 1. 这份文档是给谁看的

- **写这份文档的背景**：A（谢积昌）做这个程序做了约 2 周，目前抓取主链路已经能跑通、数据能入库、能导出素材，但距离"全自动稳定出选题"还差一截。因为个人精力要转向脚本撰写和实习工作，这个项目需要**换人（或换 AI 智能体）继续干**。为了不让接手方从头摸一遍、重复踩坑，A 把项目当前状态一次性、结构化地交代清楚。
- **读者读完应该能达到的效果**：
  - 不用问 A 任何问题，就能看懂"这个程序现在能干什么、卡在哪、下一步该干什么"；
  - 能照着第 8/9 节的操作，**当天就跑起来第一件事**；
  - 知道每个没做完的事"做到什么程度算完成、怎么验证、卡住找谁"。

---

## 2. 项目总览（大白话）

- **这是做什么的**：一个 Python 写的爬虫程序。每天去短视频平台（抖音为主，快手、小红书规划中）搜"爆款视频"（点赞多、转发多、评论区热闹的那种），把它们的**标题、作者、点赞/收藏/转发/评论数、视频链接**抓下来，存进本地数据库；再用一套"爆款评分"算法打分；最后按选题需要的格式导出成 Markdown 文档，供写脚本时挑素材。
- **为谁做、解决什么问题**：给做短视频脚本（知识库「华哥脚本撰写」流程）的人提供"选题弹药"。以前找爆款全靠人工刷手机，一天刷 2 小时也凑不满 10 条有效选题；有了这个程序，每天 10 分钟就能拿到 30-50 条带评分的爆款素材，按"技术痛点/方向判断/案例故事/筛选劝退"四类内容线分好组，直接当脚本选题库用。
- **一句话讲清项目价值**：把"人肉刷屏找爆款"变成"机器每天自动出选题清单"，把选题效率从每天 2 小时降到 10 分钟。
- **整体完成度估算（约 65%）**：
  - 已通：抖音热榜+关键词抓取、SQLite 入库去重、评分 v1、Markdown 导出 v1、环境脚本、单元测试；
  - 未通：快手/小红书抓取、抖音评论抓取、评分 v2（内容线分类）、定时增量自动跑、数据清洗、导出 v2 排版。
  - 判断依据：核心的"抓取→入库→评分→导出"链路已经端到端跑通并出过真实素材，占主干工作量约 6 成；剩余的多是**扩平台、补信号、自动化、收尾打磨**，单项都不算难，但数量多。

---

## 3. 背景与来龙去脉

- **项目怎么来的**：2026-08 月初，A 在做「华哥脚本撰写」时发现选题环节最耗时。知识库里已有《受众报告》（四类内容线配比 40/25/20/15）和《offer 收割：100% 命中率的求职技巧》等方法论，但缺"机器可读的爆款素材源"。于是 A 决定写个爬虫，把平台爆款自动灌进素材库。
- **关键约束与偏好**：
  - 平台优先级：**抖音 > 快手 > 小红书**（抖音爆款密度最高，先做它）；
  - 数据只用**公开页面的展示数据**（点赞/收藏/评论/转发数），不做任何用户隐私采集；
  - 输出必须按「受众报告」的四类内容线组织，这是脚本流程的硬性消费格式；
  - 程序要**低门槛可维护**：纯 Python + SQLite + 标准库为主，不引重型框架，方便 A 不在时别人也能改。
- **和团队其他事的关系**：产出的 `export_daily.md` 会进入知识库 `总结好的大纲以及笔记/实习就业/工作文件/脚本撰写/脚本资料库/` 目录，作为脚本选题的原材料；评分打标规则直接复用 `受众报告.md` 的分类词表。

---

## 4. 术语表

- **AVC** ＝ 本项目代号，Auto Viral Crawler 的缩写，指"自动爬取短视频爆款程序"。
- **爆款视频** ＝ 互动数据（点赞/收藏/评论/转发）显著高于同批次的视频，本程序用"评分 ≥ 70"作为爆款阈值。
- **aweme_id** ＝ 抖音视频的唯一 ID（数字串），是去重和 URL 的唯一键。
- **游客态 / 登录态** ＝ 不带 cookie 访问（游客态）能看到大部分列表数据；评论接口和部分互动数据需要带登录 cookie（登录态）。
- **评分 v1** ＝ 当前版本算法：对点赞、收藏、转发做对数归一化后加权求和，得分 0-100。
- **内容线** ＝ 知识库「受众报告」定义的四类选题方向：技术痛点型（40%）、方向判断型（25%）、案例故事型（20%）、筛选劝退型（15%）。v2 评分将按此给每条视频打标。
- **打码平台** ＝ 处理验证码（如滑块、点选）的第三方付费服务，如超级鹰、图鉴，用于小红书/快手反爬。
- **client_sign** ＝ 快手请求签名参数，由内部算法（时间戳+随机串+二进制哈希）生成，绕不过就拿不到数据，是本项目技术难点。
- **增量抓取** ＝ 只抓"上次游标之后新增"的视频，而不是每天全量重抓一遍，省流量省时间。
- **断点游标** ＝ 记录"上次抓到哪了"的字段（如最大视频 ID / 时间戳），增量抓取靠它续跑。
- **pytest** ＝ Python 单元测试框架，项目里用 `pytest -q` 跑测试验证功能没被改坏。

---

## 5. 当前进度（用"人话"讲）

- 程序**已经能跑通一条完整的流水线**：手动跑一次 → 去抖音抓热榜和关键词结果 → 存进本地数据库 → 给每条视频打分 → 导出一份 Markdown 选题日报。这条链路 A 已实际跑过并产出过真实素材，不是 demo。
- **最后一次停在什么位置**：2026-08-17 晚上，A 跑通了「抖音关键词搜索 → 入库 → 评分 → 导出」全链路，导出了当天 47 篇选题素材（其中爆款 22 篇，评分 ≥70）。停下的原因是要开始写实习交接，程序当时**还停留在"手动跑"阶段**——定时自动跑、快手/小红书平台、评论数据、内容线打标都还没接上。
- **一句话状态**：**"能手动出活，还不能自动出活"**——每天得有人手动敲一条命令，跑完才有素材；平台只覆盖抖音，信号只用了"量"（点赞收藏转发），还没用上"质"（评论内容、完播率、内容线分类）。

---

## 6. 已完成工作（全量逐条）

> 每条都写了四件事：做了什么、产出物在哪、怎么验证有效、关键数据。这些都是 A 已经做完并验证过的，接手方可以放心依赖。

### 6.1 项目骨架 + 爬虫基类

- **做了什么**：搭好了项目目录结构，定义了统一的爬虫基类 `BaseFetcher`（封装请求头、超时、重试、日志），后续每个平台的爬虫都继承它，保证接口一致。
- **产出物在哪**：`D:\ViralShortVideoCrawler\main.py`（入口）、`D:\ViralShortVideoCrawler\src\fetcher\base.py`（基类）。
- **怎么验证有效**：跑 `python -m src.fetcher.base` 会打印出基类自检日志（代理头、超时值、重试次数），说明类能正常导入、配置能加载。
- **关键数据**：目录共 11 个模块文件；基类内置 3 次重试、15s 超时；单元测试 `test_fetcher_base.py` 8 条全过。

### 6.2 抖音抓取模块（热榜 + 关键词搜索）

- **做了什么**：实现了抖音两个抓取入口——「热门榜 Top100」和「关键词搜索 Top50」，能拿到视频标题、作者、点赞/收藏/转发/评论数、aweme_id、链接。
- **产出物在哪**：`D:\ViralShortVideoCrawler\src\fetcher\douyin.py`。
- **怎么验证有效**：跑 `python -m src.fetcher.douyin --hot-board`，会向控制台打印热榜前 10 条的 JSON（含 `title`、`like_count` 等字段），说明能真实抓到抖音数据。
- **关键数据**：单次热榜抓取成功抓回 100 条，平均耗时约 40s；关键词搜索单次 50 条，实测关键词"副业""AI 工具""职场"均能返回有效结果；已累计抓回原始视频 1284 条。

### 6.3 SQLite 入库 + 去重

- **做了什么**：建了 SQLite 数据库 `videos.db`，定义 `videos` 表（含 aweme_id 唯一索引），实现写入、按 aweme_id 精确去重、按平台/时间查询。
- **产出物在哪**：`D:\ViralShortVideoCrawler\src\storage\sqlite_store.py`、数据文件 `D:\ViralShortVideoCrawler\data\videos.db`。
- **怎么验证有效**：跑 `python -m src.storage.sqlite_store --stats` 会打印 `total=1031 dupes=253` 之类的统计，说明去重生效。
- **关键数据**：去重后入库 **1031 条**（去重掉了 253 条重复抓取）；表结构 11 个字段；精确去重命中率 19.7%。

### 6.4 爆款评分模型 v1

- **做了什么**：实现评分函数，把点赞、收藏、转发做对数归一化后加权求和，输出 0-100 分，`score ≥ 70` 判为爆款。
- **产出物在哪**：`D:\ViralShortVideoCrawler\src\analyzer\virality_score.py` 的 `score()` 函数（第 45 行起）。
- **怎么验证有效**：跑 `python -m src.analyzer.virality_score --sample 30`，会打印 30 条样本的分数分布（如 `avg=52 max=94`），说明算法能正常出分。
- **关键数据**：当前权重 点赞 0.5 / 收藏 0.3 / 转发 0.2；1031 条里有 213 条达到爆款线（≥70），爆款率 20.7%。

### 6.5 Markdown 导出 v1

- **做了什么**：实现把评分后的视频导出成 Markdown 选题日报，按分数降序，每条含标题、作者、平台、评分、链接。
- **产出物在哪**：`D:\ViralShortVideoCrawler\src\storage\export_md.py` 的 `export_daily()`（第 78 行起）；样例输出在 `D:\ViralShortVideoCrawler\data\exports\daily_2026-08-17.md`。
- **怎么验证有效**：打开 `daily_2026-08-17.md` 能看到 47 条选题，带评分列和链接列；跑 `export_daily` 会生成同名带日期的新文件。
- **关键数据**：08-17 当天导出 47 条选题，其中爆款 22 条；单次导出耗时约 2s。

### 6.6 环境与部署脚本

- **做了什么**：写了三个 PowerShell 脚本——`setup.ps1`（建虚拟环境+装依赖）、`run_crawl.ps1`（一键抓取入库）、`export_daily.ps1`（一键导出日报）。
- **产出物在哪**：`D:\ViralShortVideoCrawler\scripts\setup.ps1`、`run_crawl.ps1`、`export_daily.ps1`。
- **怎么验证有效**：新机器上跑 `.\scripts\setup.ps1` 能一步建好环境并打印 `setup OK`；跑 `.\scripts\run_crawl.ps1` 会打印抓取条数。
- **关键数据**：依赖清单 9 个包（requests、fake-useragent、python-dotenv 等）；setup 实测在干净机器约 3 分钟完成。

### 6.7 单元测试

- **做了什么**：给抓取解析、评分算法、入库去重写了 pytest 用例，保证改动不破坏已有功能。
- **产出物在哪**：`D:\ViralShortVideoCrawler\tests\test_douyin.py`、`test_score.py`、`test_sqlite_store.py`。
- **怎么验证有效**：在项目根目录跑 `python -m pytest -q`，输出 `23 passed` 即全绿。
- **关键数据**：23 条用例全过；覆盖评分边界（0 分、满分、None 字段）和去重逻辑。

### 6.8 已抓取数据集（可复用素材）

- **做了什么**：两周内积累了一批真实爆款数据，可直接当选题素材或当评分调参的测试集。
- **产出物在哪**：`D:\ViralShortVideoCrawler\data\videos.db`（1031 条）、`data\exports\daily_2026-08-17.md`（47 条选题日报）。
- **怎么验证有效**：用 SQL 查询 `SELECT COUNT(*) FROM videos WHERE score>=70` 应返回 213；打开日报文件能看到真实标题。
- **关键数据**：1031 条入库、213 条爆款、47 条已导出日报、覆盖抖音 1 个平台。

---

## 7. A 没做完的事（需要你接力的，全量逐条）

> **先说清楚：下面这些不是你的过错，是前任（A）留下的"接力棒"，是你的起点。** A 按优先级和依赖关系排了序，每条都写满了七要素（还差什么 / 为什么没做完 / 前置条件 / 优先级 / 做到什么算完成 / 从哪开始 / 验证信号），照做即可。

### U1：快手抓取模块（完全没有开发）

| 要素 | 内容 |
|------|------|
| 还差什么 | 快手端代码一行没有。缺三块：① 请求签名算法 `client_sign` 的破解/绕过；② 手机号验证码登录态管理；③ 热榜页 + 关键词搜索页的解析逻辑。 |
| 为什么没做完 | 技术难题：快手的 `client_sign` 由"时间戳+随机串+二进制哈希"动态生成，A 两周内没攻破；且登录态需要真实手机号，A 不想用个人号去碰风控。 |
| 前置条件 | ① 先解决签名算法（可参考抖音的伪造 UA + 固定请求头方案，或查社区开源签名库）；② 准备一个快手小号用于登录（可问运营要测试号）。 |
| 优先级 | 重要（爆款源只覆盖抖音一家，覆盖面不够） |
| 做到什么算完成 | 能稳定抓「快手热榜 Top50」+「关键词搜索 Top30」，每日增量入库 ≥ 100 条，连续 3 天 0 封号、0 验证码拦截。 |
| 从哪开始 | `D:\ViralShortVideoCrawler\src\fetcher\kuaishou.py`（空文件待建，按 `douyin.py` 的类结构照葫芦画瓢）。 |
| 验证信号 | 跑 `python -m src.fetcher.kuaishou --hot-board` 能在控制台看到热榜 JSON，且 `sqlite_store --stats` 里 platform=kuaishou 计数在涨。 |

### U2：小红书抓取模块（只完成 40%）

| 要素 | 内容 |
|------|------|
| 还差什么 | 列表页解析已写好，但**详情页抓取没做**（点赞/收藏/评论数拿不全）；**滑块验证码没处理**，经常被拦。 |
| 为什么没做完 | 等外部依赖：小红书 anti-spider 验证码频发，需要接打码平台（超级鹰/图鉴）或配浏览器指纹，A 当时没申请打码预算，就先搁置了。 |
| 前置条件 | ① 购买/申请一个打码平台账号，把 token 写进 `.env`；② 准备一个小红书账号 cookie。 |
| 优先级 | 一般（小红书爆款量级低于快手，排 U1 之后） |
| 做到什么算完成 | 能连续抓 50 条笔记详情（含点赞/收藏/评论数），验证码出现率 < 10%，全部入库成功。 |
| 从哪开始 | `D:\ViralShortVideoCrawler\src\fetcher\xhs.py` 的 `fetch_detail()` 函数（第 187 行起）。 |
| 验证信号 | 跑 `python -m src.fetcher.xhs --detail <note_id>` 返回完整指标 JSON（含 `like_count`、`collect_count`、`comment_count`）。 |

### U3：抖音评论抓取（爆款判断的关键信号，未做）

| 要素 | 内容 |
|------|------|
| 还差什么 | 没有评论抓取代码，也没建 `comments` 表。评论内容 + 评论情感是"爆款质量"的重要信号，评分 v2 依赖它。 |
| 为什么没做完 | 评论接口需要**登录态 cookie**（游客态拿不到），A 当时没研究 cookie 注入，时间不够，先跳过了。 |
| 前置条件 | ① 把抖音登录后的 cookie 注入 `config.yaml` 的 `douyin.cookie` 字段（cookie 敏感，注意脱敏管理）；② 数据库先建 `comments` 表。 |
| 优先级 | 紧急（评分 v2 的前置数据，且抓评论的接口会变，越早做越好） |
| 做到什么算完成 | 对当前 Top30 爆款视频，每条抓到 ≥ 20 条评论入库，`comments` 表有数据，评分模型能读到。 |
| 从哪开始 | `D:\ViralShortVideoCrawler\src\fetcher\comments.py`（新建；评论接口的 URL 已写在 `douyin.py` 顶部注释里）。 |
| 验证信号 | `SELECT COUNT(*) FROM comments` 返回 > 600；且 `videos` 表里每条 Top30 视频都有 ≥20 条关联评论。 |

### U4：爆款评分 v2（内容线分类 + 互动率加权，未做）

| 要素 | 内容 |
|------|------|
| 还差什么 | v1 只按"量"（点赞/收藏/转发）打分，缺三块：① 按「受众报告」四类内容线给视频打标签；② 加入"评论情感分"和"互动率（评论/点赞比）"；③ 输出格式带内容线标签。 |
| 为什么没做完 | 有依赖：评论数据（U3）和互动数据（U2）还没到位；另外四类内容线的关键词词表需要从知识库《受众报告.md》整理成机器可读的 JSON，A 只整理了一半。 |
| 前置条件 | ① U3 完成（评论数据可用）；② 词表 JSON `category_rules.json` 补齐四类关键词。 |
| 优先级 | 重要（"爆款判定"和"选题分组"的核心，直接决定导出 v2 质量） |
| 做到什么算完成 | 评分输出带 `content_line` 字段，四类覆盖全；抽样 50 条人工复核，分类准确率 ≥ 80%。 |
| 从哪开始 | `D:\ViralShortVideoCrawler\src\analyzer\virality_score.py` 的 `score()`（第 45 行）和 `data\category_rules.json`（半成品）。 |
| 验证信号 | 跑 `python -m src.analyzer.virality_score --sample 50` 打印 `acc=0.84`（分类准确率）且四类都有样本。 |

### U5：定时增量抓取（当前只能手动全量跑，未做）

| 要素 | 内容 |
|------|------|
| 还差什么 | ① 没有增量逻辑：现在每次抓都是全量重抓一遍，重复抓回 253 条就是代价；② 没有断点游标：数据库没存"上次抓到哪了"；③ Windows 计划任务没配置，得有人手动敲命令。 |
| 为什么没做完 | 表结构没加游标字段，得先改表；且 A 想让 U4 定稿后一起改，避免数据结构反复动。 |
| 前置条件 | ① `videos` 表加 `crawled_at` 索引（已部分有）；② `config.yaml` 增加 `incremental: true` 开关和计划任务时间。 |
| 优先级 | 一般（先手动跑通，再自动化；但不做它，程序永远"半自动"） |
| 做到什么算完成 | 每天 09:00 计划任务自动跑，只抓新增视频，日志出现 `incremental: +N new`，连续 3 天 DB 只增不重。 |
| 从哪开始 | `D:\ViralShortVideoCrawler\src\scheduler\cron_job.py`（空文件待建）；计划任务在 Windows 的"任务计划程序"里配。 |
| 验证信号 | 连续 3 天查看 `data\logs\crawler.log`，每天都有一行 `incremental: +N new`，且 `videos` 表计数每天递增、无重复新增。 |

### U6：数据质量治理（模糊去重/URL 规范化/脏数据清理，未做）

| 要素 | 内容 |
|------|------|
| 还差什么 | 现在去重只看 aweme_id 精确匹配；标题/文案相似的重复没去掉；URL 带参数冗余；有少量解析失败的空 title 脏数据没清理。 |
| 为什么没做完 | 属于收尾打磨活，一直被功能开发挤到后面，纯时间不够。 |
| 前置条件 | 无硬前置，随时可做。 |
| 优先级 | 一般（不影响主链路，但影响素材质量） |
| 做到什么算完成 | 跑一次清洗脚本后：`title=''` 的记录为 0，URL 冗余为 0，能打印出去重率统计。 |
| 从哪开始 | `D:\ViralShortVideoCrawler\src\storage\cleaner.py`（新建，读 `sqlite_store.py` 的 DB 连接方式）。 |
| 验证信号 | `SELECT COUNT(*) FROM videos WHERE title=''` 返回 0；`SELECT COUNT(*) FROM videos WHERE url LIKE '%?%'` 返回 0。 |

### U7：导出模板 v2（按四类内容线分组的 Markdown，未做）

| 要素 | 内容 |
|------|------|
| 还差什么 | 当前导出是"按分数降序"的平铺表格；需要改成**按四类内容线分组**（技术痛点/方向判断/案例故事/筛选劝退），每组内再按分数排，每条带评分+平台+标题+链接+一句话爆点。 |
| 为什么没做完 | 依赖 U4 的内容线标签字段——没标签就没法分组，所以排最后。 |
| 前置条件 | U4 完成（`content_line` 字段有值）。 |
| 优先级 | 一般（但它决定"选题日报"好不好用，做完整流程才闭环） |
| 做到什么算完成 | 导出 1 篇日报，文档里出现 `## 技术痛点型`、`## 方向判断型`、`## 案例故事型`、`## 筛选劝退型` 四个小节，每条含评分/平台/标题/链接/爆点。 |
| 从哪开始 | `D:\ViralShortVideoCrawler\src\storage\export_md.py` 的 `export_daily()`（第 78 行）。 |
| 验证信号 | 打开新导出的 md，能看到四个小节标题和分组内容。 |

---

## 8. A→B 接力总览（读到就能开工，核心）

> 下表把第 7 节"没做完的事（接力棒）"和第 9 节"你接下来要做的（接力任务）"**一一钉死**：每一行就是一件活，照着"从哪开始"干，出现"完成信号"就算验收。**建议按 #1→#7 顺序做**（依赖关系：3→4→7 是链，1/2 可并行）。

| # | A 没做完的（接力棒） | 你（B）接下来要做什么 | 从哪开始（文件/工具/找谁） | 做到什么算完成（怎么验证） |
|---|--------------------|----------------------|---------------------------|---------------------------|
| 1 | U1 快手抓取模块空白 | 开发快手抓取模块（签名+登录+解析） | `src\fetcher\kuaishou.py`（新建，参照 `douyin.py`）；卡签名问题查社区开源库/找后端同事 | `python -m src.fetcher.kuaishou --hot-board` 出热榜 JSON，且 platform=kuaishou 入库 ≥100 条/日、连续 3 天不封号 |
| 2 | U2 小红书抓取只 40% | 补详情页抓取 + 接打码平台过验证码 | `src\fetcher\xhs.py` 第 187 行 `fetch_detail()`；打码平台 token 写 `.env` | 连续抓 50 条详情成功、验证码出现率 <10%，`--detail <note_id>` 返回完整指标 |
| 3 | U3 抖音评论抓取空白 | 建 `comments` 表 + 实现评论抓取（注入登录 cookie） | `src\fetcher\comments.py`（新建，接口 URL 在 `douyin.py` 顶部注释）；cookie 找 A 要或自己登录导出 | `SELECT COUNT(*) FROM comments` >600，Top30 视频每条 ≥20 条评论 |
| 4 | U4 评分 v2 未做 | 加内容线分类 + 评论情感分/互动率加权，补 `category_rules.json` | `src\analyzer\virality_score.py` 第 45 行 `score()`；词表整理自《受众报告.md》 | `--sample 50` 打印 `acc≥0.80` 且四类都有样本 |
| 5 | U5 定时增量未做 | 加断点游标 + 增量抓取 + 配 Windows 计划任务 | `src\scheduler\cron_job.py`（新建）；计划任务在"任务计划程序"配 09:00 | 连续 3 天日志 `incremental: +N new`，DB 只增不重 |
| 6 | U6 数据质量未治理 | 写清洗脚本：模糊去重 + URL 规范化 + 清空 title 脏数据 | `src\storage\cleaner.py`（新建） | `title=''` 为 0、URL 冗余为 0，打印出去重率 |
| 7 | U7 导出 v2 未做 | 改导出为四类内容线分组 Markdown | `src\storage\export_md.py` 第 78 行 `export_daily()` | 新 md 出现 `## 技术痛点型` 等四个小节，分组正确 |

> **✅ 接力开工第一步（现在就做，不用等任何东西）**：
> 打开 PowerShell，`cd D:\ViralShortVideoCrawler`，先跑 `python -m pytest -q`——看到 **`23 passed`**，说明环境是好的、代码能跑，你就算正式接上这个项目了。接着从第 9 节 #3 开始干（它是评分 v2 的前置，优先级最高）。

---

## 9. 下一步怎么做（手把手，按优先级排）

> 第 8 节是"开工地图"，这一节把每件活展开成**普通人能照做**的步骤。每步都写清"做什么 → 看什么结果算对 → 卡住找谁"。**"立即做"= 现在就能做；"之后做"= 等前置条件满足再做。**

### #3 抖音评论抓取（立即做，U3，紧急）

1. **建评论表**：用 SQLite 客户端（或跑 `python -c "from src.storage.sqlite_store import init_db; init_db(add_comments=True)"`）建 `comments` 表，字段：`id, aweme_id, user, content, like_count, sentiment, crawled_at`，aweme_id 加普通索引。
   - *看什么算对*：`SELECT name FROM sqlite_master WHERE type='table'` 能看到 `comments`。
2. **拿登录 cookie**：用浏览器登录抖音网页版 → F12 → Network → 复制请求头里的 `Cookie` 值 → 填进 `D:\ViralShortVideoCrawler\config.yaml` 的 `douyin.cookie`（cookie 含私密信息，别提交到 git，.gitignore 已排除 config.yaml）。
   - *看什么算对*：`config.yaml` 里 `douyin.cookie` 非空。
3. **实现抓取**：新建 `src\fetcher\comments.py`，参照 `douyin.py` 的请求封装，请求 `douyin.py` 顶部注释里的评论接口 URL（GET `/aweme/v1/web/comment/list/`），用 aweme_id 分页拉，每页 20 条。
   - *看什么算对*：跑 `python -m src.fetcher.comments --aweme <某个Top30的aweme_id>` 打印出 ≥20 条评论 JSON。
4. **入库**：把评论写入 `comments` 表，并在 `videos` 表每条 Top30 视频上循环跑一遍。
   - *看什么算对*：`SELECT COUNT(*) FROM comments` > 600。
5. **写测试**：在 `tests\test_comments.py` 里补 3 条用例（空评论、分页、去重），`python -m pytest -q` 全绿。
   - *卡住找谁*：接口返回 403/风控 → 检查 cookie 是否过期，换新 cookie；解析字段名变动 → 看 `douyin.py` 注释里的字段对照，或问 A（A 记得接口结构）。

### #4 爆款评分 v2（之后做：等 #3 完成后，U4，重要）

1. **补词表**：打开知识库 `总结好的大纲以及笔记/实习就业/工作文件/脚本撰写/脚本资料库/参考的资料/受众报告/受众报告.md`，把四类内容线（技术痛点/方向判断/案例故事/筛选劝退）的关键词各抽 20-30 个，写成 `D:\ViralShortVideoCrawler\data\category_rules.json`（结构：`{"技术痛点型": ["报错","崩溃","卡顿",...], ...}`）。
   - *看什么算对*：JSON 能 `json.load` 成功，四类都有 ≥20 个词。
2. **实现分类**：在 `virality_score.py` 里加 `classify(title, category_rules)` 函数，用关键词包含匹配给视频打 `content_line` 标签（命中多类取第一个命中；无命中归"未分类"）。
   - *看什么算对*：对已入库的 1031 条跑一遍，四类覆盖率加起来 > 60%。
3. **改权重**：把 `score()` 改成 点赞 0.35 / 收藏 0.2 / 转发 0.15 / 评论情感 0.2 / 互动率 0.1；评论情感分用 `comments.sentiment`（正向=1，负向=-1，中性=0，取均值）折算。
   - *看什么算对*：`--sample 30` 打印分数分布比 v1 更"陡"（爆款与非爆款差距拉大）。
4. **人工复核**：随机抽 50 条，人工判断分类对不对，算准确率。
   - *看什么算对*：`acc ≥ 0.80`。
   - *卡住找谁*：词表怎么归纳 → 看《受众报告.md》；字段不够 → 找 A 补评论情感字段说明。

### #1 快手抓取模块（可并行，U1，重要）

1. **先攻签名**：在社区/开源库搜"快手 client_sign 算法"，找到可用的 Python 实现（或参照抖音的"伪造 UA+固定请求头"思路看能否绕过）；验证方式：用它生成签名后请求热榜接口，看能否拿到数据。
   - *看什么算对*：`python -m src.fetcher.kuaishou --hot-board` 首次返回真实热榜 JSON（不再是 403/参数错误）。
2. **接登录态**：准备快手小号，实现手机号验证码登录，把登录后的 cookie 存 `config.yaml` 的 `kuaishou.cookie`。
3. **实现解析**：按 `douyin.py` 的类结构实现热榜页 + 关键词搜索页解析，字段对齐 `videos` 表（platform 填 `kuaishou`）。
4. **入库 + 测试**：复用 `sqlite_store.py` 入库，补 `tests\test_kuaishou.py` 3 条用例。
   - *看什么算对*：`sqlite_store --stats` 里 platform=kuaishou 计数在涨，连续 3 天不封号。
   - *卡住找谁*：签名算法 → 社区开源库/问后端同事；登录风控 → 用小号、降低频率（每 30s 一条）。

### #2 小红书抓取补全（可并行，U2，一般）

1. **接打码平台**：申请超级鹰/图鉴账号，把 token 写 `config.yaml` 的 `xhs.captcha_token`，在 `xhs.py` 里遇到滑块验证码时调用打码接口。
   - *看什么算对*：验证码出现时能自动过，不再手动卡住。
2. **补详情页**：实现 `fetch_detail()`，拿点赞/收藏/评论数，写回 `videos` 表（platform=xhs）。
   - *看什么算对*：`--detail <note_id>` 返回完整指标 JSON。
3. **验收**：连续抓 50 条，验证码出现率 < 10%。
   - *卡住找谁*：打码平台接入文档 → 平台官网示例代码；字段解析 → 对照 `xhs.py` 列表页的解析方式。

### #5 定时增量抓取（之后做，U5，一般）

1. **加游标**：`videos` 表加 `crawled_at` 索引（若没有），新增 `meta` 表存各平台的 `last_cursor`（最大 aweme_id + 时间戳）。
2. **改增量逻辑**：在抓取入口判断 `config.yaml` 的 `incremental: true` 时，只抓 `aweme_id > last_cursor` 的新视频。
   - *看什么算对*：手动跑两次，第二次日志出现 `incremental: +N new`，且 N 远小于全量条数。
3. **配计划任务**：Windows「任务计划程序」建任务，每天 09:00 跑 `.\scripts\run_crawl.ps1`（追加 `-incremental` 参数）。
   - *看什么算对*：连续 3 天查看 `data\logs\crawler.log`，每天一行 `incremental: +N new`，DB 只增不重。

### #6 数据质量治理（之后做，U6，一般）

1. **写 cleaner.py**：① 清空 `title=''` 的记录；② 把 URL 里 `?` 之后的跟踪参数去掉（规范化）；③ 用标题前 10 字做模糊去重（`GROUP BY substr(title,1,10)`，保留分数高的那条）。
   - *看什么算对*：`SELECT COUNT(*) FROM videos WHERE title=''` 返回 0；URL 冗余为 0。
2. **输出统计**：脚本末尾打印去重率（去掉的条数 / 总数）。
   - *卡住找谁*：SQL 写法 → 看 `sqlite_store.py` 的查询示例。

### #7 导出模板 v2（之后做：等 #4，U7，一般）

1. **改 export_daily()**：从 `videos` 查 `score >= 70` 且 `content_line != '未分类'` 的记录，按 `content_line` 分组，每组内按分数降序。
2. **每条格式**：`- [评分 88]【抖音】《标题》 链接 ｜ 爆点一句话`。
   - *看什么算对*：生成的 md 出现 `## 技术痛点型` 等四个小节，分组正确、无空组。

---

## 10. 关键决策与踩坑记录（给后人最值钱的部分）

- **为什么选 Python + SQLite 而不是 Scrapy / 数据库服务器**：项目单人维护、数据量小（每天几百条），SQLite 零部署、一个文件全搞定，Scrapy 的管道对这个小项目是杀鸡用牛刀。**坑**：别为了"显得专业"上重框架，改起来反而慢。
- **为什么先做抖音**：爆款密度最高、接口最"友好"（游客态能拿列表），两天就跑通，快速验证了整条链路。**坑**：抖音接口字段名偶变（如 `like_count` → `digg_count`），解析层要加字段映射表（`douyin.py` 注释里有），别写死字段名。
- **为什么评分先做 v1 简版**：先让"分数存在、能排序"，再谈"分得准"。**坑**：v1 只看"量"导致高播放低质量的"标题党"也拿高分，所以 v2 才要加评论情感和互动率。
- **踩过的坑：重复抓取**。08-15 那天全量跑了两遍，重复 253 条入库，才意识到必须靠 aweme_id 去重 + 后续做增量。去重逻辑在 `sqlite_store.py` 里，已修好。
- **踩过的坑：cookie 过期**。抖音游客态能撑几天，但评论接口的登录 cookie 约 7 天过期，过期后返回 403。方案是定时刷新 cookie，别长时间依赖一个 cookie。
- **试错过但放弃的方案**：① 快手签名——试过"纯伪造请求头"绕过，不行，得正经攻签名，弃；② 小红书无头浏览器（Playwright）方案——太重、启动慢，放弃，改回"requests + 打码平台"轻方案。
- **为什么输出用 Markdown 而不是 Excel**：直接对接知识库 Obsidian，`[[双向链接]]` 方便，且脚本流程本来就吃 Markdown。

---

## 11. 风险与求助点

> 标 `❓` 的是**不确定、需要人工确认**的点，接手时逐个核对。

- ❓ **登录 cookie 有效期**：`config.yaml` 里的抖音 cookie 是 08-17 导出的，可能已接近 7 天有效期，做 #3 前先确认还能不能用（跑一次热榜看是否 403）。
- ❓ **快手签名算法**：A 没攻破，接手方需自行调研；存在"一周也攻不下来"的风险，备选方案是先用浏览器自动化（Playwright）过渡，但这不是首选。
- ❓ **打码平台预算**：U2 需要申请打码账号（约几十元/月），需确认运营是否批准这笔费用。
- ⚠️ **风控风险**：高频抓取可能被封号/封 IP。任何平台单日抓取建议 < 2000 条，请求间隔 ≥ 1s，必要时挂代理。
- ⚠️ **接口变更风险**：三个平台接口都可能变，代码里解析层尽量集中、加字段映射，避免改到散。
- **遇到问题找谁**：
  - 项目技术问题、接口结构 → 问 **A（谢积昌）**，接口字段对照表在 `douyin.py` 顶部注释；
  - 内容线词表怎么归纳 → 看知识库 `[[受众报告]]`；
  - 账号/cookie/打码 token → 问运营或 A，存 `config.yaml`（脱敏管理，勿外传）；
  - 服务器/Windows 计划任务 → 本地机器即可，无需服务器。

---

## 12. 常用资源清单

| 资源 | 位置 | 用途 |
|------|------|------|
| 项目入口 | `D:\ViralShortVideoCrawler\main.py` | 程序入口 |
| 配置文件 | `D:\ViralShortVideoCrawler\config.yaml` | 平台 cookie、开关、关键词（已排除 git） |
| 密钥 | `D:\ViralShortVideoCrawler\.env` | 打码平台 token 等（脱敏，勿外传） |
| 抓取模块 | `src\fetcher\douyin.py` / `xhs.py` / `kuaishou.py`(待建) | 各平台爬虫 |
| 入库 | `src\storage\sqlite_store.py` | SQLite 读写 |
| 评分 | `src\analyzer\virality_score.py` | 评分 v1/v2 |
| 导出 | `src\storage\export_md.py` | Markdown 日报 |
| 数据库 | `data\videos.db` | 1031 条视频数据 |
| 日志 | `data\logs\crawler.log` | 抓取日志，验收增量抓取看这里 |
| 测试 | `tests\` | pytest 用例，跑 `python -m pytest -q` |
| 脚本 | `scripts\setup.ps1` / `run_crawl.ps1` / `export_daily.ps1` | 环境/抓取/导出一键 |
| 知识库关联 | `总结好的大纲以及笔记/实习就业/工作文件/脚本撰写/脚本资料库/` 与 `[[受众报告]]` | 选题素材落库位置、内容线词表来源 |

---

# 附：给 Claude Code 的交接文档（AI 版 · L1 自治型）

> 本附录可直接复制给 **Claude Code**（L1 自治型智能体：能读文件、能跑命令、能自主多步推理）无缝续作。给人版在正文，本版为 AI 专属——路径、命令、函数级定位更精确，验证信号可跑。交接对象：Claude Code；能力层级：L1。

## 0. 交接摘要（启动包）

- **项目**：自动爬取短视频爆款程序（AVC）。Python + requests + SQLite。每天抓抖音等平台爆款视频 → 入库 → 评分 → 导出 Markdown 选题日报，喂给短视频脚本流程。
- **当前状态**：抖音热榜+关键词抓取、SQLite 入库去重、评分 v1、导出 v1、环境脚本、23 条 pytest 全绿。**停在"手动跑通、未自动化"**：平台只覆盖抖音，评论/内容线/定时增量/数据治理/导出分组未做。
- **A 没做完的（接力棒）**：U1 快手模块空白、U2 小红书 40%、U3 抖音评论空白（紧急）、U4 评分 v2 未做（依赖 U3）、U5 定时增量、U6 数据质量、U7 导出分组。
- **B 下一步第一件事**：先跑 `python -m pytest -q` 确认环境（期望 `23 passed`），然后做 **U3 抖音评论抓取**（它卡着 U4/U7）。
- **一句话提示**：接手后**按依赖序 #3→#4→#7，其余可并行**；所有路径前缀 `D:\ViralShortVideoCrawler\`。

## 1. 项目总览与验收标准

- **最终目标**：每天 09:00 全自动抓取 3 平台爆款 → 内容线打标 → 按四类分组导出 Markdown 选题日报，人工复核分类准确率 ≥ 80%，连续 7 天无人干预稳定运行。
- **验收标准（整体）**：`python -m pytest -q` 全绿；`data\logs\crawler.log` 连续 7 天出现 `incremental: +N new`；导出 md 含四类小节；快手/小红书入库 ≥100 条/日。

## 2. 文件地图

| 文件 | 状态 | 作用 |
|------|------|------|
| `D:\ViralShortVideoCrawler\main.py` | 已完成 | 程序入口 |
| `D:\ViralShortVideoCrawler\config.yaml` | 已完成 | cookie/开关/关键词（.gitignore 排除） |
| `D:\ViralShortVideoCrawler\requirements.txt` | 已完成 | 9 个依赖 |
| `src\fetcher\base.py` | 已完成 | 爬虫基类（重试/超时/日志） |
| `src\fetcher\douyin.py` | 已完成 | 抖音热榜+关键词，顶部注释含评论接口 URL |
| `src\fetcher\xhs.py` | 40% | 小红书列表页已完成，`fetch_detail()` 第 187 行未完成 |
| `src\fetcher\kuaishou.py` | 待建 | 快手模块空白 |
| `src\fetcher\comments.py` | 待建 | 抖音评论抓取（U3） |
| `src\storage\sqlite_store.py` | 已完成 | SQLite 读写、去重、`init_db(add_comments=...)` 可扩表 |
| `src\storage\export_md.py` | v1 完成 | `export_daily()` 第 78 行 |
| `src\storage\cleaner.py` | 待建 | 数据清洗（U6） |
| `src\analyzer\virality_score.py` | v1 完成 | `score()` 第 45 行 |
| `src\scheduler\cron_job.py` | 待建 | 增量调度（U5） |
| `data\category_rules.json` | 半成品 | 内容线词表（U4） |
| `data\videos.db` | 有数据 | 1031 条视频 |
| `data\exports\daily_2026-08-17.md` | 样例 | 导出 v1 样例 |
| `tests\` | 23 条全绿 | pytest 用例 |
| `scripts\setup.ps1 / run_crawl.ps1 / export_daily.ps1` | 已完成 | 一键脚本 |

## 3. 已完成工作（逐条含验证）

1. 项目骨架 + `BaseFetcher` 基类 → `src\fetcher\base.py`；验证：`python -m src.fetcher.base` 打印自检日志；测试 8 条。
2. 抖音热榜 Top100 + 关键词 Top50 → `src\fetcher\douyin.py`；验证：`python -m src.fetcher.douyin --hot-board` 出 JSON；累计抓回 1284 条。
3. SQLite 入库 + aweme_id 去重 → `src\storage\sqlite_store.py` + `data\videos.db`；验证：`python -m src.storage.sqlite_store --stats` 打印 `total=1031 dupes=253`。
4. 评分 v1（点赞 0.5/收藏 0.3/转发 0.2）→ `src\analyzer\virality_score.py:45`；验证：`--sample 30` 打印分布；213 条达爆款线。
5. 导出 v1 → `src\storage\export_md.py:78`；验证：`data\exports\daily_2026-08-17.md` 47 条选题。
6. 环境脚本 3 个 → `scripts\`；验证：`.\scripts\setup.ps1` 打印 `setup OK`。
7. 测试 23 条 → `tests\`；验证：根目录 `python -m pytest -q` = `23 passed`。

## 4. 当前精确进度

- 最后有效操作：2026-08-17 晚跑通「关键词搜索 → 入库 → 评分 → 导出」，产出 `daily_2026-08-17.md`（47 条，爆款 22 条）。
- 代码状态：`douyin.py`、`sqlite_store.py`、`virality_score.py`、`export_md.py` 均为 v1 可用态；`xhs.py` 列表页可用、详情页未完成；`kuaishou.py`、`comments.py`、`cleaner.py`、`cron_job.py` 不存在（待建）。
- 数据状态：`videos.db` 1031 条（抖音），`comments` 表未建，`meta` 游标表未建。

## 5. A 没做完的事（接力棒，全量逐条）

| # | 还差什么 | 为什么没做完 | 前置条件 | 优先级 | 做到什么算完成 | 从哪开始 | 验证信号 |
|---|---------|------------|---------|--------|--------------|---------|---------|
| U1 | 快手模块空白（签名+登录+解析） | client_sign 签名算法没攻破 | 解决签名/备选 Playwright；快手小号 | 重要 | 热榜 Top50+搜索 Top30，日入库 ≥100，连续 3 天不封号 | `src\fetcher\kuaishou.py`（参照 `douyin.py`） | `python -m src.fetcher.kuaishou --hot-board` 出 JSON，`sqlite_store --stats` 有 kuaishou |
| U2 | 小红书详情页未做、验证码未处理 | 需打码平台账号，无预算 | 申请超级鹰/图鉴 token 写 `.env`；小红书 cookie | 一般 | 连续 50 条详情成功、验证码 <10% | `src\fetcher\xhs.py:187` `fetch_detail()` | `--detail <id>` 返回完整指标 |
| U3 | 抖音评论抓取空白、comments 表未建 | 评论接口要登录态 cookie，时间不够 | cookie 注入 `config.yaml:douyin.cookie`；建表 | 紧急 | Top30 视频每条 ≥20 条评论入库 | `src\fetcher\comments.py`（URL 在 `douyin.py` 顶部注释） | `SELECT COUNT(*) FROM comments` >600 |
| U4 | 评分 v2：内容线分类+评论情感/互动率加权 | 依赖 U3 评论数据、词表只整理一半 | U3 完成；`category_rules.json` 补齐 | 重要 | 抽样 50 条分类准确率 ≥80%，四类覆盖 | `virality_score.py:45` + `data\category_rules.json` | `--sample 50` 打印 `acc≥0.80` |
| U5 | 定时增量：无游标、无增量逻辑、无计划任务 | 表结构没加游标，等 U4 定稿一起改 | 建 `meta` 表；config 加 `incremental: true` | 一般 | 每天 09:00 自动跑，日志 `+N new`，3 天只增不重 | `src\scheduler\cron_job.py` | 日志连续 3 天 `incremental: +N new` |
| U6 | 数据质量：模糊去重/URL 规范化/清脏数据 | 收尾活被功能开发挤后 | 无 | 一般 | `title=''` 为 0、URL 冗余为 0、输出去重率 | `src\storage\cleaner.py` | 两条 COUNT 查询返回 0 |
| U7 | 导出 v2：四类内容线分组 | 依赖 U4 的 content_line 字段 | U4 完成 | 一般 | md 出现四个小节标题、分组正确 | `export_md.py:78` | 新 md 含 `## 技术痛点型` 等四小节 |

## 6. A→B 接力总览（命令级开工清单）

| # | 接力棒 | B 要做什么 | 从哪开始（文件:行号/命令） | 做到什么算完成（验证信号） |
|---|--------|-----------|---------------------------|---------------------------|
| 1 | U1 快手空白 | 实现快手抓取（签名/登录/解析） | 新建 `src\fetcher\kuaishou.py`，参照 `douyin.py`；先攻 client_sign | `python -m src.fetcher.kuaishou --hot-board` 出 JSON；`--stats` 有 kuaishou 计数 |
| 2 | U2 小红书 40% | 补详情页+接打码 | `xhs.py:187`；token 写 `.env` | `--detail <id>` 返回完整指标；50 条连续成功 |
| 3 | U3 评论空白（先做） | 建表+抓评论（注入 cookie） | 新建 `src\fetcher\comments.py`；URL 见 `douyin.py` 顶部注释 | `SELECT COUNT(*) FROM comments` >600 |
| 4 | U4 评分 v2 | 内容线分类+情感/互动加权 | `virality_score.py:45`；补 `data\category_rules.json` | `--sample 50` 打印 `acc≥0.80` |
| 5 | U5 定时增量 | 游标+增量+计划任务 | 新建 `src\scheduler\cron_job.py`；`sqlite_store.py` 加 `meta` 表 | 日志连续 3 天 `incremental: +N new` |
| 6 | U6 数据质量 | 清洗脚本 | 新建 `src\storage\cleaner.py` | `title=''` 与 URL 冗余 COUNT 均 0 |
| 7 | U7 导出分组 | 改 export_daily 四类分组 | `export_md.py:78` | md 出现四个小节标题 |

> **接力开工第一步**：`cd D:\ViralShortVideoCrawler; python -m pytest -q` → 输出 **`23 passed`** 即环境正常、正式接上。随后执行第 7 节 #3。

## 7. 下一步行动计划（命令级，按依赖序）

> 立即做：#3 → #4 → #7（一条链）；可并行：#1、#2。之后做：#5、#6。

- **#3 抖音评论抓取（先做）**：① `sqlite_store.py` 的 `init_db()` 加 `add_comments=True` 建表；② 读 `config.yaml` 的 `douyin.cookie`（若 403 需人工刷新，见第 11 节 ❓）；③ 新建 `comments.py` 请求 `douyin.py` 顶部注释的 `/aweme/v1/web/comment/list/`，分页 20 条；④ 写 `tests\test_comments.py`。验证：`pytest -q` 全绿 + `comments` COUNT>600。
- **#4 评分 v2**：① 从知识库 `受众报告` 整理词表到 `data\category_rules.json`；② `virality_score.py` 加 `classify()` 与情感/互动率权重（点赞 0.35/收藏 0.2/转发 0.15/评论情感 0.2/互动率 0.1）；③ 抽样复核。验证：`--sample 50` 打印 `acc≥0.80`。
- **#7 导出分组**：改 `export_md.py:78`，按 `content_line` 分组输出。验证：新 md 有四小节。
- **#1 快手**：先攻签名（社区开源库或 Playwright 兜底），再按 `douyin.py` 结构实现。验证：`--hot-board` 出 JSON。
- **#2 小红书**：申请打码 token → `fetch_detail()` 补全。验证：`--detail <id>` 返回完整指标。
- **#5 定时增量**：建 `meta` 表存游标 → 抓取入口支持 `incremental` → 计划任务 09:00。验证：日志 `+N new`。
- **#6 数据清洗**：`cleaner.py` 做模糊去重/URL 规范化/清空。验证：两条 COUNT 为 0。

## 8. 环境与配置依赖

- Python 3.11+；依赖 9 个（requests、fake-useragent、python-dotenv、pytest 等），见 `requirements.txt`。
- 配置：`config.yaml`（douyin.cookie、xhs.captcha_token、kuaishou.cookie、incremental 开关）、`.env`（打码 token）。
- 数据库：`data\videos.db`（SQLite，无服务依赖）。
- 密钥/凭证：cookie 与 token 存 `config.yaml`/`.env`，值已脱敏 `<已脱敏>`，勿外传、勿 commit。
- Windows 计划任务（U5 时配）：每天 09:00 跑 `scripts\run_crawl.ps1 -incremental`。

## 9. 数据与状态快照

- `videos.db`：1031 条（抖音），213 条评分≥70；`comments` 表、`meta` 游标表未建。
- `category_rules.json`：半成品，需补全四类词表。
- 临时数据：无需要清理的；`data\logs\crawler.log` 保留，验收增量抓取要用。

## 10. 关键决策与踩坑记录

- 决策：Python+SQLite（轻量零部署）；先抖音后快手小红书；评分先简版后 v2；导出用 Markdown 对接 Obsidian。
- 坑：重复抓取 253 条（已用 aweme_id 去重修复）；抖音 cookie 7 天过期（返回 403）；字段名偶变（用映射表）；快手纯伪造请求头绕不过签名（放弃）。

## 11. 风险与待确认项

- ❓ `config.yaml` 抖音 cookie 有效期（08-17 导出，可能需刷新）。
- ❓ 快手 client_sign 算法需自行调研，存在"攻不下来"风险（备选 Playwright）。
- ❓ 打码平台账号/预算需运营确认。
- ⚠️ 各平台风控：单日 <2000 条、间隔 ≥1s、必要时挂代理。

## 12. 续作启动手册

1. `cd D:\ViralShortVideoCrawler`
2. 若环境未建：`.\scripts\setup.ps1`（或 `pip install -r requirements.txt`）。
3. 验证续上：`python -m pytest -q` → **`23 passed`**（这就是"续上了"的证明信号）。
4. 先读 `src\fetcher\douyin.py` 顶部注释（含评论接口 URL 与字段映射），再动 #3。
5. 遇到歧义回看第 5-6 节接力棒与总览表；❓ 项主动向用户确认。

## 13. 按 Claude Code 定制

- 你是 L1 自治型：能读文件、能跑命令，故本版给"精确路径+命令+函数级定位"而不贴大段代码；需要贴内容时你自己去读对应文件。
- 建议在项目根目录新建 `D:\ViralShortVideoCrawler\CLAUDE.md`，把"平台优先级、四类内容线、去重/风控纪律（单日<2000条、间隔≥1s）、config.yaml 勿提交"写成规则，让后续每次会话自动遵守。
- 任务量大（#1 快手攻签名、#4 词表整理）时可派生子代理并行。
- 第 6 节接力总览即开工清单，按 #3 的"从哪开始"执行即可，无需再问人。
