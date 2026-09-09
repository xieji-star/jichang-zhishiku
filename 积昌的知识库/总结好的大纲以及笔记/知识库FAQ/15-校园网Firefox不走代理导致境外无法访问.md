---
title: "校园网下浏览器（Firefox）不走系统代理导致境外无法访问"
type: "知识库 FAQ / 报错修复"
date: 2026-08-31
created: 2026-08-31
updated: 2026-08-31
environment: "🏫 校园 WiFi"
tags:
  - 校园网
  - Firefox
  - 系统代理
  - 网络封锁
  - DNS污染
  - 无法访问外网
  - Rocket
source: "2026-08-31 用户报告校园 WiFi 下无法访问外网，本机 Firefox / 小火箭 实测"
---

# 🏫 校园网下浏览器（Firefox）不走系统代理导致境外无法访问

> [!summary] 📊 报错统计速览（截至 2026-08-31）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（原始事件 1 次 + 复发 0 次）。根因为 **「应用不走系统代理（Firefox 默认直连）+ 校园网直接封锁境外站点」**（台账累计 1 次）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 校园网封锁境外 + 应用不走系统代理 | **1** | 15 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!info] 📍 适用环境：🏫 校园 WiFi
> 本文档记录**校园网**（学校/宿舍校园网络）下「能上国内站、打不开境外站」的排查。校园网在**路由器/防火墙层直接封锁境外站点 + 污染 DNS**，因此只剩**走代理**一条出路；而**任何不走系统代理的应用都会连不上境外**。青旅/公寓环境见 [[04-Codex桌面端反复重新连接（公司环境）]]、[[05-Codex网络故障-青旅环境]]、[[06-国外网站访问慢但Codex正常]]。

> [!SUMMARY] 📌 结论摘要
> 用户所在**校园网在防火墙层直接封锁境外域名 + 污染 DNS**（实测直连 `google.com` 超时被拦，`baidu/qq/cloudflare` 直连 200）。而用户的主浏览器 **Firefox 默认不走 Windows 系统代理**（`network.proxy.type=0` 即直连），于是 Firefox 尝试直连境外 → 被校园网拦死 → 表现为「打不开外网」。**小火箭（Rocket/ClashR）代理隧道本身健康**（走 127.0.0.1:4780 实测 google/youtube/github 全 200、api.openai.com 401）。处置：为 Firefox 各 profile 写 `user.js` 强制走代理 `127.0.0.1:4780`，重启 Firefox 后即可访问境外。

## 🧭 快速索引

