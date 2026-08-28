# 积昌的知识库 · 交接文档（人 + AI 双版本）

> **项目名**：积昌的知识库（简称"知识库"）
> **交接对象**：① 接手维护的同事/朋友（人版）；② 下一个 AI 智能体 **Claude Code**（AI 版）
> **交接日期**：2026-08-17
> **交接方式**：同一文件内先给人版、后给 AI 版，两版之间用分隔线明确隔开

> [!info] 阅读指引
> - **你是人** → 读「第一部分：给人版」即可，从第 1 节背景读到第 8 节求助点，循序渐进。
> - **你是 Claude Code** → 直接跳转「第二部分：给 Claude Code 版」，那里的内容全部按"你拿到就能干活"的方式写成。
> - 两部分信息有重叠，但**详略和写法完全不同**：人版讲道理、讲来龙去脉；AI 版给精确路径、命令和验证信号。

---

# 第一部分：给人版（详细说明文档）

> 目标读者：**一位没有参与过本项目的同事/朋友**。读完本文，你应该能独立回答三个问题：① 这个知识库是干什么的？② 它现在做到哪一步了？③ 我接下来该做什么、怎么做？

## 1. 这份文档是给谁看的

### 1.1 背景：为什么会有这份交接

"积昌的知识库"是 **谢积昌** 的个人知识库，运行在他自己的 Windows 电脑上（当前路径 `F:\积昌的知识库 - 副本`）。它不只是一堆笔记，而是一套**由 AI 智能体（Claude Code）半自动维护的个人知识管理系统**——平时 Claude 会把散落在各处的资料（飞书消息、企业微信文件、网页、PDF、课程笔记、实习资料）整理成结构化笔记，并持续维护一套"知识地图"。

现在由于换人/换设备/让下一个 AI 无缝接手，需要把"这个系统是怎么搭的、现在是什么状态、接下来怎么维护"一次交代清楚。

### 1.2 读完你应该能达到的效果

- 看得懂整个知识库的目录结构、三层架构和"谁负责维护哪一层"；
- 知道每天/每周 Claude 在后台自动做什么（两个自动化任务）；
- 遇到"知识库报错""想整理新资料""想查某主题笔记"时，知道该走哪条流程、找哪个文件；
- 有需要时能自己启动/停止两个 IM 消息助手服务（飞书、企业微信）。

## 2. 项目总览（大白话）

| 问题 | 大白话回答 |
|---|---|
| 这是做什么的？ | 一个 **Obsidian 笔记库**，用一套叫 **LLM Wiki** 的方法论，让 AI 帮主人把杂乱资料整理成"有索引、可交叉引用、持续更新"的知识库 |
| 为谁做？ | 谢积昌自己（个人知识管理 + 实习求职 + 科研项目 + 自媒体副业都往这里沉淀） |
| 解决什么问题？ | 资料散落在飞书、微信、网页、课程里，想用的时候找不到；让 AI 负责整理和检索，主人负责提供来源和提问 |
| 整体完成度 | 约 **85%**。主体结构、规则、自动化、61 个知识页面都已就绪并稳定运行；剩余工作主要是"持续摄入新资料"和"每 3 天/每周的例行维护"，属于运行期维护而非搭建期 |
| 一句话价值 | **主人的"外置大脑"**——所有重要信息进得来、找得到、用得着 |

## 3. 背景与来龙去脉

### 3.1 项目怎么来的

这个知识库经历了几个阶段的演进：

1. **最早**：只是一个普通 Obsidian 笔记库（Obsidian 是一款本地 Markdown 笔记软件，用双向链接 `[[ ]]` 连接笔记）。
2. **引入 LLM Wiki 方法论**：主人读了 AI 专家 Andrej Karpathy 的《LLM Wiki》文章，决定不再让 AI 当"什么都往里塞的聊天机器人"，而是让 AI 当"**有纪律的 wiki 维护者**"——只维护特定文件夹、按固定工作流干活、每次都更新索引和日志。
3. **接入 IM 助手**：为了让主人"人在飞书/微信里发条消息就能把文件扔进知识库"，先后搭建了两个常驻服务：**飞书智能助手** 和 **企业微信智能助手**，它们监听消息、调用 Claude CLI 处理文件、把结果写回知识库。
4. **持续迭代**：每 3 天 Claude 会自动做一轮全库整理（LLM Wiki 迭代）；每周一自动把整个知识库备份到 GitHub。

### 3.2 关键约束与偏好

- **主人已经给 AI 开了全部权限**：Claude 操作文件/跑命令不需要再问"能不能做"。规则里明确"提问只允许问做什么/怎么做，禁止问能不能给权限"。
- **语言习惯**：所有输出、文档、回复一律用**简体中文**（代码、命令、专有名词、文件路径除外）。
- **能用中文路径就用中文路径**：知识库内几乎所有文件夹都是中文名。
- **"知识库"这个词**：在本项目语境里特指 `F:\积昌的知识库 - 副本` 这个根目录（严格说 CLAUDE.md 里写的是 `E:\...`，但当前实际运行的盘符是 **F:**，见第 9 节风险 2）。

### 3.3 与公司/团队的关系

- 飞书智能助手部署标记为"**公司用**"（`飞书智能助手/部署标记.txt`），即这台电脑上的飞书机器人供公司内部使用，接收上司/mentor 发来的文件。
- 企业微信助手用于接收企业微信消息。
- 两者都不对外部公开，仅本机 + 对应 IM 使用。

