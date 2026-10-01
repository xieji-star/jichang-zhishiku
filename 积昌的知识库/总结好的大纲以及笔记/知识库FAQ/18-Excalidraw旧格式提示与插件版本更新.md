---
title: "Excalidraw 旧版 .excalidraw 文件触发兼容模式提示与插件版本更新"
type: "知识库 FAQ / 报错记录"
date: 2026-09-13
created: 2026-09-13
updated: 2026-09-13
tags:
  - 报错
  - 知识库FAQ
  - Obsidian
  - Excalidraw
  - 插件
  - 兼容模式
  - 文件格式
source: "Obsidian 社区插件 obsidian-excalidraw-plugin（2.26.4 → 2.27.3）；触发文件 总结好的大纲以及笔记/学校/课程/大二上/电工学/回路电流法-Excalidraw.excalidraw"
---

# 🧩 Excalidraw 旧版 .excalidraw 文件触发兼容模式提示与插件版本更新

> [!summary] 📊 报错统计速览（截至 2026-09-13）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（2026-09-13 首发 1 次，暂无复发记录）。根因为 **「打开旧版 `*.excalidraw` 格式文件触发插件兼容模式提示（该文件未转换为新格式 `.excalidraw.md`）」**，并顺带完成插件版本更新（2.26.4 → 2.27.3）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🧾 旧版 *.excalidraw 文件触发兼容模式提示（未转新格式） | **1** | 18 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

## 🧭 快速索引

