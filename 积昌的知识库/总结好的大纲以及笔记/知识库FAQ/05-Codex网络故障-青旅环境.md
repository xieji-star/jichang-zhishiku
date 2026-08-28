---
title: "Codex 网络故障：青旅环境 Vortex 被切到 direct 模式（隧道未建立）"
type: "知识库 FAQ / 报错修复"
date: 2026-08-06
created: 2026-08-06
updated: 2026-08-15
environment: "🏨 青旅"
tags:
  - Codex
  - ChatGPT
  - 网络故障
  - Vortex
  - mihomo
  - direct模式
  - TUN
  - 青旅
source: "2026-08-06 晚间青旅现场实测 + Vortex 控制 API 诊断"
---

# 🏨 Codex 网络故障：青旅环境（Vortex direct 模式）

> [!summary] 📊 报错统计速览（截至 2026-08-15）
> 🔥 **本文档共记录 <span style="color:#e74c3c">10 次报错/复发事件</span>**（2026-08-06 原始事件 1 次 + 复发 9 次）。高频根因为 **「订阅更新清 OpenAI 分流规则」**（台账累计 17 次，以 04 为主发地；本文档 08-14 20:56 / 08-15 12:31 再复发 2 次）与 **「Vortex 被切 direct 模式」**（台账累计 8 次，本文档/04 各多次）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🟠 青旅公共网络抖动（长连接偶发重建） | **3** | 05 |
> | 🔴 订阅更新清 OpenAI 分流规则 | **17** | 04（为主）/ 05 / 06 |
> | 🔴 Vortex 被切 direct 模式（隧道未建立） | **8** | 05 / 04 |
> | 🟠 节点质量波动 / 机场线路故障 | **4** | 04 / 05 |
> | 🔴 Codex 应用未运行 / AppsFolder 启动命令坑 | **4** | 05 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!SUMMARY] 📌 结论摘要
> 从公寓切换到**青旅**网络后，Codex 再次报 `stream disconnected`。节点虽显示 🇺🇸 美国-IEPL 02（出口 38.45.155.83，与早上相同），但 <span style="color:#ff0000">Vortex 被切到了 `direct` 模式且 TUN 关闭</span>，导致 mixed-port `7897` 收到请求后按 direct 原样放行、**根本没走美国节点隧道**，Google/ChatGPT/Wikipedia 等全部被 GFW 阻断。把模式切回 `rule` 后，代理隧道立即恢复，ChatGPT 端点全部放行。<span style="color:#1e90ff">本次根因不是节点被风控，而是代理客户端自身模式被重置。</span>

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
| 记录时间 | 2026-08-06 20:00（Asia/Shanghai） |
| 网络环境 | 🏨 **青旅**（hostel），与早上的公寓/公司环境不同 |
| 现象 | Codex 报 `stream disconnected before completion`、界面反复重连；浏览器能开 NVIDIA 但 Google/YouTube/ChatGPT 打不开 |
| 应用 | Windows 版 Codex 桌面端 |
| 代理 | Vortex（mihomo 1.10.0），mixed-port `7897`，控制 API `127.0.0.1:39798` |
| 当前节点 | 🇺🇸 美国-IEPL 02（出口 `38.45.155.83`）——与早上一致，未被风控 |
| 关键证据 | `/configs` 返回 <span style="color:#ff0000">`mode: direct` + `tun.enable: False`</span> |
| 最终状态 | <span style="color:#1e90ff">已修复（模式切回 rule，隧道恢复）</span> |

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 代理配置层 | <span style="color:#ff0000">Vortex 被切到 `direct` 模式，TUN 关闭</span> | 控制 API `/configs`：`mode: direct`、`tun.enable: False` | 执行 `PATCH /configs {"mode":"rule"}` 切回规则模式 |
| 网络层 | 直连与走代理结果**几乎一致**（GitHub/NVIDIA/Bing 通；Google/ChatGPT/Wikipedia 全挂） | 逐站对比探测，代理路径返回的失败类型与直连相同（SSL UNEXPECTED_EOF） | 证明 7897 未提供隧道，流量实际全部直连 |
| 环境层 | 青旅网络（双网卡，主路由 `192.168.9.1`，另有一个高 metric 的 `26.0.0.1` 网关） | ipconfig + route print | 列观察项；疑似网络切换时 Vortex 模式被重置 |

> [!IMPORTANT] ⚠️ 关键认知
> **节点显示对 ≠ 隧道建立对。** 本次节点一直是「美国-IEPL 02」，和早上放行的节点完全相同，但模式是 `direct`，所以**代理端口变成了"直连放大器"**——`7897` 只是把请求原样放行到公网，任何需要翻墙的站点（Google/ChatGPT/YouTube/Wikipedia）自然全部失败。排查时必须看 `mode` 和 `tun.enable`，不能只看策略组里选了哪个节点。

## 🔬 三层诊断数据

### 1. 代理客户端层（决定性证据）

Vortex 控制 API（`http://127.0.0.1:39798`）查询结果：

```json
// GET /configs
{
  "mode": "direct",              // ← 致命项：规则模式被切换成直连
  "mixed-port": 7897,
  "tun": { "enable": false }     // ← TUN 关闭，无虚拟网卡接管
}

// GET /proxies/节点选择
{ "now": "🇺🇸|美国-IEPL 02", "type": "Selector" }
```

- `mode: direct` = mihomo 忽略所有分流规则，无论走哪个端口都直连
- `tun.enable: false` = 没有 TUN 虚拟网卡截获流量（早上在公寓时走 TUN 模式，fake-IP 池 `198.18.0.x`）

### 2. 网络层（直连 vs 代理 逐站对比）

用 Python urllib 分别走「直连（ProxyHandler 空）」与「显式代理 `127.0.0.1:7897`」探测 8 个站点（mode=direct 状态下）：

| 站点 | 直连 | 走 7897 代理 | 判定 |
|---|---|---|---|
| GitHub | 200 | 200 | 直连可达（无需代理） |
| NVIDIA | 200 | 200 | 直连可达 |
| Bing | 200 | 200 | 直连可达 |
| OpenAI | 403 | 403 | 直连可达（CF 拦截） |
| Google | FAIL 超时 | **FAIL SSL UNEXPECTED_EOF** | 被 GFW 阻断 |
| ChatGPT | FAIL 超时 | **FAIL SSL UNEXPECTED_EOF** | 被 GFW 阻断 |
| Wikipedia | FAIL 超时 | **FAIL SSL UNEXPECTED_EOF** | 被 GFW 阻断 |
| api.ipify.org | FAIL 连接被拒 | **FAIL SSL UNEXPECTED_EOF** | 出口查询失败 |

> 💡 判读：直连能通的站点走代理也通、直连被 GFW 拦的站点走代理**同样被拦**——两条路径结果几乎一致，说明 <span style="color:#ff8c00">7897 只是把流量放行成直连，根本没有建立到美国节点的隧道</span>。

### 3. 环境层（网卡与路由）

`ipconfig` 显示两块活跃网卡：

| 网卡 | IP | 网关 | 路由 metric | 是否生效 |
|---|---|---|---|---|
| 主 LAN | `192.168.8.248` | `192.168.9.1` | 35 | ✅ 生效（低 metric） |
| 另一适配器 | `26.180.78.16` | `26.0.0.1` | 9257 | ❌ 备选（高 metric） |

