---
title: "Excalidraw 渲染脚本报 Chromium not installed（Playwright 浏览器二进制缺失）"
type: "知识库 FAQ / 报错记录"
date: 2026-09-14
created: 2026-09-14
updated: 2026-09-14
tags:
  - 报错
  - 知识库FAQ
  - Excalidraw
  - Playwright
  - Chromium
  - 环境依赖
  - Python
source: "Excalidraw 渲染脚本 .claude/skills/Excalidraw图表/references/render_excalidraw.py；触发任务：整理英语网课纪要（第3篇短文·举重奶奶的逆龄人生）为 Excalidraw 旁批笔记并导出 PDF"
---

# 🧩 Excalidraw 渲染脚本报 Chromium not installed（Playwright 浏览器二进制缺失）

> [!summary] 📊 报错统计速览（截至 2026-09-14）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（2026-09-14 首发 1 次，暂无复发记录）。根因为 **「Playwright 安装了 Python 包、但从未下载浏览器二进制（Chromium），`launch()` 时找不到可执行文件」**，属环境层依赖缺失，非脚本或图纸内容问题。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🧾 Playwright 浏览器二进制缺失（Chromium 未安装） | **1** | 20 |
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
ERROR: Chromium not installed for Playwright.
Run: cd .claude/skills/Excalidraw图表/references && uv sync && uv run playwright install chromium
```

> **出现时间**：2026-09-14（整理英语网课纪要任务执行中）
> **来源**：知识库技能脚本 <span style="color:#e67e22">**`.claude/skills/Excalidraw图表/references/render_excalidraw.py`**</span>（Excalidraw 图表 skill 的渲染器）。
> **触发场景**：把英语网课纪要（第 3 篇短文《举重奶奶的逆龄人生》）整理成 Excalidraw 旁批笔记后，**第一次调用渲染脚本把 `.excalidraw` 转成 PNG** 时报此错。

## 现象描述

任务本身已推进到"最后一步出图"：旁批笔记的 Excalidraw 场景 JSON 已经生成完毕、内容校验通过，脚本启动 Playwright 准备把图渲染成 PNG 时**直接退出**，控制台打印上面那行提示。

关键特征——<span style="color:#2980b9">**这不是报错堆栈，而是脚本预先写好的"友好提示"**</span>。脚本在 `main()` 里捕获了 Playwright 抛出的 `Executable doesn't exist` 异常，转成一句人话告诉用户"去装浏览器"，然后 `sys.exit(1)`。所以：

- ✅ **文件层没问题**：图纸 JSON 合法、元素齐全，脚本自带的 `validate_excalidraw()` 已通过；
- ❌ **环境层缺东西**：本机装好了 Playwright，却没装 Playwright 要用到的**浏览器程序本体**。

> 💡 **<span style="color:#2980b9">认知：</span>** **"装了 Playwright" ≠ "装好了浏览器"**。Playwright 由两部分组成——<span style="color:#e67e22">**① Python 包**（`pip`/`uv` 装的库，只管调度）+ **② 浏览器二进制**（Chromium/Firefox/WebKit，几百 MB 的程序本体，需另外单独下载）</span>。`uv sync` 只装①，浏览器②必须再跑一条 `playwright install` 才装。本次报错正是**只有①没有②**。

## 根本原因（三层诊断）

按报错修复 skill 的三层法逐层排查，根因落在**第②层环境层**：

### ① 文件层（报错对象本身）——正常 ✅

- 传入渲染脚本的 `.excalidraw` 文件 JSON 结构完整、`type: "excalidraw"`、`elements` 数组非空；
- 脚本第 21~35 行的 `validate_excalidraw()` 校验全部通过，**没有任何文件内容错误**；
- 说明本次报错与"图纸画得对不对"无关。

### ② 环境层（机器依赖）——**根因所在** ❌

- 项目依赖已声明：`references/pyproject.toml` 里写了 `playwright>=1.40.0`，`uv.lock` 锁定实际版本为 <span style="color:#e67e22">**playwright 1.61.0**</span>；
- `uv run` 能正常拉起 Python、`import playwright` 成功——说明 **① Python 包已就位**；
- 但浏览器安装目录 <span style="color:#e74c3c">**`C:\Users\asus\AppData\Local\ms-playwright\`**</span> 下**缺少该 Playwright 版本对应的 Chromium 目录**，`p.chromium.launch(headless=True)` 找不到可执行文件，抛 `Executable doesn't exist`；
- 脚本第 124~132 行捕获该异常并打印"Chromium not installed for Playwright"，即本次报错原文。

### ③ 工具/会话层（当前会话能力）——正常 ✅

