---
title: Claude Code中Hook的概念
type: 概念笔记
date: 2026-08-13
tags:
  - AI工具
  - Claude Code
  - Hook
  - 自动化
  - 概念
source: Anthropic 官方文档、社区资料、知识库既有规则
---

# Claude Code中Hook的概念

> [!summary] 概要
> 本文用通俗语言解释 Claude Code 里的 **Hook（钩子）** 是什么：它是一种"事件自动触发外部脚本"的机制——当 Claude Code 运行到某些关键时刻（你发消息、Claude 要调工具、Claude 回答完），会自动执行你预先写好的脚本，实现安全检查、自动格式化、自动维护提醒、流程自动化等效果。Hook 配置在 `settings.json` 的 `hooks` 字段里，按事件类型（如 PreToolUse、PostToolUse、UserPromptSubmit）分组。本知识库的「自动维护触发」就是一个真实在用的 Hook 案例。

## 相关笔记

- [[Claude Code 与 Codex 对比]] — 同目录概念笔记，含 Claude Code 与 Codex 的 Hook 配置对比
- [[Claude Code 从 0 到 1 完全使用教程（Obsidian版）]] — Claude Code 安装与基础配置完整教程
- [[Claude Code打造AI秘书团]] — Claude Code 应用场景与玩法
- [[SKILL的定义以及使用]] — 与 Hook 同为 Claude Code 扩展机制的 Skill 概念
- [[skill调用指南]] — Skill 的调用方式（与 Hook 自动触发互补）

## 索引

