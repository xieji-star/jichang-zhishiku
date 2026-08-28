---
title: "Codex模型配置"
category: "AI与技术工具"
tags:
  - Codex
  - DeepSeek
  - AI配置
  - API
  - Codex++
  - 供应商配置
  - 故障排除
  - 网络故障
  - Vortex
  - 风控
source:
  - "[[../总结好的大纲以及笔记/AI/Codex模型配置大全/Codex模型配置方法大全.md]]"
  - "[[../lark-resources/codex++使用教程.pdf]]"
  - "[[../总结好的大纲以及笔记/知识库FAQ/04-Codex桌面端反复重新连接（公司环境）.md]]"
  - "[[../总结好的大纲以及笔记/知识库FAQ/05-Codex网络故障-青旅环境.md]]"
  - "[[../总结好的大纲以及笔记/知识库FAQ/06-国外网站访问慢但Codex正常.md]]"
  - "[[../总结好的大纲以及笔记/知识库FAQ/09-Microsoft Store打不开-青旅网络CDN被拦.md]]"
  - "[[../总结好的大纲以及笔记/知识库FAQ/10-mihomo IPv6出站导致ChatGPT被CF风控.md]]"
created: 2026-07-13
updated: 2026-08-24
---

# Codex 模型配置

## 概述

Codex Desktop 是一款 AI 编程助手客户端，通过 Codex++ 启动器可以接入 DeepSeek 等第三方模型。供应商配置的核心是填写 API Key、Base URL、协议信息等字段。安装方式支持 OpenAI 官网下载、Microsoft Store 和 Codex++ 启动器三种。

## 核心要点

### Codex++ 核心功能

**Codex++** 是一个面向 OpenAI Codex 桌面端的**外部增强启动器和管理工具**（开源社区项目），通过 **Chromium DevTools Protocol (CDP)** 在运行时动态注入增强脚本。GitHub：`https://github.com/BigPizzaV3/CodexPlusPlus`

| 功能 | 说明 |
|------|------|
| **插件解锁** | API Key 模式下恢复插件入口（原版禁用） |
| **会话删除** | 悬停会话即出现删除按钮，方便管理对话记录 |
| **API 中转注入** | 支持接入 DeepSeek、GLM、Kimi 等第三方大模型 |
| **Markdown 导出** | 将对话记录导出为 Markdown 文件（通过管理工具操作） |
| **供应商配置** | 灵活切换和管理多个模型供应商（Provider） |
| **用户脚本系统** | 类似 Tampermonkey，支持自定义 UI 和功能 |
| **Provider 同步** | 切换 API 后旧会话不消失，保持会话连续性 |
| **Zed 编辑器集成** | 支持远程 SSH 环境文件编辑 |

> 推荐使用 **Codex++ V1.2.3** 版本。

### 安装与启动

1. **安装 Codex 本体** → 从 OpenAI 官网下载
2. **安装 Codex++ 增强工具** → 从 GitHub Releases 下载 `.exe` 安装包
3. **通过 Codex++ 入口启动**（不要直接启动原版 Codex）
4. 安装后桌面出现两个入口：**Codex++**（增强启动器）和 **Codex++ 管理工具**（配置面板）

**启动后处理**：
- 白屏因请求 OpenAI 服务器超时，约 2 分钟内加载完成
- **白屏解决方案**：使用 VPN 或断网启动（断网后加载速度更快）
- 首次使用需配置 **Agent Sandbox**（点击 Set up → Stop 即可）

### 供应商（Provider）配置

在 Codex++ 管理工具中添加供应商：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| **名称** | 可自定义 | `DeepSeek` |
| **接入模式** | 选择纯 API | 纯 API / GAP |
| **测试模型** | 模型名称 | `deepseek-v4-flash` |
| **Base URL** | API 地址 | `https://api.deepseek.com` |
| **Key** | 在平台申请的 API Key | — |
| **上游协议** | 选择 Chat Completions | Chat Completions |

**配置步骤**：
1. 在 DeepSeek 官网注册并申请 API Key（需先充值，最低 1 元）
2. 在 Codex++ 管理工具中点击"添加供应商"
3. 填写名称（如 `DeepSeek`）、接入模式（API）、测试模型（如 `deepseek-chat`）
4. 填写 Base URL 和 API Key
5. 上游协议选择 Chat Completions
6. 保存并返回列表 → 点击"使用"启用该供应商

### 模型选择与切换

配置成功后，在 cortex 对话页面可选择：
- **DC**（默认模型）
- **Pro**（增强版）
- 部分版本可选 VS30 等

如配置成功但看不到模型 → 完全退出应用并重启试试。

### 常见问题

#### 启动白屏

