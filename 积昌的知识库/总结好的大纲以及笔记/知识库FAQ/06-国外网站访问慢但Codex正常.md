---
title: "国外网站访问慢但 Codex 正常：代理分流（OpenAI 专用节点 vs 浏览快节点）"
type: "知识库 FAQ / 报错修复"
date: 2026-08-07
created: 2026-08-07
updated: 2026-08-13
environment: "🏠 公寓/家中"
tags:
  - Codex
  - 网络故障
  - 国外网站
  - Vortex
  - mihomo
  - 分流
  - 延迟
  - 节点
  - 公寓
source: "2026-08-07 凌晨本机实测 + Vortex 控制 API 诊断 + 分流配置修复"
---

# 🌐 国外网站访问慢但 Codex 正常（公寓环境）

> [!summary] 📊 报错统计速览（截至 2026-08-13）
> 🔥 **本文档共记录 <span style="color:#e74c3c">7 次报错/复发事件</span>**（2026-08-07 原始事件 1 次 + 复发 6 次）。高频根因为 **「订阅更新清 OpenAI 分流规则」**（本文档 3 次）与 **「节点质量波动 / 机场线路故障」**（本文档 3 次）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 国外网站访问慢（浏览器需快节点分流） | **1** | 06 |
> | 🔴 订阅更新清 OpenAI 分流规则 | **13** | 04（为主）/ 05 / 06 |
> | 🟠 节点质量波动 / 机场线路故障 | **4** | 04 / 05 / 06 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!SUMMARY] 📌 结论摘要
> 浏览器打开国外网站（YouTube/Google/GitHub 等）**延迟大、加载慢**，但 Codex 桌面端一切正常。诊断发现：系统代理（Vortex `127.0.0.1:7897`）正常工作、`mode: rule`、节点为 <span style="color:#2980b9">🇺🇸 美国-IEPL 02</span>，但该节点是**为 ChatGPT/Codex 风控放行而手动固定的"保 Codex 节点"**，真实到站延迟 500ms+、吞吐极低（下载 859KB 要 10s），浏览器重页面加载被拖垮；Codex 走轻量流式 API + 长连接，天然容忍这种延迟，所以"正常"。修复方式是**代理分流**：<span style="color:#e74c3c">OpenAI/ChatGPT 域名仍走美国-IEPL 02（保住 Codex），其余国外流量改走 🇭🇰 香港-中转 01 快节点</span>，浏览器提速 2~5 倍。<span style="color:#ff8c00">顺带修复了配置文件中 `mode: direct` 的隐患（重启会退回 direct 模式导致全断网）。</span>

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
| 记录时间 | 2026-08-07 01:56（Asia/Shanghai） |
| 网络环境 | 🏠 **公寓/家中**（以太网，网关 `192.168.0.1`；WLAN 2 DNS `8.8.8.8`/`114.114.114.114`） |
| 现象 | 浏览器打开国外网站延迟大、加载慢；**Codex 桌面端正常使用** |
| 应用 | Windows 版 Codex 桌面端（正常）+ 系统浏览器（慢） |
| 代理 | Vortex（mihomo 1.10.0），mixed-port `7897`，控制 API `127.0.0.1:39798` |
| 配置路径 | `C:\Users\asus\.config\com.vortex.helper\config.yaml` |
| 系统代理 | 已启用 → `127.0.0.1:7897` |
| 当前节点 | 🇺🇸 美国-IEPL 02（出口 `38.45.155.83`）——<span style="color:#ff0000">保 Codex 专用节点</span> |
| 关键证据 | curl 走代理测 YouTube：TTFB 1.08s、总耗时 10.26s；节点实测到 YouTube 519ms vs 香港节点 280ms |
| 最终状态 | <span style="color:#1e90ff">已修复（分流：OpenAI→美国节点，其余→香港快节点）</span> |

<span style="color:#ff0000">现象本质：</span>不是"打不开"，而是"每个请求都要 1~2s 甚至更久"——页面几十个资源并发，体感就是**卡到爆**。Codex 只发少量 JSON、走长连接、流式返回，所以无感。

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 路由层 | <span style="color:#ff0000">所有国外流量（浏览器+Codex）都走了 🇺🇸 美国-IEPL 02 一个节点</span> | 规则兜底 `MATCH → 节点选择`，节点选择当前=美国-IEPL 02；活动连接 29 条全部经该节点 | 分流：OpenAI 系→美国节点，其余→香港快节点 |
| 线路层 | <span style="color:#ff0000">美国-IEPL 02 到站延迟高、吞吐低</span> | curl 走代理测 YouTube：TTFB 1.08s、总耗时 10.26s（≈95KB/s）；节点实测到 YouTube 519ms | 浏览器流量改走香港-中转 01（实测 58~280ms） |
| 配置层 | <span style="color:#ff8c00">配置文件 `mode: direct`，仅运行中被 API 改成 `rule`</span> | config.yaml 第 4 行 `mode: direct`；运行态 `/configs` 返回 `rule` | 改回 `mode: rule`，**重启不再退回 direct** |
| 认知层 | "美国-IEPL 02 快"是从 ChatGPT 风控角度选出的**唯一放行节点**，≠浏览快节点 | FAQ 04/05 节点速查表 | 明确"保 Codex 节点"与"浏览快节点"是两个诉求，需分流 |

> [!IMPORTANT] ⚠️ 关键认知
> **"Codex 能用" ≠ "节点快"**。美国-IEPL 02 是机场里唯一过 Cloudflare 风控、能放行 ChatGPT 的节点（见 [[04-Codex桌面端反复重新连接（公司环境）]] 的节点速查表），它**慢**——只是 Codex 的流量形态（轻量 JSON + 长连接 + 流式）恰好对它不敏感。浏览器是"重页面多资源"流量，同一个慢节点就把页面加载拖垮。所以**不能简单换快节点**（换了 Codex 会被 CF 403），正确做法是**按域名分流**。

## 🔬 三层诊断数据

### 1. 代理配置层（先排除"隧道没建立"）

复用 [[05-Codex网络故障-青旅环境]] 的方法，查 Vortex 控制 API（`http://127.0.0.1:39798`）：

```json
// GET /configs
{ "mode": "rule", "mixed-port": 7897, "tun": { "enable": false } }

// GET /proxies/节点选择
{ "now": "🇺🇸|美国-IEPL 02" }
```

- ✅ `mode: rule` —— 不是 direct，隧道在（与 05 的故障不同）
- ✅ 节点 = 美国-IEPL 02（与 FAQ 推荐一致）
- ⚠️ 但**配置文件** `config.yaml` 里是 `mode: direct` —— 运行时靠 API 撑在 rule，**一重启就崩**（历史遗留隐患）

规则兜底 `- MATCH, 节点选择`：所有未被直连规则命中的国外流量 → 节点选择 → 美国-IEPL 02。

