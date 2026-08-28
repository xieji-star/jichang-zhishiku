---
title: "GPT 网页版 Unable to load site：mihomo IPv6 出站被 Cloudflare 风控"
type: "知识库 FAQ / 报错修复"
date: 2026-08-11
created: 2026-08-11
updated: 2026-08-13
environment: "🏨 青旅"
tags:
  - ChatGPT
  - Firefox
  - 网络故障
  - Cloudflare
  - 风控
  - IPv6
  - mihomo
  - Vortex
source: "2026-08-11 20:47 青旅现场实测 + Vortex 控制 API 诊断"
---

# 🌐 GPT 网页版 Unable to load site（mihomo IPv6 出站被 CF 风控）

> [!summary] 📊 报错统计速览（截至 2026-08-13）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（2026-08-11 首发 1 次，暂无复发记录）。根因为 **「IPv6 出站被 CF 风控」**——mihomo 配置 `ipv6: true` 时走 IPv6 出站，CF 对数据中心 IPv6 出口风控更严。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🟠 IPv6 出站被 CF 风控 | **1** | 10 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!SUMMARY] 📌 结论摘要
> 20:40 修复青旅外网（mode:direct + OpenAI 规则被清）后，用户反馈 GPT 网页版报 <span style="color:#ff0000">`Unable to load site`</span>，错误页显示 <span style="color:#ff0000">客户端 IP 为 IPv6 `2a06:a005:87f:ffff::220`</span>。诊断发现：<span style="color:#ff8c00">mihomo 配置文件默认 `ipv6: true`，走代理出站时用 IPv6 连接 Cloudflare，CF 对 IPv6 数据中心出口的风控更严</span>——curl 简单 UA 访问 chatgpt.com 返回 200，但带 Firefox 完整指纹 + `--compressed` 返回 <span style="color:#ff0000">403 CF JS Challenge</span>（"Enable JavaScript and cookies to continue"），Firefox 实际渲染成 "Unable to load site"。在配置文件顶层加 <span style="color:#1e90ff">`ipv6: false` 并热加载后，Firefox 指纹请求 403 → 200</span>，外网与 Codex 全部恢复。<span style="color:#1e90ff">这是"代理出站 IPv6 被 CF 风控"的首次记录（FAQ 原有风控档案 04 只覆盖 IPv4 出口）。</span>

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
| 记录时间 | 2026-08-11 20:47（Asia/Shanghai） |
| 网络环境 | 🏨 **青旅**（hostel），Vortex（mihomo）代理，mixed-port `7897`，控制 API `127.0.0.1:39798` |
| 现象 | 浏览器（Firefox）打开 `chatgpt.com` 报 <span style="color:#ff0000">`Unable to load site`</span>，页面含 "If you are using a VPN, try turning it off"、Ray ID、<span style="color:#ff0000">IP: `2a06:a005:87f:ffff::220`（IPv6）</span> |
| 前置状态 | 20:40 已修复 mode:direct + OpenAI 规则被清（见 [[05-Codex网络故障-青旅环境]] 复发记录）；curl 简单 UA 测 chatgpt.com 200 |
| 关键证据 | 带 Firefox 完整指纹 + `--compressed` 走代理访问 chatgpt.com → **403 CF JS Challenge**；mihomo 配置 `ipv6: true`（默认值，配置文件无显式项） |
| 最终状态 | <span style="color:#1e90ff">已修复（配置 `ipv6: false`，热加载后 Firefox 指纹 200）</span> |

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 代理配置层 | <span style="color:#ff0000">mihomo 配置文件默认 `ipv6: true`，走代理出站用 IPv6 连接 Cloudflare</span> | 报错页客户端 IP 为 IPv6 `2a06:a005:87f:ffff::220`（非本机 IPv6）；`/configs` 运行时 `ipv6: true` | 配置顶层加 `ipv6: false`，强制 IPv4 出站 |
| 风控层 | CF 对 **IPv6 数据中心出口** 风控更严，Firefox 完整指纹触发 JS Challenge 且无法自动通过 | 简单 UA curl → 200；Firefox 指纹 + `--compressed` curl → 403 "Enable JavaScript and cookies"；Firefox 渲染为 "Unable to load site" | 关闭 IPv6 后强制 IPv4 出口，CF 放行 |
| 对比层 | IPv4 出口（美国-IEPL 02，38.45.155.83）对 chatgpt.com 正常 | 关闭 ipv6 后同指纹请求 200；08-10 04 档案记录该节点对 OpenAI 放行 | 无需换节点 |

