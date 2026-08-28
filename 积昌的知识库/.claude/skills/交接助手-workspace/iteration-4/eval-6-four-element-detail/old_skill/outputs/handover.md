# 自动爬取短视频爆款程序 交接文档（给人版）

> **一句话定位**：这是一个每天自动去抖音、小红书、快手抓取热门短视频，用一套"爆款指数"公式给每条视频打分、去重，最后把最有潜力成为爆款的视频推送到飞书群里、并能在网页看板上查看结果的程序。
>
> **阅读指引**：这份文档按"先看懂 → 知道做到哪 → 知道该干什么 → 知道怎么干"的顺序组织。**第一次读请按顺序通读第 1~5 节**，对项目有个整体认识；**准备接手干活前，精读第 6、7 节**（已做完什么、还差什么），然后**照着第 8 节的接力总览表从 #1 开始动手**；干的过程中卡住了再回头查第 9~12 节（手把手步骤、踩坑、求助点、资源清单）。第 8 节是整份文档的核心，务必重点看。

| 元信息 | 内容 |
|---|---|
| **项目名** | 自动爬取短视频爆款程序（内部代号：`hot_video_crawler`） |
| **交接对象** | 人（下一位开发者 / 接手同事）＋ AI 智能体（附录为 Claude Code 版） |
| **交接日期** | 2026-08-18 |
| **交接原因** | 原开发者（A）临时转岗，项目处于"能单平台跑通、多平台未齐"的阶段，需要接任者（B）继续完成 |
| **项目位置** | `D:\workspace\hot_video_crawler`（Windows 开发机）；服务器待部署 |

---

## 1. 这份文档是给谁看的

- **写给谁**：接下这个项目的人——可能是你的同事、未来的你自己，也可能是接手的新人。文档假定你**没参与过**这个项目的开发，所以术语、背景、每一步都会讲透。
- **为什么交接**：原开发者 A 因为转岗要在 2026-08-19 前把手上的活交出去。项目**不是从头做**，而是做到一半（约 55%），需要你接着往下做。
- **读完你应该能达到的效果**：
  - 能不看任何人的脸色，自己回答出"这项目是干嘛的、做到哪了、还差什么、下一步干什么"；
  - 能照着本文档从零把开发环境跑起来，看到日志里出现预期的输出；
  - 能照着接力总览表，把抖音的遗留问题修完，把小红书、快手的爬虫补上，把看板做出来；
  - 遇到问题时知道翻哪个文档、跑哪条命令、找谁问。

---

## 2. 项目总览（大白话）

这个项目说白了就是三句话：

1. **去各大短视频平台"逛街"**：每天定时打开抖音、小红书、快手，去话题榜、热搜榜、达人主页抓最新的热门视频信息（标题、文案、作者、点赞数、评论数、转发数、时长等）；
2. **给抓到的每条视频"打分"**：用一套加权公式算出"爆款指数"，分数越高说明越可能火；同时用"相似度比对"把内容几乎一样的老视频去掉，避免重复推送；
3. **把值得看的推给你**：分数超过阈值的视频，自动推到飞书群里，方便团队选素材、追热点、抄选题。

- **为谁做**：给内容运营/短视频选题团队用的内部工具，减少人工刷平台找素材的时间。
- **解决什么问题**：人工逐个平台翻找爆款耗时、容易漏；把"找素材"从人肉变成自动，每天固定时间出结果。
- **项目价值**：每天约省 2~3 人小时的选题时间；让团队能在 10 点前看到当天全平台热点。
- **整体完成度**：约 **55%**。判断依据：
  - ✅ 抖音单平台链路已跑通（采集→解析→打分→去重→入库→通知），有实测数据；
  - ❌ 小红书签名算法未实现、快手完全没写、网页看板只有空壳、调度与爬虫联调未验证、未部署到服务器。

---

## 3. 背景与来龙去脉

- **项目怎么来的**：2026-07 月初，运营部门提需求——"现在每天刷抖音找选题要花大半天，能不能搞个自动的"。A 在 07-10 立项，07-15 搭好骨架，开始一个平台一个平台地啃。
- **为什么先做抖音**：抖音的接口相对好逆（早期抓包就能拿到热门接口，不需要太复杂的签名），验证整套流程最快，所以 A 先用抖音把"数据从抓取到入库到通知"的完整管道打通，再复制到其他平台。
- **关键约束与用户偏好**：
  - 跑在 **Windows 开发机**上，最后要能部署到一台普通 Windows 服务器（团队没有 Linux 运维能力）；
  - 数据存 **SQLite**（先本地单机跑通，后期可换 MySQL），避免一上来就引入数据库运维成本；
  - 通知走**飞书自定义机器人**（webhook），因为团队日常工作在飞书里；
  - 老板明确要求"宁可慢一点，也不能因为爬太快被封号"——所以采集频率要克制，要带随机延迟。
- **和团队其他事情的关系**：这个程序产出的爆款清单会喂给脚本组（华哥脚本撰写）当选题素材，也和运营周报里的"热点追踪"章节挂钩。

---

## 4. 术语表

| 术语（英文/缩写） | 大白话解释 |
|---|---|
| **爆款指数（hot_score）** | 给一条视频打的综合分，由点赞、评论、转发、完播率按权重算出来，0~100 分，越高越可能火 |
| **SimHash 去重** | 一种"内容相似度"算法，把文案变成一串指纹，指纹相近就认为是同一条内容，用于去掉搬运/蹭热点的重复视频 |
| **签名算法（x-s / X-Sign）** | 小红书、抖音等平台为了防止被程序批量抓取，在请求里加的"暗号"，程序必须算出正确的暗号才能通过校验；每个平台算法都不同，是最难啃的部分 |
| **Cookie 有效期** | 平台登录凭证的有效期，过期后程序会被判定为"游客"甚至拦截；抖音的游客 Cookie 一般几天就失效 |
| **滑块验证码** | 抖音/小红书常见的"拖动拼图"验证，被识别成机器时会弹出，需要人工或第三方打码服务处理 |
| **webhook** | 一个"回调网址"，往这个网址发一条消息，飞书群里就会收到；本文档里指飞书机器人地址 |
| **APScheduler** | Python 的定时任务库，让程序能"每天 9 点自动跑一次" |
| **FastAPI** | Python 的一个网页框架，用来做看板的后端接口 |
| **cron 表达式** | 描述"多久跑一次"的写法，如 `0 9 * * *` = 每天 9 点 |
| **ORM 模型（models.py）** | 用 Python 类描述数据库表结构，程序里操作对象就相当于操作数据库表 |
| **E2E（端到端）测试** | 从"真实抓取"到"真实入库"全流程跑一遍的测试，验证整条链路而不是单个函数 |
| **阈值（threshold）** | 一个分数线，比如"爆款指数 ≥ 70 才推送" |

---

## 5. 当前进度（用"人话"讲）

- **整体阶段**：单平台（抖音）可跑通的"原型→可用"过渡阶段。管道已经通了，但**平台覆盖面、稳定性、可视化都还没到位**。
- **最后一次停在什么位置**：2026-08-17 晚上，A 手动跑了一次抖音采集，成功抓回 42 条热门视频、解析后入库 40 条（2 条因字段缺失被丢弃），飞书群里也收到了推送。但这次跑完后发现**抖音的 Cookie 已经临近过期**，如果明天不处理，采集会开始失败。这是你接手后要处理的第一个问题。
- **一句话概括现状**：**"抖音能跑但会断、小红书差签名、快手没动、看板没有、没部署。"**

---

## 6. 已完成工作（全量逐条）

以下按模块分组，每条都给了"产出物在哪、怎么验证它确实有效"。

