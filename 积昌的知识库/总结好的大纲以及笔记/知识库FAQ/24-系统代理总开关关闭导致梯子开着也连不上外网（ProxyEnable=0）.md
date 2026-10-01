---
title: "系统代理总开关关闭导致梯子开着也连不上外网（ProxyEnable=0）"
type: "知识库 FAQ / 报错修复"
date: 2026-09-20
created: 2026-09-20
updated: 2026-09-20
environment: "🏫 学校宿舍（校园 WiFi / Windows 11 / Vortex-mihomo）"
tags:
  - 系统代理
  - ProxyEnable
  - Vortex
  - mihomo
  - 校园网
  - mode global
  - 订阅清规则
  - 网络故障
  - 宿舍
source: "2026-09-20 22:11 宿舍现场：用户报「使用了梯子但无法连接外网」，实测诊断与修复"
---

# 🏫 系统代理总开关关闭导致梯子开着也连不上外网（ProxyEnable=0）

> [!summary] 📊 报错统计速览（截至 2026-09-20）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（2026-09-20 原始事件 1 次，暂无复发）。本次为<span style="color:#ff0000">四根因叠加</span>：主根因 **「系统代理总开关关闭（ProxyEnable=0）」**（台账 N18，累计 1 次，新类型），伴随 **运行态 mode 被切 global**（N2 累计 12 次）、**订阅更新清 OpenAI 分流规则**（N1 累计 23 次）、**OpenAI 规则指向节点对 OpenAI 不通**（N6 累计 7 次）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 系统代理总开关关闭（ProxyEnable=0，GUI 未运行无人设置） | **1** | 24（新类型） |
> | 🔴 运行态 mode 被切 global（GLOBAL 指向单节点） | **12** | 05 / 04 / 24 |
> | 🔴 订阅更新清 OpenAI 分流规则 | **23** | 04（为主）/ 05 / 06 / 24 |
> | 🟠 规则指向节点对 OpenAI 域名不通（美国-中转 01 Timeout） | **7** | 04 / 05 / 24 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!info] 📍 适用环境：🏫 校园网 / 宿舍
> 校园网在**路由器/防火墙层直接封锁境外站点**（实测直连 google 超时、baidu 200），因此「能否上外网」完全取决于**流量有没有进代理隧道**。本次故障的本质：<span style="color:#ff0000">梯子进程活着、隧道也通，但系统代理总开关是关的——没有任何流量被送进代理</span>，应用全部直连被校园网拦死。相关环境档案：[[15-校园网Firefox不走代理导致境外无法访问]]（校园网特征）、[[05-Codex网络故障-青旅环境]]（mode 异常家族）。

> [!SUMMARY] 📌 结论摘要
> 用户在学校宿舍报「使用了梯子，但无法连接外网」。三层诊断结果：<span style="color:#1e90ff">Vortex（mihomo）进程在线、7897 端口在听、走 7897 实测 google 302 —— **代理隧道本身是通的**</span>；但 <span style="color:#ff0000">Windows 系统代理总开关 `ProxyEnable=0`（关闭状态），ProxyServer 残留指向 127.0.0.1:7897 却不生效</span>——跟随系统代理的应用（Edge/Chrome/Firefox type=5）全部直连，境外被校园网拦死，表现为"开了梯子也连不上外网"。同时发现三重叠加隐患：① <span style="color:#ff8c00">运行态 `mode: global`</span>（GLOBAL 强制走 🇸🇬新加坡-中转 02，国内流量也被拉去绕境外）；② <span style="color:#ff8c00">OpenAI 5 条分流规则被清</span>（65 条出厂规则，订阅更新重写所致）；③ 补回规则后 <span style="color:#ff8c00">美国-中转 01 对 api.openai.com 超时</span>（gstatic 通但对 OpenAI 不通）。处置：`ProxyEnable=1` + 运行态切回 rule + 配置文件恢复 5 条 OpenAI 规则（→🇺🇸美国-中转 02）+ 补 `ipv6: false` + 热加载 204。终验：<span style="color:#1e90ff">api.openai.com 401（放行）/ chatgpt.com 带 UA 200 / google·youtube·github·baidu 全 200</span>。

## 🧭 快速索引

