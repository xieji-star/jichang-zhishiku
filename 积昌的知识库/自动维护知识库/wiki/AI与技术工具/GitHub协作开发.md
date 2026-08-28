---
title: "GitHub 协作开发"
category: "AI与技术工具"
tags:
  - GitHub
  - Git
  - 版本管理
  - 协作开发
source:
  - "[[../总结好的大纲以及笔记/AI/Claude Code 入门与 GitHub 协作开发指南/Claude Code 入门与 GitHub 协作开发——完整使用指南（Obsidian版）.md]]"
  - "[[../总结好的大纲以及笔记/知识库FAQ/12-GitHub推送被Secret-Scanning拦截（快照含API密钥）.md]]"
created: 2026-07-11
updated: 2026-08-24
---

# GitHub 协作开发

## 概述

GitHub 是代码托管与协作平台。本文涵盖从本地项目推送到 GitHub、日常更新工作流、高效逛 GitHub 寻找优质开源项目、以及 Issues 精读技巧。Git 版本管理也是 Claude Code 的"后悔药"——每完成一步就存档，改崩了随时回滚。

## 核心要点

### GitHub 三大作用
1. **跳板工具**：托管代码 → 一键部署到 Vercel/Netlify/Render
2. **存档备份**：每次提交都是版本快照，随时回滚
3. **开源协作**：浏览他人项目，学习或复用代码

### 首次推送流程

```bash
git init                          # 初始化本地仓库
git add .                         # 所有文件加入暂存区
git commit -m "first commit"      # 提交
git remote add origin <仓库地址>   # 关联远程
git push -u origin main           # 首次推送
```

### 日常更新流程

```bash
git add .
git commit -m "改了什么功能或修复了什么"
git push
```

> 技巧：让 AI 帮你写 commit 备注。

### 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| 网络连接不上 | 终端不走代理 | 开 TUN 模式或手动设置代理 |
| `[rejected]` | 远端版本高于本地 | `git pull origin main` → `git push` |

代理设置：
```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### 🚨 推送被 Secret Scanning 拦截（GH013）

> 2026-08-23 知识库例行上传 GitHub 时 `git push origin main` 被远端整体拒绝的真实报错。完整档案：[[../总结好的大纲以及笔记/知识库FAQ/12-GitHub推送被Secret-Scanning拦截（快照含API密钥）.md]]

**现象**：仓库启用了 **Secret Scanning 推送保护**，`git push` 返回 `GH013: Repository rule violations`，推送被整体拒绝（快照里混入了真实 API 密钥）。

**核心教训**：**知识库/代码备份本质是"把私有内容推到远端"，推送保护是最后一道防线——密钥消毒必须在打包阶段完成**（打快照前先排查配置文档、会话缓存等是否有明文密钥）。

**修复四步**：① 密钥打码 → ② 移除会话缓存等含密钥目录 → ③ git plumbing 重建树修正"双层嵌套"结构 → ④ 重挂父提交跳过含密钥的被拒提交。

## 高效逛 GitHub（四步法）

```
描述项目需求 → AI 推荐项目 + Awesome 系列
     ↓
快速筛选：Stars + 最近 commit 时间（排除死项目）
     ↓
AI 分析项目健康度（用链接）
     ↓
人工精读 Issue（只看 Closed 和 Bug 类）
```

### AI 健康度审计提示词

```
请作为高级架构师，对这个 GitHub 项目 [链接] 进行"健康度审计"：
1. 更新频率：过去 6 个月内是否有实质性代码提交？
2. 版本历史：最近一次 Release 是什么时候？兼容当前主流版本吗？
3. 社区响应：最近 10 个 Issue 平均回复周期？是否有大量积压 Bug？
4. 维护风险：单人维护还是组织维护？
最终结论：活跃期 / 维护期 / 已经脑死亡
```

### Issues 精读指南

**状态（State）**：
- **Open**：问题未解决
- **Closed**：已关闭（可能已解决，也可能维护者决定不修）

**标签（Label）**：
- `bug`：明确错误，需重点关注
- `wontfix`：维护者承认但不打算修——高价值排雷信息
- `duplicate`：重复反馈，跳转至主 Issue
- `help wanted` / `good first issue`：适合外部贡献者

**人工精读重点**：
- Closed 中带绿色对勾的 → 了解已有功能
- Closed 中带斜杠圆圈的 → 了解被放弃的修复
- 带 `bug` 标签的所有 Issue → 评估已知缺陷

## 关键概念

- **Star**：相当于点赞，可作为质量参考（但也可能有水分）
- **Commit**：代码提交快照，是项目的"存档点"
- **Issue**：项目的"评论区"，反映真实问题与维护态度
- **活跃度**：最近 commit 时间——超过半年未更新 ≈ 死项目

## 关联页面

- [[wiki/AI与技术工具/Claude Code]] — Claude Code 与 GitHub 的配合使用
- [[wiki/智灌云联项目/项目总览]] — 实际项目的 Git 工作流应用

## 待深入

- GitHub Actions CI/CD 自动化
- Pull Request 的 Code Review 最佳实践
- 开源贡献的完整流程