### 6.1 项目骨架与工程化（完成 100%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.1.1 | 建立项目目录结构、统一配置入口 | `D:\workspace\hot_video_crawler\config\config.yaml`、`config\platforms.yaml` | 运行 `python src/main.py --check-config` 会打印配置摘要，无报错 |
| 6.1.2 | 日志系统（按天滚动、控制台+文件双输出） | `src/utils/logger.py`；日志落盘 `logs\crawler.log` | 跑任何模块，日志目录都会按 `crawler_20260818.log` 格式生成当天文件 |
| 6.1.3 | 依赖清单 | `requirements.txt` | `pip install -r requirements.txt` 能一次装齐 |

### 6.2 抖音爬虫（完成约 90%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.2.1 | 实现 `DouyinCrawler`，能按话题/榜单页抓取视频列表 | `src/crawler/douyin.py` 中类 `DouyinCrawler`，核心方法 `fetch_hot_list()` | 手动跑 `python src/main.py --crawl douyin --limit 20`，终端打印 20 条视频 JSON，字段含 `video_id/author_id/title/like_count` 等 |
| 6.2.2 | 登录态维护：读取本地 Cookie 文件、过期自动提示 | `src/crawler/douyin.py` 的 `_load_cookie()` / `_refresh_cookie()`；Cookie 存 `config\cookies\douyin_cookie.txt` | 删除 Cookie 文件后跑一次，日志出现 `[WARN] douyin cookie missing`，说明检测逻辑生效 |
| 6.2.3 | 随机延迟 + 请求头伪装，降低封号风险 | `src/crawler/base.py` 的 `_sleep_random()`、`_fake_headers()` | 观察日志里两次请求时间差在 3~8 秒随机波动 |
| 6.2.4 | 单条视频详情（含完播率近似值） | `src/crawler/douyin.py` 的 `fetch_video_detail()` | 对已知视频 id 调用，返回 `play_rate`（完播率）字段 |

### 6.3 内容解析（完成 100%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.3.1 | 把平台原始 JSON 标准化成统一 Video 结构 | `src/parser/content_parser.py` 的 `parse_video()` | `python tests/test_parser.py` 通过（15 条用例） |
| 6.3.2 | 标题清洗（去 emoji、去 #话题 标签、去无意义符号） | 同文件 `clean_title()` | 对含 emoji 的标题调用，返回纯文本；测试已覆盖 |

### 6.4 爆款指数打分（完成 100%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.4.1 | 实现加权打分公式：`hot_score = 赞*0.4 + 评论*0.25 + 转发*0.2 + 完播*0.15`（归一化到 0~100） | `src/scoring/hot_score.py` 的 `compute_hot_score(video)` | `python tests/test_scoring.py` 通过（12 条用例）；对点赞 1 万、评论 800 的视频能算出 80 分左右 |
| 6.4.2 | 阈值可配置 | `config/config.yaml` 的 `scoring.threshold`（当前 70） | 修改阈值后重启，推送行为随之变化 |

### 6.5 去重（完成 90%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.5.1 | SimHash 指纹计算与汉明距离比对 | `src/scoring/dedup.py` 的 `simhash()` / `is_duplicate()` | `python tests/test_dedup.py` 通过（9 条用例）；两条 90% 相似文案会被判重 |
| 6.5.2 | 指纹缓存（避免重复计算） | `data\dedup_cache\fingerprint.jsonl` | 跑两次相同数据，第二次日志出现 `[INFO] dedup cache hit` |

### 6.6 存储（完成 100%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.6.1 | SQLite 建表与 ORM 模型（Video / Comment / Trend） | `src/storage/models.py`；数据库文件 `data\videos.db` | `python -c "import sqlite3; c=sqlite3.connect('data/videos.db'); print(c.execute('select count(*) from videos').fetchone())"` 能查到行数 |
| 6.6.2 | 入库与去重后的 upsert 逻辑 | `src/storage/db.py` 的 `save_videos()` | 重复插入同一 video_id 不会产生第二条记录 |

### 6.7 飞书通知（完成 100%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.7.1 | 组装并发送飞书机器人消息（卡片格式，含标题/分数/链接） | `src/notify/notifier.py` 的 `send_douyin_digest()` | 2026-08-17 实测：飞书"爆款监控"群收到一条带 5 条视频的卡片推送 |

### 6.8 调度器（完成 80%）

| # | 做了什么 | 产出物位置 | 怎么验证有效 |
|---|---|---|---|
| 6.8.1 | APScheduler 定时任务框架，cron 配置可读 | `src/scheduler.py` 的 `build_scheduler()` | 启动 `python src/main.py --scheduler` 后，控制台打印"下一执行时间" |
| 6.8.2 | 单次任务包装（把采集→解析→打分→入库→通知串成一条 job） | `src/scheduler.py` 的 `run_once()` | 手动触发该 job，日志按顺序出现 5 个阶段标记 |

> ⚠️ **注意**：6.8 的调度器**只验证了"能启动、能手动触发"**，还没有让它**无人值守地跑一个完整周期**（见 7.7）。

---

## 7. A 没做完的事（需要你接力的，全量逐条）

> 先说明：**下面这些"没做完"是前任 A 留下的"接力棒"，是你工作的起点，不是你的过错。** 你不需要为"为什么没做完"背锅，只需要按第 8 节的接力总览一条条接上。

每条按**七要素**写全：**①还差什么 ②为什么没做完（阻塞原因）③前置条件 ④优先级 ⑤做到什么程度算完成 ⑥从哪开始（开工入口）⑦怎么验证**。

---

### 接力棒 #1：抖音 Cookie 过期问题（最紧急，会直接导致采集断供）

- **①还差什么**：抖音登录态到期后，程序只会打 `[WARN] cookie missing` 并**中止本轮采集**，没有一个"自动续期 / 人工引导刷新"的闭环。
- **②为什么没做完（阻塞原因）**：抖音的 Cookie 刷新接口需要过滑块验证码，纯代码没法稳定通过；A 前期把精力放在打通主流程上，把"续期"压到最后一刻，结果最后一天 Cookie 刚好临期，没来得及做兜底。
- **③前置条件**：需要抖音账号能登录；如果走第三方打码服务，需要申请一个打码平台的 token。
- **④优先级**：🔴 **紧急**（P0）——明天（08-19）9 点定时任务一跑就可能断。
- **⑤做到什么程度算完成**：Cookie 过期时，程序能**自动**走一次"刷新→重新登录"；刷新成功就继续采集；刷新失败则**发送飞书告警**并明确提示"请人工扫码"，而不是静默中止。
- **⑥从哪开始**：`src/crawler/douyin.py` 的 `_refresh_cookie()`（约 188 行）和 `fetch_hot_list()` 开头（约 210 行）的 Cookie 检查分支。
- **⑦怎么验证**：把 `config\cookies\douyin_cookie.txt` 里的内容改成一行乱码，跑 `python src/main.py --crawl douyin --limit 5`，应看到：①日志出现 `[INFO] cookie invalid, trying refresh`；②随后要么成功抓取，要么收到飞书"请人工扫码"告警。

---

### 接力棒 #2：小红书爬虫只有壳，签名算法未实现（核心未完成项）

