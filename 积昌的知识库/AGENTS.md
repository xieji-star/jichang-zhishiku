# AGENTS.md — 积昌的知识库（Codex 规则入口）

> 本文件是 **OpenAI Codex** 在本知识库（Obsidian vault）中的工作规则入口。
> Claude Code 的规则文件是 `CLAUDE.md`，Codex 的规则文件是本文件（`AGENTS.md`）。
> 两者描述的是**同一套规则**：完整规则保存在 `.claude/` 目录中，Codex 必须先按第 1 节加载规则，再执行任何任务。
> 本文件与 `CLAUDE.md`、`.claude/CLAUDE.md` 内容冲突时，以用户最新指令为准。

---

## 0. 本知识库是什么

- 本知识库是一个基于 LLM Wiki 方法论（Karpathy《LLM Wiki》）运行的 Obsidian 知识库（"积昌的知识库"简称"知识库"）。
- 三层架构：
  - **契约层（规则）**：`.claude/` → `CLAUDE.md` + `LLM-WIKI-SCHEMA.md`
  - **wiki 层（由 AI 维护）**：`自动维护知识库/` → 含 `index.md`（总目录）、`log.md`（时间线日志）、来源页、概念页
  - **原始层（待整理）**：`收件箱/`
  - **归档区**：`已整理好的文件/`（用户拥有，只读，未获明确指令不得修改）
- 你的 Skills 位于 `.agents/skills/`（Codex 自动发现），与 `.claude/skills/` 中的技能一一对应（Codex 侧为英文名版本，见第 3 节对照表）。

## 1. 会话开始必做：加载规则（第一步，禁止跳过）

开始任何任务之前，必须依次**完整读取并严格遵守**以下文件：

1. `CLAUDE.md`（根目录）——知识库定义、任务执行准则、临时文件清理规则、飞书/企业微信任务规则、GitHub 备份规则
2. `.claude/CLAUDE.md` ——知识库硬性规则（命名规则、文件夹权限、Skill 安装位置、权限模式、文档查询顺序等）
3. `.claude/LLM-WIKI-SCHEMA.md` ——LLM Wiki 维护契约（ingest / query / lint 工作流、页面规范）
4. `自动维护知识库/index.md` ——wiki 总目录，用于定位本次任务需要查阅的文档

> **路径基准**：本文件所在目录（vault 根目录）即"知识库"根目录。操作 vault 内文件一律使用**相对路径**，禁止用绝对路径操作 vault 内文件。

## 2. 核心规则摘要（详细规则以第 1 节加载的文件为准）

### 语言
- 一律使用**简体中文**交流与输出；代码、命令、API 参数名、专有名词、文件路径、引用的原文除外。

### 文件夹权限（硬性）
| 文件夹 | 权限 |
|---|---|
| `已整理好的文件/` | **只读**——仅用户明确下达指令时才允许修改（编辑/删除/移动/重命名） |
| `自动维护知识库/` | **可自由修改**——可随意创建、编辑、维护 |
| `收件箱/` | **可编辑**——可整理、移动、重命名 |

### 文件夹 vs 文档（硬性）
- "创建文件夹" = 创建真实目录；"创建文档" = 创建 .md 文件。二者禁止混淆，表达含糊时先问用户。

### 文档查询顺序（LLM Wiki 检索法）
- 先读 `自动维护知识库/index.md` 定位相关页面 → 明确目标文件后，再去 `已整理好的文件/` 深度阅读目标笔记。
- **禁止**全库扫描式检索（不得列出整个 vault 的文件逐个试读）。

### 执行方式
- 用户已授予全部权限：**直接执行**，禁止询问"能不能做/可不可以给权限"。
- 对指令有不明白之处时，只允许问"做什么 / 怎么做"，问清楚再动手。
- 执行中发现规则与指令冲突，立即停下来向用户询问澄清，不得擅自决定。