`route print -4` 确认默认路由走 `192.168.9.1`（metric 35）。`26.x.x.x` 网关类似热点/运营商 CGNAT 类地址，metrics 高达 9257，暂不影响主流量，但**网络切换本身可能是触发 Vortex 模式被重置的原因**，列观察项。

## 🛠️ 修复过程

1. 先用「直连 vs 代理」逐站对比探测 → 发现两条路径结果一致，怀疑代理隧道未生效。
2. 查询 Vortex 控制 API `/configs` → 拿到决定性证据：<span style="color:#ff0000">`mode: direct`、TUN 关闭</span>。
3. 执行模式切换（mihomo 标准 API）：
   ```bash
   curl -X PATCH "http://127.0.0.1:39798/configs" \
        -H "Content-Type: application/json" -d '{"mode":"rule"}'
   # 返回 HTTP 204（No Content = 成功）
   ```
4. 复核 `/configs`：`mode` 已变回 `rule`；确认 `GLOBAL` → 节点选择 → 美国-IEPL 02 链路未变。
5. 重新探测外网与 ChatGPT 关键端点（结果见「✅ 验证结果」）。
6. <span style="color:#1e90ff">无需重启 Codex</span>——本次是代理侧路由问题，隧道恢复后客户端连接自然重建。

> [!NOTE] 💡 与早上（公寓）故障的区别
> 早上的根因是 <span style="color:#ff8c00">出口 IP 被 Cloudflare 风控（403 拦截页）</span>，需要换节点；本次根因是 <span style="color:#ff8c00">代理客户端自身模式被切到 direct</span>，不需要换节点——同一个"美国-IEPL 02"从早上到今天始终可用。完整对比见 [[04-Codex桌面端反复重新连接（公司环境）]]（公寓环境档案）。

## ✅ 验证结果

切回 `rule` 模式后，走代理 `7897` 重测：

| 站点/端点 | 结果 | 说明 |
|---|---|---|
| 出口 IP | `38.45.155.83` | ✅ 美国-IEPL 02，与早上一致 |
| chatgpt.com 首页 | HTTP **200** | ✅ 放行 |
| `backend-api/codex/models` | HTTP **401** | ✅ 未认证=正常放行（非 403 风控） |
| YouTube | HTTP 200 | ✅ |
| Wikipedia | HTTP 200 | ✅ |
| Google | HTTP 429 | ⚠️ 限流（数据中心 IP，说明已到达 Google） |
| GitHub / Bing / NVIDIA | HTTP 200 | ✅ |

- [x] `/configs.mode` = `rule`
- [x] 出口 = `38.45.155.83`（美国-IEPL 02）
- [x] ChatGPT 关键端点 `codex/models` 返回 401（放行）
- [x] 无需重启 Codex，客户端可正常使用

> [!note] ℹ️ 关于 TUN 关闭的说明
> 修复后 Vortex 的 <span style="color:#2980b9">TUN（全局接管）仍处于关闭状态，但**不影响 Codex 正常使用**</span>：Codex 通过系统代理 `127.0.0.1:7897` + `rule` 模式即可经由美国节点访问 ChatGPT。TUN 只影响**不认系统代理的程序**；需要全系统自动接管时可手动开启（见「后续建议」第 6 条）。

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| `mode: rule` | mihomo 的规则分流模式：按分流规则决定走代理节点还是直连；**默认应为此模式** |
| `mode: direct` | 直连模式：所有流量一律直连，**忽略分流规则与节点**——本次故障的元凶。⚠️ **direct ≠ 关闭代理客户端**：程序仍连得上 7897，但流量被旁路直连（**VPN 失效**）；切回 `rule` 即恢复隧道 |
| TUN 模式 | 代理创建一张虚拟网卡，从系统层面截获全部流量（fake-IP `198.18.0.x`）；关闭则只对显式设置代理的程序生效 |
| mixed-port | HTTP/SOCKS 混合代理端口（`7897`），程序显式指定代理时走这里 |
| 控制 API | mihomo 提供的本地 HTTP 管理接口（`127.0.0.1:39798`），可查/改配置、切节点 |
| SSL UNEXPECTED_EOF | TLS 握手被对端/中间设备强制断开，GFW 对直连被墙域名时常见此报错 |
| CGNAT | 运营商级 NAT，多个用户共享公网 IP；网关地址如 `26.x.x.x` 非标准私网段 |

## 🛡️ 后续建议与遗留事项

1. <span style="color:#ff8c00">切换网络环境（公寓 ↔ 青旅）后，若 Codex 再报 `stream disconnected`，第一件事先查 Vortex 是否被切到 direct</span>：
   ```bash
   curl http://127.0.0.1:39798/configs   # 看 mode 是否为 rule
   ```
2. 快速修复命令（若 mode=direct）：`curl -X PATCH http://127.0.0.1:39798/configs -H "Content-Type: application/json" -d '{"mode":"rule"}'`
3. <span style="color:#ff8c00">「Vortex 为何自动切到 direct」根因未明</span>：怀疑与网络切换时 Vortex 的配置持久化/自动行为有关，列观察项。若反复出现，考虑在 Vortex 内检查是否有"网络变化时重置模式"的选项，或改用更稳定的启动方式。
4. 青旅网络存在双网卡与高 metric 的 `26.0.0.1` 网关，属异常网络形态；若后续出现"时通时断"，先检查默认路由是否漂移（`route print -4`）。
5. 若切回 `rule` 后 ChatGPT 仍返回 403 拦截页（cf-ray），则是 <span style="color:#ff0000">出口 IP 被风控</span>，按 [[04-Codex桌面端反复重新连接（公司环境）]] 的节点速查表切换节点，与本篇（direct 模式）是两种不同故障，处置不同。
6. <span style="color:#2980b9">TUN 当前关闭不影响 Codex</span>：Codex 走系统代理 `127.0.0.1:7897`，`rule` 模式 + 节点正常即可用。若你希望**浏览器等所有程序**都自动走代理（不依赖各程序是否认系统代理），可在 Vortex 界面开启 TUN（对应 `/configs` 的 `tun.enable: true`）。

## 🔁 复发记录（2026-08-09 22:07）：青旅网络下 Codex 偶发重连，但网络侧三层诊断全通