- **①还差什么**：`XiaohongshuCrawler` 目前只有类骨架，`fetch_hot_list()` 是 `raise NotImplementedError`；小红书请求头必须带 `x-s` 签名和 `x-t` 时间戳，否则接口一律返回 `{"code":-100}`（签名校验失败）。
- **②为什么没做完（阻塞原因）**：小红书的 `x-s` 签名是**前端 JS 加密**，需要逆向它的加密流程（webpack 打包的 JS 里有一大段混淆代码），A 卡了两天，因为优先保抖音的进度而搁置。
- **③前置条件**：需要一台能访问小红书的网络环境（国内 IP 即可）；需要把小红书 APP / 网页版抓包工具（Fiddler/Charles）配置好，用于核对签名结果。
- **④优先级**：🟠 **重要**（P1）——项目价值的一半在"多平台覆盖"，小红书是第二个目标平台。
- **⑤做到什么程度算完成**：`fetch_hot_list()` 能返回 ≥20 条小红书热门笔记（含标题、作者、点赞、评论、转发、发布时间），字段与 `content_parser.parse_video()` 兼容；且 1 小时内连续调用不被风控拦截。
- **⑥从哪开始**：`src/crawler/xiaohongshu.py` 全文（约 60 行，全是 TODO）；签名问题建议先读 `docs/xhs_signature_notes.md`（A 留下的逆向笔记）和抓包记录 `data/raw/xhs_capture_sample.json`。
- **⑦怎么验证**：`python src/main.py --crawl xiaohongshu --limit 20`，终端打印 20 条笔记 JSON，无 `-100` 错误；随后 `python tests/test_xiaohongshu.py`（需你补写）通过。

---

### 接力棒 #3：快手爬虫完全没写（纯空文件）

- **①还差什么**：`kuaishou.py` 只是 `git` 里一个空占位文件，`KuaishouCrawler` 类、接口方法、请求头、签名全都没有。
- **②为什么没做完（阻塞原因）**：排期上快手本来就放在小红书之后，A 在转岗前没排到。
- **③前置条件**：参考抖音、小红书的实现模式（继承 `BaseCrawler`），需要先确认快手网页版的抓包接口可用。
- **④优先级**：🟡 **一般**（P2）——三平台里优先级最低，建议在抖音、小红书稳定后做。
- **⑤做到什么程度算完成**：能抓取快手热门视频列表并入库、能被 `content_parser` 解析、能参与打分推送；验收标准同小红书（≥20 条、字段兼容、不触发风控）。
- **⑥从哪开始**：`src/crawler/kuaishou.py`（先读 `base.py` 的 `BaseCrawler` 接口约定，再照 `douyin.py` 的模式抄结构）。
- **⑦怎么验证**：`python src/main.py --crawl kuaishou --limit 20` 返回 20 条数据并正常入库。

---

### 接力棒 #4：评论采集只做了基础抓取，没有情感分析（半成品）

- **①还差什么**：`comment_parser.py` 只能抓取评论原文，`analyze_sentiment()` 是空函数——"评论是正向还是负向"这个信号目前完全没用上，而爆款指数里本来想加一个"评论情绪热度"的加成。
- **②为什么没做完（阻塞原因）**：情感分析需要接一个中文情感模型或词典，A 没有来得及选型，也不确定是"本地词典"还是"调第三方 API"（后者要花钱、要申请 key）。
- **③前置条件**：需要先和运营确认"情绪加成"是不是刚需（如果团队不看情绪，这个可以降优先级）。
- **④优先级**：🟡 **一般**（P2）——锦上添花，不影响主链路。
- **⑤做到什么程度算完成**：`analyze_sentiment(text)` 返回 `positive/neutral/negative` 三态之一，且对 100 条人工标注样本的准确率 ≥ 0.75；`comment_parser.py` 有配套单测。
- **⑥从哪开始**：`src/parser/comment_parser.py` 的 `analyze_sentiment()`（约 40 行空实现）；选型建议先看 `docs/sentiment_choice_notes.md`（A 列的两种方案的利弊）。
- **⑦怎么验证**：`python tests/test_comment_parser.py` 通过；对"这个视频绝了"返回 positive、对"太烂了"返回 negative。

---

### 接力棒 #5：网页看板（FastAPI）只有空骨架（重要可视化缺口）

- **①还差什么**：`src/dashboard/app.py` 只有一个 FastAPI 实例和 `/` 健康检查，没有页面、没有接口；运营想要"打开网页就能看今日爆款 Top50"，现在只能看飞书推送。
- **②为什么没做完（阻塞原因）**：看板是"锦上添花"排在爬虫之后；A 把时间都给了爬虫主体，看板一直没排上。
- **③前置条件**：数据已入库（`data\videos.db`），所以看板可以直接基于 SQLite 读，不需要额外依赖。
- **④优先级**：🟠 **重要**（P1）——老板点名要"能在网页上看"，是上线前的验收项之一。
- **⑤做到什么程度算完成**：`python src/main.py --dashboard` 启动后，浏览器打开 `http://127.0.0.1:8000` 能看到：①今日爆款 Top50 列表（按 hot_score 排序）；②每行有标题、平台、分数、链接；③按平台筛选的下拉框；④刷新按钮。数据来自 SQLite，不用造假。
- **⑥从哪开始**：`src/dashboard/app.py`（约 25 行）；模板目录 `src/dashboard/templates/`（目前为空，需新建 `index.html`）；接口逻辑可参考 `src/storage/db.py` 里已有的 `query_top_videos()`（它已经实现了 TopN 查询）。
- **⑦怎么验证**：启动后 `curl http://127.0.0.1:8000/api/top?limit=50` 返回 JSON 且含 `hot_score` 字段；页面能正常渲染 50 条。

---

### 接力棒 #6：调度器与爬虫的无人值守联调没验证（上线拦路虎）

- **①还差什么**：`scheduler.py` 能启动、能手动触发，但**没有完整跑过一个"定时触发 → 全流程 → 推送"的无人值守周期**；也没验证"采集失败时会不会重试、重试几次、失败后会不会告警"。
- **②为什么没做完（阻塞原因）**：要等抖音 Cookie 问题（#1）先解决才能跑无人值守，否则定时跑只会连续失败；属于"被阻塞的依赖项"。
- **③前置条件**：#1（Cookie 续期）完成，且飞书 webhook 可发。
- **④优先级**：🔴 **紧急**（P0，与 #1 并列）——不验证，就不能放心让它每天自动跑。
- **⑤做到什么程度算完成**：把调度设为"每 5 分钟跑一次"，连续观察 1 小时：①每次触发都完整走完 5 阶段日志；②模拟一次网络断开，看到自动重试（默认 3 次）且最终发出失败告警；③期间数据库新增记录持续增长。
- **⑥从哪开始**：`src/scheduler.py` 的 `run_once()`（约 95 行）和 `config/config.yaml` 的 `scheduler.cron`（当前 `0 9 * * *`）。
- **⑦怎么验证**：`python src/main.py --scheduler` 后看日志，连续 12 个周期无异常；手动拔网线一次，观察重试与告警日志。

---

### 接力棒 #7：数据导出功能未实现（运营要 Excel）