- 🔗 [[#1. Hook 到底是什么——一句话加一个比喻]] — 用生活化比喻讲清 Hook 的本质
- 🎯 [[#2. Hook 能帮你做什么（典型用途）]] — 安全检查、自动格式化、自动维护等场景
- ⚙️ [[#3. Hook 配置在哪里（settings.json）]] — Hook 的存放位置与写法
- 🕐 [[#4. Hook 的种类——按触发时机分类]] — PreToolUse、PostToolUse 等事件详解
- 📨 [[#5. Hook 的返回值——脚本如何"说话"给 Claude 听]] — 退出码与 JSON 返回格式
- 🏠 [[#6. 真实案例：本知识库的自动维护 Hook]] — kb-maintenance-check.sh 是怎么工作的
- 🧩 [[#7. Hook 与其他概念的区别]] — Hook / Skill / Subagent / MCP / Permission 一表分清
- 💡 [[#8. 使用注意事项与最佳实践]] — 写 Hook 时要避开的坑
- ⚡ [[#9. 一分钟速记]] — 一句话带走核心

## 1. Hook 到底是什么——一句话加一个比喻

🔥 **<span style="color:#e74c3c">一句话定义：Hook（钩子）是 Claude Code 的"自动触发器"——当某个预定的关键时刻发生时，Claude Code 会自动运行你写好的外部脚本，不需要你手动操作。</span>**

打个比方：

> 想象你门口装了一个**感应门铃**。每次有人推门进来（事件发生），感应器就自动播放你设好的音乐（执行脚本），完全不用你伸手去按。Hook 就是这个"感应门铃"——你在 `settings.json` 里"装"好它，Claude Code 每次走到对应节点，就自动帮你干活。

- 💡 **<span style="color:#2980b9">Hook 英文原意是"钩子"，在编程里指"挂在某个执行节点上的小程序"。Claude Code 把这种通用编程思想引入到了 AI 对话流程中</span>**
- 📌 **<span style="color:#e67e22">Hook 本身不参与"思考"——它只是"听到特定声音就自动反应"的机械动作，真正负责思考的是 Claude</span>**
- ⚠️ **<span style="color:#e74c3c">关键点：Hook 是"自动的、无人值守的"。一旦配好，只要对应事件发生，它就一定运行，不需要你每次提醒</span>**

## 2. Hook 能帮你做什么（典型用途）

Hook 特别适合做那些"每次都要重复盯一遍"的杂活。常见用途：

- 🛡️ **安全检查与拦截**：Claude 要执行危险命令（如删除文件、推送代码）之前，先跑一个脚本检查，发现不对劲就**阻止**或**二次询问**
  - 例如：PreToolUse 检查到 `git push --force` 就返回 `block`，强制停下来
- 🎨 **自动格式与质量保障**：Claude 每次改完代码，自动跑一遍 lint（代码静态检查，揪出格式和潜在 bug 的工具），不合格就提醒
- 🔔 **自动维护与提醒**：像本知识库的自动维护 Hook，每天第一条消息到达时自动检查"该不该做知识库迭代/备份了"，到期就弹出提醒（见 [[#6. 真实案例：本知识库的自动维护 Hook]]）
- 🔁 **流程自动化**：Claude 回答完毕（Stop 事件）后自动把会话记录归档、同步到别处
- 📋 **给 Claude 补充"背景知识"**：在 Hook 返回里塞入额外上下文（additionalContext），让 Claude 每次开工前自动知道某些固定信息
- 🚦 **权限二次把关**：结合权限体系，对特定工具/命令做更细粒度的"先检查、再放行"

>highlight 【一句话理解】凡是你觉得"每次都得人工确认/重复做"的动作，都值得考虑用 Hook 自动化掉——前提是这件事能被一条外部命令描述清楚。

## 3. Hook 配置在哪里（settings.json）

Hook 不是单独一个文件，而是**写进 Claude Code 的配置文件 `settings.json`** 里。

### 3.1 配置文件的位置

| 层级 | 路径 | 作用范围 |
|------|------|---------|
| 用户级（全局） | `~/.claude/settings.json` | 所有项目生效 |
| 项目级 | `<项目根>/.claude/settings.json` | 当前项目生效 |
| 项目本地 | `<项目根>/.claude/settings.local.json` | 个人本地覆盖（不进版本库） |

- 📌 **<span style="color:#e67e22">项目级配置会叠加在用户级之上，`settings.local.json` 又叠加在 `settings.json` 之上——后者的优先级更高</span>**

### 3.2 配置写法（结构）

Hook 用 `hooks` 字段组织，**外层按事件名分组，内层按工具匹配**：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python /path/to/check.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/kb-maintenance-check.sh"
          }
        ]
      }
    ]
  }
}
```

- **matcher**：匹配哪个工具/事件对象（如只对 `Bash` 命令生效，可留空表示全部）
- **hooks**：要执行的命令列表，可配多条，按顺序执行
- **type**：目前固定为 `command`，即执行一条命令行命令

>highlight 【重要】配了 Hook 之后，需要**重启 Claude Code** 才会生效。改配置不用重启电脑，重启会话即可。

## 4. Hook 的种类——按触发时机分类

Hook 的类型由**事件名**决定，每个事件名代表 Claude Code 生命周期中的一个"关键时刻"：

- 🕐 **<span style="color:#2980b9">UserPromptSubmit——用户提交消息时</span>**：你每次发出一条消息、还没交给 Claude 处理前触发。适合做"开工前自动提醒/注入上下文"
  - 本知识库的自动维护 Hook 就挂在这个事件上
- 🛠️ **<span style="color:#2980b9">PreToolUse——工具被调用前</span>**：Claude 准备使用某个工具（Bash、Edit、Read 等）时触发。**可以拦截**——返回 `block` 就禁止这次调用，是"安全检查"的主力事件
- ✅ **<span style="color:#2980b9">PostToolUse——工具调用完成后</span>**：工具执行完、结果返回给 Claude 之前触发。适合做"事后检查、日志记录、自动整理"
- 🔔 **<span style="color:#2980b9">Notification——需要用户注意时</span>**：Claude 要弹出通知/请求注意时触发
- ✋ **<span style="color:#2980b9">Stop——Claude 停止生成时</span>**：Claude 回答完一段内容、把控制权交回给你时触发。适合做"收尾归档、清理临时文件"
- 🤖 **<span style="color:#2980b9">SubagentStop——子代理结束时</span>**：某个子代理（Subagent，由主代理派出去单独干活的 AI 助手）完成任务时触发
- 🗜️ **<span style="color:#2980b9">PreCompact——上下文压缩前</span>**：Claude 快要超长、准备压缩上下文时触发
- 🌅 **<span style="color:#2980b9">SessionStart / SessionEnd——会话开始 / 结束时</span>**：整个对话会话的开场与收尾（较新版本支持）

| 事件 | 触发时机 | 典型用途 |
|------|---------|---------|
| UserPromptSubmit | 你提交消息时 | 开工提醒、注入背景 |
| PreToolUse | 工具调用前 | ⛔ 安全检查、拦截危险操作 |
| PostToolUse | 工具调用后 | 事后校验、记录日志 |
| Notification | 需要你注意时 | 通知转发、提醒 |
| Stop | Claude 回答完 | 归档、清理 |
| SubagentStop | 子代理结束 | 收集子代理结果 |
| SessionStart/End | 会话开始/结束 | 初始化、收尾 |

>highlight 【挑选原则】不确定用哪个事件时，先想"这件事应该发生在『动作前』还是『动作后』"——动作前用 Pre 系列，动作后用 Post 系列。

## 5. Hook 的返回值——脚本如何"说话"给 Claude 听

Hook 脚本运行完，可以**通过返回值影响 Claude 的行为**。这是 Hook 强大之处。

### 5.1 退出码（exit code）——脚本的"基础语言"

| 退出码 | 含义 | 效果 |
|:------:|------|------|
| 0 | 正常 | 脚本 stdout 正常传递，Claude 照常工作 |
| 2 | 有信息要展示 | 脚本输出作为 stderr 显示给你看 |
| 其他非零 | 出错了 | 通常不阻断 Claude 主流程（除非是 PreToolUse 的 block） |

### 5.2 返回 JSON——脚本的"高级语言"

脚本往 stdout 打印一段 JSON，Claude Code 会解析它并执行相应动作：

```json
{
  "systemMessage": "显示给用户看的一句话",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "注入给 Claude 的额外背景信息"
  },
  "decision": "block"
}
```

- **decision**：仅 PreToolUse 可用，三选一——`block`（禁止这次工具调用）、`allow`（放行）、`ask`（弹窗问用户）
- **additionalContext**：把脚本挖到的信息**注入 Claude 的上下文**，让 Claude 不用重新查就知道
- **systemMessage**：在界面上显示一条提示，不打断流程
- **suppressOutput**：`true` 时隐藏脚本的 stdout，避免刷屏

>highlight 【真实示例】本知识库的维护脚本到期时，就是通过返回 JSON 里的 `systemMessage` 和 `additionalContext`，把"该做知识库迭代了"这件事自动告诉 Claude（见 [[#6. 真实案例：本知识库的自动维护 Hook]]）。

## 6. 真实案例：本知识库的自动维护 Hook

这是知识库正在实际运行的一个 Hook，非常典型的"自动提醒"用法：

- 📄 **脚本文件**：[kb-maintenance-check.sh](../../../../.claude/hooks/kb-maintenance-check.sh)（位于知识库 `.claude/hooks/` 目录）
- 🔗 **挂载事件**：UserPromptSubmit——每天你发出**最新一条**消息时自动触发
- 🎯 **要解决的事**：让"定期维护"不再靠人记，而是机器自动提醒

### 6.1 它做了什么

1. 读取当前时间（精确到分钟）和星期几
2. 读取两个"上次记录"标记文件：`.last-wiki-maintain`（上次知识库迭代）、`.last-github-backup`（上次上传 GitHub）
3. 计算间隔天数，判断是否到期：
   - 距上次 LLM Wiki 迭代 ≥ 3 天 → 提醒执行一轮知识库整理
   - 距上次 GitHub 上传 ≥ 7 天，或今天是周一 → 提醒执行一次备份上传
4. 无到期任务，或当天已提醒过 → 静默退出（不打扰）
5. 有到期任务 → 返回 JSON，把任务说明注入 Claude 的上下文

### 6.2 它依托的规则

这套自动维护机制在 `.claude/CLAUDE.md`（知识库规则文件）里写得很清楚：

- **定期上传 GitHub 规则**：每周一 / 距上次 ≥ 7 天自动触发，新建日期文件夹 `积昌的知识库<MMDD>`，git add + commit + push
- **LLM Wiki 迭代规则**：每 3 天一轮，按 ingest / query / lint 工作流整理全库

- 💡 **<span style="color:#2980b9">这个案例说明：Hook 的价值在于"把规则的执行时机自动化"——规则文本负责讲"该怎么做"，Hook 负责在"该做的时候"喊一嗓子</span>**
- 📌 **<span style="color:#e67e22">整个脚本只做"判断 + 提醒"，真正的整理/上传动作仍由 Claude 完成——Hook 不越俎代庖</span>**

## 7. Hook 与其他概念的区别

Claude Code 有多个容易混淆的扩展机制，用一张表分清楚：

| 概念 | 一句话解释 | 关键词 | 何时用 |
|------|-----------|--------|--------|
| **Hook** | 事件自动触发的外部脚本 | 自动、触发、无人值守 | 需要"某件事发生时自动做点什么" |
| **Skill（技能）** | 按需加载的操作说明书（SKILL.md） | 按需、教学、触发词 | 需要"教会 Claude 做一类特定任务"（见 [[SKILL的定义以及使用]] 和 [[skill调用指南]]） |
| **Subagent（子代理）** | 主代理派出去单独干活的助手 | 分工、并行、独立 | 需要"多任务并行、专人专事" |
| **MCP（模型上下文协议）** | 把外部工具/数据接入 AI 的统一接口 | 接入、外部、数据 | 需要"让 Claude 用外部 API 或数据源" |
| **Permission（权限）** | 允许/拒绝某类操作的规则 | 控制、审批、白名单 | 需要"限制 Claude 能不能做某事" |

- 🔥 **<span style="color:#e74c3c">最容易混的是 Hook 和 Skill：Hook 是"时机触发"（到点就自动跑），Skill 是"按需触发"（Claude 觉得需要才加载）。Hook 是"闹钟"，Skill 是"工具书"</span>**
- 💡 **<span style="color:#2980b9">它们还能配合使用：Hook 到点自动运行，运行结果里也可以提示 Claude 去调用某个 Skill 完成后续工作</span>**
- ⚠️ **<span style="color:#e74c3c">Claude Code 与 Codex 都有 Hook 机制，但配置位置不同：Claude Code 写在 `settings.json`，Codex 写在 `hooks.json`（详见 [[Claude Code 与 Codex 对比]] 的"其他组件对比"章节）</span>**

## 8. 使用注意事项与最佳实践

- 🛡️ **<span style="color:#e74c3c">Hook 拥有完整的系统权限——它在你机器上跑任意命令。只安装你自己写的、或来源可信的 Hook 脚本</span>**
- 🧯 **脚本必须健壮**：Hook 脚本要能"扛住异常"——出错时静默退出（exit 0），不要把错误刷满屏，更不要因为脚本 bug 卡住主流程
- 🪞 **输出要克制**：默认只把需要的信息通过返回值告诉 Claude/用户；能用 `suppressOutput: true` 就隐藏无关输出，避免每次对话都刷屏
- 🧪 **先在小范围测试**：新 Hook 先挂在 PostToolUse 等"只读、无副作用"的事件上试跑，确认稳定后再上 PreToolUse 这类能拦截/阻止的"关键节点"
- 📐 **JSON 格式必须正确**：返回的 JSON 一旦格式错误，Claude Code 可能忽略整条返回——写完后用工具校验一遍
- 📍 **事件选准**：拦截类需求用 Pre 系列，事后处理用 Post 系列；拿不准就查官方文档对应事件名
- 🔁 **改了配置要重启**：修改 `settings.json` 后需重启 Claude Code 会话才会加载新 Hook

## 9. 一分钟速记

- 🔥 **<span style="color:#e74c3c">Hook = Claude Code 的"自动触发器"：关键时刻一到，自动执行你写好的脚本</span>**
- ⚙️ **<span style="color:#e74c3c">写在 `settings.json` 的 `hooks` 字段里，按事件名（UserPromptSubmit / PreToolUse / PostToolUse / Stop 等）分组</span>**
- 📨 **<span style="color:#e74c3c">脚本通过退出码 + JSON 返回值影响行为：`decision: block` 能拦截工具调用，`additionalContext` 能给 Claude 注入上下文</span>**
- 🏠 **<span style="color:#2980b9">本知识库的自动维护提醒就是 UserPromptSubmit Hook——每天第一条消息到达时检查"该不该迭代/备份"，到期就自动提醒</span>**
- 🧩 **<span style="color:#2980b9">和 Skill 的区别：Hook 是"闹钟"（到点自动响），Skill 是"工具书"（需要才翻）</span>**
- ⚠️ **<span style="color:#e74c3c">Hook 有完整系统权限，只装可信脚本；改完配置要重启会话才生效</span>**

>highlight 【一句话带走】想在 Claude Code 里"到点自动干某件事"——用 Hook；想"教会 Claude 干某类事"——用 Skill。
