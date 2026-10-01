---
title: "cc-switch 中转 DeepSeek 内容风控拦截（Content Exists Risk 与 Usage Policy）"
type: "知识库 FAQ / 报错记录"
date: 2026-09-20
created: 2026-09-20
updated: 2026-09-20
tags:
  - 报错
  - 知识库FAQ
  - cc-switch
  - DeepSeek
  - ContentExistsRisk
  - UsagePolicy
  - invalid_request
  - 内容风控
  - Claudian
source: "Claudian（realclaudian）插件调用 Claude Code — 请求经 cc-switch 本地代理（127.0.0.1:15721）转发至 DeepSeek 的 Anthropic 兼容端点（api.deepseek.com/anthropic）"
---

# 🔀 cc-switch 中转 DeepSeek 内容风控拦截（Content Exists Risk 与 Usage Policy）

> [!summary] 📊 报错统计速览（截至 2026-09-20）
> 🔥 **本文档共记录 <span style="color:#e74c3c">2 次报错事件</span>**（2026-09-20 首发 1 次，复发 1 次）。根因为 **「Claude Code 经 cc-switch 中转至 DeepSeek（非 Anthropic 官方），DeepSeek 内容风控拦截请求」**。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🌐 cc-switch 中转至 DeepSeek 致内容风控拦截（Content Exists Risk / Usage Policy） | **2** | 23 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

## 🧭 快速索引