| 原因 | 解决方案 |
|------|---------|
| 请求 OpenAI 服务器超时（约 2 分钟内加载完成） | **方案一**：使用 VPN（推荐） |
| 域名被阻断，请求一直等待超时 | **方案二**：断网启动（断网后加载更快） |
| 持续白屏无响应 | 完全退出 Codex → 重新进入（可多试几次） |

#### API 连接问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 401 Authentication Fails | API Key 错误 | 新建 Key 和供应商重配 |
| 402 Payment Required | 账户余额不足 | 充值（最低 1 元） |
| 404 Not Found | Base URL 配置错误 | 检查 URL 格式 |
| 502 Bad Gateway | 代理配置问题 | 关闭代理或排除本地地址 |

### 汉化方法

需科学上网（美国节点全局模式）→ Settings → General → Language → 选择中文 → 退出重启
注意：**汉化目前没有不需要科学上网的替代方案**。

### 🚨 网络故障排查（连接重置 / 流中断 / 反复重连）

> 适用于 ChatGPT 账号登录模式（走 `chatgpt.com/backend-api/codex/responses`）。最典型报错：
> - `stream disconnected before completion: error sending request for url (https://chatgpt.com/backend-api/codex/responses)`
> - `unexpected status 403 Forbidden`（Cloudflare 拦截页，cf-ray 带 `-HKG` 等边缘代码）
> - 界面反复显示"重新连接"

**核心认知**：浏览器能开 NVIDIA 等外网 ≠ Codex 正常。ChatGPT 的 backend-api 对**数据中心出口 IP 风控极严**，节点 IP 被拉黑时短请求 403、POST 流式请求被直接重置 → 表现就是 `stream disconnected`。这**不是网的问题，是节点的问题**。

> [!tip] 📍 切换网络环境后先查这一项（2026-08-06 青旅实战新增）
> 从公寓/公司切到**青旅**等新网络后，Vortex 可能被重置为 `direct` 模式（TUN 关闭），此时节点显示正常但隧道根本没建立——直连能通的站通、被墙的站（Google/ChatGPT/YouTube）全挂。**先查再换节点**：
> ```bash
> curl http://127.0.0.1:39798/configs    # 看 mode 是否为 rule
> curl -X PATCH http://127.0.0.1:39798/configs -H "Content-Type: application/json" -d '{"mode":"rule"}'  # direct→rule
> ```
> 若 `mode` 已是 `rule` 仍报错，才走下方第一步的风控排查。完整记录见 [[../总结好的大纲以及笔记/知识库FAQ/05-Codex网络故障-青旅环境.md]]。
> ⚠️ **`mode: direct` ≠ 关闭了代理客户端**——程序仍连得上 7897，只是流量被旁路直连（VPN 失效）；切回 `rule` 即恢复隧道。修复后 TUN 若关闭**也不影响 Codex**（Codex 走系统代理 `127.0.0.1:7897`），TUN 只影响不认系统代理的程序。

**第一步：确认代理路径是否被风控**

```bash
curl -x http://127.0.0.1:7897 -I https://chatgpt.com
```

| 结果 | 含义 | 动作 |
|------|------|------|
| 403 + Cloudflare 拦截页 | 出口 IP 被风控 | 切节点（第二步） |
| 连接失败/超时 | 代理未运行或端口不对 | 检查 Vortex 是否开启、端口 7897 |
| 200/301/401 | 代理路径正常 | 查 Codex 日志（第四步） |

**第二步：切换节点（Vortex 控制 API）**

Vortex 基于 mihomo，控制端口通常为 `127.0.0.1:39798`（以实测为准，用 `/version` 验证）：

```bash
curl http://127.0.0.1:39798/version                          # 验证控制端口
curl http://127.0.0.1:39798/proxies                          # 查策略组，看"节点选择"当前 now
curl -X PUT "http://127.0.0.1:39798/proxies/%E8%8A%82%E7%82%B9%E9%80%89%E6%8B%A9" \
     -H "Content-Type: application/json" -d '{"name":"节点名"}'
```

- 实测通过：**🇺🇸 美国-IEPL 02**（出口 38.45.155.83）；曾被风控：🇭🇰 香港-IEPL 01（45.67.201.103）
- 切换后验证：`curl -x http://127.0.0.1:7897 "https://chatgpt.com/backend-api/codex/models?client_version=0.146.0"` 返回 **401**（未认证=放行）而非 403（仍被风控）

**第三步：重启 Codex 桌面端**（让连接全部重建）

杀全部 `ChatGPT.exe` / `codex.exe` / `node_repl.exe` 进程 → 重新从开始菜单/`shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App` 启动。

**第四步：查 Codex 日志确认**