## 4. 术语表

> 按"术语（英文/缩写）＝ 大白话解释"格式列出。都是这套系统里高频出现的词，值得花 2 分钟扫一遍。

| 术语 | 解释 |
|---|---|
| **知识库 / Vault** | 主人对"这个 Obsidian 笔记库根目录"的称呼。Vault 是 Obsidian 的官方叫法 |
| **Obsidian** | 一款本地 Markdown 笔记软件；支持 `[[双向链接]]` 把笔记连成网 |
| **Markdown** | 一种用简单符号（`#`、`-`、`**` 等）标记格式的纯文本格式，Obsidian 笔记就是这个格式 |
| **LLM Wiki** | Karpathy 提出的方法论：让 AI 像维护一个维基百科一样维护知识库——有索引、有日志、只维护固定区域、可自由修改 |
| **三层架构** | 本知识库把内容分为三层：契约层（规则）、wiki 层（AI 维护的页面）、原始层（待整理材料）。见第 5 节 |
| **Ingest（摄入）** | 新资料进来后，AI 读它、提炼、写成 wiki 页面的过程 |
| **Query（查询）** | 主人提问时，AI 按"先查索引→再读页面"的方式检索回答的过程 |
| **Lint（体检）** | AI 周期性检查知识库健康度（有无矛盾、过期说法、孤儿页、缺页），并修复 |
| **index.md** | wiki 的"总目录"，列出所有 61 个页面的链接和一句话摘要。查东西先看它 |
| **log.md** | wiki 的"操作日志"，按时间顺序追加记录 AI 每次做了什么 |
| **wiki 页面** | `自动维护知识库/wiki/` 下的结构化 Markdown 文件，每个约等于一个主题 |
| **Hook** | Claude Code 的"钩子"，在特定时机自动触发一段脚本。本项目用它实现"到期自动提醒维护" |
| **标记文件** | 根目录下以 `.` 开头的几个小文件（`.last-wiki-maintain` 等），记录上次维护日期，Hook 靠它判断是否到期 |
| **Skill（技能）** | 一种给 AI 预装的能力包（SKILL.md 描述触发条件，内含操作流程）。知识库已装约 27 个 |
| **Claude CLI / claude.exe** | Anthropic 的命令行 AI 工具，本机通过 `claude` 命令调用，两个 IM 助手都靠它干活 |
| **Claude Code** | 即 Claude CLI 的完整名称，能读文件、跑命令、改代码的编码型智能体 |
| **Codex** | OpenAI 的另一款命令行智能体（本机也装了）。规则文件叫 `AGENTS.md` |
| **lark-cli** | 飞书官方命令行工具，IM 助手通过它收发飞书消息 |
| **LocalTunnel** | 一种内网穿透工具，让外部的企业微信回调能访问本机服务 |
| **NSSM** | 把 Python 程序注册成 Windows 服务的工具（企业微信助手用它开机自启） |
| **双向链接 `[[ ]]`** | Obsidian 语法，`[[页面名]]` 表示跳转到另一个笔记，形成知识网络 |
| **Frontmatter** | 每个 wiki 页面最开头的 `---` 包裹的元信息块（标题、标签、来源、日期等） |
| **收件箱** | 规则中定义的"待整理材料存放处"，目前空/未创建（见第 9 节风险 3） |
| **已整理好的文件** | 规则中定义的"用户归档区"，**只读**，只有主人明确指令才能改 |

## 5. 当前进度（用"人话"讲）

- **整体架构**：已经搭完并稳定运行。三层架构、规则文件、自动化 Hook、两个 IM 助手、GitHub 备份流程全部就位。
- **知识内容**：wiki 已有 **61 个知识页面**，分 10 大类（AI 与技术工具、实习求职、行业知识、智灌云联项目、编程、对比分析、自媒体运营、实习训练营、销售技能、学术裁缝）。最后一次全库迭代在 **2026-08-17**。
- **收件箱**：当前为空（没有待整理的新材料），说明近期摄入已消化完。
- **自动化**：最近一次 GitHub 备份和 wiki 维护都发生在 2026-08-17，均是最新状态。
- **剩余工作**：不再是"搭建"，而是**日常运行**——持续接收新资料 → ingest 摄入 → 每 3 天迭代维护 → 每周一 GitHub 备份。

## 6. 已完成工作（全量逐条）

### 6.1 规则与架构
1. **根 `CLAUDE.md`**（约 11 KB）：知识库定义、任务执行准则、临时文件清理规则、飞书/企业微信任务规则、GitHub 备份规则、多 Agent 协作规则。位置：`F:\积昌的知识库 - 副本\CLAUDE.md`。
2. **`.claude/CLAUDE.md`**（约 26 KB）：知识库硬性规则——命名规则、文件夹权限、Skill 安装位置、权限模式、文档查询顺序、飞书科研脚本文档置顶规则等。
3. **`.claude/LLM-WIKI-SCHEMA.md`**：LLM Wiki 维护契约，定义三层架构、ingest/query/lint 三个工作流、页面规范。
4. **`.claude/agents/代码总监.md`**：一个特殊的子代理定义（多 Agent 开发时当"独立裁判/监工"用）。
5. **`自动维护知识库/CLAUDE.md`**：wiki 层的维护规范（页面约定、来源引用格式、关键原则）。

