---
title: "SKILL 技能包"
category: "AI与技术工具"
tags:
  - Skill
  - Agent
  - 按需加载
  - ClaudeCode
source:
  - "[[../总结好的大纲以及笔记/AI/SKILL的定义以及使用/SKILL的定义以及使用.md]]"
created: 2026-07-11
updated: 2026-07-11
---

# SKILL 技能包

## 概述

Skill 是 Agent（如 Claude Code）的专业技能包。本质是一个文件夹 + `SKILL.md` 文件，包含元信息（名称 + 触发条件）和正文（专业说明书）。Skill 采用三层按需加载机制，让 AI 在拥有大量技能的同时保持精准和高效。

## 核心要点

### Skill ≠ 只是提示词

虽然交互本质离不开提示词，但 Skill 在工程上远不止拷贝粘贴提示词——它包含**结构化文件夹、按需加载机制、脚本执行和资源引用**。

### 类比：厨师技能

| 厨师技能要素 | 对应 AI Skill 要素 |
|-------------|-------------------|
| **流程**（先炒什么、后放什么） | **Instructions**（指令） |
| **配方**（油温、盐量） | **Rules/参数** |
| **工具**（煤气灶、锅铲） | **Scripts**（脚本） |
| **材料**（食材） | **References/Assets**（参考资料/资源） |

### 最简单的 Skill

```
my-skill/
└── SKILL.md    ← 元信息 + 指令（唯一必需文件）
```

**SKILL.md 结构**：
- `---` 之间：**Metadata**（name + description）——告诉系统这是什么 Skill、什么时候触发
- `---` 下面：**Instructions**——具体告诉 AI 怎么做

### 完整形态的 Skill

```
my-skill/
├── SKILL.md       ← 必需：元信息 + 指令
├── references/    ← 可选：按需加载的参考资料
├── scripts/       ← 可选：可执行脚本（AI 只执行不读取，不占 Token）
└── assets/        ← 可选：资源文件（图片等）
```

## 按需加载的三层结构

| 层级 | 名称 | 加载时机 | 说明 |
|------|------|----------|------|
| **第 1 层** | **Metadata（元信息）** | **始终加载** | 每次对话 AI 都看到所有 Skill 的 name + description |
| **第 2 层** | **Instructions（指令）** | **触发时加载** | AI 判断需要用该 Skill 时，加载完整 SKILL.md |
| **第 3 层** | **Resources（资源）** | **按需加载** | references 在需要时查阅；scripts 只执行不读取 |

### 优势
- **同时拥有多个 Skill**：AI 每次只看元信息目录
- **回答更精准**：需要时才加载完整指令，无干扰
- **节省 Token**：加载内容少，消耗自然省

## 安装与管理

| 类型 | 路径 |
|------|------|
| 全局 Skill | `~/.claude/skills/` |
| 项目级 Skill | `项目目录/.claude/skills/` |

查找顺序：项目级 → 全局级（项目级可覆盖同名全局 Skill）

### 触发方式
1. **自动触发**：CC 根据元信息判断
2. **斜杠强制触发**：`/技能名称`，100% 可靠（推荐）
3. **提示词明确指定**

## 创建 Skill

### 手动方式
1. 在 `.claude/skills/` 下创建文件夹
2. 编写 `SKILL.md`（必须大写 S）
3. 用 CC 测试：询问"你有哪些 Skill？"

### Skill Creator（推荐小白）
- 交互式、选择题引导
- 拖入参考图和 API 文档即可自动处理
- 生成后自动拟测试案例跑测试

## 实用 Skill 推荐

| Skill 类型 | 用途 |
|-----------|------|
| PPT 制作 | 一句话生成演示文稿 |
| 文档处理 | 处理 Word 文档 |
| Excel 处理 | 表格整理 |
| PDF 处理 | PDF 操作 |
| 前端设计 | 生成前端网页 |

## 关键概念

- **渐进式披露（Progressive Disclosure）**：Skill 最核心的设计——三层按需加载
- **Scripts 只执行不读取**：不占 Token，但依赖 SKILL.md 指引足够清晰
- **References 按需查阅**：只在特定场景加载特定参考文件
- **Skill Creator**：用 AI 辅助创建 Skill 的工具

## 关联页面

- [[wiki/AI与技术工具/Claude Code]] — Skill 的运行环境与触发机制

## 待深入

- 自定义 Skill 的最佳实践模式
- 多 Skill 协同工作的架构设计
- Skill 市场的生态分析
