---
title: "tool_result 内嵌伪 PNG 致 API 400 unsupported image"
type: "知识库 FAQ / 报错记录"
date: 2026-09-02
created: 2026-09-02
updated: 2026-09-02
tags:
  - 报错
  - 知识库FAQ
  - image
  - tool_result
  - API400
  - Claudian
  - 会话
source: "Claudian（realclaudian）插件调用 Claude Code —『创建带 PPT 风格页面的动画 HTML 幻灯片』会话（8197acc5）"
---

# 🖼️ tool_result 内嵌伪 PNG 致 API 400 "unsupported image"

> [!summary] 📊 报错统计速览（截至 2026-09-02）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（2026-09-02 首发 1 次，暂无复发记录）。根因为 **「tool_result 内嵌伪 PNG（图片下载失败文本被包装成 base64 图片）」**。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🧾 tool_result 内嵌伪 PNG（图片下载失败被包装成 base64 图片） | **1** | 17 |
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
❌ Error: unknownAPI Error: 400 messages.10.content.0.tool_result.image[0]: You have uploaded an unsupported image. Please make sure your image is valid and has one of the following formats: webp, png, jpeg, and gif.

❌ Error: Claude Code returned an error result: API Error: 400 messages.10.content.0.tool_result.image[0]: You have uploaded an unsupported image. Please make sure your image is valid and has one of the following formats: webp, png, jpeg, and gif.
```

> **出现时间**：2026-09-02 21:36
> **来源**：Claudian（realclaudian）Obsidian 插件调用 Claude Code CLI。
> **触发场景**：会话「创建带 PPT 风格页面的动画 HTML 幻灯片」（session `8197acc5-dc6e-4693-9aab-a3f9b02ffd5d`）反复弹出该报错，**每次发消息都失败，会话被卡死**。

## 现象描述

在 Obsidian 的 Claudian（realclaudian）面板中，某个会话**反复弹出上述 400 报错**。关键特征：

- 🔥 **<span style="color:#e74c3c">报错指向 `messages.10.content.0.tool_result.image[0]`</span>** ——即重建后的 API 请求里，某条消息的 tool_result 中嵌了一张"**非法图片**"；
- **每一次发送消息都报此错**，会话无法继续推进（永久卡死）；
- 报错由 **Claude Code CLI 本身**输出（插件只是透传显示）；
- 报错列举的合法格式为 `webp / png / jpeg / gif` ——说明**API 校验图片格式失败**，而非文件读取失败。

> 💡 **<span style="color:#2980b9">认知：</span>** 这不是"文件读不出来"，而是**会话历史里有一张"看似图片、实则不是图片"的脏数据**，导致整条会话的每次请求都过不了 API 校验。

## 根本原因

### 核心原因：图片下载失败的文本，被当作 base64 图片塞进了 tool_result

AI 在生成 PPT 页面的某个环节调用了图片下载工具，**源站不可达**。下载工具返回的是一段错误文本 "**Source image is unreachable**"（27 字节），但这段文本**被包装成了 base64 图片**：

```json
{
  "type": "image",
  "source": {
    "type": "base64",
    "data": "U291cmNlIGltYWdlIGlzIHVucmVhY2hhYmxl",   // ← 解码后是 "Source image is unreachable"
    "media_type": "image/png"                          // ← 声明是 PNG，但字节根本不是
  }
}
```

**base64 解码后是文本，不匹配 PNG 文件头签名（`\x89PNG\r\n\x1a\n`）**——API 判定为 "unsupported image"。从此，**该会话每次请求都会把这条含"伪 PNG"的历史重发一遍 → 反复报错，会话被永久卡死。**

### 故障链条

1. 会话中 AI 尝试下载一张图片，**源站不可达**；
2. 工具返回错误文本 "Source image is unreachable"（27 字节）；
3. 该文本**被包装成 base64 图片（media_type=image/png）写入 `tool_result`**（`message.content`）；
4. API 校验图片格式 → **400 unsupported image**；
5. 会话卡死，无法继续。

> ⚠️ **<span style="color:#e67e22">根因归属：</span>** 属**文件/环境类**报错——准确说是**会话数据（.jsonl）内嵌脏图片**。这不是网络/代理问题，也不是硬件环境问题。

## 诊断数据

**定位文件**：`C:\Users\asus\.claude\projects\F-------------\8197acc5-dc6e-4693-9aab-a3f9b02ffd5d.jsonl` 第 **1465** 行。

- `message.content[0]` 为 `tool_result`，其 `content` 为：
  `[{type: "image", source: {type: "base64", data: "U291cmNlIGltYWdlIGlzIHVucmVhY2hhYmxl", media_type: "image/png"}}]`
- 📊 **<span style="color:#e67e22">base64 解码结果</span>**：`U291cmNlIGltYWdlIGlzIHVucmVhY2hhYmxl` → `"Source image is unreachable"`（27 字节），**magic bytes 不匹配 PNG 签名**；
- 顶层 `toolUseResult` 字段同样含脏数据：
  `{type: "image", file: {base64: "U291cmNlIGltYWdlIGlzIHVucmVhY2hhYmxl", type: "image/png", originalSize: 27}}`；
- 第 **1463 行** AI 已自语："The AI image download failed (27 bytes). Let me inspect it and retry with a valid ID." ——与上述 27 字节完全对上；
- 第 **1466 行**正是被记录进 jsonl 的本次 400 报错原文（作为 assistant 消息回显）。

> 🔍 **<span style="color:#e74c3c">全库扫描结论：</span>** 用脚本遍历 `C:\Users\asus\.claude\projects\` 下**所有**会话 jsonl 的 tool_result 图片块，校验 media_type 是否合法 + base64 解码后 magic bytes 是否匹配——**仅此 1 处非法**，其余全部合法，无潜伏同根因会话。

## 修复过程

1. **备份**（硬性安全底线）：复制 `8197acc5-dc6e-4693-9aab-a3f9b02ffd5d.jsonl`（21,015,844 字节）到 `总结好的大纲以及笔记/知识库FAQ/原始文件备份/` 并加 `.bak-20260902` 后缀，确保修复不丢原始数据；
2. **定位**：扫描 jsonl，校验每个 tool_result 图片块，命中第 1465 行（media_type=image/png 但 magic 不符）；
3. **修复 `message.content`**：将该行 `content` 内的非法 image 块**替换为合法 text 块**：
   ```json
   [{"type": "text", "text": "Source image is unreachable — 图片下载失败（27 bytes），并非有效图片，此处为伪 PNG 修正后的占位文本。"}]
   ```
4. **同步修复 `toolUseResult`**：把 `{type:"image", file:{...}}` 改为 `{type:"text", text:"Source image is unreachable — 图片下载失败（27 bytes），伪 PNG 已修正。"}`（否则插件仍可能把它当图片处理）；
5. **写回**：其余行保持原样，仅替换第 1465 行。

> 🛠️ **<span style="color:#2980b9">修复脚本要点：</span>** 读文件后先判断换行符（`\n` 或 `\r\n`）；按行 split → `json.loads` 第 1465 行 → 修改 → `json.dumps(..., ensure_ascii=False)` 替换该行 → 按原换行符 join 写回。

## 技术栈与涉及工具

- **Claudian（realclaudian）Obsidian 插件**：调用 Claude Code CLI 执行会话；
- **会话实际数据**：`C:\Users\<用户名>\.claude\projects\<项目路径>\<session-id>.jsonl`；
- **会话索引**：`.claudian/sessions/conv-*.meta.json`（记录了 sessionId 与标题）；
- **Anthropic Messages API**；图片支持格式仅 `webp / png / jpeg / gif`。

## 遇到的问题与坑

- 🕳️ **<span style="color:#e74c3c">报错下标 ≠ jsonl 行号：</span>** 报错 `messages.10...image[0]` 里的"10"是 **API 重建 messages 数组后的下标**，不是 jsonl 行号。本案例中非法图片实际在第 1465 行，而报错仍标 10——**定位要遍历扫描 tool_result 图片块**，不要被下标误导；
- 🕳️ **必须同时修 `message.content` 与 `toolUseResult`：** 只修 `message.content` 虽然能过 API 校验，但插件可能读 `toolUseResult` 渲染/处理，漏修可能导致后续又把脏数据写回；
- 🕳️ **修复后需让插件重新加载会话：** 插件内存可能缓存旧历史。修复后若仍报错，应**关闭该标签页重新打开**（或重新 resume），让插件从磁盘重建历史。

## 验证结果

- ✅ **第 1465 行修复成功**：`message.content` 已变为 text 块，`toolUseResult` 已变为 text；
- ✅ **全量复检该会话**：1479 行全部可解析（0 行 parse 失败）；tool_result 图片块 **69 个全部合法**；非法图片 **0 个**；
- ✅ **全库扫描**：所有会话 jsonl 的 tool_result 图片全部合法，**无同类潜伏会话**；
- 📌 **诚实说明**：本会话为**历史已卡死**的会话，修复的是"磁盘上的历史数据"。**插件内存中的旧状态需重新加载后才会生效**（见使用建议）。

## 使用建议与遗留事项

- 🔥 **<span style="color:#e74c3c">立即操作：</span>** 若该「创建带 PPT 风格页面的动画 HTML 幻灯片」会话仍报错，**关闭其标签页后重新打开**（或重新 `resume`），让插件从修复后的磁盘 jsonl 重建历史即可恢复；
- 💡 若该会话语义已因卡死而混乱，**直接新建会话**重新执行该任务更省事；
- ⚠️ **<span style="color:#e67e22">根因预防：</span>** 这是"图片下载失败文本被包装成图片"的 bug——遇到 `API 400 unsupported image`，**优先按本档案定位**：扫描会话 jsonl 的 tool_result 图片块，校验 media_type + magic bytes；
- 📌 **监测对象**：Claudian 在"生成/下载图片"场景失败时，可能再次产生同类伪图片；后续遇同类报错按本档案处理，并将"伪 PNG 清洗"纳入常规体检手段。

## 🔗 相关笔记

- [[00-报错统计台账]] — 报错统计权威源（本档案为 F15 行）
- [[03-Claudian会话ID未找到（双机同步）]] — 同属 Claudian 会话数据问题（meta 与 jsonl 分离）
- [[01-Obsidian反复报错Request too large]] — 同系列文件类报错
- [[02-后台任务UUID引用悬空]] — 同属会话体系问题
