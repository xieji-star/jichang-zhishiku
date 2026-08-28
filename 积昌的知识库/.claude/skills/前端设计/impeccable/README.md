# impeccable

> **来源仓库：** `pbakaus/impeccable`（GitHub，Apache 2.0 协议）
> **作者：** Paul Bakaus
> **版本：** 4.0.4
> **类型：** 前端设计品味技能（单一技能，独立项目）

本文件夹是 **impeccable** 这一个 skill 的完整项目文件，与前面收拢的技能包不同，它**保持为可自动调用的独立技能**。

## 功能简介

给 AI 编程助手（Claude Code、Cursor、Codex 等）注入**设计品味**，避免生成千篇一律的 "AI 味"（AI slop）界面。内置 23 条设计命令 + 7 个领域参考 + 确定性检测规则。

常用命令（`/impeccable <命令> <目标>`）：

| 命令 | 作用 |
|------|------|
| `craft` | 完整"塑造→构建"流程 |
| `audit` | 无障碍/性能/响应式检查 |
| `critique` | UX 设计评审 |
| `polish` | 最终打磨 |
| `bolder` / `quieter` | 加强 / 弱化设计强度 |
| `distill` | 剥离到本质 |
| `harden` | 错误处理、i18n、边界情况 |
| `animate` / `colorize` / `typeset` / `layout` | 动效 / 配色 / 排版 / 布局 |
| `live` | 浏览器可视化迭代模式 |
| `init` / `document` / `extract` | 初始化 / 文档 / 提取 |

## 目录结构

```
impeccable/
├── SKILL.md                  # 主技能定义（name: impeccable, v4.0.4）
├── README.md                 # 本说明
├── reference/                # 35 个命令参考文件（audit、critique、polish、craft…）
└── scripts/                  # 检测器、live 模式、命令元数据等脚本
```

## 使用方式

- **可直接自动调用**：impeccable 位于 `.claude/skills/` 直接子目录，属于自动可用技能，触发后按 SKILL.md 执行。
- **CLI 方式**：`npx impeccable <命令>`
- **检测命令**：`node .claude/skills/impeccable/scripts/detect.mjs <目标>`（目录 / 文件 / URL）

> 说明：本技能的 `allowed-tools` 依赖固定路径 `.claude/skills/impeccable/scripts/*`，因此目录名保持 `impeccable` 不变。
