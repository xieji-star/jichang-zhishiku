---
title: Claude Code支持的多Agent开发模型下能够调用最多多少个子Agent
type: 概念笔记
date: 2026-08-15
tags:
  - AI工具
  - Claude Code
  - 多Agent
  - Subagent
  - 并发
  - 概念
source: Anthropic 官方更新日志、Claude Cookbook、开发者社区（classmethod / dev.to / zubnet / tembo 等）
---

# Claude Code支持的多Agent开发模型下能够调用最多多少个子Agent

> [!summary] 概要
> Claude Code 的「多 Agent 开发」本质上是**主代理（主 Claude）派生子代理（Subagent）并行干活**的模型。关于「最多能用多少个 Agent」，**没有一个单一的固定数字**——它取决于你问的是「能定义多少个」还是「能同时跑多少个」：**能定义的子代理数量理论上无上限**（就是一个文件的事），而**能同时运行的数量受版本与功能限制**。按 2026 年 8 月的最新版本：普通子代理**并发默认上限 20 个**（可用 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` 调高）；会话累计 spawn 上限原本是 200 个，已在 v2.1.224 移除（理论上可无限）；而 Dynamic Workflows（动态工作流）这个专门做大规模并行的特性，则是**并发 16 个、单次运行总量 1000 个**的硬上限。实际开发中，官方与社区都建议**从 2–4 个并发起步**，别一上来就拉满。另注意：这里的「20 并发」是 Claude Code CLI 的限制；若你在 Obsidian 聊天窗口里只看到「最多同时 3 个」，那是该集成环境独立的并发上限（详见 2.1 节）。

## 相关笔记

- [[Claude Code中Hook的概念]] — 同目录概念笔记，含 Subagent 与 Hook/Skill 的对比表
- [[Claude Code 与 Codex 对比]] — Claude Code 与 Codex 的架构对比
- [[SKILL的定义以及使用]] — 与 Subagent 同为 Claude Code 扩展机制
- [[Claude Code打造AI秘书团]] — 多 Agent 的应用玩法

## 索引

- 🔍 [[#1. 先分清两个“数量”——能定义 vs 能同时跑]] — 回答前必须先澄清的关键区分
- ⚙️ [[#2. 普通子代理的并发上限：默认 20（可调）]] — `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`
- ⚠️ [[#2.1 特别说明：为什么我在 Obsidian 聊天窗口里最多同时调用 3 个]] — CLI 的 20 并发 vs 本窗口的 3 并发
- 🪆 [[#3. 子代理还能再派子代理吗？——嵌套深度限制]] — `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`
- 🚀 [[#4. 会话累计 200 个的上限已被移除（v2.1.224）]] — 从「200 封顶」到「理论无限」
- 🌀 [[#5. Dynamic Workflows：16 并发 / 1000 总量的硬上限]] — 大规模并行的专用特性
- 💰 [[#6. 预算类限制：--max-budget-usd]] — 花钱上限也会卡住 spawn
- 📊 [[#7. 一张表汇总所有“上限”]] — 快速查阅
- 💡 [[#8. 实践建议：从 2–4 个并发起步]] — 别一上来就拉满
- ⚡ [[#9. 一分钟速记]] — 一句话带走核心

## 1. 先分清两个「数量」——能定义 vs 能同时跑

「最多能用多少个 Agent」这个问题，其实混着两个完全不同的概念，必须拆开看：

- 🗂️ **<span style="color:#2980b9">数量①：能定义/注册多少个子代理（Agent）</span>**
  - 自定义子代理就是放在 `.claude/agents/`（项目级）或 `~/.claude/agents/`（用户级）目录下的一个 `.md` 文件，YAML frontmatter 里写明名字、描述、可用工具、模型。
  - 你建多少个文件，就有多少个子代理——**理论上无上限**，只受磁盘空间限制。
  - 除此之外还有**内置子代理**（如 general-purpose、Explore、Plan 等），以及社区编排框架（如 oh-my-claudecode 一次性定义 **19 个专业 Agent**）可以参考。

- 🏃 **<span style="color:#e74c3c">数量②：能同时/累计运行多少个（这才是真正的瓶颈）</span>**
  - 「运行」受**并发数、嵌套深度、会话累计、预算**等多重限制，这些才是官方在 2026 年几个版本里反复调整的地方（第 2–6 节逐一说明）。

>highlight 【一句话理解】「能建多少 Agent」几乎没限制；真正有上限的是「能同时跑多少 Agent」——这取决于 Claude Code 的版本和功能开关。

## 2. 普通子代理的并发上限：默认 20（可调）

- 🔥 **<span style="color:#e74c3c">Claude Code v2.1.217（约 2026-07-21 发布）引入了「最大并发子代理数」，默认值为 20 个</span>**
  - 也就是：**同一条消息里，最多同时有 20 个子代理在后台并行运行**。
  - 官方给它的定位很直白：**防止单条消息无限地 spawn 后台 Agent**（否则一个指令可能瞬间拉起成百上千个进程，把机器和 API 配额都拖垮）。

- ⚙️ **<span style="color:#e67e22">可以通过环境变量调高/调低：`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`</span>**
  - 例：想允许 50 个并发，就设置 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=50`。
  - 注意：调得越高，越考验你的 API 配额、机器性能和 review 流程——上限是「防呆」用的，不是「推荐值」。