- **①还差什么**：`data\exports\` 是空目录，程序没有任何"导出 CSV/Excel"的能力；运营每周要一份"本周爆款汇总表"，目前靠手工从飞书消息里复制，很痛苦。
- **②为什么没做完（阻塞原因）**：优先级一直被排后，属于"想做的很多、时间不够"。
- **③前置条件**：数据已入库（已具备）。
- **④优先级**：🟡 **一般**（P2）——不影响主链路，但影响运营的每周产出效率。
- **⑤做到什么程度算完成**：`python src/main.py --export --week 2026-08-10` 在 `data\exports\` 生成 `爆款汇总_20260810.xlsx`，含 Sheet1（Top 视频明细）、Sheet2（按平台汇总），能直接用 Excel 打开。
- **⑥从哪开始**：`src/storage/export.py`（需新建）；可参考 `requirements.txt` 里预留的 `openpyxl` 依赖。
- **⑦怎么验证**：生成后打开文件，行数与 `SELECT count(*) FROM videos WHERE ...` 一致。

---

### 接力棒 #8：部署到服务器 / 常驻运行（上线最后一公里）

- **①还差什么**：程序只在 A 的 Windows 开发机上手动跑过；没有部署文档、没有 Windows 计划任务（Task Scheduler）配置、没有开机自启、没有日志轮转清理方案。
- **②为什么没做完（阻塞原因）**：一切要等主流程稳定（#1、#6）才敢部署，否则部署了也是天天失败。
- **③前置条件**：#1、#6 完成后才建议做；需要一台 Windows 服务器（团队有 Windows Server 2019，可用远程桌面登录）。
- **④优先级**：🟠 **重要**（P1，但排在 #1/#6 之后）——这是"能每天自动跑"的最后一步。
- **⑤做到什么程度算完成**：在服务器上用"任务计划程序"注册一个每天 09:00 触发、运行 `python src\main.py --scheduler` 的计划任务；服务器重启后任务仍在；日志写到 `logs\` 且自动滚动保留 7 天。
- **⑥从哪开始**：`docs/DEPLOY_WINDOWS.md`（需你新建，A 还没写）；服务器信息见第 11 节"求助点"。
- **⑦怎么验证**：把服务器时间手动改到 09:01 等触发，看到日志出现"任务启动"且飞书收到推送；重启服务器后确认任务还在。

---

### 接力棒 #9：采集失败重试与告警策略不完善（稳定性缺口）

- **①还差什么**：目前只有最基础的重试（`base.py` 里 `retry_count=3` 是写死的），没有"退避策略"（失败后逐渐拉长间隔）、没有"连续失败 N 次就停一天"的熔断、告警也只覆盖抖音。
- **②为什么没做完（阻塞原因）**：属于"稳定性打磨"，A 原计划在三个平台都通了之后再统一做，现在提前转岗。
- **③前置条件**：无硬性前置，可与 #2/#3 并行推进。
- **④优先级**：🟡 **一般**（P2）。
- **⑤做到什么程度算完成**：`config/config.yaml` 里有 `retry.max_attempts / retry.backoff_seconds / retry.circuit_break_count` 三个可配置项；连续失败 5 次后当日自动停采并发送飞书告警"今日已熔断"。
- **⑥从哪开始**：`src/crawler/base.py` 的 `_fetch_with_retry()`（约 66 行）。
- **⑦怎么验证**：把接口地址改成错误地址，连续触发，观察第 5 次后日志出现熔断标记、飞书收到告警。

---

## 8. A→B 接力总览（读到就能开工，核心）

> 这张表把"**A 没做完的（接力棒）**"和"**B 接下来要做的（接力任务）**"一一钉死。**照着 #1 往下做就行，不用问任何人。** 每条都给了"从哪开始"和"做到什么算完成（怎么验证）"。

| # | A 没做完的（接力棒） | 你（B）接下来要做什么 | 从哪开始（文件/工具/找谁） | 做到什么算完成（怎么验证） |
|---|----------------------|----------------------|---------------------------|---------------------------|
| 1 | 抖音 Cookie 过期会静默中断 | 给 Cookie 加"自动续期 + 失败告警"闭环 | `src/crawler/douyin.py:188` `_refresh_cookie()`；`:210` 检查分支 | 乱码 Cookie 后跑 `python src/main.py --crawl douyin --limit 5`，看到续期或飞书"请扫码"告警 |
| 2 | 小红书签名（x-s/x-t）未实现，`fetch_hot_list()` 抛 NotImplementedError | 逆向小红书签名，实现 `XiaohongshuCrawler.fetch_hot_list()` | `src/crawler/xiaohongshu.py` 全文；参考 `docs/xhs_signature_notes.md` | `python src/main.py --crawl xiaohongshu --limit 20` 返回 20 条 JSON，无 `-100` |
| 3 | 快手爬虫是空文件 | 照抖音模式实现 `KuaishouCrawler` | `src/crawler/kuaishou.py`；先读 `base.py` 的接口约定 | `python src/main.py --crawl kuaishou --limit 20` 返回 20 条并入库 |
| 4 | 评论情感分析是空函数 | 选型（本地词典 vs 第三方 API）并实现 `analyze_sentiment()` | `src/parser/comment_parser.py:40`；选型见 `docs/sentiment_choice_notes.md` | 单测通过；"绝了"→positive，"太烂了"→negative |
| 5 | 网页看板只有空壳 | 实现 FastAPI 看板（Top50 列表 + 平台筛选） | `src/dashboard/app.py`；模板 `src/dashboard/templates/index.html`（新建） | `curl http://127.0.0.1:8000/api/top?limit=50` 返回含 `hot_score` 的 JSON |
| 6 | 调度器无人值守联调没验证 | 验证"定时触发→全流程→推送"连续 1 小时稳定，补重试/熔断 | `src/scheduler.py:95` `run_once()`；`config/config.yaml` 的 `scheduler.cron` | 每 5 分钟触发，连续 12 周期无异常；断网一次能看到重试+告警 |
| 7 | 数据导出未实现 | 实现导出 Excel（周爆款汇总） | `src/storage/export.py`（新建）；依赖 `openpyxl` | `python src/main.py --export --week 2026-08-10` 生成可打开的 xlsx |
| 8 | 未部署到服务器 | 写部署文档 + 配 Windows 计划任务常驻 | `docs/DEPLOY_WINDOWS.md`（新建）；服务器见求助点 | 服务器 09:00 自动触发，飞书收到推送，重启后任务仍在 |
| 9 | 重试/熔断/告警策略不完善 | 把重试参数配置化，加连续失败熔断+告警 | `src/crawler/base.py:66` `_fetch_with_retry()` | 错地址连续触发，第 5 次熔断并收到飞书告警 |

> **🚀 接力开工第一步**：打开 `D:\workspace\hot_video_crawler`，在命令行执行 `python src/main.py --check-config`，看到打印出"抖音/小红书/快手 + 数据库 + 飞书 webhook"的配置摘要且无报错——**出现这个输出，说明你已经正式接上，可以开始 #1 了**。如果这一步就报错，先看第 12 节"常用资源清单"里的环境安装，再回头跑。

---

## 9. 下一步怎么做（手把手）

> 承接第 8 节接力总览，把"你接下来要做的"展开成**普通人能照做**的步骤。**先做立即做的事，再做之后的事。**

### 立即做（接手第一周内）

**第 1 步：把环境跑起来，验证"接上了"**
1. 打开命令行（Win+R 输入 `cmd` 回车），输入 `cd /d D:\workspace\hot_video_crawler` 回车；
2. 输入 `pip install -r requirements.txt` 回车，等它装完（看到 `Successfully installed ...` 说明成功）；
3. 输入 `python src/main.py --check-config` 回车。**看到配置摘要且没有红色报错 = 第 1 步做对了。** 如果提示缺少 Python，先装 Python 3.10+，勾选"Add to PATH"。
4. **卡住了看哪**：`docs/README.md`（A 写的环境安装说明）；还不行就找韩玲（见求助点）要环境快照。

**第 2 步：处理抖音 Cookie 过期（接力棒 #1）**
1. 打开 `src\crawler\douyin.py`，翻到约 188 行的 `_refresh_cookie()`；
2. 在函数里补上"读取新 Cookie → 写回 `config\cookies\douyin_cookie.txt` → 返回 True"的逻辑（你可以在函数里调一个手动引导：把浏览器里 F12 → Application → Cookies 里的值复制进文件）；
3. 在 `fetch_hot_list()` 开头（约 210 行）把"Cookie 无效就 `raise`"改成"先尝试 `_refresh_cookie()`，失败才发飞书告警并中止"；
4. 验证：把 Cookie 文件改成乱码，跑 `python src/main.py --crawl douyin --limit 5`。**看到 `[INFO] cookie invalid, trying refresh` 且最终能抓到数据（或收到告警）= 做对了。**
5. 卡住了看 `docs/cookie_notes.md` 和踩坑记录第 10 节 10.2。