> [!summary] 📌 复发摘要
> 用户反馈"Codex 又重新连接了"，当前在青旅。三层诊断结果：**代理配置层、网络层、节点层全部健康**——与本次故障（direct 模式）和 06 档案（分流规则被清）都不同。具体证据：`mode: rule`、5 条 OpenAI 分流规则完好、MATCH 兜底→🇭🇰 香港-IEPL 01（84ms）、保 Codex 节点 🇺🇸 美国-IEPL 02（231ms）可用、走代理实测 chatgpt.com 首页 200 / `codex/models` 401（放行非风控）/ `ws.chatgpt.com` 可达、Codex 进程在线且活动连接正经美国-IEPL 02 访问 chatgpt.com、系统代理 `127.0.0.1:7897` 正常。唯一异常：**青旅公共网络延迟抖动**（连续 5 次走代理访问 chatgpt.com 全通，但耗时 1.1~4.5s 波动）。判定：非代理/配置故障，无需改配置；"重新连接"为公共网络抖动导致 Codex 流式长连接偶发重建。处置：重启 Codex 重建连接即可。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | `/configs.mode` | `rule` ✅（非 direct） |
| 代理配置 | OpenAI 分流规则（5 条） | 完好，→ 🇺🇸 美国-IEPL 02 ✅ |
| 代理配置 | MATCH 兜底 | 🇭🇰 香港-IEPL 01（84ms）✅ |
| 网络层 | 节点延迟体检 | 美国-IEPL 02 = 231ms、香港-IEPL 01 = 84ms、香港-IEPL 03 = 81ms 全部可用 |
| 网络层 | 走代理实测 | chatgpt.com 200 / `codex/models` 401（放行）/ `ws.chatgpt.com` 404（可达）/ YouTube 200 |
| 网络层 | 出口分流 | ip-api.com→香港 45.67.201.103（兜底）；ChatGPT 域名→美国节点 |
| 环境层 | Codex 进程 | `codex.exe` 在线，活动连接 5 条经美国-IEPL 02 访问 chatgpt.com/chat.openai.com/ab.chatgpt.com |
| 环境层 | 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897` ✅ |
| 环境层 | 网络抖动 | 连续 5 次 chatgpt.com 全通，耗时 1.1~4.5s 波动 ⚠️ |

> [!warning] ⚠️ 关键认知
> **"Codex 界面显示重新连接" ≠ "代理隧道故障"**。本次三层诊断全部正常（mode=rule、规则完好、节点全通、Codex 连接活跃），真正的诱因是青旅公共 Wi-Fi 的延迟抖动（1.1~4.5s 波动）导致 Codex 流式长连接偶发断开自动重建。排查顺序建议：先查 `/configs` mode 与 `/rules` 分流规则（排除 05/06 两类已知故障），再实测 ChatGPT 端点与节点 delay（排除风控/下线），若全部正常 → 判定为网络抖动，重启 Codex 即可，不要盲目改配置。

## 🔁 复发记录（2026-08-10 22:29）：青旅网络下 Codex 重新连接，网络侧三层诊断全通（与 08-09 复发同款）

> [!SUMMARY] 📌 复发摘要
> 用户反馈"Codex 又重新连接了"，当前在青旅。三层诊断结果：**代理配置层、网络层、节点层全部健康**——与本文主故障（direct 模式）、04 档案订阅清规则（08-10 当天已 8 次）、节点风控均不同。具体证据：`mode: rule`、TUN=true、5 条 OpenAI 规则完好（→🇺🇸 美国-IEPL 02）、MATCH 兜底→🇭🇰 香港-IEPL 01（105ms）、美国-IEPL 02 节点 delay 314ms、走代理实测 chatgpt.com 200 / `codex/models` 401（放行）/ `ws.chatgpt.com` 404 / `api.openai.com` 401、Codex 进程在线（21:32 启动）且连接经 7897。唯一异常：<span style="color:#ff8c00">mihomo DNS 解析 chatgpt.com 得污染 IP 31.13.94.10（Facebook 段），但 OpenAI 规则走代理不受影响</span>。判定：非代理/配置故障，无需改配置；"重新连接"为青旅公共网络延迟抖动导致 Codex 流式长连接偶发重建。处置：**重启 Codex**（杀 ChatGPT/codex/codex-code-mode-host/node_repl 后经 AppsFolder 重新拉起），22:32 新进程建立 8+ 条连接走 7897，`codex/models` 401（0.94s）恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | `/configs.mode` | `rule` ✅（非 direct） |
| 代理配置 | TUN | `enable=true` ✅ |
| 代理配置 | OpenAI 分流规则（5 条） | 完好，→ 🇺🇸 美国-IEPL 02 ✅ |
| 代理配置 | MATCH 兜底 | 🇭🇰 香港-IEPL 01（105ms）✅ |
| 网络层 | 节点延迟体检 | 美国-IEPL 02 = 314ms、香港-IEPL 01 = 105ms 全部可用 |
| 网络层 | 走代理实测 | chatgpt.com 200 / `codex/models` 401（放行）/ `ws.chatgpt.com` 404 / `api.openai.com` 401 |
| 网络层 | chatgpt.com 首页 403 判定 | 瞬时 CF challenge；浏览器 UA 复测 **200**（CF-Ray 落点 LAX，美国节点）✅ |
| 网络层 | DNS 解析 | chatgpt.com → `31.13.94.10`（污染 IP，规则走代理不受影响）⚠️ |
| 环境层 | Codex 进程 | 21:32 启动在线，codex.exe 连接经 127.0.0.1:7897 ✅ |
| 环境层 | 处置后 | 重启 → 22:32 新进程（PID 31800）8+ 条连接走 7897，`codex/models` 401（0.94s）✅ |

> [!warning] ⚠️ 关键认知（延续 08-09）
> **"Codex 界面显示重新连接" ≠ "代理隧道故障"**。本次（青旅）三层诊断全部正常：mode=rule、TUN 开启、OpenAI 规则完好、节点 delay 全通、Codex 连接活跃且走 7897。**与 08-09 复发完全同款，判定为青旅公共 Wi-Fi 延迟抖动导致流式长连接偶发重建**，处置=重启 Codex，不要盲目改配置（当前配置文件 21:32 刚由一键脚本修复过，属良好状态）。另注意 `节点选择` 策略组当前指向 🇭🇰 香港-IEPL 01（对 OpenAI 403 风控的历史坏线路），但 OpenAI 5 条规则**直接指定** 🇺🇸 美国-IEPL 02 绕开了它，故不影响 Codex——若日后 OpenAI 规则被清、chatgpt.com 掉进 MATCH 兜底时才会踩雷。

## 🔁 复发记录（2026-08-11 20:40）：青旅外网全挂 + GPT 用不了（配置文件 mode: direct + OpenAI 规则被清）

> [!summary] 📌 复发摘要
> 用户回到青旅，反馈"外网连接不上了，又用不了 GPT"。三层诊断结果：**配置文件持久层 `mode: direct`（05 已知坑的"重启回退"变体）+ OpenAI 5 条分流规则被清（06 已知坑"订阅更新清规则"）+ 香港-IEPL 01/03 节点挂掉** 三重叠加。运行时 `mode: rule` 是之前手动 PATCH 的**假象**，磁盘配置文件第 4 行一直是 `mode: direct`——一旦热加载/重启就覆盖运行时，所有 HTTPS 走直连被 GFW 阻断（SSL UNEXPECTED_EOF）。同时 OpenAI 规则被清后 chatgpt.com 掉进兜底走已挂的香港-IEPL 01，GPT 打不开。处置：改配置文件 `mode: direct`→`rule` + 恢复 5 条 OpenAI 规则（→🇺🇸 美国-IEPL 02）+ MATCH 兜底改指 🇹🇼 台湾-IEPL 03（72ms），热加载后外网全恢复、GPT 走美国节点 200。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 磁盘配置文件 `mode` | <span style="color:#ff0000">`direct`（致命项，运行时是 rule 但配置持久层是 direct）</span> |
| 代理配置 | 运行时 `/configs.mode` | 热加载前 `rule`（手动 PATCH 的假象）→ 热加载后被配置覆盖成 `direct` |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空</span>，chatgpt.com 掉进 `MATCH → 节点选择 → 香港-IEPL 01` |
| 代理配置 | MATCH 兜底 | `节点选择`（指向已挂的香港-IEPL 01） |
| 网络层 | 节点 delay 体检 | 🇺🇸 美国-IEPL 02=207ms ✅；🇹🇼 台湾-IEPL 03=72ms ✅；🇭🇰 香港-IEPL 01=**504 挂**；🇭🇰 香港-IEPL 03=**503 挂**；🇭🇰 香港-IEPL 02=77ms ✅ |
| 网络层 | 走代理实测（修复前） | chatgpt.com **SSL UNEXPECTED_EOF**、youtube/google/wikipedia 全 SSL EOF（mode=direct 直连被 GFW 拦） |
| 网络层 | 走代理实测（修复后） | chatgpt.com **200**（CF-Ray LAX=美国-IEPL 02）；youtube/google/wikipedia **200**；出口 ipify=185.248.184.172（台湾-IEPL 03）✅ |
| 网络层 | Codex 端点 | `backend-api/codex/models` → 308 重定向（非 403 风控）✅ |
| 环境层 | 7897 端口 | `0.0.0.0:7897` LISTENING（PID 12272 = com.vortex.helper.exe 服务）✅ |
| 环境层 | Vortex 服务 | `com.vortex.helper` RUNNING（服务型，Session 0）✅ |

### 修复过程

1. 查 `/configs`：运行时 `mode: rule`，排除 05 主故障"运行时 direct"，一度误判为纯清规则问题。
2. 查 `/rules`：OpenAI 5 条规则消失 → 确认"订阅更新清规则"复发；MATCH 兜底 `节点选择`→香港-IEPL 01。
3. 节点 delay 体检：香港-IEPL 01（504）/03（503）挂，美国-IEPL 02（207ms）/台湾-IEPL 03（72ms）可用。
4. 备份配置文件 → 加回 5 条 OpenAI 规则 + MATCH 改台湾-IEPL 03 → 热加载（HTTP 204）。
5. 热加载后**全部 HTTPS 变 SSL EOF**——关键转折：`curl /configs` 发现运行时被配置覆盖成 `direct`，查配置文件第 4 行确认 `mode: direct`。
6. 改配置文件 `mode: direct`→`rule` → 再热加载 → 运行时恢复 `rule`。
7. 复测：chatgpt.com 200（LAX）、youtube/google/wikipedia 200、codex/models 308 全通。

> [!IMPORTANT] ⚠️ 关键认知（本次新坑）
> **"运行时 mode=rule" ≠ "配置持久层 mode=rule"**。05 档案已知"重启回退 direct"，但本次是**配置文件的 direct 一直在、运行时靠手动 PATCH 维持 rule**，热加载（`PUT /configs?force=true`）会把磁盘配置重载覆盖运行时——**凡排查到 runtime mode=rule 却出现"全站 HTTPS 直连被墙"，必须回头查磁盘配置文件第 4 行 `mode:`**，否则热加载会"帮倒忙"把隧道弄坏。修复必须**改配置文件本体**（持久化），不能只 PATCH 运行时。
> **节点 delay 通 ≠ 程序实测通**：修复前 delay 测试（美国/台湾全通）但外部 curl 全 SSL EOF，正是被 mode=direct 掩盖——delay 走 mihomo 内部代理逻辑、外部 HTTPS 走直连，两条路径不同，要分别实测才能定位。

## 🔁 复发记录（2026-08-12 00:15）：青旅网络下 Codex 使用异常——美国-IEPL 02 节点不稳 + external-controller 端口脱节

> [!SUMMARY] 📌 复发摘要
> 用户回到青旅，反馈"现在又不可以正常使用Codex了"。三层诊断结果：**代理配置层、网络层、环境层基本健康**——`mode: rule`、`ipv6: false`、OpenAI 5 条规则完整（→🇺🇸 美国-IEPL 02）、MATCH 兜底→🇹🇼 台湾-IEPL 03、Codex 进程在线且日志（截至 00:14）**无任何 stream disconnected / 403 / reset 网络错误**（仅 ResizeObserver/devicecheck 无害噪声）、走代理实测 `codex/models` **401 放行**。但发现<span style="color:#ff8c00">两个配置隐患</span>：① <span style="color:#ff0000">**OpenAI 规则指向的美国-IEPL 02 节点对 api.openai.com delay 504 超时**</span>（08-11 14:08 已记录该节点不稳），而美国-中转 01 = 343ms 稳定可用；② <span style="color:#ff8c00">**配置文件 `external-controller: 39797` 与运行态 39798 端口脱节**</span>（订阅更新遗留）。处置：备份配置 → OpenAI 5 条规则切到 🇺🇸 美国-中转 01 + external-controller 改回 39798 → 热加载 **204** → 重启 Codex → 9 条 OpenAI 连接 **8 条走美国-中转 01**、`codex/models` 401（0.96s）恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | `/configs.mode` | `rule` ✅（非 direct） |
| 代理配置 | `ipv6` | `false` ✅（10 档案已处理过 IPv6 风控） |
| 代理配置 | OpenAI 分流规则（5 条） | 完好，修复前 → 🇺🇸 美国-IEPL 02 |
| 代理配置 | MATCH 兜底 | 🇹🇼 台湾-IEPL 03 ✅ |
| 代理配置 | external-controller | <span style="color:#ff8c00">配置文件 `39797` vs 运行态 `39798`（端口脱节）</span> |
| 网络层 | 节点 delay 体检（api.openai.com） | 美国-IEPL 02=**504 超时**⚠️ / 美国-中转 01=**343ms**✅ / 香港-IEPL 01=436ms / 日本-IEPL 02=846ms / 台湾-IEPL 03=**504**⚠️ |
| 网络层 | 走代理实测（修复前） | `codex/models` **401**、`api.openai.com` **401**、google **200**（美国-IEPL 02 实际仍放行，delay 504≠不通） |
| 环境层 | Codex 进程 | 在线，日志截至 00:14 无网络错误（仅 ResizeObserver loop / devicecheck 噪声） |
| 环境层 | 活动连接（修复前） | 7 条 OpenAI 连接全部走 🇺🇸 美国-IEPL 02 |
| 环境层 | 活动连接（修复后） | 9 条中 **8 条走 🇺🇸 美国-中转 01**、1 条残留美国-IEPL 02（旧空壳进程）✅ |

### 修复过程

1. **三层诊断**：`/configs`（mode/ipv6/tun）、`/rules`（OpenAI 规则）、节点 delay 体检、走代理实测 `codex/models`、Codex 日志 grep 错误关键词。
2. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260812-0015-before-fix.yaml`（SHA256 `863f94f800d0a964`）。
3. **改配置**（Python UTF-8 安全写入，Unicode 转义节点名避开 GBK 坑）：
   - `external-controller: 127.0.0.1:39797` → `127.0.0.1:39798`（修复端口脱节）；
   - OpenAI 5 条规则（openai.com/chatgpt.com/chatgpt-api.com/oaistatic.com/oaiusercontent.com）→ <span style="color:#1e90ff">`🇺🇸|美国-中转 01`</span>。
