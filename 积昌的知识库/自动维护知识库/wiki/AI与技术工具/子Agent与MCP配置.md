---
title: "子Agent与MCP配置"
category: "AI与技术工具"
tags:
  - Claude Code
  - 子Agent
  - MCP
  - AI秘书团
  - 工具配置
  - 自动化
  - CLI工具
  - 插件
  - Cookbook
source:
  - "[[../总结好的大纲以及笔记/AI/Claude Code打造AI秘书团/Claude Code打造AI秘书团.md]]"
  - "[[../lark-resources/备忘录文档_202607140043.pdf]]"
created: 2026-07-11
updated: 2026-07-11
---

# 子 Agent 与 MCP 配置

## 概述

Claude Code（简称 CC）不只是编程工具，更是可以组建 **AI 秘书团**的"贴身秘书"。其核心能力在于：① **子 Agent（Sub-agent）**——创建不同特长的 AI 助手；② **MCP 工具**——挂载第三方服务扩展能力。本页详解如何从零搭建个人 AI 秘书团。

## 核心要点

### Claude Code 的定位

| 类型 | 类比 | 特点 |
|------|------|------|
| **网页聊天 AI** | 小区问询处机器人 | 没有手没有脚，不认识你，只能回答问题 |
| **打包 AI 产品** | 前台小姐姐机器人 | 不认识你，但能做有限操作 |
| **Claude Code** | **贴身秘书机器人** | ① 了解你的全部资料和偏好 ② 工具箱无限（自带 + MCP 外挂）③ 能带团队（创建子 Agent） |

### 安装与基础配置

#### 安装方式

```powershell
# 方式一：命令行安装（Windows PowerShell）
irm https://claude.ai/install.ps1 | iex

# 方式二：winget 安装
winget install Anthropic.ClaudeCode

# 方式三：通过 Cursor Agent 自动安装
# 在 Cursor 中直接说"帮我安装 Claude Code"
```

#### 配置（国内用户）

需要替换为国产大模型 API（如智谱 AI、DeepSeek、Minimax），使用 **CC Switch** 工具配置多模型切换。

```bash
# 启动 Claude Code
claude

# 跳过权限确认（效率模式）
claude --dangerously-skip-permissions
```

### 核心命令

| 命令 | 作用 |
|------|------|
| `/help` | 显示所有指令 |
| `/init` | 初始化项目，生成 CLAUDE.md |
| `/compact` | 压缩聊天上下文（占用 >60% 时使用） |
| `/clear` | 清空上下文，重开会话 |
| `/cost` | 查看上下文占比 |
| `/plan` | 开启计划模式 |
| `/simplify` | 派生 3 个 agent 进行代码审核 |
| `/agents` | 管理子 Agent |
| `/memory` | 管理记忆系统 |
| `/btw` | 临时问与项目无关的问题（与上下文隔离） |

### 秘书团架构设计

#### 典型成员

| 秘书 | 角色 | 职责 | 需要 MCP |
|------|------|------|----------|
| **新闻球** | 信息助理 | 每天搜刮 AI 新闻，总结推送 | Firecrawl / RSS |
| **穿搭球** | 形象顾问 | 查天气→穿搭建议→生成参考图 | 天气 MCP + 即梦 MCP |
| **教练球** | 健康管理 | 记录健康数据，推荐运动和饮食 |（无需特殊 MCP） |
| **日报球** | 日程规划 | 规划日程早报，发工作群 | 飞书 MCP |
| **反思球** | 成长导师 | 收工复盘，引导深度思考 |（无需特殊 MCP） |

#### 创建流程

1. **创建构想文档**：在项目中写下每个秘书的职责设定
2. **让 CC 完善设计**：选中文档，让 CC 自动生成详细设定、MCP 清单、文件夹结构
3. **填写个人信息模板**：年龄、偏好、健康目标等
4. **配置 MCP 工具**：在 Smithery 搜索安装所需 MCP
5. **创建子 Agent**：使用 `/agents` 命令创建各秘书

### MCP 工具配置

#### 工具市场：Smithery