### 文档创建与编辑排版
- 凡是涉及文档的创建或编辑，一律先调用 `doc-conversion-formatting` skill（对应 Claude 侧「文档转换+排版」）处理。

### 临时文件清理
- 任务结束后删除临时产物：`_` / `temp_` / `tmp_` 开头的临时脚本、测试文件、缓存、中间文件；不确定是否该删的先问用户。

### GitHub 定期备份
- 每 3 天将整个知识库上传到 `https://github.com/xieji-star/jichang-zhishiku`（仓库内新建日期文件夹 `积昌的知识库<MMDD>`，如 `积昌的知识库0805`；只保留最近 10 版，超出删除最早版本）。
- 除非用户明确说不上传，到期自动执行。上传前先读取当天时间，提交信息中包含日期。

### LLM Wiki 每周维护
- 每次会话开始检查 `.last-wiki-maintain` 标记文件：若距上次整理已满 7 天，先执行一轮 ingest / query / lint 整理（含 `index.md` 与 `log.md` 同步维护），完成后把标记文件更新为当天日期。

### 自动化任务（飞书 / 企业微信）
- prompt 以"🔴 自动化任务 — 来自飞书/企业微信"开头时：**禁止任何飞书操作（企业微信任务）**，或按规则执行；直接行动，回复 100–200 字，完整内容写入 vault 指定路径（`lark-resources/` / `wecom-resources/` 存放上传文件，处理完成后不清理）。

### 飞书任务身份（仅飞书任务适用）
- 文档增删改查 → 用户"落日"（`--as user`）；文档总结/读书笔记整理 → bot 身份（`--as bot`）；上司/mentor 相关文件处理 → 一律 `--as user`。

## 3. Skills 使用

- 在 Codex 中输入 `/skills` 可查看全部可用技能（位于 `.agents/skills/`，Codex 自动扫描加载）。
- 触发方式与 Claude 相同：由各 SKILL.md 中 `description` 描述的场景自动触发。
- 与 Claude 侧中文名的对应关系（Codex 内使用**英文名**）：

| Codex skill（.agents/skills/） | 对应 Claude skill（.claude/skills/） |
|---|---|
| `lark-*`（27 个，飞书系列） | `飞书智能助手/lark-*` |
| `feishu-manual-takeover` | `飞书智能助手/feishu-manual-takeover` |
| `ai-consultant` | AI咨询师 |
| `excalidraw-diagram` | Excalidraw图表 |
| `jd-analysis` | JD深度剖析 |
| `llm-knowledge-base` | LLM知识库 |
| `bm-md` | Markdown排版工具 |
| `frontend-design` | frontend-design |
| `wecom-summary` | 企业微信总结 |
| `meeting-notes-organizer` | 会议笔记整理 |
| `huage-script-writing` | 华哥脚本撰写 |
| `innovation-competition-mentor` | 国创赛导师 |
| `sop-workflow-organizer` | 工作SOP与业务线整理 |
| `skill-health-check` | 技能健康检查 |
| `skill-creator` | 技能创建工具 |
| `skill-search` | 技能搜索 |
| `prompt-optimizer` | 提示词优化 |
| `boost-prompt` | 提示词优化（英文原版） |
| `doc-conversion-formatting` | 文档转换+排版 |
| `daily-report-assistant` | 日报助手 |
| `mock-interview` | 模拟面试 |
| `kb-error-repair` | 知识库报错修复 |
| `resume-material-recorder` | 简历素材记录 |

> 维护约定：`.agents/skills/` 是 Codex 专用副本（英文名 + Codex 严格格式），`.claude/skills/` 是 Claude 原版（中文名）。两处内容应保持一致；新增/更新 skill 时同步两处。

## 4. 其他

- 知识库规则文件指代："知识库的规则" = `.claude/` 文件夹。
- 遇到本文件未覆盖的场景，以 `.claude/CLAUDE.md` 与根 `CLAUDE.md` 的完整规则为准。