- `uv` 环境可用、Python 3.11+ 运行正常；
- 网络可达 `esm.sh`（渲染模板要在线加载 `@excalidraw/excalidraw`），无代理/防火墙阻断；
- 会话无图片投递限制（本次不涉及读取图片类文件）。

### 故障链条

1. 技能是首次在本机使用（或曾清理过 `ms-playwright` 目录）→ 只有 Playwright **Python 包**，没有**浏览器二进制**；
2. 渲染脚本启动 → 调用 `p.chromium.launch(headless=True)`；
3. Chromium 可执行文件不存在 → 抛 `Executable doesn't exist`；
4. 脚本捕获后打印友好提示 → 报错终止。

## 诊断数据

**① 报错定位**（`render_excalidraw.py`）：

| 位置 | 代码 | 作用 |
|---|---|---|
| 第 124~132 行 | `try: browser = p.chromium.launch(headless=True)` / `except … "Executable doesn't exist" in str(e)` | 捕获"浏览器未装"，打印本次报错文案并 `sys.exit(1)` |
| 第 82~84 行 | `except ImportError: … playwright not installed` | 另一种情况：**连 Python 包都没有**时走这里（本次**未**触发） |

> 🔍 **<span style="color:#e74c3c">两种缺失要分清：</span>** 报 `ImportError / playwright not installed` = 缺 **Python 包**（跑 `uv sync`）；报本次的 `Chromium not installed` = 缺**浏览器二进制**（跑 `playwright install chromium`）。**本次是后者。**

**② 依赖与版本**：

| 项 | 值 |
|---|---|
| Python 包声明 | `pyproject.toml` → `playwright>=1.40.0` |
| 锁定版本 | `uv.lock` → <span style="color:#e67e22">**playwright 1.61.0**</span> |
| 运行方式 | `uv run python render_excalidraw.py <file.excalidraw>` |

**③ 修复前 vs 修复后（浏览器安装目录对比）**：