日志数据库：`C:\Users\asus\.codex\logs_2.sqlite`（表 `logs`）。搜索特征：
- `403` / `Forbidden` / `cf-ray` → 风控
- `error sending request for url` / `ConnectFailed` → 连接层问题
- `127.0.0.1:4780` ConnectionRefused → 旧 Rocket 端口残留（仅影响遥测，可忽略）

**快速检查清单**：
- [ ] 代理客户端在运行？`7897` 有监听？
- [ ] chatgpt.com 返回 **403** 还是 **401**？
- [ ] 当前出口节点是否在风控名单？
- [ ] Codex 日志是否有 403 / error sending request？

**节点可用性速查表**（2026-08-06 实测，ChatGPT 视角）：

| 节点 | ChatGPT 风控 | 外网连通 | 结论 |
|------|:---:|:---:|------|
| **🇺🇸 美国-IEPL 02**（38.45.155.83） | ✅ 放行(401) | ✅ 全通 | **推荐固定** |
| 🇸🇬 新加坡-IEPL 01/02/03 | ❌ SSL 断流 | ❌ | 不可用 |
| 🇭🇰 香港-IEPL 01 / 家宽系列 | ❌ 403 拦截 | ⚠️ | 不可用于 ChatGPT |
| 🇯🇵 日本原生 / 日本-IEPL | ❌ 403 | ⚠️ | 不可用于 ChatGPT |
| 🇹🇼 台湾-IEPL / 家宽 | ❌ 403 或断流 | ⚠️ | 不可用于 ChatGPT |

> 💡 **注意**：Vortex「自动节点」可能自动切回坏线路（如新加坡），建议手动固定节点。Google 对数据中心 IP 会 429 限流（不影响 YouTube/ChatGPT）。

按网络环境查档案（**先按当前所在环境选文档**）：
- 🏠 **公寓/公司环境**（DNS 污染、出口 IP 风控、节点体检）→ [[../总结好的大纲以及笔记/知识库FAQ/04-Codex桌面端反复重新连接（公司环境）.md]]
- 🏨 **青旅环境**（Vortex 被切 direct 模式、隧道未建立）→ [[../总结好的大纲以及笔记/知识库FAQ/05-Codex网络故障-青旅环境.md]]

**分流体系与新型网络故障档案**（2026-08-07 起持续沉淀）：

| 档案 | 故障特征 | 一句话处置 |
|------|---------|-----------|
| [[../总结好的大纲以及笔记/知识库FAQ/06-国外网站访问慢但Codex正常.md]] | 浏览器外网慢但 Codex 正常 | 代理分流：OpenAI/ChatGPT 域名固定走「保 Codex 节点」，其余外网走快节点 |
| [[../总结好的大纲以及笔记/知识库FAQ/09-Microsoft Store打不开-青旅网络CDN被拦.md]] | Store 打不开但外网正常 | 恢复 13 条 Microsoft 直连规则；下载 CDN 被青旅网络 TLS 中间人拦截需换网 |
| [[../总结好的大纲以及笔记/知识库FAQ/10-mihomo IPv6出站导致ChatGPT被CF风控.md]] | 网页版 `Unable to load site`，报错页 IP 是 IPv6 | mihomo 配置加 `ipv6: false`，强制 IPv4 出站 |

> ⚠️ **关键认知升级**（06/09/10 沉淀）：
> 1. **"Codex 能用" ≠ "节点快"**——保 Codex 节点（美国-IEPL 02）慢但能过 CF 风控，浏览流量应分流走快节点；
> 2. **订阅更新会重写 config.yaml**（清掉自定义分流规则、把 `mode` 还原成 direct）是反复复发的高危诱因——再遇故障先查 `/rules` 有无 openai/chatgpt 规则、`/configs.mode` 是否 rule；
> 3. **delay 正常 ≠ 对 ChatGPT 放行**——必须走代理实测目标端点（`codex/models` 返回 401=放行，403=风控）；
> 4. **IPv6 出站更易被 CF 风控**——`Unable to load site` + IPv6 报错 IP 时优先关 `ipv6`；
> 5. **节点可用性"来回漂移"**——不要长期迷信任何一个放行节点，每次故障先体检再定节点。

## 关联页面

- [[wiki/AI与技术工具/Claude Code]] — Claude Code 使用指南
- [[wiki/AI与技术工具/子Agent与MCP配置]] — 子 Agent 与 MCP 工具配置
- [[wiki/AI与技术工具/SKILL技能包]] — Agent Skill 的定义与创建

## 待深入

- 不同大模型 API 的比较与选择
- Codex++ 高级配置（模型列表、系统提示词）
- Codex 与 Claude Code 的功能对比
