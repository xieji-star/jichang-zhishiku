---
title: "AI概念速查"
category: "AI与技术工具"
tags:
  - Claude Code
  - Codex
  - Hook
  - Token
  - 概念
  - 计费
source:
  - "[[总结好的大纲以及笔记/技能/AI/概念/Claude Code 与 Codex 对比.md]]"
  - "[[总结好的大纲以及笔记/技能/AI/概念/Claude Code中Hook的概念.md]]"
  - "[[总结好的大纲以及笔记/技能/AI/概念/Codex的5.6三大旗舰模型差异.md]]"
  - "[[总结好的大纲以及笔记/技能/AI/概念/Token的计费方式以及如何更好的省Token.md]]"
  - "[[总结好的大纲以及笔记/技能/AI/概念/json含义详解.md]]"
created: 2026-08-13
updated: 2026-08-24
---

# AI 概念速查

## 概述

整理 `技能/AI/概念/` 目录下的 5 个核心 AI 概念：**Claude Code 与 Codex 的对比、Hook（钩子）机制、Codex 5.6 三大旗舰模型差异、Token 计费方式与省 Token 技巧、JSON 数据格式**。用于快速理解两款主流 AI 编程工具的异同、事件钩子机制、模型选型、成本控制与通用数据交换格式。

## 核心要点

### Claude Code 与 Codex 对比

| 维度 | Claude Code | Codex |
|------|-------------|-------|
| **规则文件** | `CLAUDE.md` | `AGENTS.md` |
| **配置文件** | `settings.json`（JSON） | `config.toml`（TOML） |
| **Skill 标准** | SKILL.md（同标准） | SKILL.md（同标准，两者通用） |
| **文档回退机制** | 项目文档回退 | `project_doc_fallback_filenames`（兜底读取文档文件名） |

> 两者核心逻辑相近（项目规则 + 配置 + Skill 技能包），只是文件格式与命名不同；Skill 采用同一套 SKILL.md 标准。

### Claude Code 中的 Hook（钩子）

**Hook** 是"在某个事件发生时自动执行命令"的机制，用于让 Claude Code 在特定时机自动做动作（如格式化、日志、权限检查）：

| 事件 | 触发时机 | 示例 |
|------|---------|------|
| `PreToolUse` | 工具调用前 | 拦截危险命令 |
| `PostToolUse` | 工具调用后 | 写文件后自动格式化 |
| `UserPromptSubmit` | 用户提交消息时 | 知识库维护检查（比对到期任务） |
| `Stop` | 会话停止时 | 清理/收尾 |

- 每个 Hook 返回 JSON（可带 `systemMessage` / `hookSpecificOutput.additionalContext` / `decision` 等）
- 知识库实战案例：`.claude/hooks/kb-maintenance-check.sh`（UserPromptSubmit，比对 `.last-wiki-maintain` / `.last-github-backup`，到期提示迭代/上传）

### Codex 5.6 三大旗舰模型差异

Codex 5.6 版本按模型能力划分为三个旗舰档位：

| 模型 | 定位 |
|------|------|
| **Sol** | 最强推理/复杂任务档 |
| **Terra** | 中间档 |
| **Luna** | 轻量/快速档 |

（具体能力边界与适用场景以官方发布说明为准，选型时按任务复杂度与成本权衡。）

### Token 计费方式与省 Token 技巧

**计费三块**：

| 计费项 | 说明 |
|--------|------|
| **输入（Input）** | 发给模型的全部上下文（提示词 + 历史 + 工具结果） |
| **输出（Output）** | 模型生成的回答内容 |
| **命中缓存（Cache）** | 相同前缀上下文命中缓存时大幅降价（最便宜的计费段） |

**省 Token 核心思路**：

1. **减少无效输入**：不清扫全库、不走"全库 find/grep 逐个试读"（知识库检索法即为此设计）
2. **复用缓存**：保持上下文前缀稳定，让重复前缀命中缓存
3. **精简输出**：让模型按需输出（如限制长度、结构化返回）
4. **只读该读的**：查文档走"索引→定位→读取"窄路径，避免 Token 消耗在搜索上

### JSON 概念

**JSON**（JavaScript Object Notation，JavaScript 对象表示法）是互联网上使用最广泛的数据交换格式——轻量、与语言无关、人类可读机器可解析。来源：[[总结好的大纲以及笔记/技能/AI/概念/json含义详解.md]]

| 要点 | 说明 |
|------|------|
| **两种核心结构** | 对象 `{}`（键值对）+ 数组 `[]`（有序列表） |
| **六种数据类型** | 字符串、数字、布尔、空值、对象、数组 |
| **语法硬规则** | 双引号、无注释、无尾逗号 |
| **前后端配对** | `JSON.stringify`（对象→字符串）与 `JSON.parse`（字符串→对象） |
| **典型应用** | Web API 前后端通信、配置文件（`settings.json`/`package.json`）、数据库存储、日志输出、**AI 接口请求/响应体** |
| **与 AI 工具的关系** | Claude Code 的 Hook 返回 JSON、飞书助手 NDJSON 事件流、`hooks.json`/`settings.json` 配置——几乎处处是 JSON |

## 关键概念/术语

- **CLAUDE.md / AGENTS.md**：Claude Code / Codex 的项目规则文件
- **Hook**：事件触发的自动命令机制（PreToolUse / PostToolUse / UserPromptSubmit / Stop 等）
- **Sol / Terra / Luna**：Codex 5.6 三档旗舰模型
- **Token 三块计费**：输入 / 输出 / 命中缓存（缓存最便宜）
- **JSON**：轻量与语言无关的文本数据交换格式（对象 `{}` + 数组 `[]`）

## 关联页面

- [[wiki/AI与技术工具/Claude Code]] — Claude Code 完整指南
- [[wiki/AI与技术工具/Codex模型配置]] — Codex 安装与模型/供应商配置
- [[wiki/AI与技术工具/SKILL技能包]] — Agent Skill 定义与创建

## 待深入

- Codex 5.6 各模型的具体能力参数与官方对比
- 更细的 Token 缓存机制（前缀缓存触发条件）
