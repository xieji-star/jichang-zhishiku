---
title: "关闭代理软件后浏览器打不开国内网站：Firefox 手动代理残留"
type: "知识库 FAQ / 报错修复"
date: 2026-09-17
created: 2026-09-17
updated: 2026-09-17
environment: "🏠 本地（Windows 11 / Firefox / 代理软件已完全退出）"
tags:
  - Firefox
  - 代理
  - user.js
  - network.proxy.type
  - 4780
  - 浏览器劫持
  - 手动代理
  - 网络故障
  - 知识库自伤
source: "2026-09-17 用户现场反馈：「我的电脑现在被VPN劫持了，不开VPN无法正常使用国内的网站」"
---

# 🔌 关闭代理软件后浏览器打不开国内网站（Firefox 手动代理残留）

> [!summary] 📊 报错统计速览（截至 2026-09-17）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错/修复事件</span>**（2026-09-17 原始事件 1 次，暂无复发）。主根因为 **「Firefox `user.js` 强制手动代理指向失效端口 4780」**（台账 N15，累计 1 次）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 Firefox `user.js` 强制手动代理（`type=1` → `127.0.0.1:4780`，无任何例外规则） | **1** | 21 |
> | 🟠 代理软件完全退出后 4780 端口关闭，请求全部落入死端口 | **1** | 21 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!info] 📍 适用环境：🏠 本地 Windows 11（非校园网）
> 本文档记录**浏览器层**被失效代理劫持的问题，与 [[14-断开VPN后国内网络无法连接（代理残留环境变量与DNS）]] 同属「关闭代理后国内连不上」大类，但<span style="color:#1e90ff">根因层次完全不同</span>：14 号是**系统级**（环境变量 + 网卡 DNS），本文是**浏览器级**（Firefox 自己的代理配置）。外网慢 / 代理分流问题见 [[06-国外网站访问慢但Codex正常]]。

> [!SUMMARY] 📌 结论摘要
> 「电脑被 VPN 劫持、不开 VPN 连国内网站都用不了」<span style="color:#ff0000">不是病毒、不是流量被隧道绑架</span>，而是 **2026-08-31 由「知识库报错修复」skill 自己写进 Firefox 的一条配置**（见 [[15-校园网Firefox不走代理导致境外无法访问]]）在环境变化后变成了陷阱：当时为让 Firefox 在校园网下能上外网，把三个 profile 的 `network.proxy.type` 强设为 <span style="color:#ff8c00">`1`（手动代理）并指向 `127.0.0.1:4780`（小火箭/ClashR），且**没有配置任何例外规则**</span>。后果是：**只要代理软件退出，4780 端口关闭，Firefox 的全部请求（含国内网站）都被送进这个死端口**，于是浏览器什么网站都打不开；而微信、QQ 等程序走系统直连（`ProxyEnable=0`），完全不受影响——这正是「<span style="color:#1e90ff">只有浏览器坏、其他都正常</span>」的由来。改回 Firefox 默认的 `type=5`（跟随系统代理）后，Firefox 全部连接恢复直连，国内网站 <span style="color:#1e90ff">HTTP 200 仅 0.134 s</span>，问题解决。

## 🧭 快速索引

