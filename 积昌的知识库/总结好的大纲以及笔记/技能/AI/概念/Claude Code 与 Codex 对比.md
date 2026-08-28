---
title: Claude Code 与 Codex 对比
type: 概念笔记
date: 2026-08-04
tags:
  - AI工具
  - Claude Code
  - Codex
  - Skill
  - 概念
source: OpenAI 官方文档、社区资料、知识库既有笔记
---

# Claude Code 与 Codex 对比

> [!summary] 概要
> 本文档回答两个核心问题：① **Codex 中"原本的 .claude 文件"叫什么**——答：Codex 没有 `.claude` 文件，它的对应物是项目指令文件 `AGENTS.md` 和配置文件 `config.toml`（目录为 `~/.codex/` 与 `.codex/`）；② **Codex 的 skill 文件叫什么**——答：`SKILL.md`，与 Claude Code 共用同一套开放的 Agent Skills 标准，但存放位置不同（`.agents/skills/` vs `.claude/skills/`）。文档同时给出两个 AI 编程 agent 在指令体系、配置体系、技能体系、扩展组件上的详细差异对比。

## 相关笔记

- [[Claude Code 从 0 到 1 完全使用教程（Obsidian版）]] — Claude Code 安装与基础配置完整教程
- [[Claude Code 入门与 GitHub 协作开发——完整使用指南（Obsidian版）]] — Claude Code 使用与协作开发指南
- [[Claude Code打造AI秘书团]] — Claude Code 应用场景与玩法
- [[关于MCP调用与子Agent的使用]] — MCP 与子代理（Claude Code 侧）
- [[Codex 零基础系统入门教程]] — Codex 入门教程（含与 Claude Code 对比章节）
- [[Codex模型配置方法大全]] — Codex 模型供应商配置
- [[Codex的5.6三大旗舰模型差异]] — GPT-5.6 三档模型（Sol/Terra/Luna）差异与选择
- [[Codex++使用教程]] — Codex++ 增强工具使用
- [[SKILL的定义以及使用]] — Skill 概念定义与结构
- [[skill调用指南]] — Skill 调用方式
- [[Token的计费方式以及如何更好的省Token]] — Token 计费原理与省 Token 技巧
- [[Claude Code中Hook的概念]] — Hook（钩子）机制概念详解

## 索引