### 6.2 知识库内容（wiki 层）
6. **`自动维护知识库/index.md`**：总目录，61 个页面 + 一句话摘要 + 来源数 + 最后更新日期。
7. **`自动维护知识库/log.md`**：时间线日志，记录从 2026-07-14 至今的每次 ingest/query/lint/update。
8. **`自动维护知识库/LLM Wiki.md`**：Karpathy《LLM Wiki》方法论文档。
9. **`自动维护知识库/wiki/` 下的 61 个页面**，按 10 大分类组织，例如：
   - **AI 与技术工具**：Claude Code、GitHub协作开发、SKILL技能包、子Agent与MCP配置、Codex模型配置（含 10 份网络故障档案）、AI概念速查、飞书智能助手、企业微信智能助手。
   - **智灌云联项目**：项目总览、LSTM预测模型、智能Agent决策、硬件架构、数据与算法 + 10 个概念解析页 + 3 个技术问答页 + 文献综述。
   - **实习求职 / 实习训练营 / 自媒体运营 / 学术裁缝 / 行业知识 / 对比分析 / 编程 / 销售技能** 等主题均有对应页面。

### 6.3 自动化（Hook 驱动）
10. **`.claude/hooks/kb-maintenance-check.sh`**：`UserPromptSubmit` Hook——每天最新一条消息到达时自动检查两个标记文件，到期就提示执行（见第 7.1 节"两个例行任务"）。
11. **`.claude/settings.json`**：注册了该 Hook，以及两个 UI 相关 Hook（impeccable 设计检查，依赖 Node 22）。
12. 三个标记文件：`.last-wiki-maintain`、`.last-github-backup`、`.last-maintenance-prompt`（当前均记录为 2026-08-17）。

### 6.4 IM 消息助手（两个常驻服务）
13. **飞书智能助手**：`飞书智能助手/server.py`（v2.0.0），架构为 `飞书 → lark-cli event consume → server.py → Claude CLI → 知识库`。含多轮对话、会话状态机、意图理解。部署标记"公司用"。资源目录 `lark-resources/`。
14. **企业微信智能助手**：`微信智能助手/server.py`（FastAPI），架构为 `微信 → 企业微信 → LocalTunnel → server.py → Claude CLI → 知识库`，监听 `127.0.0.1:8800`，用 NSSM 注册为 Windows 服务。资源目录 `wecom-resources/`。

### 6.5 Skills（技能包）
15. `.claude/skills/` 下约 **27 个技能**（中文名）：交接助手、文档转换+排版、知识库报错修复、华哥脚本撰写、JD深度剖析、AI咨询师、模拟面试、简历素材记录、国创赛导师、周日报助手、飞书智能助手等。
16. `.agents/skills/` 下是 **Codex 专用副本**（英文名），与 `.claude/skills/` 一一对应（对照表在 `AGENTS.md` 第 3 节）。
17. **`交接助手` skill**：就是生成这份文档所用的方法论（区分人/AI 交接对象、按智能体习性定制、强制"如何验证续上了"闭环）。
18. **知识库报错修复相关**：`总结好的大纲以及笔记/知识库FAQ/` 下有 00-报错统计台账.md 和 10+ 份故障档案（Obsidian 报错、Codex 网络故障、mihomo/代理问题等），配套 `知识库报错修复` skill 使用。

### 6.6 原始资料（只读层）
19. `总结好的大纲以及笔记/` 下 5 个主题文件夹：**学校**（作业/大创与国创/科研）、**实习就业**、**技能**（AI/剪辑/电脑）、**浪尖训练营**、**知识库FAQ**。这些是 wiki 页面的原始来源，**只读**。

## 7. 未完成事项（全量逐条）

> 本项目没有"做一半的搭建任务"。剩余的都是**周期性例行任务**，按时间触发，规则已写好、Hook 会自动提醒。

| # | 未完成事项 | 为什么还没做/何时做 | 前置条件 | 优先级 | 做到什么程度算完成 |
|---|---|---|---|---|---|
| 1 | **LLM Wiki 例行迭代** | 每 3 天一轮，到 2026-08-20 又到期 | 有 3 天以上新资料积累或主人要求 | 高（自动） | 走完一轮 ingest/query/lint，同步更新 `index.md` 与 `log.md`，并把 `.last-wiki-maintain` 更新为当天日期 |
| 2 | **GitHub 定期备份** | 每周一 / 距上次 ≥7 天 | 无 | 高（自动） | 整库 `git add -A + commit + push` 到 `xieji-star/jichang-zhishiku`，新建日期文件夹 `积昌的知识库<MMDD>`，只保留最近 10 版，更新 `.last-github-backup` |
| 3 | **新资料摄入（ingest）** | 主人随时丢新文件到飞书/企业微信/收件箱 | 有新资料 | 中（按需） | 资料被整理成 wiki 页面、索引与日志已更新 |
| 4 | **知识库报错处理** | 出现报错时 | 出现文件读取/网络类报错 | 中（按需） | 按 `知识库报错修复` skill 流程：记录时间→查 FAQ→复现→三层诊断→备份→修复→验证→写进报错台账 |

## 8. 下一步怎么做（手把手）