**第 3 步：跑通无人值守联调（接力棒 #6）**
1. 打开 `config\config.yaml`，把 `scheduler.cron` 临时改成 `*/5 * * * *`（每 5 分钟）；
2. 跑 `python src/main.py --scheduler`，让它挂机 1 小时；
3. **看到每 5 分钟出现一次完整的"5 阶段日志"（采集→解析→打分→入库→通知），且数据库 `videos` 表行数持续增长 = 做对了。** 中途故意断网一次，应看到自动重试和最终告警。

### 之后做（第一周后，按优先级）

**第 4 步：实现小红书签名（接力棒 #2）**
1. 先读 `docs/xhs_signature_notes.md` 和 `data/raw/xhs_capture_sample.json`，理解抓包里 `x-s` 是怎么算的；
2. 在 `src/crawler/xiaohongshu.py` 里实现签名生成函数 `_gen_sign(params, ts)`；
3. 实现 `fetch_hot_list()`，把签名塞进请求头；
4. 验证：`python src/main.py --crawl xiaohongshu --limit 20` 返回 20 条数据。**没有 `-100` 错误 = 做对了。**
5. 卡住了找谁：`docs/xhs_signature_notes.md` 里的备注写了 A 求助过的一个逆向交流群。

**第 5 步：做网页看板（接力棒 #5）**
1. 打开 `src/storage/db.py`，找到 `query_top_videos()`，确认它返回 `(video_id, title, platform, hot_score, url)`；
2. 在 `src/dashboard/app.py` 加一个 `/api/top` 接口调用它；
3. 新建 `src/dashboard/templates/index.html`，用表格渲染 + 平台下拉筛选；
4. 验证：`python src/main.py --dashboard` 后浏览器开 `http://127.0.0.1:8000`，能看到 Top50 且能按平台筛选。

**第 6 步以后（按需）**：快手爬虫（#3）→ 评论情感分析（#4）→ 数据导出（#7）→ 重试熔断完善（#9）→ 部署服务器（#8）。每一条的做法都在第 7 节里写清了"从哪开始 + 怎么验证"，按图索骥即可。

> **做任何一步之前**，先确认 `data\videos.db` 有数据（`python -c "import sqlite3;c=sqlite3.connect('data/videos.db');print(c.execute('select count(*) from videos').fetchone())"`），否则先跑一次抖音采集。

---

## 10. 关键决策与踩坑记录

### 10.1 关键决策（为什么这么选）

| 决策 | 选择 | 理由（大白话） |
|---|---|---|
| 先做抖音 | 抖音 → 小红书 → 快手 | 抖音接口最好逆，先用它把"整条管道"打通，再复制到其他平台 |
| 数据库用 SQLite | SQLite，暂不上 MySQL | 单机跑、无 DBA，SQLite 零运维；后期量大再换 |
| 通知走飞书 webhook | 飞书机器人卡片 | 团队日常在飞书，卡片能带标题/分数/链接，一眼可扫 |
| 打分用加权公式 | 赞0.4/评论0.25/转发0.2/完播0.15 | 简单、可解释，运营能听懂；后期可换机器学习 |
| 采集加随机延迟 | 3~8 秒随机 | 老板明确要求"宁慢勿封号"，这是硬约束 |
| 框架选 APScheduler + FastAPI | 都是 Python 生态轻量方案 | 不引入 Celery/Node 等重型依赖，单人可维护 |

### 10.2 踩过的坑（最值钱的部分）

**坑 1：抖音接口返回 `-8888` 风控码**
- **现象**：连续请求约 30 次后，接口开始返回 `{"code":-8888,"msg":"验证码"}`，数据全空。
- **根因**：请求频率太高、且请求头里少了 `Referer` 和 `User-Agent` 的完整伪装。
- **怎么避开**：①已加的随机延迟别去掉；②`_fake_headers()` 里必须带 `Referer: https://www.douyin.com/`；③如果出现 `-8888`，立刻停止 10 分钟，别硬重试。

**坑 2：Cookie 文件是 UTF-8 带 BOM，导致匹配失败**
- **现象**：明明复制了正确的 Cookie，程序却说"无效"。
- **根因**：文本编辑器存文件时加了 BOM 头（`﻿`），程序按字符串对比时首字符不匹配。
- **怎么避开**：读 Cookie 时用 `open(path, encoding='utf-8-sig')`；或者存 Cookie 前用 VS Code 右下角把编码切成"UTF-8（无 BOM）"。这个坑 A 已修进 `_load_cookie()`，**你改动时不要"顺手"改回 `utf-8`**。

**坑 3：飞书 webhook 发送后 20 分钟才到群**
- **现象**：手动测试时消息延迟很久。
- **根因**：往 webhook 发消息时带了自定义 `msg_type: interactive` 卡片但字段不完整，飞书走了低优先级队列。
- **怎么避开**：卡片字段必须齐全（`title/body/url`），且不能把同一个 webhook 并发轰炸。A 已经把 `notifier.py` 改好，**你不要再加"重试发送"的循环**，否则会触发飞书限流。

**坑 4：SQLite 在 Windows 上偶发 "database is locked"**
- **现象**：调度任务和手动跑同时写库时报锁。
- **根因**：两个连接同时写同一个 SQLite 文件。
- **怎么避开**：`db.py` 里已把连接设为 `timeout=30` 并开了 WAL 模式（`PRAGMA journal_mode=WAL`）；**不要在别处再开独立连接同时写**。如果加了看板，看板只读、不要写。

### 10.3 试错过但放弃的方案

- **放弃 1：用 selenium 模拟浏览器跑小红书**。试过，能跑但内存占用高、容易被反爬，放弃了；后来改走"纯接口 + 逆向签名"路线。
- **放弃 2：情感分析直接用 OpenAI API**。成本不可控（每条评论都调用太贵），只列进了备选，未采用。

---

## 11. 风险与求助点

### 11.1 风险与待确认项（标 ❓ 的需人工确认）

- ❓ **抖音 Cookie 的账号归属**：`config\cookies\douyin_cookie.txt` 里是 A 的测试号登录态，8-19 前要换成团队的专用采集号（找雷勤要账号）。**在你换号之前，续期逻辑先别写死用 A 的号。**
- ❓ **小红书签名是否要接第三方打码**：如果逆向卡住，团队是否接受花小钱买打码服务？需要运营/领导拍板（找雷勤）。
- ❓ **评论情绪加成是不是刚需**：如果运营不看评论情绪，接力棒 #4 可以降级甚至砍掉。
- ❓ **服务器具体地址/账号**：第 8 接力棒要用，A 走得太急没留，需要找雷勤要。
- ⚠️ **风险：抖音接口改版**。任何平台接口都可能突然改版导致程序失效，这是爬虫项目的固有风险，遇到就按"抓包→改解析→加签名"的老路修。

### 11.2 遇到问题找谁

| 问题类型 | 找谁 | 怎么联系 |
|---|---|---|
| 抖音 Cookie 账号 / 服务器地址 | 雷勤（领导） | 飞书私聊；账号信息他说了算 |
| 小红书逆向的参考笔记 | 文档自足 | `docs/xhs_signature_notes.md`（A 已写好） |
| 环境安装 / 依赖问题 | 韩玲（mentor） | 飞书私聊；她有 A 留的环境快照 |
| 需求层面的取舍（要不要情绪加成等） | 雷勤 | 飞书私聊 |
| 代码层面的技术卡点 | 先翻本文档 10、11 节 → 仍无解再问雷勤协调资源 | — |

