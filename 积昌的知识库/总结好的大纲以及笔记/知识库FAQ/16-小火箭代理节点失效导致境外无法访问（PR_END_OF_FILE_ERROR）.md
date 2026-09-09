---
title: "小火箭（小火箭加速/ClashR）所选用代理节点失效导致境外无法访问（PR_END_OF_FILE_ERROR）"
type: "知识库 FAQ / 报错修复"
date: 2026-09-02
created: 2026-09-02
updated: 2026-09-02
environment: "🏫 校园局域网（宿舍）"
tags:
  - 校园网
  - PR_END_OF_FILE_ERROR
  - 小火箭
  - ClashR
  - 节点失效
  - 境外无法访问
  - 代理切换
  - Rocket
source: "2026-09-02 用户报告校园宿舍网下 Firefox 报 PR_END_OF_FILE_ERROR 无法访问境外，小火箭 VPN 亦失效，本机实测定位"
---

# 🌐 小火箭（小火箭加速/ClashR）所选用代理节点失效导致境外无法访问（PR_END_OF_FILE_ERROR）

> [!summary] 📊 报错统计速览（截至 2026-09-02）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（原始事件 1 次 + 复发 0 次）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 小火箭所选代理节点失效（美国节点 503）+ fork 无法 API 切换含 emoji 组名 | **1** | 16 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!info] 📍 适用环境：🏫 校园局域网（宿舍）
> 本文档记录**校园网**下「境外打不开，浏览器报 `PR_END_OF_FILE_ERROR`」且**代理隧道本身挂了**的场景。与 [[15-校园网Firefox不走代理导致境外无法访问]] 的区别在于：**15 是"应用不走系统代理"，本文是"代理隧道经由一个已失效（503）的节点被掐断"**。两者可叠加出现，先判代理由谁接管，再判节点健康度。

> [!SUMMARY] 📌 结论摘要
> 用户的代理客户端是 **小火箭加速**（`E:\小火箭\Rocket\小火箭加速.exe`，底层 ClashR fork + 火箭/huojian vmess 订阅），系统代理设 `127.0.0.1:4780`（`ProxyEnable=1`），Firefox 已由 [[15-校园网Firefox不走代理导致境外无法访问]] 改为走 4780（user.js `network.proxy.type=1`）。本次 **代理隧道 4780 连 google/youtube/github 全部 TSL 被掐断（curl 返回 HTTP 000 / exit 35）**，浏览器因此报 `PR_END_OF_FILE_ERROR`。逐层实测定位：**校园网直连封锁境外（google 超时）但放行国内 + cloudflare 正常**；而延迟测试显示所选节点 **`美国 01 AT&SANJOSE` 返回 503（节点已失效）**，`★自动选择|美国最优★` 亦 503，**美国节点全线挂**；**香港/台湾节点正常**（387~460ms）。**根因 = 代理组 `🔰国外流量` 当前选中已失效的美国节点**。修复：因 ClashR fork 无法通过 API `PUT /proxies` 切换**含 emoji（🔰）组名**的组（恒定 400 `Body invalid`，ASCII 组名则正常），改走「清空 ClashR `.cache` 持久化 + 重启小火箭加速」让组回落配置默认首项 `★自动选择|香港最优★`，外网随即恢复。

## 🧭 快速索引

