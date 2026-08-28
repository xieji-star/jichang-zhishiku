---
title: "Claude Code 完全使用指南"
category: "AI与技术工具"
tags:
  - ClaudeCode
  - AI编程
  - 终端工具
source:
  - "[[../总结好的大纲以及笔记/AI/Claude Code从0~1的入门/Claude Code 从 0 到 1 完全使用教程（Obsidian版）.md]]"
  - "[[../总结好的大纲以及笔记/AI/Claude Code 入门与 GitHub 协作开发指南/Claude Code 入门与 GitHub 协作开发——完整使用指南（Obsidian版）.md]]"
created: 2026-07-11
updated: 2026-07-11
---

# Claude Code 完全使用指南

## 概述

Claude Code（简称 CC）是 Anthropic 推出的终端交互式 AI 编程助手。不同于云端沙箱，它能完整理解项目代码库、直接修改文件，并通过 `CLAUDE.md` 项目文件快速上手。本页综合两门课程内容，覆盖从安装到高级拓展的全流程。

## 核心要点

### 四大优势
1. **完整理解项目**：阅读整个代码库，非仅处理片段
2. **CLAUDE.md 设计文件**：项目启动时自动加载，相当于"老员工"入职
3. **深度协作体验**：终端对话式交互，边讨论边开发
4. **擅长复杂任务**：主动多问多确认，完成度高

### 安装方式（Windows）

| 方式 | 命令 | 适用场景 |
|------|------|----------|
| 官方安装 | `irm https://claude.ai/install.ps1 \| iex` | 有梯子、能访问 Claude 官网 |
| winget | `winget install Anthropic.ClaudeCode` | Cloudflare 拦截时的替代方案 |
| 国内镜像 | `irm https://daheiai.com/cc.ps1 \| iex` | 无梯子时的第三方方案 |

前置条件：Windows 需先安装 Git → `winget install Git.Git`

### CC Switch（多模型切换）

由于 Anthropic 对中国 IP 限制严格，推荐使用 CC Switch 配置国内大模型（如 DeepSeek、Minimax）替代 Claude 官方 API。

### 三种权限模式（Shift+Tab 切换）

| 模式 | 功能 |
|------|------|
| **默认模式（Default）** | 每步询问，新手推荐 |
| **Accept Edits** | 文件修改自动批准，shell 命令仍需确认 |
| **计划模式（Plan）** | 只读，不修改文件 |

全自动：`claude --dangerously-skip-permissions`（慎用）

## 核心斜杠命令

| 命令 | 作用 | 频率 |
|------|------|------|
| `/init` | 项目初始化，生成 CLAUDE.md | 每项目 1 次 |
| `/clear` | 清空上下文，重开会话 | 频繁 |
| `/compact` | 压缩上下文 | 上下文达 60% 时 |
| `/cost` | 查看上下文占比 | 频繁 |
| `/context` | 详细上下文占用 | 诊断时 |
| `/model` | 切换模型 | 按需 |
| `/plan` | 开启计划模式 | 方案确认前 |
| `/simplify` | 代码审核（派生 3 个 agent） | 定期 |
| `/resume` | 恢复历史对话 | 按需 |
| `/memory` | 管理记忆与 Auto Memory | 偶尔 |
| `/agents` | 管理子 Agent | 按需 |
| `/plugin` | 插件管理 | 偶尔 |

## 上下文管理

### 监控
- `/cost`：查占比，超过 60% 时 CC 会变笨
- `/context`：详细展示各模块占用
- 可配置 statusLine 在顶部常驻显示进度条

### 管理流程（核心决策日志法）
1. 让 CC 整理决策日志：
   ```
   帮我总结当前对话的决策日志：
   【已确定的技术决策】【已完成的模块】
   【当前正在做的任务】【未解决的问题】【下一步计划】
   ```
2. 人工检查并补充修正
3. `/clear` 清空对话
4. 新对话首条粘贴总结 → CC 继续工作

> 核心思想：由你来记忆关键节点，不依赖 CC 自己的记忆。

## 三级记忆机制

| 级别 | 位置 | 适用范围 |
|------|------|----------|
| 全局级 | `~/.claude/CLAUDE.md` | 所有项目 |
| 项目级 | 项目根目录 `CLAUDE.md` | 当前项目，可提交 Git |
| 文件夹级 | 子文件夹 `CLAUDE.md` | 仅该文件夹生效 |

## 高级拓展

### Skills（技能包）
- 本质：文件夹 + `SKILL.md`
- 查找顺序：项目级 → 全局级
- 触发方式：自动触发 / 斜杠强制（`/技能名称`）/ 提示词指定
- 推荐 Skill：Find-Skill、Frontend-Design、Skill-Creator

### 子 Agent
- `/agents` 进入管理界面
- 可手动创建项目级或全局级子 Agent
- 复杂可并行任务时 CC 自动派生

### Hooks（钩子）
- 自动触发器："当 CC 做了 X 时，自动执行 Y"
- 例如：任务完成提示音、代码提交前自动格式化

### MCP 扩展
- Model Context Protocol：连接 AI 与外部工具/服务的"转接头"

## 关键概念

- **CLAUDE.md**：项目说明书，让 CC 快速理解项目。三级记忆第一优先级
- **Auto Memory**：CC 自动记录的按需注入规则（`.claude/memory/`），第二优先级
- **上下文窗口**：CC 的"记忆容量"，需主动管理
- **ESC 键**：单按 = 中断任务（保留上下文）；双按 = 退出 CC（丢失上下文）

## 关联页面

- [[wiki/AI与技术工具/GitHub协作开发]] — CC 与 GitHub 的协作流程
- [[wiki/AI与技术工具/SKILL技能包]] — Skill 的深入解析与创建方法

## 待深入

- MCP 扩展的具体配置与最佳实践
- 自定义 Hooks 的高级用法
- 多模型切换的性能对比数据