### 2. 网络层（节点延迟与吞吐实测）

**活动连接分布**（`/connections`，102 条）：73 条 DIRECT + **29 条 `🇺🇸 美国-IEPL 02 > 节点选择`**。走该节点的宿主包含浏览器后台（canva/microsoft/google 等）**和** Codex（chatgpt.com、ws.chatgpt.com）——证实浏览器流量确实走了代理且共用美国节点。

**curl 走代理拆解（YouTube，859KB）**：

| 指标 | 修复前 | 修复后 |
|---|---|---|
| TTFB（首字节） | 1.08s | 0.39s |
| 总耗时 | **10.26s** | **0.74s** |
| 吞吐估算 | ≈95KB/s | ≈2.4MB/s |

> 💡 慢在**下载吞吐**而非纯延迟：TTFB 1s 可忍，但下载 859KB 花了 9s，页面几十个资源必然卡死。

**候选节点 → 真实站点延迟体检**（mihomo `/proxies/{name}/delay`）：

| 节点 | →gstatic(generate_204) | →YouTube | 判定 |
|---|---|:---:|---|
| 🇺🇸 美国-IEPL 02（原） | 198ms | **519ms** | 慢 |
| 🇭🇰 香港-中转 01 | 58ms | **280ms** | <span style="color:#1e90ff">快</span> |
| 🇭🇰 香港-IEPL 01 | 51ms | 516ms | 快(轻请求) |
| 🇯🇵 日本-IEPL 02 | 101ms | 353ms | 较快 |
| 🇹🇼 台湾家宽-IEPL 01 | 142ms | 399ms | 较快 |

**香港-中转 01 多站点确认**（78~271ms，全部达标）：Google 78ms、YouTube 167ms、Wikipedia 98ms、GitHub 99ms、X 271ms、Bing 160ms、Microsoft 97ms。

**美国-IEPL 02 对 OpenAI API**（250~280ms，全部放行）：`codex/models` 270ms、`codex/responses` 277ms、`api.openai.com/v1/models` 251ms。

### 3. 环境层

- 系统代理已启用：`ProxyEnable=1`、`ProxyServer=127.0.0.1:7897`（WinINET 注册表）——浏览器默认走它
- Vortex 进程 `com.vortex.helper`（PID 13460）监听 `7897` 与 `39798`
- DNS：以太网 `192.168.0.1`、WLAN 2 `8.8.8.8/114.114.114.114`；Vortex 内置 fake-ip（`198.18.0.1/16`）+ DoH（alidns/doh.pub），DNS 无污染

## 🛠️ 修复过程

1. **查 FAQ 命中**：04/05 已记录"Codex 故障"两类（DNS 污染、出口风控、direct 模式），但"浏览器慢而 Codex 正常"是**新症状**，根因（共用一个慢速保 Codex 节点）未记录 → 走完整诊断后**新建文档**。
2. **备份配置**：复制 `config.yaml` → `总结好的大纲以及笔记/知识库FAQ/原始文件备份/vortex-config-20260807.yaml`。
3. **确认隧道正常**：`/configs` mode=rule、节点=美国-IEPL 02 → 排除 direct/隧道问题。
4. **节点体检**：批量 delay 测试发现美国节点到 YouTube 519ms、香港-中转 01 仅 280ms → 定位"节点慢"。
5. **修改 `config.yaml`**（已备份）：
   - `mode: direct` → <span style="color:#1e90ff">`mode: rule`</span>（修重启隐患）
   - 在 `GEOIP, CN, DIRECT` 之前新增 OpenAI/ChatGPT 专用规则：
     ```yaml
     - DOMAIN-SUFFIX,openai.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,chatgpt.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,chatgpt-api.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,oaistatic.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,oaiusercontent.com,🇺🇸|美国-IEPL 02
     ```
   - 兜底 `- MATCH, 节点选择` → <span style="color:#1e90ff">`- MATCH, 🇭🇰|香港-中转 01`</span>
6. **热加载**：`PUT /configs?force=true` body=`{"path":"C:\\Users\\asus\\.config\\com.vortex.helper\\config.yaml"}`，返回 **HTTP 204**（成功）。
   - 踩坑：第一版 MATCH 写成 `香港-中转 01`（漏了国旗前缀 `🇭🇰|`），报 `proxy [香港-中转 01] not found`；改为完整代理名 `🇭🇰|香港-中转 01` 后加载成功。

> [!NOTE] 💡 为什么只加 5 条 OpenAI 规则就够了
> `DOMAIN-SUFFIX,openai.com` 已覆盖 `api.openai.com`、`chat.openai.com`、`auth.openai.com` 及所有 `*.openai.com`；`DOMAIN-SUFFIX,chatgpt.com` 覆盖 `chatgpt.com`、`ws.chatgpt.com`、`ab.chatgpt.com` 等全部 `*.chatgpt.com`。Codex 用到的域名都在内。

## ✅ 验证结果

**规则已生效**（`/rules`）：

```text
63 | DomainSuffix | openai.com         | 🇺🇸|美国-IEPL 02
64 | DomainSuffix | chatgpt.com        | 🇺🇸|美国-IEPL 02
65 | DomainSuffix | chatgpt-api.com    | 🇺🇸|美国-IEPL 02
67 | DomainSuffix | oaiusercontent.com | 🇺🇸|美国-IEPL 02
68 | GeoIP        | cn                 | DIRECT
69 | Match        |                    | 🇭🇰|香港-中转 01
```

**走代理实测（分流后）**：

| 站点 | 修复前 | 修复后 | 结论 |
|---|---|---|---|
| YouTube | 1.12s / 总 10.26s | **0.41s** / 总 0.74s | ✅ 大幅提速 |
| Wikipedia | 1.48s | **0.65s** | ✅ |
| GitHub | 2.65s | **0.47s** | ✅ |
| Google | 2.13s（429） | **1.02s（200）** | ✅ 不仅提速还脱离限流 |
| `chatgpt.com/backend-api/codex/models` | 2.13s（401） | **2.13s（401）** | ✅ 仍走美国节点、CF 放行 |

- [x] `/configs.mode` = `rule`（运行态 + 配置文件均已修复）
- [x] OpenAI 域名规则 → 美国-IEPL 02，Codex 关键端点仍返回 401（放行）
- [x] 其余国外流量 → 香港-中转 01，YouTube/GitHub/Google 提速 2~5 倍
- [x] 配置热加载成功（HTTP 204），无需重启 Codex / Vortex

