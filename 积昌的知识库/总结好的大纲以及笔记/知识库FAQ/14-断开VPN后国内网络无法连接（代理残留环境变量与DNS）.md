---
title: "断开 VPN 后国内网络无法连接：代理残留环境变量与 DNS"
type: "知识库 FAQ / 报错修复"
date: 2026-08-29
created: 2026-08-29
updated: 2026-08-29
environment: "🏠 本地（Windows 11 / 无线网卡 WLAN 2）"
tags:
  - VPN
  - 代理
  - 环境变量
  - http_proxy
  - DNS
  - 8.8.8.8
  - 223.5.5.5
  - Rocket
  - Vortex
  - Clash
  - 网络故障
source: "2026-08-29 用户现场反馈：「断开 VPN 后无法正常连接国内网络」"
---

# 🔌 断开 VPN 后国内网络无法连接（代理残留环境变量与 DNS）

> [!summary] 📊 报错统计速览（截至 2026-08-29）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错/修复事件</span>**（2026-08-29 原始事件 1 次，暂无复发）。主根因为 **「代理工具残留的 http_proxy 环境变量 + WLAN 2 DNS 8.8.8.8」**（台账 N11，累计 1 次）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🟠 代理残留 `http_proxy`/`https_proxy` 环境变量（指向失效节点） | **1** | 14 |
> | 🟡 WLAN 2 适配器 DNS 残留 `8.8.8.8` | **1** | 14 |
> | 🟠 代理进程仍在运行但上游节点失效（叠加项） | **1** | 14 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!info] 📍 适用环境：🏠 本地 Windows 11
> 本文档记录**断开/关闭代理（VPN）后国内网络无法连接**的排查。它不同于 [[04-Codex桌面端反复重新连接（公司环境）]] / [[05-Codex网络故障-青旅环境]] 关注的「外网（Codex/OpenAI）故障」——本文是**代理工具在关闭后仍残留系统设置，反过来劫持国内访问**。外网慢 / 代理分流问题见 [[06-国外网站访问慢但Codex正常]]。

> [!SUMMARY] 📌 结论摘要
> 「电脑被 VPN 捆绑、断开后国内连不上」<span style="color:#ff0000">并非网络流量被隧道绑架</span>，而是代理工具关闭后**残留的两处系统设置**在作祟：<span style="color:#ff8c00">① 用户级持久化环境变量 `http_proxy`/`https_proxy` 指向已失效的 `127.0.0.1:7897`</span>，让 curl / git / Python 等所有读取环境变量的程序强行走死代理（上游节点挂，5 秒后返回 502）；<span style="color:#ff8c00">② WLAN 2 适配器 DNS 被写成 `8.8.8.8`</span>，国内解析偏慢、偶发不稳（实测 0.78s 对 223.5.5.5 的 0.12s）。清理环境变量 + 改回国内 DNS 后，直连国内 <span style="color:#1e90ff">baidu HTTP 200 仅 0.12s</span>，问题解决。

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
| 记录时间 | 2026-08-29 17:49（Asia/Shanghai） |
| 现象 | 用户反馈「断开 VPN 后，国内网络无法正常连接」，怀疑电脑被 VPN 捆绑 |
| 代理 | 小火箭（Rocket）+ `com.vortex.helper.exe`（Vortex）+ `clashr-windows-amd64.exe` |
| 代理监听 | `127.0.0.1:7897`（Vortex）、`4780`/`4781`（clashr）、`53`（Vortex DNS 劫持） |
| 直接证据 | `http_proxy=http://127.0.0.1:7897`（用户级持久化）；WLAN 2 DNS = `8.8.8.8`；走代理 curl 返回 HTTP 502 / 出口 `127.0.0.1` |
| 最终状态 | <span style="color:#1e90ff">已修复（清环境变量 + DNS 改回 223.5.5.5）并验证通过</span> |

<span style="color:#ff0000">关键证据：</span>

```text
# 走代理（读取 http_proxy 环境变量）→ 代理进程活着但节点失效
curl http://www.baidu.com        → HTTP 502, 出口IP=127.0.0.1   (耗时 5.0s)

# 直连（绕过代理）→ 正常
curl --noproxy "*" http://www.baidu.com → HTTP 200, 出口IP=103.235.46.102 (耗时 0.57s)

# WLAN 2 适配器 DNS 残留
Get-DnsClientServerAddress -InterfaceAlias "WLAN 2"  → 8.8.8.8, 114.114.114.114
```