[Smithery.ai](https://smithery.ai) 是 MCP 工具市场，可搜索和安装各种第三方工具。

#### 配置示例

```bash
# 配置即梦 MCP（AI 图片生成）
npx @smithery/cli install @jimeng/mcp --key "your_session_id"

# 配置飞书 MCP
claude mcp add feishu --type command --command "npx" \
  --args "@feishu/mcp-server" \
  --env "APP_ID=xxx" --env "APP_SECRET=xxx"

# 查看已配置的 MCP
claude mcp list
```

#### 即梦 MCP 配置要点

1. 在 Smithery 搜索 "Jimeng" 或 "即梦"
2. 登录即梦官网 → 右键检查 → Application → Cookies → 获取 Session ID
3. 将 Session ID 填入配置命令

### 子 Agent 的存储与维护

```
项目目录/.claude/agents/
├── news_agent/          # 新闻球
├── outfit_agent/        # 穿搭球
├── coach_agent/         # 教练球
├── daily_agent/         # 日报球
└── reflect_agent/       # 反思球
```

每个子 Agent 包含：
- **提示词（Prompt）**：定义了何时调用及其职责
- **工具权限**：可调用哪些工具
- **模型选择**：使用的模型
- **颜色标识**：方便对话中区分

创建完成后可手动编辑 `.claude/agents/` 下的文件修改提示词。

### 初始化秘书团规章制度

所有子 Agent 创建完成后，执行 `/init` 生成 **CLAUDE.md**——相当于秘书团的"规章制度"，包含项目结构、成员介绍、工作原则。

CLAUDE.md 可手动修改，使其更符合个人需求。

### 日常工作流示例

#### 早晨：新闻简报
"早上好" → CC 召唤新闻球 → 搜索 AI 新闻 → 总结写入文档 → 推送飞书

#### 上午：穿搭建议
新闻球完成后 → 穿搭球上场 → 询问场合 → 查天气 → 给出穿搭建议 → 生成参考图

#### 白天：日程规划
日报球上场 → 询问工作安排 → 理清待办 → 生成日程早报 → 发工作群

#### 晚上：反思复盘
反思球上场 → 回顾当天 → 引导深度思考和复盘

### 进阶技巧

#### 上下文管理

- `/cost` 监控上下文占比，>60% 需压缩
- `/compact` 压缩聊天记录（相当于生成"工作总结"交给下一个秘书）
- 可配置常驻状态栏显示上下文进度条

#### Memory 记忆系统

```
项目目录/.claude/memory/memory.md
```

- **启用 Auto Memory**：`/memory` → 选择 Auto-memory
- CC 会记住偏好和习惯
- 换电脑后只要有记忆文件，CC 还是熟悉你的 CC

#### CLAUDE.md 的作用

相当于整个项目的"规章制度"：
- 定义项目目标和结构
- 规定秘书团成员职责
- 设定工作原则和语言偏好
- 秘书团所有行动都必须遵循

#### CLI 工具——Agent 连接的轻量化方案

CLI（Command Line Interface）是让 AI Agent 调用外部工具的另一种方式，比 MCP 更轻量。

| 类型 | 特点 | 适用场景 |
|:----:|------|----------|
| **MCP** | 转接头式连接，占用托管资源较大 | 复杂工具连接 |
| **CLI 工具** | 轻量命令式，AI 直接调用，精准高效 | 日常自动化操作 |
| **Function Call** | API 原生接口 | 开发者自定义 |

**代表工具**：**Open CLI**（`open-cli`）——将常用网页和社交媒体操作封装为 CLI 命令，Agent 可直接调用。

```bash
# 安装 Open CLI
你可以让 CC 帮你直接安装好
# 使用示例：查社交媒体上某地的推荐
opencil search "深圳必吃餐厅" --platform=xiaohongshu
```

> CLI 工具的输出比人类操作浏览器截图更精准高效，是目前很多厂商将操作接口转为 CLI 方向的原因。

**常用 CLI 工具列表**：
- 网页搜索与内容抓取
- 社交媒体操作
- 文件处理与格式转换
- 项目管理与部署
- API 测试与调用

#### Cookbook——条件反射式自动触发

Cookbook 是为 Agent 设定的 **自动触发器（Auto-trigger）**——当满足某个条件时自动执行某个动作。

**示例**：
1. **任务完成提示音**：每次 CC 完成任务后发出 "叮" 的提示音
2. **代码提交前检查**：每次提交代码前自动触发代码格式检查
3. **日常提醒**：每天早上自动推送日报

配置方式：直接跟 CC 说需求→ CC 会给出配置方案→ 配合完成即可。

#### 插件系统（Plugins）

插件将 Skills、MCP、CLI 打包在一起，是完整的扩展包。

| 管理方式 | 命令 |
|---------|------|
| **进入插件管理** | `/plugin` 或 `/pluck in` |
| **发现新插件** | 在插件管理页面浏览 "发现" 标签 |
| **安装插件** | 选择插件 → 选择安装范围 → 确认 |
| **管理已安装** | 在插件页面查看和管理 |

> 插件是 CC 生态的"应用商店"，安装后自动获得该插件的所有能力。

## 关键概念

- **子 Agent（Sub-agent）**：CC 内部的专用 AI 助手，有独立的提示词、工具权限和模型配置
- **MCP（Model Context Protocol）**：AI 模型与外部工具之间的标准接口协议
- **CLAUDE.md**：项目根目录的配置文件，定义 AI 助手的规则和行为
- **上下文压缩（/compact）**：生成工作总结和交接文档，清出空间给新任务
- **Auto Memory**：自动记录用户偏好和习惯的持久化记忆系统
- **CLI 工具（Command Line Interface）**：AI Agent 可直接调用的轻量命令工具，比 MCP 更高效
- **Cookbook**：Agent 的条件反射式自动触发器
- **插件（Plugin）**：将 Skills、MCP、CLI 打包的完整扩展包

## 关联页面

- [[wiki/AI与技术工具/Claude Code]] — Claude Code 完全使用指南
- [[wiki/AI与技术工具/GitHub协作开发]] — GitHub 协作开发流程
- [[wiki/AI与技术工具/SKILL技能包]] — SKILL 技能包定义与使用
- [[wiki/AI与技术工具/Codex模型配置]] — Codex 模型配置与 API 设置

## 待深入

- 各 MCP 工具的详细配置教程
- 子 Agent 提示词编写的最佳实践
- 多模型切换策略（何时用 Claude vs 国产模型）
- Cookbook 自动触发器的更多实用场景
- CLI 工具的自定义开发方法