- 📌 [[#📌 报错概况|报错概况]]
- 🔍 [[#🔍 根因分析|根因分析]]
- 📊 [[#📊 诊断数据|诊断数据]]
- 🔧 [[#🔧 修复过程|修复过程]]
- ⚠️ [[#⚠️ 关键认知|关键认知]]
- 💡 [[#💡 使用建议与遗留事项|使用建议与遗留事项]]

## 📌 报错概况

- **现象**：校园 WiFi 下，浏览器/应用打不开境外站点（Google、YouTube、GitHub 等），但国内站（百度、QQ）正常。
- **报错形态**：境外站在浏览器一直转圈/超时；直连检测 `google.com` 返回 000 超时。
- **关键澄清**：用户明确这是**学校 WiFi**，不是宿舍/青旅。校园网的网络策略与公寓/青旅不同。

## 🔍 根因分析

### 单层根因（本次为「环境 + 工具」两层叠加）

| 层 | 根因 |
|---|---|
| **环境层（校园网）** | 校园网在路由器/防火墙层**直接封锁境外域名 + 污染 DNS**（GFW 式过滤）。实测：直连 `baidu/qq/cloudflare` 200，直连 `google` 10s 超时。无 captive portal（msftconnecttest/generate_204 均 200/204）。 |
| **工具层（Firefox）** | **Firefox 默认不走 Windows 系统代理**：`network.proxy.type=0`（直连）、且不用 PAC/系统代理。因此 Firefox 会**直连**境外 → 被校园网拦死。而 Edge（默认用系统代理）能通。 |

**一句话**：校园网只放行国内、封锁境外；Firefox 又擅自直连；两者叠加 → 境外全打不开。

## 📊 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 环境层 | 认证门户检测（mastconnecttest / google generate_204 直连） | 200 / 204 → **无 captive portal**（不用登录即可上） |
| 环境层 | 直连国内 `baidu.com` / `qq.com` / `cloudflare.com` | **200**（放行） |
| 环境层 | 直连境外 `google.com` | **10s 超时 / 000 被拦**（封锁） |
| 环境层 | DNS 污染 | chatgpt.com / google / api.openai.com 在 223.5.5.5 / 1.1.1.1 / 8.8.8.8 全解析成 Facebook IP |
| 环境层 | 系统代理注册表 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:4780`（指向小火箭）✅ |
| 环境层 | 小火箭进程 | ClashR PID 29676，4780/4781/4788 在听 ✅ |
| 工具层 | 运行中的浏览器 | **Firefox 17 实例**、Edge 15 实例、Chrome 0 |
| 工具层 | Firefox 代理设置 | 各 profile `prefs.js` **无** `network.proxy.type` 行（有效值=0 直连）|
| 网络层 | 走代理 `127.0.0.1:4780` 实测 | google 200 / youtube 200 / github 200 / api.openai.com 401（均可达）✅ |

## 🔧 修复过程

1. **定位**：系统代理正确（4780）、小火箭健康、走代理境外全 200，**唯独 Firefox 打不开境外** → 判定为 Firefox 不走代理，叠加校园网封锁。
2. **改 Firefox**：为全部 3 个 profile 写 `user.js`（优先级最高、重启生效）强制走代理 `127.0.0.1:4780`：
   ```
   user_pref("network.proxy.type", 1);              // 手动代理
   user_pref("network.proxy.http", "127.0.0.1");
   user_pref("network.proxy.http_port", 4780);
   user_pref("network.proxy.ssl", "127.0.0.1");
   user_pref("network.proxy.ssl_port", 4780);
   user_pref("network.proxy.share_proxy_settings", true);
   user_pref("network.proxy.no_proxies_on", "localhost, 127.0.0.1, ::1");
   ```
   Profile 目录：`%APPDATA%\Mozilla\Firefox\Profiles\{53w7d75e.default-release, u38z4dog.default, umie11gt.default-default}\user.js`。
3. **验证**：user.js 各 10 行、`type=1`；Firefox 将走的代理路径实测 google/youtube 200、api.openai.com 401 可达。**重启 Firefox 后生效**。

> [!warning] ⚠️ 关键认知
> **① Firefox 默认不走 Windows 系统代理**：它在 `about:preferences` 里有**独立**代理设置，默认 `network.proxy.type=0`（直连）。所以「系统代理设了 4780」对 Firefox 无效。**Edge/Chrome 默认用系统代理，Firefox 不是。**
> **② 校园网 ≠ 全断，而是「选择性封锁」**：直连国内+Cloudflare 通、境外（google/yt/x）被封、DNS 被污染。所以「国内能上、外网不能上」正是校园网特征，不是代理或路由器坏了。
> **③ 只改系统代理不够，除非走 TUN**：只要网络封锁境外 + 应用直连，任何不走系统代理的应用都连不上。彻底的解法是开启小火箭 **TUN 模式**（透明代理，接管所有流量，含不走系统代理的应用）；本次先做 Firefox 定向修复。
> **④ 境外可达 ≠ 一定打得开**：走代理连境外站点多数 200，但 `chatgpt.com` 可能被 Cloudflare 弹**人机验证 403**（见 [[04-Codex桌面端反复重新连接（公司环境）]] 台账 N12），那是节点 IP 风控，与「连不上」是两码事。

## 💡 使用建议与遗留事项

- **重启 Firefox**（Ctrl+Shift+Q 完全退出后重开）：让 `user.js` 生效；确认后应能打开境外站。
- **遗留**：① 若重启 Firefox 后**仍**打不开某个境外站，告诉我具体站点与报错，我针对性排查；② 若你其它应用（非浏览器）也连不上境外——因为它们不走系统代理——告诉我，我可以开启小火箭 **TUN 模式**一次性接管全部流量；③ `chatgpt.com` 若弹人机验证，先看 [[04-Codex桌面端反复重新连接（公司环境）]] 的 N12（已钉到新加坡 01）。
- **反向确认**：若你**只有 Firefox 打不开境外、Edge 正常**，即 100% 命中本文档根因。

## 🔗 相关笔记

- [[04-Codex桌面端反复重新连接（公司环境）]] · OpenAI 钉死到被 CF 风控节点（台账 N12）
- [[06-国外网站访问慢但Codex正常]] · 国外网站访问慢（浏览器需快节点分流）
- [[08-Edge浏览器Secure DNS导致ChatGPT解析慢]] · Edge Secure DNS
- [[05-Codex网络故障-青旅环境]] · 青旅环境
- [[00-报错统计台账]] · 全局报错统计