### 8.1 如果你是"人"接手维护，按这个顺序走

1. **先读规则文件（约 10 分钟）**：用 Obsidian 打开 `F:\积昌的知识库 - 副本`，依次打开 `CLAUDE.md` → `.claude/CLAUDE.md` → `.claude/LLM-WIKI-SCHEMA.md`。不需要背下来，知道"规则都在 .claude/ 里"即可。
2. **看看"知识地图"长什么样**：打开 `自动维护知识库/index.md`，滚动看一遍 61 个页面；想深入哪个主题就点 `[[双向链接]]`。
3. **掌握"查资料"的正确姿势**：查任何主题，**永远先看 `自动维护知识库/index.md` 定位页面，再点进对应页面**；不要用文件管理器把整个库翻一遍。这是硬性规则。
4. **掌握"存新资料"的正确姿势**：新资料来了 → 丢给飞书/企业微信助手（或放进 `收件箱/`）→ 让 Claude 按 ingest 流程整理 → 它会自动更新 index 和 log。
5. **两个例行任务**（Hook 会自动提醒，你不用记）：
   - **每 3 天**：让 Claude 做一轮 LLM Wiki 迭代。
   - **每周一**：让 Claude 把知识库备份到 GitHub。
6. **遇到报错**：直接跟 Claude 说"知识库报错了"，它会走 `知识库报错修复` skill 的固定流程，并会问你是哪类报错。

### 8.2 如何验证你"接住了"

- 你能在 Obsidian 里打开知识库，index.md 显示 61 个页面；
- 你能说出三层架构各自是哪个文件夹；
- 你能找到飞书/企业微信助手服务怎么启动（见下节）。

### 8.3 两个 IM 助手服务的手动启停（会用到才看）

> [!warning] 重要警告
> 飞书助手目录里的 `restart.bat` 会执行 `taskkill /f /im python.exe` **把机器上所有 Python 进程全部杀掉**（包括正在运行的 Claude 自己）。**不要用它**。手动启动请直接跑 `python server.py`。

- **启动飞书助手**：打开命令提示符，执行：
  ```bat
  cd /d "F:\积昌的知识库 - 副本\飞书智能助手" && python server.py
  ```
  成功标志：日志出现 `开始监听飞书消息` 和 `lark-cli 进程 PID`。
- **启动企业微信助手**：双击 `微信智能助手\start-with-tunnel.bat`（自带 LocalTunnel），或 `restart-service.bat`（以 NSSM 服务方式）。监听 `127.0.0.1:8800`。
- **查看有没有在运行**：`tasklist /fi "imagename eq python.exe"`。

## 9. 关键决策与踩坑记录（给后人最值钱的部分）

| 决策/踩坑 | 详情 |
|---|---|
| **为什么用 LLM Wiki 三层架构** | 因为"让 AI 自由发挥改所有笔记"会乱；限定"AI 只维护 `自动维护知识库/`，其余区域只读/待整理"，AI 才能成为有纪律的维护者 |
| **为什么"给人"和"给 AI"的文档要分开** | 人理解力有限需要手把手+术语解释；AI 能读文件跑命令但每个产品习性不同，给它通用模板接不住。因此本项目专门做了"交接助手"skill 和智能体习性档案（`.claude/skills/交接助手/references/agent-profiles.md`） |
| **Codex 网络故障系列** | 这台电脑有"公寓/青旅/公司"多网络环境，Codex/代理多次出问题，共沉淀 10+ 份 FAQ 档案（在 `知识库FAQ/`）。踩坑要点：`mode:direct ≠ 关代理客户端`、TUN 关不影响走系统代理的 Codex、IPv6 出站可能被 CF 风控。**换网络环境先查 FAQ** |
| **`restart.bat` 杀所有 Python** | 这是飞书助手的坑：重启脚本用 `taskkill /f /im python.exe`，会把 Claude 自己和其他服务一起杀掉。规则文件已明确禁止用它，改用手动 `python server.py` |
| **obsidian 报错 Request too large / pdftoppm 失败** | 读取大 PDF 时可能报错，对应 `知识库FAQ/01-Obsidian反复报错Request too large.md`，一般用拆分/换工具解决 |
| **尝试过但放弃的方案** | 没有记录在案的"放弃方案"；一些备选（如轻抖等采集工具对比）记录在 `wiki/自媒体运营/短视频爆款采集系统` 页面里 |

## 10. 风险与求助点