- [[#🚨 错误概览|🚨 错误概览]]
- [[#🧩 根本原因|🧩 根本原因]]
- [[#🔬 三层诊断数据|🔬 三层诊断数据]]
- [[#🛠️ 修复过程|🛠️ 修复过程]]
- [[#🧰 技术栈与术语|🧰 技术栈与术语]]
- [[#🧱 排查中遇到的问题（踩坑）|🧱 排查中遇到的问题（踩坑）]]
- [[#✅ 验证结果|✅ 验证结果]]
- [[#🛡️ 后续建议|🛡️ 后续建议]]
- [[#🔗 相关笔记与附件|🔗 相关笔记与附件]]

## 🚨 错误概览

| 项目 | 现场信息 |
|---|---|
| 记录时间 | 2026-09-17 19:16 反馈，22:08–22:20 修复（Asia/Shanghai） |
| 现象 | 用户反馈「电脑被 VPN 劫持了，不开 VPN 无法正常使用国内网站」，怀疑系统被捆绑 |
| 复现条件 | <span style="color:#ff8c00">完全退出代理软件（小火箭 / Vortex / ClashR 全退）后，**浏览器**打不开国内网站，而微信、QQ、命令行等其他程序一切正常</span> |
| 故障载体 | **Firefox** 三个 profile 的 `user.js` 中强制写入的手动代理配置（Edge 干净、系统层干净） |
| 失效端口 | `127.0.0.1:4780`（小火箭 / ClashR 的 HTTP 代理端口，代理软件退出后无人监听） |
| 配置来源 | 2026-08-31 由「知识库报错修复」skill 写入（对应台账 N13 / [[15-校园网Firefox不走代理导致境外无法访问]]） |
| 最终状态 | <span style="color:#1e90ff">已修复（三个 profile 改回 `network.proxy.type=5`）并验证通过</span> |

<span style="color:#ff0000">关键证据：</span>

```text
# 走 4780（= 修复前 Firefox 的处境）→ 端口无人监听，连接被拒
curl -x http://127.0.0.1:4780 http://www.baidu.com
  → Failed to connect to www.baidu.com port 80 via 127.0.0.1 after 2024 ms

# 走 7897（Vortex 端口，同样已退出）
curl -x http://127.0.0.1:7897 http://www.baidu.com   → code=000

# 直连（= 修复后 Firefox 的处境）→ 完全正常
curl --noproxy "*" http://www.baidu.com
  → HTTP 200，0.134 s，出口 110.242.69.21

# 故障现场：Firefox 三个 profile 的 user.js 全文一致
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "127.0.0.1");
user_pref("network.proxy.http_port", 4780);
user_pref("network.proxy.ssl", "127.0.0.1");
user_pref("network.proxy.ssl_port", 4780);
user_pref("network.proxy.share_proxy_settings", true);
user_pref("network.proxy.no_proxies_on", "localhost, 127.0.0.1, ::1");
```

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 🔴 配置层（主根因） | <span style="color:#ff0000">Firefox 三个 profile 的 `user.js` 强制 `network.proxy.type=1`（手动代理）+ `127.0.0.1:4780`，且 `no_proxies_on` 只排除 localhost、**没有任何国内域名例外**</span> | 三个 profile 的 `user.js` 内容完全一致，注释写明「2026-08-31 由「知识库报错修复」skill 加入」 | 改为 `network.proxy.type=5`（跟随系统代理），并清理 `prefs.js` 残留 |
| 🟠 运行态（触发器） | <span style="color:#ff8c00">代理软件完全退出 → 4780 端口关闭 → Firefox 把全部请求（含国内）发给死端口</span> | 代理软件退出后 `Get-NetTCPConnection -LocalPort 4780` 无监听；`curl -x 4780` 报 `Could not connect to server` | 无需单独处理，根因修复后自动消失 |
| 🔵 设计缺陷（源头） | <span style="color:#1e90ff">2026-08-31 的修复只考虑「校园网下 Firefox 不走代理上不了外网」，**没有考虑「代理软件不在时」的兜底**，选了无分流能力的静态手动代理</span> | 15 号文档记载的修复方案原文 | 见「后续建议」，已回写提示到 15 号文档 |

> [!IMPORTANT] ⚠️ 关键澄清：这不是"劫持"，是"自伤"
> 排查确认**不存在**任何外部劫持：无 TUN 虚拟网卡（`Get-NetAdapter` 仅见 WLAN 2 / Radmin VPN / 以太网）、无 LSP 分层服务提供程序注入、`hosts` 文件干净（仅注释）、系统代理 `ProxyEnable=0`、WinHTTP 直连、git 无代理、DNS 已是国内快速 DNS。真正的"劫持者"是 <span style="color:#ff0000">知识库自己在 2026-08-31 写进 Firefox 的那 7 行配置</span>——它在"校园网 + 代理软件常开"的原始环境下是正确的，但环境一旦变成"代理软件不常开"，就立刻反噬。

## 🔬 三层诊断数据

### 1. 系统层（先排除"真劫持"）

- 用户级 / 机器级环境变量：`http_proxy`、`https_proxy`、`HTTP_PROXY`、`HTTPS_PROXY`、`all_proxy`、`ALL_PROXY` **全部为空**；仅残留 `no_proxy=localhost,127.0.0.1,::1`（代理工具写入标记，无副作用）。
- WinINet 系统代理：<span style="color:#1e90ff">`ProxyEnable=0`（未启用）</span>，`ProxyServer` 为空，`AutoConfigURL` 为空（无 PAC）。
- WinHTTP：`Direct access (no proxy server)`；`git config` 的 `http.proxy` / `https.proxy` 均为空。
- `hosts` 文件：<span style="color:#1e90ff">仅含注释，无任何生效条目</span>（未被劫持）。
- 网卡与路由：`WLAN 2`（MediaTek Wi-Fi 6E MT7922，ifIndex 13，Up）、`Radmin VPN`（ifIndex 18，Up）、以太网（断）；默认路由 <span style="color:#1e90ff">WLAN 2 → 192.168.0.1（metric 0，主）</span>、Radmin VPN → 26.0.0.1（metric 9256，备份）——**无 TUN 网卡绑架路由**。
- DNS：`WLAN 2 = 223.5.5.5 + 114.114.114.114`（国内快速 DNS，上次修复成果仍有效）；`nslookup www.baidu.com` 走 `public1.alidns.com`，解析正常。
- Winsock LSP：无第三方分层服务提供程序；网络过滤驱动仅系统自带（`WFPLWFS`、`ndproxy` 等）。
- IPv6：WLAN 2 仅有链路本地地址（`fe80::`），无全局 IPv6；Teredo 隧道虽显示 `qualified`，但 `curl -6` 访问国内站点立即失败（code=6）——<span style="color:#1e90ff">IPv6 不构成阻塞</span>。

### 2. 浏览器层（真正的故障点）

- **Edge**：`Preferences` 与 `Secure Preferences` 中 `proxy` 与 `dns_over_https` 均为空；23 个扩展中<span style="color:#1e90ff">无任何代理类扩展</span>（无 SwitchyOmega 之类）——**Edge 干净**。
- **Firefox**：三个 profile（`53w7d75e.default-release`、`u38z4dog.default`、`umie11gt.default-default`）的 `user.js` **全部**含有同一段手动代理配置：

```js
// 让 Firefox 走小火箭（Rocket/ClashR）代理 127.0.0.1:4780
// 原因：校园网直接封锁境外站点，Firefox 默认不走 Windows 系统代理（直连）会打不开外网。
// 2026-08-31 由「知识库报错修复」skill 加入。重启 Firefox 后生效。
user_pref("network.proxy.type", 1);          // 1 = 手动代理，所有流量强制走下面指定的代理
user_pref("network.proxy.http", "127.0.0.1");
user_pref("network.proxy.http_port", 4780);
user_pref("network.proxy.ssl", "127.0.0.1");
user_pref("network.proxy.ssl_port", 4780);
user_pref("network.proxy.share_proxy_settings", true);
user_pref("network.proxy.no_proxies_on", "localhost, 127.0.0.1, ::1");  // 仅排除本机，国内域名照样走代理
```

- 对应 `prefs.js` 中也写入了同一批值（`53w7d75e.default-release` 第 208–214 行），说明配置已实际生效。
- `user.js` 是 **Firefox 启动时强制覆盖**的配置文件——即使在浏览器界面里手动改回设置，下次启动仍会被它覆盖回来，这也是用户「怎么改都改不好」的原因。

### 3. 实测层（对照实验）

| 测试路径 | 命令 | 结果 |
|---|---|---|
| 走 `4780`（修复前 Firefox 的路径） | `curl -x http://127.0.0.1:4780 http://www.baidu.com` | ❌ `Could not connect to server`（2024 ms 后失败） |
| 走 `7897`（Vortex 端口） | `curl -x http://127.0.0.1:7897 http://www.baidu.com` | ❌ `code=000` |
| **直连**（修复后 Firefox 的路径） | `curl --noproxy "*" http://www.baidu.com` | ✅ <span style="color:#1e90ff">HTTP 200，0.134 s，110.242.69.21</span> |
| 直连 qq / taobao | `curl --noproxy "*" ...` | ✅ 302 / 0.119 s、200 / 0.463 s |

> [!NOTE] 💡 三条路径的对照结论
> <span style="color:#ff8c00">命令行直连国内一切正常</span>，唯一会失败的就是「强制走 4780」这条路径——而它恰好就是修复前 Firefox 的唯一路径。<span style="color:#1e90ff">根因定位到此闭合。</span>

## 🛠️ 修复过程

1. **备份原配置**（先备份后改动）：将三个 profile 的 `user.js` 与 `prefs.js` 备份到
   `总结好的大纲以及笔记/知识库FAQ/原始文件备份/Firefox代理配置备份-20260917/`
   （命名形如 `53w7d75e.default-release__user.js`，共 5 个文件；`u38z4dog.default` 无 `prefs.js`，属从未启动过的 profile）。
2. **确认 Firefox 未运行**：`Get-Process firefox` 为空——`prefs.js` 只在 Firefox 退出时写入，必须在关闭状态下修改，否则会被回写覆盖。
3. **修改三个 `user.js`**：把 `network.proxy.type` 由 `1` 改为 **`5`（使用系统代理设置，Firefox 默认值）**，删除指向 `127.0.0.1:4780` 的 `http` / `http_port` / `ssl` / `ssl_port` / `share_proxy_settings` 五行（`type=5` 时它们本就不生效，删掉更干净），并重写注释记录本次变更的来龙去脉。
4. **清理 `prefs.js` 残留**：`53w7d75e.default-release/prefs.js` 的 7 行手动代理配置替换为单行 `user_pref("network.proxy.type", 5);`，防止将来 `user.js` 被删除后旧值回潮。
5. **验证**：先用 Firefox 自身启动 headless 实例打开 `www.baidu.com`，检查其真实 TCP 连接；再用三条路径对照实验复核（见上表）。

> [!NOTE] 💡 关于另一个残留项的处理
> `umie11gt.default-default/prefs.js` 中还有一行 `network.proxy.allow_hijacking_localhost = true`。经判断这属于 **Firefox 隐私强化配置（arkenfox 类）** 的标准条目（与 `network.http.speculative-parallel-limit = 0` 同批出现），**与本次故障无关**、在 `type=5` 且系统代理关闭时不产生任何影响，故<span style="color:#1e90ff">保留未动</span>，避免破坏原有的隐私配置意图。

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| `user.js` | Firefox profile 目录下的一个**特制配置文件**，浏览器每次启动时都会读取它并**强制覆盖** `prefs.js` 中的同名设置。常用于部署固定策略；也意味着用界面改设置会被它顶回去 |
| `prefs.js` | Firefox 保存用户设置的正式文件，浏览器运行中改设置、退出时写入 |
| `network.proxy.type` | Firefox 的代理模式开关：**0** = 不使用代理（全直连）；**1** = 手动配置代理；**2** = 自动代理配置脚本（PAC）；**4** = 自动检测；**5** = 使用系统代理设置（**Firefox 默认值**） |
| `no_proxies_on` | 手动代理模式下的"例外列表"，列在这里的地址不走代理。原配置只排除了 `localhost`，所以国内域名照样全部走代理 |
| `127.0.0.1:4780` | 小火箭 / ClashR 在本机开的 HTTP 代理端口。软件运行时它转发流量；软件退出后**端口随之关闭**，再往里发请求就会"连接被拒" |
| `no_proxy` / `http_proxy` | 操作系统层面的环境变量，影响 curl / git / Python 等命令行程序（浏览器**不读**这些变量） |
| TUN / TAP | 虚拟网卡技术，在网络层接管全部流量（浏览器无感知）；本次排查确认**未启用** |
| LSP | Winsock 分层服务提供程序，一种可注入网络栈的旧式劫持手段；本次排查确认**无第三方注入** |
| PAC | 自动代理配置脚本，可按域名规则自动决定走不走代理——<span style="color:#1e90ff">这是静态手动代理做不到的</span> |
| HEADLESS 模式 | 浏览器不开窗口、在后台运行的模式，本案例用它来实测 Firefox 的真实网络连接 |

## 🧱 排查中遇到的问题（踩坑）

1. **<span style="color:#ff0000">现象与实测矛盾，差点走错方向。</span>** 用户说"不开 VPN 连国内网站都上不了"，但命令行 `curl` 直连国内一切正常（0.13 s）——说明系统层没问题，故障范围被压缩到"浏览器"。**教训：先问清"哪个程序、什么条件"，比一头扎进系统排查省一半时间。**
2. **<span style="color:#ff8c00">系统层指标全部正常，容易误判为"没问题"。</span>** 环境变量、系统代理、hosts、DNS、路由逐项检查全绿。若因此停手，就永远找不到真正藏在**浏览器 profile** 里的配置——**排查必须覆盖"系统层 → 应用层"两个面**。
3. **<span style="color:#ff8c00">Edge 干净、Firefox 有问题，两台浏览器要分别查。</span>** 一开始只扫了 Edge（`Preferences` 里 `proxy` 为空、23 个扩展无代理类），差点得出"浏览器都没问题"的错误结论；实际 Firefox 的问题藏在 `user.js` 而非界面设置里。
4. **`user.js` 优先级高于界面设置。** 该文件每次启动强制覆盖 `prefs.js`，所以在 Firefox 设置界面里改代理是**无效的**（下次启动被顶回）——必须直接改文件。
5. **<span style="color:#1e90ff">Firefox 启动后会"自动抹掉"与默认值相同的设置。</span>** 改完 `prefs.js` 后启动 Firefox 测试，发现 `network.proxy.type = 5` 这一行**从 `prefs.js` 里消失了**——这不是失败，恰恰是**成功**：`5` 是 Firefox 默认值，浏览器认为无需记录。判据：<span style="color:#1e90ff">`prefs.js` 中不再出现任何 `network.proxy` 手动代理行，即代表已回到默认直连状态</span>。
6. **Store 版 Firefox 不支持 `--headless --screenshot` 参数。** 用该命令做网页截图验证时，Firefox 进程启动了但截图始终不生成、任务不退出；改用<span style="color:#1e90ff">检查 Firefox 进程的真实 TCP 连接</span>（`Get-NetTCPConnection` 按 OwningProcess 过滤）来判断它连向哪里，反而更直接可靠。**教训：验证手段要选"能被观测到"的，而不是"看起来漂亮"的。**
7. **profile 活跃度难以直接判定。** `times.json` 记录的是**创建时间**而非最后使用时间，无法据此判断哪个 profile 在用；最终采用"<span style="color:#1e90ff">三个 profile 全部修正</span>"的策略，并用 headless 启动后哪个 `prefs.js` 被回写来反推实际在用的 profile（结果是 `53w7d75e.default-release`）。

## ✅ 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| Firefox 三个 profile 的 `user.js` | `network.proxy.type = 1` + `127.0.0.1:4780` | <span style="color:#1e90ff">`network.proxy.type = 5`（跟随系统代理）</span> |
| `53w7d75e.default-release/prefs.js` | 7 行手动代理配置 | <span style="color:#1e90ff">无任何手动代理残留</span> |
| Firefox 实际 TCP 连接 | （理论）全部发往 `127.0.0.1:4780` | <span style="color:#1e90ff">全部直连公网（如 151.101.65.91:443、34.54.185.247:443），**无一条连向本地代理端口**</span> |
| 走 `4780` 访问 baidu | — | ❌ 连接被拒（证明修复前的必然失败） |
| 直连访问 baidu | 命令行正常 | <span style="color:#1e90ff">HTTP 200，0.134 s</span> |

> [!NOTE] 💡 关于"重启 Firefox 后生效"
> `user.js` 与 `prefs.js` 都在 Firefox **启动时**读取，因此本次修改在**下次启动 Firefox 时自然生效**，无需额外操作（本次修复时 Firefox 处于关闭状态）。用户只需正常打开浏览器，国内网站即可访问。

## 🛡️ 后续建议

1. **访问外网时怎么办（重要）**：本次修复把 Firefox 改为"跟随系统代理"，因此——
   - 代理软件开启**并且打开了「系统代理」开关**时，Firefox 会自动走代理，可正常访问外网；
   - 代理软件退出时，Firefox 自动直连，国内网站不受影响。
   <span style="color:#ff8c00">若发现开着代理软件却仍上不了外网，请到代理软件里确认「系统代理 / 设置系统代理」开关是否打开</span>（这是 Firefox `type=5` 生效的前提）。
2. **不要再给浏览器配"静态手动代理"**：静态手动代理**没有任何分流能力**——要么全走、要么全不走，无法做到"国内直连 + 国外走代理"。若确需按域名分流，应使用 **PAC 脚本**或让代理软件开 **TUN 模式**（在网络层接管），而不是在浏览器里钉死一个端口。
3. **配置"指向本地端口"的代理时，必须考虑端口不在的情况**：本地代理端口（4780 / 7897 等）随代理软件启停而存在，任何"钉死端口"的配置在软件退出后都会变成死代理。本次正是踩了这个坑。
4. **同类识别（复用本文方法）**：<span style="color:#1e90ff">「只有浏览器打不开、其他程序正常」→ 优先查浏览器自身的代理配置</span>。Firefox 看三个 profile 的 `user.js` / `prefs.js` 中 `network.proxy.type`；Edge/Chrome 看 `Preferences` 中的代理设置与代理类扩展。配合"走代理端口 / 直连"两路对照法可快速闭环。
5. **本次修复的元教训**：<span style="color:#ff0000">修复方案必须考虑"环境变化后会不会变成新的故障源"</span>。2026-08-31 的修复在当时是有效的，但引入了"代理软件退出即全断"的隐患——这类"有时效性的修复"应当把前提条件和恢复方法一并写进文档（已在 [[15-校园网Firefox不走代理导致境外无法访问]] 中补充提示）。

## 🔗 相关笔记与附件

- [[00-报错统计台账]] — 台账 N15 条目
- [[15-校园网Firefox不走代理导致境外无法访问]] — **本配置的来源**（2026-08-31 写入），已补写副作用提示
- [[14-断开VPN后国内网络无法连接（代理残留环境变量与DNS）]] — 同类现象（关代理后国内连不上），根因在**系统层**（环境变量 + 网卡 DNS）
- [[05-Codex网络故障-青旅环境]] — 代理模式（direct / rule / global）相关故障档案
- [[06-国外网站访问慢但Codex正常]] — 代理分流问题的标准处置
- 配置备份（可随时还原）：`总结好的大纲以及笔记/知识库FAQ/原始文件备份/Firefox代理配置备份-20260917/`（含三个 profile 的 `user.js` 与 `prefs.js` 原件）