> [!note] ℹ️ 关于 Codex 端点 401
> `codex/models` 返回 **401（未认证）** 是**正常放行**的信号（请求到达了 OpenAI 后端，只是没带 Token）；若被 CF 风控会返回 **403 拦截页（cf-ray）**。分流后 Codex 流量仍走美国节点，401 保持不变 → Codex 不受影响。

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| 代理分流（split routing） | 按域名/规则把不同流量送到不同节点：OpenAI 系走美国节点（防风控），其他国外流量走香港节点（求快） |
| 保 Codex 节点 | 机场里唯一能通过 Cloudflare 风控放行 ChatGPT 的节点（美国-IEPL 02）；它慢但 Codex 能用 |
| 浏览快节点 | 延迟低、吞吐高的节点（香港-中转 01）；浏览器重页面加载需要它 |
| TTFB | Time To First Byte，从发请求到收到第一个字节的时间；越高越"转圈圈" |
| `MATCH` 兜底规则 | mihomo 规则列表最后一条，所有未被前面规则命中的流量走这里 |
| 热加载 | 不重启进程，通过控制 API 重读配置文件（`PUT /configs?force=true`） |
| 出口 IP 风控 | Cloudflare 对数据中心出口 IP 拦截（403），需换"干净"节点绕过；见 [[04-Codex桌面端反复重新连接（公司环境）]] |
| fake-ip | mihomo 内置 DNS 模式，返回 `198.18.x.x` 虚拟地址由代理接管，避免本地 DNS 污染 |

## 🛡️ 后续建议与遗留事项

1. <span style="color:#ff8c00">浏览器再慢时，先看当前兜底节点是谁</span>：`curl http://127.0.0.1:39798/rules` 看最后一条 `Match` 的目标；若被改回慢节点，按本档把 `MATCH` 指回 `🇭🇰|香港-中转 01`。
2. <span style="color:#ff8c00">"节点选择"策略组当前已不被兜底规则引用</span>（MATCH 直指香港-中转 01）。若你想在 Vortex 界面里手动换"浏览节点"，需要改配置文件里 `- MATCH, ...` 的目标（或把兜底改回 `节点选择` 并手动把节点选择选到快节点）。
3. <span style="color:#ff0000">配置文件 `mode: direct` 是历史遗留雷</span>：本次已改回 `rule`。若之后 Vortex 大版本更新重写配置，注意复查 `mode` 是否为 `rule`（这是 05 档案里"被切 direct 全断网"的根源）。
4. 机场订阅更新可能增删节点：若"香港-中转 01"下线，用 `GET /proxies/节点选择` 列节点，再 `GET /proxies/{节点}/delay?url=https://www.youtube.com` 挑一个快节点改 MATCH。
5. Google 若返回 429 限流：香港数据中心 IP 被 Google 频率限制属正常，不影响 YouTube/ChatGPT 等；重度用 Google 可考虑日本节点，但要接受其延迟略高于香港。
6. Codex 再报 `stream disconnected`：先查是否出口 IP 被风控（`curl -x http://127.0.0.1:7897 -I https://chatgpt.com` 出现 403/cf-ray 即风控），按 [[04-Codex桌面端反复重新连接（公司环境）]] 切节点——与本文档的"浏览器慢"是两类不同故障。

## 🔁 复发记录（2026-08-08）：ChatGPT 连不上——分流规则被订阅更新清除

> [!summary] 📌 复发摘要
> 2026-08-08 19:56 用户反馈"ChatGPT 又连不上了"。诊断发现：**上次（08-07）加进 `config.yaml` 的 5 条 OpenAI 分流规则被机场订阅更新整体回退清除**，配置文件的 `mode` 也被还原成 `direct`（运行态仍为 rule、TUN 开，故浏览器"能上网但 ChatGPT 打不开"）。ChatGPT 流量因此掉进兜底 `MATCH → 节点选择`，而节点选择当时指向 🇸🇬 **新加坡-IEPL 02**——该节点过不了 Cloudflare 风控，走代理 curl `chatgpt.com` 报 **SSL 错误（exit 35）**。按本文档既有方案重建分流规则 + 改回 `mode: rule` + 热加载后，ChatGPT 恢复（浏览器 UA 首页 200、`codex/models` 401）。

### 现象与复现

- 现象：ChatGPT 网页/客户端连不上，但其他国外网站（YouTube/Google 等）基本能开。
- 复现证据：`curl -x http://127.0.0.1:7897 https://chatgpt.com/` → exit 35、HTTP 000、5s 超时（SSL UNEXPECTED_EOF 类）。

### 根因分析（与 08-07 首发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 分流规则 | **08-07 加的 5 条 OpenAI 规则被订阅更新清除** | `/rules` 只剩 65 条、无 openai/chatgpt 规则；config.yaml rules 段回到 `MATCH, 节点选择` |
| 节点 | 节点选择 = 🇸🇬 新加坡-IEPL 02（非保 Codex 节点） | `GET /proxies/节点选择` → `now: 🇸🇬|新加坡-IEPL 02` |
| 配置持久化 | 文件 `mode: direct`（运行态 rule，重启会崩） | config.yaml 第 4 行 `mode: direct` |
| 运行态 | mode=rule、TUN 开、端口 7897 | `GET /configs` 正常 |

> [!warning] ⚠️ 核心认知
> 本次与 08-07 首发**症状不同**：首发是"浏览器慢但 Codex 正常"（节点慢），本次是"ChatGPT 连不上但其他国外网站基本能开"（**分流规则消失 + 节点选错**）。共同点都是 `config.yaml` 被外部改动：首发是 `mode` 被改 direct，本次是**整个 rules 段被回退**。**机场订阅更新会重写 config.yaml**，是反复复发的高危诱因。

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260808.yaml`。
2. **改配置**（沿用本文档 08-07 方案）：
   - `mode: direct` → `mode: rule`；
   - `GEOIP, CN, DIRECT` 前加 5 条：
     ```yaml
     - DOMAIN-SUFFIX,openai.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,chatgpt.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,chatgpt-api.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,oaistatic.com,🇺🇸|美国-IEPL 02
     - DOMAIN-SUFFIX,oaiusercontent.com,🇺🇸|美国-IEPL 02
     ```
   - 兜底 `- MATCH, 节点选择` → `- MATCH, 🇭🇰|香港-中转 01`。
3. **热加载**：`PUT http://127.0.0.1:39798/configs?force=true` body=`{"path":"C:\\Users\\asus\\.config\\com.vortex.helper\\config.yaml"}` → **HTTP 204**。
   - ⚠️ 踩坑：bash 里反斜杠转义易出错，报 `Body invalid`（400）；改用 Python `urllib` + `json.dumps` 构造 body 后成功。

### 验证结果

| 验证项 | 结果 |
|---|---|
| `GET /rules` | 70 条；openai.com/chatgpt.com/chatgpt-api.com/oaistatic.com/oaiusercontent.com → 🇺🇸美国-IEPL 02；`MATCH` → 🇭🇰香港-中转 01 |
| 浏览器 UA 访问 `chatgpt.com/` | **HTTP 200**（1.98s） |
| `chatgpt.com/backend-api/codex/models` | **HTTP 401** + CF-RAY `a27e5a73fa6b16df-LAX`（放行正常） |
| 配置文件 `mode` | `rule`（持久化，重启不回退） |

