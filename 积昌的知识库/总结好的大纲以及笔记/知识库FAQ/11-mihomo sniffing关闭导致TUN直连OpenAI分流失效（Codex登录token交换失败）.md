---
title: "Codex 登录 token 交换失败：mihomo sniffing 关闭导致 TUN 直连不按域名分流"
type: "知识库 FAQ / 报错修复"
date: 2026-08-13
created: 2026-08-13
updated: 2026-08-13
environment: "🏨 青旅"
tags:
  - Codex
  - 登录失败
  - token_exchange_failed
  - TUN
  - sniffing
  - mihomo
  - 分流
  - 青旅
source: "2026-08-13 19:42 青旅现场实测 + Vortex 控制 API 诊断"
---

# 🔑 Codex 登录 token 交换失败（mihomo sniffing 关闭致 TUN 直连不按域名分流）

> [!summary] 📊 报错统计速览（截至 2026-08-13）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（2026-08-13 原始事件 1 次）。根因为 **「mihomo sniffing 关闭致 TUN 直连不按域名分流」**（台账累计 1 次，本文档）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 mihomo sniffing 关闭致 TUN 直连不按域名分流 | **1** | 11 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!SUMMARY] 📌 结论摘要
> 用户回到青旅，代理配置修复后（见 [[05-Codex网络故障-青旅环境#🔁 复发记录（2026-08-13 19：30）]]），Codex 登录仍报 <span style="color:#ff0000">`Token exchange failed: error sending request for url (https://auth.openai.com/oauth/token)`</span>（错误码 `token_exchange_failed`）。诊断发现：<span style="color:#ff0000">**mihomo `sniffing: false`（TUN 捕获直连流量不嗅探 SNI）导致 TUN 直连路径下 OpenAI 域名全部无法命中 `DOMAIN-SUFFIX,openai.com` 规则**</span>——auth.openai.com / chatgpt.com / api.openai.com 走 TUN 直连全部 `exit 35`（SSL 被 GFW 重置），而 google.com 走 TUN 却 200（命中 MATCH→🇹🇼 台湾-IEPL 03 兜底）。即：**凡是不认系统代理、走直连/TUN 的应用流量（如 Codex 原生 HTTP 客户端的 token 交换），OpenAI 域名都会被 GFW 拦**。处置：配置文件加 `sniffing: true` + 热加载 + 重启 Codex 后，TUN 直连路径恢复——`api.openai.com/v1/models` **401**、`auth.openai.com` **403**（curl 无 UA 的 CF 挑战，连接已通）。<span style="color:#1e90ff">Codex 登录可重试。</span>

## 🧭 快速索引

- 🚨 [[#🚨 错误概览|错误概览]]
- 🧩 [[#🧩 根本原因|根本原因]]
- 🔬 [[#🔬 三层诊断数据|三层诊断数据]]
- 🛠️ [[#🛠️ 修复过程|修复过程]]
- ✅ [[#✅ 验证结果|验证结果]]
- 🧰 [[#🧰 技术栈与术语|技术栈与术语]]
- 🛡️ [[#🛡️ 后续建议与遗留事项|后续建议与遗留事项]]
- 🔗 [[#🔗 相关笔记与附件|相关笔记与附件]]

## 🚨 错误概览

| 项目 | 现场信息 |
|---|---|
| 记录时间 | 2026-08-13 19:42（Asia/Shanghai） |
| 网络环境 | 🏨 **青旅**（hostel） |
| 现象 | Codex 登录报 `Sign-in could not be completed`；`Token exchange failed: error sending request for url (https://auth.openai.com/oauth/token)`；错误码 `token_exchange_failed` |
| 应用 | Windows 版 Codex 桌面端 |
| 代理 | Vortex（mihomo 1.10.0），mixed-port `7897`，控制 API `127.0.0.1:39798`，**TUN 开启** |
| 关键证据 | TUN 直连（`curl --noproxy '*'`）auth.openai.com/chatgpt.com/api.openai.com 全部 `exit 35`；google.com 却 **200**（走 MATCH→台湾-IEPL 03）；`/configs` `sniffing: false` |
| 最终状态 | <span style="color:#1e90ff">已修复（sniffing: true + 重启 Codex，TUN 直连路径恢复）</span> |

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 代理配置层 | <span style="color:#ff0000">mihomo `sniffing: false`，TUN 捕获的直连流量不嗅探 SNI/域名</span> | `/configs` `sniffing: false`；直连 google 200、直连 OpenAI 全 exit 35 | 配置文件加 `sniffing: true` + 热加载 |
| 路由层 | TUN 直连流量因无法识别域名，**不命中 `DOMAIN-SUFFIX,openai.com` 规则**，全部掉进 `MATCH → 🇹🇼 台湾-IEPL 03` | 直连 api.openai.com 走 TUN 时不在 /connections 显示 openai 链 | 开启 sniffing 后按 SNI 命中域名规则 |
| 节点层 | 🇹🇼 台湾-IEPL 03 对 OpenAI 域名失败（对 api.openai.com 504、chatgpt 403/断流），但对 Google 等普通外网可用 | 节点 delay 体检：台湾-IEPL 03 对 api.openai.com=**504**、对 gstatic=**81ms** | 不需换节点；让 OpenAI 流量正确落到 🇺🇸 美国-IEPL 02 |
| 应用层 | Codex 原生 HTTP 客户端（token 交换）不认系统代理（WinINET），走直连 → 被 TUN 捕获 → 因 sniffing 关闭而分流失效 | token 交换请求 `error sending request`；WebView 登录页（走系统代理）正常 | 修好 TUN 分流路径后应用直连即可用 |

> [!IMPORTANT] ⚠️ 关键认知
> **代理端口路径通 ≠ TUN 直连路径通。** 走 `-x 127.0.0.1:7897`（显式代理）时 mihomo 按 CONNECT 主机名直接命中域名规则，OpenAI 正常；但**走 TUN 直连**时，若 `sniffing: false`，mihomo 只能按目标 IP 匹配规则（域名规则失效），所有国外流量统一掉进 `MATCH` 兜底——OpenAI 域名恰好兜底到一个对 OpenAI 失败的快节点，于是表现为"代理能通、应用登录却失败"。**凡出现"浏览器/显式代理能上 OpenAI，但某应用（不认系统代理、走直连）登录/访问失败"，第一件事查 `/configs` 的 `sniffing` 是否为 true。**

## 🔬 三层诊断数据

### 1. 代理配置层（决定性证据）

```json
// GET /configs（修复前）
{ "mode": "rule", "tun": { "enable": true }, "sniffing": false, "ipv6": false }

// GET /rules（修复前）
// 5 条 OpenAI 规则在位 → 🇺🇸|美国-IEPL 02；MATCH → 🇹🇼|台湾-IEPL 03
```

- 规则、节点、mode 全部健康（这是 05 档案 19:30 已修复的状态）
- ⚠️ **唯一异常：`sniffing: false`**——TUN 直连流量不嗅探域名

### 2. 网络层（显式代理 vs TUN 直连 对比）

**走显式代理 `127.0.0.1:7897`（全通）：**

| 站点 | 结果 |
|---|---|
| auth.openai.com 首页 | HTTP 200（1.32s） |
| auth.openai.com/oauth/token POST | HTTP 400（空请求的正常服务器响应） |
| api.openai.com/v1/models | HTTP 401（放行） |

**TUN 直连（`curl --noproxy '*'`，修复前 `sniffing: false`）：**

| 站点 | 结果 | 判定 |
|---|---|---|
| google.com | HTTP 200（0.89s） | ✅ MATCH→台湾-IEPL 03 兜底，普通外网正常 |
| baidu.com | HTTP 200 | ✅ 直连 |
| auth.openai.com | **exit 35 / HTTP 000** | 🔴 被 GFW 重置 |
| chatgpt.com | **exit 35 / HTTP 000** | 🔴 被 GFW 重置 |
| api.openai.com | **exit 35 / HTTP 000** | 🔴 被 GFW 重置 |

> 💡 判读：google 能通、OpenAI 全挂 → 不是 TUN 整体失效，而是 **OpenAI 域名未被识别、掉进兜底坏节点**。google 经台湾-IEPL 03 可用，OpenAI 经台湾-IEPL 03 失败（该节点对 OpenAI 403/504）。

### 3. 环境层

- 系统代理（WinINET）：`ProxyEnable=1`、`ProxyServer=127.0.0.1:7897` ✅
- **WinHTTP 代理：未设置（直接访问）**——Rust/reqwest 类客户端的另一种取值通道
- 代理环境变量（HTTP_PROXY/HTTPS_PROXY）：**无**
- TUN 网卡：`Meta Tunnel` Up
- Codex 进程：登录时在线，活动连接含 auth.openai.com→美国-IEPL 02（WebView 登录页走系统代理正常）

## 🛠️ 修复过程

1. **复现**：显式代理 curl auth.openai.com 全通（200/400）→ 排除节点与规则问题；TUN 直连 curl OpenAI 全 exit 35、google 200 → 锁定"TUN 直连分流失效"。
2. **定位**：`/configs` 显示 `sniffing: false` → 域名规则对 TUN 直连流量失效。
3. **改配置**（Python UTF-8 安全写入，备份 `原始文件备份/vortex-config-20260813-1945-sniffing.yaml`）：顶层 `mode: rule` 后插入 `sniffing: true`。
4. **热加载**：`PUT /configs?force=true` → **HTTP 204**；恢复 TUN → **204**。
5. **（可选）WinHTTP 代理**：`netsh winhttp set proxy 127.0.0.1:7897` 因非管理员会话报"拒绝访问"，**跳过**——TUN sniffing 修复已覆盖直连路径，无需此项。
6. **重启 Codex**：杀全部 ChatGPT/codex/node_repl/codex-code-mode-host → PowerShell `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"` 拉起（规避 MSYS 路径转换坑）。

## ✅ 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| TUN 直连 api.openai.com | exit 35 | **401**（1.00s，放行） |
| TUN 直连 auth.openai.com | exit 35 | **403**（0.89s，CF 无 UA 挑战，连接已通） |
| TUN 直连 chatgpt.com | exit 35 | **403**（CF 无 UA 挑战） |
| 显式代理 codex/models | 401 | **401**（0.89s） |
| 显式代理 auth.openai.com/oauth/token POST | 400 | **400**（端点响应正常） |
| codex 进程 | 旧进程 35012 | 新进程 **35756**，10 条 Established → 127.0.0.1:7897 |

- [x] 配置文件持久化 `sniffing: true`（热加载/重启不回退，除非订阅更新重写）
- [x] `/configs` mode=rule / ipv6=false / tun=true / port=7897
- [x] TUN 直连路径下 OpenAI 域名已按域名规则分流到 🇺🇸 美国-IEPL 02
- [x] Codex 已重启，可重试登录

> [!note] ℹ️ 关于 403 的判断
> `curl` 无浏览器 UA 访问 auth.openai.com/chatgpt.com 首页返回 **403** 是 Cloudflare 对落地页的机器人指纹拦截（FAQ 05/06 一致判据），**不是出口 IP 风控**；以 `api.openai.com/v1/models` 返回 **401** 为准。真实浏览器/WebView 带完整 UA 时登录页正常加载。

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| `token_exchange_failed` | Codex OAuth 登录流程中，应用用授权码向 `auth.openai.com/oauth/token` 换取令牌的请求失败 |
| TUN 直连 | 应用不设代理、直接发 TCP/TLS 连接，被 mihomo 虚拟网卡（TUN）捕获后按规则转发 |
| `sniffing` | mihomo 对捕获到的流量嗅探 TLS 的 SNI/域名，从而能按**域名规则**分流；关闭时只能按 IP 匹配 |
| SNI | TLS 握手时客户端明文的"服务器名称"，mihomo 靠它识别目标是哪个域名 |
| 显式代理 | 应用主动走 `127.0.0.1:7897`，mihomo 直接拿到 CONNECT 主机名，天然命中域名规则 |
| MATCH 兜底 | 规则列表最后一条，未命中前面任何规则的流量走这里 |
| WinHTTP / WinINET | Windows 两套代理配置通道；浏览器/WebView 多走 WinINET，原生程序/Rust 客户端可能走 WinHTTP |

## 🛡️ 后续建议与遗留事项

1. <span style="color:#ff8c00">**`sniffing: true` 已在配置文件中持久化**，但订阅更新重写 config.yaml 时可能被清回默认（false）。再遇"显式代理能上 OpenAI、某应用登录/访问却失败"，先查 `curl -s http://127.0.0.1:39798/configs` 的 `sniffing` 字段。</span>
2. <span style="color:#ff8c00">**WinHTTP 代理未设置**（需管理员权限），暂不影响本机（TUN 已兜底直连）；若日后有更多"不认系统代理"的应用需要代理，可用管理员运行 `netsh winhttp set proxy 127.0.0.1:7897`。</span>
3. 台湾-IEPL 03 对 OpenAI 失败（504/403），仅适合作普通外网兜底；**OpenAI 流量必须走 🇺🇸 美国-IEPL 02**（sniffing 修复后已正确命中）。
4. 本档与 05 档案（青旅）强相关：05 管"配置被清/direct"，本档管"配置健康但 TUN 分流失效"——**排查顺序：① 配置/规则（05）→ ② sniffing/TUN 分流（本档）→ ③ 节点质量**。

## 🔗 相关笔记与附件

- [[05-Codex网络故障-青旅环境]] — 🏨 **青旅环境**档案：Vortex 被切 direct / 订阅清规则；本次事件的代理配置修复见其 08-13 19:30 复发记录
- [[04-Codex桌面端反复重新连接（公司环境）]] — Codex 网络故障总档案：DNS 污染、出口风控、节点速查表
- [[06-国外网站访问慢但Codex正常]] — 分流规则档案：OpenAI 走美国节点、其余走快节点
- [[00-报错统计台账]] — 全局报错统计
- 配置备份：`原始文件备份/vortex-config-20260813-1945-sniffing.yaml`（修复前）