- [[#🚨 错误概览|🚨 错误概览]]
- [[#🧩 根本原因|🧩 根本原因]]
- [[#🔬 三层诊断数据|🔬 三层诊断数据]]
- [[#🛠️ 修复过程|🛠️ 修复过程]]
- [[#🧱 排查中遇到的问题（踩坑）|🧱 排查中遇到的问题（踩坑）]]
- [[#🧰 技术栈与术语|🧰 技术栈与术语]]
- [[#✅ 验证结果|✅ 验证结果]]
- [[#🛡️ 后续建议与遗留事项|🛡️ 后续建议与遗留事项]]
- [[#🔗 相关笔记与附件|🔗 相关笔记与附件]]

## 🚨 错误概览

| 项目 | 现场信息 |
|---|---|
| 记录时间 | 2026-09-20 22:11–22:30（Asia/Shanghai） |
| 网络环境 | 🏫 **学校宿舍**（校园 WiFi，防火墙层封锁境外 + 污染 DNS） |
| 现象 | 用户开了梯子（Vortex 进程在跑），但浏览器/应用打不开外网 |
| 直连检测 | baidu **200**（0.22s）、google **000**（8s 超时被拦）——校园网选择性封锁特征 |
| 代理进程 | `com.vortex.helper`（PID 19320，服务型 Session 0）在线；<span style="color:#ff8c00">**Vortex GUI 未运行**</span> |
| 关键证据 ① | 注册表 <span style="color:#ff0000">`ProxyEnable=0`</span>（系统代理总开关关闭），`ProxyServer=127.0.0.1:7897` 残留但无效 |
| 关键证据 ② | 运行态 `/configs.mode` = <span style="color:#ff0000">`global`</span>（GLOBAL → 🇸🇬新加坡-中转 02）；规则 65 条出厂版（OpenAI 5 条被清） |
| 走代理实测（修复前） | google via 7897 = **302**（隧道通！）；api.openai.com / chatgpt.com = 000 超时 |
| 最终状态 | <span style="color:#1e90ff">已修复（系统代理开启 + rule 模式 + OpenAI 规则恢复，全站可用）</span> |

> [!IMPORTANT] ⚠️ 关键认知
> **「梯子开着」= 进程在跑 ≠ 流量在走代理。** Vortex 是<span style="color:#2980b9">服务进程（Session 0）+ GUI 分离</span>架构：只开服务时，`ProxyEnable` 没人设置。系统代理总开关一关，Edge/Chrome/Firefox（type=5 跟随系统代理）就**全部直连**——在校园网环境等于"没开梯子"。排查口诀：<span style="color:#ff8c00">先查注册表 `ProxyEnable`，再查隧道（走 7897 实测），最后才查节点</span>。

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 🔴 环境层（主根因） | <span style="color:#ff0000">系统代理总开关被关（`ProxyEnable=0`），应用流量根本不进代理</span> | 注册表 `Internet Settings`：`ProxyEnable=0`、`ProxyServer=127.0.0.1:7897`（指向还在但开关关闭） | `Set-ItemProperty ProxyEnable=1`，即时生效 |
| 🔴 代理配置层（叠加） | <span style="color:#ff0000">运行态 `mode: global`</span>：强制所有流量（含国内）走 GLOBAL 组指向的 🇸🇬新加坡-中转 02，忽略分流规则 | `/configs`：`mode: global`；`/proxies`：`GLOBAL.now=新加坡-中转 02`；磁盘配置文件却是 `mode: rule`（运行态被切，05 已知 global 变体） | `PATCH /configs {"mode":"rule"}` + 热加载 |
| 🟠 代理配置层（叠加） | <span style="color:#ff8c00">OpenAI 5 条分流规则被清空</span>（65 条出厂规则），openai/chatgpt 域名掉进 `MATCH → 节点选择` | `/rules`：65 条、无 openai/chatgpt 规则（「订阅更新清规则」累计第 23 次） | 配置文件恢复 5 条规则（→🇺🇸美国-中转 02）+ 热加载 |
| 🟠 网络层（叠加） | <span style="color:#ff8c00">美国-中转 01 节点对 api.openai.com 超时</span>（gstatic 204 测速 229ms 正常——"delay 通 ≠ 程序实测通"） | 节点 delay 实测：美国-中转 01 对 `api.openai.com/v1/models` = **Timeout**；美国-中转 02 = **233ms** 全场最优 | OpenAI 规则改指 🇺🇸美国-中转 02 |
| 🟡 伴随项 | `ipv6: true` 回退（10 档案已知坑，订阅重写后恢复默认） | `/configs.ipv6=True` | 配置文件补 `ipv6: false` + 热加载 |

**一句话**：校园网拦境外 + 系统代理开关关闭（主因）→ 应用全直连；就算手动走 7897，mode=global + OpenAI 规则被清 + 规则节点不通又把 OpenAI 系拦住——四层问题叠出"开了梯子也连不上外网"。

## 🔬 三层诊断数据

### 1. 环境层（系统代理与校园网）

| 检查项 | 结果 | 判定 |
|---|---|---|
| 直连 baidu.com | 200（0.22s） | 校园网放行国内 ✅ |
| 直连 google.com | 000（8s 超时） | 校园网封锁境外 |
| `ProxyEnable` | <span style="color:#ff0000">**0**</span> | <span style="color:#ff0000">系统代理总开关关闭（主根因）</span> |
| `ProxyServer` | `127.0.0.1:7897` | 指向正确但开关关闭=无效 |
| `ProxyOverride` | localhost;127.*;10.*;172.16-31.*;192.168.* | 本地绕过列表完整 |
| Vortex 进程 | `com.vortex.helper` PID 19320（服务） | 在线；<span style="color:#ff8c00">GUI 未运行</span> |
| 监听端口 | 53（DNS 劫持）/ 7897（mixed-port）/ 39797（控制 API） | 正常；⚠️ 控制 API 在 **39797**（04/05 老档案里的 39798 已过时） |

### 2. 代理配置层（运行态 vs 磁盘）

| 检查项 | 运行态（修复前） | 磁盘配置文件 |
|---|---|---|
| `mode` | <span style="color:#ff0000">`global`</span> | `rule`（持久层正常，运行态被切） |
| GLOBAL 组指向 | 🇸🇬新加坡-中转 02 | — |
| 规则数 | 65（出厂版，OpenAI 0 条） | 65（同被清） |
| `ipv6` | true | （缺失，补插 false） |
| `tun.enable` | false | false |

### 3. 网络层（节点 delay 体检）

- 56 个真实节点对 gstatic 204 全部在线（机场订阅已续费，与 [[22-机场订阅到期导致小火箭节点清空（全站境外无法访问）]] 的到期状态不同）：香港-IEPL 01 = 89ms、日本-中转 02 = 90ms、美国-中转 01 = 229ms。
- <span style="color:#ff8c00">关键分野</span>：对 `api.openai.com/v1/models` 复测——美国-中转 02 = **233ms** / 香港-IEPL 01 = 286ms / 美国-IEPL 02 = 339ms 可用；<span style="color:#ff0000">美国-中转 01 = Timeout、台湾-IEPL 02 = Timeout</span>。
- 走 7897 实测（修复前）：google 302 ✅（经 GLOBAL→新加坡）、baidu 000/200 抖动（国内也被拉去绕境外，global 模式副作用）、api.openai.com 000、chatgpt.com 000。

## 🛠️ 修复过程

1. **复现与分层对照**：直连 baidu 200 / google 000 → 校园网封锁特征；走 7897 测 google 302 → **隧道本身是通的**，故障在"流量没进代理"。
2. **查系统代理（PowerShell，规避 Git Bash `reg query` 静默失败坑）**：`ProxyEnable=0` → <span style="color:#ff0000">锁定主根因</span>。
3. **备份**：`config.yaml` → `总结好的大纲以及笔记/知识库FAQ/原始文件备份/vortex-config-20260920-2215-before-fix.yaml`（SHA256 前 16 位 `a9532c212d1333c8`）。
4. **改配置文件（持久层）**：恢复 5 条 OpenAI 规则（→🇺🇸美国-中转 02，2 空格缩进与出厂一致）+ 补顶层 `ipv6: false`；`python -c` + `yaml.safe_load` 自检（70 条规则、98 节点无重名）。
5. **切运行态**：`PATCH /configs {"mode":"rule"}` → 204。
6. **热加载**：`PUT /configs?force=true`（空 body `{}`）→ 204；复核运行态 mode=rule / ipv6=False / 70 条规则。
7. **开系统代理**：`Set-ItemProperty 'HKCU:\...\Internet Settings' -Name ProxyEnable -Value 1`（ProxyServer 已是 7897，ProxyOverride 保留原值）；`GetSystemWebProxy()` 验证 google/baidu 均解析到 `http://127.0.0.1:7897/`。
8. **节点复测与规则修正**：OpenAI 规则初指美国-中转 01 → 实测 Timeout → 批量体检后切 🇺🇸美国-中转 02（233ms）→ 再热加载 → 复测全通。

```bash
# 切模式（mihomo 标准 API）
curl -X PATCH "http://127.0.0.1:39797/configs" -H "Content-Type: application/json" -d '{"mode":"rule"}'
# 热加载（空 body 重载当前配置文件；带 path 的转义容易踩坑，见踩坑③）
curl -X PUT "http://127.0.0.1:39797/configs?force=true" -H "Content-Type: application/json" -d '{}'
```

## 🧱 排查中遇到的问题（踩坑）

1. **<span style="color:#ff0000">Git Bash 里 `reg query` 查系统代理静默失败</span>**：`reg query ... | grep -i proxy` 无任何输出，差点误判"系统代理未配置"。这是 05 档案已知坑——改 PowerShell `Get-ItemProperty 'HKCU:\...\Internet Settings'` 一次拿到全部字段。
2. **<span style="color:#ff8c00">YAML 块序列缩进不一致导致热加载 400</span>**：插入的 5 条规则用 0 空格缩进（`- DOMAIN...`），出厂规则全是 2 空格缩进（`  - DOMAIN...`），mihomo 解析出畸形结构，报 `proxy [🇺🇸|美国-中转 01 - DOMAIN] not found`（把列表 join 成一条巨型规则）。**教训：往 mihomo 配置里插规则，缩进必须与文件内既有规则一致；改完用 `yaml.safe_load` 自检。**
3. **<span style="color:#ff8c00">全局替换节点名导致"duplicate name" 400</span>**：为切节点把 `美国-中转 01` 全局替换成 `02`，但 proxies 节点清单里 01/02 是**同时存在的两个真实节点**——替换后清单里出现两个 02，mihomo 报 `proxy 🇺🇸|美国-中转 02 is the duplicate name`。二次恢复时又把 02 的定义改没了。最终**从备份恢复原始文件一次性重做**（只动 rules 段，不碰 proxies/proxy-groups 段）。**教训：切规则指向节点时，只改 rules 段里规则的最后一列，严禁全局替换节点名。**
4. **热加载 body 的反斜杠转义**：bash 单引号内 `\\\\` 会变成 JSON 里的 `\\\\`（两层转义），路径非法报 400；<span style="color:#1e90ff">空 body `{}` 即可重载当前配置文件，最稳</span>。
5. **<span style="color:#1e90ff">delay 通 ≠ 程序实测通（第三次验证）</span>**：美国-中转 01 对 gstatic 204 = 229ms 正常，对 `api.openai.com/v1/models` = Timeout。节点体检必须用**目标域名**复测（OpenAI 系用 api.openai.com，401/403 也算"连接完成"）。
6. **控制 API 端口漂移**：本次在 **39797**（与配置 external-controller 一致），04/05 老档案的 39798 已失效。排查第一步先 `netstat -ano | findstr <PID>` 探明真实端口。

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| `ProxyEnable` / `ProxyServer` | Windows 系统代理（WinINET）的总开关与地址，注册表路径 `HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings`。**开关=0 时指向再正确也不生效** |
| Vortex（mihomo 内核） | 代理客户端：`com.vortex.helper` 为服务进程（Session 0），GUI 负责管理系统代理开关；<span style="color:#ff8c00">GUI 不开则没人写 ProxyEnable</span> |
| mixed-port 7897 | HTTP/SOCKS 混合代理端口，应用显式指定或经系统代理进来 |
| `mode: global` | 全局模式：所有流量强制走 GLOBAL 组指向的单节点，忽略分流规则（国内也绕境外，慢且抖） |
| `mode: rule` | 规则分流模式：按 rules 决定直连/代理，**默认应为 rule** |
| 401（api.openai.com） | 未认证=**正常放行**（连接与 TLS 全通），非 403 风控；OpenAI 系可达性判据 |
| CF challenge（403） | Cloudflare 人机验证；curl 无浏览器 UA 访问 chatgpt.com 常见，带 UA 复测 200 即真通 |
| yaml.safe_load 自检 | 改 YAML 配置后用 Python yaml 库解析验证（规则数/重名/类型），避免把坏配置推给热加载 |

## ✅ 验证结果

| 检查项 | 结果 |
|---|---|
| 热加载 | ✅ HTTP 204 |
| 运行态 | ✅ `mode: rule` / `ipv6: False` / mixed-port 7897 / 规则 70 条（OpenAI 5 条 → 美国-中转 02） |
| 系统代理 | ✅ `ProxyEnable=1`、`ProxyServer=127.0.0.1:7897`；`GetSystemWebProxy()` 解析 google/baidu → `http://127.0.0.1:7897/` |
| api.openai.com | ✅ **401**（1.10s，放行非风控） |
| chatgpt.com | ✅ 带 Chrome UA **200**（1.85s；无 UA 403 为瞬时 CF challenge） |
| google / youtube / github | ✅ 200 / 200 / 200 |
| baidu（国内分流） | ✅ 200（0.21s，走 DIRECT） |
| 配置持久层 | ✅ YAML 解析通过：70 条规则、98 节点无重名、`mode: rule`、`ipv6: false`（重启不回退） |

## 🛡️ 后续建议与遗留事项

1. <span style="color:#ff8c00">**"开梯子上不了外网"标准排查顺序（沉淀为口诀）**</span>：① `Get-ItemProperty` 查 `ProxyEnable`（系统代理总开关）→ ② 走 7897 实测 google（隧道通不通）→ ③ `/configs` 查 mode（非 rule 即异常）→ ④ `/rules` 查 OpenAI 规则 → ⑤ 节点对 api.openai.com delay 体检 → ⑥ 进程/端口核对。
2. **Vortex GUI 与服务的关系**：只开服务（com.vortex.helper）时系统代理开关无人管理；<span style="color:#2980b9">建议日常使用时让 Vortex GUI 常驻（或确认其"开机自启 + 自动设置系统代理"选项开启）</span>，避免重启电脑后 `ProxyEnable=0` 复现。**「为何本次 ProxyEnable=0」直接诱因未定**（GUI 未运行 / 用户手动关过 / 重启后未恢复），列观察项。
3. **TUN 模式可选增强**：当前 TUN 关闭，不认系统代理的应用仍走直连。若需全系统接管（含终端工具、非浏览器应用），可在 Vortex 开启 TUN（`tun.enable: true`），参照 [[05-Codex网络故障-青旅环境]] 08-15 复发记录的做法。
4. **订阅更新清规则（第 23 次）未根治**：机场订阅每次更新都会重写 config.yaml 为出厂版。短期靠本 skill 恢复；长期建议（04 档案多次提出）：关闭 Vortex 自动更新订阅，或把 fix 脚本固化（`fix_vortex_config.py` 的 BASE 端口需改为 39797）。
5. **美国-中转 01 列为观察节点**：本次确认其对 OpenAI 域名 Timeout（第三次出现"美国-中转 01 挂"类事件）；当前 OpenAI 规则已切美国-中转 02（233ms），若再失效候选：香港-IEPL 01（286ms）/ 美国-IEPL 02（339ms）。
6. **小火箭状态**：`rocket.yaml` 仍为空配置（27941 B，proxies 0），但小火箭进程未运行、不影响本次故障；机场订阅已续费（Vortex 节点池 56 个全绿），如需启用小火箭先更新订阅。

## 🔗 相关笔记与附件

- [[05-Codex网络故障-青旅环境]] — mode 异常家族（direct/global）与"订阅清规则"的主档案，本次为其第 12 次 mode 异常 + 第 23 次清规则的复发地之一
- [[15-校园网Firefox不走代理导致境外无法访问]] — 校园网封锁境外的环境特征档案
- [[04-Codex桌面端反复重新连接（公司环境）]] — 出口 IP 风控 / 节点速查表
- [[22-机场订阅到期导致小火箭节点清空（全站境外无法访问）]] — 账号到期类根因（本次已续费，节点池健康）
- [[21-关闭代理软件后浏览器打不开国内网站（Firefox手动代理残留）]] — 系统代理/手动代理残留的对照案例
- [[00-报错统计台账]] — N18（本次新类型）/ N1 第 23 次 / N2 第 12 次 / N6 第 7 次
- 配置备份：`总结好的大纲以及笔记/知识库FAQ/原始文件备份/vortex-config-20260920-2215-before-fix.yaml`（修复前原始状态）