> [!note] ℹ️ 关于首页 403
> 无浏览器 UA 的 curl 访问 `chatgpt.com/` 首页返回 403，是 Cloudflare 对落地页的机器人指纹拦截，**不是**出口 IP 风控——以 `codex/models` 返回 401 为准（FAQ 05/06 一致判据）。浏览器/客户端实际使用不受影响。

### 本次新增遗留事项

1. <span style="color:#ff0000">机场订阅更新会重写 `config.yaml` 并清除自定义规则</span>——复发高发点。若再次出现"ChatGPT 连不上但其他国外网站能开"，**先查 `/rules` 里有没有 openai/chatgpt 规则**：没有就按本复发记录重建分流规则。
2. 建议后续：若 Vortex 支持"订阅更新合并自定义规则"或"保留 rules 覆盖段"，优先开启；否则把本文档的 5 条规则 + `mode: rule` + `MATCH` 方案存为一份可复用的补丁片段，方便快速重建。
3. 配置文件备份已更新至 `vortex-config-20260808.yaml`（修复后版本为运行态）。

## 🔁 复发记录（2026-08-08 22:20）：兜底节点「香港-中转 01」线路下线，全站国外流量断连

> [!summary] 📌 复发摘要
> 2026-08-08 22:20 用户反馈"ChatGPT 打不开了"。诊断发现：**本次与 19:56 复发不同**——5 条 OpenAI 分流规则与 `mode: rule` 均完好，ChatGPT 域名走美国-IEPL 02 实测 HTTP 200 / `codex/models` 401（正常放行）；真正的故障是 **机场批量下线了中转/直连线路**，兜底节点「🇭🇰 香港-中转 01」延迟测试报错、不可用，导致所有未命中 OpenAI 规则的外网流量（Google/YouTube/GitHub/Wikipedia 等）全部 SSL 握手失败（curl exit 35 / HTTP 000），浏览器体感"国外网全断"→ 表现为"ChatGPT 打不开"。将兜底 `MATCH` 换到当前最快可用节点「🇭🇰 香港-IEPL 03」（实测 88ms）并热加载后，全站恢复。

### 现象与复现

- 现象：ChatGPT 网页打不开/转圈，其他国外网站（Google/YouTube/GitHub/Wikipedia）同样打不开。
- 复现证据（走代理 7897，浏览器 UA）：
  - `chatgpt.com/` → **HTTP 200**（说明 ChatGPT 主域名实际能通）
  - `chatgpt.com/backend-api/codex/models` → **HTTP 401**（正常放行，未风控）
  - `www.google.com/` → **exit 35 SSL 握手失败 / HTTP 000**
  - `www.youtube.com/`、`github.com`、`www.wikipedia.org/` → **exit 35 SSL 握手失败 / HTTP 000**

### 根因分析（与 19:56 复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 节点层 | **兜底节点「🇭🇰 香港-中转 01」线路下线**，代理隧道建立失败 | `GET /proxies/{香港-中转 01}/delay` → `An error occurred in the delay test` |
| 规则层 | OpenAI 5 条分流规则 **完好**（未像 19:56 那样被订阅更新清除） | `/rules` 尾段：openai.com/chatgpt.com/chatgpt-api.com/oaistatic.com/oaiusercontent.com → 🇺🇸 美国-IEPL 02 |
| 配置层 | `mode: rule`（运行态+配置文件均正常） | `/configs` mode=rule；config.yaml 第 4 行 `mode: rule` |
| 故障放大 | 「节点选择」策略组指向 🇸🇬 新加坡-IEPL 02（FAQ 已知坏线路） | `GET /proxies/节点选择` → now = 🇸🇬 新加坡-IEPL 02（延迟测试同样报错） |