## 🧩 根本原因

| 层级 | 根因 | 证据 | 处置 |
|---|---|---|---|
| 环境层 | <span style="color:#ff0000">代理工具关闭后残留**用户级持久化环境变量** `http_proxy`/`https_proxy` = `127.0.0.1:7897`</span> | `[Environment]::GetEnvironmentVariable("http_proxy","User")` 返回该值；代理节点失效后所有读环境变量的程序 5 秒后 502 | 用 `SetEnvironmentVariable(..., $null, "User")` 清空，同步清空当前会话 |
| 网络层 | <span style="color:#ff8c00">WLAN 2 适配器 DNS 被写成 `8.8.8.8`（Google）</span> | 代理写入的静态 DNS；8.8.8.8 国内解析慢/不稳（0.78s） | `netsh` 改回 `223.5.5.5` 主 + `114.114.114.114` 备 |
| 配置层 | <span style="color:#ff8c00">代理进程仍在运行但上游节点已失效</span> | `7897`/`53` 仍由 Vortex 监听；走代理 502 | 说明项，未删除代理本体（保留外网访问能力） |

> [!IMPORTANT] ⚠️ 关键澄清：没有 TUN 劫持
> 排查确认**不存在** TUN/TAP 虚拟网卡绑架路由：`Get-NetAdapter` 仅见无线网卡、Radmin VPN、蓝牙、以太网（无代理虚拟网卡）；`Get-NetRoute -DestinationPrefix "0.0.0.0/0"` 显示 <span style="color:#1e90ff">WLAN 2（metric 0）才是主路由</span>，Radmin VPN（metric 9256）只是备份。系统代理 `ProxyEnable=0`（已禁用）、WinHTTP 直连。因此**浏览器（走系统直连）其实一直能访问国内**，真正「断」的是读取 `http_proxy` 环境变量的程序——这正是「捆绑」的体现。

## 🔬 三层诊断数据

### 1. 文件与配置层

- 用户级持久化环境变量：`http_proxy` / `https_proxy` / `HTTP_PROXY` / `HTTPS_PROXY` 均为 `http://127.0.0.1:7897`；`all_proxy` 为空；`no_proxy=localhost,127.0.0.1,::1`。
- 检查 `.curlrc`（`C:\Users\asus\.curlrc`）：**不存在**。
- Git 全局/系统代理：`git config --global --get http.proxy` 与 `--get https.proxy`、`git config --system --get http.proxy` 均**为空**。
- WinINet 系统代理：`ProxyEnable=0`（禁用），`ProxyServer=127.0.0.1:4780`（残留值但未启用）。

### 2. 环境与网络层

- `Get-NetAdapter`：`WLAN 2`（MediaTek Wi-Fi 6E MT7922，ifIndex 13，Up）、`Radmin VPN`（Famatech，ifIndex 18，Up）、`蓝牙网络连接`（断）、`以太网`（断）——**无 TUN**。
- `Get-NetRoute "0.0.0.0/0"`：WLAN 2 → `192.168.0.1`（metric 0，主）；Radmin VPN → `26.0.0.1`（metric 9256，备份）。
- `Get-DnsClientServerAddress -InterfaceAlias "WLAN 2"`：<span style="color:#ff8c00">`8.8.8.8` + `114.114.114.114`</span>（静态，代理残留）。
- `Get-NetTCPConnection -State Listen`：`7897`（PID 16920）、`53`（PID 16920）、`4780`/`4781`（PID 6668）均在监听；进程为 `com.vortex.helper.exe` 与 `clashr-windows-amd64.exe`，节点失效。

### 3. 工具与会话层

- 走代理（读环境变量）`curl http://www.baidu.com` → <span style="color:#ff0000">HTTP 502，出口 `127.0.0.1`，耗时 5.0s</span>。
- 强制直连 `curl --noproxy "*" http://www.baidu.com` → <span style="color:#1e90ff">HTTP 200，出口 `103.235.46.102`，耗时 0.57s</span>。
- 剥离代理环境变量的子进程 `curl http://www.qq.com` → <span style="color:#1e90ff">HTTP 302，出口 `221.198.70.47`，耗时 0.31s</span>。
- 结论：<span style="color:#1e90ff">直连国内完全可用，唯一阻塞点就是残留的 `http_proxy` 环境变量</span>。