## 2.1 特别说明：为什么我在 Obsidian 聊天窗口里最多同时调用 3 个

如果你发现自己在**当前这个 Obsidian 聊天窗口**里，一次最多只能并行调用 3 个子代理，而不是上面说的 20 个——这是正常的，因为**两套环境的限制根本不是一回事**：

- 🧩 **<span style="color:#e74c3c">前面的 20 / 16 / 1000 是「Claude Code CLI（命令行工具）」的限制；你现在用的窗口是「Obsidian 内的 Claude 集成助手（Claudian）」，它派子代理走的是另一套独立实现</span>**
  - 也就是说：`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` 这类环境变量**只在标准 `claude` CLI 里生效**，这个 Obsidian 窗口不读它，它有自己的并发控制（从你的观察看，默认是 3）。

- 📦 **<span style="color:#e74c3c">主要原因①：上下文 / Token 预算保护</span>**
  - 每并行一个子代理，它的返回结果都要回流到主会话，成倍占用上下文窗口；3 个并行已经会吃掉大量 Token。若放开到 20 个，主上下文会瞬间膨胀，很快触发压缩（compaction）或丢信息。限制到 3，是「并行收益 vs 上下文消耗」之间的折中。

- 🔢 **<span style="color:#2980b9">主要原因②：底层模型单次响应的并行工具调用上限</span>**
  - 「并行派子代理」= 在同一条消息里同时发出多个 Agent 工具调用；底层 Claude API 对单条回复能携带的工具调用块数量有限，这个窗口在此基础上进一步收敛到了 3。

- 🛡️ **<span style="color:#2980b9">主要原因③：防止写冲突 + 界面稳定</span>**
  - 多个子代理同时读写知识库的同一批文件，容易互相覆盖、产生冲突；控制并行数能降低冲突风险，也让 Obsidian 界面保持稳定、不卡顿。

- 🎯 **<span style="color:#e67e22">原因④：产品定位决定的保守默认值</span>**
  - 这个窗口定位是「知识库管理助手」，典型任务（查资料、写笔记、整理文档）用 2–3 个并行子代理已经够用，几十上百个 Agent 并行反而容易失控，所以默认设得比较保守。

- 📌 **<span style="color:#e67e22">说明：以上①②③④是结合「环境差异 + 上下文/Token 机制 + 并行工具调用原理」的分析；这个窗口的具体并发参数属于产品实现细节，官方若给出确切数字，以当前集成助手的文档为准</span>**