> [!warning] ⚠️ 核心认知
> **"ChatGPT 主域名能通" ≠ "ChatGPT 能正常打开"**：OpenAI 5 个域名被规则固定走美国-IEPL 02（未受本次故障影响），但 ChatGPT 页面内的第三方资源、以及浏览器同时打开的其他国外站点全部走兜底节点；兜底一挂，整体体感就是"打不开"。**排查 ChatGPT 类故障不能只看 OpenAI 域名是否放行，还要验证兜底 MATCH 节点是否可用。**

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260808-2220.yaml`（17,001 字节）。
2. **节点体检**（`/proxies/{name}/delay?url=gstatic/generate_204`）：
   - 已挂：🇭🇰 香港-中转 01/02、香港-直连、香港家宽-IEPL、🇯🇵 日本-中转 01、🇺🇸 美国-中转 01、🇸🇬 新加坡-IEPL 02 → 全部 `ERR`
   - 可用：🇭🇰 香港-IEPL 03 **88ms**、香港-IEPL 01 90ms、🇹🇼 台湾-IEPL 01 121ms、🇯🇵 日本-IEPL 02 126ms、🇺🇸 美国-IEPL 01 250ms、美国-IEPL 02 217ms
3. **改配置**：`- MATCH, 🇭🇰|香港-中转 01` → `- MATCH, 🇭🇰|香港-IEPL 03`（其余 5 条 OpenAI 规则与 `mode: rule` 保持不动）。
4. **热加载**：`PUT /configs?force=true` body=`{"path":"C:\\Users\\asus\\.config\\com.vortex.helper\\config.yaml"}` → **HTTP 204**。
5. **切节点选择**：`PUT /proxies/节点选择 {"name":"🇭🇰|香港-IEPL 03"}` → **HTTP 204**（把 19:56 后 Vortex 自动切到的坏线路新加坡-IEPL 02 拨正）。

### 验证结果

| 站点/端点 | 修复前 | 修复后 |
|---|---|---|
| chatgpt.com 首页 | 200（2.5s） | **200** |
| codex/models | 401（放行） | **401（放行）** |
| Google | exit 35 / 000 | **302** |
| YouTube | exit 35 / 000 | **200** |
| GitHub | exit 35 / 000 | **200** |
| Wikipedia | exit 35 / 000 | **200** |

- [x] `MATCH` → 🇭🇰 香港-IEPL 03（`/rules` 确认）
- [x] OpenAI 5 域名仍 → 🇺🇸 美国-IEPL 02（未受影响）
- [x] `/configs.mode` = rule
- [x] 「节点选择」now = 🇭🇰 香港-IEPL 03

### 本次新增遗留事项

1. <span style="color:#ff0000">机场节点变更频繁（中转/直连系列批量下线，仅 IEPL 系列存活）</span>——本次香港-中转 01 下线即为此类。**以后再遇"国外网全断但 ChatGPT 主域名能通"**，先 `GET /proxies/{兜底节点}/delay` 体检兜底节点，挂了就换可用 IEPL 节点。
2. 「节点选择」会被 Vortex「自动节点」自动切到测速优的坏线路（本次又切回新加坡-IEPL 02）——若 Vortex 界面里节点选择被自动改，注意拨回可用节点。
3. 配置备份已更新至 `vortex-config-20260808-2220.yaml`（修复后版本为运行态）。
4. 建议把「兜底节点可用性体检」加入日常巡检：浏览器卡国外网时先看 `/rules` 最后一条 `Match` 目标是谁、该节点 delay 是否报错。

## 🔁 复发记录（2026-08-09 00:28）：外网全断——订阅更新清除规则 + 节点选择切到坏线路

> [!summary] 📌 复发摘要
> 2026-08-09 00:28 用户反馈"不能正常访问外网"。诊断发现：**08-08 22:20 修复后的分流配置再次被机场订阅更新整体回退**——5 条 OpenAI 分流规则消失（`/rules` 回到 65 条出厂版、末尾 `MATCH → 节点选择`），配置文件 `mode` 又被还原成 `direct`（运行态仍为 rule，重启会崩）；同时「节点选择」被 Vortex 自动切到 🇸🇬 **新加坡-IEPL 02**（FAQ 已知坏线路，delay 503）。兜底走坏线路导致**全站外网断连**：走代理实测 Google/YouTube/ChatGPT/GitHub 全部 **HTTP 000**。按本文档既有方案重建分流规则 + `mode: rule` + 兜底改 🇭🇰 香港-IEPL 03 + 热加载 + 拨正节点选择后，全站恢复（Google 302 / YouTube 200 / ChatGPT 200 / codex/models 401）。

### 现象与复现

- 现象：浏览器无法访问任何国外网站（Google/YouTube/ChatGPT/GitHub/Wikipedia 全部打不开）。
- 复现证据（走代理 7897，浏览器 UA）：`www.google.com` / `www.youtube.com` / `chatgpt.com` / `github.com` → **HTTP 000**（连接失败）。

### 根因分析（与 08-08 两次复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 分流规则 | **5 条 OpenAI 规则再次被订阅更新清除**（规则回 65 条出厂版） | `/rules` 总数 65、无 openai/chatgpt 规则；config.yaml rules 段回到 `MATCH, 节点选择` |
| 节点层 | **「节点选择」被切到 🇸🇬 新加坡-IEPL 02（坏线路）**，兜底流量全部经它 | `GET /proxies/节点选择` → now = 🇸🇬 新加坡-IEPL 02；该节点 delay 测试 **503** |
| 配置持久化 | 文件 `mode: direct`（运行态 rule，重启会崩） | config.yaml 第 4 行 `mode: direct` |
| 运行态 | mode=rule、TUN 关、端口 7897 | `GET /configs` 正常 |

> [!warning] ⚠️ 核心认知
> 本次是 **08-08 19:56（订阅清除规则）与 08-08 22:20（兜底节点下线）两种故障的叠加复发**：既没有 OpenAI 规则，兜底节点又指向坏线路新加坡-IEPL 02 → 外网全断。**Vortex「自动节点」会把「节点选择」自动切到测速异常的坏线路（新加坡-IEPL 02 已是第三次出现）**；订阅更新每次都会重写 config.yaml 清掉自定义规则。这两个因素叠加，是"外网全断"的高频根因。

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260809.yaml`（16,708 字节）。
2. **节点体检**（`/proxies/{name}/delay`）：新加坡-IEPL 02、香港-中转 01/02 全部 **503 下线**；美国-IEPL 02 **206ms**（保 Codex）、香港-IEPL 03 **69ms**、香港-IEPL 01 57ms、日本-IEPL 02 111ms 可用。
3. **改配置**（沿用本文档方案）：
   - `mode: direct` → `mode: rule`；
   - `GEOIP, CN, DIRECT` 前加 5 条 OpenAI 规则 → `🇺🇸|美国-IEPL 02`；
   - 兜底 `- MATCH, 节点选择` → `- MATCH, 🇭🇰|香港-IEPL 03`。
4. **热加载**：`PUT /configs?force=true` body=`{"path":"C:/Users/asus/.config/com.vortex.helper/config.yaml"}` → **HTTP 204**。
5. **拨正节点选择**：`PUT /proxies/节点选择 {"name":"🇭🇰|香港-IEPL 03"}` → **HTTP 204**。

### 验证结果

| 站点/端点 | 修复前 | 修复后 |
|---|---|---|
| Google | HTTP 000 | **302** |
| YouTube | HTTP 000 | **200** |
| chatgpt.com 首页 | HTTP 000 | **200** |
| Wikipedia | HTTP 000 | **200** |
| GitHub | HTTP 000 | **200** |
| codex/models | - | **401**（放行正常，未风控） |

- [x] `/rules` 70 条；5 条 OpenAI 规则 → 🇺🇸 美国-IEPL 02；`MATCH` → 🇭🇰 香港-IEPL 03
- [x] `/configs.mode` = rule（运行态 + 配置文件均已修复，重启不回退）
- [x] 「节点选择」now = 🇭🇰 香港-IEPL 03
- [x] 出口 IP `103.17.98.26`（香港，兜底流量正常出站）

### 本次新增遗留事项

1. <span style="color:#ff0000">「外网全断」已是第三次（08-08 19:56 规则清除 / 08-08 22:20 兜底节点下线 / 08-09 00:28 二者叠加）</span>。**再遇"外网全断"，按固定三步排查**：① `curl -s http://127.0.0.1:39798/rules` 看有无 openai/chatgpt 规则（无→订阅又清了）；② `curl -s http://127.0.0.1:39798/proxies/节点选择` 看 now 是否坏线路（新加坡-IEPL 02 必坏）；③ 兜底 `MATCH` 节点 delay 是否可用。
2. 建议把本文档的 **5 条 OpenAI 规则 + `mode: rule` + `MATCH` 快节点** 存为一份可复用补丁（skill 速记已具备），供订阅更新后快速重建。
3. 配置备份已更新至 `vortex-config-20260809.yaml`（修复后版本为运行态）。

## 🔁 复发记录（2026-08-09 21:04）：ChatGPT 反复"正在重新连接"——订阅再清规则 + 节点切坏线路 + 长连接黏连