## 🛠️ 修复过程

1. **复现并锁定主根因**：用 `curl` 分别走代理 / `--noproxy` / 剥离 env 三路对照，确认「读环境变量 → 502」是唯一断点。
2. **清空用户级持久化代理环境变量**：
   ```powershell
   [Environment]::SetEnvironmentVariable("http_proxy",  $null, "User")
   [Environment]::SetEnvironmentVariable("https_proxy", $null, "User")
   [Environment]::SetEnvironmentVariable("HTTP_PROXY",   $null, "User")
   [Environment]::SetEnvironmentVariable("HTTPS_PROXY",  $null, "User")
   [Environment]::SetEnvironmentVariable("all_proxy",    $null, "User")
   [Environment]::SetEnvironmentVariable("ALL_PROXY",    $null, "User")
   # 同步清空当前会话（继承父进程旧值的情况）
   $env:http_proxy=$null; $env:https_proxy=$null; $env:HTTP_PROXY=$null; $env:HTTPS_PROXY=$null
   ```
   > ⚠️ 本会话（Claude）启动时已继承旧环境变量，需剥离后另起子进程验证；用户**新开的进程**读的是已清空的 User 级值，直接生效。
3. **改 WLAN 2 DNS 为国内快速 DNS**（需管理员；netsh 命令写入 `_fix_dns.bat`）：
   ```bat
   netsh interface ipv4 set dnsservers "WLAN 2" static 223.5.5.5 primary
   netsh interface ipv4 add dnsservers "WLAN 2" 114.114.114.114 index=2
   ipconfig /flushdns
   ```
4. **提权执行**：会话为 Medium 完整性级别，无法直接改 DNS；最终用 `Start-Process -FilePath "F:\...\_fix_dns.bat" -Verb RunAs -Wait` 提权运行成功（UAC 弹窗后 netsh 生效）。
5. **验证**：`Get-DnsClientServerAddress` + `netsh interface ipv4 show dnsservers "WLAN 2"` 确认 DNS 已变更为 `223.5.5.5` + `114.114.114.114`；`nslookup www.baidu.com` 走 `public1.alidns.com`；直连 baidu HTTP 200 仅 0.12s。
6. **清理**：删除临时 `_fix_dns.bat` 与日志。

> [!NOTE] 💡 期间先尝试了 `Set-DnsClientServerAddress`、`netsh`、`schtasks /rl HIGHEST`、`Start-Process -RunAs` 四种提权路径（详见踩坑节），最终只有 `Start-Process -RunAs` + 修正编码后的 bat 成功。

## 🧰 技术栈与术语

| 术语 | 通俗解释 |
|---|---|
| `http_proxy`/`https_proxy` | 环境变量，告诉 curl / git / Python 等把 HTTP/HTTPS 流量转发给哪个代理。一旦指向失效节点，这些程序全部连不上 |
| 用户级 vs 当前会话环境变量 | User 级是持久化的（写入注册表，重启/新进程有效）；当前会话值是本次进程继承的 |
| `127.0.0.1:7897` | Vortex helper 的本地代理端口；节点失效时返回 502 Bad Gateway |
| `8.8.8.8` | Google 公共 DNS，国内访问偏慢、响应偶发被干扰；`223.5.5.5`（阿里）/`114.114.114.114`（电信）为国内快速 DNS |
| `ProxyEnable=0` | WinINet 系统代理开关；=0 表示浏览器不使用系统代理（直连） |
| TUN / TAP | 虚拟网卡技术，可接管全部流量；本案例**未启用** |
| `netsh interface ipv4 set dnsservers` | 命令行设置网卡静态 DNS（需管理员权限） |
| Radmin VPN | 一个虚拟局域网工具，本案例中仅作备份路由（metric 9256），非主路由 |

## 🧱 排查中遇到的问题（踩坑）

> 本节是本案例**最值得沉淀**的部分：修改系统网络设置时，编码/权限/路径三类坑都踩到了。