| # | 风险/待确认点 | 说明 |
|---|---|---|
| 1 | ❓ **盘符 E: vs F:** | 所有 CLAUDE.md 规则文件里写的路径都是 `E:\积昌的知识库 - 副本`，但**当前实际运行在 `F:\积昌的知识库 - 副本`**。这是历史遗留（从 E: 拷贝/迁移到 F:）。规则里的绝对路径如遇报错，请按 F: 修正。**建议找人确认后统一改规则文件** |
| 2 | ❓ **`收件箱/` 和 `已整理好的文件/` 当前不存在** | 规则反复提到这两个文件夹，但当前根目录下并没有创建。`已整理好的文件` 是只读归档区、`收件箱` 是待整理区，缺目录时相关流程可能找不到落盘位置。需主人确认是否需要补建 |
| 3 | ❓ **密钥/token** | 飞书与企业微信的 `config.json` 里含 API Token（`ANTHROPIC_AUTH_TOKEN`）和企业微信 `secret`/`encoding_aes_key`。本交接文档已脱敏；若需迁移/交接这些文件，请走私密渠道，不要明文发到聊天/仓库 |
| 4 | ❓ **Claude CLI 依赖 DeepSeek 中转** | 两个助手的 `config.json` 都配置 `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`（即用 DeepSeek 模型跑 Claude CLI）。若 DeepSeek 账号欠费/失效，两个 IM 助手都会失灵 |
| 5 | ❓ **impeccable 设计 Hook 依赖 Node 22** | `.claude/settings.json` 里注册了 UI 检查 Hook，需要 Node 22+；机器上没有时会提示降级（不影响知识库核心功能） |
| 6 | ❓ **`.yolov8m-seg.pt.*.part` 半成品** | 根目录有个约 39 MB 的 `.part` 未下载完文件，疑似采集系统的模型下载残留，可清理或确认用途 |

**遇到问题找谁/看哪：**
- 知识库结构问题 → 看 `.claude/CLAUDE.md` 与 `自动维护知识库/CLAUDE.md`；
- 报错 → 走 `知识库报错修复` skill，先查 `总结好的大纲以及笔记/知识库FAQ/00-报错统计台账.md` 是否已有同类记录；
- 飞书/企业微信助手问题 → 看各自目录的 `logs/` 与 `config.json`；
- 本项目主人：**谢积昌**（本机用户名 asus）。

## 11. 常用资源清单

| 资源 | 路径 | 用途 |
|---|---|---|
| 规则总入口 | `F:\积昌的知识库 - 副本\CLAUDE.md` | 知识库最上层定义 |
| 硬性规则 | `F:\积昌的知识库 - 副本\.claude\CLAUDE.md` | 权限/命名/查询顺序等 |
| 维护契约 | `F:\积昌的知识库 - 副本\.claude\LLM-WIKI-SCHEMA.md` | ingest/query/lint 规范 |
| 总目录 | `F:\积昌的知识库 - 副本\自动维护知识库\index.md` | 61 页知识地图 |
| 操作日志 | `F:\积昌的知识库 - 副本\自动维护知识库\log.md` | AI 维护时间线 |
| wiki 页面 | `F:\积昌的知识库 - 副本\自动维护知识库\wiki\` | 全部知识页面 |
| 原始资料 | `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\` | 只读来源 |
| 报错台账 | `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\知识库FAQ\00-报错统计台账.md` | 报错档案索引 |
| 飞书助手 | `F:\积昌的知识库 - 副本\飞书智能助手\` | 飞书消息服务 |
| 企业微信助手 | `F:\积昌的知识库 - 副本\微信智能助手\` | 企业微信回调服务 |
| Skills | `F:\积昌的知识库 - 副本\.claude\skills\` | 中文技能包 |
| Codex 副本 | `F:\积昌的知识库 - 副本\.agents\skills\` | 英文技能包（Codex 用） |
| GitHub 仓库 | `https://github.com/xieji-star/jichang-zhishiku`（账号 `xieji-star`） | 每周备份目的地 |
| 交接助手 skill | `F:\积昌的知识库 - 副本\.claude\skills\交接助手\` | 本次交接文档的方法论 |

---

# 第二部分：给 Claude Code 版（AI 启动包）

> **目标智能体：Claude Code**（Anthropic 命令行编码智能体，本机命令为 `claude`）
>
> 本部分按 Claude Code 的习性定制：能读文件、能跑命令、自动加载 `CLAUDE.md`。因此只给**精确路径 + 可执行命令 + 可验证信号**，不做叙事。可直接把本部分复制给下一个 Claude Code 会话作为启动上下文。
>
> 惯例：所有相对路径均相对于 vault 根目录 `F:\积昌的知识库 - 副本`；Windows 环境，命令以 PowerShell 为主。

## 0. 交接摘要（启动包）

- **项目**：积昌的知识库 —— 基于 Karpathy《LLM Wiki》方法论运行的 Obsidian 知识库，Claude Code 是它的维护者。当前实际根目录 `F:\积昌的知识库 - 副本`（注意：规则文件里写的是 E:，见第 10 节风险 1）。
- **当前状态**：wiki 61 页、10 大类，全部已摄入；收件箱为空；最近一次 LLM Wiki 迭代与 GitHub 备份均为 2026-08-17；两个 IM 助手（飞书/企业微信）常驻服务已配置。
- **最关键三件事**：
  1. **已完成**：三层架构 + 规则 + Hook 自动化 + 61 页知识 + 两个 IM 助手服务全部就绪。
  2. **卡在哪**：无阻塞。剩余全是周期性例行任务（每 3 天 wiki 迭代、每周一 GitHub 备份），由 Hook 自动提醒。
  3. **下一步第一件事**：按第 1 节加载规则 → 读 `自动维护知识库/index.md` 与 `log.md` 确认现状 → 若 `.last-wiki-maintain` 距今 ≥3 天则执行一轮 ingest/query/lint 迭代。
- **从哪继续最省力**：先 `Read` 根 `CLAUDE.md` + `.claude/CLAUDE.md` + `.claude/LLM-WIKI-SCHEMA.md`，然后读 `自动维护知识库/index.md`，即可无缝进入维护者角色。

## 1. 启动前必读（第一条，禁止跳过）

Claude Code 会自动加载根 `CLAUDE.md` 和全局 `~/.claude/CLAUDE.md`，但仍请**依次完整读取**以下文件再开工（它们定义本知识库全部硬性规则）：

```powershell
Set-Location "F:\积昌的知识库 - 副本"
# 依次读（Read 工具）：
# 1. CLAUDE.md                          — 知识库定义、任务准则、临时文件清理、IM 任务、GitHub 备份
# 2. .claude\CLAUDE.md                  — 硬性规则：命名、文件夹权限、Skill 安装位置、查询顺序
# 3. .claude\LLM-WIKI-SCHEMA.md         — ingest / query / lint 工作流契约
# 4. 自动维护知识库\index.md            — 61 页知识地图（定位用）
# 5. 自动维护知识库\CLAUDE.md           — wiki 层维护规范
```

## 2. 项目总览与验收标准

- **一句话定位**：让 Claude Code 当一个"有纪律的 wiki 维护者"，持续把主人的资料整理成可检索、可交叉引用的结构化知识库。
- **最终目标**：三件事稳定运转——① 持续 ingest 新资料；② 每 3 天一轮全库迭代（ingest/query/lint）；③ 每周一备份到 GitHub。
- **验收标准（可检验）**：
  - `自动维护知识库/index.md` 页面数与 `自动维护知识库/wiki/` 实际页面数一致（当前 61）；
  - `log.md` 持续追加，格式 `## [YYYY-MM-DD] <动作> | <标题>`；
  - 根目录标记文件日期被正确更新（见第 11 节验证）。