| 目录 `<LOCALAPPDATA>\ms-playwright\` | 修复前 | 修复后 |
|---|---|---|
| `chromium_headless_shell-<rev>/` | ❌ 缺失 | ✅ <span style="color:#e67e22">**已装（build 1228，约 270MB）**</span> |
| `chromium-<rev>/` | ❌ 缺失 | ✅ 已装 |
| `ffmpeg-<rev>/` | ❌ 缺失 | ✅ 已装 |
| `winldd-<rev>/` | ❌ 缺失 | ✅ 已装（Windows 依赖检查工具） |

> 📊 **<span style="color:#e67e22">数据说明：</span>** 渲染脚本用的是 **headless shell**（无头模式专用精简版 Chromium），所以真正被拉起来的是 `chromium_headless_shell-1228`；`chromium-1228`、`ffmpeg-1011`、`winldd-1007` 是 `playwright install chromium` 的配套下载项。

## 修复过程

### 第 1 步：定位（三层诊断）

确认文件层正常 → 锁定环境层缺浏览器二进制 → 会话层正常，无需重启。

### 第 2 步：安装浏览器二进制

在技能脚本目录执行（<span style="color:#e74c3c">**必须在 `pyproject.toml`/`uv.lock` 所在目录跑，`uv run` 才认得环境**</span>）：

```bash
cd "F:\积昌的知识库 - 副本\.claude\skills\Excalidraw图表\references"
uv run playwright install chromium
```

下载内容：

- <span style="color:#e67e22">**Chrome Headless Shell（build 1228，对应 Chrome 149）**</span>
- **Winldd**（Windows 依赖扫描工具，Chromium 正常启动的前置依赖）

安装落点：`C:\Users\asus\AppData\Local\ms-playwright\`（Playwright 默认路径）。

### 第 3 步：重新渲染

安装完成后**原命令直接重跑**，不再报错——6 页 PNG 全部渲染成功。

> ⚠️ **无需重启会话**：本次是"缺文件"而非"改 PATH/环境变量"，装完当下即可生效（与 [[01-Obsidian反复报错Request too large]] 里"装完 poppler 必须重启会话"的情况不同）。

## 技术栈与涉及工具

- **Playwright**（微软开源浏览器自动化库）：Python 包 + 浏览器二进制**两段式**安装；
- **uv**（Astral 出品的 Python 包与环境管理器）：`uv run` 在项目虚拟环境内执行脚本；
- **Chromium / Chrome Headless Shell**：Playwright 驱动无头浏览器渲染 Excalidraw 的 SVG；
- **Excalidraw 渲染脚本**（`render_excalidraw.py`）：读 `.excalidraw` JSON → 用 Playwright 打开 `render_template.html` → 在线加载 `@excalidraw/excalidraw` → `exportToSvg` → 截图存 PNG；
- **Excalidraw 图表 skill**：知识库技能 `.claude/skills/Excalidraw图表/`。

## 遇到的问题与坑

- 🕳️ **<span style="color:#e74c3c">"装了 Playwright" 是假象：</span>** `uv sync` / `pip install playwright` 只装**调度库**，不装**浏览器本体**。缺浏览器时脚本报的是"Chromium not installed"，不是"playwright not installed"，容易被误读成"包没装好"而白折腾 `uv sync`；
- 🕳️ **<span style="color:#e67e22">安装必须在项目目录内跑：</span>** `uv run playwright install` 依赖当前目录的虚拟环境，在知识库根目录或别的目录跑，可能装到别的环境或直接失败；
- 🕳️ **浏览器默认装 C 盘、体积不小：** `ms-playwright` 默认落在 `C:\Users\<用户>\AppData\Local\`，本次约 <span style="color:#e67e22">**270MB**</span>（另含 ffmpeg/winldd 等）。若需迁到 F 盘，用环境变量 `PLAYWRIGHT_BROWSERS_PATH` 指定（见下节遗留事项）；
- 🕳️ **本次报错与图纸无关：** 脚本先做 `validate_excalidraw()` 再启动浏览器，**能走到 launch 这一步，就说明图纸 JSON 已通过校验**——排查时不必回头怀疑图纸；
- 🕳️ **在线渲染依赖外网：** 渲染模板要从 `esm.sh` 拉 `@excalidraw/excalidraw`（脚本给了 120s 超时）。本次网络正常、与报错无关，但若日后在受限网络下报渲染失败，需先查代理（见 [[06-国外网站访问慢但Codex正常]]）。

## 验证结果

- ✅ **报错消除**：重跑 `uv run python render_excalidraw.py …` 不再出现 `Chromium not installed`；
- ✅ **产物生成**：6 个分页 PNG 全部渲染成功；
- ✅ **最终交付**（任务闭环）：
  - `第3篇短文-举重奶奶的逆龄人生（旁批笔记）.excalidraw.md`（81,675 字节）
  - `第3篇短文-举重奶奶的逆龄人生（旁批笔记）.pdf`（5,436,733 字节，**6 页 A4 横向**）
  - 存放于 `总结好的大纲以及笔记/学校/课程/英语/`
- ✅ **目录自检**：`ms-playwright/` 下 `chromium_headless_shell-1228`、`chromium-1228`、`ffmpeg-1011`、`winldd-1007` 四个目录齐备。

## 使用建议与遗留事项

- 💡 **<span style="color:#2980b9">以后遇到同款报错直接照方抓药：</span>** 进技能目录跑 `uv run playwright install chromium` 即可，无需重复三层诊断；
- 📌 **<span style="color:#e67e22">迁移到 F 盘（可选优化）：</span>** 若要遵守知识库「下载默认装 F 盘」规则，可设环境变量后再安装：
  ```bash
  export PLAYWRIGHT_BROWSERS_PATH="F:/Programs/ms-playwright"   # Git Bash
  # 或 PowerShell: $env:PLAYWRIGHT_BROWSERS_PATH="F:\Programs\ms-playwright"
  uv run playwright install chromium
  ```
  装完后**后续每次跑渲染脚本都要带上同一环境变量**，否则 Playwright 仍去 C 盘默认路径找浏览器。本次未迁移（已装于 C 盘可用），列为可选优化；
- 📌 **监测对象**：若日后重装知识库、清理 `ms-playwright` 目录或换机，渲染脚本会再次报 `Chromium not installed`——按本档案第 2 步一条命令即可恢复；
- 📎 **关联对象**：
  - 渲染脚本：[查看脚本：render_excalidraw.py](.claude/skills/Excalidraw图表/references/render_excalidraw.py)
  - 渲染模板：[查看模板：render_template.html](.claude/skills/Excalidraw图表/references/render_template.html)

## 🔗 相关笔记

- [[00-报错统计台账]] — 报错统计权威源（本档案为 **F19** 行）
- [[18-Excalidraw旧格式提示与插件版本更新]] — 同属 Excalidraw 相关报错（插件/文件格式类）
- [[17-tool_result内嵌伪PNG致API400unsupported-image]] — 同属"环境/工具链导致渲染或投递失败"类报错
- [[01-Obsidian反复报错Request too large]] — 同属"环境层缺依赖（poppler）"类报错，处理思路一致（装依赖→验证）
- [[06-国外网站访问慢但Codex正常]] — 若渲染脚本在线拉取 `@excalidraw/excalidraw` 失败，可先排查网络/代理