4. **热加载**：`PUT /configs?force=true` → **HTTP 204**。
5. **重启 Codex**：PowerShell `Get-Process ChatGPT,codex,node_repl | Stop-Process -Force`（Git Bash `taskkill /F` 被 MSYS 路径转换坑，改用 PowerShell）+ `explorer.exe shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App` 重新拉起。
6. **验证**：见上表。

### 本次新增遗留事项

1. <span style="color:#ff8c00">**美国-IEPL 02 再次确认不稳**</span>（对 api.openai.com delay 504 超时，08-11 14:08 已记录）；当前 OpenAI 规则已切到 🇺🇸 美国-中转 01（delay 343ms + codex/models 401 0.96s 实测最优）。若其波动，候选放行节点：美国-中转 01 / 美国-直连 / 日本-IEPL 02。
2. <span style="color:#ff8c00">**external-controller 端口脱节复发**</span>（配置文件 39797 vs 运行态 39798，订阅更新遗留）；本次已改回 39798。再遇"控制 API 访问 39798 失败"先查配置文件第 7 行。
3. **订阅更新改动**（本次 OpenAI 规则未被清，但 external-controller 已被订阅改过端口）；强烈建议 Vortex GUI 关闭"自动更新订阅"。
4. 配置备份已更新至 `原始文件备份/vortex-config-20260812-0015-before-fix.yaml`（修复前）。