- 📌 [[#📌 报错概况|报错概况]]
- 🔍 [[#🔍 根因分析|根因分析]]
- 📊 [[#📊 诊断数据|诊断数据]]
- 🔧 [[#🔧 修复过程|修复过程]]
- ⚠️ [[#⚠️ 关键认知|关键认知]]
- 💡 [[#💡 使用建议与遗留事项|使用建议与遗留事项]]

## 📌 报错概况

- **现象**：校园宿舍 WiFi 下，浏览器（本机主浏览器 Firefox）**打不开境外站**，报 `PR_END_OF_FILE_ERROR`（NSPR 的"连接被对端意外终止"错误）；用户同时反馈"小火箭的 VPN 也不行"。
- **报错原文**：`PR_END_OF_FILE_ERROR`（Firefox 报错页：`由于不能验证所收到的数据是否可信，无法显示您想要查看的页面`，错误代码 `PR_END_OF_FILE_ERROR`）。
- **关键澄清**：该错误≠ 普通超时/转圈，也不是"连不上"，而是**连接建立后、TLS 握手阶段被掐断**（对端 EOF）。这正是"客户端连上了本地代理，但本地代理连上游（坏节点）时被中断"的典型表现。

## 🔍 根因分析

### 三层根因（环境 + 工具/代理 + 工具/端口三层叠加）

| 层 | 根因 |
|---|---|
| **环境层** | 校园网在**防火墙层面封锁境外域名**（GFW 式过滤，实测直连 `google.com` 10s 超时/000 被拦），但放行国内（`baidu/qq` 200）与 `cloudflare.com`（200）。因此境外流量**必须走代理**。 |
| **工具层（代理隧道）** | **代理所选节点已失效**：`🔰国外流量` 组当前选中 `美国 01 AT&SANJOSE`，延迟测试返回 **503（服务器不可用，即节点死）**；`★自动选择|美国最优★` 亦 503，**美国节点全线宕**。ClashR 连该坏节点建隧道时被中断 → 本地代理层返回 EOF → 浏览器报 `PR_END_OF_FILE_ERROR`。`香港 01 HKIX`(387ms) / `台湾 01`(433ms) / `★自动选择|香港最优★`(460ms) 均正常。 |
| **工具层（切换机制）** | ClashR（`clashr-windows-amd64`，小火箭加速的内核）**无法通过 REST API 切换含 emoji 组名的组**：`PUT /proxies/{组名}` 对含 `🔰` 的组名恒定返回 **400 `{"message":"Body invalid"}`**（ASCII 组名如 `Others`/`Domestic` 则正常切换）。此 fork bug 使"仅 API 切节点"这条路走不通，被迫采用「清理 `.cache` 持久化 + 重启内核」的方案。 |

**一句话**：校园网只放行国内、封锁境外；境外流量又恰好落在小火箭里**已失效的美国节点**上——代理隧道经由坏节点被中断，浏览器收到 EOF，表现为 `PR_END_OF_FILE_ERROR`。

## 📊 诊断数据

| 层级 | 检查项 | 结果 |
|---|---|---|
| 环境层 | 直连国内 `baidu.com` / `qq.com` | **200 / 501**（放行） |
| 环境层 | 直连 `cloudflare.com` | **200**（放行，与 [[15-校园网Firefox不走代理导致境外无法访问]] 结论一致） |
| 环境层 | 直连境外 `google.com` | **10s 超时 / 000 被拦**（封锁） |
| 工具层 | 系统代理注册表 | `ProxyServer=127.0.0.1:4780`，`ProxyEnable=1` ✅ |
| 工具层 | 小火箭内核 | `clashr-windows-amd64` 运行中，监听 **4780(HTTP)/4781(SOCKS)/4788(控制器)** ✅ |
| 工具层 | 走代理 `127.0.0.1:4780` | 修复前：`google/youtube/github` **全部 HTTP 000**（TLS 被掐断，exit 35）❌ |
| 工具层 | 内核控制器 API | `127.0.0.1:4788`（`/version` 有响应；rocket.yaml 里写的 `0.0.0.0:9090` 与实际不符，实际监听 4788 = config.yaml 的 controller） |
| 工具层 | 代理组拓扑 | `MATCH,Others` → `Others`(`Proxy`) → `Proxy`(`🔰国外流量`) → 选中节点 |
| 工具层 | 延迟实测（`http://www.gstatic.com/generate_204`） | `美国 01 AT&SANJOSE` **503** ❌；`★自动选择|美国最优★` **503** ❌；`★自动选择|香港最优★` **460ms** ✅；`香港 01 HKIX` **387ms** ✅；`台湾 01 中華電信` **433ms** ✅ |
| 工具层 | API 切换 emoji 组 | `PUT /proxies/🔰国外流量` → **400 `{"message":"Body invalid"}`**（任何目标都 400，含当前值）；`PUT /proxies/Domestic`→`DIRECT`、`PUT Others`→`Proxy` 均 **OK** |
| 工具层 | 选择持久化 | `.cache`（ClashR gob 缓存）存 `🔰国外流量: 美国 01 AT&SANJOSE`；`clashy-configs/configs.json` 仅存 `currentSelector: "🔰国外流量"`、`currentProxy: ""`（**不**存具体节点） |
| 验证 | 走代理 `127.0.0.1:4780` 修复后 | `google.com` **302** ✅ / `youtube.com` **200** ✅ / `github.com` **200** ✅ / `generate_204` **204** ✅ |
| 验证 | Firefox 代理配置 | 3 个 profile 的 `user.js` 均 `network.proxy.type=1` + `127.0.0.1:4780` ✅（走代理链路完好） |

## 🔧 修复过程

1. **定位**：系统代理正确（4780）、ClashR 进程健康、走代理却境外全 000 → 逐节点延迟实测 → 发现**所选美国节点 503，节点失效**。
2. **尝试 API 切换**：`PUT /proxies/🔰国外流量` → 恒定 400 `Body invalid`（对照实验确认是**含 emoji 组名**在 fork 里无法切，与目标节点无关）。
3. **尝试配置重载**：`PUT /configs?force=true`（路径=`rocket.yaml`）→ 204 但组选择不变（ClashR 重载时保留内存中 select 组 `now`）。
4. **找到持久化源**：ClashR 的选择持久化在 `.cache`（gob 编码），`.cache` 存着 `🔰国外流量: 美国 01`。
5. **落地修复**：
   1. 先备份 `rocket.yaml` → `总结好的大纲以及笔记/知识库FAQ/原始文件备份/`（规范备份）；
   2. 用 `Stop-Process` 停止小火箭内核 `clashr-windows-amd64`（PID 3732；注意 bash 里 `taskkill /f /pid` 会被 `F:/` 路径转换坑，改用 PowerShell）；小火箭 GUI（`小火箭加速.exe`，4 个 Electron 进程）**不会自动拉起内核**；
   3. 移走 `.cache`（防下次读到坏节点选择）；
   4. 用原启动命令（`-d clash-configs` + `-signature`）拉起内核 → 默认加载 `config.yaml`（模板、无代理组）→ 用 `PUT /configs?force=true` 推送 `rocket.yaml`（带全部代理组）；此时 `.cache` 触发过一次被 GUI 重建为旧值 → 再次清空 `.cache`；
   5. 干净重启整机小火箭加速（停止所有 `小火箭加速.exe` + 内核 + 清空 `.cache`）→ 重启 `E:\小火箭\Rocket\小火箭加速.exe` → 内核重新监听 4780/4788，`🔰国外流量` **回落配置默认首项 `★自动选择|香港最优★`**。
6. **验证**：走代理 `127.0.0.1:4780` 实测 google 302 / youtube 200 / github 200 / generate_204 204；Firefox user.js 未动，仍指向 4780。

> [!warning] ⚠️ 关键认知
> **① 节点失效 ≠ 隧道断了**：ClashR 进程在跑、端口在听，但不代表所选节点可用——务必做**逐节点延迟实测**（`GET /proxies/{节点}/delay`）。返回 503 即节点死；返回 5 选 1 的延迟数字才是可用。**"隧道能连上本地代理"与"能连境外"是两回事。**
> **② ClashR fork 的 emoji 组名切换 bug**：`PUT /proxies/{组}` 对含非 ASCII（如 `🔰国外流量`）的组名恒定返回 400 `Body invalid`，而 ASCII 组名（`Others`/`Domestic`/`Proxy`）正常。**这是 fork 的路由/解析 bug**，误导性错误文案，别被"Body invalid"骗去检查请求体。
> **③ ClashR 重载（`PUT /configs`）不会重置 select 组选择**：它保留内存中组的 `now`。真正清空选择必须**删 `.cache` 持久化 + 重启内核**。
> **④ 选择持久化藏在 `.cache`**：ClashR（含小火箭加速内核）把各 select 组的当前选择写进 `clash-configs/.cache`（gob 二进制，非 `config.yaml`，也不是 Rocket 的 `configs.json`）。`configs.json` 的 `currentProxy` 通常是空的——**别在那里找节点**。
> **⑤ 重启内核要用 PowerShell 别用 bash `taskkill`**：bash 下 `/f` `/pid` 会被 MSYS 路径转换坑（报"无效参数 F:/"）。用 `Stop-Process -Id <PID> -Force`。
> **⑥ 小火箭 GUI 不会自动重启内核**：杀掉 `clashr-windows-amd64` 后，`小火箭加速.exe` **不**会自动拉起；需手动用原命令（含 `-signature`）拉起，或整机重启小火箭加速。
> **⑦ 订阅商美国节点全挂时**：`★自动选择|美国最优★` 与 `美国 01` 都 503，说明是**机场美国线路整体故障**，不是单个节点问题；此时 OpenAI/Codex 走香港能否过 Cloudflare 风控是另说，但普通境外浏览用香港节点即可。

## 💡 使用建议与遗留事项

- **即刻生效**：重启 Firefox（`Ctrl+Shift+Q` 完全退出后重开）以清掉失败连接，境外站应可打开。若仍有个别报错，强刷（`Ctrl+F5`）或重开标签页即可。
- **遗留**：① 若你**需要 OpenAI/Codex**（对出口 IP 风控敏感，见 [[04-Codex桌面端反复重新连接（公司环境）]] 台账 N12），香港节点不一定过 Cloudflare 人机验证——当前美国全挂，需等机场修复美国线路，或临时用台湾/日本节点并实测 `chatgpt.com` 是否回 challenge；② 若**其它不走 4780 的应用**也连不上境外，说明它们没走小火箭——需开小火箭 **TUN 模式**一次性接管，或逐个配已写代理；③ 若再次打不开境外，先查 `🔰国外流量` 当前选中节点 delay，再按本文流程处理。
- **预防**：建议把小火箭的子组 `🔰国外流量` 里**顺手把已知常挂的美国节点换到后位**，或改用 `★自动选择|香港最优★` 这类会自动测速的节点；避免手动钉死单一易挂节点（尤其 OpenAI 分流用美国节点时）。

## 🔗 相关笔记

- [[15-校园网Firefox不走代理导致境外无法访问]] · 校园网 + Firefox 不走系统代理（本文与其可叠加）
- [[04-Codex桌面端反复重新连接（公司环境）]] · 节点延迟/出口 IP 风控/OpenAI 分流（台账 N6、N12）
- [[06-国外网站访问慢但Codex正常]] · 代理分流（快节点）
- [[10-mihomo IPv6出站导致ChatGPT被CF风控]] · CF 风控
- [[00-报错统计台账]] · 全局报错统计