>highlight 【一句话理解】「20 个」是 CLI 的调参上限，「3 个」是这个 Obsidian 窗口的默认并发——两者不冲突，只是环境不同。真要做几十上百个 Agent 的大规模并行，得回到标准 Claude Code CLI（或 Dynamic Workflows）里做。

## 3. 子代理还能再派子代理吗？——嵌套深度限制

- 🪆 **<span style="color:#e74c3c">v2.1.217 起，子代理默认不能再 spawn 嵌套子代理（嵌套深度 = 1 层）</span>**
  - 也就是说：主代理派出的子代理，默认只能「自己干活」，不能再往下派孙子代理，避免递归失控。

- ⚙️ **<span style="color:#e67e22">想要更深嵌套，用环境变量 `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 开启</span>**
  - 官方示例给的是 `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=2`（允许派到第二层）。
  - 这个限制和「并发 20」是两回事：一个管「横向同时开多少个」，一个管「纵向能套多少层」。

## 4. 会话累计 200 个的上限已被移除（v2.1.224）

- 🔥 **<span style="color:#e74c3c">早期版本里，一个会话有「200 个已 spawn 子代理」的累计上限</span>**
  - 一旦一个会话累计派满 200 个子代理，就**不再 spawn 新的**，逼你串行干活或重启会话。
  - 这让跑「大批量并行测试 / 多 Agent 代码审查」这类重活时非常憋屈。

- 🚀 **<span style="color:#2980b9">v2.1.224 移除了这个 200 上限</span>**
  - 官方说法是「unlimited subagents」（无限制子代理），把这块长期存在的扩展瓶颈拆掉了。
  - 社区实测：以前一次性 spawn 250 个子代理会失败，升级后可以完整跑完。

- 📌 **<span style="color:#e67e22">「移除 200 上限」指的是会话累计数，不等于「并发无上限」——并发仍受第 2 节的 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` 约束</span>**

## 5. Dynamic Workflows：16 并发 / 1000 总量的硬上限

Dynamic Workflows（动态工作流）是 Claude Code 面向「大规模并行编排」推出的特性（当前为研究预览版），它有自己的硬性上限：

- 🌀 **<span style="color:#e74c3c">并发上限：最多 16 个 Agent 同时运行</span>**
  - 机器 CPU 核心数较少时，这个并发数还会更少（不是固定 16，是「最多 16」）。

- 🧱 **<span style="color:#e74c3c">总量上限：单次运行（per run）最多 1000 个 Agent</span>**
  - 这 1000 是「防失控循环」的兜底硬顶，不是让你去冲的目标；工作流试图 spawn 超过 1000 就会撞墙。
  - 这两个上限**一般不可调**，且因为还在研究预览阶段，行为可能会变。

- 🔧 **<span style="color:#2980b9">它的工作方式</span>**：Claude 动态编写编排脚本，用「并行扇出（fan-out，最多 16 个子代理并行）」+「收敛（critic 子代理互相质询、反复迭代直到答案收敛）」的组合来自动扩展任务。

## 6. 预算类限制：--max-budget-usd

- 💰 **<span style="color:#e74c3c">除了「数量」上限，还有「钱」的上限——`--max-budget-usd`</span>**
  - 一旦预算达到上限，Claude Code 会**停止正在运行的后台子代理，并拒绝新的 spawn**。
  - 换句话说：即使并发数没到 20、会话也没到累计上限，只要钱花完了，一样派不出新 Agent。

- 📌 **<span style="color:#e67e22">跑多 Agent 之前先设好预算，是最实用的「总闸」——它同时约束了 Agent 数量和 API 花费</span>**

## 7. 一张表汇总所有「上限」