> [!summary] 📌 复发摘要
> 2026-08-09 21:04 用户反馈 ChatGPT 界面又开始"正在重新连接"。诊断发现：**08-09 00:28 修复后的分流配置第三次被机场订阅更新整体回退**——5 条 OpenAI 规则再次消失（`/rules` 回 65 条出厂版、末尾 `MATCH → 节点选择`），配置文件 `mode` 又被还原成 `direct`，且 <span style="color:#ff0000">`external-controller` 被订阅重写为 `39797`（运行态仍为 39798）</span>；同时「节点选择」被自动切到 🇸🇬 **新加坡-IEPL 02**（坏线路，gstatic 通但 OpenAI 断流）。ChatGPT 流量掉进兜底走坏线路，<span style="color:#ff8c00">旧 websocket 长连接黏在旧线路反复被断 → 界面持续显示"正在重新连接"</span>。按本文档方案重建分流规则 + `mode: rule` + 兜底换 **🇭🇰 香港-IEPL 01**（原兜底香港-IEPL 03 已下线）+ 热加载 + 拨正节点选择 + 定向关闭黏连的 OpenAI 旧连接后，ChatGPT 恢复（首页 200、codex/models 401、活动连接全部走美国-IEPL 02）。

### 现象与复现

- 现象：ChatGPT（浏览器/客户端）界面反复显示"正在重新连接"，发送消息/刷新都受影响；其他国外网站基本能开。
- 复现证据（走代理 7897，浏览器 UA）：
  - `chatgpt.com/` → **HTTP 403**（修复前；无 OpenAI 规则，走了坏线路）
  - `chatgpt.com/backend-api/codex/models` → **HTTP 401**（能到 OpenAI 后端但线路不稳定）
  - `GET /rules` → 65 条、**无任何 openai/chatgpt 规则**，末尾 `Match → 节点选择`
  - `GET /proxies/节点选择` → `now = 🇸🇬|新加坡-IEPL 02`

### 根因分析（与 08-09 00:28 复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 分流规则 | **5 条 OpenAI 规则第三次被订阅更新清除**（规则回 65 条出厂版） | `/rules` 总数 65、无 openai/chatgpt；config.yaml rules 段回到 `MATCH, 节点选择` |
| 节点层 | **「节点选择」被自动切到 🇸🇬 新加坡-IEPL 02（坏线路）** | `GET /proxies/节点选择` → now = 新加坡-IEPL 02；gstatic delay 92ms 但 OpenAI 流量 SSL 断流/403 |
| 配置持久化 | 文件 `mode: direct` + **`external-controller` 被订阅改成 `39797`** | config.yaml 第 4 行 `mode: direct`、第 6 行 `external-controller: 127.0.0.1:39797`（运行态 39798，两者脱节） |
| 会话层 | <span style="color:#ff8c00">**旧长连接黏在坏线路**（本次新增症状来源）</span> | `/connections` 4 条 chatgpt/openai 连接 `chains = [🇸🇬 新加坡-IEPL 02, 节点选择]`——websocket 反复断→界面"正在重新连接" |
| 兜底节点 | 上次兜底 **香港-IEPL 03 已下线** | `/proxies/{香港-IEPL 03}/delay` 先 504、复测 78ms（间歇性）；香港-IEPL 01 稳定 54ms |

> [!warning] ⚠️ 与 08-09 00:28 复发的区别
> 00:28 是"**外网全断**"（兜底坏线路导致所有外网站全挂）；本次是"**ChatGPT 反复重新连接**"——OpenAI 主域名实际能通（codex/models 401），但 <span style="color:#ff8c00">websocket 长连接黏在坏线路（新加坡-IEPL 02）上反复被重置</span>，UI 表现为"正在重新连接"。**多了一个"长连接黏连"处理步骤**（见 FAQ 04），且订阅重写还改了 `external-controller` 端口（39797/39798 脱节）——这两点都是新信息。

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260809-2104.yaml`（16,708 字节）。
2. **节点体检**（`/proxies/{name}/delay`）：新加坡-IEPL 02 gstatic 92ms（但 OpenAI 断流）；<span style="color:#1e90ff">美国-IEPL 02 226ms（保 ChatGPT）</span>、<span style="color:#1e90ff">香港-IEPL 01 54ms（YouTube 304ms）</span>；香港-IEPL 03 / 香港-中转 01 间歇 504。
3. **改配置**（沿用本文档方案 + 修复端口脱节）：
   - `mode: direct` → `mode: rule`；
   - `external-controller: 127.0.0.1:39797` → `127.0.0.1:39798`（**与运行态对齐，防 Vortex 重启后控制 API 失联**）；
   - `GEOIP, CN, DIRECT` 前加 5 条 OpenAI 规则 → `🇺🇸|美国-IEPL 02`；
   - 兜底 `- MATCH, 节点选择` → `- MATCH, 🇭🇰|香港-IEPL 01`。
4. **热加载**：`PUT /configs?force=true` body=`{"path":"C:/Users/asus/.config/com.vortex.helper/config.yaml"}`（Python urllib + json.dumps 构造，避免 bash 转义坑）→ **HTTP 204**。
5. **拨正节点选择**：`PUT /proxies/节点选择 {"name":"🇭🇰|香港-IEPL 01"}` → **HTTP 204**。
6. **定向关闭黏连旧连接**：`DELETE /connections/{id}` 关闭 5 条 OpenAI 旧连接（4 条黏在新加坡-IEPL 02 + 1 条已在美国-IEPL 02），让客户端按新规则重建 websocket。

### 验证结果

| 站点/端点 | 修复前 | 修复后 |
|---|---|---|
| chatgpt.com 首页 | 403 | **200**（1.96s） |
| codex/models | 401（线路不稳） | **401**（0.99s，稳定放行） |
| YouTube | 依赖兜底（坏） | **200**（0.76s） |
| Google | - | **302**（0.37s） |
| GitHub | - | **200**（0.83s） |

- [x] `/rules` 70 条；5 条 OpenAI 规则 → 🇺🇸 美国-IEPL 02；`MATCH` → 🇭🇰 香港-IEPL 01
- [x] `/configs.mode` = rule（运行态 + 配置文件均已修复，重启不回退）
- [x] `/configs` external-controller = 39798（与运行态一致）
- [x] 「节点选择」now = 🇭🇰 香港-IEPL 01
- [x] 定向关闭旧连接后，活动连接 `chatgpt.com → [🇺🇸 美国-IEPL 02]`（websocket 重建成功）

### 本次新增遗留事项

1. <span style="color:#ff0000">「订阅清除规则 + 节点切坏线路」已是第 4 次复发（08-08 19:56 / 08-08 22:20 / 08-09 00:28 / 08-09 21:04）</span>。再遇 ChatGPT 类故障，按固定排查四步：① `/rules` 有无 openai/chatgpt 规则（无→订阅又清了）；② `/proxies/节点选择` now 是否坏线路（新加坡-IEPL 02 必坏）；③ 兜底 `MATCH` 节点 delay 是否可用；④ `/connections` 有无 OpenAI 连接黏在坏链路上（有→定向 DELETE）。
2. <span style="color:#ff8c00">本次新增：订阅重写还会改 `external-controller` 端口（39797）</span>。若 Vortex 大版本更新/重启后控制 API `39798` 连不上，先查配置文件第 6 行端口是否被改，拨回 39798 再重启。
3. <span style="color:#ff8c00">兜底节点已从 香港-IEPL 03 换成 香港-IEPL 01（54ms）</span>。机场节点变更频繁（中转/直连系列长期下线、IEPL 间歇波动），每次故障都要先体检再定兜底。
4. skill「知识库报错修复」的**分流修复速记里兜底节点仍写 `香港-中转 01`（已长期下线）**，建议更新为"体检后选最快可用 IEPL 节点"（当前 = 香港-IEPL 01），避免下次照抄坏节点。
5. 配置备份已更新至 `vortex-config-20260809-2104.yaml`（修复后版本为运行态）。

## 🔁 复发记录（2026-08-10 00:36）：Codex 卡死——OpenAI 规则指向的「美国-IEPL 02」节点整条死亡

> [!summary] 📌 复发摘要
> 2026-08-10 00:32 用户反馈"Codex 又卡了"。与既往复发**不同**：5 条 OpenAI 分流规则与 Microsoft 直连规则均完好（订阅未清规则），`mode: rule`、兜底香港-IEPL 01 也正常；真正故障是 <span style="color:#ff0000">**保 Codex 节点「🇺🇸 美国-IEPL 02」整条线路死亡**</span>（gstatic delay ERR、走代理 curl chatgpt.com 全 SSL 失败 exit 35 / HTTP 000），而 5 条 OpenAI 规则仍强制所有 ChatGPT 流量走它 → Codex 全部请求失败卡死。批量体检 35 节点仅 **11 存活**，且**存活节点全部对 codex/models 返回 401（放行）**——机场线路已变化，不再只有美国-IEPL 02 能过 Cloudflare。将 5 条 OpenAI 规则改指最快存活放行节点 <span style="color:#1e90ff">「🇯🇵 日本-IEPL 02」（108ms）</span> 并热加载、清理黏在死节点上的 4 条旧 OpenAI 连接后，Codex 恢复（codex/models 401、首页 200、日志无 stream disconnected）。

### 现象与复现

- 现象：Codex 桌面端卡住（发送/响应不工作）；浏览器其他外网正常。
- 复现证据：`curl -x http://127.0.0.1:7897 https://chatgpt.com/backend-api/codex/models` → **exit 35 / HTTP 000**（SSL 握手失败）；`GET /proxies/{美国-IEPL 02}/delay` → **ERR**。