---

## 12. 常用资源清单

| 资源 | 位置 | 用途 |
|---|---|---|
| 项目根目录 | `D:\workspace\hot_video_crawler` | 一切代码都在这里 |
| 全局配置 | `config\config.yaml` | 阈值、cron、重试、数据库连接（改这里生效） |
| 平台参数 | `config\platforms.yaml` | 各平台接口 URL、字段映射 |
| 密钥文件 | `config\.env` | 飞书 webhook、DB 口令等，**已脱敏，勿外传** |
| 抖音 Cookie | `config\cookies\douyin_cookie.txt` | 登录态，接力棒 #1 的主角 |
| 数据库 | `data\videos.db` | SQLite，所有视频/评论数据 |
| 原始数据 | `data\raw\` | 平台原始 JSON 落盘，用于复现/调试 |
| 去重缓存 | `data\dedup_cache\fingerprint.jsonl` | SimHash 指纹缓存 |
| 导出目录 | `data\exports\` | 待实现的 Excel 导出输出地 |
| 日志 | `logs\crawler_*.log` | 排查问题的第一现场 |
| 环境说明 | `docs\README.md` | 环境安装步骤 |
| 小红书逆向笔记 | `docs\xhs_signature_notes.md` | 接力棒 #2 的钥匙 |
| Cookie 处理笔记 | `docs\cookie_notes.md` | 接力棒 #1 参考 |
| 情感分析选型笔记 | `docs\sentiment_choice_notes.md` | 接力棒 #4 参考 |
| 测试 | `tests\` | 单测；`python -m pytest tests -q` 一次跑完 |

> **密钥说明**：所有 token / webhook 已在文档与配置中脱敏为占位符，真实值只在 `config\.env` 和本地，请勿提交到 Git 或发到群里。

---

---

# 附录：给 AI 智能体看的交接文档（Claude Code 版）

> **给 AI 版说明**：下面的文档**可直接复制给 Claude Code** 使用。它按 Claude Code 的习性定制（能读文件、能跑命令、自动读 CLAUDE.md），所以给的是"精确路径 + 可执行命令 + 文件:行号 + 可跑验证"，比人版更紧凑、更命令化。两个版本讲的接力内容**完全一致**（同一份接力棒），只是表达方式不同。

---

# 自动爬取短视频爆款程序 交接文档（给 Claude Code 版）

> 目标智能体：**Claude Code**。交接日期：2026-08-18。项目路径：`D:\workspace\hot_video_crawler`（Windows，shell 为 PowerShell）。

## 0. 交接摘要（启动包）

- **项目**：`hot_video_crawler` —— 每天定时爬抖音/小红书/快手热门视频，打分、去重、入库、飞书推送，并提供一个 FastAPI 看板。
- **当前进度**：约 55%。抖音单平台链路已跑通（采集→解析→打分→去重→入库→通知）；小红书只做了类壳（签名未实现）；快手是空文件；看板是空骨架；调度无人值守联调未验证；未部署。
- **最关键三件事**：
  1. **已完成**：抖音爬虫 + 打分 + 去重 + SQLite 存储 + 飞书通知均有测试通过的实现；
  2. **A 没做完的（接力棒）**：共 9 条，见第 5/6 节，最优先是 #1 抖音 Cookie 续期（08-19 前必须处理）和 #6 无人值守联调；
  3. **B 第一步**：跑 `python src/main.py --check-config` 验证环境 → 处理 #1。
- **从哪继续最省力**：直接照第 6 节接力总览 #1 的"从哪开始"开工，无需读别的。

## 1. 项目总览与验收标准

- **一句话定位**：多平台短视频爆款采集/评分/推送系统。
- **最终目标**（可检验）：
  - 三平台（抖音/小红书/快手）每天 09:00 自动采集 ≥20 条/平台并入库；
  - 爆款指数 ≥70 的视频自动推送飞书；
  - 网页看板可查 Top50、可按平台筛选；
  - 无人值守连续运行 7 天无人工干预。
- **验收标准**：第 6 节接力总览每条"做到什么算完成"列全部满足。

## 2. 文件地图（精确路径）

| 路径 | 作用 | 当前状态 |
|---|---|---|
| `D:\workspace\hot_video_crawler\config\config.yaml` | 全局配置（阈值/cron/重试/DB） | 已配置，`scheduler.cron` 当前 `0 9 * * *` |
| `D:\workspace\hot_video_crawler\config\platforms.yaml` | 平台接口参数 | 已配置抖音/小红书/快手（快手 URL 是占位） |
| `D:\workspace\hot_video_crawler\config\.env` | 密钥（webhook/口令，脱敏） | 只本地，勿提交 |
| `D:\workspace\hot_video_crawler\config\cookies\douyin_cookie.txt` | 抖音登录 Cookie | **临期**，接力棒 #1 主角 |
| `D:\workspace\hot_video_crawler\src\main.py` | 入口：`--check-config/--crawl/--scheduler/--dashboard` | 已可用 |
| `D:\workspace\hot_video_crawler\src\scheduler.py` | APScheduler 调度 | 80%，未无人值守验证 |
| `D:\workspace\hot_video_crawler\src\crawler\base.py` | `BaseCrawler` 抽象基类 + 重试 | 已完成，`_fetch_with_retry()` 在 :66 |
| `D:\workspace\hot_video_crawler\src\crawler\douyin.py` | 抖音爬虫 | 90%，`_refresh_cookie()` :188、Cookie 检查 :210 |
| `D:\workspace\hot_video_crawler\src\crawler\xiaohongshu.py` | 小红书爬虫 | 只有壳，`fetch_hot_list()` 抛 NotImplementedError |
| `D:\workspace\hot_video_crawler\src\crawler\kuaishou.py` | 快手爬虫 | 空占位 |
| `D:\workspace\hot_video_crawler\src\parser\content_parser.py` | 统一解析 | 完成，`parse_video()`/`clean_title()` |
| `D:\workspace\hot_video_crawler\src\parser\comment_parser.py` | 评论解析 + 情感 | 评论基础抓取完成，`analyze_sentiment()` :40 是空函数 |
| `D:\workspace\hot_video_crawler\src\scoring\hot_score.py` | 爆款指数 | 完成，`compute_hot_score()` |
| `D:\workspace\hot_video_crawler\src\scoring\dedup.py` | SimHash 去重 | 完成，`simhash()`/`is_duplicate()` |
| `D:\workspace\hot_video_crawler\src\storage\models.py` | ORM 模型 | 完成 |
| `D:\workspace\hot_video_crawler\src\storage\db.py` | 连接 + `save_videos()` + `query_top_videos()` | 完成 |
| `D:\workspace\hot_video_crawler\src\storage\export.py` | Excel 导出 | **不存在，需新建** |
| `D:\workspace\hot_video_crawler\src\notify\notifier.py` | 飞书推送 | 完成，`send_douyin_digest()` |
| `D:\workspace\hot_video_crawler\src\dashboard\app.py` | FastAPI 看板 | 只有 `/` 健康检查，约 25 行 |
| `D:\workspace\hot_video_crawler\src\dashboard\templates\` | 看板模板 | 空，需新建 `index.html` |
| `D:\workspace\hot_video_crawler\tests\` | 单测 | test_parser/test_scoring/test_dedup 通过 |
| `D:\workspace\hot_video_crawler\docs\` | 笔记（README/xhs_signature_notes/cookie_notes/sentiment_choice_notes） | 有 4 份，缺 DEPLOY_WINDOWS.md |
| `D:\workspace\hot_video_crawler\data\videos.db` | SQLite 数据库 | 有 40 条抖音数据 |
| `D:\workspace\hot_video_crawler\data\raw\` | 原始 JSON | 含 xhs_capture_sample.json 抓包样本 |
| `D:\workspace\hot_video_crawler\data\exports\` | 导出输出 | 空 |
| `D:\workspace\hot_video_crawler\logs\` | 日志 | `crawler_*.log` |

## 3. 已完成工作（全量逐条）

见人版第 6 节同一清单（内容一致）。要点速记：
- 抖音爬虫 `DouyinCrawler`（`fetch_hot_list()`/`fetch_video_detail()`）可用；
- `hot_score.py::compute_hot_score` 公式 `赞*0.4+评论*0.25+转发*0.2+完播*0.15`，归一化 0~100；
- `dedup.py::simhash/is_duplicate`，缓存到 `data\dedup_cache\fingerprint.jsonl`；
- `db.py::save_videos` 对重复 `video_id` upsert 不产生第二行；
- `notifier.py::send_douyin_digest` 飞书卡片实测可送达；
- 测试：`python -m pytest tests -q` 当前应全绿（parser 15 + scoring 12 + dedup 9 = 36 条）。

## 4. 当前精确进度

- **最后一步有效操作**：2026-08-17 手动 `python src/main.py --crawl douyin --limit 50`，抓回 42 条、入库 40 条、飞书推送 5 条 Top。日志尾行在 `logs\crawler_20260817.log`。
- **当前代码状态**：抖音链路代码可用但 Cookie 临期；小红书/快手/看板未实现；调度未无人值守验证。
- **数据状态**：`data\videos.db` 的 `videos` 表现有 40 行（均为抖音，platform='douyin'）。

## 5. A 没做完的事（接力棒，全量逐条）

> 每个未完成项就是 B 要接的活。七要素 = 还差什么 / 阻塞原因 / 前置条件 / 优先级 / 完成标准 / 开工入口 / 验证信号。

1. **Cookie 续期闭环**：`_refresh_cookie()` 未实现自动续期；过期即静默中止。阻塞：需过滑块。前置：团队采集号。优先级 P0。完成标准：乱码 Cookie 后仍能续期或发告警。入口：`src/crawler/douyin.py:188/:210`。验证：`python src/main.py --crawl douyin --limit 5` 见 `[INFO] cookie invalid, trying refresh`。
2. **小红书签名**：`fetch_hot_list()` 未实现，接口需 `x-s`/`x-t`。阻塞：前端 JS 混淆逆向未完成。前置：见 `docs/xhs_signature_notes.md`。优先级 P1。完成标准：`--crawl xiaohongshu --limit 20` 返回 20 条、无 `-100`。入口：`src/crawler/xiaohongshu.py`。验证：命令输出 + 新增单测。
3. **快手爬虫**：空文件。阻塞：排期靠后。前置：参考 `douyin.py`/`base.py`。优先级 P2。完成标准：`--crawl kuaishou --limit 20` 返回并入库。入口：`src/crawler/kuaishou.py`。验证：命令输出。
4. **情感分析**：`analyze_sentiment()` 空实现。阻塞：未选型。前置：确认是否刚需（❓问雷勤）。优先级 P2。完成标准：三态返回 + 100 条标注样本准确率 ≥0.75。入口：`src/parser/comment_parser.py:40`。验证：`pytest tests/test_comment_parser.py`。
5. **看板**：`app.py` 只有 `/`。阻塞：排期靠后。前置：`db.py::query_top_videos()` 已可用。优先级 P1。完成标准：`/api/top?limit=50` 返回含 `hot_score` 的 JSON + 页面可筛选。入口：`src/dashboard/app.py` + 新建 `templates/index.html`。验证：`curl http://127.0.0.1:8000/api/top?limit=50`。
6. **无人值守联调**：未完整跑过定时周期。阻塞：依赖 #1。前置：#1 完成。优先级 P0。完成标准：`*/5 * * * *` 连跑 1 小时 12 周期无异常 + 断网重试告警。入口：`src/scheduler.py:95` + `config.yaml scheduler.cron`。验证：日志 5 阶段标记连续出现。
7. **导出 Excel**：`export.py` 不存在。阻塞：排期靠后。前置：数据已入库。优先级 P2。完成标准：`--export --week 2026-08-10` 生成 xlsx。入口：新建 `src/storage/export.py`（`openpyxl` 已列依赖）。验证：生成文件可打开、行数与库一致。
8. **部署**：无部署文档、无计划任务。阻塞：依赖 #1/#6。前置：Windows 服务器账号（❓找雷勤）。优先级 P1。完成标准：Task Scheduler 每天 09:00 触发、重启后仍在。入口：新建 `docs/DEPLOY_WINDOWS.md`。验证：服务器日志出现任务启动 + 飞书收到推送。
9. **重试/熔断**：`base.py:66` 写死 `retry_count=3`，无退避/熔断/告警。阻塞：A 计划后做。前置：无。优先级 P2。完成标准：`config.yaml` 有 `retry.max_attempts/backoff_seconds/circuit_break_count`；连续失败 5 次熔断 + 告警。入口：`src/crawler/base.py:66`。验证：错地址连续触发观察熔断日志与告警。