## 🔁 复发记录（2026-08-12 01:03）：青旅网络下 Codex 再次使用异常——三层诊断全通（网络抖动，重启即恢复）

> [!SUMMARY] 📌 复发摘要
> 用户反馈"网络又不好使了，Codex 又用不了"，当前在青旅。距 00:15 修复仅约 50 分钟。三层诊断**全部健康**：`mode: rule`、`external-controller: 39798`（00:15 修复保持）、OpenAI 5 规则完好→🇺🇸 美国-中转 01、MATCH→🇹🇼 台湾-IEPL 03、`ipv6: false`；节点 delay 全通（美国-中转 01=268ms、香港-IEPL 01=89ms、台湾-IEPL 03=445ms、日本-IEPL 02=508ms）；走代理实测 `codex/models` 401 / google 200 / youtube 200；本机直连 baidu 200；系统代理 `127.0.0.1:7897` 正常；路由无漂移（默认路由 192.168.9.1 metric 35）；Codex 日志无任何网络错误（仅会话渲染层无害噪声）。**判定与 08-09/08-10 复发同款：青旅公共 Wi-Fi 延迟抖动导致 Codex 流式长连接偶发重建**，非配置/节点/风控故障。处置：**重启 Codex**（杀进程 + AppsFolder 拉起），新实例 codex.exe PID 28488 连接 4 条全部走美国-中转 01，`codex/models` 401（1.64s）恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | `/configs.mode` | `rule` ✅（非 direct） |
| 代理配置 | external-controller | `39798` ✅（00:15 修复保持，未回退） |
| 代理配置 | OpenAI 分流规则（5 条） | 完好 → 🇺🇸 美国-中转 01 ✅ |
| 代理配置 | MATCH 兜底 | 🇹🇼 台湾-IEPL 03 ✅ |
| 网络层 | 节点 delay（api.openai.com） | 美国-中转 01=268ms / 香港-IEPL 01=89ms / 台湾-IEPL 03=445ms / 日本-IEPL 02=508ms **全通**；仅美国-直连 504 |
| 网络层 | 走代理实测 | `codex/models` 401 / google 200 / youtube 200 ✅ |
| 网络层 | 本机直连 | baidu 200（0.27s）✅ |
| 环境层 | 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897` ✅ |
| 环境层 | 路由 | 默认路由 192.168.9.1（metric 35）✅；Radmin VPN 高 metric 备选 |
| 环境层 | Codex 日志 | 无网络错误（仅 Conversation state not found / ResizeObserver 无害噪声） |
| 环境层 | 处置后 | 新实例 PID 28488，OpenAI 连接 4 条走美国-中转 01，`codex/models` 401（1.64s）✅ |

> [!warning] ⚠️ 关键认知（延续 08-09/08-10）
> **"Codex 界面显示重新连接/转圈" ≠ "代理隧道故障"**。本次配置、节点、实测、路由、进程全部正常，纯属青旅公共 Wi-Fi 抖动导致流式长连接偶发重建。**三层诊断全通时不要盲目改配置**——处置=重启 Codex 即可。同时提示：00:15 刚切到美国-中转 01，本次再次实测该节点 268ms 稳定，比美国-IEPL 02（520ms）更优，维持现状。

## 🔁 复发记录（2026-08-12 20:30）：青旅网络下 Codex 无法使用——网络三层全通，实为应用未运行 + AppsFolder 启动命令被 MSYS 路径转换坑

> [!SUMMARY] 📌 复发摘要
> 用户回到青旅，反馈"Codex 无法正常使用"。三层诊断结果：**代理配置层、网络层、环境层全部健康**——`mode: rule`、OpenAI 5 条规则完好（→🇺🇸 美国-IEPL 02，对 api.openai.com delay **217ms 已恢复**）、MATCH→🇹🇼 台湾-IEPL 03、系统代理 `127.0.0.1:7897` 正常；节点 delay 体检：美国-IEPL 02=217ms、台湾-IEPL 03=130ms、日本-IEPL 02=135ms、香港-IEPL 01=390ms 全通，仅美国-中转 01=ERR（挂）；走代理实测 `codex/models` **401**（放行非风控）/ chatgpt.com 带 UA **200**（首次无 UA 403 为瞬时 CF challenge）。<span style="color:#ff0000">**真正问题**：Codex 应用进程（codex.exe / ChatGPT.exe）完全未运行</span>，且 Git Bash（MSYS）里执行 `explorer.exe shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App` 因 <span style="color:#ff8c00">**MSYS 路径转换破坏反斜杠参数而静默失效**</span>（无进程、无崩溃日志，`Start-Process` 直接启动 WindowsApps 下 exe 报 Access denied）。处置：改用 **PowerShell 启动**（`explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"`）后 Codex 正常拉起（ChatGPT.exe 多实例 + codex.exe PID 33320），<span style="color:#1e90ff">16 条连接全部经 127.0.0.1:7897 走代理</span>，`codex/models` 401（0.9s）恢复。判定：**非网络/代理/节点故障**，是应用未运行 + 启动命令被 MSYS 坑；网络侧保持健康，未改任何配置。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | `/configs.mode` | `rule` ✅（非 direct） |
| 代理配置 | OpenAI 分流规则（5 条） | 完好 → 🇺🇸 美国-IEPL 02 ✅（00:15 曾切美国-中转 01，现被回退指回 IEPL 02，但该节点 delay 217ms 已恢复可用） |
| 代理配置 | MATCH 兜底 | 🇹🇼 台湾-IEPL 03 ✅ |
| 网络层 | 节点 delay（api.openai.com） | 美国-IEPL 02=217ms / 台湾-IEPL 03=130ms / 日本-IEPL 02=135ms / 香港-IEPL 01=390ms **全通**；仅美国-中转 01=ERR（挂） |
| 网络层 | 走代理实测 | `codex/models` 401（放行）/ chatgpt.com 带 UA 200（无 UA 首测 403=瞬时 CF challenge）✅ |
| 环境层 | 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897` ✅ |
| 环境层 | 7897 端口 | `::` LISTENING（PID 13480 = com.vortex.helper）✅ |
| 环境层 | Codex 进程（修复前） | **codex.exe / ChatGPT.exe 全部不存在** ⚠️（根因） |
| 环境层 | 启动方式坑 | Git Bash `explorer.exe shell:AppsFolder\...` **静默失效**（MSYS 路径转换破坏 `\`）；PowerShell `Start-Process` 直接跑 WindowsApps 下 exe 报 **Access denied**；PowerShell `explorer.exe "shell:AppsFolder\..."` **成功** |
| 环境层 | 处置后 | ChatGPT.exe 多实例（PID 11636/19392/32388 等）+ codex.exe（PID 33320），**16 条连接全部经 127.0.0.1:7897**，`codex/models` 401（0.9s）✅ |

### 修复过程

1. **三层诊断**：`/configs`（mode/ipv6/tun）、`/rules`（OpenAI 规则）、节点 delay 体检、走代理实测 `codex/models`/chatgpt.com、系统代理查询（`reg query /v` 在 Git Bash 报语法错，改 PowerShell `Get-ItemProperty`）。
2. **排除网络故障**：mode=rule、规则完好、节点 delay 全通、`codex/models` 401 放行、chatgpt.com 带 UA 200 → 网络侧健康。
3. **定位真正问题**：`Get-Process *codex*,*ChatGPT*,*node_repl*` 返回空 → Codex 应用未运行。
4. **启动坑排查**：bash 里 `explorer.exe shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App` 无进程无崩溃（MSYS 把参数里的 `\` 吃掉）；`Start-Process "C:\Program Files\WindowsApps\...\app\Codex.exe"` 报 Access denied（WindowsApps ACL 保护，只能走 Appx 激活）。
5. **修复**：PowerShell 执行 `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"`（**给参数加双引号**）→ 应用正常拉起。
6. **验证**：进程在线 + 16 条连接走 7897 + `codex/models` 401 恢复。