### 根因分析（与 08-08/08-09 复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 规则层 | **5 条 OpenAI 规则完好**（订阅未清），但全部指向已死的美国-IEPL 02 | `/rules` 83 条：openai.com/chatgpt.com/... → 🇺🇸 美国-IEPL 02 |
| 节点层 | <span style="color:#ff0000">**美国-IEPL 02 整条线路死亡**</span>（gstatic delay ERR、chatgpt.com SSL 断流） | delay ERR；走代理 curl chatgpt.com → exit 35 / 000 |
| 连接层 | 4 条 OpenAI 长连接黏在死节点上 | `/connections` chains=`['🇺🇸|美国-IEPL 02']` |
| 配置层 | `mode: rule`、Microsoft 直连规则、兜底香港-IEPL 01 均正常 | `/configs` + `/rules` |

> [!warning] ⚠️ 与既往复发的区别
> 既往（08-08/08-09）：订阅更新清掉 5 条 OpenAI 规则 + 节点选择切到坏线路。本次：**规则在位，但规则指向的"保 Codex 节点"（美国-IEPL 02）自己死了**。排查时若 `/rules` 里 openai/chatgpt 规则都在，**别急着重建规则——先体检规则指向的那个节点是否还活着**（`GET /proxies/{节点}/delay`）。

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260810-codex-prefix.yaml`。
2. **节点体检**：35 节点仅 11 存活（美国-IEPL 01/02 全死、美国-中转 02 存活 230ms；日本-IEPL 02 108ms / 香港-IEPL 01 172ms 等存活）；存活节点批量实测 `codex/models` **全部 401 放行**。
3. **改配置**：5 条 OpenAI 规则目标 `🇺🇸|美国-IEPL 02` → <span style="color:#1e90ff">`🇯🇵|日本-IEPL 02`</span>（最快存活放行节点；Python UTF-8 安全写入）。
4. **热加载**：`PUT /configs?force=true` body=`{"path":"C:/Users/asus/.config/com.vortex.helper/config.yaml"}` → **HTTP 204**。
5. **清理黏连**：DELETE 4 条 chains 含美国-IEPL 02 的 OpenAI 旧连接（chatgpt.com×2、chat.openai.com、ab.chatgpt.com）。
6. **验证 + 观察 Codex 日志**。

### 验证结果

| 验证项 | 修复前 | 修复后 |
|---|---|---|
| codex/models | exit 35 / 000 | **401**（0.68s，放行） |
| chatgpt.com/ 首页 | exit 35 / 000 | **200**（2.36s） |
| `/rules` OpenAI 规则 | → 🇺🇸 美国-IEPL 02（死） | → 🇯🇵 日本-IEPL 02 |
| OpenAI 活动连接 | chains=`['🇺🇸 美国-IEPL 02']` | chains=`['🇯🇵 日本-IEPL 02']` |
| Codex 最新日志 | 卡死 | stream disconnected / 403 / ERR_CONNECTION_RESET 全为 0 |

- [x] `/rules` 83 条；5 条 OpenAI 规则 → 🇯🇵 日本-IEPL 02；MATCH → 🇭🇰 香港-IEPL 01
- [x] `/configs.mode` = rule
- [x] 4 条死节点旧连接已清理，新连接全部走日本-IEPL 02
- [x] Codex 最新日志（00:36）`stream disconnected` / `403` / `ERR_CONNECTION_RESET` 全为 0，会话正常

### 本次新增遗留事项

1. <span style="color:#ff0000">**"规则在但节点死"是新变体**</span>：再遇 Codex 卡，先 `/rules` 看 openai/chatgpt 规则在不在；<span style="color:#ff8c00">在的话立即体检规则指向的节点（`/proxies/{节点}/delay`），别默认是订阅清规则</span>。
2. **节点可用性速查表已过时**：本次实测存活节点（11 个）全部对 codex/models 放行 401，包括 日本-IEPL 02/01、香港-IEPL 01、香港家宽-IEPL、新加坡-IEPL 01、台湾-IEPL 02、美国-中转 02 等——<span style="color:#ff8c00">机场线路已变化，"只有美国-IEPL 02 能过 CF"不再成立</span>。当前 OpenAI 规则指向 = 🇯🇵 日本-IEPL 02（108ms 最快）。
3. 配置备份已更新至 `原始文件备份/vortex-config-20260810-codex-prefix.yaml`（修复前）；`vortex-config-20260810-fixed.yaml` 为含 Microsoft 直连规则的修复后版本。

## 🔁 复发记录（2026-08-10 01:05）：外网进不去——OpenAI 规则残留日本节点，实测对 ChatGPT 403

> [!summary] 📌 复发摘要
> 2026-08-10 01:05 用户反馈"外网又进不去了"。与 00:36 复发**首尾呼应**：00:36 因美国-IEPL 02 整条死亡，把 5 条 OpenAI 规则紧急改指日本-IEPL 02（当时实测最快放行节点）；约 30 分钟后美国-IEPL 02 已恢复（delay 199ms），但运行态规则仍指向日本-IEPL 02，走代理实测 chatgpt.com 返回 <span style="color:#ff0000">403</span>（google/youtube 走 MATCH→香港-IEPL 01 正常）。判定为"OpenAI 规则残留临时切换节点 + 该节点对 ChatGPT 放行状态不可靠（机场线路漂移）"。将 5 条 OpenAI 规则改回 🇺🇸 美国-IEPL 02 并热加载后：chatgpt.com 首页 200（浏览器 UA）、codex/models 401（放行）、google/youtube/wikipedia 全通，修复完成。

### 现象与复现

- 现象：外网"进不去"；浏览器打开 ChatGPT 失败（Codex 关联受影响），google/youtube 正常。
- 复现证据：`/rules` 显示 5 条 OpenAI 规则全部指向 🇯🇵 日本-IEPL 02（00:36 临时切换残留）；走代理 `curl -x 127.0.0.1:7897 https://chatgpt.com` → **403**（0.48s）。`/configs` mode=rule（未被切 direct），排除 05 类故障。

