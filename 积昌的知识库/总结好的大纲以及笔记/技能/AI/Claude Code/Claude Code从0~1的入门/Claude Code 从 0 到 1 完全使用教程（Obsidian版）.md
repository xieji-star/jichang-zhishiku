---
title: Claude Code 从 0 到 1 完全使用教程
tags:
  - ClaudeCode
  - GitHub
  - AI编程
  - Obsidian
  - 教程
aliases:
  - Claude Code 从零到一教程
  - Claude Code 完全使用教程
---

# Claude Code 从 0 到 1 完全使用教程

> 本教程基于完整视频课程逐字稿整理，从安装到高级拓展全流程覆盖。内容按原文推进顺序组织，保留全部技术要点，去除口语化重复表达，形成一份可直接上手的完整指南。
>
> 📘 **对照原讲义**：[[Claude Code完全教程【视频文档】.pdf|《Claude Code完全教程【视频文档】.pdf》]] —— 点击链接可打开原讲义。

> [!IMPORTANT]
> 为保证链接正常打开，请确保 PDF 位于当前 Obsidian Vault 内，且路径完全一致：
>
> `AI/Claude Code从0~1的入门/Claude Code完全教程【视频文档】.pdf`

---

## 目录

- [[#一、上手：安装与基础配置]]
- [[#二、基础交互方式]]
- [[#三、掌控 CC：后悔药与上下文管理]]
- [[#四、个性化：让 CC 记住你是谁]]
- [[#五、高级拓展功能]]
- [[#六、常用命令速查表]]
- [[#七、总结]]

## 一、上手：安装与基础配置

📘 [[Claude Code完全教程【视频文档】.pdf|对照原讲义：部署前准备与安装 Claude Code]]

### 1.1 安装准备

- 首先需要下载并安装一个 **Agent IDE**（智能体集成开发环境）。推荐以下免费 IDE：
  - **Cursor**（官网下载）
  - **Google Antigravity**（官网下载）
  - **Trae**（官网下载，分国内版和国际版）
- 以 Cursor 为例，下载完成后构建合适的开发环境布局即可开始。

### 1.2 安装 Claude Code 本体

#### 方式一：终端命令行安装（需魔法上网）

- **Windows（PowerShell）**：

```powershell
# 先安装 Git
winget install Git.Git

# 再安装 Claude Code
irm https://claude.ai/install.ps1 | iex
```

- **Windows（CMD）**：

```cmd
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

- **macOS/Linux**：

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

安装完成后，验证版本号确认安装成功：

```bash
claude --version
```

#### 方式二：Agent 原生安装（需魔法上网）

直接在 IDE 的 Agent 对话中输入提示词：

> 帮我安装 node 并且用 npm 安装好最新的 claude code

完成后同样用 `claude --version` 验证。

#### 方式三：无魔法安装

##### Windows

1. 先用以下命令安装 Git：

```powershell
winget install Git.Git
```

2. 在 IDE Agent 中输入提示词：

> 执行这条代码安装 Claude Code：`winget install Anthropic.ClaudeCode`，安装完后把 Claude Code 的可执行文件路径配置到系统环境变量的 Path 里。

3. 重启 IDE，用 `claude --version` 验证。

##### macOS

1. 先安装 Homebrew：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. 向 IDE Agent 输入：

> 帮我把 Homebrew 加到 PATH 路径变量里面去。

3. 在终端输入：

```bash
brew install --cask claude-code@latest
```

4. 用 `claude --version` 验证。

### 1.3 配置大模型（安装 CC Switch）

📘 [[Claude Code完全教程【视频文档】.pdf|对照原讲义：配置大模型]]

由于 Claude 官方对中国 IP 限制较严，推荐使用 CC Switch 做多模型切换和管理。

- 下载地址：[CC Switch v3.14.1](https://github.com/farion1231/cc-switch/releases/tag/v3.14.1)
- 根据系统选择对应安装包下载安装。
- 务必在打开 Claude Code 之前优先配置 CC Switch：
  1. 在 CC Switch 的 Claude Code 页面添加 API Key 供应商（如 Minimax、DeepSeek 等）。
  2. 填写 API Key 和 Base URL（可从官方文档中获取）。
  3. 选择「启用」设置好的 API，配置完成。

### 1.4 启动与进入项目

- 在 IDE 终端输入 `claude` 回车。
- 根据个人喜好设置皮肤与主题，一路 yes 后进入 CC 主界面。
- 默认情况下，CC 接到任务后会进入计划模式（Plan Mode）。

### 1.5 三种权限模式（Shift+Tab 切换）

| 模式 | 功能说明 |
|---|---|
| 默认模式 | 启动后的初始交互状态，增强版对话终端，用于意图确认、信息查询和简单任务 |
| 计划模式 | 分析需求并制定执行步骤，不直接改动代码 |
| Accept Edits 模式 | 执行代码变更的最终确认与写入 |

额外提醒：

若希望 CC 一路绿灯执行所有操作，重启后输入：

```bash
claude --dangerously-skip-permissions
```

Accept Edits 模式下执行终端命令时，三个选项含义依次是：

- **Yes**：仅同意这一次的命令执行。
- **Yes, and don't ask again for: xxx**：同意且该项目之后执行同类操作不再询问。
- **No**：不同意，再商量。

## 二、基础交互方式

📘 [[Claude Code完全教程【视频文档】.pdf|对照原讲义：基础实操与如何提供文件给 CC]]

### 2.1 最基础的交互：打字对话

直接在终端中输入自然语言指令，Claude Code 会理解并执行。

### 2.2 提供文件给 CC 的三种方式

| 方式 | 操作 | 说明 |
|---|---|---|
| ① @本地文件 | `@文件名` | 让 CC 精准读取指定文件，节省 token。CC 不会每时每刻加载所有文件，@ 操作帮它快速定位 |
| ② 拖拽/粘贴图片 | 拖拽图片到终端 | 利用多模态能力传递设计稿、配色参考等。快捷键：Windows：`Alt+V`；macOS：`Command+V` |
| ③ 多行文本输入 | 在文本框内换行 | 编写长提示词时使用。Windows：`Ctrl+Enter`；macOS：`Option+Enter` |

原则：给 CC 的指令越短，它可能花更多 token 去探索文件；描述越具体，执行越准确。

### 2.3 常用斜杠命令（/）

📘 [[Claude Code完全教程【视频文档】.pdf|对照原讲义：指令大全]]

| 命令 | 作用 |
|---|---|
| `/help` | 显示所有指令及其含义 |
| `/model` | 切换高中低档模型 |
| `/btw` | 临时问与项目无关的问题，与上下文隔离，按 ESC 退出后自动移除 |
| `/simplify` | 派生出 3 个 agent，从代码质量、运行效率、复用性三个角度做代码审核并自动优化 |
| `/rewind` | 进入回滚界面 |
| `/compact` | 主动压缩精简上下文 |
| `/clear` | 彻底清空上下文，重开会话 |
| `/context` | 详细展示当前上下文信息（占比、类别等） |
| `/resume` | 在全新上下文中恢复之前的对话 |
| `/init` | 初始化创建项目级 `claude.md` |
| `/memory` | 管理全局、项目记忆及 Auto Memory |
| `/agents` | 创建、调用、管理子 Agent |
| `/plugin` | 发现新插件、管理已下载插件 |

## 三、掌控 CC：后悔药与上下文管理

📘 [[Claude Code完全教程【视频文档】.pdf|对照原讲义：掌控与管理]]

### 3.1 Git 版本管理（后悔药）

- 在 CC 中输入提示词：“帮我下载 Git，并与我的 GitHub 账号绑定”，CC 会引导完成。
- Git 是项目的“存档系统”，每做完一步就提交一次存档。
- 可直接让 CC 帮你完成：提交存档、推送到远程、回滚到某个版本。
- 💡 建议：养成版本管理习惯，有了 Git 兜底，可放心让 CC 尝试各种方案。

### 3.2 上下文管理

#### 监控上下文

- `/context`：详细展示上下文占比及各模块占用情况。
- 配置常驻显示：向 CC 输入提示词：“帮我配一个 statusLine，显示当前目录+模型+上下文剩余百分比”，重启终端后生效（顶部显示进度条）。

#### 管理流程

- 当上下文占比高于 60% 时，执行 `/compact` 主动压缩。
- 也可执行 `/clear` 彻底清空，重开会话。

#### 恢复历史对话

- 在新会话中输入 `/resume`，选择恢复到你想要的会话。

## 四、个性化：让 CC 记住你是谁

📘 [[Claude Code完全教程【视频文档】.pdf|对照原讲义：个性化]]

### 4.1 claude.md 三级记忆机制

| 级别 | 位置 | 适用范围 | 共享性 |
|---|---|---|---|
| 全局级 | `~/.claude/CLAUDE.md` | 所有项目通用 | 仅自己 |
| 项目级 | 项目根目录 `/CLAUDE.md` | 当前项目 | 团队共享，可提交 Git |
| 文件夹级 | 子文件夹中的 `CLAUDE.md` | 仅对该文件夹生效 | 可提交 Git |

#### 创建方式

- 项目级：输入 `/init`，CC 自动分析项目并生成 `claude.md`（推荐项目有雏形后再初始化）。
- 全局级：
  - 方式一：直接说“记得永远说中文，写进全局 claude.md”。
  - 方式二：输入 `/memory`，选择「User Memory」进入编辑。

#### 最佳实践

- 只放最顶层、基本不变的原则。
- 在使用过程中逐步添加 CC 经常犯的错误。
- 项目级 `claude.md` 应动态更新：项目增加新功能、CC 踩了新坑后及时同步。

### 4.2 Auto Memory（自动记忆）

- 启用：输入 `/memory`，选择「Auto-memory」回车开启。
- 存储位置：`项目目录/.claude/memory/`（仅作用于当前项目）。
- 工作机制：
  - 每次打开项目时，CC 只先加载 `memory.md`（索引文件）。
  - 具体细节按需读取，不占用过多上下文。
  - 每记录一条记忆，终端会显示“wrote N memories”。
- 管理：若记忆有误，直接说“忘掉刚才说的不喜欢浅色主题”，CC 会自动删除。

#### 两层记忆配合

- `claude.md`：第一优先级，全部注入上下文，主动设立的规矩。
- Auto Memory：第二优先级，CC 自己记录的按需注入的规则。

两者配合，CC 会越来越懂你。

## 五、高级拓展功能

📘 [[Claude Code完全教程【视频文档】.pdf|对照原讲义：能力扩展]]

### 5.1 Skills（技能包）

#### 什么是 Skill？

- 本质是一个文件夹 + `skill.md` 文件。
- 包含元信息（名称 + 触发条件）和正文（专业说明书）。
- CC 每次只读取几行元信息，知道有这个说明书存在，什么时候看由大模型自己决定。

#### 推荐 Skill

| Skill 名称 | 功能 | 获取方式 |
|---|---|---|
| Find-Skill | 查找和安装来自 Agent Skill 开放生态的技能 | 将 GitHub 链接给 CC 安装 |
| Frontend-Design | 创建生产级、设计精良的前端界面 | 同上 |
| Skill-Creator | 创建、修改和改进 Skill | 同上 |
| 卡帕西 Skill | 基于卡帕西经验总结，提升编码表现 | 同上 |

- Skill 合集网站：lobehub —— 可按分类查找或查看精选推荐。
- 创建自己的 Skill：可参考网页版教学文档《AgentSkills指南（Claude Code版）》。

#### 安装位置

| 类型 | 路径 |
|---|---|
| 全局 Skill | `~/.claude/skills/` |
| 项目级 Skill | `项目目录/.claude/skills/` |

Claude Code 查找顺序：先项目级，再全局级。项目级可覆盖同名全局 Skill。

#### 触发方式

- 自动触发：CC 根据元信息判断。
- 斜杠强制触发：`/技能名称`，100% 可靠（推荐）。
- 提示词明确指定：在对话中明确要求使用某个 Skill。

### 5.2 MCP 扩展

- MCP（Model Context Protocol）：连接 AI 与外部工具/服务的“转接头”。
- 学习资源：
  - 视频教程：《用神器 Claude Code！打造贴身 AI 秘书团【小白教程】》
  - 文档教程：《Claude Code 教程》

### 5.3 CLI 命令行工具

| CLI 名称 | 功能 |
|---|---|
| 飞书 CLI | 200+ 命令，覆盖消息、文档、多维表格、日历、邮箱等 |
| OpenCLI | 通用命令行中心，将任何网站/应用变成命令行界面 |
| CLI（GitHub 官方） | 将 PR、Issue 等带到终端 |
| Gemini-CLI | 从终端直接访问 Gemini 模型 |

更多 CLI 可按需查找：Command-line interface（GitHub 主题推荐页）。

### 5.4 子 Agent（Sub-agent）

#### 创建方式

- 自动触发：任务复杂且可并行时，CC 自动派生子 Agent。
- 手动创建：输入 `/agents`，在 Library 界面进行创建。

#### 手动创建步骤

1. 选择创建项目级或全局级子 Agent。
2. 选择「AI 辅助创建」，让 AI 根据意图辅助创建。
3. 描述想要的子 Agent 功能。
4. 决定子 Agent 的工具权限（勾选需要的权限）。
5. 选择模型（一般选 Sonnet）。
6. 为子 Agent 挑选区别于主 Agent 的颜色。
7. 完成后，在 Library 下选择已创建的子 Agent 进行调用或管理。

### 5.5 Hooks（钩子）

Hooks 是自动触发器——设定“当 CC 做了某件事时，自动执行另一件事”。

#### 任务完成提示音

> 设置一个 hook，每次完成任务之后，都自动执行一个声音脚本，发出一个提示音“叮”进行提醒。

#### 代码提交前检查

> 设置一个 hook，每次提交代码之前，都会自动触发代码格式的检查。

### 5.6 插件（Plugin）

- 本质：打包了 Skill、SubAgent、Hook、MCP 的整合性概念。
- 管理方式：输入 `/plugin` 进入插件管理界面：
  - 发现新插件
  - 管理已下载插件

#### 推荐插件

| 插件名称 | 功能 |
|---|---|
| commit-commands | 简化 Git 工作流程（提交、推送、创建 PR） |
| content-creator | 跨平台内容创作（博客、视频脚本、社交媒体） |
| security-guidance | 安全提醒钩子，提示潜在安全问题（命令注入、XSS 等） |

更多插件可在官方/三方插件网站查看：Plugins / Claude Code Plugins（内容由 AI 生成，请谨慎参考）。

## 六、常用命令速查表

| 命令 | 作用 | 使用频率 |
|---|---|---|
| `/init` | 项目初始化，生成 `claude.md` | 每个项目 1 次 |
| `/clear` | 清空当前对话 | 频繁 |
| `/compact` | 压缩上下文，释放窗口 | 上下文到 60% 时 |
| `/cost` | 查看上下文占比 | 频繁 |
| `/context` | 详细展示上下文占用情况 | 需要详细诊断时 |
| `/model` | 切换高中低档模型 | 按需 |
| `/btw` | 临时问无关问题 | 按需 |
| `/simplify` | 代码审核（内置 Skill） | 定期 |
| `/resume` | 恢复历史对话 | 按需 |
| `-c` 启动参数 | 继续上一次对话 | 频繁 |
| `/memory` | 管理记忆（claude.md + Auto Memory） | 偶尔 |
| `/agents` | 创建/调用/管理子 Agent | 按需 |
| `/plugin` | 插件管理 | 偶尔 |
| `/rewind` | 回滚对话或文件 | 出错时 |

### 其他快捷键

| 操作 | 快捷键 |
|---|---|
| 中断当前任务（保留上下文） | 单按 ESC |
| 退出 CC（丢失上下文） | 双按 ESC |
| 多行文本换行 | macOS：Option+回车；Windows：Ctrl+回车 |
| 粘贴图片 | Windows：Alt+V；macOS：Command+V |

## 七、总结

本教程带您走过了四个阶段：

| 阶段 | 核心内容 |
|---|---|
| ① 上手 | Agent IDE 准备 → 三种方式安装 CC → CC Switch 配置大模型 → 三种权限模式 → 基础交互与斜杠命令 |
| ② 掌控 | Git 版本管理（后悔药）→ 上下文监控（`/context` + statusLine）→ `/compact` 压缩 → `/clear` 清空 → `/resume` 恢复 |
| ③ 个性化 | `claude.md`（全局/项目/文件夹三级）→ Auto Memory 自动记忆 → 让 CC 记住你的要求和习惯 |
| ④ 高级拓展 | Skills（技能包安装/创建/触发）→ MCP 扩展 → CLI 工具 → 子 Agent（并行分身）→ Hooks（自动触发器）→ 插件管理 |

### 核心心法

- 从“一问一答”到“构建系统、组织 AI、让它自己去干”。
- 习惯与 AI 的协作方式后，无论未来出现什么新工具，都能上手很快。
- Git 存档 + 上下文管理 + 记忆机制是保证长期稳定使用的三大支柱。
- 📌 课程中涉及的安装包、命令速查表、常用 Skill 和 CLI 工具列表可参考讲义原文。
- 下一步建议：选一个你实际工作中的小项目，跟着教程从 `/init` 开始完整走一遍流程，在实际操作中巩固以上所有知识点。

---

## 原讲义入口

📘 [[Claude Code完全教程【视频文档】.pdf|打开《Claude Code完全教程【视频文档】.pdf》]]