> [!warning] ⚠️ 关键认知（本次新坑）
> **① "Codex 用不了" ≠ "网络故障"**：网络三层全通（含 `codex/models` 401 放行）时，第一件事先查 **Codex 进程是否在运行**（`Get-Process *codex*,*ChatGPT*`），进程没了就只是应用没启动，别去改配置。
> **② Git Bash 的 MSYS 路径转换会破坏 `shell:AppsFolder\...` 参数**：`explorer.exe shell:AppsFolder\OpenAI.Codex_...!App` 在 bash 里静默失效（反斜杠被转换），必须改用 **PowerShell** 且**给整个 URI 加引号**：`explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"`。
> **③ WindowsApps 目录受 ACL 保护**：直接 `Start-Process` 运行安装目录里的 `Codex.exe` 报 Access denied，只能经 Appx 激活机制（AppsFolder 协议）启动。

## 🔁 复发记录（2026-08-13 19:30）：青旅网络下 Codex 使用异常——第 14 次订阅清规则 + 配置文件 mode:direct + 端口脱节 + ipv6 回退 + Codex 应用未运行

> [!SUMMARY] 📌 复发摘要
> 用户回到青旅，反馈"现在回到青旅了，请将网络配置好，我要使用 Codex"。三层诊断结果：**配置文件持久层 `mode: direct`（05 已知坑"重启回退"变体，运行态 rule 是热加载前假象）+ OpenAI 5 条分流规则被清（"订阅更新清规则"已知坑，累计第 14 次）+ external-controller 端口脱节（配置文件 39797 vs 运行态 39798）+ ipv6 回退 true（10 档案已处理过又被订阅重置）** 四重叠加；同时 **Codex 应用未运行**（codex.exe / ChatGPT.exe 全部不存在，F9 同款）。节点侧：脚本默认 🇺🇸 美国-IEPL 02 对 api.openai.com delay **270ms** 存活、🇹🇼 台湾-IEPL 03 对 gstatic **81ms** 存活（对 OpenAI 504 仅作兜底不受影响）——节点健康无需更换。处置：运行一键脚本 `fix_vortex_config.py`（备份→mode→rule、端口→39798、恢复 5 条 OpenAI 规则→🇺🇸 美国-IEPL 02、MATCH→🇹🇼 台湾-IEPL 03、热加载 **204**、恢复 TUN **204**）→ 补插 `ipv6: false` + 热加载 **204** + 恢复 TUN **204** → 验证 `/configs` mode=rule/ipv6=false/tun=true/port=7897、`/rules` **70 条**（OpenAI 5 条→美国-IEPL 02、MATCH→台湾-IEPL 03）→ 走代理实测 `codex/models` **401**（0.94s）/ chatgpt.com **200**（1.93s）/ google **200** / youtube **200** → PowerShell 经 AppsFolder 启动 Codex（规避 MSYS 路径转换坑）→ codex.exe（PID 6556）多条 Established → 127.0.0.1:7897，恢复可用。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 磁盘配置文件 `mode` | <span style="color:#ff0000">`direct`（致命项；运行时 rule 是热加载前假象，热加载即被配置覆盖）</span> |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空</span>，仅剩 65 条出厂规则；chatgpt.com 掉进 `MATCH → 节点选择 → 🇭🇰 香港-IEPL 01`（历史 403 风控线路） |
| 代理配置 | external-controller | <span style="color:#ff8c00">配置文件 `39797` vs 运行态 `39798`（端口脱节复发）</span> |
| 代理配置 | ipv6 | <span style="color:#ff8c00">回退 `true`（10 档案已处理过，订阅更新后又恢复默认）</span> |
| 网络层 | 节点 delay 体检（api.openai.com） | 🇺🇸 美国-IEPL 02=**270ms** ✅；🇺🇸 美国-中转 02=269ms；🇯🇵 日本-IEPL 02=236ms；🇺🇸 美国-直连=**503 挂**；🇹🇼 台湾-IEPL 03=**504 挂**（对 OpenAI，仅兜底不受影响） |
| 网络层 | 节点 delay 体检（gstatic） | 🇹🇼 台湾-IEPL 03=**81ms** ✅；🇭🇰 香港-IEPL 02=59ms；🇯🇵 日本-IEPL 02=105ms |
| 网络层 | 走代理实测（修复后） | `codex/models` **401**（0.94s，放行非风控）/ chatgpt.com **200**（1.93s）/ google **200** / youtube **200** ✅ |
| 环境层 | 7897 端口 | LISTENING（Vortex PID 15068）✅ |
| 环境层 | 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897` ✅ |
| 环境层 | Codex 进程（修复前） | **codex.exe / ChatGPT.exe 全部不存在** ⚠️（F9 同款：应用未运行） |
| 环境层 | 处置后 | PowerShell `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"` 拉起 → codex.exe（PID 6556）+ 多 ChatGPT.exe，多条 Established → 127.0.0.1:7897 ✅ |

### 修复过程

1. **三层诊断**：`/configs`（mode=rule/tun=true/ipv6=true/port=7897）、`/rules`（OpenAI 规则 0、65 条出厂版）、配置文件（mode:direct/39797/无 OpenAI 规则/MATCH→节点选择）、节点 delay 体检、Codex 进程检查。
2. **节点体检**：脚本默认 OPENAI_NODE 美国-IEPL 02（270ms）与 MATCH_NODE 台湾-IEPL 03（81ms）均存活 → **无需更新脚本**。
3. **运行一键脚本** `scripts/fix_vortex_config.py`：备份（`原始文件备份/vortex-config-20260813-1926-before-fix.yaml`）→ mode→rule、端口→39798、恢复 5 条 OpenAI 规则→美国-IEPL 02、MATCH→台湾-IEPL 03 → 热加载 **204** → 恢复 TUN **204**。
4. **补插 `ipv6: false`**（顶层，脚本不处理）+ 备份（`原始文件备份/vortex-config-20260813-1926-ipv6.yaml`）+ 热加载 **204** + 恢复 TUN **204**。
5. **启动 Codex**：PowerShell `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"`（规避 bash→MSYS 路径转换坑，见 F9）→ 进程拉起。
6. **验证**：见上表。