- 🎯 [[#1. 核心答案速览]] — 一句话回答：Codex 里没有 .claude，对应物是 AGENTS.md；skill 叫 SKILL.md
- 🏢 [[#2. 两个软件的基本信息]] — 开发商、定位、使用场景对比
- 📄 [[#3. 指令文件体系对比（.claude ↔ AGENTS.md）]] — 全局与项目指令的发现机制、优先级、上限
- ⚙️ [[#4. 配置文件体系对比（settings.json ↔ config.toml）]] — 模型、权限、沙箱、信任级别等配置项
- 🧩 [[#5. Skill 体系对比（.claude/skills ↔ .agents/skills）]] — SKILL.md 格式、存放位置、调用方式、创建与禁用
- 🧰 [[#6. 其他组件对比]] — 子代理、hooks、会话记录、记忆
- 📊 [[#7. 核心差异总结表]] — 一表看懂全部对应关系
- 💡 [[#8. 实用结论与互通技巧]] — 技能跨软件复用、fallback 配置

## 1. 核心答案速览

🔥 **<span style="color:#e74c3c">Codex 中没有 `.claude` 文件——`.claude` 是 Claude Code（Anthropic）的专属约定。</span>** 用户所说的".claude 文件"，在 Codex 中的对应物是：

- **指令文件**：`AGENTS.md`（项目级）+ `~/.codex/AGENTS.md`（全局），另有 `AGENTS.override.md` 做临时覆盖
- **配置文件**：`config.toml`（相当于 Claude Code 的 `settings.json`）
- **配置目录**：`~/.codex/`（用户级）和 `.codex/`（项目级）

🔥 **<span style="color:#e74c3c">Codex 的 skill 文件叫 `SKILL.md`</span>**——一个 skill 就是一个文件夹，核心是 `SKILL.md`，遵循与 Claude Code 相同的 **Agent Skills 开放标准**，所以同一个技能文件夹两边都能用。

>highlight 【一句话记住】Claude Code 用 `.claude` + `CLAUDE.md`；Codex 用 `.codex` + `AGENTS.md`；两者都用 `SKILL.md` 定义技能，只是技能存放目录不同（`.claude/skills/` vs `.agents/skills/`）。

## 2. 两个软件的基本信息

- **Claude Code**：Anthropic 出品的 AI 编程 agent（命令行工具），以自然语言驱动编码、文件操作、命令执行（安装与入门见 [[Claude Code 从 0 到 1 完全使用教程（Obsidian版）]]，进阶玩法见 [[Claude Code打造AI秘书团]]）
  - 配置目录：`~/.claude/`（用户级）、项目根 `CLAUDE.md`
  - 指令文件：`CLAUDE.md`
- **Codex**：OpenAI 出品的 AI 编程 agent（CLI + IDE 扩展 + 云端应用），早期是 ChatGPT 中的代码执行沙箱，后发展为独立 agent 工具（入门教程见 [[Codex 零基础系统入门教程]]，模型接入配置见 [[Codex模型配置方法大全]]）
  - 配置目录：`~/.codex/`（用户级，可用 `CODEX_HOME` 环境变量改位置）、项目级 `.codex/`
  - 指令文件：`AGENTS.md`
- 💡 **<span style="color:#2980b9">共同点：两者都是"用大白话指挥 AI 写代码/干活"的终端 agent，都支持技能（Skill）、子代理（Agent/Subagent）、钩子（Hook，概念详解见 [[Claude Code中Hook的概念]]）、MCP（模型上下文协议，即把外部工具接入 AI 的统一接口）等扩展机制</span>**

## 3. 指令文件体系对比（.claude ↔ AGENTS.md）

### 3.1 命名与位置

| 层级 | Claude Code | Codex |
|------|-------------|-------|
| 全局指令 | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md`（存在 `AGENTS.override.md` 时优先用它） |
| 项目指令 | 项目根目录 `CLAUDE.md` | 仓库根 `AGENTS.md`，并**向下逐层读取**到当前工作目录 |
| 项目配置 | `.claude/settings.local.json` | `.codex/config.toml` |

### 3.2 AGENTS.md 的发现与优先级机制（重点）

Codex 每次运行按以下顺序构建"指令链"：

1. **全局层**：读 `~/.codex/AGENTS.md`；若存在 `AGENTS.override.md` 则优先使用（临时全局覆盖，不删除基础文件）
2. **项目层**：从 Git 仓库根**逐目录向下**走到当前工作目录，每层检查 `AGENTS.md`，每层至多取一个文件
3. **合并顺序**：从根向下拼接，**越靠近当前目录的文件优先级越高**（拼在最后面，覆盖前面的内容）
4. **大小上限**：累计总大小默认 **32 KiB（约 8000 token）**，超了停止读取；空文件跳过

>highlight 【注意】⚠️ 越靠近当前工作目录的 AGENTS.md 权重越高——这允许子项目"局部覆盖"仓库根目录的全局约定。

- 📊 **<span style="color:#e67e22">上限可调：`project_doc_max_bytes` 配置项可把 32 KiB 上限调大（如 65536）</span>**
- 📌 **<span style="color:#e67e22">AGENTS.md 是纯 Markdown、无严格 schema，相当于项目的"宪法"；Claude Code 的 CLAUDE.md 同理</span>**

### 3.3 互读兼容（fallback 机制）

Codex 支持配置 fallback 文件名，让它**直接读取 CLAUDE.md、.cursorrules 等其他工具的指令文件**：

```toml
# ~/.codex/config.toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md", "CLAUDE.md"]
project_doc_max_bytes = 65536
```

💡 **<span style="color:#2980b9">这意味着一份项目指令可以同时服务 Claude Code 和 Codex，不需要维护两份</span>**

## 4. 配置文件体系对比（settings.json ↔ config.toml）

| 功能 | Claude Code | Codex |
|------|-------------|-------|
| 配置文件 | `settings.json`（JSON 格式） | `config.toml`（TOML 格式） |
| 模型设置 | 模型、temperature 等 | `model`、`model_reasoning_effort`、`model_verbosity` |
| 权限/审批 | permissions 规则 | `approval_policy`、`[permissions.<name>]`、`sandbox_mode` |
| 项目信任 | 每个目录可单独授权 | `[projects."<绝对路径>"].trust_level` |
| MCP 服务器 | mcpServers 配置 | `[mcp_servers.<name>]` |
| 钩子 | hooks（JSON） | `hooks.json`（`~/.codex/hooks.json` 或 `.codex/hooks.json`） |

- 📊 **<span style="color:#e67e22">Codex 的 `config.toml` 还支持 `shell_environment_policy`（环境变量策略）、`[memories]`（记忆配置）等专属项</span>**
- 📌 **<span style="color:#e67e22">设置 `CODEX_HOME` 环境变量可以运行多套 Codex 配置档案，每套拥有独立的 AGENTS.md 和配置</span>**

## 5. Skill 体系对比（.claude/skills ↔ .agents/skills）

### 5.1 共同的 SKILL.md 标准

🔥 **<span style="color:#e74c3c">Claude Code 和 Codex 的 skill 采用同一个开放的 Agent Skills 标准——核心都是 `SKILL.md` 文件</span>**，因此同一个技能文件夹理论上可以直接在两个软件间复制使用（Skill 的概念与结构定义见 [[SKILL的定义以及使用]]，通用调用方式见 [[skill调用指南]]）。

一个标准 skill 的目录结构：

```
my-skill/
├── SKILL.md          # 必需：YAML frontmatter（name + description）+ Markdown 指令正文
├── scripts/          # 可选：可执行的 Python/Bash 脚本
├── references/       # 可选：按需加载的参考文档
├── assets/           # 可选：模板、图标等资源
└── agents/
    └── openai.yaml   # 可选（Codex）：UI 元数据、调用策略、工具依赖
```

- 💡 **<span style="color:#2980b9">SKILL.md 的 frontmatter 只有两个必需字段：`name`（小写字母/数字/连字符，≤64 字符，文件夹名必须与 name 一致）和 `description`（写清"何时触发、何时不触发"，是隐式调用的关键）</span>**
- 💡 **<span style="color:#2980b9">正文仅在技能被触发后才加载，建议控制在 500 行以内，超了就拆到 references/</span>**

### 5.2 存放位置不同

| 作用域 | Claude Code | Codex |
|--------|-------------|-------|
| 项目级 | `.claude/skills/` | `$REPO_ROOT/.agents/skills/`、`$CWD/.agents/skills/` |
| 用户级 | `~/.claude/skills/` | `$HOME/.agents/skills/`（另有 `~/.codex/skills/`） |
| 管理员级 | — | `/etc/codex/skills` |
| 内置 | 随 Claude Code 附带 | `$skill-creator`、`$plan`、`$skill-installer` 等 |

- ⚠️ **<span style="color:#e74c3c">注意：Codex 的项目级技能放在 `.agents/skills/`（不是 `.codex/skills/`），同名技能不会合并</span>**

### 5.3 调用方式

- **隐式调用**：任务与某个技能 `description` 匹配时自动触发（两边都支持）
- **显式调用**：Claude Code 用 `/技能名`；Codex 在提示中输入 `$技能名` 或用 `/skills` 命令

### 5.4 渐进式披露（上下文管理）

Codex 用三级加载控制上下文占用：

1. **元数据**（name + description + 路径）→ 始终在上下文中（约 100 词）
2. **SKILL.md 正文** → 技能触发时才加载
3. **scripts/references/assets** → 按需加载（脚本可直接执行，不进上下文）

- 📊 **<span style="color:#e67e22">初始技能列表最多占用上下文窗口的 2% 或 8000 字符；技能太多时 Codex 会先截短描述、甚至省略部分技能</span>**

### 5.5 创建与禁用

- **创建方式**：Claude Code 手动建文件夹；Codex 额外提供 `$skill-creator` 引导式创建、**Record & Replay**（录制工作流自动草拟技能）
- **禁用技能（不用删除文件）**：Codex 在 `~/.codex/config.toml` 中配置：

```toml
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```

- **跨仓库分发**：Codex 支持把多个技能打包成 **plugin**（技能 + MCP 配置 + 应用集成），一键安装到多个仓库

## 6. 其他组件对比

| 组件 | Claude Code | Codex |
|------|-------------|-------|
| 子代理 | `.claude/agents/*.md` | `~/.codex/agents/`、`.codex/agents/*.md` |
| 钩子（Hook） | settings.json 中配置 | `~/.codex/hooks.json`、`.codex/hooks.json` |
| 会话记录 | `~/.claude/projects/` | `~/.codex/sessions/`（YYYY/MM/DD 归档）、`log/` |
| 记忆 | memory 相关配置 | `~/.codex/memories/`（会话摘要持久化） |
| 认证信息 | 登录态文件 | `~/.codex/auth.json`（OAuth + API Key） |

- 📌 **<span style="color:#e67e22">项目级资源覆盖同名全局资源——两个软件都是这个规则</span>**

## 7. 核心差异总结表

| 维度 | Claude Code | Codex |
|------|-------------|-------|
| 开发商 | Anthropic | OpenAI |
| 项目指令文件 | `CLAUDE.md` | `AGENTS.md`（逐目录向下合并，32 KiB 上限） |
| 全局指令 | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` + `AGENTS.override.md` |
| 主配置 | `settings.json`（JSON） | `config.toml`（TOML） |
| 配置目录 | `.claude/` | `.codex/`（可用 CODEX_HOME 迁移） |
| 技能文件 | `SKILL.md`（同标准） | `SKILL.md`（同标准） |
| 技能位置 | `.claude/skills/` | `.agents/skills/`、`~/.agents/skills/` |
| 技能调用 | `/技能名` | `$技能名`、`/skills` |
| 子代理 | `.claude/agents/` | `.codex/agents/` |
| 钩子 | settings.json hooks | `hooks.json` |
| 会话记录 | `~/.claude/projects/` | `~/.codex/sessions/` |
| 互读对方指令 | 不直接支持 | 可通过 `project_doc_fallback_filenames` 读取 CLAUDE.md |

## 8. 实用结论与互通技巧

- 🔥 **<span style="color:#e74c3c">知识库现有的 `.claude/skills/` 技能是标准 SKILL.md，若想给 Codex 用，把技能文件夹复制到 `~/.agents/skills/` 或项目 `.agents/skills/` 即可，基本不用改格式</span>**
- 💡 **<span style="color:#2980b9">同一项目的 `AGENTS.md` 与 `CLAUDE.md` 内容可以互相引用（Codex 的 fallback 配置直接读 CLAUDE.md），避免维护两份指令</span>**
- ⚠️ **<span style="color:#e74c3c">两者虽然都用 SKILL.md，但 Codex 特有 `agents/openai.yaml`（调用策略、MCP 依赖声明）等可选元数据；Claude Code 的技能如需跨用，先检查描述格式是否兼容</span>**
- 📌 **<span style="color:#e67e22">选择建议：团队/个人已深度使用 Obsidian 知识库 + Claude Code 生态（如本知识库），技能互通成本低；Codex 的优势是 OpenAI 模型生态与插件分发机制</span>**

>highlight 【相关知识】本知识库的 Claude Code 与 Codex 详细操作教程见相关笔记区；Skill 概念与调用细节见 [[SKILL的定义以及使用]] 与 [[skill调用指南]]。

---

写作提醒
`.claude` 文件夹是 Claude Code 专属约定，Codex 里找不到它——问"Codex 的 .claude 文件"时，答 AGENTS.md 与 config.toml 即可。
skill 两边同标准：同是 SKILL.md，位置不同（.claude/skills vs .agents/skills），复制即可互通。
配置细节以官方文档为准：Claude Code 看 Anthropic 文档，Codex 看 developers.openai.com/codex。