## 6. A→B 接力总览（读到就能开工，核心）

| # | A 没做完的（接力棒） | B 要做什么 | 从哪开始（文件:行号 / 函数 / 命令） | 做到什么算完成（验证信号） |
|---|--------------------|-----------|--------------------------------|---------------------------|
| 1 | 抖音 Cookie 过期静默中断 | 加自动续期 + 失败告警 | `src/crawler/douyin.py:188` `_refresh_cookie()`；`:210` 检查分支 | `python src/main.py --crawl douyin --limit 5` 日志出现 `cookie invalid, trying refresh`，随后成功或收到告警 |
| 2 | 小红书签名未实现 | 逆向 `x-s/x-t` 并实现 `fetch_hot_list()` | `src/crawler/xiaohongshu.py`；读 `docs/xhs_signature_notes.md` | `python src/main.py --crawl xiaohongshu --limit 20` 返回 20 条 JSON，无 `-100` |
| 3 | 快手空文件 | 照 `douyin.py` 实现 `KuaishouCrawler` | `src/crawler/kuaishou.py`；接口约定见 `base.py` | `--crawl kuaishou --limit 20` 返回 20 条并入库 |
| 4 | 情感分析空函数 | 选型并实现 `analyze_sentiment()` | `src/parser/comment_parser.py:40`；选型见 `docs/sentiment_choice_notes.md` | `pytest tests/test_comment_parser.py` 通过；"绝了"→positive |
| 5 | 看板空壳 | 实现 `/api/top` + 页面 | `src/dashboard/app.py`；模板新建 `src/dashboard/templates/index.html` | `curl http://127.0.0.1:8000/api/top?limit=50` 返回含 `hot_score` 的 JSON |
| 6 | 无人值守未联调 | 验证定时全流程 + 补重试告警 | `src/scheduler.py:95` `run_once()`；`config.yaml scheduler.cron` 改 `*/5 * * * *` | 连跑 1 小时 12 周期无异常；断网一次见重试+告警日志 |
| 7 | 导出未实现 | 新建 `export.py` 导出周汇总 xlsx | 新建 `src/storage/export.py`；依赖 `openpyxl` | `python src/main.py --export --week 2026-08-10` 生成可打开 xlsx |
| 8 | 未部署 | 写部署文档 + 配计划任务 | 新建 `docs/DEPLOY_WINDOWS.md`；服务器信息见第 11 节 ❓ | 服务器 09:00 触发、重启后任务仍在、飞书收到推送 |
| 9 | 重试/熔断不完善 | 参数化 + 熔断 + 告警 | `src/crawler/base.py:66` `_fetch_with_retry()` | 错地址连续 5 次触发熔断，飞书收"今日已熔断"告警 |