> [!warning] ⚠️ 关键认知（延续 08-13 10:44 / 08-12 09:38）
> **"Codex 用不了" ≠ "网络故障"**：本次仍属"订阅更新重写 config.yaml"完整套餐——配置文件 `mode: direct`（热加载/重启即覆盖运行时）+ OpenAI 规则被清 + 端口脱节 + ipv6 回退四重叠加，同时 Codex 应用又未运行（F9 同款）。排查顺序固定：① 配置文件第 4 行 mode + 第 6 行 external-controller → ② `/rules` 有无 openai 规则 → ③ 节点 delay + 走代理实测 `codex/models` → ④ `Get-Process *codex*,*ChatGPT*` 进程是否在跑。**每次跑脚本前必须先实测节点**（节点漂移频繁），本次脚本默认值仍可用（美国-IEPL 02=270ms / 台湾-IEPL 03=81ms）。

## 🔁 复发记录（2026-08-14 20:56）：青旅网络下配置 Codex 网络——第 16 次订阅清规则 + 配置文件 mode:direct + 端口脱节 + ipv6 回退 + Codex 应用未运行

> [!SUMMARY] 📌 复发摘要
> 用户回到青旅，反馈"将 Codex 的网络环境配置好让我可以正常访问外网，并打开 Codex"。三层诊断结果：**配置文件持久层 `mode: direct`（05 已知坑"重启回退"变体，运行态 rule 是热加载前假象）+ OpenAI 5 条分流规则被清（"订阅更新清规则"已知坑，累计第 16 次）+ external-controller 端口脱节（配置文件 39797 vs 运行态 39798）+ ipv6 回退 true（10 档案已处理过又被订阅重置）** 四重叠加；同时 **Codex 应用未运行**（codex.exe / ChatGPT.exe 全部不存在，F9 同款）。节点侧：脚本默认 🇺🇸 美国-IEPL 02 对 api.openai.com delay **264ms** 存活、🇹🇼 台湾-IEPL 03 对 gstatic **90ms** 存活——节点健康无需更换。处置：运行一键脚本 `fix_vortex_config.py`（备份→mode→rule、端口→39798、恢复 5 条 OpenAI 规则→🇺🇸 美国-IEPL 02、MATCH→🇹🇼 台湾-IEPL 03、热加载 **204**、恢复 TUN **204**）→ 补插 `ipv6: false` + 热加载 **204** + 恢复 TUN **204** → 验证 `/configs` mode=rule/ipv6=false/tun=true/port=7897、`/rules` **70 条**（OpenAI 5 条→美国-IEPL 02、MATCH→台湾-IEPL 03）→ 走代理实测 `codex/models` **401**（1.32s）/ chatgpt.com 重试 **200**（CF-Ray LAX）/ google **200** / youtube **200** → PowerShell 经 AppsFolder 启动 Codex（规避 MSYS 路径转换坑）→ codex.exe（PID 33868）5 条 + ChatGPT（PID 33016）14 条 Established → 127.0.0.1:7897，恢复可用。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 磁盘配置文件 `mode` | <span style="color:#ff0000">`direct`（致命项；运行时 rule 是热加载前假象，热加载即被配置覆盖）</span> |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空</span>，仅剩 65 条出厂规则；chatgpt.com 掉进 `MATCH → 节点选择`（历史 403 风控线路） |
| 代理配置 | external-controller | <span style="color:#ff8c00">配置文件 `39797` vs 运行态 `39798`（端口脱节复发）</span> |
| 代理配置 | ipv6 | <span style="color:#ff8c00">回退 `true`（10 档案已处理过，订阅更新后又恢复默认）</span> |
| 网络层 | 节点 delay 体检（api.openai.com） | 🇺🇸 美国-IEPL 02=**264ms** ✅；🇺🇸 美国-中转 02=252ms；🇯🇵 日本-IEPL 02=248ms；🇺🇸 美国-中转 01=**504 挂** |
| 网络层 | 节点 delay 体检（gstatic） | 🇹🇼 台湾-IEPL 03=**90ms** ✅；🇭🇰 香港-IEPL 01=68ms；🇭🇰 香港-IEPL 02=74ms |
| 网络层 | 走代理实测（修复后） | `codex/models` **401**（1.32s，放行非风控）/ chatgpt.com 重试 **200**（CF-Ray LAX）/ google **200** / youtube **200** ✅ |
| 环境层 | 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897` ✅ |
| 环境层 | Codex 进程（修复前） | **codex.exe / ChatGPT.exe 全部不存在** ⚠️（F9 同款：应用未运行） |
| 环境层 | 处置后 | PowerShell `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"` 拉起 → codex.exe（PID 33868）+ 多 ChatGPT.exe，codex 5 条 + ChatGPT 14 条 Established → 127.0.0.1:7897 ✅ |

### 修复过程

1. **三层诊断**：`/configs`（mode=rule 假象/tun=true/ipv6=true/port=7897）、`/rules`（OpenAI 规则 0、65 条出厂版）、配置文件（mode:direct/39797/无 OpenAI 规则/MATCH→节点选择）、节点 delay 体检、Codex 进程检查。
2. **节点体检**：脚本默认 OPENAI_NODE 美国-IEPL 02（264ms）与 MATCH_NODE 台湾-IEPL 03（90ms）均存活 → **无需更新脚本**。
3. **运行一键脚本** `scripts/fix_vortex_config.py`：备份（`原始文件备份/vortex-config-20260814-2057-before-fix.yaml`）→ mode→rule、端口→39798、恢复 5 条 OpenAI 规则→美国-IEPL 02、MATCH→台湾-IEPL 03 → 热加载 **204** → 恢复 TUN **204**。
4. **补插 `ipv6: false`**（顶层，脚本不处理）+ 备份（`原始文件备份/vortex-config-20260814-2057-ipv6.yaml`）+ 热加载 **204** + 恢复 TUN **204**。
5. **启动 Codex**：PowerShell `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"`（规避 bash→MSYS 路径转换坑，见 F9）→ 进程拉起。
6. **验证**：见上表。

> [!warning] ⚠️ 关键认知（延续 08-13 19:30 / 08-13 10:44）
> **"回到青旅配置 Codex 网络" = "订阅更新重写 config.yaml"完整套餐再复发**：配置文件 `mode: direct` + OpenAI 规则被清 + 端口脱节 + ipv6 回退四重叠加，同时 Codex 应用又未运行（F9 同款）。排查顺序固定：① 配置文件第 4 行 mode + 第 6 行 external-controller → ② `/rules` 有无 openai 规则 → ③ 节点 delay + 走代理实测 `codex/models` → ④ `Get-Process *codex*,*ChatGPT*` 进程是否在跑。**每次跑脚本前必须先实测节点**（节点漂移频繁），本次脚本默认值仍可用（美国-IEPL 02=264ms / 台湾-IEPL 03=90ms）。

## 🔁 复发记录（2026-08-15 12:31）：青旅网络下配置 Codex 网络——第 17 次订阅清规则 + 配置文件 mode:direct + 端口脱节 + ipv6 回退 + sniffing 清退 + tun 回退 + Codex 应用未运行