### 根因分析（与 00:36 复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 规则层 | 5 条 OpenAI 规则完好，但目标仍是 00:36 临时切的 🇯🇵 日本-IEPL 02 | `/rules`：openai.com/chatgpt.com/... → 日本-IEPL 02 |
| 节点层 | <span style="color:#ff0000">**日本-IEPL 02 对 ChatGPT 域名实测 403**，美国-IEPL 02 已恢复健康（199ms）</span> | 走代理 chatgpt.com 403；节点 delay 体检全活（美 199 / 日 109 / 港 81ms） |
| 认知层 | <span style="color:#ff8c00">**delay 正常 ≠ 对 ChatGPT 放行**</span>：日本-IEPL 02 delay 109ms 很健康但 chatgpt.com 403；必须实测目标端点 | 00:36 曾验证日本对 codex/models 放行 → 仅 30 分钟后已不可靠，证明机场线路可用性"来回漂移" |

> [!warning] ⚠️ 与既往复发的区别（第三个变体）
> 既往 08-08/08-09：订阅更新**清掉** OpenAI 规则。00:36：规则在但**指向的节点死**（美国死）。本次：规则在、**所有节点 delay 全活，但规则指向的节点对 ChatGPT 实测 403**（日本被 CF 拦）。排查顺序升级为：① `/rules` 看规则在不在、指向谁 → ② 节点 delay 体检是否存活 → ③ **必须走代理实测目标端点（chatgpt.com / codex/models），别只看 delay、别用无浏览器头 curl 下结论**。

### 修复过程

1. **备份**：`config.yaml`（故障态，OpenAI→日本）→ `原始文件备份/vortex-config-20260810-before-fix-openai-jp.yaml`。
2. **节点体检**：四节点全活（美 199 / 日 109 / 港 81 / 台 219ms）→ 排除"节点死"，问题在"放行状态"。
3. **改配置**：5 条 OpenAI 规则目标 `🇯🇵|日本-IEPL 02` → `🇺🇸|美国-IEPL 02`（Python UTF-8 安全写入，与 00:36 方向相反）。
4. **热加载**：`PUT /configs?force=true` body=`{"path":"C:/Users/asus/.config/com.vortex.helper/config.yaml"}` → HTTP 204。

### 验证结果

| 验证项 | 修复前（规则→日本-IEPL 02） | 修复后（规则→美国-IEPL 02） |
|---|---|---|
| chatgpt.com 首页 | 403（curl 无浏览器头） | **200**（浏览器 UA，1.83s） |
| codex/models | —（未单独实测） | **401**（0.88s，放行非风控） |
| google | 302 | 302 ✅ |
| youtube | 200 | 200 ✅ |
| wikipedia | — | 200 ✅ |
| 规则→代理分布 | OpenAI 5 条→日本 | OpenAI 5 条→美国；DIRECT 77；MATCH→香港-IEPL 01 |

- [x] `/rules` 83 条；5 条 OpenAI 规则 → 🇺🇸 美国-IEPL 02；MATCH → 🇭🇰 香港-IEPL 01；无规则指向 节点选择
- [x] `/configs.mode` = rule；系统代理 ProxyEnable=1 / ProxyServer=127.0.0.1:7897
- [x] Microsoft 直连规则完好（实测 12 条 DIRECT）

### 本次新增遗留事项

1. <span style="color:#ff0000">**节点可用性是"来回漂移"态**</span>：00:36 美国死→切日本放行；01:05 美国活、日本对 ChatGPT 403→切回美国。**不要长期迷信任何一个"放行节点"**，机场线路会反复变化。
2. <span style="color:#ff8c00">**delay 正常 ≠ 放行 ChatGPT**</span>：本次日本 delay 109ms 健康但 chatgpt.com 403。排查必须走代理实测目标端点；且用带浏览器 UA 的 curl，避免 curl 指纹被 CF 拦造成误判。
3. 当前 OpenAI 规则指向 = 🇺🇸 美国-IEPL 02（实测 200/401 放行）。若再 403，按"规则在不在→节点活不活→端点实测"三步排查；候选放行节点可复用 00:36 实测的 11 个存活节点（当时对 codex/models 全放行 401）。
4. 配置备份：`原始文件备份/vortex-config-20260810-before-fix-openai-jp.yaml`（故障态）；`vortex-config-20260810-fixed.yaml`（含 Microsoft 直连规则的良好基准，本次修复后与之对齐）。

## 🔗 相关笔记与附件

- [[04-Codex桌面端反复重新连接（公司环境）]] — 🏠 公寓环境 Codex 故障档案：DNS 污染 + 出口 IP 风控 + 节点可用性速查表（美国-IEPL 02 是唯一放行节点，本文档据此分流）
- [[05-Codex网络故障-青旅环境]] — 🏨 青旅环境档案：Vortex 被切 direct 导致隧道未建立；本档沿用了其"查 /configs mode"的排查法
- [Vortex 配置备份（修改前）](原始文件备份/vortex-config-20260807.yaml) — 修复前原始配置，SHA-256 `5505f1ee189531ee24028b2f96447df12069a30f644d7f43d66e90c7f6fd09db`
- [Vortex 配置备份（复发 2026-08-08 修改前）](原始文件备份/vortex-config-20260808.yaml) — 本次复发修复前原始配置（rules 段已回退出厂版）