## 3. 文件地图（精确路径）

> 按"入口 → 规则 → 内容 → 自动化 → 服务"排列。✅=已就绪，⚠️=需注意。

| 路径（相对 vault 根 `F:\积昌的知识库 - 副本`） | 作用 | 状态 |
|---|---|---|
| `CLAUDE.md` | 知识库总规则（根） | ✅ |
| `.claude\CLAUDE.md` | 硬性规则 | ✅ |
| `.claude\LLM-WIKI-SCHEMA.md` | LLM Wiki 维护契约 | ✅ |
| `.claude\settings.json` | Hook 注册（UserPromptSubmit 维护检查 + impeccable UI Hook） | ✅ |
| `.claude\hooks\kb-maintenance-check.sh` | 到期自动提醒脚本（读 3 个标记文件） | ✅ |
| `.last-wiki-maintain` / `.last-github-backup` / `.last-maintenance-prompt` | 维护日期标记（当前均 2026-08-17） | ✅ |
| `.claude\agents\代码总监.md` | 多 Agent 开发时的独立裁判子代理 | ✅ |
| `.claude\skills\` | 约 27 个中文技能包（含交接助手、文档转换+排版、知识库报错修复等） | ✅ |
| `.agents\skills\` | Codex 专用英文技能副本（与 `.claude\skills` 对照，见 `AGENTS.md`） | ✅ |
| `自动维护知识库\index.md` | wiki 总目录（61 页） | ✅ |
| `自动维护知识库\log.md` | 操作时间线（append-only） | ✅ |
| `自动维护知识库\LLM Wiki.md` | Karpathy 方法论文档 | ✅ |
| `自动维护知识库\CLAUDE.md` | wiki 层维护规范 | ✅ |
| `自动维护知识库\wiki\` | 61 个知识页面（10 大类） | ✅ |
| `总结好的大纲以及笔记\` | 原始来源（只读）：学校/实习就业/技能/浪尖训练营/知识库FAQ | ✅ |
| `总结好的大纲以及笔记\知识库FAQ\00-报错统计台账.md` + 01~11 档案 | 报错修复索引 | ✅ |
| `飞书智能助手\` | server.py + config.json + restart.bat（⚠️ 勿用 restart.bat，杀所有 python） | ✅ |
| `微信智能助手\` | server.py(FastAPI) + config.json + NSSM 服务 + LocalTunnel | ✅ |
| `lark-resources\` / `wecom-resources\` | 飞书/企微上传文件的落地目录（处理完不清理） | ✅ |
| `收件箱\` | 规则中的待整理区 | ⚠️ 当前不存在（见风险 3） |
| `已整理好的文件\` | 规则中的只读归档区 | ⚠️ 当前不存在（见风险 3） |
| `.yolov8m-seg.pt.*.part` | 约 39MB 半成品下载 | ⚠️ 可清理/确认 |

## 4. 已完成工作（全量逐条，供快速核验）

1. **规则体系**：`CLAUDE.md` + `.claude/CLAUDE.md` + `.claude/LLM-WIKI-SCHEMA.md` + `自动维护知识库/CLAUDE.md` 四层规则齐备。
2. **wiki 内容**：`自动维护知识库/index.md` 记录 61 页（10 大类），与 `wiki/` 实际文件一致（2026-08-17 已 lint 核对，无孤儿页）。
3. **自动化 Hook**：`.claude/hooks/kb-maintenance-check.sh` 已注册进 `settings.json` 的 `UserPromptSubmit`，逻辑见文件头注释（wiki ≥3 天、GitHub ≥7 天或周一触发）。
4. **GitHub 备份**：仓库 `https://github.com/xieji-star/jichang-zhishiku`（账号 `xieji-star`），方式=新建日期文件夹 `积昌的知识库<MMDD>` 后 `git add -A + commit + push`，只保留最近 10 版。
5. **飞书助手**：`飞书智能助手/server.py` v2.0.0；架构 `飞书 → lark-cli event consume → server.py → Claude CLI → Vault`；会话状态机 IDLE/AWAITING_INSTRUCTION/CLARIFYING/PROCESSING；部署标记"公司用"。
6. **企业微信助手**：`微信智能助手/server.py`（FastAPI）；`server.host=127.0.0.1, port=8800`；LocalTunnel 内网穿透；NSSM 注册为 Windows 服务；回调流程见文件头 docstring。
7. **Claude CLI 配置**：两个助手的 `config.json` 均把 Claude CLI 指向 `...WinGet\Packages\Anthropic.ClaudeCode_...\claude.exe`，且通过 `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic` 走 DeepSeek 模型（token 见风险 3，已脱敏）。
8. **技能包**：`.claude/skills/` 约 27 个；Codex 副本 `.agents/skills/`；双语对照表在 `AGENTS.md` 第 3 节。

