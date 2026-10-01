---
title: "Playwright 页面等待字体测量超时（esm.sh 动态导入卡住）"
type: "知识库 FAQ / 报错记录"
date: 2026-09-29
created: 2026-09-29
updated: 2026-09-29
tags:
  - 报错
  - 知识库FAQ
  - Playwright
  - Excalidraw
  - 字体测量
  - 网络
  - CDN
source: "Excalidraw 图表 skill 的字宽测量脚本 .claude/skills/Excalidraw图表/references/_measure_chars.py；触发任务：放大英语旁批笔记（第3篇短文·举重奶奶的逆龄人生）的正文行间距"
---

# ⏱️ Playwright 页面等待字体测量超时（esm.sh 动态导入卡住）

> [!summary] 📊 报错统计速览（截至 2026-09-29）
> 🔥 **本文档共记录 <span style="color:#e74c3c">3 次报错事件</span>**（2026-09-29 首发 1 次 + 同日复发 2 次）。根因为 **「测量/渲染页要在浏览器里从境外 CDN（esm.sh）动态 import 数 MB 的 `@excalidraw/excalidraw` 包，境外线路抽风时 120 秒上限内没加载完，`window.__ready`（测量页）/ `window.__moduleReady`（渲染页）始终不置位」**，属 <span style="color:#2980b9">**网络 / CDN 层**</span>问题（既不是文件问题，也不是本机环境缺依赖）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🧾 Playwright 页面等待超时（esm.sh 动态导入卡住） | **3** | 26（测量脚本 1 次 + 渲染脚本 2 次） |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

## 🧭 快速索引