- 🧾 [[#错误信息|错误信息]]
- ⚠️ [[#现象描述|现象描述]]
- 🔍 [[#根本原因|根本原因]]
- 📊 [[#诊断数据|诊断数据]]
- 🛠️ [[#修复过程|修复过程]]
- 📽️ [[#技术栈与涉及工具|技术栈与涉及工具]]
- 🕳️ [[#遇到的问题与坑|遇到的问题与坑]]
- ✅ [[#验证结果|验证结果]]
- 📌 [[#使用建议与遗留事项|使用建议与遗留事项]]

## 错误信息

**用户贴出的报错原文（Claudian 面板显示）：**

```
Error: invalid_requestAPI Error: Claude Code is unable to respond to this request, which appears to violate our Usage Policy (https://www.anthropic.com/legal/aup). Try rephrasing the request or attempting a different approach.
Error: invalid_request
```

**cc-switch 日志 / 数据库里记录的真实上游报错（DeepSeek 返回）：**

```
上游 HTTP 400: {"error":{"message":"Content Exists Risk","type":"invalid_request_error","param":null,"code":"invalid_request_error"}}
上游 HTTP 402: {"error":{"message":"Insufficient Balance","type":"unknown_error","param":null,"code":"invalid_request_error"}}
上游 HTTP 502（网关错误）
```

> **出现时间**：2026-09-20 20:58–21:29（当日反复出现；此前 09-19 亦有同类记录）
> **来源**：Claudian（realclaudian）Obsidian 插件 → Claude Code CLI → **cc-switch 本地代理** → **DeepSeek API**
> **触发场景**：模型为 `claude-haiku-4-5-20251001`（即 Claudian 里的 "haiku"），被 cc-switch 映射到 DeepSeek 的 `deepseek-flash` 供应商时反复报错。

## 现象描述

在 Obsidian 的 Claudian 面板中，**每次发送消息都弹报错**，会话无法推进。关键特征：

- 🔥 **<span style="color:#e74c3c">报错表面指向 Anthropic「Usage Policy」，实则来自 DeepSeek 的内容风控</span>**——Claude Code 收到的 `type` 是 `invalid_request_error`，于是按 Anthropic 风格包装成「violates our Usage Policy」展示；
- 数据库里真实的错误是 **`Content Exists Risk`（400，内容风险）** 和 **`Insufficient Balance`（402，余额不足）**；
- 切换供应商前（`deepseek-v4-flash`）**持续失败**；切换后（`deepseek-v4-pro`）**立即恢复正常**。

> 💡 **<span style="color:#2980b9">认知：</span>** 这不是 Anthropic 在拦截，也不是网络/文件故障，而是**「你以为在用的 Claude，其实后端是 DeepSeek」**——DeepSeek 有独立的内容风控（内容存在风险即拒绝）和账户余额校验。

## 根本原因

### 核心原因：Claude Code 走 cc-switch 中转，后端根本不是 Anthropic Claude

`C:\Users\asus\.claude\settings.json` 里配了：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",
    "ANTHROPIC_AUTH_TOKEN": "PROXY_MANAGED"
  }
}
```

`127.0.0.1:15721` 是 **cc-switch.exe**（Claude Code 中转切换器）监听的本地代理端口。它把 Claude Code 的请求**改写后转发到用户选中的第三方供应商**。数据库里共 12 个供应商，**没有一个是真正的 Anthropic Claude**：

| 供应商名 | 实际后端 | 模型 |
|---|---|---|
| `claude-official`（⚠️ 名字有误导） | api.deepseek.com | DeepSeek-V3.2 |
| `deepseek-v4-pro`（**当前选中**） | api.deepseek.com | deepseek-v4-pro |
| `deepseek-v4-flash`（报错元凶） | api.deepseek.com | deepseek-flash |
| DouBaoSeed | 火山方舟 ark.cn-beijing.volces.com | doubao-seed |
| 硅基流动免费 | api.siliconflow.cn | Qwen2.5-72B |
| Zhipu GLM | open.bigmodel.cn | glm-5.3 |
| My Claude | ai.hsnb.fun | grok-4.5 |
| 英伟达NIM | integrate.api.nvidia.com | gpt-oss |

所以 Claudian 里选 "haiku / sonnet / opus" 时，实际调用的是 **DeepSeek / 豆包 / 千问 / GLM** 等国产模型。

### 故障链条

1. Claudian 用 "haiku"（`claude-haiku-4-5-20251001`）发起请求；
2. Claude Code 按 `ANTHROPIC_BASE_URL=127.0.0.1:15721` 把请求交给 cc-switch；
3. cc-switch 按当前供应商 `deepseek-v4-flash`，把请求转发到 `https://api.deepseek.com/anthropic/v1/messages`；
4. DeepSeek 内容风控判定内容「存在风险」→ 返回 `400 Content Exists Risk`（`type=invalid_request_error`）；
5. 或 DeepSeek 账户余额不足 → 返回 `402 Insufficient Balance`；
6. Claude Code 把 `invalid_request_error` 包装成「violates our Usage Policy」展示给用户。

> ⚠️ **<span style="color:#e67e22">根因归属：</span>** 属**网络/代理类**（cc-switch 是 API 中转代理层）。本质是「中转供应商（DeepSeek）的内容风控 + 余额」拦截，不是网络连通性故障，也不是文件/环境故障。

## 诊断数据

**环境变量（`env`）：** `ANTHROPIC_BASE_URL=http://127.0.0.1:15721`、`ANTHROPIC_AUTH_TOKEN=PROXY_MANAGED`。

**端口监听：** `netstat` 显示 `127.0.0.1:15721 LISTENING`，进程为 `cc-switch.exe`（PID 17304）。

**cc-switch 配置：** `C:\Users\asus\.cc-switch\`，`settings.json` 里 `currentProviderClaude = 0d2782a1-c216-4fcd-bb24-0212e0038c7c`（即 deepseek-v4-pro，2026-09-20 21:29:21 热切换后）。

**请求日志统计（proxy_request_logs 表）：**

| 供应商 | 状态码 | 次数 | 含义 |
|---|---|---:|---|
| `e7cfd98c`（deepseek-v4-flash） | 400 | 19 | Content Exists Risk（内容风控） |
| `e7cfd98c`（deepseek-v4-flash） | 402 | 4 | Insufficient Balance（余额不足） |
| `e7cfd98c`（deepseek-v4-flash） | 502 | 32 | 上游网关错误 |
| `83a61c76`（Zhipu GLM） | 429 | 55 | 限流 |
| `0d2782a1`（deepseek-v4-pro，当前） | 200 | 26 | **全部成功** |

> 🔍 **<span style="color:#e74c3c">关键证据：</span>** 切换供应商前（deepseek-v4-flash）持续 400/402/502；21:29:21 热切换到 deepseek-v4-pro 后，26 次请求**全部 200 成功、0 报错**。

## 修复过程

1. **诊断**（无需改文件，只读排查）：查 `~/.claude/settings.json` 发现 API 走本地代理 → `netstat` 定位 15721 端口为 cc-switch → 读 cc-switch 日志与 SQLite 数据库 → 确认后端是 DeepSeek、报错是「Content Exists Risk + Insufficient Balance」；
2. **修复动作（已由热切换完成）**：把当前供应商从 `deepseek-v4-flash` 切到 `deepseek-v4-pro`（2026-09-20 21:29:21 已切换，日志显示切换后请求全部成功）；
3. **无需改 cc-switch 配置**：当前 deepseek-v4-pro 状态健康，**不主动动供应商配置**，避免误伤。

> 🛠️ **<span style="color:#2980b9">本次修复性质：</span>** 属「诊断 + 确认已修复」型，不是「改文件」型。核心结论是**报错的元凶是 deepseek-v4-flash 供应商（内容风控 + 余额），换供应商即恢复**。

## 技术栈与涉及工具

- **Claudian（realclaudian）Obsidian 插件**：调用 Claude Code CLI；
- **Claude Code CLI**：模型配置走 `~/.claude/settings.json` 的 `env`；
- **cc-switch**：Claude Code 中转切换器（本地代理 `127.0.0.1:15721`，配置库 `C:\Users\asus\.cc-switch\cc-switch.db`，日志 `logs/cc-switch.log`）；
- **DeepSeek Anthropic 兼容端点**：`https://api.deepseek.com/anthropic/v1/messages`；
- **其它供应商**：火山方舟（豆包）、硅基流动（Qwen）、智谱（GLM）、ai.hsnb.fun（grok）等。

## 遇到的问题与坑

- 🕳️ **<span style="color:#e74c3c">「Claude Official」供应商名极具误导性：</span>** cc-switch 里 `claude-official` 的 `ANTHROPIC_BASE_URL` 已被改成 `api.deepseek.com`、模型全映射为 DeepSeek-V3.2——**名字叫 Claude Official，实际是 DeepSeek**，排查时别被名字骗了；
- 🕳️ **报错文案 ≠ 真实来源：** 面板显示「violates our Usage Policy（anthropic.com 链接）」，但上游真实返回是 DeepSeek 的「Content Exists Risk」——因为 `type=invalid_request_error` 被 Claude Code 按 Anthropic 风格包装，**看到 anthropic.com 链接不代表请求真到了 Anthropic**；
- 🕳️ **同一供应商可能同时踩多个坑：** deepseek-v4-flash 同时出现 400（内容风控）、402（余额）、502（网关），**别只看一个状态码**，要按供应商维度统计；
- 🕳️ **国产模型普遍带内容风控：** DeepSeek、豆包、GLM、Qwen 均受内容合规约束，遇到「内容风险」类拒绝是**供应商行为，不是知识库/插件 bug**，换供应商或改写内容才能解决。

## 验证结果

- ✅ **当前供应商 deepseek-v4-pro 完全健康：** 数据库统计 26 次请求全部 `200`、0 次报错；
- ✅ **报错元凶定位明确：** deepseek-v4-flash 供应商 400×19 + 402×4 + 502×32，切换后报错消失；
- ✅ **本会话（当前修复对话）正常跑通**：说明当前 deepseek-v4-pro 路线可用；
- 📌 **诚实说明：** 本次未改动任何配置文件（cc-switch 配置已由热切换到位），修复 = 「确认当前供应商可用 + 说清根因」。

## 🔁 复发记录（2026-09-20 21:55）

**<span style="color:#e74c3c">触发内容定位：VPN / 代理 / 翻墙相关对话</span>**

- 用户切回 `deepseek-v4-flash` 后再次报错，随后连续热切换 `deepseek-v4-flash copy` → `deepseek-v4-pro`，**三个供应商全部返回 `400 Content Exists Risk`**（21:54:54 / 21:55:29 / 21:55:54 / 21:55:58）；
- 定位失败会话 `8bef9ee8`（仅 119 字节，只有 ai-title）标题为「修复 VPN 无法连接外网问题」——**首轮请求即被拦截**；
- 相邻会话 `c914d543`（「Fix VPN connection failure in school dorm network」）末条 `USER: 继续任务` → `ASST: API Error: 400 Content Exists Risk`；
- 🔥 **结论：触发内容 = VPN / 翻墙 / 代理 排查对话**。DeepSeek（中国公司）依《生成式人工智能服务管理暂行办法》**必须过滤「翻墙、VPN 绕过网络审查、访问境外被墙网站」类内容**，用户大量 VPN 排查对话（含代理配置、访问 Google/OpenAI 等）命中其风控；
- ⚠️ **切换 flash/pro 无效**：两者同为 DeepSeek、共用同一套内容风控，换模型不解决内容问题。
- 📌 **补充（22:02–22:07，用户报「Error: unknown 一直显示」）：** 「Error: unknown」是 Claudian 对**同一错误的显示前缀**（它无法归类错误类型时显示 unknown），底层原文仍是 `Error: unknownAPI Error: 400 Content Exists Risk`；用户连开多个「修复宿舍网络无法连接外网 / Troubleshoot VPN connection in dorm / Fix VPN connection in dorm network」会话，**首条消息即被拦**——出现 119–120 字节的失败会话（只有 ai-title、无任何 assistant 回复）。**只要会话涉及 VPN / 翻墙 / 连接外网，DeepSeek 一律首轮拦截。**

## 使用建议与遗留事项

- 🔥 **<span style="color:#e74c3c">立即生效：</span>** 保持当前供应商 `deepseek-v4-pro` 即可；若再遇「Content Exists Risk / Usage Policy」，**第一反应是换 cc-switch 供应商**（豆包、GLM、Qwen 等），而不是改知识库文件；
- 💡 **余额告警：** deepseek-v4-flash 的 key 出现过 `Insufficient Balance`（402），**去 DeepSeek 开放平台查余额并充值**，否则换回该供应商仍会报错；
- 💡 **内容风控：** 若某段内容反复触发「Content Exists Risk」，说明 DeepSeek 判定该内容存在风险——**改写/绕开该内容**，或换到内容策略不同的供应商；
- ⚠️ **<span style="color:#e67e22">想要真正的 Claude：</span>** 当前 12 个供应商里没有一个是 Anthropic 官方，全是国产/第三方模型。若需真 Claude，要在 cc-switch 里配一个**真实 Anthropic API key**（或可靠的 Claude 中转站）；
- 📌 **监测对象：** cc-switch 各供应商的 4xx/5xx 状态码分布（尤其 400 内容风控、402 余额、429 限流），作为「换供应商决策」的依据。

## 🔗 相关笔记

- [[00-报错统计台账]] — 报错统计权威源（本档案为 N17 行）
- [[01-Obsidian反复报错Request too large]] — 同系列「invalid_request」报错（但根因是体积超限，与此不同）
- [[05-Codex网络故障-青旅环境]]、[[06-国外网站访问慢但Codex正常]] — 同属「代理/中转」体系问题
- [[17-tool_result内嵌伪PNG致API400unsupported-image]] — 同为 Claudian 会话 4xx 报错案例