> [!SUMMARY] 📌 复发摘要
> 用户回到青旅，反馈"将网络环境配置好，我要使用 Codex"。三层诊断结果：**配置文件持久层 `mode: direct`（05 已知坑"重启回退"变体）+ OpenAI 5 条分流规则被清（"订阅更新清规则"已知坑，累计第 17 次）+ external-controller 端口脱节（配置文件 39797 vs 运行态 39798）+ ipv6 回退 true（10 档案已处理过又被订阅重置）+ sniffing 清退（11 档案已处理过，订阅重写后配置丢失 `sniffing: true`）+ tun.enable 回退 false** 六重叠加；同时 **Codex 应用未运行**（codex.exe / ChatGPT.exe 全部不存在，F9 同款）。运行态 `/configs` 显示 mode=rule 是热加载前旧配置假象，文件被订阅重写后与运行态不同步，重启即翻车。处置：**综合一键修复**（备份 `原始文件备份/vortex-config-20260815-1231-full-fix.yaml` → mode→rule、端口→39798、补插 sniffing:true、补插 ipv6:false、恢复 5 条 OpenAI 规则→🇺🇸 美国-IEPL 02、MATCH→🇹🇼 台湾-IEPL 03、tun.enable→true → 热加载 **204** → 恢复 TUN **204**）→ 验证 `/configs` mode=rule/ipv6=false/tun=true/port=7897、`/rules` **70 条**（OpenAI 5 条→美国-IEPL 02、MATCH→台湾-IEPL 03）→ 走代理实测 `api.openai.com` **401**（1.4s）/ chatgpt.com **403**（CF 挑战，连接已通）/ google **200**（0.53s）→ TUN 直连重测 `api.openai.com` **401**（1.6s，实时连接确认 `host=api.openai.com | rule=DomainSuffix | chain=🇺🇸|美国-IEPL 02`；首测 000 为热加载后 fake-ip 映射瞬时未刷新）→ DNS 确认走 fake-ip（198.18.0.2，api.openai.com→198.18.0.21）→ 配置持久化确认（重启不回退）→ PowerShell 经 AppsFolder 启动 Codex（规避 MSYS 路径转换坑，见 F9）→ codex.exe（PID 37912）+ 8 个 ChatGPT.exe 渲染进程，app-server 崩溃数 **0**、已成功响应 **40** 次、插件同步完成，恢复可用。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 磁盘配置文件 `mode` | <span style="color:#ff0000">`direct`（致命项；运行态 rule 是热加载前旧配置假象，文件与运行态不同步）</span> |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空</span>，仅剩出厂规则；chatgpt.com 掉进 `MATCH → 节点选择`（历史 403 风控线路） |
| 代理配置 | external-controller | <span style="color:#ff8c00">配置文件 `39797` vs 运行态 `39798`（端口脱节复发）</span> |
| 代理配置 | sniffing | <span style="color:#ff8c00">清退（配置文件无 `sniffing` 行；11 档案已处理过，订阅重写又被抹掉）</span> |
| 代理配置 | ipv6 | <span style="color:#ff8c00">回退 `true`（10 档案已处理过，订阅更新后又恢复默认）</span> |
| 代理配置 | tun.enable | <span style="color:#ff8c00">回退 `false`（已知坑，订阅重写后 TUN 关闭）</span> |
| 网络层 | 节点 delay 体检 | 全部 FAIL——延迟体检要求 HTTP 200，OpenAI 返回 401/403（CF 挑战）计 FAIL；用 gstatic 204 URL 复核仍 FAIL（mihomo 1.10.0 delay API 报告怪癖），但实际连接已通，以实测为准 |
| 网络层 | 走代理实测（修复后） | `api.openai.com/v1/models` **401**（1.4s）/ chatgpt.com **403**（3.2s，CF 挑战连接已通）/ google **200**（0.53s）✅ |
| 网络层 | TUN 直连（修复后） | `api.openai.com/v1/models` **401**（1.6s），实时连接确认 `rule=DomainSuffix → chain=🇺🇸|美国-IEPL 02`；首测 000 为热加载后 fake-ip 映射瞬时未刷新 ✅ |
| 网络层 | DNS | 走 mihomo fake-ip（DNS 服务器 198.18.0.2，api.openai.com→198.18.0.21、chatgpt.com→198.18.0.22）✅ |
| 环境层 | Codex 进程（修复前） | **codex.exe / ChatGPT.exe 全部不存在** ⚠️（F9 同款：应用未运行） |
| 环境层 | 处置后 | PowerShell `Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'` 拉起 → codex.exe（PID 37912）+ 8 个 ChatGPT.exe 渲染进程；app-server 崩溃数 **0**、已成功响应 **40** 次、插件同步完成 ✅ |

### 修复过程

1. **三层诊断**：`/configs`（运行态 mode=rule 假象 / tun=False / sniffing=False / ipv6=True）、`/rules`（OpenAI 规则 0）、配置文件（mode:direct / 39797 / 无 OpenAI 规则 / 无 sniffing / MATCH→节点选择 / tun.enable:false）、节点 delay 体检、Codex 进程检查。
2. **综合一键修复**：备份（`原始文件备份/vortex-config-20260815-1231-full-fix.yaml`）→ mode→rule、端口→39798、补插 `sniffing: true`、补插 `ipv6: false`、恢复 5 条 OpenAI 规则→美国-IEPL 02、MATCH→台湾-IEPL 03、tun.enable→true → 热加载 **204** → 恢复 TUN **204**。
3. **验证**：`/configs`（mode=rule/ipv6=false/tun=true/port=7897）、`/rules` **70 条**（OpenAI 5 条→美国-IEPL 02、MATCH→台湾-IEPL 03）、走代理实测、TUN 直连重测、DNS 确认、配置持久化确认（重启不回退）。
4. **启动 Codex**：PowerShell `Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'`（规避 bash→MSYS 路径转换坑，见 F9）→ 进程拉起并健康确认。
5. **验证**：见上表。

> [!warning] ⚠️ 关键认知（延续 08-14 20:56 / 08-13 19:30）
> **"回到青旅配置 Codex 网络" = "订阅更新重写 config.yaml"完整套餐再复发**，本次叠加到 **六重**：配置文件 `mode: direct` + OpenAI 规则被清 + 端口脱节 + ipv6 回退 + sniffing 清退 + tun.enable 回退，同时 Codex 应用未运行（F9 同款）。排查顺序固定：① 配置文件第 4 行 mode + 第 6 行 external-controller + 顶层 sniffing/ipv6/tun 项 → ② `/rules` 有无 openai 规则 → ③ 节点 delay + 走代理实测 `api.openai.com`（**401 即放行**，不要被 403 CF 挑战 / 000 瞬时超时误导）→ ④ `Get-Process *codex*,*ChatGPT*` 进程是否在跑。**节点 delay FAIL ≠ 节点挂**：延迟体检要求 HTTP 200，OpenAI 类域名返回 401/403 计 FAIL 属正常，用 204 URL 复核并辅以走代理 / TUN 直连实测，以真实连接链为准。

## 🔗 相关笔记与附件

- [[04-Codex桌面端反复重新连接（公司环境）]] — **公寓环境**档案：DNS 污染 + 出口 IP 风控 + 网络体检，与本篇（青旅 + direct 模式）互补
- [[06-国外网站访问慢但Codex正常]] — **分流规则**档案：OpenAI 域名走美国节点、其余走香港快节点；含多次"订阅更新清规则"复发记录
- [[wiki/AI与技术工具/Codex模型配置]] — Codex 配置总纲，含「🚨 网络故障排查」章节与节点可用性速查表
- 速查：早上公寓故障的节点批量实测、出口风控判定方法见 [[04-Codex桌面端反复重新连接（公司环境）#🔁 复发记录（2026-08-06）：出口 IP 被 Cloudflare 风控]]