- 🧾 [[#错误信息|错误信息]]
- ⚠️ [[#现象描述|现象描述]]
- 🔍 [[#根本原因（三层诊断）|根本原因（三层诊断）]]
- 📊 [[#诊断数据|诊断数据]]
- 🛠️ [[#修复过程|修复过程]]
- 📽️ [[#技术栈与涉及工具|技术栈与涉及工具]]
- 🕳️ [[#遇到的问题与坑|遇到的问题与坑]]
- ✅ [[#验证结果|验证结果]]
- 📌 [[#使用建议与遗留事项|使用建议与遗留事项]]

## 错误信息

```
playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 120000ms exceeded.
```

> **出现时间**：2026-09-29（放大英语旁批笔记正文行间距任务执行中）
> **来源**：知识库技能脚本 <span style="color:#e67e22">**`.claude/skills/Excalidraw图表/references/_measure_chars.py`**</span>（Excalidraw 图表 skill 的**真实字体字宽测量**脚本）。
> **触发场景**：为英语旁批笔记调整正文行间距，需要重跑「<span style="color:#2980b9">两遍测量工作流（two-pass metrics）</span>」——**第一遍**先由生成器产出 `_chars.json`（待测字符清单），再交给 `_measure_chars.py` 用**真机字体**逐个量宽，产出的 `_charmetrics.json` 供**第二遍**排版精确计算行宽。报错就发生在**第一遍的字宽测量**里。

## 现象描述

任务此前一切正常：字宽测量脚本能被拉起、Playwright 能启动、Chromium 也能开；直到脚本执行到**"等页面把 Excalidraw 模块加载好"**这一步，**原地卡满 120 秒**，然后抛超时退出（后台任务 `bxeomsl9j`，退出码 1）。

关键特征——<span style="color:#2980b9">**报错发生在"下载"而不是"渲染"**</span>。脚本启动的测量页里有一句：

```js
const m = await import("https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle");
window.__ready = true;          // ← 只有 import 成功才置位
```

而 Python 侧在 `page.goto()` 之后紧接着等这个标志位：

```python
page.wait_for_function("window.__ready === true", timeout=120000)
```

于是逻辑链变成：<span style="color:#e74c3c">**境外 CDN 没在 120 秒内把包下完 → `window.__ready` 始终为 undefined → 等待函数超时 → 抛 TimeoutError**</span>。

- ✅ **文件层没问题**：待测字符清单是几百字节的小 JSON，格式合法；
- ✅ **环境层没问题**：Playwright Python 包与 Chromium 浏览器二进制**都已装好**（这一层的问题早在 [[20-Playwright Chromium未安装]] 里修掉了），本次**没有**报 `Chromium not installed`；
- ❌ **网络层出问题**：页面依赖的**境外 CDN 这一次抽风**，多兆字节的模块没能在上限内下载完。

> 💡 **<span style="color:#2980b9">认知：</span>** **"脚本能启动" ≠ "脚本能跑完"**。这个脚本的外部依赖有两段——<span style="color:#e67e22">**① 本机能力**（Playwright + Chromium，装一次长期有效）+ **② 外部网络**（每次运行都要从 `esm.sh` 现场拉 `@excalidraw/excalidraw`，几 MB）</span>。①已在 09-14 修好，本次卡的是②。**同一个脚本，两种完全不同的失败模式，不能混为一谈。**

## 根本原因（三层诊断）

按报错修复 skill 的三层法逐层排查，根因落在**第③层网络层**：

### ① 文件层（报错对象本身）——正常 ✅

- 输入 `_chars.json` 结构为 `{"combos":[{"fs":42,"fam":2},…],"chars":["a","字",…]}`，仅描述"要测哪些字号×字体组合、哪些字符"，体积极小、可正常 `json.loads`；
- 脚本自带的 `ast.parse`/输入校验均通过，与"内容对不对"无关。

### ② 环境层（机器依赖）——正常 ✅

- Playwright 依赖与浏览器二进制齐备（`ms-playwright\chromium_headless_shell-…` 已在位，见 [[20-Playwright Chromium未安装]]）；
- `uv run` 能拉起 Python 环境、`import playwright` 正常；
- 本次报错文案是 `Page.wait_for_function: Timeout`，**不是** `Executable doesn't exist` / `Chromium not installed`——**从报错文案即可判定"环境层这次没问题"**。

### ③ 网络 / CDN 层（外部依赖）——**根因所在** ❌

- 测量页 `<script type="module">` 里对 `https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle` 做**动态 import**，该包为 <span style="color:#e67e22">**多兆字节**</span>的单文件 bundle，且托管在**境外 CDN**；
- 本机出网需经代理，境外 CDN 的**首包/持续下载速度会间歇性抽风**；
- 这一次恰好落在抽风窗口内，120 秒硬上限内没下完 → `window.__ready` 不置位 → 超时；
- **`goto` 之后的等待是"硬超时"**，不会自动重试——脚本原版**只等一次，失败即 `sys.exit(1)`**，把偶发的网络抖动放大成"任务失败"。

### 故障链条

1. 生成器跑完 → 产出 `_chars.json`（正常）；
2. `_measure_chars.py` 启动 Chromium、打开本地测量页（正常）；
3. 页面开始 `await import("https://esm.sh/…")` → 境外 CDN 抽风，**数 MB 包下载停滞**；
4. 120 秒到 → `page.wait_for_function` 抛 `TimeoutError`；
5. 原脚本无重试逻辑 → 直接失败退出。

## 诊断数据

**① 报错定位**（`_measure_chars.py`）：

| 位置 | 代码 | 作用 |
|---|---|---|
| HTML `<script type="module">` | `await import("https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle")` → `window.__ready = true` | 成功后置"就绪"标志位（<span style="color:#e74c3c">**卡住的就是这一句**</span>） |
| `main()` 第 120 行附近 | `page.wait_for_function("window.__ready === true", timeout=120000)` | 等模块加载完，**硬上限 120 秒、只等一次** |
| `main()` 第 133~135 行 | `err = page.evaluate("window.__err")` | 若 import 直接抛错则打印 `__err`（本次**未**触发，说明是"慢"而非"错/被封"） |

> 🔍 **<span style="color:#e74c3c">两种失败要分清：</span>** 若打印 `ERROR: excalidraw module failed: …` = import **抛异常**（CDN 被拦 / 域名解析失败）；本次是 `wait_for_function` **超时** = import **没抛错但没在下完**（**慢**）。**本次是后者**——这点直接决定了处置方式是"重试"而非"换源/查墙"。

**② 网络对照证据**（报错后立刻实测，证明是**瞬时段性抖动**而非持续故障）：

| 目标 | HTTP 状态 | 耗时 | 结论 |
|---|---|---|---|
| `https://esm.sh` | <span style="color:#e67e22">**200**</span> | <span style="color:#e67e22">**0.53 s**</span> | 报错后瞬间即通 → **瞬时抖动** |
| `https://cdn.jsdelivr.net` | 200 | 4.55 s | 备用 CDN 可达，但明显偏慢 |

> 📊 **<span style="color:#e67e22">数据说明：</span>** 报错当时不通、**报错后 0.53 秒就通**，恰恰说明问题在**境外线路的瞬时抖动**上，而不是"CDN 挂了"或"被墙了"。这类问题的正确处置是**重试 + 加固重试逻辑**，不需要动网络配置。

**③ 修复前 vs 修复后（脚本行为对比）**：

| 行为 | 修复前 | 修复后 |
|---|---|---|
| 加载失败处置 | 等一次、失败即退出 ❌ | <span style="color:#e67e22">**最多重试 3 次**</span> ✅ |
| 重试方式 | — | 每次**新建 page** 重开（清掉上一次的坏状态） |
| 失败提示 | 只抛 playwright 原始堆栈 | 追加一句人话指引：提示检查 `https://esm.sh` 可达性（代理/网络）后重跑 |
| 重复 import | 文件里**有两行** `from playwright.sync_api import sync_playwright`（冗余） | 已删除重复行 |

## 修复过程

### 第 1 步：定位（三层诊断）

对照报错文案排除环境层（不是 `Chromium not installed`）→ 确认文件层正常 → 锁定**网络/CDN 层瞬时抖动**。

### 第 2 步：直接重试（验证"瞬时"判断）

**原命令直接重跑**，这一次加载成功、8 组字号×字体的字宽全部量出，`_charmetrics.json` 正常落盘 —— **反证了根因确为瞬时网络抖动**。

### 第 3 步：加固脚本（把"偶发"变"可自愈"）

单靠"重跑一次"只是运气好，治本做法是**把重试写进脚本**。改动点：

```python
ready = False
for attempt in range(1, 4):                       # ← 最多 3 次
    try:
        page.goto(tmp_html.as_uri())
        page.wait_for_function("window.__ready === true", timeout=120000)
        ready = True
        break
    except Exception as e:
        print(f"[警告] 第 {attempt}/3 次加载超时：{type(e).__name__}: {e}",
              file=sys.stderr)
        page = browser.new_page(viewport={"width": 1200, "height": 400})   # ← 换新页再试
if not ready:
    print("ERROR: 连续 3 次都没能加载 excalidraw 模块——"
          "检查能否访问 https://esm.sh （代理/网络），再重跑本脚本。",
          file=sys.stderr)
    sys.exit(1)
```

同时把注释写进代码，让**未来的自己**一眼看懂为什么需要重试：

```python
# 页面要动态 import esm.sh 上的 excalidraw 包（约数 MB）并下载内嵌字体，
# 境外 CDN 偶发抽风会让这一句等到 120s 超时 → 重试即可，不必改代码。
```

并顺手删掉重复的 `from playwright.sync_api import sync_playwright`。

### 第 4 步：重跑加固版验证

加固版脚本完整跑通，控制台依次打印字体栈探测 + 8 行 `[OK] <fs>|<fam>: N 字符，最大宽度 …px`。

> ⚠️ **无需重启会话**：本次是改脚本逻辑，不涉及 PATH / 环境变量。

## 技术栈与涉及工具

- **Playwright**（微软开源浏览器自动化库）：`sync_playwright()` 启 Chromium、`page.goto()` 开本地 HTML、`wait_for_function()` 等页面条件、`page.evaluate()` 回读结果；
- **Chromium（headless shell）**：真正执行 `import` 与 SVG 文字量宽的运行体（本机已装，见 [[20-Playwright Chromium未安装]]）；
- **esm.sh**（境外 ES Module CDN）：动态按需提供 `@excalidraw/excalidraw@0.18.0` 的 bundle —— <span style="color:#e67e22">**本次报错的外部依赖方**</span>；
- **`_measure_chars.py`**（字宽测量脚本）：用**真机字体栈**逐字符 `getComputedTextLength()`，产出 `_charmetrics.json`，供排版器精确算行宽（避免"估宽"导致的换行错位）；
- **两遍测量工作流（two-pass metrics）**：先生成字符清单 → 再真机量宽 → 再回灌生成器排版，是 Excalidraw 旁批/范文混排（印刷体 + 手写体同栏）必需的精度保障；
- **uv**：在 `references/` 项目虚拟环境内执行脚本；
- **Excalidraw 图表 skill**：知识库技能 `.claude/skills/Excalidraw图表/`。

## 遇到的问题与坑

- 🕳️ **<span style="color:#e74c3c">报错文案欺骗性：</span>** `Timeout` 出现在 `wait_for_function`，很容易被误读成"页面渲染慢 / 元素等不到"。实际卡的是**页面内部的网络下载**，与 Excalidraw 渲染逻辑无关——**看到超时先分清"等的是 DOM 还是等的是网络"**；
- 🕳️ **<span style="color:#e67e22">"能启动"与"能跑完"要分开判断：</span>** 同一个脚本，09-14 报的是 `Chromium not installed`（本机缺二进制，属**环境层**），09-29 报的是 `Timeout`（境外 CDN 慢，属**网络层**）。**前者要装东西，后者只要重试**——处置方式完全相反，切勿照着旧档案乱装依赖；
- 🕳️ **<span style="color:#2980b9">境外 CDN 是"每次运行"的依赖：</span>** 脚本每跑一次都要现场从 `esm.sh` 拉包，所以**历史上跑通过不代表这次不失败**，网络抖动是随机事件，与脚本版本无关；
- 🕳️ **超时是硬上限、不会自动重试：** 原脚本 `for` 循环之外只有一次等待，偶发抖动会直接变成"任务失败"，必须靠**脚本层重试**消化；
- 🕳️ **报错后立刻实测 0.53 秒即通：** 这个对照动作成本极低、价值极高——它一次性排除了"CDN 挂了 / 域名被墙 / 代理配置错"三种错误方向，**不必再去折腾代理配置**；
- 🕳️ **冗余 import 是修复时的意外收获：** 原文件有两行同名 import，虽不影响运行，但顺手清掉（属低风险整洁性改动）。

## 验证结果

- ✅ **报错消除**：加固版脚本重跑，8 组组合（`42|2`、`24|2`、`19|1`、`31|2`、`23|1`、`18|2`、`26|1`、`20|1`）字宽**全部量出**，`_charmetrics.json` 正常落盘；
- ✅ **脚本自愈能力**：新增 3 次重试 + 失败人话指引，可自行消化同类瞬时抖动；
- ✅ **下游产物一致**：用新字宽表重跑的生成器，元素数与**线上成品完全吻合**（122 elements / 108 texts / 8 pages）—— 证明测量结果准确、排版无回归；
- ✅ **最终交付**（行间距任务的成品，任务闭环）：
  - `第3篇短文-举重奶奶的逆龄人生（旁批笔记）.pdf`（**10 页 A4 纵向**，4,246,355 字节；正文行距由 1.85 放大到 **4.25 ≈ 21.6mm**，批注保持 1.75 ≈ 6.6mm）
  - `第3篇短文-举重奶奶的逆龄人生（旁批笔记）.excalidraw.md`（51,194 字节）
  - 存放于 `总结好的大纲以及笔记/学校/课程/英语/`
- ✅ **备份留档**：见下方「附件」——修复前的原始成品另有 `_备份20260915.pdf` / `_备份20260915.excalidraw.md`（同目录）。

## 🔁 复发记录（2026-09-29 22:04）：渲染脚本同样卡在 esm.sh 动态导入——第 2、3 次

> **复发时间**：2026-09-29 22:04
> **发生地**：<span style="color:#e67e22">**`.claude/skills/Excalidraw图表/references/render_excalidraw.py`**</span>（Excalidraw 出图脚本，**同一 skill 的另一个脚本**）——本档案首发的 1 次发生在 `_measure_chars.py`（字宽测量），本次 2 次发生在**渲染脚本**，**同一个根因换了个脚本继续发作**。

### 触发场景

实现"**批注内英文改用意大利斜体**"需求时，需要把重新生成的 `.excalidraw` 渲染成 PNG。先用最小可行性样例 `_test_italic.excalidraw` 验证"Unicode 数学斜体字母在手写体（fontFamily=1）下能否正常回退显示"，渲染脚本**连续 2 次**抛出同一款超时：

```
ERROR: 连续 3 次都没能加载 excalidraw 模块——检查能否访问 https://esm.sh （代理/网络）后重跑本脚本。
playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 120000ms exceeded.
```

（渲染脚本内部等的是 `window.__moduleReady === true`，与测量脚本的 `window.__ready` 是**同一套机制、同一个 CDN 依赖**，只是标志位名字不同。）

### 诊断证据（本次补测，比首发更细）

**① 系统代理配置**（PowerShell 读注册表）：

| 项 | 值 |
|---|---|
| `ProxyEnable` | `1`（系统代理**是开着的**） |
| `ProxyServer` | `127.0.0.1:7897` |
| 当时 `netstat` | **7897 端口一度无监听**（代理进程/隧道状态抖动） |

**② IPv6 出站对照**（`curl` 直测那个 8.2 MB 的 bundle）：

| 命令 | 结果 | 耗时 |
|---|---|---|
| `curl -sL <bundle>`（默认） | <span style="color:#e67e22">**HTTP 200**</span> | 1.1–1.7 s |
| `curl -4`（强制 IPv4，解析到 `104.26.14.209`） | 200 | 正常 |
| `curl -6`（强制 IPv6） | <span style="color:#e74c3c">**code 000**</span> | 0.048 s（**无 IPv6 出站路由**） |

→ 证明：<span style="color:#2980b9">**本机 IPv4 通路是好的、IPv6 根本不通**</span>；Chromium 若走 IPv6 优选就会瞬间失败。

**③ 网络 A/B 实验**（`_test_proxy_ab.py`，用 `page.goto()` 直达 bundle 而非 fetch，避免 CORS 假阳性）：

| 组别 | 启动参数 | 结果 |
|---|---|---|
| A 默认 | — | <span style="color:#e74c3c">`net::ERR_CONNECTION_CLOSED`</span> |
| B 强制不走代理 | `--no-proxy-server` | <span style="color:#e74c3c">`net::ERR_CONNECTION_CLOSED`</span> |
| C 强制 IPv4 | `--no-proxy-server --host-resolver-rules=MAP esm.sh 104.26.14.209` | 稍后复测 **200** |
| D 走本地代理 | `--proxy-server=http://127.0.0.1:7897` | 稍后复测 **200**（此时 7897 已有 ESTABLISHED 连接） |

> 🔍 **<span style="color:#e74c3c">关键判读：</span>** 首测 A/B 两种配置**同时**报 `ERR_CONNECTION_CLOSED`（走代理、不走代理都断）——说明**不是代理配置的锅**，而是**出网链路本身在分钟级抖动**；几分钟后同一套 4 组参数复测**全部 200**，链路自行恢复。**这正是"瞬时段性抖动"的教科书证据**，与首发"报错后 0.53 s 即通"是同一现象、更强证据。

### 处置（与首发一致：重试即愈，不改配置）

1. **不装任何东西**（报错文案不是 `Chromium not installed`，环境层无病）；
2. **不折腾代理配置**（A/B 已排除代理因素，IPv6 只是次要放大项，IPv4 通路正常）；
3. **原命令重跑** → 模块加载成功，`_test_italic.png` 渲染出图、字体回退正常（**无豆腐块**）；
4. **加固渲染脚本**：把测量脚本同款的 **3 次重试 + 每次换新 page + 失败人话指引** 移植到 <span style="color:#e67e22">**`render_excalidraw.py`**</span>，并加注释指向本档案（"重试即可自愈，不必改代码"）。

### 影响与结论

- ✅ **两个脚本现已同款加固**（`_measure_chars.py` + `render_excalidraw.py`），同类抖动都能自愈；
- ✅ **下游任务不受影响**：加固后正式渲染 10 页 PNG **一次通过**，最终交付 `第3篇短文-举重奶奶的逆龄人生（旁批笔记）.pdf`（10 页 A4，4,284,621 字节）与同名 `.excalidraw.md`（60,151 字节）；
- 📌 **新增监测建议**：凡是**在浏览器里动态 `import` 境外 CDN 包**的知识库脚本，都应内置"3 次重试"；本机 **IPv6 无出站路由**，若日后此类超时变频繁，可优先排查 Chromium 是否在尝试 IPv6 优选（`--host-resolver-rules` 锁 IPv4 可作应急手段）。

## 使用建议与遗留事项

- 💡 **<span style="color:#2980b9">以后遇到同款 `wait_for_function: Timeout` 直接照方抓药：</span>** 先**原命令重跑一次**；若仍失败再查 `https://esm.sh` 可达性与代理（见 [[06-国外网站访问慢但Codex正常]]），**不要去重装 Playwright/Chromium**；
- 💡 **<span style="color:#2980b9">看到 `Chromium not installed` 则相反：</span>** 那是环境层缺二进制，照 [[20-Playwright Chromium未安装]] 跑 `uv run playwright install chromium`；
- 📌 **<span style="color:#e67e22">可选优化（未实施）：</span>** 若日后抖动变频繁，可考虑 ① 把 `@excalidraw/excalidraw` 的 bundle **本地缓存**（改从本地文件 import，彻底摆脱境外 CDN）；② 或给 `esm.sh` 配**备用 CDN 回退**（如 `cdn.jsdelivr.net`）。本次抖动为偶发、加固后已能自愈，故未实施，列为监测项；
- 📌 **监测对象**：凡是**每次运行都要在线拉包**的技能脚本（字宽测量、Excalidraw 渲染），都可能复现本类超时——若连续多次重试仍失败，才升级为"网络/代理"问题排查；
- 📎 **附件**：
  - 测量脚本·加固后留档：[查看留档：_measure_chars.py（2026-09-29加固后）.py](总结好的大纲以及笔记/知识库FAQ/原始文件备份/_measure_chars.py（2026-09-29加固后）.py)
  - 渲染脚本·加固后留档：[查看留档：render_excalidraw.py（2026-09-29加固后）.py](总结好的大纲以及笔记/知识库FAQ/原始文件备份/render_excalidraw.py（2026-09-29加固后）.py)
  - 现役脚本：[查看脚本：_measure_chars.py](.claude/skills/Excalidraw图表/references/_measure_chars.py)　·　[查看脚本：render_excalidraw.py](.claude/skills/Excalidraw图表/references/render_excalidraw.py)

## 🔗 相关笔记

- [[00-报错统计台账]] — 报错统计权威源（本档案为 **F20** 行）
- [[20-Playwright Chromium未安装]] — **同一个脚本、不同层**的报错（环境层缺浏览器二进制），两者处置方式相反，务必对照阅读
- [[06-国外网站访问慢但Codex正常]] — 若确为持续性境外访问慢（而非瞬时抖动），走该档案的分流修复
- [[04-Codex桌面端反复重新连接（公司环境）]] — 同属"境外网络链路不稳定"总类
- [[22-机场订阅到期导致小火箭节点清空（全站境外无法访问）]] — 另一类"境外不可达"故障（订阅到期），用于区分"抖动"与"断网"
- [[18-Excalidraw旧格式提示与插件版本更新]] — 同属 Excalidraw 工具链相关记录
