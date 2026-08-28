# LLM Wiki Schema / 知识库 Wiki 维护规范

依据 Andrej Karpathy《LLM Wiki》方法论（原文见 `自动维护知识库/来源/Karpathy LLM Wiki.md`）制定。
本文件是知识库 wiki 层的**契约（schema）**：定义结构、约定与工作流，让 Claude 成为"有纪律的 wiki 维护者"而非通用聊天机器人。
本文件与 `.claude/CLAUDE.md` 一并阅读；两者冲突时以用户最新指令为准。

Based on Andrej Karpathy's "LLM Wiki" methodology (original: `自动维护知识库/Karpathy LLM Wiki.md`).
This file is the **schema** of the knowledge base's wiki layer: it defines structure, conventions, and workflows so that Claude acts as a "disciplined wiki maintainer" rather than a generic chatbot.
Read this file together with `.claude/CLAUDE.md`; when they conflict, the user's latest instruction wins.

---

## 1. 三层架构 / Three Layers

| 方法论层 (Methodology) | 本知识库落点 (In this vault) | 角色 (Role) |
|---|---|---|
| Raw sources（原始层） | `收件箱/`（含 `待整理/`、`飞书/<日期>/`） | 待整理的来源材料，LLM 读取后整理；可编辑（见 CLAUDE.md 权限规则） |
| The wiki（wiki 层） | `自动维护知识库/` | LLM 维护的 markdown 页面：索引、日志、来源页、概念页、综合页。可自由修改 |
| The schema（契约层） | `.claude/CLAUDE.md` + `LLM-WIKI-SCHEMA.md` | 规定结构、约定与工作流 |

补充说明 / Note:
- `已整理好的文件/` 是用户拥有并**只读**的归档区（仅有用户明确指令时才能修改），不属于 wiki 层，但 wiki 页可链接到其中的笔记。
  (`已整理好的文件/` is a user-owned, READ-ONLY archive (modifiable only on explicit user instruction); it is not part of the wiki layer, though wiki pages may link to its notes.)
- 原始材料进入 `收件箱` → 整理后：wiki 页写入 `自动维护知识库/`；需要归档的成品笔记由用户决定是否放入 `已整理好的文件/`（用户指令下执行）。
  (Raw material lands in `收件箱` → after organizing: wiki pages go into `自动维护知识库/`; finished notes for archiving go into `已整理好的文件/` only under user instruction.)

## 2. 核心文件 / Core Files

### index.md（内容导向目录 / content-oriented catalog）
- 位于 `自动维护知识库/index.md`，是 wiki 全部页面的目录：每页一行（链接 + 一句话简介 + 可选元数据：来源、日期），按分类组织。
- 每次 ingest 后必须更新。回答查询时先读 index 定位相关页，再深入。
- 规模提示：约 100 个来源、数百页以内，纯 index 检索足够，无需 embedding/RAG 基建。

### log.md（时间线日志 / chronological log）
- 位于 `自动维护知识库/log.md`，**只追加（append-only）**，记录做了什么、何时做的（ingest / query / lint）。
- 每条目统一前缀格式，保证可用 unix 工具解析：
  ```
  ## [YYYY-MM-DD] <动作> | <标题>
  ```
- 常用命令：`grep "^## \[" log.md | tail -5` 查看最近 5 条。

## 3. 工作流 / Workflows

### Ingest（摄入）
1. 用户投入新来源（文件/链接/消息），放入 `收件箱/`；
2. LLM 读取来源（文本优先；图片单独查看补充上下文）；
3. 与用户讨论要点（可选）；
4. 在 `自动维护知识库/` 写入/更新页面：来源摘要页、相关概念页、索引 index.md；
5. 在 log.md 追加条目：`## [YYYY-MM-DD] ingest | <标题>`；
6. 建议：逐个来源摄入、用户全程参与；也可按用户要求批量。
7. 原始文件本身保持不变（整理完成的成品若用户要求归档，经明确指令移入 `已整理好的文件/`）。

### Query（查询）
- 先读 `自动维护知识库/index.md` 定位相关页，再读取页面，综合回答并给出引用。
- **好的回答可以存回 wiki**：比较表、分析、发现的联系等有价值的内容，与用户确认后作为新页面存入 `自动维护知识库/`，并在 log.md 追加 `query` 条目——让探索像 ingest 一样复利积累。

### Lint（体检）
- 周期性（或用户要求时）检查 wiki 健康度：页面间矛盾、被新来源取代的过时说法、无入链的孤儿页、被提及但无专页的重要概念、缺失的交叉引用、可用网络搜索补足的数据缺口。
- 在 log.md 追加 `lint` 条目，记录发现与修复。

## 4. 页面规范 / Page Conventions

- 页面使用 YAML frontmatter（方便 Dataview 动态生成表格）：
  ```yaml
  ---
  title: <标题>
  source: <来源 URL/路径>
  source_type: <类型：GitHub Gist / 网页 / PDF / 飞书消息 ...>
  fetched_at: <YYYY-MM-DD>
  tags: [<标签>]
  ---
  ```
- 交叉引用用 wiki 链接 `[[页面名]]`；对 `已整理好的文件/` 内的笔记也可链接。
- 原始来源页（如 Karpathy LLM Wiki 原文）保持正文原样，只允许加 frontmatter，不改写原文；改写/综合内容放到独立的 wiki 页面。
- 分类建议（按需增减）：方法论 / 概念 / 来源 / 综合 / 个人 / 项目。

## 5. 维护纪律 / Maintenance Discipline

- 只维护 `自动维护知识库/` 与 `收件箱/`；**不触碰** `已整理好的文件/`（除非用户明确指令）。
- index.md 与 log.md 是 wiki 的骨架，任何写入/更新后必须同步维护二者。
- 本 schema 本身与用户规则共同演进：发现不适用或更好的约定时，向用户提出并更新本文件。