> [!IMPORTANT] ⚠️ 关键认知
> **CF 的 JS Challenge 对"IPv6 数据中心出口"比对 IPv4 更敏感。** 报错页显示 `IP: 2a06:a005:87f:ffff::220`（IPv6）说明代理出站走了 IPv6——即使节点本身是 IPv4 节点，mihomo 开启 `ipv6: true` 时解析到目标 AAAA 记录会用 IPv6 直连出站，CF 看到 IPv6 数据中心 IP 风控升级。**排查"网页版打不开但 curl 能 200"时，先看错误页 IP 是否为 IPv6，是则优先在 mihomo 配置关 `ipv6`。**

## 🔬 三层诊断数据

### 1. 代理配置层（决定性证据）

- `GET /configs`：`mode: rule`、`ipv6: true`（配置文件无显式 `ipv6` 字段，取 mihomo 默认值 true）、`tun.enable: false`
- 配置文件顶层：无 `ipv6` 字段（第 4 行 `mode: rule`，第 5 行 `log-level: info`）

### 2. 网络层（走代理 7897 实测 chatgpt.com）

| 测试条件 | 结果 | 判定 |
|---|---|---|
| curl 简单 UA | **HTTP 200** | IPv4 出口放行 |
| curl 带 Firefox 完整指纹 + `--compressed` | **HTTP 403**，返回体 `Enable JavaScript and cookies to continue`（`_cf_chl_opt` JS Challenge） | IPv6 出口被 CF 风控 |
| Firefox 实际浏览器 | `Unable to load site`，IP: `2a06:a005:87f:ffff::220`（IPv6） | Challenge 无法通过 |
| 关闭 `ipv6: false` 后，同 Firefox 指纹 | **HTTP 200**（连续 3 次稳定） | IPv4 出口放行 |

### 3. 环境层（确认报错 IP 非本机）

