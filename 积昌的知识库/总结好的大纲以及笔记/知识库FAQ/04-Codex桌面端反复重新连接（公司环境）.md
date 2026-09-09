---
title: "Codex 桌面端反复重新连接（公寓环境）：代理出口、污染 DNS 与旧长连接残留"
type: "知识库 FAQ / 报错修复"
date: 2026-08-04
created: 2026-08-04
updated: 2026-08-31
environment: "🏠 公寓"
tags:
  - Codex
  - ChatGPT
  - 网络故障
  - Rocket
  - Clash
  - DNS
  - ERR_CONNECTION_RESET
  - 公寓
source: "2026-08-04 用户现场反馈与本机 Codex / Rocket 日志"
---

# 🔌 Codex 桌面端反复重新连接（🏠 公寓环境）

> [!summary] 📊 报错统计速览（截至 2026-08-31）
> 🔥 **本文档共记录 <span style="color:#e74c3c">23 次报错/复发事件</span>**（08-04 原始事件 1 次 + 复发/复查 22 次）。高频根因为 **「订阅更新清 OpenAI 分流规则」**（台账累计 22 次，以本文档为主发地）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 订阅更新清 OpenAI 分流规则 | **22** | 04（为主）/ 05 / 06 |
> | 🟠 配置被切 direct 模式 | **10** | 04 / 05 |
> | 🔴 出口 IP 被 Cloudflare 风控 | **1** | 04 |
> | 🔴 OpenAI 分流规则钉死到被 CF 风控的数据中心节点 | **1** | 04 |
> | 🟠 节点质量波动 / 机场线路故障 | **6** | 04 / 05 |
> | 🟠 Codex 应用长连接卡死（网络全通，重启恢复） | **2** | 04 |
> | 🟠 mihomo sniffing 关闭致 TUN 直连不按域名分流 | **3** | 11 / 04 |
> | 🔴 Codex 主运行时更新失败（EPERM）/ 进程堆积致状态错乱 | **1** | 04 |
> | 🔴 Codex 主运行时插件同步失败致 app-server 崩溃（发消息无回应） | **1** | 04 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!info] 📍 适用环境：🏠 公寓
> 本文档记录**公寓/公司环境**下的 Codex 网络故障排查（DNS 污染、出口 IP 风控、节点质量体检）。**青旅环境**的故障（Vortex 被切到 direct 模式）见 [[05-Codex网络故障-青旅环境]]。

> [!SUMMARY] 📌 结论摘要
> 本次“每次发送消息都像在重新连接”并非单一界面故障。现场日志确认了 <span style="color:#ff0000">`net::ERR_CONNECTION_RESET`</span> 与消息订阅通道断开；系统 DNS 对 OpenAI 域名返回异常地址，Rocket 又长期使用波动较大的美国 02 出口。修改规则后，桌面端已有长连接仍黏在旧线路上，因此必须同时完成 <span style="color:#ff8c00">DNS 映射修正、稳定节点切换、旧连接定向重建</span>。21:57 起真实应用连接已全部走日本 04 和新地址，观察窗口内未新增连接重置或消息通道重连。

## 🧭 快速索引