- 🧾 [[#错误信息|错误信息]]
- ⚠️ [[#现象描述|现象描述]]
- 🔍 [[#根本原因|根本原因]]
- 📊 [[#诊断数据|诊断数据]]
- 🛠️ [[#修复过程|修复过程]]
- 📽️ [[#技术栈与涉及工具|技术栈与涉及工具]]
- 🕳️ [[#遇到的问题与坑|遇到的问题与坑]]
- ✅ [[#验证结果|验证结果]]
- 📌 [[#使用建议与遗留事项|使用建议与遗留事项]]

## 错误信息

```
*.excalidraw 是兼容旧版的绘图文件格式。需要转换为新格式才能解锁本插件的全部功能。

[转换为新格式]
```

```
Excalidraw 的新版本已在社区插件中可用。您正在使用 2.26.4。最新版本是 2.27.3。
```

> **出现时间**：2026-09-13 23:30
> **来源**：Obsidian 社区插件 **Excalidraw**（`obsidian-excalidraw-plugin`）。
> **触发场景**：每次用 Excalidraw 打开旧版绘图文件 `总结好的大纲以及笔记/学校/课程/大二上/电工学/回路电流法-Excalidraw.excalidraw` 时，顶部弹出第一条提示条；同时插件检测到版本落后，弹出第二条更新提示。

## 现象描述

用户反馈：<span style="color:#e74c3c">**"一调用 Excalidraw 插件，就弹出这个报错和更新提示"**</span>。拆开来看是**两件互不相同的事**：

- **① 兼容模式提示（本文报错主体）**：打开 **`*.excalidraw`** 旧版格式文件时，插件在文档顶部显示一条提示条——该文件被"以兼容模式打开"，提示转换为新格式才能用全部功能；
- **② 插件更新提示**：插件版本 2.26.4 落后于最新 2.27.3，弹出版本更新提示。

> 💡 **<span style="color:#2980b9">认知：</span>** 第 ① 条**不是故障，是插件的"格式迁移提醒"**——Excalidraw 插件 2.x 起把绘图文件的主格式从纯 JSON 的 `*.excalidraw` 换成了 Obsidian 笔记形态的 <span style="color:#e67e22">**`*.excalidraw.md`**</span>；旧格式文件仍能打开，但走的是**兼容模式**（功能受限），所以插件每次打开都提醒一次。

## 根本原因

### ① 兼容提示：文件扩展名判定 + 未迁移的旧格式文件

在插件源码中，是否进入"兼容模式"由**文件扩展名**直接判定：

```js
compatibilityMode = "excalidraw" === this.file.extension
```

只要打开的文件的 <span style="color:#e67e22">**`extension` 恰为 `excalidraw`**</span>（即 `*.excalidraw`），插件就进入兼容模式并弹出提示：

```js
compatibilityMode || new Notice(t$d("COMPATIBILITY_MODE"))
// COMPATIBILITY_MODE: "*.excalidraw file opened in compatibility mode.
//   Convert to new format for full plugin functionality."
// CONVERT_FILE: "Convert to new format"
```

**因此只要知识库里还存在 `*.excalidraw` 文件，打开它就必然弹提示。** 根治办法是<span style="color:#e74c3c">**把旧格式文件迁移为新格式 `.excalidraw.md`**</span>。

> ⚠️ **<span style="color:#e67e22">注意区分两个同名字段：**</span>插件设置项里也有一个 `compatibilityMode`（界面名"New drawings as legacy files / 新绘图保存为旧版文件"），它是**开关**，值为 `false`——若把它改成 `true` 虽能关掉提示，但会导致**以后新建的每张图都存成旧格式**，属于因噎废食，本档案不采用。

### ② 更新提示：插件版本落后

插件 <span style="color:#e67e22">**`manifest.json` 中 version = 2.26.4**</span>，而仓库最新发布为 **2.27.3**；插件/ Obsidian 比对后提示更新。

### 故障链条

1. 库中存有 1 个旧格式文件 `回路电流法-Excalidraw.excalidraw`（并被记在 Obsidian 的 <span style="color:#e67e22">**workspace 打开状态**</span>里）；
2. 用户打开它 → 插件按扩展名判定进入兼容模式 → 弹兼容提示；
3. 插件同时比对新版本 → 弹更新提示；
4. 两条提示叠加，表现为"一开插件就报错"。

## 诊断数据

**① 全库旧格式文件清点**（`find -name "*.excalidraw"`）：

| 文件 | 位置 | 状态 |
|---|---|---|
| `图灵学术——流量培训.excalidraw` | `.trash/`（Obsidian 回收站） | 插件不扫描 `.trash`，**不触发**提示 |
| `回路电流法-Excalidraw.excalidraw` | `总结好的大纲以及笔记/学校/课程/大二上/电工学/` | **18,092 字节 / 31 个图元**，被 workspace 记录为已打开 → **本次报错触发者** |

**② 插件版本实测**：`.obsidian/plugins/obsidian-excalidraw-plugin/manifest.json` → `"version": "2.26.4"`；`main.js` 4,106,403 字节（实际 5,106,403）、`styles.css` 224,752 字节。

**③ 插件设置**（`data.json`）：`compatibilityMode=false`、`useExcalidrawExtension=true`、`compress=true`、`showNewVersionNotification=true`、`previousRelease=2.26.4`。

**④ 旧格式文件结构**：标准 excalidraw.com 场景 JSON——`{type, version:2, source:"https://excalidraw.com", elements:[31], appState, files:{}}`。

**⑤ 新格式文件结构**（对照插件自己写出的样本 `中间文件/Excalidraw/Drawing 2026-09-11 21.35.43.excalidraw.md`，570 字节）：

```markdown
---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== …

## Drawing
```compressed-json
<base64（LZString，按 256 字符 + 空行分块）>
```
%%
```

**⑥ <span style="color:#2980b9">压缩算法逆向结论</span>**：`compressed-json` 块 = <span style="color:#e67e22">**`LZString.compressToBase64(场景JSON)`**</span>，再按 **256 字符一段、段间插入 `\n\n`** 拼装（插件 `compress()` 函数）：

```js
function compress(e){
  const t = LZString.compressToBase64(e);
  let i = "";
  for (let e = 0; e < t.length; e += 256) i += `${t.slice(e, e+256)}\n\n`;
  return i.trim();
}
```

> 🔍 **<span style="color:#e74c3c">关键校验：</span>** 解剖插件样本时发现 base64 串以 `===` 结尾（正常 base64 最多两个 `=`）——正是 **LZString 的 padding 特征**（余 1 字符时补 `===`），由此确定算法不是 pako/zlib。

## 修复过程

### 第 1 步：备份（先备份后改动）

- 旧格式原件 → `总结好的大纲以及笔记/知识库FAQ/原始文件备份/回路电流法-Excalidraw.excalidraw`（保持原名）；
- 插件 2.26.4 全套原件（`main.js` / `manifest.json` / `styles.css` / `data.json`）→ <span style="color:#e67e22">**`F:\Programs\_excalidraw-plugin-backup\obsidian-excalidraw-plugin-2.26.4\`**</span>（放 F 盘、不放进知识库，避免 5MB 大文件撑大 GitHub 备份仓库）。

### 第 2 步：逆向并复刻插件压缩算法（Node + lz-string）

用 Node 脚本复刻插件的 `compress()` / `decompress()`，并先做**自检**：把插件样本解压后再重压，看能否<span style="color:#e74c3c">**字节级还原**</span>——

```
[自检] 样本解压长度 : 195
[自检] 重压与原块一致 : PASS ✅
```

自检通过，说明我方实现与插件**完全一致**，再执行转换：

```
[转换] 元素数量 : 31
[转换] 场景字节数 : 12903
[转换] 写出 : …/回路电流法-Excalidraw.excalidraw.md -> 5872 bytes
```

### 第 3 步：替换旧文件

- 删除旧格式 `回路电流法-Excalidraw.excalidraw`（内容已由新文件承接，原件另有备份）；
- 新文件 `<span style="color:#2980b9">回路电流法-Excalidraw.excalidraw.md</span>` 就地落在原目录，与 `回路电流法-CircuitJS.md`、`回路电流法-TikZJax.md`、`回路电流法-双回路电路.drawio.svg` 同目录。

### 第 4 步：更新插件到 2.27.3

从 GitHub Release 下载 2.27.3 的 3 个资产，覆盖安装（**保留 `data.json` 设置**）：

```bash
base="https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/download/2.27.3"
curl -sSL -o main.js       "$base/main.js"        # 4,884,569 bytes
curl -sSL -o manifest.json "$base/manifest.json"  # version 2.27.3
curl -sSL -o styles.css    "$base/styles.css"     # 333,231 bytes
```

> 🛠️ **<span style="color:#2980b9">安装后核对：</span>** 已装 `manifest.json` 版本 = `2.27.3`、`main.js` 内 `PLUGIN_VERSION="2.27.3"`、文件尾正常以 `module.exports=ExcalidrawPlugin;` 结束（确认下载非 HTML 错误页）。

## 技术栈与涉及工具

- **Obsidian**：知识库宿主程序，社区插件体系（`.obsidian/plugins/<id>/` 下 `main.js` + `manifest.json` + `styles.css` + `data.json`）；
- **Excalidraw 插件**（`obsidian-excalidraw-plugin`，作者 Zsolt Viczian）：`.excalidraw`（旧，纯 JSON）与 `.excalidraw.md`（新，Obsidian 笔记内嵌绘图）双格式；
- **LZString**（字符串压缩库，pieroxy 出品）：插件用它把场景 JSON 压成 base64；
- **Node.js 24.15.0 + `lz-string` 包**：本次用于复刻压缩算法并完成格式转换；
- **GitHub Release 资源下载**（`curl -L`）：用于插件版本更新。

## 遇到的问题与坑

- 🕳️ **<span style="color:#e74c3c">压缩算法不是 pako/zlib：**</span>插件内置了 pako，容易先入为主以为绘图用 zlib 压缩；实际 `compressed-json` 块用的是 **LZString.compressToBase64**。识别线索：base64 串以 `===` 三连等号结尾（LZString 余 1 字符的 padding），zlib 不会出现；
- 🕳️ **<span style="color:#e67e22">分块规则别漏：**</span>内容是 base64 按 **256 字符 + `\n\n`** 分段，不是单行长串；解码前要先把 `\n`/`\r` 全部剔除再喂给 LZString；
- 🕳️ **两个 `compatibilityMode` 不是一回事**：源码里的 `compatibilityMode`（扩展名判定）与设置项 `compatibilityMode`（"新绘图存旧格式"开关）同名不同义，别用设置项去压提示；
- 🕳️ **Obsidian 运行中改文件要重启才生效**：插件文件已替换，但 Obsidian 内存里仍是 2.26.4，**必须重启 Obsidian** 才加载 2.27.3；
- 🕳️ **`.trash` 里的旧文件不用管**：Obsidian 不扫描 `.trash`，其中的 `.excalidraw` 不会触发提示，无需迁移。

## 验证结果

- ✅ **转换正确性（三层全过）**：
  - 解压新文件 → 与原 JSON **字节级一致**（`PASS ✅`）；
  - 结构化深度比对 → `PASS ✅`；
  - 与插件样本**结构布局一致** → `PASS ✅`；
- ✅ **提示不再触发**：新文件扩展名 `<span style="color:#e67e22">`excalidraw.md`</span>`，不再命中 `extension === "excalidraw"` 判定；
- ✅ **插件已更新**：已装版本 `2.27.3` = 最新版，`PLUGIN_VERSION` 与 `manifest.json` 双向核对一致；
- 📌 **诚实说明**：以上为**磁盘层验证**；Obsidian 内的实际打开效果需**重启后**由用户确认（见下节）。

## 使用建议与遗留事项

- 🔥 **<span style="color:#e74c3c">立即操作：重启 Obsidian</span>**（或命令面板 → "Reload app without saving"），让插件加载 2.27.3、并让文件树刷新出新格式文件；
- 📌 **重启后首次会弹一次"更新内容"（Release Notes）窗口**：这是插件升级后的标准一次性提示（`previousRelease` 由 2.26.4 变为 2.27.3），看过关掉即可，**不是故障**；
- 💡 **以后一律用新格式**：新建绘图保持 `*.excalidraw.md`（当前设置 `useExcalidrawExtension=true` 已正确）；**不要再手工创建 `*.excalidraw`**，否则兼容提示会再次出现；
- ⚠️ **<span style="color:#e67e22">旧工作区记录已失效：**</span>Obsidian 的 `workspace.json` 仍记着旧路径 `…回路电流法-Excalidraw.excalidraw`，重启后该标签页会自动失效/消失，属正常；需要时打开新文件 `[[回路电流法-Excalidraw.excalidraw]]` 即可；
- 📎 **原件与回滚**：
  - 旧格式原件备份：[查看备份：回路电流法-Excalidraw.excalidraw](总结好的大纲以及笔记/知识库FAQ/原始文件备份/回路电流法-Excalidraw.excalidraw)
  - 插件 2.26.4 回滚包：`F:\Programs\_excalidraw-plugin-backup\obsidian-excalidraw-plugin-2.26.4\`（如需回退，整目录覆盖回 `.obsidian/plugins/obsidian-excalidraw-plugin/`）；
- 📌 **监测对象**：若日后又出现"兼容模式"提示，按本档案**三步走**——`find` 全库 `*.excalidraw` → 用 LZString 转换脚本转成 `.excalidraw.md` → 删除旧文件（保留备份）。

## 🔗 相关笔记

- [[00-报错统计台账]] — 报错统计权威源（本档案为 **F17** 行）
- [[01-Obsidian反复报错Request too large]] — 同属 Obsidian 文件/环境类报错
- [[17-tool_result内嵌伪PNG致API400unsupported-image]] — 同属 Obsidian 插件/文件格式类报错
- [[回路电流法-Excalidraw.excalidraw]] — 本档案修复的对象（已迁移为新格式的绘图）
- [[Obsidian仿真图-制作规范]] — 电工学仿真图制作规范（本次绘图所属场景）