1. **<span style="color:#ff0000">用 Write 工具写中文 .bat → UTF-8 编码被 cmd 按 GBK 读取 → 整份脚本乱码解析失败。</span>**
   现象：`netsh ... set dnsservers` 被拆成 `nsservers`、`ipconfig /flushdns` 被拆成 `flushdns` 等「xxx 不是内部或外部命令」，脚本根本没跑到设置 DNS 的步骤。
   修复：改为 <span style="color:#1e90ff">PowerShell `[System.IO.File]::WriteAllText($path, $text, [System.Text.Encoding]::ASCII)`</span> 用 **纯 ASCII 内容 + 显式 CRLF** 重写（`.bat` 内容避免中文），绕开 cmd 默认代码页的编码坑。
2. **<span style="color:#ff8c00">`.bat` 内重定向日志到 `C:\` 根目录被 Medium 权限拒绝（Access denied）</span>**。
   修复：日志改写到可写路径 `C:\Users\asus\fix_dns.log`（非提权、提权都能写，且无中文路径）。
3. **<span style="color:#ff8c00">`schtasks /create` 在 Git-Bash（MSYS2）里被路径转换破坏</span>**：`/create` 被转成 `D:/download/Git/create`；改到 PowerShell 里又被「Access is denied」（Medium 无法注册提权任务，连 `/ru SYSTEM` 也不行）。
4. **`Set-DnsClientServerAddress` 报 CIM PermissionDenied；`netsh` 报「请求的操作需要提升」**——当前会话是 Medium 完整性级别，改 DNS 必须管理员。
5. **右键「以管理员身份运行」未真正提权**：跑了 bat 但日志仍显示「需要提升」。最终用 `Start-Process -Verb RunAs -Wait` 提权成功。
6. **`Start-Process -Verb RunAs` 直接跑 `.bat` 有时不可靠**（先跑了一次无日志）；改用提权后 `cmd /c bat` 的效果仍不确定，最终在 bat 修正编码后直接 `Start-Process -Verb RunAs` 才一次成功。

## ✅ 验证结果

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| 用户级 `http_proxy`/`https_proxy` | `http://127.0.0.1:7897` | <span style="color:#1e90ff">空（已清除）</span> |
| WLAN 2 DNS | `8.8.8.8` + `114.114.114.114` | <span style="color:#1e90ff">`223.5.5.5` + `114.114.114.114`</span> |
| 默认 DNS 解析（nslookup baidu） | `dns.google`（8.8.8.8），0.78s | <span style="color:#1e90ff">`public1.alidns.com`（223.5.5.5）</span> |
| 直连国内（curl，剥离代理 env） | 走代理 502 | <span style="color:#1e90ff">HTTP 200，仅 0.12s</span> |

## 🛡️ 后续建议

1. **彻底解绑（避免复发）**：若希望代理只在需要外网时接管（而非一直全局劫持），请在代理软件（Rocket / Vortex）设置里<strong>关闭「设置系统代理 / 设置环境变量」选项</strong>。否则下次启动代理软件时，它可能<strong>重新写入</strong> `http_proxy` 环境变量——本次修复在代理软件重启前有效。
2. **外网访问**：当前代理节点已失效（实测走代理 502）。访问国外网站前需在代理软件里**换一个可用节点**。
3. **DNS 已归位**：WLAN 2 已用国内快速 DNS（223.5.5.5 + 114.114.114.114），国内访问稳定高效。
4. **同类识别**：<span style="color:#ff8c00">「断开 VPN 后国内连不上」优先怀疑代理残留的环境变量 + 适配器 DNS 8.8.8.8</span>，可复用本文的「走代理 / `--noproxy` / 剥离 env」三路对照法快速定位。

## 🔗 相关笔记与附件

- [[00-报错统计台账]] — 台账 N11 条目
- [[06-国外网站访问慢但Codex正常]] — 代理分流问题（外网慢，但 Codex 正常），与本文「国内连不上」方向相反
- [[04-Codex桌面端反复重新连接（公司环境）]] / [[05-Codex网络故障-青旅环境]] — 外网（Codex/OpenAI）故障档案
- [[08-Edge浏览器Secure DNS导致ChatGPT解析慢]] — 另一处 DNS 相关（Edge 安全 DNS）
- 临时脚本 `_fix_dns.bat` 与日志 `C:\Users\asus\fix_dns.log`：**修复完成后已删除**，本次未留原始文件备份（未改动任何源文件，仅清除环境变量与改 DNS，无原始数据损失）。