| 检查项 | 结果 |
|---|---|
| 本机 IPv6 | `fdfd::1ab4:4e10`（Teredo ULA）、`fe80::...`（链路本地）、`2001:0:14c9:...`（Teredo 隧道）——**均非 `2a06:a005:87f:ffff::220`** |
| 判定 | 报错 IP 是代理出站到 CF 时 CF 看到的客户端 IPv6（节点侧出口），非本机地址 |
| 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897`（正常） |
| Firefox 连接 | 主进程 `127.0.0.1:... → 7897 ESTABLISHED`（走代理正常） |

## 🛠️ 修复过程

1. 复现：带 Firefox 完整指纹 curl 走代理访问 chatgpt.com → 403 CF JS Challenge（此前简单 UA 200）。
2. 分析报错页 IP 为 IPv6 → 怀疑 mihomo IPv6 出站。
3. 查 `/configs` 确认 `ipv6: true`（配置文件无显式字段，为默认值）。
4. 备份：`原始文件备份/vortex-config-20260811-2047-before-ipv6-fix.yaml`。
5. 编辑 `C:\Users\asus\.config\com.vortex.helper\config.yaml` 顶层（`mode: rule` 之后）加 <span style="color:#1e90ff">`ipv6: false`</span>。
6. 热加载：`PUT /configs?force=true`（Python json 构造 body，返回 **204**），确认运行时 `ipv6: False`。
7. 复测：同 Firefox 指纹 curl → **HTTP 200**（连续 3 次）；youtube/google 200、codex/models 308。

> [!NOTE] 💡 为什么不改浏览器而改代理
> 报错 IP 是代理出站的 IPv6，根因在代理层，改 mihomo 配置一处即可让所有走代理的程序（浏览器/Codex/App）统一走 IPv4 出站。若只改 Firefox（禁用 IPv6/HTTP/3）则 Codex 桌面端等其它程序仍可能踩 IPv6 风控。国内网络环境以 IPv4 为主，关 IPv6 对用户体验影响极小。

## ✅ 验证结果

- [x] 运行时 `/configs.ipv6` = `false`
- [x] 走代理 Firefox 指纹 `chatgpt.com` → **200**（连续 3 次稳定，1.7~1.9s）
- [x] `youtube.com` → 200、`google.com` → 200（MATCH 兜底走台湾-IEPL 03）
- [x] `chat.openai.com/backend-api/codex/models` → 308（放行，非 403 风控）
- [x] `mode` 保持 `rule`，OpenAI 5 条规则 → 🇺🇸 美国-IEPL 02（未受影响）

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| IPv6 出站 | 代理转发流量时优先使用 IPv6 连接目标（目标有 AAAA 记录时）；mihomo `ipv6: true` 默认开启 |
| CF JS Challenge | Cloudflare 反机器人验证页（403），要求浏览器执行 JS 并通过后才放行；数据中心/代理 IP 更易触发 |
| `ipv6: false` | mihomo 关闭 IPv6 支持，DNS 不返回 AAAA、出站只用 IPv4，规避 IPv6 出口风控 |
| Teredo | Windows 的 IPv6 过渡隧道技术，本机地址形如 `2001:0:...` |
| Ray ID | Cloudflare 边缘响应的唯一标识（`a297584d2acf4625`），用于风控/故障定位 |

## 🛡️ 后续建议与遗留事项

1. <span style="color:#ff8c00">以后网页版 ChatGPT 报 `Unable to load site` / `Access denied` 且错误页 IP 是 IPv6，第一优先在 mihomo 配置关 `ipv6`</span>：
   ```bash
   # 查看当前 ipv6 运行时状态
   curl http://127.0.0.1:39798/configs | python -c "import sys,json;print(json.load(sys.stdin).get('ipv6'))"
   # 若为 true：配置文件顶层加 ipv6: false 后热加载
   ```
2. <span style="color:#2980b9">热加载命令（JSON body 用 Python 构造避免转义坑）</span>：
   ```bash
   python -c "import urllib.request,json; req=urllib.request.Request('http://127.0.0.1:39798/configs?force=true',data=json.dumps({'path':r'C:\Users\asus\.config\com.vortex.helper\config.yaml'}).encode(),method='PUT',headers={'Content-Type':'application/json'}); print(urllib.request.urlopen(req).status)"
   ```
3. 若日后需要 IPv6（访问 IPv6-only 站点），可在 Vortex 界面开回 `ipv6: true`，但需接受 ChatGPT 可能再触发 CF IPv6 风控的风险。
4. 备份文件 `vortex-config-20260811-2047-before-ipv6-fix.yaml` 保留在 FAQ 原始文件备份目录，确认稳定后可清理。
5. 本次与 20:40 的 direct 模式故障是**先后两个独立问题**：先修 direct（05 档案复发记录），再修 IPv6 风控（本文档）。若 GPT 仍打不开，检查是否叠加了 `订阅更新清规则`（见 06 档案）。

## 🔗 相关笔记与附件

- [[04-Codex桌面端反复重新连接（公司环境）]] — **IPv4 出口被 CF 风控**档案：节点速查表、美国-IEPL 02 / 美国-直连放行节点；本文档是其 IPv6 变体
- [[05-Codex网络故障-青旅环境]] — 青旅 direct 模式故障档案；20:40 已补充本次 IPv6 风控前的复发记录
- [[06-国外网站访问慢但Codex正常]] — 分流规则档案：OpenAI 域名走美国节点、MATCH 走快节点；含"订阅更新清规则"反复复发记录
- [[08-Edge浏览器Secure DNS导致ChatGPT解析慢]] — 浏览器 DoH 导致的 ChatGPT 访问问题（慢），与本篇（IPv6 风控打不开）可叠加
- 备份：`知识库FAQ/原始文件备份/vortex-config-20260811-2047-before-ipv6-fix.yaml`