## 5. 当前精确进度

- 最后一步有效操作：**2026-08-17 的 ingest/lint 全库迭代**（见 `自动维护知识库/log.md` 最新条目）——更新了 `wiki/自媒体运营/短视频爆款采集系统` 页面（frontmatter 来源 3→7），并 lint 确认 61 页与 index 一致、收件箱为空。
- 标记文件现状：`.last-wiki-maintain`=2026-08-17，`.last-github-backup`=2026-08-17，`.last-maintenance-prompt`=2026-08-17。
- **你的起点**：规则与内容均已就绪，无待办的半成品。从"维护者模式"开始即可。

## 6. 未完成事项（全量逐条）

| # | 事项 | 触发条件 | 前置 | 优先级 | 完成标准 |
|---|---|---|---|---|---|
| 1 | LLM Wiki 迭代（ingest/query/lint） | `.last-wiki-maintain` 距今 ≥3 天（预计 2026-08-20） | 有 ≥3 天新资料或用户要求 | 高 | 走完一轮，同步 `index.md` + `log.md`，更新 `.last-wiki-maintain` |
| 2 | GitHub 备份 | 周一 或 `.last-github-backup` ≥7 天 | 无 | 高 | push 成功 + 新建 `积昌的知识库<MMDD>` + 只留 10 版 + 更新 `.last-github-backup` |
| 3 | 新资料 ingest | 收件箱/飞书/企微有新文件 | 有来源 | 中 | 写成 wiki 页 + 更新 index/log |
| 4 | 报错处理 | 用户报错 | 出现文件/网络类报错 | 中 | 走 `知识库报错修复` skill 流程 + 写台账 |

## 7. 下一步行动计划（命令级）

> 按顺序执行。每条都有"预期产出/验证"。

1. **加载规则与现状**（立即做）：
   ```powershell
   Set-Location "F:\积昌的知识库 - 副本"
   Get-Date                       # 先读当前时间（本库规则：每日首条指令先显示时间）
   ```
   预期：看到日期时间；随后用 Read 读第 1 节列出的规则文件与 `自动维护知识库\index.md`。

2. **判断是否到期**：
   ```powershell
   Get-Content ".last-wiki-maintain", ".last-github-backup"
   ```
   计算距今天数。≥3 天 → 执行 LLM Wiki 迭代；今天周一或 ≥7 天 → 执行 GitHub 备份。规则细节见 `CLAUDE.md`「定期上传 GitHub 规则」与「LLM Wiki 迭代规则」。

3. **例行迭代（如到期）**：按 `.claude/LLM-WIKI-SCHEMA.md` 走 ingest/query/lint，完成后：
   ```powershell
   Set-Content ".last-wiki-maintain" (Get-Date -Format 'yyyy-MM-dd')
   ```

4. **GitHub 备份（如到期）**：
   ```powershell
   $d = Get-Date -Format 'MMdd'
   New-Item -ItemType Directory -Path "积昌的知识库$d" -Force
   git add -A; git commit -m "知识库备份 $(Get-Date -Format 'yyyy-MM-dd')"; git push
   ```
   保留最近 10 个日期文件夹；完成后更新 `.last-github-backup` 为当天。

5. **日常 ingest**：用户提供新来源（文件/链接/消息）→ 读来源 → 与用户讨论要点（可选）→ 写入/更新 `wiki/` 页面 → 更新 `index.md` → 追加 `log.md`。来源文件本身只读，不改写；需要归档的成品按用户明确指令移入 `已整理好的文件/`。

## 8. 环境与配置依赖（完整清单）