- [[#🚨 错误概览|🚨 错误概览]]
- [[#🧩 根本原因|🧩 根本原因]]
- [[#🔬 三层诊断数据|🔬 三层诊断数据]]
- [[#🛠️ 修复过程|🛠️ 修复过程]]
- [[#🧰 技术栈与术语|🧰 技术栈与术语]]
- [[#🧱 排查中遇到的问题|🧱 排查中遇到的问题]]
- [[#✅ 验证结果|✅ 验证结果]]
- [[#🛡️ 后续建议|🛡️ 后续建议]]
- [[#🔗 相关笔记与附件|🔗 相关笔记与附件]]

## 🚨 错误概览

| 项目 | 现场信息 |
|---|---|
| 记录时间 | 2026-08-04 21:41（Asia/Shanghai） |
| 现象 | 发送消息后频繁显示重新连接，访问速度慢，偶发请求失败 |
| 应用 | Windows 版 Codex 桌面端 `26.727.6591.0` |
| 代理 | Rocket / ClashR，系统代理 `127.0.0.1:4780`，控制端口 `4788` |
| 直接证据 | `chatgpt_pubsub_transport_closed`、`chatgpt_pubsub_reconnect_scheduled`、`net::ERR_CONNECTION_RESET` |
| 最终状态 | <span style="color:#1e90ff">已修复并进入持续观察</span> |

<span style="color:#ff0000">关键错误：</span>

```text
net::ERR_CONNECTION_RESET
chatgpt_pubsub_transport_closed
chatgpt_pubsub_reconnect_scheduled
```

旧日志中的消息订阅连接通常在 3～11 秒后自行打开，但反复出现时，用户界面就会表现为“重新连接”。当前会话还在 21:14、21:18 记录到真实的底层连接重置。

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 环境层 | <span style="color:#ff0000">系统 DNS 被污染</span> | `chatgpt.com`、`api.openai.com` 等曾解析到与 OpenAI 无关的地址 | 在 Rocket `hosts` 中固定经 DoH 核验的 Cloudflare 地址 |
| 网络层 | <span style="color:#ff0000">美国 02 出口存在连接重置与高延迟</span> | 当前日志出现 `ERR_CONNECTION_RESET`；节点实测接近 1 秒且有失败 | 横向测试美、日、新线路，切换至日本 04 |
| 会话层 | <span style="color:#ff8c00">旧长连接没有自动继承新规则</span> | 修改后活动连接仍显示美国 02 和旧 IP | 仅关闭 OpenAI 相关旧连接，让应用按新规则重建 |
| 配置层 | `chatgpt.com` 只固定到单一旧地址 | DoH 同时返回 `172.64.155.209` 与 `104.18.32.47` | 改用本次测试更稳的 `104.18.32.47` |

> [!IMPORTANT] ⚠️ 容易误判的日志
> 本地 Codex 服务曾以 `0x40010004` 退出，退出信息末尾带有插件图标路径警告。该退出码更像进程被终止，且警告早于退出近一小时；因此 <span style="color:#ff8c00">不能把“最后一条错误输出”等同于崩溃根因</span>。插件警告被记录为次要噪声，本次没有为消除噪声而修改无关插件。

## 🔬 三层诊断数据

### 1. 文件与配置层

- Rocket 配置：`C:\Users\asus\AppData\Roaming\Rocket\clash-configs\rocket.yaml`
- 原映射：`chatgpt.com -> 172.64.155.209`
- 新映射：<span style="color:#1e90ff">`chatgpt.com -> 104.18.32.47`</span>
- Cloudflare DoH 与 Google DoH 均返回同一双地址集合，排除了继续使用本机污染 DNS 的风险。
- 配置修改前 SHA-256 与知识库备份一致。

### 2. 环境与网络层

- Windows 系统代理已启用：`127.0.0.1:4780`。
- Rocket 在线、规则模式正常。
- 美国 02 / 美国 04 在测试中均出现失败；日本 04 三轮节点探测为 <span style="color:#1e90ff">3/3 成功，平均约 810ms</span>。
- 高频短连接压力测试仍可能被线路或 Cloudflare 主动重置，因此最终验收以桌面端真实长连接日志为准。

### 3. 工具与会话层

- 切换规则后，活动连接仍显示：`美国 02 -> 172.64.155.209`。
- 定向关闭 5 条 OpenAI 旧连接后，新连接显示：
  - `chatgpt.com -> 104.18.32.47 -> 日本 04`
  - `ab.chatgpt.com -> 104.18.32.47 -> 日本 04`
  - `chat.openai.com -> 104.18.37.228 -> 日本 04`
- <span style="color:#1e90ff">21:57 后没有新增 `ERR_CONNECTION_RESET`、pubsub 重连或本地 transport 断开</span>。

## 🛠️ 修复过程

1. 搜索 `知识库FAQ`，确认没有同根因记录，避免重复建档。
2. 复现并读取 Codex 桌面日志，分离“消息订阅重连”“HTTP 连接重置”“本地服务退出”三类事件。
3. 备份 Rocket 原始配置到 FAQ 的 `原始文件备份`，并核对哈希。
4. 使用加密 DNS 核验 OpenAI 域名的真实 Cloudflare 地址。
5. 将 `chatgpt.com` 映射由 `172.64.155.209` 改为 <span style="color:#1e90ff">`104.18.32.47`</span>，热加载配置。
6. 对美国、日本、新加坡候选出口进行多轮实测，按“零失败优先、延迟其次”选中 <span style="color:#1e90ff">日本 04 NTT</span>。
7. 同步更新 `🔰国外流量` 与 `GLOBAL` 选择器。
8. 仅断开仍黏在旧线路上的 OpenAI 连接，保留其他网站连接；桌面端自动重建成功。
9. 重新检查真实应用日志和控制器连接路径。

> [!NOTE] 💡 与终端弹窗问题的关系
> 先前创建的网络自愈计划任务会弹出终端窗口，已被删除，脚本也已停用。它不是本次连接重置的根因，但移除后可避免 <span style="color:#ff8c00">“为了修网络反而周期性打扰桌面”</span>。

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| PubSub | 发布/订阅长连接，用来实时接收对话状态；断开时界面可能显示重新连接 |
| `ERR_CONNECTION_RESET` | 对端或中间代理强制重置 TCP 连接，并非普通 HTTP 404/500 |
| DNS 污染 | 域名被解析到错误 IP，导致请求去错服务器或被重置 |
| DoH | DNS over HTTPS，通过 HTTPS 查询 DNS，降低本地 DNS 被篡改的风险 |
| Clash `hosts` | 代理内部的域名到 IP 映射，优先于不可信的系统解析结果 |
| 长连接黏连 | 连接建立后继续使用原节点；只改规则不会自动迁移已存在连接 |
| 出口节点 | 代理访问公网时实际使用的远端服务器 |

## 🧱 排查中遇到的问题

1. <span style="color:#ff8c00">插件图标路径警告容易误导</span>：它只是退出时保留的最后两条 stderr，时间关系不支持将其定为崩溃原因。
2. 节点“能访问”不等于稳定：一次延迟测试无法发现间歇重置，因此采用多节点、多轮次和真实应用日志交叉验证。
3. 修改规则后旧连接仍保留旧路径：必须检查控制器的活动连接，不能只看配置文件。
4. 高频 `curl` 短连接与桌面长连接行为不同：压力测试作为参考，真实验收以应用日志为主。

## ✅ 验证结果

- [x] Rocket 配置热加载成功。
- [x] `🔰国外流量` 与 `GLOBAL` 均选择日本 04。
- [x] `chatgpt.com` 新连接目标为 `104.18.32.47`。
- [x] 三类 OpenAI 长连接全部显示日本 04 路径。
- [x] Rocket 持久化缓存已保存 `GLOBAL` 与 `🔰国外流量 -> 日本 04`，重启后不会自动退回美国 02。
- [x] 旧 OpenAI 连接已定向清理，其他连接未清理。
- [x] 21:57～22:03 的真实应用观察窗口未新增 `ERR_CONNECTION_RESET`。
- [x] 21:57～22:03 未新增 `chatgpt_pubsub_reconnect_scheduled`。
- [x] 21:57～22:03 未新增本地 `transport_closed`。

<span style="color:#1e90ff">验收结论：</span>配置、运行时路由和真实会话三层已一致，当前修复有效。

## 🛡️ 后续建议

1. 保持 Rocket 在 Codex 使用期间运行；若代理退出，系统代理仍指向 `127.0.0.1:4780` 时所有访问都会失败。
2. 不再使用会弹窗的计划任务做网络自愈。
3. 若后续日志再次出现连续 `ERR_CONNECTION_RESET`，优先切换到本次零失败候选日本 03 / 日本 02，并检查机场线路质量。
4. 不要仅凭“延迟最低”选节点；<span style="color:#ff0000">稳定性应优先于几十毫秒的速度差</span>。
5. Rocket 订阅更新可能覆盖手工 `hosts`；更新后应复查本条 FAQ 中的映射与备份。

## 🔁 复发记录（2026-08-10 15:50）：公司网络下 Codex 反复重连——机场节点全部故障（trojan 转发失效）+ 订阅清规则 + DNS 污染

> [!SUMMARY] 📌 复发摘要
> 用户在公司网络反馈"Codex 刚刚还能用，现在反复重连无法使用"。三层诊断发现**三个叠加问题**：① <span style="color:#ff8c00">**机场订阅更新（08-10 09:17）再次重写 config.yaml**</span>——5 条 OpenAI 分流规则被清（`/rules` 回 65 条出厂版、`MATCH → 节点选择`）、`mode` 还原 `direct`、`external-controller` 改 `39797`（06 文档第 5 次同款复发）；② <span style="color:#ff0000">**chatgpt.com 被 mihomo DNS 解析到污染 IP**（108.160.166.9 / 118.193.240.41），无 OpenAI 规则时命中 `GEOIP,cn,DIRECT` 直连超时</span>；③ <span style="color:#ff0000">**机场所有节点当前不可用**</span>——批量 trojan 探测：中转/直连系列（z1/z2/dd 服务器）TLS 握手失败，IEPL 系列（iepl-q/iepl-t 中转机）trojan 转发返回 **nginx 欢迎页（转发被短路）**，节点 delay 31/32 死、mihomo 拨号 i/o timeout。**经 TCP/TLS 直连通、中转机 TLS 证书正常（Let's Encrypt hk.catxstar.com）排除公司网络封锁/MITM，判定为机场侧线路故障**。已把本机配置修复到位（mode/端口/OpenAI 规则/TUN），机场恢复后 Codex 应立即可用。

### 现象与复现

- 现象：公司网络下 Codex 桌面端反复显示"重新连接"，发送/响应不工作；浏览器打开 Google/YouTube/ChatGPT 也失败，但 Bing（Microsoft 直连规则）正常。
- 复现证据（走代理 7897，浏览器 UA）：
  - `chatgpt.com/` → **exit 35 / HTTP 000**（SSL 握手失败）
  - `www.google.com/`、`www.youtube.com/` → **exit 35 / HTTP 000**
  - `www.bing.com/` → **HTTP 302**（命中 Microsoft 直连规则，直连成功）
  - `GET /rules` → 65 条、**无任何 openai/chatgpt 规则**，末尾 `Match → 节点选择`
  - `GET /proxies/节点选择` → `now = 🇸🇬|新加坡-IEPL 02`（FAQ 已知坏线路）

### 根因分析（与 08-09 复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 分流规则 | **5 条 OpenAI 规则第 5 次被订阅更新清除** | `/rules` 65 条出厂版、无 openai/chatgpt；config.yaml rules 段 `MATCH, 节点选择` |
| 配置持久化 | 文件 `mode: direct` + **`external-controller: 39797`** | config.yaml 第 4/6 行（运行态 rule/39798，两者脱节） |
| DNS 层 | <span style="color:#ff0000">**mihomo 解析 chatgpt.com 得到污染 IP**</span> | `GET /dns/query?name=chatgpt.com` → `108.160.166.9`（非 Cloudflare）；日志 `chatgpt.com:443 match GeoIP/cn → DIRECT → dial tcp 118.193.240.41:443: i/o timeout` |
| 节点层 | <span style="color:#ff0000">**机场节点全部故障**</span> | delay 32 节点仅 1 存活（美国-直连）；trojan 探测中转 TLS 失败、IEPL 返回 nginx 蜜罐页 |
| 环境层 | 公司网络 | 排除：TCP/TLS 到中转机均连通；中转机证书正常 |

> [!warning] ⚠️ 关键认知（新变体）
> 既往复发（08-08/08-09）是"订阅清规则 + 节点切坏线路"，本次新增 **"机场节点整体故障"** 维度：**mihomo delay 全 503 ≠ 配置问题**，必须独立验证节点本身。判定方法：**TCP 直连中转机 → TLS 握手 → trojan 隧道探测**，若 TCP/TLS 通但 trojan 转发返回 nginx 欢迎页 → 机场中转机转发失效（机场侧问题，非本机/公司网络）。本机配置修复无法让机场恢复，只能把配置修到"机场恢复后立即可用"。

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260810-company-before.yaml`（SHA256 5cc0584d75667a87）。
2. **改配置**（沿用 06 文档方案 + 修复端口脱节）：
   - `mode: direct` → `mode: rule`；
   - `external-controller: 127.0.0.1:39797` → `127.0.0.1:39798`；
   - `GEOIP, CN, DIRECT` 前加 5 条 OpenAI 规则 → `🇺🇸|美国-IEPL 02`；
   - 兜底 `- MATCH, 节点选择` → `- MATCH, 🇭🇰|香港-IEPL 01`；
   - ⚠️ 踩坑：插入规则初始用 4 空格缩进导致 YAML 嵌套错误，改为 2 空格对齐后正常。
3. **热加载**：`PUT /configs?force=true` body=`{"path":"C:/Users/asus/.config/com.vortex.helper/config.yaml"}` → **HTTP 204**。
4. **恢复 TUN**：热加载后 `tun.enable` 回落到 false（配置文件恒为 false），`PATCH /configs {"tun":{"enable":true}}` → **HTTP 204**（恢复用户此前运行态）。

### 验证结果

| 验证项 | 结果 |
|---|---|
| `GET /configs` | mode=rule、mixed-port 7897、tun.enable=true ✅ |
| `GET /rules` | 70 条；openai.com/chatgpt.com/chatgpt-api.com → 🇺🇸 美国-IEPL 02；MATCH → 🇭🇰 香港-IEPL 01 ✅ |
| 配置持久化 | `mode: rule`、`external-controller: 39798`（重启不回退）✅ |
| 走代理 chatgpt.com | 仍 exit 35 ⚠️（**机场节点故障，非配置问题**） |

### 本次新增遗留事项

1. <span style="color:#ff0000">**机场节点整体故障**（2026-08-10 15:50 时点）</span>：中转/直连 TLS 失败、IEPL trojan 转发短路（返回 nginx 欢迎页）。**需联系机场确认线路状态，本机无法修复**。机场恢复后本机配置已就绪，Codex 应立即可用。
2. **订阅更新第 5 次清规则**（08-08 19:56 / 22:20 / 08-09 00:28 / 21:04 / 08-10 09:17）。再遇"Codex 反复重连"固定排查：① `/rules` 有无 openai 规则（无→订阅又清了）→ ② `节点 delay` 是否全 503（是→机场故障，先验证 trojan 隧道再等恢复）→ ③ chatgpt.com 是否被 DNS 污染走 DIRECT（`dns/query` 查）。
3. <span style="color:#ff8c00">**chatgpt.com DNS 污染**</span>：mihomo 用 alidns DoH（国内）解析 chatgpt.com 得到非 Cloudflare IP。恢复 OpenAI 域名规则（走代理后境外解析）可绕开；若再次出现 `match GeoIP/cn` 直连 chatgpt.com，可在 config.yaml hosts 固定 Cloudflare IP。
4. 配置备份已更新至 `原始文件备份/vortex-config-20260810-company-before.yaml`（修复前）。

### 🧪 确证补充（2026-08-10 16:10）：机场节点故障的完整证据链

> [!SUMMARY] 📌 补充结论
> 用户对"机场故障"结论存疑、要求彻底修复后，本轮做了**全链路铁证验证**，确认 <span style="color:#ff0000">**机场侧 trojan 服务整体塌缩，本机无法修复**</span>。此前最大的矛盾点——"Python 直连中转机 TCP 成功但 mihomo 拨号 i/o timeout"——已解开：<span style="color:#1e90ff">mihomo 的"dial"含 TLS 握手，而中转机 TLS 后不跑 trojan 服务（返回 nginx 欢迎页），故表现为超时</span>；Python 只做纯 TCP connect（成功），两者并不矛盾。本机配置已修复到"机场恢复后立即可用"，**需联系机场恢复线路**。

**🔬 证据链（16:00-16:10 实测）**

| # | 验证项 | 结果 | 结论 |
|---|---|---|---|
| 1 | mihomo DIRECT 出站 | 百度经代理 200 / 98ms | ✅ mihomo 进程出站健康 |
| 2 | Python/PowerShell/openssl 直连中转机 | 5 类节点 TCP+TLS 全部成功（46~1139ms） | ✅ 非公司网络封锁/GFW |
| 3 | **合法 trojan 握手**（SHA224密码+CMD+ATYP+ADDR+PORT） | 美国IEPL02/香港IEPL01/香港中转01/香港直连/新加坡IEPL02 **全部返回 `HTTP/1.1 200 OK Server: nginx` 标准欢迎页（711B）** | 🔴 **中转端口非 trojan 服务** |
| 4 | TLS 证书 SNI 比对 | 请求 `US.catxstar.com`/`r.hk2.cat.bilibili.com` 等 → 全部返回 **`CN=hk.catxstar.com` 同一默认证书** | 🔴 **中转服务器 vhost 路由塌缩为单一默认站点** |
| 5 | 多解析器（阿里/腾讯 DoH） | 节点域名均解析同一批 IP，无健康备用 | ✅ 无 DNS 换 IP 路径 |
| 6 | 刷新订阅 | 订阅域名直连 TCP 通但 TLS 被 SNI 阻断（HTTP 000）；代理又全挂 | ⛔ 无法从本机获取新节点 |
| 7 | 日志时间线 | 节点拨号错误 09:10 后消失（10:00 基本可用），12:00 起直连类错误突增 | 机场约在午间塌缩，与"刚刚还能用"吻合 |

**🎯 判定方法沉淀（下次复用）**：验证"机场是否真的挂了"只需 3 步——
1. `openssl s_client -connect <中转机IP>:<端口> -servername <节点SNI> -brief` → 看证书 CN 是否与该节点应返回的域名一致（美国节点返回 hk.catxstar.com = vhost 塌缩）；
2. 用**合法 trojan 格式**（`sha224hex(密码)\r\n + \x01\x03 + len(host)+host + port_be`）发 CONNECT → 若收到 `Server: nginx` 欢迎页 = trojan 服务被短路；
3. 对比多节点：若"国内中转"与"海外直连"节点**全部**返回同一默认证书/欢迎页 → 机场侧整体故障，非单线问题。

> [!warning] ⚠️ 对"Python 直连成功"的误判教训
> 纯 TCP `socket.create_connection` 成功 ≠ trojan 隧道可用。中转机能 TCP/TLS 握手（机场保活探测、或蜜罐伪装），但**不跑 trojan 转发**。判断隧道是否可用，必须发送**合法 trojan CONNECT 请求**看是否被转发，只看 TCP/TLS 连通性会被假象误导（本次 15:50 首诊后曾因 Python TCP 成功而一度怀疑机场结论，实为 TLS 层后无 trojan 服务）。

**✅ 本机最终状态（机场恢复后立即可用）**
- [x] `mode: rule`、`external-controller: 39798`（配置持久化，重启不回退）
- [x] 5 条 OpenAI 分流规则 → 美国-IEPL 02；`MATCH` → 香港-IEPL 01
- [x] `tun.enable: true`（已恢复用户此前运行态）
- [x] 配置备份：`原始文件备份/vortex-config-20260810-company-before.yaml`（SHA256 `5cc0584d75667a87`）

**📞 用户行动项**：<span style="color:#ff0000">**联系机场客服/频道，反馈"所有 trojan 节点在握手后返回 nginx 欢迎页、且所有节点证书统一为 hk.catxstar.com（vhost 塌缩）"**</span>。这是机场侧中转机配置/线路故障，本机无法修复。机场恢复后，无需再改任何配置，Codex 直接可用。

### ✅ 修复确认（2026-08-10 16:35）：IEPL/中转全挂但「直连」节点可用，切到 🇺🇸 美国-直连后 Codex 恢复

> [!SUMMARY] 📌 突破结论
> 16:10 判定"机场全挂"后，用户再次要求修复。全量测试 36 个节点发现：**国内中转/ IEPL 系列仍全部故障（nginx 欢迎页），但「直连」系列有 2 个恢复**——<span style="color:#1e90ff">🇹🇼 台湾-直连（149ms）与 🇺🇸 美国-直连（232ms）</span>。其中 **🇺🇸 美国-直连（出口 23.172.200.76，美国加州 Radishcloud）可正常连通 OpenAI 全部端点**（`codex/models` 401、`codex/responses` 401、`ws.chatgpt.com` 404 可达），台湾-直连到 OpenAI 却 503/504（不通）。<span style="color:#ff0000">已将 5 条 OpenAI 规则与 MATCH 兜底全部改指 🇺🇸 美国-直连，重启 Codex 后连接全部走新节点、无任何错误，Codex 恢复可用。</span>

**🔬 关键诊断（为什么 delay 测节点通但 curl 502）**

| 现象 | 原因 |
|---|---|
| `/delay` 直测 🇺🇸 美国-直连到 chatgpt.com = 944ms / api.openai.com = 282ms ✅ | delay 接口绕过规则引擎**直接测节点** |
| 经代理 curl 仍 502/000 | 运行态规则 `MATCH → 🇭🇰 香港-IEPL 01`（坏节点）把流量引到死线，**与节点无关** |
| 教训 | **切换节点后必须同时改运行态规则**；判断"节点能不能用"用 `/delay?url=<目标>` 直测，判断"流量走哪"看 `/rules` |

**🔬 节点可用性复核（16:35 全量）**

| 节点 | delay | OpenAI 连通 | 结论 |
|------|:---:|:---:|------|
| 🇺🇸 美国-直连（dd.ioioioioioio.com:41613, SNI d.usq1） | 232ms | ✅ chatgpt 944ms / api.openai 282ms | <span style="color:#1e90ff">**推荐（已启用）**</span> |
| 🇹🇼 台湾-直连（dd.ioioioioioio.com:19135, SNI d.twq1） | 149ms | ❌ 503/504 | 快但 OpenAI 不通，留作备用 |
| 其余 34 个节点（IEPL/中转/家宽等） | 全部 503 | ❌ | 仍挂（nginx 欢迎页） |

**🛠️ 本次修复动作**
1. 全量 delay 测试 36 节点 → 锁定 2 个可用直连节点。
2. `节点选择` 手动切到 🇺🇸 美国-直连（运行态，用于 Match 兜底）。
3. 备份后编辑 `config.yaml`：5 条 OpenAI 规则 `美国-IEPL 02` → <span style="color:#1e90ff">`🇺🇸|美国-直连`</span>；`MATCH` → `🇺🇸|美国-直连`。备份：`原始文件备份/vortex-config-20260810-1620-before-switch-to-direct.yaml`（SHA256 `e83e87b1...`）。
4. `PUT /configs?force=true` 热加载 → 运行态 70 条规则生效（OpenAI→美国-直连）。
5. 热加载后 TUN 回落 false，`PATCH /configs {"tun":{"enable":true}}` 恢复。
6. 杀全部 ChatGPT.exe / codex.exe / node_repl.exe 后重启 Codex（版本已升级 26.803.5235.0）。

**✅ 验证结果**
- [x] `codex/models` 401、`codex/responses` 401、`ws.chatgpt.com` 404（全端点放行，非 403 风控）
- [x] 重启后 144 条 ChatGPT/codex 连接全部走 🇺🇸 美国-直连，**0 错误**
- [x] 配置持久化（文件已改，重启不回退）：OpenAI 5 规则 + MATCH → 美国-直连
- [x] TUN=true 恢复
- 出口 `23.172.200.76`（美国加州）；主页 `chatgpt.com` 首页 403 `Cf-Mitigated: challenge` 属浏览器 CF 挑战，不影响 API 端点

**⚠️ 遗留与提醒**
1. <span style="color:#ff8c00">**IEPL/中转节点仍全挂**（nginx 欢迎页），机场侧未恢复</span>；当前靠「美国-直连」支撑，若该节点质量波动，Codex 可能再次重连。可定期 `GET /proxies/{美国-直连}/delay?url=https://api.openai.com/v1/models` 复查。
2. 台湾-直连虽快但 OpenAI 不通（可能被 CF 风控），**勿作为 Codex 节点**。
3. 若机场恢复 IEPL 线路，可切回美国-IEPL 02（原唯一放行节点）；本文件 08-06 速查表仍适用。
4. 订阅再更新可能再次清规则/改节点名，届时按「08-10 15:50 复发记录」的排查清单处理。

## 🔁 复发记录（2026-08-10 18:01）：GPT 网页版 PR_END_OF_FILE_ERROR——订阅清规则 + mode direct（机场已恢复，纯配置问题）

> [!SUMMARY] 📌 本次复发结论
> 用户在公司网络反馈"浏览器访问 GPT 网页版报 <span style="color:#ff0000">`PR_END_OF_FILE_ERROR`（建立安全连接失败）</span>"。三层诊断定位为**纯配置问题（第 6 次订阅清规则复发）**，与 15:50 时点相比**机场线路已恢复**：① <span style="color:#ff8c00">**订阅更新再次重写 config.yaml**</span>——`mode` 还原 `direct`、`external-controller` 改回 `39797`（运行态 39798）、5 条 OpenAI 规则被清（`/rules` 65 条出厂版）、`MATCH → 节点选择`（当前指向坏节点 `🇭🇰|香港-IEPL 01`）、`tun.enable=false`；② <span style="color:#ff0000">**`mode: direct` 下 chatgpt.com 命中 `GEOIP,CN,DIRECT` 直连被 GFW 阻断**，TLS 连接被对端关闭 → 浏览器报 PR_END_OF_FILE_ERROR</span>；③ <span style="color:#1e90ff">**机场节点已恢复**（实测美国-IEPL 01/02、美国-直连、台湾-直连、日本-IEPL 02 均可连通 OpenAI，api.openai.com 401 / chatgpt.com 200）</span>，与 15:50"机场全挂"不同。已修复配置：`mode→rule`、端口→39798、恢复 5 条 OpenAI 规则→`🇺🇸|美国-IEPL 02`、`MATCH→🇭🇰|香港-IEPL 01`、热加载、恢复 TUN。验证 chatgpt.com 302、api.openai.com 401、google.com 302 全通。

### 现象与复现

- 现象：公司网络下浏览器（Firefox）访问 GPT 网页版报 `PR_END_OF_FILE_ERROR`（建立安全连接失败 / 由于不能验证所收到的数据是否可信），Codex/桌面端同样无法使用。
- 复现证据（走代理 7897，浏览器 UA）：`chatgpt.com/` → **exit 35 / HTTP 000**（SSL 握手失败）；`api.openai.com/v1/models` → **exit 35 / HTTP 000**；`GET /configs` → `mode: direct`、`tun.enable: false`；`GET /rules` → 65 条、无任何 openai/chatgpt 规则、末尾 `Match → 节点选择`；`节点选择` now = `🇭🇰|香港-IEPL 01`（历史已知对 OpenAI 403 风控的坏线路）。

### 根因分析（与 15:50 复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 配置持久化 | `mode: direct` + `external-controller: 39797`（与运行态 39798 脱节） | config.yaml 第 4/6 行；`/configs` 运行态 rule/39798 |
| 分流规则 | **5 条 OpenAI 规则第 6 次被订阅更新清除** | `/rules` 65 条出厂版；config.yaml rules 段无 openai/chatgpt |
| 路由层 | `mode: direct` → chatgpt.com 命中 `GEOIP,CN,DIRECT` 直连被 GFW 阻断 | TLS 连接被对端关闭 → `PR_END_OF_FILE_ERROR`；curl exit 35 |
| 节点层 | **机场已恢复**（非故障） | 实测美国-IEPL 01/02、美国-直连、台湾-直连、日本-IEPL 02 到 api.openai.com 均 401、chatgpt.com 200 |
| 坏线路 | `节点选择` 当前指向 `🇭🇰|香港-IEPL 01`（对 OpenAI 403 风控） | 切该节点走代理 curl：api 403 / chatgpt 403 |

> [!warning] ⚠️ 关键认知（新变体）
> **`PR_END_OF_FILE_ERROR`（TLS 连接被对端突然关闭）是"直连被墙"的浏览器表现**——当 `mode: direct` 且无 OpenAI 规则时，chatgpt.com 走直连被 GFW 断开，浏览器渲染成"建立安全连接失败 / PR_END_OF_FILE_ERROR"。这与 Codex 的 `stream disconnected` / curl 的 `exit 35` 是**同一根因（配置被清 → 直连）的不同形态**，符合"同一根因 4 种报错"规律。判断依据：先查 `/configs` mode（是 direct 就是配置被清），再查 `/rules` 有无 openai 规则。

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260810-1801-before.yaml`（SHA256 `88606fd1ebb1757bacd6535a969f21f817c521e10bd1964d95fdd831e13c6036`）。
2. **改配置**（Python UTF-8 安全写入，避开 emoji 节点名 GBK 乱码坑）：
   - `mode: direct` → `mode: rule`；
   - `external-controller: 127.0.0.1:39797` → `127.0.0.1:39798`；
   - `GEOIP, CN, DIRECT` 前加 5 条 OpenAI 规则 → `🇺🇸|美国-IEPL 02`；
   - 兜底 `- MATCH, 节点选择` → `- MATCH, 🇭🇰|香港-IEPL 01`。
3. **热加载**：`PUT /configs?force=true` body=`{"path":"C:/Users/asus/.config/com.vortex.helper/config.yaml"}` → **HTTP 204**。
4. **恢复 TUN**：热加载后 `tun.enable` 回落 false（配置文件恒为 false），`PATCH /configs {"tun":{"enable":true}}` → **HTTP 204**。

> [!note] 💡 本次踩坑
> mihomo 控制 API 切换节点用 **PUT**（`PUT /proxies/节点选择`，body=`{"name":"<节点>"}`），PATCH 会返回 405；且 URL 路径中文（策略组名）必须 quote，而 body 里的目标节点名**不要**编码——一开始把目标节点名编码进路径导致 PUT 400。

### 验证结果

| 验证项 | 结果 |
|---|---|
| `GET /configs` | mode=rule、mixed-port 7897、tun.enable=true ✅ |
| `GET /rules` | 70 条；openai.com/chatgpt.com/chatgpt-api.com/oaistatic.com/oaiusercontent.com → 🇺🇸 美国-IEPL 02；MATCH → 🇭🇰 香港-IEPL 01 ✅ |
| 配置持久化 | `mode: rule`、`external-controller: 39798`（重启不回退）✅ |
| 走代理 chatgpt.com | **302**（正常重定向，可访问）✅ |
| 走代理 api.openai.com | **401**（正常未认证响应）✅ |
| 走代理 google.com | 302（外网正常）✅ |

### 本次新增遗留事项

1. <span style="color:#ff0000">**订阅更新清规则已累计 6 次**（08-08 19:56 / 22:20 / 08-09 00:28 / 21:04 / 08-10 09:17 / 08-10 18:01）</span>。再遇"外网打不开 / PR_END_OF_FILE_ERROR / Codex 重连"固定排查三步：① `GET /configs` 查 mode（direct=配置被清）→ ② `GET /rules` 查有无 openai 规则（无=订阅又清了）→ ③ 实测节点 delay + 走代理 curl 确认可用节点后重写配置。
2. <span style="color:#1e90ff">**机场线路已恢复**</span>（美国-IEPL 01/02、美国-直连、台湾-直连、日本-IEPL 02 实测可用）。OpenAI 规则可继续用 `🇺🇸|美国-IEPL 02`（原推荐放行节点），若其波动可换美国-IEPL 01 / 美国-直连。
3. `PR_END_OF_FILE_ERROR` 新增为"同一根因 4 种形态"的一种浏览器表现（与 Codex `stream disconnected`、curl `exit 35`、`ERR_CONNECTION_RESET` 并列）。
4. 配置备份已更新至 `原始文件备份/vortex-config-20260810-1801-before.yaml`（修复前）。

## 🔁 复发记录（2026-08-10 19:54）：回公寓后外网断——第 7 次订阅清规则 + 一键修复脚本落地（彻底修复方案）

> [!SUMMARY] 📌 本次复发结论
> 用户从公司回到公寓后外网又断。诊断确认**第 7 次订阅清规则复发**，但形态有变化：<span style="color:#ff8c00">**配置文件已被订阅更新覆盖回出厂版**（`mode: direct`、`external-controller: 39797`、65 条出厂规则、`MATCH → 节点选择`、`tun: false`），而**运行态仍残留 18:01 的 rule 内存设置**（文件与运行态脱节）</span>——此时运行态规则缺 OpenAI 5 条，chatgpt.com 掉进 `MATCH → 节点选择 → 🇭🇰|香港-IEPL 01`（对 OpenAI 403 风控），浏览器无法访问 GPT。**公寓网络下机场节点正常**（美国-IEPL 01/02、美国-直连、日本-IEPL 02 实测均 401/200）。已按同方案修复并验证。**本次新增彻底修复措施：落地一键修复脚本 `scripts/fix_vortex_config.py`**（备份→改配置→热加载→恢复TUN→验证，幂等），后续订阅再清规则运行脚本 5 秒恢复。

### 现象与复现

- 现象：回到公寓（🏠）后浏览器无法连接外网（GPT 网页版不可达），Codex 同受影响。
- 复现证据：`GET /configs` → 运行态 mode=rule 但 tun=false；`GET /rules` → 65 条（无 OpenAI 规则）、MATCH→节点选择；配置文件第 4 行 `mode: direct`、第 6 行 `external-controller: 39797`（**与运行态 39798 脱节**，一旦 Vortex 重启/热加载即回退 direct）。

### 根因分析（与 18:01 的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 配置持久化 | **订阅更新第 7 次覆盖 config.yaml 为出厂版**（mode direct + 39797 + 65 规则 + TUN false） | 配置文件 4/6/1288/1293 行；`/rules` 65 条 |
| 运行态脱节 | 运行态残留 18:01 的 rule（未重启），但规则段已被热加载前的文件状态影响 | 运行态 mode=rule vs 文件 mode=direct 不一致 |
| 路由层 | 运行态缺 OpenAI 规则 → chatgpt.com 掉 `MATCH → 节点选择 → 香港-IEPL 01`（403 风控） | 走代理 curl chatgpt.com 403 |
| 节点层 | 公寓网络下机场节点正常（非故障） | 美国-IEPL 01/02、美国-直连、日本-IEPL 02 → api 401 / chatgpt 200 |
| TUN | 热加载/更新后 tun.enable 回落 false | `/configs` tun.enable=false |

> [!warning] ⚠️ 关键认知（脱节陷阱）
> **"运行态 mode=rule 但外网仍不通" ≠ 配置没问题**——`/configs` 显示的是运行态内存，`config.yaml` 才是持久化真相。订阅更新覆盖的是**文件**；若 Vortex 尚未重启/热加载，运行态仍是旧配置，此时表现是"规则缺 OpenAI 5 条"（65 条）。**判断必须同时看文件与运行态**：文件 `mode: direct` 就是订阅已覆盖，Vortex 一重启就全断。

### 修复过程

1. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260810-1954-apartment-before.yaml`（SHA256 `02cea7a0abb2ea41fca875e1ead1d1cabf5607dbca742a2f610447d072bf713b`）。
2. **改配置**（同 18:01 方案，Python UTF-8 安全写入）：`mode→rule`、`external-controller→39798`、恢复 5 条 OpenAI 规则→`🇺🇸|美国-IEPL 02`、`MATCH→🇭🇰|香港-IEPL 01`。
3. **热加载** 204 + **恢复 TUN** 204。
4. **彻底加固（新增）**：创建一键修复脚本 `总结好的大纲以及笔记/知识库FAQ/scripts/fix_vortex_config.py`——自动备份→检查/修复 mode/端口/OpenAI规则/MATCH→热加载→恢复TUN→验证，**幂等**（已良好时提示"无需修改"）。实测运行通过。

### 验证结果

| 验证项 | 结果 |
|---|---|
| `GET /configs` | mode=rule、port 7897、tun.enable=true ✅ |
| `GET /rules` | 70 条；OpenAI 5 规则→美国-IEPL 02；MATCH→香港-IEPL 01 ✅ |
| 一键脚本幂等 | 重跑报"无需修改（已良好）"，热加载/TUN 全 204 ✅ |
| 走代理 chatgpt.com | **200** ✅ |
| 走代理 api.openai.com | **401** ✅ |
| 走代理 google / youtube | 302 / 200 ✅ |

### 彻底修复方案（本次沉淀）

1. <span style="color:#1e90ff">**一键修复脚本**：`总结好的大纲以及笔记/知识库FAQ/scripts/fix_vortex_config.py`</span>。再遇"外网断 / PR_END_OF_FILE_ERROR / Codex 重连"：先 `curl -s http://127.0.0.1:39798/rules | grep -c openai`（0=订阅又清了）→ 运行脚本 → 5 秒恢复。**这是当前最可靠的根治手段**。
2. <span style="color:#ff8c00">**建议在 Vortex GUI 关闭"自动更新订阅"**</span>（或把更新间隔调到很长）：Vortex 主界面 → 订阅/设置 → 自动更新，关闭即可从源头避免 config.yaml 被反复覆盖。GUI 内部状态文件（`.store.json`/`cache.db`）格式不透明，**不要手动改**。
3. 订阅更新把节点名/列表改写时，若脚本指向的节点消失（`proxy not found`），按 04 文档 08-06 速查表重新实测节点后修改脚本顶部的 `OPENAI_NODE`/`MATCH_NODE`。
4. 已知良好配置备份：`原始文件备份/vortex-config-20260810-1955-before-fix.yaml`（脚本自动备份的修复后状态）。

### 🔁 复发速记（2026-08-10 21:32）：第 8 次订阅清规则——一键脚本 5 秒恢复，Codex 重启后正常

> [!SUMMARY] 📌 速记
> 用户 21:32 反馈"Codex 又重连"。诊断：`/rules` 65 条、OpenAI 规则 0、TUN false、配置文件 `mode: direct`/`39797`——**第 8 次订阅清规则**（19:55 修复后又覆盖）。直接运行一键脚本 `scripts/fix_vortex_config.py`：自动备份（`vortex-config-20260810-2132-before-fix.yaml`）→ 修复 mode/端口/OpenAI规则/MATCH → 热加载 204 → 恢复TUN 204 → 验证 mode=rule/tun=True。随后 `codex/models` 401 放行、重启 Codex（杀 ChatGPT.exe/codex.exe 后经 `shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App` 拉起）、codex.exe 15+ 条连接走 7897、日志 connected 无错误。<span style="color:#1e90ff">**一键脚本已证明有效：从发现到恢复 < 1 分钟。**</span>

> [!warning] ⚠️ 复发频率提示
> 订阅清规则已累计 **8 次**（08-08 ×3 / 08-09 ×1 / 08-10 ×4），当天内最多 3 次。**强烈建议在 Vortex GUI 关闭"自动更新订阅"**（主界面→订阅→自动更新→关闭），否则会持续反复。若无法关闭，固定流程 = 报错 → 跑 `fix_vortex_config.py` → 重启 Codex。

## 🔁 复发记录（2026-08-06）：出口 IP 被 Cloudflare 风控

> [!SUMMARY] 📌 本次复发结论
> 代理客户端已从 Rocket 更换为 <span style="color:#ff8c00">Vortex（端口 7897，TUN 模式）</span>，但 Vortex 默认节点 <span style="color:#ff0000">「🇭🇰 香港-IEPL 01」（出口 45.67.201.103）被 Cloudflare 对 OpenAI 域名风控</span>：`GET /backend-api/codex/models` 返回 403 拦截页（cf-ray 落点 HKG），`POST /backend-api/codex/responses` 与 `/ps/mcp` 连接被重置 → 界面表现为 <span style="color:#ff0000">`stream disconnected before completion: error sending request for url (https://chatgpt.com/backend-api/codex/responses)`</span>。切换至 <span style="color:#1e90ff">「🇺🇸 美国-IEPL 02」（出口 38.45.155.83）</span> 并重启 Codex 后恢复，01:42 后日志无任何 403。

### 🧩 本次根因（与 08-04 对比）

| 层级 | 08-04 根因 | 08-06 根因 | 处置 |
|---|---|---|---|
| 环境层 | 系统 DNS 污染 + Rocket(4780) 出口不稳 | 代理客户端换成 <span style="color:#ff8c00">Vortex(7897)</span>，Rocket 退出；Codex 遥测仍残留连接 <span style="color:#ff8c00">4780</span>（ConnectionRefused，仅影响指标上传，不影响主功能） | 无需改 DNS（Vortex 已接管）；4780 残留记录为遗留项 |
| 网络层 | 美国 02 出口连接重置 | <span style="color:#ff0000">香港-IEPL 01 出口 IP 被 Cloudflare 风控</span>：403 拦截页 + POST 断流；批量实测 22 个节点中 18 个 403/断流 | 切至美国-IEPL 02（唯一 200 OK） |
| 会话层 | 旧长连接黏在旧线路 | Codex 旧进程缓存旧代理/请求被重置 | 切换节点后重启 Codex 桌面端，连接全部重建 |

### 🔬 本次诊断数据

- 现场日志（`C:\Users\asus\.codex\logs_2.sqlite`）：01:34 `unexpected status 403 Forbidden ... url: https://chatgpt.com/backend-api/codex/models?client_version=0.146.0, cf-ray: a2678de44a6d8a4c-HKG`（Cloudflare 拦截页）；01:34~01:35 `/backend-api/ps/mcp` 反复 `error sending request`；01:13~01:38 遥测每 3 分钟连 `127.0.0.1:4780` ConnectionRefused。
- 节点实测（Vortex 控制 API `127.0.0.1:39798` 批量切换 + curl 测 chatgpt.com）：日本原生×5、台湾家宽×2、台湾 IEPL×2、香港家宽×3、香港 IEPL×2、美国 IEPL 01、新加坡 IEPL×3 均 <span style="color:#ff0000">403 或 SSL 断流</span>；<span style="color:#1e90ff">「🇺🇸 美国-IEPL 02」200 OK，切后 `codex/models`、`codex/responses` 均返回 401（正常未认证响应）</span>。
- 进程证据：新 Codex 进程（PID 42592）启动后与 `127.0.0.1:7897` 建立 4 条 Established 连接；01:42 后日志 292 条中无 403，模型列表刷新成功。

### 🛠️ 本次修复过程

1. 确认代理客户端已由 Rocket(4780) 换成 Vortex(7897，TUN 模式，DNS fake-IP `198.18.0.x`）。
2. 从 Codex 日志定位 403 拦截页（cf-ray HKG）→ 锁定出口 IP 风控。
3. 经 Vortex 控制 API（`http://127.0.0.1:39798`，mihomo 1.10.0）批量切换 22 个候选节点实测。
4. 将「节点选择」策略组固定为 <span style="color:#1e90ff">🇺🇸 美国-IEPL 02</span>（`PUT /proxies/节点选择 {"name":"🇺🇸|美国-IEPL 02"}`）。
5. 重启 Codex 桌面端（杀全部 ChatGPT.exe / codex.exe / node_repl.exe 后经 `shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App` 拉起）。
6. 验证新进程日志无 403、连接走 7897。

### ✅ 本次验证结果

- [x] 节点已固定为美国-IEPL 02（GLOBAL → 节点选择 → 美国-IEPL 02），出口 38.45.155.83。
- [x] 从该出口实测 `codex/models`、`codex/responses` 返回 401（放行）。
- [x] Codex 重启后 01:42~01:45 日志 292 条，**无任何 403 / codex/responses 连接错误**。
- [x] 模型列表刷新成功（无 `unexpected status 403`）。
- [x] 新进程 4 条连接 Established 至 `127.0.0.1:7897`。

### 🛡️ 遗留事项与提醒

1. <span style="color:#ff8c00">遥测残留</span>：opentelemetry 指标导出仍尝试连 `127.0.0.1:4780`（Rocket 旧端口，ConnectionRefused，每 3 分钟一次 DEBUG 日志）。来源未定位（不在环境变量/配置文件中），疑为 Codex 内部缓存的旧系统代理；**仅影响遥测指标上传，不影响使用**，暂不处理。
2. <span style="color:#ff8c00">偶发 EOF</span>：01:43 插件目录列表出现一次空响应（EOF），未复现，列为观察项。
3. 机场订阅更新可能改节点列表/质量，**若 Codex 再报 stream disconnected，先查当前出口 IP 是否被风控**：`curl -x http://127.0.0.1:7897 -I https://chatgpt.com`，403 拦截页即风控，按本文档步骤切节点。
4. 切换节点会瞬时中断本机所有代理流量，建议在低峰操作。

### 📡 网络体检与节点复查（2026-08-06 09:50 上午）

> [!SUMMARY] 📌 复查结论
> 用户确认 Codex 恢复正常使用后，执行全量网络质量体检发现：节点已被 <span style="color:#ff8c00">Vortex「自动节点」切回「🇸🇬 新加坡-IEPL 02」</span>（该线路全线 SSL 断流，外网请求全部 5s 超时、SSL error 35，不可用）。切回 <span style="color:#1e90ff">🇺🇸 美国-IEPL 02</span> 后，9 个主流外网站 8 个 HTTP 200、仅 Google 429 限流，ChatGPT/Codex 关键端点正常。<span style="color:#ff0000">美国-IEPL 02 是当前唯一同时满足「ChatGPT 风控放行」+「外网全通」的节点，应手动固定。</span>

**为什么节点会变？** Vortex 存在「自动节点」策略组，会自动切换到机场中当时测速较优的线路；而新加坡-IEPL 全线（01/02/03）此前批量实测即为 SSL 断流，属于机场质量差的线路。

**外网连通性实测（美国-IEPL 02，出口 `38.45.155.83`，走代理 7897）**：

| 网站 | 状态码 | 延迟 | 结论 |
|------|-------|------|------|
| Google | 429 | 2.1s | ⚠️ 限流（数据中心 IP，非断流） |
| YouTube | 200 | 1.2s | ✅ 正常 |
| GitHub | 200 | 1.0s | ✅ 正常 |
| NVIDIA | 200 | 2.4s | ✅ 正常 |
| OpenAI | 200 | 1.0s | ✅ 正常 |
| ChatGPT | 200 | 1.1s | ✅ 正常 |
| Bing | 200 | 0.3s | ✅ 最快 |
| X/Twitter | 200 | 1.0s | ✅ 正常 |
| Wikipedia | 200 | 1.4s | ✅ 正常 |

**稳定性**：Google 连测 5 次全部稳定响应（429 是频率限制，非连接重置）→ 线路稳定。

**Codex 关键端点**：`codex/models` → 401，`codex/responses` → 405（均已到达后端，正常放行）。

**🛡️ 节点可用性速查表（供快速决策）**：

| 节点 | ChatGPT 风控 | 外网连通 | 结论 |
|------|:---:|:---:|------|
| <span style="color:#1e90ff">🇺🇸 美国-IEPL 02</span>（38.45.155.83） | ✅ 放行(401) | ✅ 全通 | <span style="color:#1e90ff">**推荐手动固定**</span> |
| 🇸🇬 新加坡-IEPL 01/02/03 | ❌ SSL 断流 | ❌ | 不可用 |
| 🇭🇰 香港-IEPL 01 / 家宽系列 | ❌ 403 拦截 | ⚠️ 部分通 | 不可用于 ChatGPT |
| 🇯🇵 日本原生 / 日本-IEPL | ❌ 403 | ⚠️ 部分通 | 不可用于 ChatGPT |
| 🇹🇼 台湾-IEPL / 家宽 | ❌ 403 或断流 | ⚠️ 部分通 | 不可用于 ChatGPT |
| 🇺🇸 美国-IEPL 01 | ❌ 403 | ⚠️ | 不可用 |

**建议**：
1. 在 Vortex 中把「节点选择」<span style="color:#ff8c00">手动固定为 美国-IEPL 02</span>，或关闭「自动节点」，避免自动切回新加坡等坏线路。
2. Google 429 属出口 IP 限流，不影响 YouTube/ChatGPT 等；若日常重度用 Google，可临时切 🇯🇵/🇹🇼 线路，但会牺牲 ChatGPT 可用性——<span style="color:#ff0000">二者需权衡</span>。
3. 后续 Codex 再出问题，先按上方「复发记录」排查清单定位，再对照本速查表选节点。

## 🔁 复发记录（2026-08-11 10:01）：公司网络下 GPT 打不开——第 9 次订阅清规则 + mode direct + 端口脱节

> [!SUMMARY] 📌 复发摘要
> 用户在公司网络反馈"无法正常连接 GPT 和外网"。三层诊断确认 **第 9 次订阅清规则复发**（形态与 08-10 18:01 完全同款）：① <span style="color:#ff8c00">**订阅更新再次重写 config.yaml**</span>——5 条 OpenAI 规则被清（`/rules` 回 65 条出厂版、`MATCH → 节点选择`）、`mode` 还原 `direct`、`external-controller` 改回 `39797`（运行态 39798）；② <span style="color:#ff0000">**chatgpt.com 无 OpenAI 规则时掉进兜底 `MATCH → 节点选择 → 🇭🇰 香港-IEPL 01`（对 OpenAI 403 风控的历史坏线路）**</span> → 浏览器打开 GPT 返回 403；③ 实测 google/youtube 仍通（香港-IEPL 01 对普通网站可用），**美国-IEPL 02 对 OpenAI 放行**（codex/models 401、chatgpt.com 200）。运行一键脚本 `scripts/fix_vortex_config.py` 后：`mode→rule`、端口→39798、恢复 5 条 OpenAI 规则→`🇺🇸|美国-IEPL 02`、`MATCH→🇭🇰|香港-IEPL 01`、热加载、恢复 TUN。验证 chatgpt.com 200 / codex/models 401 / google 302 / youtube 200 全通。

### 现象与复现

- 现象：公司网络下浏览器打开 GPT 失败（**403**），Codex/桌面端同受影响；google/youtube 等普通外网可访问。
- 复现证据（走代理 7897，浏览器 UA）：
  - `chatgpt.com/` → **HTTP 403**（0.84s，Cloudflare 拦截）
  - `www.google.com/` → **302**、`www.youtube.com/` → **200**（外网基本通）
  - `GET /rules` → **65 条、无任何 openai/chatgpt 规则**，末尾 `Match → 节点选择`
  - `GET /proxies/节点选择` → `now = 🇭🇰|香港-IEPL 01`（对 OpenAI 403 风控的历史坏线路）

### 根因分析（与既往复发的对比）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 分流规则 | **5 条 OpenAI 规则第 9 次被订阅更新清除** | `/rules` 65 条出厂版；config.yaml rules 段无 openai/chatgpt、末尾 `- MATCH, 节点选择` |
| 配置持久化 | 文件 `mode: direct` + **`external-controller: 39797`**（与运行态 39798 脱节） | config.yaml 第 4/6 行；运行态 rule/39798 |
| 节点层 | 兜底 `节点选择` → 🇭🇰 香港-IEPL 01（对 OpenAI 403 风控），但 🇺🇸 美国-IEPL 02 对 OpenAI 放行 | 走代理实测：香港-IEPL 01 下 chatgpt 403；切美国-IEPL 02 后 codex/models **401**、chatgpt 首页 **200** |

> [!warning] ⚠️ 关键认知
> 本次与 08-10 18:01 **完全同款**（第 9 次订阅清规则）：现象是"GPT 403 打不开但普通外网基本通"。固定排查顺序不变：① `GET /configs` 查 mode（direct=配置被清）→ ② `GET /rules` 查有无 openai 规则（无=订阅又清了）→ ③ 节点 delay 体检 + **走代理实测目标端点（codex/models 401 判据）**。⚠️ 注意：切换节点后必须实测 HTTP 状态，不能只看 delay（delay 通 ≠ 对 ChatGPT 放行）。

### 修复过程

1. **备份**（脚本自动）：`config.yaml` → `原始文件备份/vortex-config-20260811-1001-before-fix.yaml`。
2. **节点体检**（`/proxies/{name}/delay?url=api.openai.com`）：存活=美国-IEPL 02（279ms）/ 美国-直连 / 美国-中转 01 / 日本-IEPL 01/02 / 香港-IEPL 01 / 台湾-直连；故障=美国-IEPL 01 / 美国-中转 02 / 香港-IEPL 03。
3. **运行一键脚本** `scripts/fix_vortex_config.py`：`mode→rule`、`external-controller→39798`、恢复 5 条 OpenAI 规则→`🇺🇸|美国-IEPL 02`、`MATCH→🇭🇰|香港-IEPL 01`、热加载 **204**、恢复 TUN **204**。
4. **验证**：mode=rule / port=7897 / tun=True；`/rules` 70 条。

### 验证结果

| 站点/端点 | 修复前 | 修复后 |
|---|---|---|
| chatgpt.com 首页 | 403 | **200**（2.04s） |
| codex/models | — | **401**（1.28s，放行非风控） |
| google.com | 302 | **302** ✅ |
| youtube.com | 200 | **200** ✅ |

- [x] `/rules` **70 条**；5 条 OpenAI 规则 → 🇺🇸 美国-IEPL 02；`MATCH` → 🇭🇰 香港-IEPL 01
- [x] `/configs.mode` = rule；tun=True；port=7897
- [x] 配置持久化（mode/端口已写入文件，重启不回退）

### 本次新增遗留事项

1. <span style="color:#ff0000">**订阅清规则已累计 9 次**（08-08 ×3 / 08-09 ×1 / 08-10 ×4 / 08-11 ×1）</span>。一键脚本 `fix_vortex_config.py` 再次验证有效：**从发现到恢复 < 1 分钟**。**强烈建议在 Vortex GUI 关闭"自动更新订阅"**（主界面→订阅→自动更新→关闭），从源头避免 config.yaml 被反复覆盖。
2. 当前 OpenAI 规则指向 🇺🇸 美国-IEPL 02（本次实测 401/200 放行）；若再 403 或该节点波动，按"规则在不在 → 节点活不活 → 走代理实测端点"三步排查，候选放行节点可实测 美国-直连 / 美国-中转 01 / 日本-IEPL 02。
3. 配置备份已更新至 `原始文件备份/vortex-config-20260811-1001-before-fix.yaml`（修复前）。

## 🔁 复发记录（2026-08-11 14:08）：第 10 次订阅清规则——OpenAI 规则再被清 + 脚本默认节点美国-IEPL 02 已不稳，改用美国-中转 01

> [!SUMMARY] 📌 复发摘要
> 用户反馈"网络都进不去了，Codex 也用不了"。三层诊断确认 **第 10 次订阅清规则复发**（形态与 08-11 10:01 完全同款）：① <span style="color:#ff8c00">**订阅更新再次重写 config.yaml**</span>——5 条 OpenAI 规则被清（`/rules` 回 65 条出厂版、`MATCH → 节点选择`）、`mode` 还原 `direct`、`external-controller` 改回 `39797`（运行态 39798）；② <span style="color:#ff0000">**chatgpt.com 掉进兜底 `MATCH → 节点选择 → 🇭🇰 香港-IEPL 01`（对 OpenAI 403 风控的历史坏线路）**</span> → 走代理实测 chatgpt.com / codex/models 均 **403**，浏览器与 Codex 全挂。**本次新增**：③ <span style="color:#ff8c00">**一键脚本默认的 `OPENAI_NODE`（🇺🇸 美国-IEPL 02）对 api.openai.com delay 504 超时、codex/models 5.66s 偏慢，已非最优**</span>——批量实测候选节点，**🇺🇸 美国-中转 01（delay 314ms + codex/models 401 1.38s）为当前最快稳定放行节点**，已更新脚本 `OPENAI_NODE`。运行一键脚本 + 重启 Codex 后恢复：codex/models 401（0.95s）、chatgpt.com 200（2.06s）、google 302 / youtube 200，8 条 OpenAI 活动连接全部走 🇺🇸 美国-中转 01。

### 现象与复现

- 现象：浏览器无法访问外网（GPT 打不开），Codex 桌面端用不了；进程在线但 OpenAI 活动连接 = 0。
- 复现证据（走代理 7897，浏览器 UA）：`chatgpt.com/` → **403**、`codex/models` → **403**；`GET /rules` → 65 条、无 openai/chatgpt、末尾 `Match → 节点选择`；`GET /proxies/节点选择` → `now = 🇭🇰|香港-IEPL 01`。

### 根因分析（与 08-11 10:01 第 9 次复发的区别）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 分流规则 | **5 条 OpenAI 规则第 10 次被订阅更新清除** | `/rules` 65 条出厂版；config.yaml rules 段无 openai/chatgpt、末尾 `- MATCH, 节点选择` |
| 配置持久化 | 文件 `mode: direct` + `external-controller: 39797`（与运行态 39798 脱节） | config.yaml 第 4/6 行；运行态 rule/39798 |
| 节点层 | 兜底 `节点选择` → 🇭🇰 香港-IEPL 01（对 OpenAI **403** 风控） | 走代理实测 chatgpt.com / codex/models 均 403 |
| 节点层（新增） | <span style="color:#ff8c00">**脚本默认 OpenAI 节点 美国-IEPL 02 已不稳**（api.openai.com delay 504 超时、codex/models 5.66s）</span> | delay 体检 + 走代理实测对比 |
| 会话层 | Codex 进程在线但 websocket 长连接未建立 | `/connections` OpenAI 相关 = 0 |

> [!warning] ⚠️ 关键认知（新增）
> **一键脚本的 `OPENAI_NODE` 不是永久的**：脚本默认 `🇺🇸|美国-IEPL 02`（08-06 起长期推荐），但机场线路频繁漂移，本次它对 api.openai.com delay **504 超时**（08-11 10:01 还是 279ms）。**每次跑脚本前必须先实测候选节点**（delay + 走代理 `codex/models` HTTP 状态，delay 通 ≠ 放行），把最快稳定放行节点写进脚本再运行——否则可能"修了配置但规则指向的节点本身已坏"。

### 修复过程

1. **节点体检**（`/proxies/{name}/delay?url=api.openai.com`）：美国-中转 01 **314ms** ✅、日本-IEPL 02 229ms ✅、香港-IEPL 01 68ms ✅、**美国-IEPL 02 / 美国-直连 504 Timeout ⚠️**。
2. **走代理实测候选节点**（逐一切换节点选择 → 实测 `codex/models`）：美国-中转 01 **401**(1.38s) / 美国-直连 401(1.25s) / 美国-IEPL 02 401(5.66s 慢) / 日本-IEPL 02 401(2.89s) / **香港-IEPL 01 403**(4.74s)。
3. **更新脚本** `fix_vortex_config.py`：`OPENAI_NODE = '🇺🇸|美国-IEPL 02'` → `'🇺🇸|美国-中转 01'`（注释说明实测依据）。
4. **运行一键脚本**：备份（`原始文件备份/vortex-config-20260811-1407-before-fix.yaml`）→ mode→rule、端口→39798、恢复 5 条 OpenAI 规则→美国-中转 01、MATCH→香港-IEPL 01 → 热加载 **204** → 恢复 TUN **204**。
5. **重启 Codex**：杀全部 ChatGPT.exe/codex.exe → AppsFolder 重新拉起 → 8 条 OpenAI 连接全部重建走美国-中转 01。

### 验证结果

| 站点/端点 | 修复前 | 修复后 |
|---|---|---|
| chatgpt.com 首页 | 403 | **200**（2.06s） |
| codex/models | 403 | **401**（0.95s，放行非风控） |
| google.com | — | **302** |
| youtube.com | — | **200** |
| OpenAI 活动连接 | 0 | 8 条全部 `['🇺🇸|美国-中转 01']` |

- [x] `/rules` 70 条；5 条 OpenAI 规则 → 🇺🇸 美国-中转 01；MATCH → 🇭🇰 香港-IEPL 01
- [x] `/configs.mode` = rule；tun=True；port=7897
- [x] 配置持久化（mode/端口已写入文件，重启不回退）

### 本次新增遗留事项

1. <span style="color:#ff0000">**订阅清规则已累计 10 次**（08-08 ×3 / 08-09 ×1 / 08-10 ×4 / 08-11 ×2）</span>。一键脚本有效（从发现到恢复 < 5 分钟，含节点实测），**但必须先实测节点再跑**。强烈建议在 Vortex GUI 关闭"自动更新订阅"（主界面→订阅→自动更新→关闭），从源头避免 config.yaml 被反复覆盖。
2. <span style="color:#ff8c00">**美国-IEPL 02 不再推荐为默认 OpenAI 节点**（本次 api delay 504 超时）</span>；当前脚本 `OPENAI_NODE = 🇺🇸|美国-中转 01`（实测 401 1.38s）。若再波动，候选放行节点：美国-中转 01 / 美国-直连 / 日本-IEPL 02。
3. 配置备份已更新至 `原始文件备份/vortex-config-20260811-1407-before-fix.yaml`（修复前）。

## 🔁 复发记录（2026-08-12 09:38）：公司网络下 Codex 又用不了——第 11 次订阅清规则 + 配置文件 mode:direct + 端口脱节 + ipv6 回退

> [!SUMMARY] 📌 复发摘要
> 用户到公司，反馈"网络不好使了、Codex 又用不了了"。三层诊断结果：**配置文件持久层 `mode: direct`（05 已知坑的"重启回退"变体）+ OpenAI 5 条分流规则被清（"订阅更新清规则"已知坑，累计第 11 次）+ external-controller 端口脱节（配置文件 39797 vs 运行态 39798）+ ipv6 回退 true（10 档案已处理过又被订阅重置）** 四重叠加。节点侧：08-12 00:15 刚切的 🇺🇸 美国-中转 01 已挂（delay 504 超时），🇺🇸 美国-IEPL 02 恢复（delay 267ms、实测 `codex/models` 401 放行）。处置：备份 → Python 改配置文件 `mode: direct`→`rule` + 插入 `ipv6: false` + `external-controller`→39798 + 恢复 5 条 OpenAI 规则（→🇺🇸 美国-IEPL 02）+ MATCH 兜底→🇹🇼 台湾-IEPL 03 → 热加载 **204** → 恢复 TUN **204** → 重启 Codex → 新实例 4 条 OpenAI 连接全部走美国-IEPL 02，`codex/models` 401 恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 磁盘配置文件 `mode` | <span style="color:#ff0000">`direct`（致命项；运行时 rule 是手动 PATCH 假象，热加载即被配置覆盖）</span> |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空</span>，仅剩 65 条出厂规则；chatgpt.com 掉进 `MATCH → 节点选择 → 🇭🇰 香港-IEPL 01` |
| 代理配置 | external-controller | <span style="color:#ff8c00">配置文件 `39797` vs 运行态 `39798`（端口脱节复发）</span> |
| 代理配置 | ipv6 | <span style="color:#ff8c00">回退 `true`（10 档案已处理过，订阅更新后又恢复默认）</span> |
| 网络层 | 节点 delay 体检（api.openai.com） | 🇺🇸 美国-IEPL 02 = **267ms** ✅（00:15 记录不稳后已恢复）；🇺🇸 美国-中转 01 = **504 挂** ⚠️（00:15 刚切的节点）；香港-IEPL 01 = 436ms |
| 网络层 | 走代理实测（修复后） | `codex/models` **401**（1.30s，放行非风控）；google **200**；youtube **200**；chatgpt.com 首页 403（curl UA 的 CF challenge，API 端点不受影响）✅ |
| 环境层 | 7897 端口 | LISTENING ✅ |
| 环境层 | 处置后 | 重启 Codex → 新实例 OpenAI 连接 **4 条全部走 🇺🇸 美国-IEPL 02**，`codex/models` 401 ✅ |

### 修复过程

1. **三层诊断**：`/configs`（mode/ipv6/tun/端口）、`/rules`（OpenAI 规则）、节点 delay 体检、走代理实测 `codex/models`。
2. **备份**：`config.yaml` → `原始文件备份/vortex-config-20260812-0939-company-before-fix.yaml`（SHA256 `9ef34fb4e0248f01`）。
3. **改配置**（Python UTF-8 安全写入，Unicode 转义节点名避开 GBK 坑）：
   - `mode: direct` → `rule`；
   - 顶层插入 `ipv6: false`（规避 CF IPv6 风控，见 [[10-mihomo IPv6出站导致ChatGPT被CF风控]]）；
   - `external-controller: 127.0.0.1:39797` → `127.0.0.1:39798`（修复端口脱节）；
   - 恢复 5 条 OpenAI 规则（openai.com/chatgpt.com/chatgpt-api.com/oaistatic.com/oaiusercontent.com）→ <span style="color:#1e90ff">`🇺🇸|美国-IEPL 02`</span>（实测放行且 delay 最优）；
   - `- MATCH, 节点选择` → `- MATCH, 🇹🇼|台湾-IEPL 03`（快节点兜底）。
   - 新 SHA256 `6619a95cb0d2e5bb`。
4. **热加载**：`PUT /configs?force=true` → **HTTP 204**；恢复 TUN → **204**。
5. **重启 Codex**：PowerShell 杀 ChatGPT/codex/node_repl → `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"` 重新拉起。
6. **验证**：见上表。

### 本次新增遗留事项

1. <span style="color:#ff0000">**订阅清规则累计第 11 次**（08-08 ×3 / 08-09 ×1 / 08-10 ×4 / 08-11 ×2 / 08-12 ×1）</span>。一键脚本有效但**必须先实测节点再跑**；强烈建议在 Vortex GUI 关闭"自动更新订阅"（主界面→订阅→自动更新→关闭）。
2. <span style="color:#ff8c00">**节点漂移反复**：美国-中转 01（00:15 刚切）仅半天又挂（504），美国-IEPL 02（08-11 判不稳）恢复（267ms）</span>。候选放行节点（按本次实测）：美国-IEPL 02 / 美国-直连 / 日本-IEPL 02。
3. **订阅更新还会重置其他配置**：本次连同 ipv6（回退 true）与 external-controller（改回 39797）一并被重置——修复时需按 04/05/06/10 四份档案逐项核对。
4. 配置备份已更新至 `原始文件备份/vortex-config-20260812-0939-company-before-fix.yaml`（修复前）。

## 🔁 复发记录（2026-08-13 10:44）：公司网络下 Codex 又无法进入——第 13 次订阅清规则 + 配置文件 mode:direct + 端口脱节 + ipv6 回退 + 节点漂移

> [!SUMMARY] 📌 复发摘要
> 用户到公司，反馈"Codex 又无法进入"。三层诊断结果：**配置文件持久层 `mode: direct`（08-12 同款"重启回退"变体）+ OpenAI 5 条分流规则被清（"订阅更新清规则"已知坑，累计第 13 次）+ external-controller 端口脱节（配置文件 39797 vs 运行态 39798）+ ipv6 回退 true（10 档案已处理过又被订阅重置）** 四重叠加。节点侧：脚本默认的 <span style="color:#ff8c00">🇺🇸 美国-中转 01 已挂（api delay 504）</span>，<span style="color:#1e90ff">🇺🇸 美国-IEPL 02 恢复（delay 351ms、实测 `codex/models` 401 放行）</span>。处置：实测候选节点（美国-IEPL 02/美国-直连/美国-中转 02/日本-IEPL 02/台湾-IEPL 03 均 401 放行）→ 更新一键脚本 OPENAI_NODE=美国-IEPL 02、MATCH_NODE=台湾-IEPL 03 → 运行脚本（备份/mode/端口/OpenAI规则/MATCH/热加载/TUN 全 204）→ 补插 `ipv6: false` + 热加载 + 恢复 TUN → 重启 Codex → 新实例连接走代理、`codex/models` 401 恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 磁盘配置文件 `mode` | <span style="color:#ff0000">`direct`（致命项；运行时 rule 是手动 PATCH 假象，热加载即被配置覆盖）</span> |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空</span>，仅剩 65 条出厂规则；chatgpt.com 掉进 `MATCH → 节点选择 → 🇭🇰 香港-IEPL 01`（历史 403 风控线路） |
| 代理配置 | external-controller | <span style="color:#ff8c00">配置文件 `39797` vs 运行态 `39798`（端口脱节复发）</span> |
| 代理配置 | ipv6 | <span style="color:#ff8c00">回退 `true`（10 档案已处理过，订阅更新后又恢复默认）</span> |
| 网络层 | 节点 delay 体检（api.openai.com） | 🇺🇸 美国-中转 01 = **504 挂**（脚本默认节点）；🇺🇸 美国-IEPL 02 = **351ms** ✅；🇺🇸 美国-直连 = 225ms；🇺🇸 美国-中转 02 = 239ms；🇹🇼 台湾-IEPL 03 = 77ms |
| 网络层 | 走代理实测（逐节点 `codex/models`） | 美国-IEPL 02 / 美国-直连 / 美国-中转 02 / 日本-IEPL 02 / 台湾-IEPL 03 全部 **401 放行**；修复前兜底香港-IEPL 01 为 **403** |
| 环境层 | 7897 / 39798 端口 | LISTENING ✅ |

### 修复过程

1. **三层诊断**：`/configs`（mode/ipv6/tun/端口）、`/rules`（OpenAI 规则 0）、节点 delay 体检、走代理实测 `codex/models`。
2. **实测候选节点**（逐一切换 `节点选择` + 实测）：5 个候选全部 401 放行 → 选 <span style="color:#1e90ff">`🇺🇸 美国-IEPL 02` 为 OPENAI_NODE（351ms 稳定）、`🇹🇼 台湾-IEPL 03` 为 MATCH_NODE（77ms 最快）</span>。
3. **更新一键脚本** `scripts/fix_vortex_config.py`：`OPENAI_NODE` `美国-中转 01`→`美国-IEPL 02`、`MATCH_NODE` `香港-IEPL 01`→`台湾-IEPL 03`（注释注明 08-13 实测依据）。
4. **运行脚本**：备份（`原始文件备份/vortex-config-20260813-1044-before-fix.yaml`）→ mode→rule、端口→39798、恢复 5 条 OpenAI 规则→美国-IEPL 02、MATCH→台湾-IEPL 03 → 热加载 **204** → 恢复 TUN **204**。
5. **补插 `ipv6: false`**（顶层，规避 CF IPv6 风控）+ 备份（`原始文件备份/vortex-config-20260813-1044-ipv6.yaml`）+ 热加载 **204** + 恢复 TUN **204**。
6. **重启 Codex**：杀全部 ChatGPT/codex/node_repl → AppsFolder 重新拉起（新 codex PID 33232）。

### 验证结果

| 站点/端点 | 修复前 | 修复后 |
|---|---|---|
| codex/models | 403 | **401**（0.88s，放行非风控） |
| google.com | 302（坏节点） | **200** |
| youtube.com | — | **200** |
| 新 codex 进程 | — | 多条 ESTABLISHED → 127.0.0.1:7897 ✅ |

- [x] `/configs`：mode=rule、ipv6=false、tun=true、port=7897
- [x] `/rules` 70 条；OpenAI 5 规则 → 🇺🇸 美国-IEPL 02；MATCH → 🇹🇼 台湾-IEPL 03
- [x] 配置持久化（mode/端口/ipv6 已写入文件，重启不回退）

### 本次新增遗留事项

1. <span style="color:#ff0000">**订阅清规则累计第 13 次**（08-08 ×3 / 08-09 ×1 / 08-10 ×4 / 08-11 ×2 / 08-12 ×1 / 08-13 ×1）</span>。一键脚本有效但**必须先实测节点再跑**；强烈建议在 Vortex GUI 关闭"自动更新订阅"（主界面→订阅→自动更新→关闭）。
2. <span style="color:#ff8c00">**节点漂移持续**：美国-中转 01（08-11 起脚本默认）已挂（504），美国-IEPL 02（08-12 判恢复）本次确认 351ms 放行</span>。候选放行节点（本次实测）：美国-IEPL 02 / 美国-直连 / 美国-中转 02 / 日本-IEPL 02 / 台湾-IEPL 03。
3. **订阅更新还会重置 ipv6**（本次回退 true 已补 false）——修复时需按 04/05/06/10 四份档案逐项核对。
4. 配置备份已更新至 `原始文件备份/vortex-config-20260813-1044-before-fix.yaml` 与 `vortex-config-20260813-1044-ipv6.yaml`（修复前）。

## 🔁 复发记录（2026-08-13 14:34）：网络/代理三层全通但 Codex 流式连接卡死——重启应用恢复

> [!SUMMARY] 📌 复发摘要
> 用户反馈 Codex 报 <span style="color:#ff0000">`stream disconnected before completion: error sending request for url (https://chatgpt.com/backend-api/codex/responses)`</span>。逐层诊断：**代理运行态与磁盘配置全部健康**（mode=rule、ipv6=false、tun=true、port=7897、OpenAI 5 规则 → 🇺🇸 美国-IEPL 02、MATCH → 🇹🇼 台湾-IEPL 03，磁盘与运行态一致）——<span style="color:#1e90ff">**不是**"订阅清规则 / 重启回退 / 端口脱节 / ipv6 回退"任一已知坑</span>；**节点侧**美国-IEPL 02=202ms 存活、台湾-IEPL 03=81ms；**端点侧** `codex/models` 连续 3 次 401 稳定、`codex/responses` POST=401 可达、google=200——<span style="color:#1e90ff">**无 CF 风控、无断流、无抖动**</span>。判定根因为 <span style="color:#e74c3c">**Codex 应用侧流式连接（SSE/长连接）陈旧卡死**</span>（应用进程在跑、有 37 条代理连接，但流请求已断）。处置：杀全部 ChatGPT/codex/node_repl → PowerShell 从 AppsFolder 重新拉起（AppID `OpenAI.Codex_2p2nqsd0c76g0!App`）→ 新 codex 进程建立 8 条 → 7897 代理连接，恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 运行态 `/configs` | <span style="color:#1e90ff">mode=rule / mixed-port=7897 / ipv6=false / tun=true ✅</span> |
| 代理配置 | 磁盘 `config.yaml` | mode: rule、external-controller 39798、OpenAI 5 规则→美国-IEPL 02、MATCH→台湾-IEPL 03 ✅（与运行态一致） |
| 代理配置 | `/rules` | 70 条；openai.com/chatgpt.com/chatgpt-api.com → 🇺🇸 美国-IEPL 02 ✅ |
| 网络层 | 节点 delay（api.openai.com） | 🇺🇸 美国-IEPL 02=**202ms** ✅；🇹🇼 台湾-IEPL 03=81ms ✅；🇺🇸 美国-直连=**504 挂**；🇺🇸 美国-中转 02=313ms |
| 网络层 | 走代理实测 | `codex/models`=**401**×3 稳定（无 403/超时）；`codex/responses` POST=401；google=200 ✅ |
| 环境层 | 进程 | Codex 应用在运行（旧 codex PID 33232/50812 + ChatGPT 全套 + node_repl×4），7897 有 37 条 Established |
| 应用层 | 判定 | 网络/代理/端点全通 → 流式长连接卡死，重启应用恢复 |

### 修复过程

1. **三层诊断**：/configs、/rules、config.yaml、节点 delay、走代理实测 codex/models×3 与 codex/responses——**全部健康，排除一切网络类已知坑**（订阅清规则/direct 回退/端口脱节/ipv6/节点漂移/CF 风控）。
2. **确认根因**：应用侧长连接陈旧卡死（进程在跑但流请求断）。
3. **重启 Codex**：PowerShell 杀全部 `ChatGPT/codex/codex-code-mode-host/node_repl` → `Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'` 重新拉起（<span style="color:#ff8c00">规避 bash→MSYS 路径转换坑，见 F9 档案</span>）。
4. **验证**：新 codex PID 34244，8 条 Established → 127.0.0.1:7897，代理流量恢复。

### 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| codex/models（走代理） | 401（可达） | 401（可达） |
| 代理 7897 活动连接 | 37 条（旧进程） | 46 条（含新 codex 8 条）✅ |
| codex 进程 | 33232/50812（陈旧） | 34244（全新）✅ |
| 结论 | 应用流式连接卡死 | 重启后恢复 |

### 本次新增遗留事项

1. **新增根因类型**（台账 N8）：**Codex 应用长连接卡死（网络/代理全通，重启恢复）**——与 F9「应用未运行」不同：本次应用在跑、仅流式连接陈旧。<span style="color:#e74c3c">遇到"网络三层全通 + Codex 进程在跑 + 仍 stream disconnected"时，直接重启应用即可，无需改代理配置。</span>
2. 重启应用统一用 PowerShell：`Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'`（bash 里 `explorer shell:AppsFolder\...` 会被 MSYS 转换静默失效）。

## 🔁 复发记录（2026-08-14 09:37）：公司网络下配置 Codex 网络——第 15 次订阅清规则 + 配置文件 mode:direct + 端口脱节 + ipv6 回退 + chatgpt.com DNS 污染

> [!SUMMARY] 📌 复发摘要
> 用户到公司，要求配置网络准备使用 Codex。三层诊断结果：**配置文件持久层 `mode: direct`（"重启回退"变体，台账第 6 次）+ OpenAI 5 条分流规则被清（"订阅更新清规则"已知坑，累计第 15 次）+ external-controller 端口脱节（配置文件 39797 vs 运行态 39798）+ ipv6 回退 true（10 档案已知坑被订阅重置）** 四重叠加。**本次新增关键证据**：<span style="color:#ff0000">**chatgpt.com 被 mihomo 国内 DoH 解析到污染 IP `118.193.240.41`**（与 08-10 15:50 复发记录同一污染 IP），无 OpenAI 规则时走节点连污染 IP → TLS 握手失败（curl exit 35 / HTTP 000）</span>；而 <span style="color:#1e90ff">**api.openai.com 解析正常（202.160.129.164）、走代理 401 放行**</span>——证明节点本身对 OpenAI 可用、非节点故障。节点 delay 全通（美国-IEPL 02=277ms、台湾-IEPL 03=249ms、美国-直连=267ms、日本-IEPL 02=266ms）。处置：备份 → 运行一键脚本（mode→rule、端口→39798、恢复 5 条 OpenAI 规则→🇺🇸 美国-IEPL 02、MATCH→🇹🇼 台湾-IEPL 03、热加载 **204**、恢复 TUN **204**）→ 补插 `ipv6: false`（备份 + 热加载 204 + 恢复 TUN 204）→ 从 AppsFolder 启动 Codex（新 codex PID 33120）。验证 codex/models=**401**（0.89s）、api.openai.com=401、google=200、youtube=200；新 codex 进程 7 条连接全部走 127.0.0.1:7897。

### 现象与复现

- 现象：用户到公司要求配置 Codex 网络。启动 Codex 前走代理实测 `chatgpt.com` / `codex/models` 均 **HTTP 000（5s 超时，TLS 握手失败）**，`google.com` **302**（外网通）。
- 复现证据（走代理 7897）：
  - 运行态 `/configs`：mode=rule（手动 PATCH 假象）、**ipv6=true**、tun=true、port=7897
  - 磁盘 `config.yaml`：**`mode: direct`** + **`external-controller: 39797`**（与运行态 39798 脱节）
  - `GET /rules` → **openai/chatgpt 规则 0 条**（65 条出厂版），末尾 `Match → 节点选择`
  - `GET /proxies/节点选择` → `now = 🇭🇰|香港-IEPL 01`（对 OpenAI 403 风控的历史坏线路）
  - `GET /dns/query?name=chatgpt.com` → **`118.193.240.41`**（污染 IP，非 Cloudflare）
  - 走代理 curl verbose：`CONNECT tunnel established, response 200` 后 **`curl: (35) schannel: failed to receive handshake`**（TLS 握手失败）

### 根因分析（与既往复发的对比）

| 层级 | 本次根因 | 证据 |
|---|---|---|
| 配置持久化 | 文件 `mode: direct` + **`external-controller: 39797`**（与运行态 39798 脱节，台账第 6 次） | config.yaml 第 4/6 行；运行态 rule/39798 |
| 分流规则 | **5 条 OpenAI 规则第 15 次被订阅更新清除** | `/rules` 65 条出厂版、无 openai/chatgpt；config.yaml rules 段无 DOMAIN-SUFFIX,openai.com |
| DNS 层 | <span style="color:#ff0000">**chatgpt.com 被 mihomo 国内 DoH 解析到污染 IP `118.193.240.41`**</span> | `/dns/query?name=chatgpt.com` → 118.193.240.41（与 08-10 15:50 同一污染 IP） |
| 路由层 | 无 OpenAI 规则 → chatgpt.com 走节点连污染 IP → TLS 握手失败 | curl exit 35 / HTTP 000；`CONNECT 200` 后 schannel handshake failed |
| 节点层 | <span style="color:#1e90ff">**节点无故障**</span>（delay 全通、api.openai.com 401 放行） | 美国-IEPL 02=277ms / 台湾-IEPL 03=249ms / 美国-直连=267ms / 日本-IEPL 02=266ms；走代理 api.openai.com=**401** |

> [!warning] ⚠️ 关键认知（新增判据）
> **判断 ChatGPT/Codex 是否可用必须测 `chatgpt.com` 域，不能只测 `api.openai.com`**——本次 `api.openai.com` 解析正常（202.160.129.164）且 401 放行，`chatgpt.com` 却因污染 IP 走节点 TLS 全挂。二者同属 OpenAI 但在 mihomo 国内 DoH 下的污染结果不同。修复后 OpenAI 规则（DOMAIN-SUFFIX,chatgpt.com → 节点）使 chatgpt.com 走境外解析/节点，绕开污染。

### 修复过程

1. **备份**（脚本自动）：`config.yaml` → `原始文件备份/vortex-config-20260814-0937-before-fix.yaml`。
2. **运行一键脚本** `scripts/fix_vortex_config.py`（08-13 节点配置有效无需改）：`mode→rule`、`external-controller→39798`、恢复 5 条 OpenAI 规则→`🇺🇸|美国-IEPL 02`、`MATCH→🇹🇼|台湾-IEPL 03`、热加载 **204**、恢复 TUN **204**。
3. **补插 `ipv6: false`**（顶层，规避 CF IPv6 风控；脚本不含此项）+ 备份（`原始文件备份/vortex-config-20260814-0937-ipv6.yaml`）+ 热加载 **204** + 恢复 TUN **204**。
4. **启动 Codex**：`Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'`（新 codex PID 33120）。

### 验证结果

| 站点/端点 | 修复前 | 修复后 |
|---|---|---|
| codex/models | 000 | **401**（0.89s，放行非风控） |
| api.openai.com | 401（本可通） | **401** |
| chatgpt.com 首页 | 000 | 403（curl UA 的 CF challenge，不影响 API 端点） |
| google.com | 302 | **200** |
| youtube.com | — | **200** |
| 新 codex 进程 | — | **7 条 ESTABLISHED → 127.0.0.1:7897** ✅ |

- [x] `/configs`：mode=rule、ipv6=false、tun=true、port=7897
- [x] `/rules` 70 条；OpenAI 5 规则 → 🇺🇸 美国-IEPL 02；MATCH → 🇹🇼 台湾-IEPL 03
- [x] 配置持久化（mode/端口/ipv6 已写入文件，重启不回退）

### 本次新增遗留事项

1. <span style="color:#ff0000">**订阅清规则累计第 15 次**（08-08 ×3 / 08-09 ×1 / 08-10 ×4 / 08-11 ×2 / 08-12 ×1 / 08-13 ×2 / 08-14 ×1）</span>。一键脚本有效（从发现到恢复 < 5 分钟），但**必须先实测节点再跑**；强烈建议在 Vortex GUI 关闭"自动更新订阅"（主界面→订阅→自动更新→关闭）。
2. <span style="color:#ff8c00">**一键脚本仍不含 `ipv6: false` 处理**（本次运行态 ipv6=true 需手动补插）</span>——建议后续把 ipv6:false 纳入脚本默认项，避免每次手动补。
3. **chatgpt.com DNS 污染判据沉淀**：`/dns/query?name=chatgpt.com` 得到非 Cloudflare IP（如 118.193.240.41）即污染；修复后经 OpenAI DOMAIN 规则走境外解析绕开。
4. 配置备份已更新至 `原始文件备份/vortex-config-20260814-0937-before-fix.yaml` 与 `vortex-config-20260814-0937-ipv6.yaml`（修复前）。

## 🔁 复发记录（2026-08-14 12:23）：青旅网络下 Codex 正常打开但发消息无回应——N8 长连接卡死第 2 次（重启恢复）

> [!SUMMARY] 📌 复发摘要
> 用户回到青旅，Codex 能正常打开但发消息无回应。三层诊断结果：**网络/代理/端点全部健康**——运行态 mode=rule / tun=true / ipv6=false / port=7897、OpenAI 5 条规则→🇺🇸 美国-IEPL 02、MATCH→🇹🇼 台湾-IEPL 03、节点 delay 全通（美国-IEPL 02=258ms、台湾-IEPL 03=253ms、美国-直连=239ms）、显式代理 + TUN 直连 api.openai.com 均 401（0.85~1.10s）——<span style="color:#1e90ff">**排除一切网络类已知坑**</span>；Codex 进程在跑但活动连接大量 `上传:0 下载:0`（陈旧）→ 判定为 <span style="color:#e74c3c">**N8 Codex 应用长连接卡死第 2 次复发**</span>（与 08-13 14:34 完全同型）。处置：① 备份 config.yaml；② <span style="color:#ff8c00">**补回 `sniffing: true`**</span>（订阅更新把配置文件里的 sniffing 字段清掉——[[11-mihomo sniffing关闭导致TUN直连OpenAI分流失效（Codex登录token交换失败）|doc 11]] 遗留事项第 1 条预警场景，本次未造成实际失败，预防性补回）；③ 杀全部 ChatGPT/codex/node_repl/codex-code-mode-host → PowerShell AppsFolder 重启（新 codex PID 41036）；④ 验证 13 条 OpenAI 连接全走美国-IEPL 02、显式代理/TUN 直连均 401。恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 运行态 `/configs` | mode=rule / mixed-port=7897 / ipv6=false / tun=true ✅（**sniffing 运行态显示 False**） |
| 代理配置 | 磁盘 `config.yaml` | mode: rule、external-controller 39798、OpenAI 5 规则→美国-IEPL 02、MATCH→台湾-IEPL 03 ✅；**`sniffing` 字段被订阅更新清除** |
| 代理配置 | `/rules` | 70 条；openai.com/chatgpt.com/chatgpt-api.com/oaistatic.com/oaiusercontent.com → 🇺🇸 美国-IEPL 02 ✅ |
| 网络层 | 节点 delay（api.openai.com） | 🇺🇸 美国-IEPL 02=**258ms** ✅；🇹🇼 台湾-IEPL 03=253ms ✅；🇺🇸 美国-直连=239ms ✅ |
| 网络层 | 走代理实测 | `api.openai.com/v1/models`=**401**×3 稳定（0.85~1.10s）✅ |
| 网络层 | TUN 直连实测 | `api.openai.com/v1/models`=**401**（0.90s）✅——当前 fake-ip DNS 映射兜底，OpenAI 未掉进兜底坏节点 |
| 环境层 | 进程 | Codex 应用在跑（codex PID 33120 + ChatGPT 全套 + node_repl×5），活动连接 17 条 OpenAI 但大量 `上传:0 下载:0`（陈旧） |
| 应用层 | 判定 | 网络/代理/端点全通 → **N8 流式长连接卡死**，重启应用恢复 |

### 修复过程

1. **三层诊断**：/configs、/rules、config.yaml、节点 delay、走代理实测 ×3、TUN 直连实测、/connections——网络/代理/端点全部健康，排除订阅清规则/direct 回退/端口脱节/ipv6/节点漂移/CF 风控/DNS 污染等一切网络类已知坑。
2. **补回 `sniffing: true`**（预防性）：config.yaml 在 `mode: rule` 后插入 `sniffing: true`（订阅更新重写清掉该字段）+ 热加载 **204** + 恢复 TUN **204**。备份：`原始文件备份/vortex-config-20260814-1223-sniffing-before-fix.yaml`。
3. **重启 Codex**（N8 处置）：杀全部 ChatGPT/codex/codex-code-mode-host/node_repl → `Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'` 重新拉起（规避 bash→MSYS 路径转换坑，见 F9 档案）。
4. **验证**：新 codex PID 41036，13 条 OpenAI 连接全走 🇺🇸 美国-IEPL 02；显式代理 api.openai.com=401 ×3；TUN 直连=401。

### 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| 显式代理 api.openai.com/v1/models | 401（可达，但冷启动一次 20.4s） | **401** ×3（0.85~1.10s）✅ |
| TUN 直连 api.openai.com/v1/models | 401（0.90s） | **401**（0.88s）✅ |
| 活动连接 OpenAI 相关 | 17 条，大量上传/下载=0（陈旧） | 13 条 HTTPS → 美国-IEPL 02（新进程）✅ |
| codex 进程 | 33120（陈旧） | **41036**（全新）✅ |
| config.yaml sniffing | **字段缺失**（订阅更新清除） | **sniffing: true 已持久化** ✅ |
| 结论 | N8 长连接卡死 + sniffing 配置被清 | 重启应用 + 补回 sniffing 后恢复 |

### 本次新增遗留事项

1. <span style="color:#ff0000">**N8 长连接卡死累计第 2 次**（08-13 14:34 / 08-14 12:23）。</span>处置口诀不变：<span style="color:#e74c3c">"网络三层全通 + Codex 进程在跑 + 仍无响应 → 直接重启应用，无需改代理配置"</span>。
2. <span style="color:#ff8c00">**订阅更新再次清掉 `sniffing: true`**（[[11-mihomo sniffing关闭导致TUN直连OpenAI分流失效（Codex登录token交换失败）|doc 11]] 遗留事项第 1 条兑现）。</span>本次因 fake-ip DNS 映射 + 节点恰好可用而未造成实际失败，但属隐患——**下次修配置后务必确认 config.yaml 含 `sniffing: true`**。建议把 `sniffing: true` 纳入一键脚本默认项。

## 🔁 复发记录（2026-08-14 18:10）：青旅网络下 Codex 发消息仍无回应——主运行时更新 EPERM 失败 + 进程堆积致状态错乱（全杀重启恢复）

> [!SUMMARY] 📌 复发摘要
> 用户再次反馈（距 12:23 修复约 6 小时）：Codex 正常打开但发消息无回应。**网络三层再次确认全健康**（显式代理 + TUN 直连 api.openai.com 均 401、chatgpt.com 403、节点延迟全绿、真实发消息端点 POST `chatgpt.com/backend-api/codex/responses` 走代理与 TUN 均 **401** 快速响应）——排除网络类一切已知坑。转向**应用层深挖日志**，找到真正根因：<span style="color:#ff0000">① **主运行时更新失败**——Codex 试图把 primary-runtime **26.812→26.813** 时，因运行时目录被活动进程占用报 **EPERM**（`activate_runtime` 阶段 rename 失败），消息处理链路中断；② **进程严重堆积**——10 个 ChatGPT.exe + 多个残留（正常 4-6 个），多次启动未清理；③ **会话状态丢失**——`Conversation state not found`（conversationId `019fffa5…`），该会话发消息无回应。</span>处置：杀全部 Codex 家族进程（释放运行时目录锁）→ AppsFolder 重新拉起 → 新 codex PID **57292**、19 条 OpenAI 连接全走美国-IEPL 02、新日志 **0 EPERM / 0 会话状态错误**。恢复。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | /configs、/rules、config.yaml | mode=rule / sniffing:true（12:23 已补） / ipv6=false / tun=true / OpenAI 5 规则→美国-IEPL 02 ✅ |
| 网络层 | **真实发消息端点** POST `chatgpt.com/backend-api/codex/responses` | 走代理=**401**（0.87s）、TUN=**401**（0.88s）✅ |
| 网络层 | 节点 delay（api.openai.com） | 美国-IEPL 02=243ms ✅、美国-直连=284ms ✅ |
| 网络层 | 走代理实测 | api.openai.com=401×多、chatgpt.com=403、google/youtube/github=200 ✅ |
| 环境层 | 进程 | 🔴 **10 个 ChatGPT.exe 堆积**（正常 4-6 个），多次启动残留 |
| 环境层 | 运行时 | primary-runtime **26.812** 在位；更新 **26.813** 报 **EPERM**（rename 被占） |
| 应用层 | 会话状态 | 🔴 **`Conversation state not found`**（conversationId `019fffa5…`）反复出现 |
| 应用层 | 判定 | **运行时更新失败 + 进程堆积 + 会话状态错乱 → 消息处理中断** |

### 修复过程

1. **网络三层复测全通** → 排除网络（与 12:23 同，本次更深挖应用层）。
2. **日志深挖**：读 `Logs/2026/08/14/codex-desktop-*-51844-*.log` → 定位 `primary_runtime_install_failed` EPERM + `Conversation state not found` + 进程堆积。
3. **全杀进程**：PowerShell 杀全部 `codex.exe / ChatGPT.exe / node_repl.exe / codex-code-mode-host.exe`（**含堆积的 10 个 ChatGPT.exe**）→ 释放运行时目录锁。
4. **重新拉起**：`Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'` → 新 codex PID 57292。
5. **验证**：19 条 OpenAI 连接全走 🇺🇸 美国-IEPL 02（含 `ws.chatgpt.com` 流式端点）；新日志 `0 EPERM` / `0 会话状态错误`；api.openai.com=401。

### 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| 进程 | 🔴 10 个 ChatGPT.exe 堆积 | ✅ 干净进程树（codex 1 + ChatGPT 8 + node_repl 1） |
| 运行时更新 | 🔴 EPERM（26.812→26.813 失败） | ✅ 无 EPERM，旧运行时 26.812 正常使用 |
| 会话状态 | 🔴 `Conversation state not found` | ✅ 0 错误 |
| OpenAI 连接 | — | ✅ 19 条 → 美国-IEPL 02（含 ws.chatgpt.com 流式） |
| 端点 | api.openai.com=401 | ✅ 401（0.84s） |

### 本次新增遗留事项

1. <span style="color:#ff0000">**新增根因类型（台账 F10）**：Codex 主运行时更新失败（EPERM）+ 进程堆积致消息处理中断。</span><span style="color:#e74c3c">处置 = 全杀 Codex 家族进程（含全部 ChatGPT.exe 残留）+ 重新拉起；无需改代理配置。</span>
2. <span style="color:#ff8c00">**运行时 EPERM 是 Codex 自身的"运行时热更新"缺陷**：运行时目录被活动进程占用，rename 必然失败。</span>遇"发消息无回应"先查应用日志是否 EPERM + 进程是否堆积（`tasklist | grep ChatGPT`）。
3. **会话状态丢失仅影响特定会话**：若某会话仍无回应，新建会话即可，无需全局处理。
4. 本档 12:23 复发（记 N8 长连接卡死）与本次（F10 运行时/状态错乱）**同属应用层故障**——网络/代理配置两次均无需改动；排查顺序：**网络三层 → 应用日志 EPERM/会话状态 → 进程堆积**。

## 🔁 复发记录（2026-08-14 18:36）：青旅网络下 Codex 发消息仍无回应——主运行时 26.813 装完插件市场同步失败致 app-server 崩溃（删损坏运行时重装恢复）

> [!SUMMARY] 📌 复发摘要
> 距 18:10 修复约 26 分钟，用户再次反馈"Codex 正常打开但发消息无回应"（当日第 3 次）。本次挖到**当天三次复发的同一根链条**：<span style="color:#ff0000">18:10 全杀进程后，primary-runtime **26.813 安装成功**，但 **post-install 插件市场同步失败**（`Failed to sync primary runtime bundled plugin marketplace`，failureStage=sync_plugins）——这使运行时进入损坏态，随后 **codex.exe 应用服务器（app-server）崩溃退出**（约 18:23），仅剩 10 个孤儿 ChatGPT.exe 渲染进程：UI 看似正常、后端已死</span>。诊断铁证：新会话日志自 18:23 起刷屏 <span style="color:#ff0000">`Codex app-server process is not available`</span>，`tasklist` 已无 codex.exe。处置：杀全部孤儿渲染进程 → **把损坏的运行时目录改名备份**（`codex-primary-runtime.corrupt-20260814-1838`，1334MB/26.813，先备份后改动）→ AppsFolder 重新拉起 → 触发**全新干净重装**：26.813 经 `persistent.oaistatic.com` 下载 3.4 分钟、`bundle_install outcome=installed errorCode=null failureStage=null`、**`plugin_marketplace_sync_completed marketplaceName=openai-primary-runtime`（5 插件全就位，对比修复前失败）**。<span style="color:#1e90ff">app-server 恢复稳定、主窗口正在正常处理消息 turn（reasoning summary 持续完成）。恢复。</span>

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | /configs、/rules、config.yaml | mode=rule / sniffing:true（12:23 已补）/ ipv6=false / tun=true / OpenAI 5 规则→美国-IEPL 02 ✅（网络层当日已多次复测全通，本次不动代理） |
| 环境层 | 进程 | 🔴 **codex.exe（app-server）已死亡**，仅剩 10 个孤儿 ChatGPT.exe（18:12 启动、全无后端） |
| 环境层 | 运行时 | 🔴 primary-runtime **26.813 在位但损坏**——安装成功、post-install 插件市场同步失败（`post_install/sync_plugins`） |
| 应用层 | 日志 | 🔴 自 18:23 起刷屏 **`Codex app-server process is not available`**（renderer 请求全部 -32000） |
| 应用层 | 判定 | **运行时损坏 → app-server 崩溃 → 孤儿渲染进程空壳**，消息处理链路彻底中断 |

### 修复过程

1. **定位**：日志 `codex-desktop-*-51844-*.log` 读到最后一段完整序列——`primary_runtime_bundle_install_outcome outcome=installed`（26.813 装完）→ `primary_runtime_install_failed ... failureStage=sync_plugins`（插件同步失败）→ `Codex app-server process is not available`（刷屏）。判定损坏运行时导致后端崩溃。
2. **清孤儿进程**：PowerShell 杀全部 `codex.exe / ChatGPT.exe / node_repl.exe / codex-code-mode-host.exe`（10 个渲染进程全部清理）。
3. **备份损坏运行时**：`Rename-Item` 把 `codex-runtimes\codex-primary-runtime` 改名 → `codex-primary-runtime.corrupt-20260814-1838`（保留 26.813 现场，先备份后改动）。
4. **触发全新重装**：`Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'` → 新会话（log `codex-desktop-dbb89b55-…-t0`）启动时检测到运行时缺失 → 自动下载 `persistent.oaistatic.com/.../26.813.12317/...tar.gz`（479MB，走 🇺🇸 美国-IEPL 02）→ 解压重建（22241 文件 / 1334MB）。
5. **验证**（下节）。

### 验证结果

| 检查项 | 修复前（18:36） | 修复后 |
|---|---|---|
| 运行时重装 | 🔴 26.813 损坏（sync_plugins 失败） | ✅ `bundle_install outcome=installed errorCode=null failureStage=null`（3.4 分钟） |
| 插件同步 | 🔴 `Failed to sync primary runtime bundled plugin marketplace` | ✅ `plugin_marketplace_sync_completed marketplaceName=openai-primary-runtime`（5 插件全就位） |
| app-server 进程 | 🔴 codex.exe 死亡 | ✅ PID 40576 持续存活（>5 分钟，远超此前崩溃窗口） |
| app-server 错误 | 🔴 `Codex app-server process is not available` 刷屏 | ✅ 计数 **0**；最近 200 行 error=**0** |
| 消息处理 | 🔴 发消息无回应 | ✅ 主窗口 `Reasoning summary item completed` 持续完成（thread 019fefa6 / 019fffdd），turn 正常推进 |
| 进程树 | 🔴 10 孤儿渲染进程 | ✅ codex 1 + ChatGPT 10 + codex-code-mode-host 1 + node_repl 2（完整） |
| 下载临时目录 | — | ✅ `codex-runtime-install-sxuURk` 已自动清理 |

### 本次新增遗留事项

1. <span style="color:#ff0000">**新增根因类型（台账 F11）**：Codex 主运行时安装后插件市场同步失败致 app-server 崩溃。</span>这是 **F10 的"尾段"**：18:10 全杀进程解决了 EPERM、让 26.813 装上，但**中断的更新把运行时留在 post-install 插件同步失败态** → app-server 崩溃 → UI 空壳。**三连复发实为同一条链：运行时更新路径的三种失败形态**（N8 卡死表象 / F10 EPERM+进程堆积 / F11 插件同步失败→后端崩溃）。
2. <span style="color:#e74c3c">**根治动作 = 删（备份）损坏运行时目录 + 触发干净重装**</span>，而非再次"全杀重启"——因为损坏的 26.813 只要还在，app-server 就会反复崩溃。**判断口诀**：日志见 `sync_plugins` 失败 + `Codex app-server process is not available` 刷屏 → 直接备份并移除 `codex-runtimes\codex-primary-runtime` 后重启，让它重装。
3. <span style="color:#ff8c00">**坏运行时备份已保留**：`codex-runtimes\codex-primary-runtime.corrupt-20260814-1838`（1334MB）。确认新版运行稳定后可删除释放空间（C 盘仅剩 ~10GB）。</span>
4. 网络层当日三次全程健康，**本次仍属应用层故障**；排查顺序再升级：**网络三层 → 应用日志（EPERM / sync_plugins / app-server not available）→ 进程树 → 运行时完整性**。

## 🔁 复发记录（2026-08-18 15:10）：Codex 持续显示"模型繁忙，切换模型"——第 18 次订阅清规则 + 配置文件 mode:direct + 端口脱节 + ipv6 回退 + sniffing 回退 + 新加坡坏节点

> [!SUMMARY] 📌 复发摘要
> 用户反馈"使用 Codex 一直显示模型繁忙、让我切换模型，但之前都不会"。本次直接证据指向**网络/代理配置又被订阅更新清空**（台账 N1 累计第 18 次），而非 OpenAI 服务端真过载：<span style="color:#ff0000">config.yaml 被还原为 `mode: direct` + `external-controller: 39797`（与运行态 39798 脱节）+ `ipv6: true` 回退 + sniffing 被清 + 5 条 OpenAI 分流规则再次被清（/rules 仅 65 条出厂版）+ MATCH 兜底回到「节点选择」</span>；且当前 `节点选择 = 🇸🇬 新加坡-进阶IEPL 01`（历史对 OpenAI 不通），走代理实测 chatgpt.com 超时（000）。"模型繁忙"实为 OpenAI 请求在坏路由/坏节点下反复失败的应用层表象。处置：备份 → fix_vortex_config.py 一键恢复（mode/端口/5 规则→美国-IEPL 02、MATCH→台湾-IEPL 03、热加载、恢复 TUN）→ 补 `ipv6: false`（生效）→ 补 `sniffing: true`（文件生效、运行态待 Vortex 全重启）→ 全杀 Codex 进程后经 AppsFolder 重启 → <span style="color:#1e90ff">codex/models 实测 401（网络路径已通）、应用重新认证并连接。</span>

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置(文件) | config.yaml | 🔴 `mode: direct` + `external-controller: 39797`（与运行态 39798 脱节）+ `ipv6: true` 回退 + sniffing 被清 + 无 OpenAI 5 规则 + 末尾 `- MATCH, 节点选择` |
| 代理配置(运行态) | /rules | 🔴 65 条出厂版、无 openai/chatgpt（**订阅更新第 18 次清规则**） |
| 代理配置(运行态) | 节点选择 | 🔴 🇸🇬 新加坡-进阶IEPL 01（历史对 OpenAI 不通，delay 通 ≠ 对 ChatGPT 放行） |
| 网络层 | 走代理实测（修复前） | 🔴 `chatgpt.com` 经 7897 → 000 超时 |
| 应用层 | Codex 进程与日志 | 在跑（11×ChatGPT + codex）、app 已认证；日志无直接 429/503/busy 服务端码 → "模型繁忙"为坏路由下的应用层表象 |

### 修复过程

1. **备份（先备份后改动）**：`fix_vortex_config.py` 自动备份 → `原始文件备份/vortex-config-20260818-1509-before-fix.yaml`；补 ipv6/sniffing 前再手动备份 → `原始文件备份/vortex-config-20260818-ipv6-sniffing-before.yaml`。
2. **一键修复**：`python scripts/fix_vortex_config.py` → `mode: direct→rule`、`external-controller: 39797→39798`、恢复 5 条 OpenAI 规则→🇺🇸 美国-IEPL 02、`MATCH→🇹🇼 台湾-IEPL 03`、热加载 204、恢复 TUN 204。
3. **补 ipv6**：config.yaml 加 `ipv6: false` → 运行态 `ipv6=False` ✅。
4. **补 sniffing**：config.yaml 加 `sniffing: true`（文件行 6 已生效）→ 但运行态 `/configs` 仍 False；PATCH 布尔 `{"sniffing":true}` 返回 204 不生效、对象格式 400 → 判定 mihomo 该版本运行态不反映该字段，**需 Vortex 全重启才生效**。⚠️ 对 Codex 影响小：Codex 走显式代理 `127.0.0.1:7897`（非 TUN），域名由 CONNECT/SNI 已获知，不依赖 sniffing。
5. **重启 Codex 应用**：全杀 `ChatGPT / codex / codex-code-mode-host` 进程 → `Start-Process 'shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App'` 重新拉起 → 新日志 `authenticatedAccountPresent=true`、app-server `connected`。

### 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| mode | 🔴 direct（文件） | ✅ rule |
| external-controller | 🔴 39797（文件，与运行态脱节） | ✅ 39798（文件/运行态一致） |
| OpenAI 分流规则 | 🔴 65 条出厂版、无 OpenAI | ✅ /rules 70 条、5 条 OpenAI→美国-IEPL 02 |
| ipv6 | 🔴 true（回退） | ✅ false |
| sniffing | 🔴 被清 | ⚠️ 文件 true、运行态仍 false（遗留，见下） |
| 节点 | 🔴 新加坡-进阶IEPL 01 | ✅ 美国-IEPL 02=201ms / 台湾-IEPL 03=73ms |
| 端点实测 | 🔴 chatgpt.com 000 超时 | ✅ `codex/models` 401、`api.openai.com/v1/models` 401（无 token 预期响应，网络路径已通） |
| Codex 应用 | 🔴 持续"模型繁忙" | ✅ 重启后重新认证、app-server connected |

### 本次新增遗留事项

1. <span style="color:#ff0000">**N1 订阅清规则累计第 18 次**（上次为 08-15 12:31 第 17 次，青旅）</span>。一键脚本有效但**必须先实测节点再跑**；再次强烈建议在 Vortex GUI 关闭"自动更新订阅"（主界面→订阅→自动更新→关闭）。
2. <span style="color:#e74c3c">**sniffing 运行态仍 False**（台账 N9 累计第 2 次）</span>：config.yaml 已写 `sniffing: true`，但运行态需 **Vortex 全重启**才生效。Codex 走显式代理 7897 不受影响，暂不处理；如需彻底应用（消除 TUN 直连不分流的隐患），可全重启 Vortex。
3. `backend-api.chatgpt.com` 经代理仍超时（000，exit 35）——非 Codex 关键端点（`codex/models` 走 `chatgpt.com` 正常），暂不处理。
4. <span style="color:#ff8c00">**"模型繁忙"的定性**</span>：本次已确认为本机代理配置损坏所致；若网络修复后仍偶发"模型繁忙"，才属 OpenAI 服务端真负载/账号级风控，本机不可解。

## 🔁 复发记录（2026-08-18 15:28）：GPT 网页版报 `unsupported_country`（OpenAI 服务在所在国家/地区不可用）——第 19 次订阅清规则 + mode:global + 端口脱节 + ipv6 回退 + sniffing 回退（TUN 关闭致浏览器直连识别为中国大陆 IP）

> [!SUMMARY] 📌 复发摘要
> 距 15:10 第 18 次修复仅 18 分钟，用户反馈 GPT **网页版**报错：`糟糕，出错了! OpenAI服务在你所在的国家/地区不可用。错代码:unsupported_country 请求ID:358c5ea7...`。本次直接证据：<span style="color:#ff0000">运行态 `mode=global`（全局模式，所有流量走全局节点、绕过全部分流）+ ipv6 回退 true + TUN 关闭 + sniffing false + OpenAI 规则再次被清（/rules 0 条）</span>；磁盘 config.yaml 亦被清回 `mode: direct` + `external-controller: 39797`（**订阅更新第 19 次清规则包**）。TUN 关 + 系统代理未接管 → 浏览器直连 chatgpt.com → 出口识别为中国大陆 IP → OpenAI 判 `unsupported_country`。处置：备份 → fix_vortex_config.py（mode→rule、端口→39798、5 规则→美国-IEPL 02、MATCH→台湾-IEPL 03、热加载、恢复 TUN）→ 补回 `ipv6: false`（生效）与 `sniffing: true`（文件）→ <span style="color:#1e90ff">chatgpt.com / api.openai.com / codex/models 全部恢复可达（401/403 预期码），运行态确认 OpenAI 连接链 = 🇺🇸 美国-IEPL 02。</span>

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置(运行态) | /configs | 🔴 `mode=global`（全局模式，绕过分流）+ `ipv6=true` 回退 + `tun=false` + `sniffing=false` |
| 代理配置(运行态) | /rules | 🔴 0 条 OpenAI 规则（**订阅更新第 19 次清规则**） |
| 代理配置(文件) | config.yaml | 🔴 `mode: direct` + `external-controller: 39797`（与运行态 39798 脱节）+ 无 ipv6/sniffing 字段 + 无 OpenAI 规则 |
| 网络层 | 浏览器出口 | 🔴 TUN 关 + 系统代理未接管 → 直连识别为中国大陆 IP → `unsupported_country` |
| 网络层 | 走代理实测（修复前） | 🔴 chatgpt.com 经 7897 → 000 超时 |

### 修复过程

1. **备份（先备份后改动）**：`fix_vortex_config.py` 自动 → `原始文件备份/vortex-config-20260818-1529-before-fix.yaml`。
2. **一键修复**：`python scripts/fix_vortex_config.py` → `mode→rule`、`39797→39798`、恢复 5 条 OpenAI 规则→🇺🇸 美国-IEPL 02、`MATCH→🇹🇼 台湾-IEPL 03`、热加载 204、恢复 TUN 204。
3. **补回 ipv6/sniffing**：config.yaml 加 `ipv6: false`（运行态生效 `ipv6=False` ✅）与 `sniffing: true`（文件行 6，运行态仍 false 待 Vortex 全重启）。
4. **验证连接链**（下节）。

### 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| mode | 🔴 global | ✅ rule |
| OpenAI 分流规则 | 🔴 0 条 | ✅ 5 条→美国-IEPL 02（/rules 70 条） |
| ipv6 | 🔴 true | ✅ false |
| TUN | 🔴 false | ✅ true |
| 端点实测 | 🔴 chatgpt.com 000 超时 | ✅ chatgpt.com 403（Turnstile 人机验证页，curl 无 cookie 属正常）、api.openai.com 401、codex/models 401 |
| OpenAI 连接链 | — | ✅ `chatgpt.com / auth.openai.com / chat.openai.com` → 🇺🇸 美国-IEPL 02 |
| 非 OpenAI 出口归属 | — | 🇹🇼 台湾-IEPL 03（台湾=OpenAI 支持地区，正常） |

### 🔄 节点切换跟进（2026-08-18 15:39）：美国线路全线超时 → OpenAI 节点切到台湾-IEPL 03

> [!SUMMARY] 📌 跟进摘要
> 19 次修复后用户反馈"节点超时"。复测发现 **chatgpt.com / api.openai.com 经原 OpenAI 节点（美国-IEPL 02）TLS 握手卡死**（verbose：CONNECT 隧道 200 但 `schannel: failed to receive handshake, SSL/TLS connection failed`），美国线路全线不稳。对 8 个候选节点做 **2 轮真实端点压测**：**美国节点全部失败**（家宽 01 / IEPL 02 / 中转 02 均 000），**日本-IEPL 01/02 与 台湾-IEPL 03 两轮全通**，其中 **台湾-IEPL 03 最快（0.4-0.5s）**。已将 5 条 OpenAI 规则切到 🇹🇼 台湾-IEPL 03（同时也是 MATCH 兜底），chatgpt.com / api.openai.com / google / youtube 全部 <1s 恢复。

| 节点 | 第 1 轮 codex/api | 第 2 轮 codex/api | 判定 |
|---|---|---|---|
| 🇺🇸 美国-家宽 01 5倍消耗 | 000 / 401(8.8s) | — | ❌ |
| 🇺🇸 美国-IEPL 02 | 000 / 000 | — | ❌ |
| 🇺🇸 美国-中转 02 | 000 / 000 | — | ❌ |
| 🇯🇵 日本-IEPL 01 | 401(1.7s)/401(0.6s) | 401(0.7s)/401(0.6s) | ✅ |
| 🇯🇵 日本-IEPL 02 | 401(2.5s)/401(1.2s) | 401(4.5s)/401(5.7s) | ✅ |
| 🇯🇵 日本原生-IEPL 01 | 000 / 000 | — | ❌ |
| 🇯🇵 日本星链家宽-IEPL 01 | 401(5.2s)/401(3.4s) | 000 / 000 | ❌ |
| 🇹🇼 台湾-IEPL 03 | 401(0.5s)/401(0.5s) | 401(0.4s)/401(0.5s) | ✅ 最快 |

- **根因定性**：台账 **N6（节点质量波动 / 机场线路故障）+1 → 5**；美国线路当日故障，台湾/日本稳定放行 OpenAI。
- **联动修改**：`fix_vortex_config.py` 的 `OPENAI_NODE` 与 `MATCH_NODE` 均已改为 🇹🇼 台湾-IEPL 03（脚本注释含 2026-08-18 实测结论），下次订阅清规则一键修复将直接落在稳定节点。

### 本次新增遗留事项

1. <span style="color:#ff0000">**N1 订阅清规则累计第 19 次**（08-18 当日 15:10 与 15:28 连续 2 次）</span>。**再次强烈建议在 Vortex GUI 关闭"自动更新订阅"**（主界面→订阅→自动更新→关闭），这是 19 次复发的唯一根源。
2. <span style="color:#e74c3c">**运行态 `mode=global` 系新形态**（磁盘 direct、运行态 global）</span>——疑似 Vortex GUI 被切到"全局模式"，或订阅配置携带 global；修复已回 `rule`，⚠️ **不要在 Vortex 手动切全局模式**。
3. `sniffing` 运行态仍 false（同 15:10 第 18 次，config.yaml 已 true，需 Vortex 全重启生效；Codex/浏览器走显式代理或 fake-ip 均不依赖 sniffing，暂不处理）。

## ⚖️ 解决方案与风险须知：删除损坏运行时备份（codex-primary-runtime.corrupt-20260814-1838）

> [!NOTE] ✅ 处置状态（2026-08-14 18:55）
> **已执行删除。** 安全确认（当前在用运行时 `codex-primary-runtime` 版本 = 26.813.12317 完好）通过后，用 `Remove-Item -Recurse -Force` 删除该备份，**释放 1.3GB**。下方完整保留决策过程供日后参考；若将来需取证，可重新下载复现（原损坏现场已无法恢复）。

> [!SUMMARY] 📌 结论速览
> **可以安全删除。** 该备份是 **<span style="color:#ff0000">损坏的运行时二进制包</span>**：不含任何用户数据、可从 OpenAI CDN 随时重新下载、**不是有效回滚点**。删除**不影响当前 Codex 运行**，仅释放 **1.3GB** 磁盘空间。唯一代价是**失去该损坏现场的证据**（无法再反查插件同步失败的具体损坏文件）。

### 这个备份是什么

- 修复 18:36 复发时，按「先备份后改动」原则把损坏的 `codex-primary-runtime` **改名**而来（原目录已移走，非复制）。
- 内容 = **纯运行时二进制包**：`dependencies/`（内置 node / python / git / poppler / powershell / libheif / jxrlib）+ `plugins/` + `runtime.json`（bundleVersion **26.813.12317**，总大小 1334.2 MB）。
- **不含用户数据**（已核实）：会话记录、登录态、用户配置都不在此目录——它们在 `C:\Users\asus\.codex\` 与 AppData；备份内所有 `config` 类文件均为捆绑依赖自带（git 的 gitconfig、powershell 的配置文件、python 包内部配置等）。

### 删除的影响（逐项说明）

| 影响面 | 删除后结果 | 说明 |
|---|---|---|
| 当前 Codex 运行 | **零影响** | 当前用的是新的 `codex-primary-runtime`（干净重装版），Codex 运行时不引用 `.corrupt-20260814-1838` 目录 |
| 用户数据 | **零丢失** | 备份内无任何用户数据（见上） |
| 恢复能力 | **不降低** | 该备份本身是**损坏态**，**不能**作为回滚点；将来运行时再坏，Codex 会自动从 `persistent.oaistatic.com` 重下——本次就是这么恢复的（`trigger=startup_missing`） |
| 磁盘空间 | 释放 **1.3GB** | C 盘当前仅剩 ~10GB，删除可缓解空间压力 |
| 故障取证 | **失去现场** | 唯一真正的损失：无法再 diff / 分析插件同步失败（`post_install/sync_plugins`）的具体损坏文件。若计划向 OpenAI 支持上报或日后复盘，可暂缓删除 |

### 保留 vs 删除 的风险对比

| 方案 | 好处 | 风险 |
|---|---|---|
| **删除** | 释放 1.3GB；消除"误把损坏运行时恢复回去"的隐患 | 失去取证样本（影响极小，可重新下载复现） |
| **保留** | 保留取证现场 | 占 1.3GB（C 盘紧张）；<span style="color:#ff0000">若被误重命名回 `codex-primary-runtime`，会把损坏运行时重新引入，再次触发 app-server 崩溃</span> |

### 建议操作

1. **确认新运行时稳定后再删**：✅ **已完成（2026-08-14）**——观察期已过崩溃窗口（app-server 稳定、0 崩溃、消息处理正常）；安全确认通过后已删除。
2. **删除命令**（PowerShell）：✅ **已执行**——
   ```powershell
   Remove-Item 'C:\Users\asus\.cache\codex-runtimes\codex-primary-runtime.corrupt-20260814-1838' -Recurse -Force
   ```
3. **万一需要"恢复"**：不需要——当前 `codex-primary-runtime` 就是完好版；若它也损坏，Codex 会自动重下，此备份无恢复价值。

> [!WARNING] ⚠️ 风险须知（三条硬约束）
> ① **该备份不是回滚点**——它是损坏版，拷回/改回原名会重新引入插件同步失败与 app-server 崩溃；**永远不要把它重命名回 `codex-primary-runtime`**。② **删除前确认**当前 `codex-primary-runtime\runtime.json` 存在且显示 `bundleVersion: 26.813.12317`。③ 若日后需向 OpenAI 上报/复现该故障，先保留此目录再联系支持。

## 🔁 复发记录（2026-08-31 00:10）：手机热点下 Codex 反复重连——小火箭 OpenAI 规则被清（第 21 次）

> [!SUMMARY] 📌 复发摘要
> 用户在**手机热点**（移动网络）下使用 Codex，发现又开始"反复重新连接"。三层诊断：**小火箭（Rocket/ClashR）在线**（控制端口 4788、HTTP 4780、系统代理 `127.0.0.1:4780`）、`/configs.mode = rule`（✅ **排除** mode 异常，非 direct/global，与 05/04 前几次的 mode 坑不同）、**OpenAI 5 条分流规则被清空**（=「订阅更新清 OpenAI 分流规则」累计**第 21 次**），chatgpt.com 落入 `MATCH→Others→Proxy→🔰国外流量→台湾 03` **单节点链**；叠加**手机热点抖动** → 08-30 23:40 `error sending request`（chatgpt.com 不可达）+ `timeout waiting for child process to exit`，23:41 网络恢复（`/backend-api/ps/plugins/installed` 回 401 `token_expired`），23:51 `turn-complete` 恢复。处置：**备份 → 逐节点改规则目标实测（香港 01 HKIX / 日本 03 仅 2/6 不稳，台湾 03 / 美国 06 / 新加坡 01 全 6/6 通过）→ 选定迁移期一致的原🇹🇼 台湾 03 中華電信为钉死节点 → 热加载 204 → 8/8 稳定验证**。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 运行态 `/configs.mode` | `rule` ✅（非 direct/global，排除 mode 异常） |
| 代理配置 | 运行态 `/configs.port` | `4780`（HTTP）/ `4781`（SOCKS）；`mixed-port=0`；控制 API 在 `4788` |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空（=0）</span>（「订阅更新清规则」累计第 21 次） |
| 代理配置 | MATCH 兜底 | `- MATCH,Others` → Others→Proxy→🔰国外流量 |
| 代理配置 | 🔰国外流量 当前节点 | `台湾 03 中華電信`（放行 codex/models=401） |
| 网络层 | 走代理实测 `codex/models` | **401**（OpenAI 可达，0.96s，✅ 未封） |
| 网络层 | 走代理实测 `chatgpt.com` | **403**（Cloudflare Turnstile 人机验证页，curl 无 cookie 属正常，✅） |
| 网络层 | 节点**两阶段**实测（08-31 00:0x） | **①初筛**（PUT 切换 🔰国外流量 + curl）：台湾 03 / 美国 01 / 日本 03 / 香港 01 / 美国 06 全部 `codex/models=401`；⚠️ 美国 01 AT&SANJOSE 的 `api.openai.com` 超时（000/5s）、日本 03 NTTドコモ 偏慢（3.45s）、香港 01 **初看**最快 0.85~0.99s。**②定稿**（改规则目标逐节点连测 6 次）：**香港 01 HKIX 2/6、日本 03 2/6（不稳）；台湾 03 / 美国 06 / 新加坡 01 全 6/6 稳定** → 改判选 **台湾 03 中華電信** |
| 环境层 | 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:4780` ✅（指向小火箭） |
| 环境层 | Codex 日志（UTC） | 15:40:18Z `error sending request`(chatgpt.com 不可达) + 15:40:44Z `timeout waiting for child process to exit`；15:41:48Z `/backend-api/ps/plugins/installed` 回 401 `token_expired`（网络已恢复）；**15:51:30Z `turn-complete`（恢复）** |

### 修复过程

1. **三层诊断**：`/configs`（mode=rule / port=4780/null / mixed-port=0）、`/rules`（OpenAI 规则 = 0）、`/proxies`（🔰国外流量 = 台湾 03）、走代理 curl 实测 `codex/models`（401）/ `chatgpt.com`（403）；并读 Codex 日志确认 15:40 网络错误 → 15:51 turn-complete。
2. **两阶段节点体检**：①初筛经 PUT 切换 🔰国外流量 + curl（用 Python UTF-8 切换，见新坑①）→ 台湾 03 / 美国 01 / 日本 03 / 香港 01 / 美国 06 全放行，香港 01 初看最快；②**改规则目标逐节点连测**（这才是有效口径——OpenAI 规则一旦钉死，切换 🔰国外流量 已不影响 codex/models，见新坑④）→ 香港 01 2/6、日本 03 2/6 不稳，台湾 03 / 美国 06 / 新加坡 01 6/6 稳定 → **选定台湾 03 中華電信**。
3. **备份**：`原始文件备份/rocket-config-20260830-1-before-fix.yaml`（SHA256 前缀 `f002e5d64bbcc6941049`）。
4. **改 `rocket.yaml`**：在 `GEOIP,CN,Domestic` 之后、`- MATCH,Others` 之前插入 5 条 OpenAI 规则 → `台湾 03 中華電信`（`openai.com / chatgpt.com / chatgpt-api.com / oaistatic.com / oaiusercontent.com`）。
5. **热加载**：`PUT /configs?force=true` body `{"path":"C:/Users/asus/AppData/Roaming/Rocket/clash-configs/rocket.yaml"}`（⚠️ 用**正斜杠**路径，反斜杠报 `Body invalid`，见新坑②）→ **HTTP 204**。
6. **验证**：`/rules` OpenAI 规则 **5 条 → 台湾 03 中華電信**；走代理实测 `codex/models` **401** / `chatgpt.com` **403**；**8/8 连测稳定**；Codex 日志 15:51:30Z `turn-complete`（已恢复）。

> [!warning] ⚠️ 关键认知（本次新坑）
> **① Windows 下 curl 直传中文/日文节点名会被 GBK 编码破坏**：`-d '{"name":"台湾 03 中華電信"}'` 落到服务端变乱码，PUT 切换报 `Selector update error: proxy not exist`（但该名明明在组的 `all` 列表里）；同一请求内 ASCII 名（如 `Others→Proxy`）却 204 成功。**改切换节点/推送规则时一律用 Python `json.dumps(ensure_ascii=False).encode('utf-8')`**，不要用 curl 裸中文——这也是本机 N10「Node fetch 代理兼容性」之外又一"中文/编码兼容"坑。
> **② 小火箭热加载 body 的 Windows 路径反斜杠会报 `Body invalid`**：`{"path":"C:\\Users\\...\\rocket.yaml"}` 400；**改用正斜杠** `{"path":"C:/Users/.../rocket.yaml"}` 即 204。（05/04 的 mihomo 与 小火箭 热加载均需如此。）
> **③ OpenAI 规则插入位**：放到 `GEOIP,CN,Domestic` 与 `- MATCH,Others` 之间即可（OpenAI 域名非 CN，GEOIP,CN 不会误吞；置于 MATCH 前确保被命中）；无需插到规则段顶部。
> **④ ⚠️ 一旦 OpenAI 规则钉死到某节点，再切换 🔰国外流量 分组就不再改变 codex/models 的出口**——因为规则优先命中，直接走钉死节点。此时若改用「切换 🔰国外流量」来测候选节点，测的全是同一个钉死节点，结果会失真（本案例曾据此误判香港 01 最优）。**要横向测候选节点，必须临时改规则目标（改 rocket.yaml 并热加载）再逐节点连测，而不是切分组**。

> [!NOTE] 📌 与「VPN 客户端迁移」小节的关系
> 本复发正是 [[#🔄 VPN 客户端迁移（2026-08-18 15：45）：SakuraCat（Vortex/mihomo）→ 小火箭（Rocket/ClashR）|迁移小节]] 的「遗留事项①：订阅更新会清掉 OpenAI 规则」被触发——小火箭 GUI 刷新订阅重写 `rocket.yaml`，第 21 次清空这 5 条规则，需重新添加。本次**沿用迁移期的钉死节点 台湾 03 中華電信**（08-31 逐节点实测确认其在香港 01 / 日本 03 不稳时仍全通过，最稳），逻辑与迁移期一致。

## 🔁 复发记录（2026-08-31 18:58）：宿舍 WiFi 下外网访问异常——订阅更新重写 rocket.yaml 清 OpenAI 规则（第 22 次）

> [!SUMMARY] 📌 复发摘要
> 用户报告**宿舍 WiFi** 下"外网无法正常连接"（VPN = 小火箭，额度充裕）。三层诊断：**小火箭（Rocket/ClashR）在线**（PID 29676，控制端口 4788、HTTP 4780、系统代理 `127.0.0.1:4780`）、`/configs.mode = rule`（✅ **排除** mode 异常，非 direct/global）、**OpenAI 5 条分流规则被清空**（=「订阅更新清 OpenAI 分流规则」累计**第 22 次**），chatgpt.com 落入 `MATCH→Others→Proxy→🔰国外流量→台湾 03` **单节点链**。⚠️ **本次无法复现"外网无法连接"**——走代理实测 google / youtube / github / telegram / reddit 等**全部 200 可达**（显式 `curl -x` 与系统代理/WinINET 两条路径均通），代理栈端到端判定为**健康**；报错最可能源于 **18:15 订阅更新瞬间的隧道抖动**（更新重写 `rocket.yaml` 的当口连接被切）。尽管外网已恢复，仍**按 skill 第六步把 OpenAI 规则补回**（钉死 台湾 03 中華電信），避免后续 codex/models 落入单节点链被抖断。处置：**备份 → 补 5 条 OpenAI 规则 → 台湾 03 中華電信 → 热加载 204 → /rules 5 条 + codex/models 401 + 外网全 200 验证**。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | 运行态 `/configs.mode` | `rule` ✅（非 direct/global，排除 mode 异常） |
| 代理配置 | 运行态 `/configs.port` | `4780`（HTTP）/ `4781`（SOCKS）；`mixed-port=0`；控制 API 在 `4788` |
| 代理配置 | OpenAI 分流规则（5 条） | <span style="color:#ff0000">被清空（=0）</span>（「订阅更新清规则」累计第 22 次） |
| 代理配置 | 配置文件摘要 | `rocket.yaml` 与 **08-30 修复前备份**逐字节一致（SHA256 前缀 `f002e5d64bbcc6941049`，70654 字节）→ 说明订阅更新把配置**整体回退**到未加 OpenAI 规则的状态 |
| 代理配置 | MATCH 兜底 | `- MATCH,Others` → Others→Proxy→🔰国外流量 |
| 环境层 | 进程 | 小火箭 `clashr-windows-amd64.exe` PID 29676 运行中 |
| 环境层 | 系统代理 | `ProxyEnable=1`、`ProxyServer=127.0.0.1:4780` ✅（指向小火箭） |
| 网络层 | 走显式代理实测外网 | `curl -x http://127.0.0.1:4780` google / youtube / github / telegram / reddit 等**全部 200** ✅（google 8/8 稳定） |
| 网络层 | 走系统代理实测外网 | PowerShell `Invoke-WebRequest` (WinINET) 同域**全部 200** ✅ |
| 网络层 | 走代理实测 `codex/models` | **401**（OpenAI 可达）✅ |

### 修复过程

1. **三层诊断**：`/configs`（mode=rule / port=4780 / mixed-port=0）、`/rules`（OpenAI 规则 = 0）、/proxies（🔰国外流量 = 台湾 03）；先走显式代理与系统代理两条路径实测外网——**均 200 可达**，判定代理栈端到端健康（无法复现报错，倾向瞬时抖动）。
2. **备份**：`原始文件备份/rocket-config-20260831-1-before-fix.yaml`（70654 字节，SHA256 `F002E5D64BBCC69410495F45B0D8A799B2A8ECC7F290C508FE5B037907EC597E`；另有 08-30 早晨的 `rocket-config-20260830-1-before-fix.yaml`）。
3. **改 `rocket.yaml`**：在 `GEOIP,CN,Domestic` 之后、`- MATCH,Others` 之前插入 5 条 OpenAI 规则 → `台湾 03 中華電信`（`openai.com / chatgpt.com / chatgpt-api.com / oaistatic.com / oaiusercontent.com`），钉死到迁移期一致的最稳节点。
4. **热加载**：`PUT /configs?force=true` body `{"path":"C:/Users/asus/AppData/Roaming/Rocket/clash-configs/rocket.yaml"}`（⚠️ 用**正斜杠**路径，反斜杠报 `Body invalid`，见 00:10 复发新坑②）→ **HTTP 204**。
5. **验证**：`/rules` OpenAI 规则 **5 条 → 台湾 03 中華電信**；走代理实测 `codex/models` **401**；外网 google 等**全 200**。

> [!warning] ⚠️ 关键认知（本次补充）
> **① 本次是少见的"报错已自愈"案例**：用户报告"外网无法连接"，但实测代理栈端到端健康、外网全 200——报错大概率是 **18:15 订阅更新重写 rocket.yaml 的当口连接被切**造成的瞬时抖动，而非持续故障。**诊断时先走「显式代理 + 系统代理」双路径实测**，能快速区分"真故障"与"瞬时抖动"。
> **② 订阅更新并非只清 OpenAI 规则，而是把整个配置回退到上次未加规则的状态**（08-30 备份逐字节一致）。因此 OpenAI 规则这种**非订阅内容的手工改动一定会被下一次订阅更新清掉**——这是迁移节的「遗留事项①」，已成高频复发根因（N1 累计 22 次）。
> **③ 哪怕外网已恢复，也要把 OpenAI 规则补回**：chatgpt.com 单走 `MATCH→Others→Proxy→🔰国外流量→台湾 03` 单节点链，一旦该节点抖动就会把 Codex 入口一并抖断；钉死规则才能隔离 OpenAI 流量。**"外网能通" ≠ "Codex 稳"**（与 08-07 案例的 "Codex 能用 ≠ 节点快" 同理，方向相反）。

> [!NOTE] 📌 与「VPN 客户端迁移」小节的关系
> 本复发是迁移节「遗留事项①：订阅更新会清掉 OpenAI 规则」的**连续第 2 次被触发**（00:10 第 21 次 → 18:58 第 22 次，同日两次）。规律已非常明确：**只要点小火箭 GUI 的刷新订阅，rocket.yaml 就会被整体重写、OpenAI 规则必被清掉、需重新补回**。用户若不想反复手动补，需在订阅更新后养成「检查 `/rules` 是否还有 5 条 OpenAI 规则」的习惯。

## 🔁 复发记录（2026-08-31 19:15）：OpenAI 钉死的台湾 03 数据中心 IP 被 Cloudflare 风控致 chatgpt.com 403——改钉新加坡 01 Singtel（用户要求排除港台澳）

> [!SUMMARY] 📌 复发摘要
> 用户报告宿舍 WiFi 下「外网仍连不上」，并**硬性要求 OpenAI 与通用流量必须走「非香港/台湾/澳门」节点**。多 Agent（代码总监 + 3 子代理）诊断：**通用流量正常**（走代理 google/youtube/github 全 200、api.openai.com 401），**真正卡点是 OpenAI 被钉死在「台湾 03 中華電信」——该节点出口为数据中心 IP，被 Cloudflare 风控，致 chatgpt.com 返回 403 人机验证拦截页（CF-RAY `-KHH` 台湾高雄）**。深层缺陷：**晨间「选台湾 03」所用的 `api.openai.com 返 401` 是假阳性**——不带 key 时 api.openai.com 恒返 401，与节点是否被 CF 风控无关；真实判别标准是 chatgpt.com 是否回非 challenge 状态。处置：**备份 → 多 Agent 逐节点实测（9 候选全 chatgpt 200 + api 401 + 出口 ICN/SIN/LAX 非港台澳）→ 改钉双 Agent 验证 + ISP 品牌线路（风控面小）的 新加坡 01 Singtel → 热加载 204 → 验证规则 5 条非港台澳 + api 401 + 通用全 200**。

### 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 代理配置 | OpenAI 5 条规则目标 | 改前=台湾 03 中華電信（数据中心 IP，被 CF 风控）→ 改后=**新加坡 01 Singtel**（非港台澳） |
| 代理配置 | 运行态 `/configs.mode` | `rule` ✅（非 direct/global，排除 mode 异常） |
| 网络层 | `chatgpt.com` 走代理 | **403 + `Cf-Mitigated: challenge`**（CF-RAY `-KHH` 台湾高雄）——数据中心 IP 被风控，用户「连不上」的真正卡点 |
| 网络层 | `api.openai.com/v1/models` | **401**（不带 key 恒返 401，**假阳性判据**——不能用来判是否被 CF 风控） |
| 网络层 | 通用外网站点 | google/youtube/github/wikipedia 全 200/204 ✅（通用流量正常，排除全站断） |
| 网络层 | 逐节点实测（9 候选） | 韩国 07/01/06/03 SK텔레콤(ICN)、新加坡 01/04 Singtel(SIN)、日本 01 NTTドコモ、美国 06 IDC&VERTEX(LAX)、美国 01(SJC) **全 chatgpt 200 无 challenge + api 401 + 出口非港台澳** |
| 网络层 | 延迟（gstatic） | 美国 06 460ms / 新加坡 01 509ms / 韩国 07 511ms / 美国 01(对照) 576ms |
| 环境层 | 第二代理客户端 | 仅 ClashR(PID 29676)，无可冲突的 mihomo/Vortex；7897/7898 已释放 |
| 环境层 | TUN / IPv6 | 无 TUN 适配器；WLAN2 仅 IPv4 无原生 v6；Teredo active（风控诱因，非主因） |
| 环境层 | 系统代理 / DNS | ProxyEnable=1 + 127.0.0.1:4780；WLAN2 DNS=223.5.5.5+114.114.114.114（无残留 8.8.8.8）；chatgpt.com 本地解析被污染成 Facebook IP（仅影响直连路径） |

### 修复过程

1. **三层诊断 + 系统侧复核**：`/configs`（mode=rule）、`/rules`（5 条 OpenAI 规则已存在，但钉死台湾 03）、`/proxies`（通用出口美国 01）；双路径（显式 + 系统）实测确认通用流量 200、api.openai.com 401、**chatgpt.com 403+challenge** → 定位卡点为 OpenAI 节点被 CF 风控。
2. **多 Agent 并行**：① Agent A 只读枚举非港台澳节点 + `/proxies/{name}/delay` 延迟体检（198 叶子，排除 24 个港台澳，172 实测）；② Agent C 系统侧诊断（无第二客户端/无 TUN、DNS 污染、challenge 根因）；③ **代码总监**独立核验 + 风险唱反调（指出备份缺失、台湾节点违反硬性要求、单点钉死风险）。
3. **备份**：`原始文件备份/rocket-config-20260831-1915-before-openai-node-change.yaml`（71351 字节，SHA256 `8b69a30b71ca222f764c8812d95815b960f7b6ac3235739d233f07fb84783002`）。
4. **改 `rocket.yaml`**：5 条 OpenAI 规则 台湾 03 中華電信 → **新加坡 01 Singtel**（第 1264-1268 行），并更新第 1263 行注释说明新根因。
5. **热加载**：`PUT /configs?force=true` body `{"path":"C:/Users/asus/AppData/Roaming/Rocket/clash-configs/rocket.yaml"}`（正斜杠，反斜杠报 `Body invalid`）→ **HTTP 204**。
6. **验证**：`/rules` 5 条 → 新加坡 01 Singtel（**不含港台澳**）；走代理 `api.openai.com` **401**（可达）；通用 google **204** / youtube / github **200**；`chatgpt.com` **403**（urllib/juan 无浏览器指纹所致，视为弱信号，留待用户浏览器/Codex 终验）。

> [!warning] ⚠️ 关键认知（本次新坑 / 重大纠偏）
> **① ⚠️「api.openai.com 返 401」不能作为节点是否被 CF 风控的判据——它是假阳性**：不带 key 时 api.openai.com 恒返回 401（哪怕节点被风控）；若节点完全不可达才返回 000/超时。晨间「选台湾 03」正是拿 401 当「全通过」，把被风控的数据中心节点误选为最稳节点。**真正判别标准 = chatgpt.com 是否返回非 challenge 状态（200/302）**。
> **② 数据中心 IP 更易被 Cloudflare 风控，ISP 品牌线路风控面更小**：台湾 03（中華電信数据机房）/美国 06（IDC）这类机房 IP 易被 CF 判 bot；新加坡 01 Singtel、韩国 SK텔레콤 这类真实 ISP 品牌线路风控面小。选 OpenAI 节点应优先 ISP 线路。
> **③ chatgpt.com 返 403 依赖 TLS 指纹（JA3/JA4）/UA/Cookie**：用 `requests`/urllib 这类无浏览器指纹的客户端，chatgpt.com 可能回 200 也可能回 403（不稳定、弱判据）。**改节点后必须由用户在真实浏览器/Codex 终验**，日志如实说明未在代理侧 100% 复现用户的风控现象。
> **④ 用户硬性要求「排除香港/台湾/澳门节点」**：本次已把 OpenAI 钉死的台湾 03 改为新加坡 01 Singtel，通用出口仍为美国 01（在轨、稳定，按代码总监建议暂不盲换）；**任何港/台/澳节点（含「台湾 01-08」「香港 01-16」「★自动选择|香港最优★」）一律不再作为 OpenAI 或通用出口**。

> [!NOTE] 📌 与「VPN 客户端迁移」小节的关系
> 本复发是**对迁移节「遗留事项①」后续的深化**：迁移期选「台湾 03」依赖的判据（api.openai.com 401）经多 Agent 复核为**假阳性**，实际该节点被 CF 风控。本次为满足用户「排除港台澳节点」的硬性要求，并把 OpenAI 从被风控的数据中心节点迁到 ISP 品牌线路（新加坡 01 Singtel）。遗留事项①（订阅更新清规则）仍未根除——+ 新增「订死节点的 IP 若被风控需随节点切换复核」的认知。

## 🔄 VPN 客户端迁移（2026-08-18 15:45）：SakuraCat（Vortex/mihomo）→ 小火箭（Rocket/ClashR）

> [!SUMMARY] 📌 迁移摘要
> 用户明确要求 **停用 SakuraCat，改用小火箭（Rocket，ClashR 内核）** 作为代理客户端。本机长期并存两套代理：SakuraCat（mihomo/Vortex，端口 7897 + TUN）与小火箭（ClashR，端口 4780）。本次迁移 = **小火箭配置 OpenAI 分流规则（指向 🇹🇼 台湾 03 中華電信）+ 系统代理切到 4780 + 停用并禁用 SakuraCat 服务与进程**，OpenAI 全链路经小火箭实测恢复可达。

### 🚀 小火箭关键信息

| 项目 | 值 |
|---|---|
| 内核 | `clashr-windows-amd64.exe`（ClashR 遗留版） |
| HTTP / SOCKS 端口 | 4780 / 4781 |
| 控制 API | `127.0.0.1:4788`（来自 `configs.json` controllerPort；rocket.yaml 声明的 9090 仅是文件内配置） |
| 运行配置 | `C:\Users\asus\AppData\Roaming\Rocket\clash-configs\rocket.yaml`（196 节点 / 6 分组 / 679 规则） |
| 订阅地址 | `https://212.50.235.33:22696/ssp/huojian/link/DjegUrjkAN3skIq4?clash=9`（机场代号 "huojian"） |
| 分组结构 | `Proxy → 🔰国外流量`（196 国外节点）→ `Domestic / AsianTV / GlobalTV / Others` |

### 🔧 迁移过程

1. **节点体检（Rocket 机场实测）**：对 5 个候选节点实测 —— **台湾 01/03/05 中華電信（211.20.157.x）、美国 02 AT&SANJOSE（134.195.101.22）、日本 02 NTT（116.80.64.234）全部放行 `api.openai.com`（401 预期码）**；而原选中节点「★自动选择|香港最优★」经**英国出口（81.168.109.211）被 Cloudflare 风控**（api 403）→ 判定必须为 OpenAI 加专用分流规则。
2. **添加 OpenAI 分流规则**：`rocket.yaml` 规则段顶部插入 5 条 `DOMAIN-SUFFIX, openai.com / chatgpt.com / chatgpt-api.com / oaistatic.com / oaiusercontent.com → 🇹🇼 台湾 03 中華電信`。备份 → `原始文件备份/rocket-config-20260818-1545-before-fix.yaml` → 热加载（`PUT /configs?force=true` 204）。
3. **规则独立生效验证**：把 🔰国外流量 分组切到坏节点「英国 01 伦敦」（出口确认英国 94.156.250.87），`api.openai.com` **仍返回 401** → 证明 OpenAI 规则独立生效、不受分组选中节点影响；随后将分组切回 🇹🇼 台湾 03（出口 211.20.157.201 台中）。
4. **系统代理切换**：`ProxyEnable=1, ProxyServer=127.0.0.1:4780`（此前 ProxyEnable=0、ProxyServer=7897——流量实际靠 SakuraCat 的 TUN 接管）。
5. **停用 SakuraCat**：结束 `SakuraCat.exe`×5；提权（UAC）`Stop-Service + Set-Service -StartupType Disabled` 停止并禁用 `com.vortex.helper` 服务（无 TUN 适配器残留，无流量劫持）。
6. **最终验证（经系统代理 4780）**：`api.openai.com` → **401** ✅、`chatgpt.com` → **403**（Turnstile 人机验证页，curl 无 cookie 属正常）✅、`chatgpt.com/backend-api/codex/check_login` → 403 ✅、退出 IP = **🇹🇼 台湾 台中（211.20.157.201）** ✅。

### ⚠️ 遗留事项与风险

1. <span style="color:#ff0000">**订阅更新会清掉 OpenAI 规则**（同 SakuraCat N1 问题）</span>：小火箭 GUI 刷新订阅会重写 `rocket.yaml`、清掉这 5 条规则，届时需重新添加（备份 `rocket-config-20260818-1545-before-fix.yaml` 内含本次规则模板）。
2. `chatgpt-api.com` 域名经台湾节点 TLS 握手失败（`schannel: failed to receive handshake`）：该域名非 GPT 网页 / Codex 实际使用域名（实际走 `chatgpt.com/backend-api` 与 `api.openai.com`），规则保留但无实际影响；介意可移除该行。
3. **系统代理已接管 4780**：若浏览器仍显示旧出口，重启浏览器（Edge/Chrome 需重新读取 WinINET 代理设置）。
4. `com.vortex.helper` 服务已**禁用**：如需回退 SakuraCat，需重新启用服务并恢复 TUN 模式。

### 🔧 迁移后续修复（2026-08-18 15:56）：OpenAI 节点超时 + mode 被切 global → 改 URLTest 自动优选组

> [!SUMMARY] 📌 跟进摘要
> 迁移完成后用户反馈"还是无法打开"。诊断发现两个叠加问题：① **小火箭核心运行态 `mode` 被切到 `global`**（GLOBAL 选中已宕机的「美国 01 AT&SANJOSE」）——全局模式绕过分流规则，OpenAI 全走死亡节点 → 000 打不开；② **OpenAI 规则目标「台湾 03 中華電信」当时超时**（08-18 节点波动）。处置：`mode` 切回 `rule` + 新增 **`★OpenAI|自动优选★` url-test 分组**（健康检查直指 `https://api.openai.com/v1/models`，成员含 日本 03 / 台湾 08 / 台湾 05 / 台湾 01 / 日本 02 / 美国 02，**自动 failover**）→ OpenAI 规则目标改为该组 → 实测稳定。

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| mode | 🔴 `global`（绕过分流） | ✅ `rule`（稳定，4 次采样未回弹） |
| OpenAI 规则目标 | 🔴 台湾 03 中華電信（已超时 504） | ✅ `★OpenAI\|自动优选★`（URLTest，当前优选 日本 03） |
| api.openai.com | 🔴 000 超时 | ✅ 401（0.8-1.5s，×3 稳定） |
| chatgpt.com | 🔴 000 / 403 抖动 | ✅ 403 Turnstile（预期码，×3 稳定） |
| 退出 IP | 🔴 美国 01（宕机） | ✅ 🇯🇵 日本 03（116.80.49.65） |

- **根因定性**：台账 **N6（节点质量波动 / 机场线路故障）+1 → 6**；叠加小火箭运行态被切 `global` 属一次性现象（未见复发，若小火箭 GUI 存在「全局模式」开关，请保持在**规则模式**）。
- **联动修改**：`configs.json` 默认节点 `currentProxy` 改为 `日本 03 NTTドコモ`（避免 GUI 回写选中到已宕机的美国 01）；`rocket.yaml` 内 OpenAI 规则目标统一为 `★OpenAI|自动优选★` 组。

### 🔍 迁移后浏览器确认（2026-08-18 16:15）：Firefox「代理服务器拒绝连接」为迁移期瞬时故障 + `127.0.0.1:8000` 实为本地开发应用（排除误判）

> [!SUMMARY] 📌 跟进摘要
> 迁移完成后 Firefox 报 `代理服务器拒绝连接`（`Firefox 无法连接到 chatgpt.com 的服务器`）。逐层排查后定性：**这是迁移窗口期的瞬时故障，当前已自愈**；netstat 里持续出现的 `127.0.0.1:8000` SynSent **不是代理连接，是用户本机开发应用的后端调用**（`localhost:3000` 前端页面在 fetch `127.0.0.1:8000/api/*`，而 8000 后端未启动）——**属红鲱鱼，与本次代理故障无关**，勿再据此误判代理被切。

**三层诊断数据：**

| 检查项 | 结果 | 结论 |
|---|---|---|
| 系统代理注册表 | `ProxyEnable=1` `ProxyServer=127.0.0.1:4780` `AutoConfigURL=空` | ✅ 指向小火箭 HTTP 端口，正确 |
| 小火箭核心/监听 | `clashr-windows-amd64`（PID 50388）存活；4780/4781/4788 均在监听 | ✅ 代理进程在线 |
| 运行态 mode / 规则 | `mode: rule`；顶部 5 条 OpenAI 规则 → `★OpenAI\|自动优选★`（679 条规则齐全） | ✅ 分流正常 |
| 代理实测 | `chatgpt.com→403`、`api.openai.com→401`、`baidu.com→200`（均经 4780） | ✅ 代理链路通（403/401 为 CF 预期码） |
| Firefox cookies | `chatgpt.com` 全套 + `cf_clearance` 写入时间 **16:12:43** | ✅ 证明 Firefox 已通过 Cloudflare Turnstile、成功加载过 chatgpt.com |
| `127.0.0.1:8000` 连接 | 监听 8000 抓到明文请求：`GET /api/error-logs?limit=50`、`GET /api/collections/...`，`Referer/Origin: http://localhost:3000/` | ✅ 是本机 Node 开发应用（node.exe 监听 3000）在调自己的后端，8000 后端未启动 → SynSent 重试 |

- **根因定性**：本次「代理服务器拒绝连接」发生在 **SakuraCat 停止 → 小火箭接管** 的迁移窗口（或此前 OpenAI 节点超时 / mode=global 时段），当时浏览器走的代理路径短暂不可用所致；URLTest 自动优选组落地 + 节点恢复正常后已自愈（cookies 16:12:43 为自愈证据）。**不新增台账行**（非新根因，属 N6 节点波动 + 迁移期瞬态）。
- **排除项**：Firefox 三个 profile 的 `prefs.js` / `user.js` / 企业策略 / 扩展权限均无任何 `network.proxy.*` 配置（无 FoxyProxy/SwitchyOmega 类扩展）→ 浏览器本身没有指向 8000 的代理设置；`127.0.0.1:8000` 与代理无关。
- **遗留提示**：若 Firefox 再报 `代理服务器拒绝连接`，先看是否小火箭核心（PID clashr / 端口 4780）掉线或 GUI 被切全局模式；`netstat` 里对 `127.0.0.1:8000` 的 SynSent 一律先按「本地开发应用后端未启动」排除，勿当代理故障处理。

## 🔗 相关笔记与附件

- [[05-Codex网络故障-青旅环境]] — 🏨 **青旅环境**档案：Vortex 被切到 direct 模式导致隧道未建立（2026-08-06 晚），与本文档互补
- [[02-后台任务UUID引用悬空]] — 相似表象但根因不同；该条是会话元数据引用悬空，本条是网络连接被重置。
- [Rocket 迁移前配置备份](原始文件备份/rocket-config-20260818-1545-before-fix.yaml)
- Codex 现场日志：`C:\Users\asus\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\Codex\Logs\2026\08\04\`