> **🚀 接力开工第一步（Claude Code 可直接执行）**：
> ```powershell
> cd D:\workspace\hot_video_crawler
> python src/main.py --check-config
> ```
> **出现配置摘要且无报错 = 正式接上**，然后按 #1 改 `douyin.py`。若此步报缺依赖，先 `pip install -r requirements.txt`。

## 7. 下一步行动计划（命令级）

> 按第 6 节接力总览顺序，展开成可直接执行的步骤。Windows shell 用 PowerShell。

**第 1 步（验证接入）**
```powershell
cd D:\workspace\hot_video_crawler
pip install -r requirements.txt
python src/main.py --check-config   # 期望：打印抖音/小红书/快手+DB+飞书摘要
python -m pytest tests -q            # 期望：36 passed
```

**第 2 步（接力棒 #1：Cookie 续期）**
1. 打开 `src/crawler/douyin.py`，读 `_load_cookie()`（注意 `utf-8-sig`，别改成 `utf-8`）与 `_refresh_cookie()`（:188）。
2. 在 `_refresh_cookie()` 实现：请求刷新接口 → 写入 `config\cookies\douyin_cookie.txt` → 返回 bool；刷新失败时调 `notifier.py` 的告警函数。
3. 改 `fetch_hot_list()`（:210 附近）：Cookie 无效时先 `_refresh_cookie()`，False 才告警并中止。
4. 验证：
```powershell
# 先把 Cookie 改成乱码
Set-Content config\cookies\douyin_cookie.txt -Value "garbage"
python src/main.py --crawl douyin --limit 5
# 期望日志：cookie invalid, trying refresh → 成功抓取 或 飞书告警
```

**第 3 步（接力棒 #6：无人值守联调）**
1. 临时改 `config.yaml`：`scheduler.cron: "*/5 * * * *"`。
2. ```powershell
   python src/main.py --scheduler   # 挂机 1 小时
   ```
3. 期望：每 5 分钟一条完整 5 阶段日志；中途断网一次应见重试（3 次）与最终告警。
4. 完成后把 cron 改回 `0 9 * * *`。

**第 4 步（接力棒 #2：小红书签名）**
1. 读 `docs/xhs_signature_notes.md` 与 `data/raw/xhs_capture_sample.json`。
2. 实现 `_gen_sign(params, ts)` 与 `fetch_hot_list()`（签名进请求头 `x-s`/`x-t`）。
3. 验证：
```powershell
python src/main.py --crawl xiaohongshu --limit 20   # 期望：20 条 JSON，无 -100
```

**第 5 步（接力棒 #5：看板）**
1. 确认 `db.py::query_top_videos()` 返回 `(video_id,title,platform,hot_score,url)`。
2. `app.py` 加 `GET /api/top`；新建 `templates/index.html` 渲染表格 + 平台下拉。
3. ```powershell
   python src/main.py --dashboard
   # 另开终端：
   curl http://127.0.0.1:8000/api/top?limit=50
   ```

**后续**：快手（#3）→ 情感分析（#4）→ 导出（#7）→ 熔断（#9）→ 部署（#8），均按第 6 节入口与验证执行。

## 8. 环境与配置依赖（完整清单）

- **Python**：3.10+（开发机已装 3.11）。
- **依赖库**：`requirements.txt`（requests、APScheduler、fastapi、uvicorn、sqlalchemy、openpyxl、pytest 等）。
- **数据库**：SQLite（`data\videos.db`），WAL 模式已开；连接 `timeout=30`。
- **密钥/配置**：`config\.env` 含飞书 webhook 等，**值已脱敏**；不要提交 Git。
- **网络**：抖音/小红书/快手均需国内可直连网络；无需代理。
- **端口**：看板占用 `8000`；勿与其他服务冲突。
- **无 Docker**：部署走 Windows 计划任务，不是容器。

## 9. 数据与状态快照

- `data\videos.db`：`videos` 表 40 行（均 platform='douyin'）；`comments` 表少量测试数据。
- `data\raw\`：抖音原始 JSON 若干 + `xhs_capture_sample.json`（小红书抓包样本，逆向用）。
- `data\dedup_cache\fingerprint.jsonl`：去重指纹缓存，可安全清理（会重算）。
- **临时数据**：`config\cookies\douyin_cookie.txt` 是临期测试号，**需替换**为团队采集号（❓找雷勤）。
- **需保留**：`data\raw\` 与 `docs\` 是调试与逆向的关键依据，勿删。

## 10. 关键决策与踩坑记录

- **决策**：先抖音→后小红书→再快手；SQLite 非 MySQL；飞书 webhook；加权公式 `0.4/0.25/0.2/0.15`；随机延迟 3~8s；APScheduler + FastAPI。
- **坑**：① 抖音 `-8888` 风控 → 别去掉延迟 + `_fake_headers()` 必须带 Referer，遇到立即停 10 分钟；② Cookie 文件 BOM → 读用 `utf-8-sig`，**勿改回 `utf-8`**；③ 飞书卡片字段不全导致延迟 → 别加重试发送循环；④ SQLite locked → 已 WAL + timeout=30，**不要另开写连接**。
- **放弃**：selenium 跑小红书（内存/反爬）；OpenAI 做情感分析（成本）。

## 11. 风险与待确认项

- ❓ 抖音采集号：`douyin_cookie.txt` 目前是 A 的测试号，需雷勤提供团队号（P0 前置）。
- ❓ 服务器地址/账号：接力棒 #8 需要，A 未留。
- ❓ 情感分析是否刚需：决定 #4 是否降级。
- ❓ 小红书打码服务是否可采购：逆向卡住时的备选方案。
- ⚠️ 平台接口随时可能改版；遇到 `-8888`/`-100` 类风控码按"抓包→改解析→加签名"处理。

## 12. 续作启动手册

> 第 6 节是"开工清单"（接 A 的活）；本节是"环境还原"（把 A 的环境跑起来）。

**从零恢复完整步骤：**
1. 确认 Python 3.10+：`python --version`。
2. 装依赖：`pip install -r requirements.txt`。
3. 核对配置：`python src/main.py --check-config`。
4. 跑测试确认基线：`python -m pytest tests -q`（期望 36 passed）。
5. 手动采一次抖音：`python src/main.py --crawl douyin --limit 20`。
6. 启动调度：`python src/main.py --scheduler`。
7. 启动看板：`python src/main.py --dashboard`。

**如何验证"续上了"（关键）**：跑完第 3 步 `--check-config` **无报错并打印配置摘要**、第 4 步 **36 passed**、第 5 步 **终端出现视频 JSON 且 `videos` 表行数增加** —— 三条信号齐了即确认环境与 A 完全一致、可正式开始第 6 节 #1。

## 13. 按 Claude Code 定制的附加内容

- **建议写 CLAUDE.md**：接手后请在 `D:\workspace\hot_video_crawler\CLAUDE.md` 写入三条铁律：①Cookie 文件读取必须用 `utf-8-sig`；②不得给飞书 webhook 加重试循环；③看板只读 SQLite、不写库。Claude Code 会自动加载遵守。
- **可并行派生子代理**：#2 小红书签名逆向、#5 看板、#7 导出三者互不依赖，可各派一个子代理并行推进；#1/#6 串行依赖，别并行。
- **❓ 提问入口**：遇到不确定（如账号/服务器信息、需求取舍），先查第 11 节，再决定是否问雷勤；不要凭空假设接口参数。
- **验证可跑**：所有"做到什么算完成"列的验证信号都是可直接执行的命令/日志/curl 输出，请跑真实验证后再标记完成。