| 维度 | 上限值 | 是否可调 | 生效版本 / 特性 |
|------|--------|---------|----------------|
| 可定义的子代理数量 | **无上限**（= `.claude/agents/` 下文件数） | — | 所有版本 |
| 普通子代理**并发** | 默认 **20** | ✅ `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | v2.1.217+ |
| 子代理**嵌套深度** | 默认 **1 层**（不再派生） | ✅ `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` | v2.1.217+ |
| 会话**累计 spawn** | 原 **200**，已移除 → **无限** | — | v2.1.224 |
| Dynamic Workflows **并发** | 最多 **16**（受 CPU 核心影响） | ❌ 一般不可调 | 研究预览 |
| Dynamic Workflows **总量** | **1000 / run** | ❌ 一般不可调 | 研究预览 |
| 预算 | `--max-budget-usd` | ✅ 命令行参数 | 相关版本 |

>highlight 【核心结论】没有「一个数字」能回答所有情况：**日常普通子代理 = 并发默认 20（可调）、累计已不限**；**大规模并行（Dynamic Workflows）= 并发 16、总量 1000**。

## 8. 实践建议：从 2–4 个并发起步

- 🧪 **<span style="color:#e74c3c">别一上来就拉满默认的 20 并发</span>**——那是「防呆上限」，不是「推荐开法」。
- 🐢 **<span style="color:#2980b9">小仓库 / 首次上线，建议先 2–4 个并发</span>**，确认仓库结构、API 配额、代码 review 流程都能承受后，再逐步上调 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`。
- 🎯 **<span style="color:#e67e22">按任务类型选工具</span>**：普通「分工并行」用内置/自定义子代理即可；真正需要上百上千 Agent 的「大规模并行」场景，再考虑 Dynamic Workflows（记得它是研究预览，行为可能变）。
- 🛡️ **<span style="color:#e74c3c">一定先设 `--max-budget-usd` 总闸</span>**——数量上限防不住烧钱，预算上限才是兜底。

## 9. 一分钟速记

- 🔥 **<span style="color:#e74c3c">「最多多少个子 Agent」没有单一答案：能定义 = 无上限，能同时跑 = 看版本与功能</span>**
- ⚙️ **<span style="color:#e74c3c">普通子代理并发默认 20，`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` 可调</span>**
- 🪆 **<span style="color:#e74c3c">默认子代理不能再派生（嵌套 1 层），`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 可加深</span>**
- 🚀 **<span style="color:#2980b9">会话累计 200 上限已在 v2.1.224 移除，理论上无限</span>**
- 🌀 **<span style="color:#e74c3c">Dynamic Workflows：并发 16、单次总量 1000（硬上限）</span>**
- 💰 **<span style="color:#e74c3c">`--max-budget-usd` 才是真正的总闸，钱花完就派不出新 Agent</span>**

>highlight 【一句话带走】想「建多少 Agent」随便建；想「同时跑多少 Agent」——日常按并发 20（可调）算，大规模并行按 16/1000 算，但无论如何先设好预算上限。

## 参考资料

- [Claude Code v2.1.217 Major Updates（subagent limits and behavior）](https://dev.classmethod.jp/en/articles/20260722-cc-updates-v2-1-217/)
- [Claude Code 2.1.224 Drops 200-Subagent Cap](https://dev.to/gentic_news/claude-code-21224-drops-200-subagent-cap-scale-your-parallel-workflows-now-1hnn)
- [Claude Code Dynamic Workflows: 16 concurrent, 1000 max](https://www.zubnet.ai/news/en/claude-code-dynamic-workflows-parallel-subagents-1000-cap/)
- [Claude Code 2.1.217 Subagent Concurrency and Budget Guide](https://dev.to/ahab_indieseek/claude-code-21217-subagent-concurrency-and-budget-guide-5g9c)
- [Claude Code Multi-Agent Orchestration: 2026 Guide – Tembo](https://www.tembo.io/blog/claude-code-multi-agent-orchestration)
- [Claude Code Parallel Agents & Workflows](https://mcp.directory/blog/claude-code-parallel-subagents-workflows-2026)
- [Orchestrate subagents at scale with dynamic workflows – Claude Cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows)