| 依赖 | 值/位置 | 说明 |
|---|---|---|
| Obsidian vault 根目录 | `F:\积昌的知识库 - 副本` | 所有操作以此为根；**注意规则文件写的是 E:，实际是 F:** |
| Claude CLI | `C:\Users\asus\AppData\Local\Microsoft\WinGet\Packages\Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe\claude.exe` | 两个 IM 助手调用它 |
| DeepSeek 中转 | `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`；`ANTHROPIC_MODEL=deepseek-v4-flash` | 在 `飞书智能助手\config.json` 与 `微信智能助手\config.json` 中；token 见风险 3 |
| 飞书工具 | `lark-cli`（事件消费/发消息） | 飞书助手依赖；身份分"落日"(user) 与"谢积昌的飞书CLI"(bot) |
| 企业微信回调 | `127.0.0.1:8800`；LocalTunnel；NSSM 服务 | 见 `微信智能助手\config.json` |
| Hook 脚本 | bash（Windows Git Bash） | `kb-maintenance-check.sh` 需 bash 环境 |
| Node.js | 22+（impeccable UI Hook 才需要） | 缺失时该 Hook 降级，不影响核心功能 |
| 密钥/token | 见 `飞书智能助手\config.json`、`微信智能助手\config.json` | ⚠️ 已脱敏，不外泄 |
| Git | 需配置好 `xieji-star/jichang-zhishiku` 远程 | 每周备份用 |

## 9. 数据与状态快照

- **wiki**：61 页与 index 一致；无孤儿页；收件箱为空。
- **日志**：`自动维护知识库/log.md` 自 2026-07-14 起持续追加，最新条目 2026-08-17。
- **标记文件**：三者均 2026-08-17。
- **IM 资源目录**：`lark-resources/`、`wecom-resources/`、`lark-im-resources/` 存放上传文件，处理完**不清理**（用户可能后续使用）。
- **半成品残留**：根目录 `.yolov8m-seg.pt.e672...part`（39MB）——疑似模型下载残留，可清理或人工确认。

## 10. 关键决策与踩坑记录（AI 侧重点）

- **文档查询顺序（硬性）**：查资料只走 `index.md → 定位页面 → 深入读取` 的窄路径；**禁止全库 find/ls/grep 扫描式检索**（规则原文，见 `.claude/CLAUDE.md`「知识库文件查阅规则」）。
- **文档创建/编辑一律用 `/文档转换+排版` skill**（规则强制）。
- **飞书 `restart.bat` 是雷**：它 `taskkill /f /im python.exe` 会杀光所有 Python 进程（含 Claude 自己）。启动飞书助手只能 `cd 飞书智能助手 && python server.py`（不要用 restart.bat）。
- **Codex/网络故障档案**：`总结好的大纲以及笔记/知识库FAQ/` 01~11 是按"公寓/青旅/公司"环境分类的排障档案，换网络先查它（尤其 04/05/06/10/11）。
- **`已整理好的文件/` 只读**：除非用户明确指令，任何情况下不得修改该区域（当前该目录不存在，见风险 3）。
- **人 vs AI 交接方法论**：需要交接文档时加载 `交接助手` skill，并按 `references/agent-profiles.md` 定制（本部分即按 Claude Code 档案定制）。

## 11. 续作启动手册 + 如何验证续上了

**从零恢复完整步骤：**
1. `Set-Location "F:\积昌的知识库 - 副本"` → `Get-Date`。
2. Read 依次：`CLAUDE.md` → `.claude\CLAUDE.md` → `.claude\LLM-WIKI-SCHEMA.md` → `自动维护知识库\index.md` → `自动维护知识库\log.md`。
3. 读标记文件，判定到期任务。
4. 按需执行迭代/GitHub 备份/ingest（见第 7 节）。
5. 如需启动 IM 服务：飞书 `python server.py`；企微 `start-with-tunnel.bat` 或 NSSM 服务。

**如何验证"续上了"（出现以下任一即算接住）：**
- ✅ 你成功读完规则，能说出三层架构各自路径；
- ✅ `index.md` 统计为 **61 页 / 10 大类**，且与 `wiki/` 实际一致；
- ✅ `Get-Content .last-wiki-maintain, .last-github-backup` 输出 `2026-08-17`（未到期）；若到期，你执行了对应任务并更新了日期；
- ✅ 你能跑 `git -C "F:\积昌的知识库 - 副本" status` 看到仓库干净（备份后）；
- ✅ 飞书助手启动日志出现 `开始监听飞书消息` 与 `lark-cli 进程 PID`；企微服务监听 `127.0.0.1:8800` 可通。

## 12. 按 Claude Code 定制的附加说明

- **自动加载规则**：根 `CLAUDE.md` 会被 Claude Code 自动加载；遇到规则与指令冲突，**立即停下问用户澄清**，不得擅自选择（规则强制）。
- **多 Agent**：若用户明确说"重任务"，可启动最多子代理并行，并必须一并调用 `.claude\agents\代码总监.md` 子代理做独立裁判/防偏航；默认轻任务单代理即可。
- **子代理权限**：子代理遇到权限不足不得停下来请求授权，应改用可行替代方式并在结果中说明（规则强制）。
- **提问边界**：只允许问"做什么/怎么做"；禁止问"能不能给权限/能不能做"。
- **临时文件**：`_`/`temp_`/`tmp_` 开头的临时脚本、`test_*.png`、`benchmark.json` 等可自主删除；其余删除必须先问用户。

---

> [!note] 两版说明
> 以上 **第一部分（给人版）** 面向人类读者，含背景叙述、术语表、手把手步骤、求助点；
> **第二部分（给 Claude Code 版）** 可直接复制给下一个 Claude Code 会话作为启动上下文，精确到路径与命令。
> 若后续要交接给 **Codex**，请按 `.claude/skills/交接助手/references/agent-profiles.md` 中的 Codex 档案另行定制（PowerShell 命令、从哪个函数继续、查 config.toml、代理注意事项）。
