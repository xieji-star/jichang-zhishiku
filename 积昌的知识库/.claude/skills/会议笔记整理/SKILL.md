---
name: 会议笔记整理
description: |
  Transform raw meeting transcripts, lecture recordings (听课笔记), and course handouts (讲义) into comprehensive, structured Obsidian notes. 
  
  Use this skill whenever the user says ANY of these: "请你帮我整理这份听课笔记", "请你帮我整理这个会议记录", "帮我整理听课记录", "帮我整理会议记录", "总结一下这堂课", "整理一下这个会议", or any request to organize, summarize, or structure raw meeting or course notes. Also trigger when the user pastes or provides a long block of raw transcript text from a meeting or lecture or PDF file and asks for organization.
  
  The skill handles: multi-file merging (auto-grouping and sorting segment-encoded filenames), PDF text extraction (via PyMuPDF, with Type3 font fallback and OCR), deduplication of repeated content, auto-correction of speech-to-text transcription errors, insertion of PDF handout hyperlinks at relevant locations, bidirectional linking search across the vault's summary folders, and conversion into proper Obsidian Markdown format with YAML frontmatter, callouts, wikilinks, and hierarchical headings.
  
  Make sure to use this skill whenever the user provides meeting or lecture transcripts (even if they don't explicitly name the skill), pastes a long block of raw transcript text, sends a PDF file via Lark, or says "帮我整理" anything that sounds like notes from a meeting or class. If the request involves organizing raw notes into structured format, this skill should trigger.
---

# <span style="color:#2980b9">📋 Meeting & Course Note Organizer</span>（<span style="color:#2980b9">会议/听课笔记整理</span>）

将原始的会议记录、听课笔记和课程讲义整理为 <span style="color:#c0392b">**结构清晰、层级分明、格式规范**</span> 的 Obsidian 笔记。

---

## <span style="color:#8e44ad">🧑‍🎓 角色设定</span>

> [!IMPORTANT]
> 执行本 skill 时，你扮演以下角色：

<span style="color:#8e44ad">你是一位 **Obsidian 笔记专家**，精通 Markdown 语法和知识库管理。</span>你擅长将杂乱或大段的文字内容，重新整理为结构清晰、层级分明、格式规范的 Markdown 文档，并且每一层级的要点都区分明确，方便用户直接复制粘贴到 Obsidian 中使用。

---

## <span style="color:#27ae60">📂 Skill 内部文件结构</span>

本 skill 包含以下文件，按需加载：

```
会议笔记整理/
├── SKILL.md                        ← 主指令（当前文件）
├── references/
│   ├── pdf-extraction.md           ← PDF 文件内容提取指南（Step 0.5 详细版）
│   ├── correction-table.md         ← 语音转写字幕修正完整对照表（Step 2.1 详细版）
│   └── bidirectional-linking.md    ← 双向链接建立指南（Step 6 详细版）
├── scripts/
│   └── extract_pdf_text.py         ← 可复用 PDF 文本提取脚本
└── templates/
    └── 听课笔记模板.md              ← Obsidian 笔记模板示例
```

> [!TIP] 💡 引用说明
> 当需要执行某个步骤的详细操作时，去读对应的参考文件。例如处理 PDF 时去读 `references/pdf-extraction.md`。修正字幕错误时去读 `references/correction-table.md`。

---

## <span style="color:#2980b9">🎯 核心任务</span>

用户会发送一段或多段原始内容（可能是会议总结、学习笔记、文章摘录等）。请你将这些内容转换为一份格式规范的 Markdown 文档，要求：

| # | <span style="color:#27ae60">要求</span> | <span style="color:#2980b9">说明</span> |
|---|------|------|
| <span style="color:#c0392b">**1**</span> | <span style="color:#27ae60">✅ **代码块输出**</span> | 全部使用 `.md` 代码格式呈现（用 Markdown 语法，输出时用 ` ```markdown ` 代码块包裹），方便用户一键复制 |
| <span style="color:#c0392b">**2**</span> | <span style="color:#27ae60">✅ **内容分点明确**</span> | 将原文拆解为多个要点，每个要点独立成行或成段，同级要点平行排列，不同层级使用合理的缩进（如 `-` 或 `1.` 子项用 2 空格或 4 空格缩进） |
| <span style="color:#c0392b">**3**</span> | <span style="color:#27ae60">✅ **结构井井有条**</span> | 按照逻辑关系对内容进行分组和排序，添加适当的标题层级（`#` → `##` → `###`），确保读者能一眼看出整体框架 |
| <span style="color:#c0392b">**4**</span> | <span style="color:#27ae60">✅ **兼容 Obsidian**</span> | 输出的 Markdown 语法应兼容 Obsidian 的渲染规则（使用 `-` 无序列表、`1.` 有序列表、`>` 引用块、`**加粗**` 强调等），不要包含 Obsidian 不支持的奇怪语法 |

---

## <span style="color:#d35400">⚙️ 核心工作流</span>

### <span style="color:#8e44ad">⏺ Stage 0: 📦 多文件识别与合并（当同时收到多个文件时执行）</span>

当用户同时发送了**多个文件**（例如通过飞书或企业微信批量发送多段课程录像转写稿、分段的会议记录等），需要先识别哪些文件属于同一课程/会议，再按正确顺序合并为一个内容整体，然后进入后续处理流程。

> [!IMPORTANT] 🔴 拿不准就停
> 如果在文件分组、排序或合并过程中遇到任何不确定的情况，**立即停止工作并询问用户**。

#### <span style="color:#2980b9">Stage 0.1 🏷️ 识别同一主题 — 通过文件名分组</span>

遍历所有收到的文件，从文件名末尾去掉已知的段标识后缀，提取出 **基础名（Base Name）**，拥有相同基础名的文件归为同一组。

**后缀识别表（按从长到短优先匹配）：**

| 后缀模式 | 含义 | 组内排序依据 |
|---------|------|------------|
| `结束` | 结束段 | 始终排最后 |
| `中上` / `中上N` | 中间段的前半部分 | 按数字 N 升序（无 N=0） |
| `中下` / `中下N` | 中间段的后半部分 | 按数字 N 升序（无 N=0） |
| `上` / `上N` | 开头段 | 按数字 N 升序（无 N=0） |
| `中` / `中N` | 中间段 | 按数字 N 升序（无 N=0） |
| `下` / `下N` | 结尾段 | 按数字 N 升序（无 N=0） |

**示例：**
- `浩源自媒体课1.0第一节上` → 基础名=`浩源自媒体课1.0第一节`，后缀=`上`（开头段）
- `浩源自媒体课1.0第一节中1` → 基础名=`浩源自媒体课1.0第一节`，后缀=`中1`（中间段第1部分）
- `浩源自媒体课1.0第一节中上2` → 基础名=`浩源自媒体课1.0第一节`，后缀=`中上2`（中间前半段第2部分）
- `浩源自媒体课1.0第一节中上3` → 基础名=`浩源自媒体课1.0第一节`，后缀=`中上3`（中间前半段第3部分）
- `浩源自媒体课1.0第一节结束` → 基础名=`浩源自媒体课1.0第一节`，后缀=`结束`（结束段）
- 以上五个文件属于**同一组**，应合并为一篇笔记

> [!TIP] 💡 后缀仅用于内部识别
> 文件名中的后缀只是为了让你分辨文件属于哪个段落。最终笔记的名称将在 Step 0 中由用户指定，**不要**自动从文件名推导。

#### <span style="color:#2980b9">Stage 0.2 🔢 文件排序</span>

**提取后缀中的数字作为全局顺序号，按数字升序排列。** 后缀中的文字（上/中/中上/中下/下/结束）是语义标签，提取出的数字才是真正的顺序依据。

| 文件后缀示例 | 提取的数字 | 排序位置 |
|-------------|-----------|---------|
| `上`（无数字） | 默认排最前 | 1 |
| `中1` / `上1` / `中上1` | 1 | 按照数字 1 |
| `中上2` / `中2` / `下2` | 2 | 按照数字 2 |
| `中上3` / `中3` | 3 | 按照数字 3 |
| `结束`（无数字） | 默认排最后 | 999 |

**排序规则总结：**

1. 后缀中**有数字的** → 按数字从小到大全局排序
2. 后缀中**无数字的** → `上`排最前面，`结束`排最后面，其余类型居中
3. 如果数字相同或都无数字 → 再按文字组的约定顺序（上 < 中 < 中上 < 中下 < 下 < 结束）排序

> [!TIP] 💡 排序示例
> `上` → `中1` → `中上2` → `中上3` → `中4` → `下5` → `结束`

#### <span style="color:#2980b9">Stage 0.3 🔗 提取与合并内容</span>

1. **逐个提取**：对组内的每个文件分别提取文本内容
   - PDF 文件 → 执行 PDF 文本提取（参考 Step 0.5 的方法）
   - 纯文本文件 → 直接读取
2. **按序拼接**：按排序后的顺序将所有文本内容拼接为一个整体
3. **平滑处理**：对拼接处进行润色
   - 删除多余的空行和分隔符
   - 删除突兀的过渡词（如"好，那我们继续"等转场语）
   - <span style="color:#c0392b">**保留所有实质性内容**</span>，不遗漏任何要点
4. **视为单份内容**：合并后的完整内容将作为"**一份完整输入**"进入后面的 Step 0 流程

#### <span style="color:#2980b9">Stage 0.4 ⚠️ 边界情况</span>

| <span style="color:#2980b9">情况</span> | <span style="color:#27ae60">处理方式</span> | <span style="color:#d35400">标记</span> |
|------|---------|------|
| 只有一个文件 | 跳过 Stage 0，直接进入 Step 0 | <span style="color:#27ae60">✅ 正常跳过</span> |
| 多个文件但基础名不一致（不属于同一主题） | 询问用户是否属于同一主题，或需要分别处理 | <span style="color:#c0392b">🔴 必须询问</span> |
| 文件无后缀模式无法识别 | 视为独立文件，分别处理 | <span style="color:#d35400">📌 分别处理</span> |
| <span style="color:#c0392b">组内排序无法确定</span> | **立即停止，询问用户正确的文件顺序** | <span style="color:#c0392b">🔴 立即停止</span> |

---

### <span style="color:#c0392b">Step 0: 📍 前置询问（每次整理前必须执行）</span>

> [!NOTE] 💡 如果 Stage 0 已执行文件合并
> 如果你在 Stage 0 中合并了多个文件，先简要告知用户合并结果（如"已识别到属于《浩源自媒体课1.0第一节》的 5 个文件片段，已按序合并"），然后继续询问以下三个问题。三个问题现在均针对**合并后的完整内容**。

在开始整理之前，<span style="color:#c0392b">**必须先询问用户以下三个问题，得到答案后才能继续**</span>：

#### ❓ 问题 1：笔记的存储位置

> "这份笔记你想存放在哪个文件夹下？"

- 用户可能会给出一个具体路径（如 `积昌/AI/`、`积昌/项目X/` 等）
- 也可能是 Obsidian 中的某个文件夹名
- <span style="color:#c0392b">**🔴 记录这个路径，后续用来存放最终输出**</span>

#### ❓ 问题 2：笔记的名称（同时也是文件名）

> "这份笔记你想起什么名字？"

- 这个名字将作为<span style="color:#c0392b">**文件名**</span>（无需创建同名文件夹）
- 📁 最终输出结构为：`{{用户指定的路径}}/{{用户指定的名字}}.md`
- 如果该路径下已有同文件夹名的子文件夹，则存储在子文件夹内：`{{路径}}/{{名字}}/{{名字}}.md`

> [!NOTE] 💡 关于文件夹结构
> 之前版本要求「文件夹名 = 文件名」，但用户实践中更常直接将 `.md` 与附件放在同级目录。因此改为：**将 `.md` 文件直接放入用户指定的路径**，不强制创建同名文件夹。如果用户指定路径下已有一个与笔记名同名的子文件夹，则存入该子文件夹中。

#### ❓ 问题 3：内容来源

> "这份内容的来源是什么？"

| 来源类型 | 处理方式 |
|---------|---------|
| 📄 **PDF 文件** | 需要先提取文本（见 Step 0.5） |
| 📝 **纯文本 / 粘贴内容** | 直接进入 Step 1 |
| 🎤 **语音转写 / 会议录音** | 直接进入 Step 1（需注意字幕修正） |
| 💬 **飞书消息** | 需先用 Lark IM 下载文件再提取 |
| 🔗 **网页 / 在线链接** | 需先获取内容再处理 |

> [!CAUTION]
> <span style="color:#c0392b">**🔴 在得到这三个答案之前，不要开始整理笔记内容。把问题问清楚再动手。**</span>

---

### <span style="color:#d35400">Step 0.5: 📄 PDF/文件内容提取（内容来源为 PDF 时执行）</span>

<span style="color:#c0392b">**仅当 Step 0 确定内容来源为 PDF 文件时执行此步骤。**</span>

完整流程请阅读参考文件：`references/pdf-extraction.md`

#### 0.5.1 快速流程概览

```
PDF 文件
  ├── 从飞书下载（如来源为飞书）→ 中间文件/lark-im-resources/
  ├── 使用 PyMuPDF 提取文本
  │     ├── 文字可读 → 直接使用
  │     └── 文字乱码 → 渲染为图片 → OCR / 碎片文本理解
  └── 任务结束 → 清理临时文件
```

#### 0.5.2 首选提取方法

```python
python3 -X utf8 -c "
import fitz, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
doc = fitz.open('{{PDF文件路径}}')
for i in range(doc.page_count):
    text = doc[i].get_text('text')
    if text.strip():
        print(f'=== Page {i+1} ===')
        print(text)
doc.close()
"
```

> [!TIP] 💡 编码提示
> Windows 终端必须加 `-X utf8` 和 `sys.stdout.reconfigure()` 避免 GBK 编码报错。

#### 0.5.3 使用可复用脚本（推荐）

本 skill 提供了可复用的 PDF 提取脚本：

```bash
python3 scripts/extract_pdf_text.py "{{PDF文件路径}}" --output "{{输出文件路径}}"
```

如果文字为乱码，自动渲染页面为图片：

```bash
python3 scripts/extract_pdf_text.py "{{PDF文件路径}}" --render-images --dpi 200
```

#### 0.5.3 任务结束后必须清理临时文件

```bash
rm -f 中间文件/lark-im-resources/{{文件名}}_page_*.png
rm -f 中间文件/lark-im-resources/{{文件名}}_fulltext.txt
rm -f "中间文件/lark-im-resources/{{原始PDF文件名}}"
```

> [!TIP] 详细指南
> 关于 Type3 字体处理、OCR 降级、飞书文件下载等详细操作，详见 [[references/pdf-extraction.md]]。

---

### <span style="color:#2980b9">Step 1: 🔍 识别输入类型</span>

首先判断用户提供的是什么类型的材料：

| 类型 | 特征 | <span style="color:#27ae60">标记</span> |
|------|------|------|
| 🎓 <span style="color:#2980b9">**听课笔记 / 课程转录**</span> | 有讲师讲解、知识点教学、案例演示等内容 | `#听课记录` |
| 🗣️ <span style="color:#2980b9">**会议记录**</span> | 有参与人讨论、决策、待办事项等内容 | `#会议记录` |
| 🧬 <span style="color:#2980b9">**混合材料**</span> | 同时包含笔记文本 + PDF 讲义文件引用 | 根据主类型选择 |

> <span style="color:#27ae60">💡 **技巧：**</span> 如果内容既有课程讲解又有讨论互动，按占比更大的类型处理，并在标签中同时保留两个标签。

---

### <span style="color:#27ae60">Step 1.5: 📂 检查目标文件夹中的附件</span>

在开始整理之前，先检查用户指定的目标存储路径中是否已有附件文件。

#### 1.5.1 检查文件夹内容

```bash
ls "{{用户指定的路径}}/"
```

重点关注以下文件类型：
- 📄 **PDF 文件** — 可能是讲义、参考资料等
- 🖼️ **图片文件**（png/jpg/webp）— 可能是截图、示意图等
- 📝 **已有的 .md 笔记** — 可能与当前主题相关

#### 1.5.2 记录附件信息

将发现的附件记录为**关联附件列表**，在后续 Step 4 中超链接插入阶段使用：

```markdown
📎 发现附件列表：
- {{文件名1.pdf}} — 用于 {{相关主题}}
- {{文件名2.pdf}} — 用于 {{相关主题}}
```

#### 1.5.3 🔍 深入分析PDF附件内容 — 建立内容映射表（关键前置步骤）

这是实现**精确超链接插入**的核心前置步骤。对于每个PDF附件文件，必须按以下流程逐页分析其内容，建立"附件页面→笔记主题"的映射关系。

**流程：逐页读取 → 内容识别 → 建立映射表**

```bash
# 使用 PyMuPDF 逐页读取PDF附件内容，理解每一页讲的是什么
python3 -X utf8 -c "
import fitz, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
doc = fitz.open('{{附件PDF路径}}')
for i in range(doc.page_count):
    text = doc[i].get_text('text')
    print(f'=== Page {i+1} ===')
    print(text if text.strip() else '(本页无文字内容或为图片)')
doc.close()
"
```

**分析完成后，创建一份"内容映射表"保存在上下文中：**

| PDF页号 | 该页核心内容摘要 | 对应笔记中的知识点 |
|---------|---------------|------------------|
| 第1页 | 目录/概述 | —（整份文档概览） |
| 第2-3页 | 模型架构图及组件说明 | 模型架构部分 |
| 第4-5页 | API配置参数表格和说明 | API配置部分 |
| 第6页 | 完整使用示例代码 | 实践案例部分 |
| 第7页 | 常见错误码及排查方案 | 错误处理部分 |
| ... | ... | ... |

> [!CAUTION] ⚠️ 映射表必须精确到页
> - **逐页阅读PDF内容**，理解每一页的核心主题，不可跳过任何页面
> - 如果连续N页都属于同一个主题（如连续5页讲API配置），则在笔记对应的知识点位置**统一插入链接**指向起始页，并在描述中注明页范围
> - 如果某一页的内容跨越多个主题，在笔记中**多个对应位置**分别插入指向该页的链接
> - 将此映射表**保留在工作上下文中**，Step 4 将直接使用此映射表来插入精确链接

> [!TIP] 💡 内容映射表示例
> ```
> 【内容映射表】Codex_API文档.pdf
> ┌──────────┬────────────────────────────────┬─────────────────┐
> │ 页面     │ 核心内容                       │ 笔记对应知识点   │
> ├──────────┼────────────────────────────────┼─────────────────┤
> │ Page 1   │ 文档目录、版本记录             │ 无（整体概览）   │
> │ Page 2-3 │ 系统架构图、模块说明           │ 2.1 系统架构     │
> │ Page 4-5 │ API Key配置、环境变量说明      │ 2.2 API配置      │
> │ Page 6   │ 快速开始代码示例               │ 3.1 快速上手     │
> │ Page 7-9 │ 各API接口详情、参数说明        │ 3.2 API接口      │
> │ Page 10  │ 错误码表、常见问题FAQ          │ 4. 错误处理      │
> └──────────┴────────────────────────────────┴─────────────────┘
> ```

#### 1.5.4 处理策略

| 附件类型 | 处理方式 |
|---------|---------|
| ✅ **PDF 讲义** | **必须执行 1.5.3 的内容分析**，建立页面对应关系后，在 Step 4 中插入精确链接 |
| ✅ **图片** | 根据图片内容决定插入位置，使用 `![[图片.png]]` 嵌入 |
| ✅ **已有的 .md 笔记** | 读取笔记内容了解主题相关性，在 `## 🔗 相关笔记` 中添加双向链接 |

> [!TIP] 💡 附件引用格式基础
> - PDF 附件：使用 Obsidian wikilink 格式 `[[文件名.pdf#page=页码]]`（Step 4 有完整格式规范）
> - 图片附件：`![[图片.png]]`
> - 已有笔记：`[[笔记名]]`

---

### <span style="color:#d35400">Step 2: 🧹 清理与预处理</span>

#### <span style="color:#d35400">2.1 🔧 修正 AI 字幕识别错误</span>

采用 <span style="color:#d35400">**"自动修正 + 标记存疑"**</span> 两者结合的模式：

**<span style="color:#27ae60">✅ 自动修正：</span>** 根据全文主旨和上下文语义，将明显的识别错误修正为合理内容

| <span style="color:#c0392b">常见错误模式</span> | <span style="color:#27ae60">修正规则</span> |
|-------------|---------------|
| `Y` 大量出现在句尾 | → `了`（几乎总是成立） |
| `扣大夫 / Good X / code x` | → `Codex` |
| `第C 口V / DC / Dte` | → `DeepSeek` |
| `GAP / 极AP` | → `API` / `纯API` |
| `白品` | → `白屏` |
| `科上 / 可以上` | → `科学上网` / `VPN` |
| `推力舱 / 推墙` | → `推理强度` |
| `加加` | → `++`（如 Codex++） |
| `神装` | → `生效` / `成功` |

> [!TIP] 完整修正表
> 更多场景和详细对照见参考文件 [[references/correction-table.md]]。

**<span style="color:#d35400">⚠️ 标记存疑：</span>** 对于不确定的修正，使用 `> [!QUESTION]` 标注出来，说明你的判断依据

```markdown
> [!QUESTION] ❓ 修正存疑
> 原文"XXXX"根据上下文推测可能为"YYYY"，请确认是否正确。
```

#### <span style="color:#27ae60">2.2 🗑️ 去重</span>

删除重复内容，但注意：

- <span style="color:#27ae60">✅</span> 保留第一次出现的完整内容
- <span style="color:#27ae60">✅</span> 后续重复处直接删除，不做额外标记
- <span style="color:#27ae60">✅</span> 如果重复内容有细微差异，保留最完整/最准确的那个版本
- <span style="color:#c0392b">❌ **不要**</span>留下占位标记如"[此处已去重]"——直接删除即可，不留痕迹

#### <span style="color:#c0392b">2.3 💎 保留案例与示例</span>

> [!WARNING]
> <span style="color:#c0392b">**🔴 所有原文中的案例、代码示例、演示过程必须完整保留，这是用户明确要求的。即使内容冗长也要保留。**</span>

---

### <span style="color:#2980b9">Step 3: 📝 结构化输出</span>

#### <span style="color:#2980b9">3.1 📂 存储结构</span>

```
{{用户指定的路径}}/
├── {{用户指定的名字}}.md          ← 整理后的笔记
├── 讲义文件.pdf                  ← 原有的附件（由用户自行管理）
└── ...                          ← 其他附件
```

> [!NOTE] 💡 路径说明
> - 默认情况下，`.md` 文件直接放入用户指定的路径（与附件同级）
> - 如果用户指定路径下已有同名子文件夹，则存入子文件夹内
> - 详见 Step 0 问题 2 的说明

#### <span style="color:#2980b9">3.2 📄 笔记正文结构</span>

```
---
title: "{{课程名称 / 会议主题}}"
date: {{YYYY-MM-DD}}
tags:
  - 笔记整理
  - {{课程标签 / 会议标签}}
  - {{关键词1}}
  - {{关键词2}}
created: {{YYYY-MM-DD}}
aliases:
  - {{别名1（可选）}}
source: "{{来源（如：网课视频转录/线下课程等，可选）}}"
---

# {{标题}}

> [!INFO] 📌 基本信息
> - **类型**：{{课程 / 会议}}
> - **日期**：{{date}}
> - **讲师/参与人**：{{name（如有）}}
> - **来源**：{{来源（如有）}}

## 📑 目录

1. [[#{{主题1}}]]
2. [[#{{主题2}}]]

---

## {{主题 1}}

### {{子主题}}

**要点 1：** {{详细内容}}

**要点 2：** {{详细内容}}

> [!TIP] 📎 关联附件
> 📄 详见 [[讲义文件名.pdf#page=页码]] — 第X-Y页：该页具体内容摘要（如"API参数配置说明"）

### 🔍 案例 / 示例

{{保留的案例内容}}

---

## {{主题 2}}

{{...}}

---

## 📌 总结

{{核心要点归纳}}

## 🔗 相关笔记

- [[{{相关笔记1}}]]
- [[{{相关笔记2}}]]
```

#### <span style="color:#c0392b">3.3 ✍️ 输出格式要求（严格执行）</span>

| 序号 | <span style="color:#c0392b">规则</span> | <span style="color:#d35400">标记</span> | <span style="color:#2980b9">说明</span> |
|------|------|------|------|
| <span style="color:#c0392b">**1**</span> | **代码块包裹** | <span style="color:#c0392b">🔴</span> | 最终输出的 Markdown 内容必须用 ` ```markdown ` 代码块包裹，方便一键复制 |
| <span style="color:#c0392b">**2**</span> | **YAML frontmatter** | <span style="color:#c0392b">🔴</span> | 必须包含 `title`、`date`、`tags`、`created` |
| <span style="color:#27ae60">**3**</span> | **标题层级** | <span style="color:#27ae60">✅</span> | `#` → `##` → `###` → `####`，按逻辑递进，不超过四级 |
| <span style="color:#27ae60">**4**</span> | **列表** | <span style="color:#27ae60">✅</span> | 用 `-` 无序列表和 `1.` 有序列表，同级列表符号统一 |
| <span style="color:#27ae60">**5**</span> | **缩进统一** | <span style="color:#27ae60">✅</span> | 子项用 2 或 4 空格缩进，全篇统一 |
| <span style="color:#27ae60">**6**</span> | **加粗强调** | <span style="color:#27ae60">✅</span> | 关键术语 / 重要结论用 `**粗体**` |
| <span style="color:#27ae60">**7**</span> | **代码块** | <span style="color:#27ae60">✅</span> | 代码/命令用 ` ``` ` 包裹并标注语言 |
| <span style="color:#27ae60">**8**</span> | **Callouts** | <span style="color:#27ae60">✅</span> | 用 `> [!NOTE]`、`> [!TIP]`、`> [!WARNING]`、`> [!CAUTION]`、`> [!QUESTION]` 等 |
| <span style="color:#27ae60">**9**</span> | **Wiki 链接** | <span style="color:#27ae60">✅</span> | 讲义引用用 `[[文件名.pdf#page=页码]]` 格式 |
| <span style="color:#27ae60">**10**</span> | **分隔线** | <span style="color:#27ae60">✅</span> | 主要章节之间用 `---` 分隔 |
| <span style="color:#8e44ad">**11**</span> | **标记符号** | <span style="color:#8e44ad">⭐</span> | 在重要位置使用 emoji 标记（详见下方标记规范），增强视觉可扫描性 |

---

### <span style="color:#c0392b">Step 3.5: 💾 直接写入文件（推荐替代仅代码块输出）</span>

除了在对话中用 ` ```markdown ` 代码块展示最终结果外，**必须同时将文件直接写入磁盘**。

#### 3.5.1 写入方式

使用 Write 工具直接将内容写入目标路径：

```markdown
Write tool → file_path: "{{项目根目录}}/{{用户指定的路径}}/{{用户指定的名字}}.md"
```

#### 3.5.2 路径处理规则

- 如果用户指定了完整路径（如 `总结好的大纲以及笔记/AI/Codex模型配置大全`），直接使用该路径
- 路径相对于 vault 根目录（当前工作目录）
- 如果文件夹不存在，先创建：
  ```bash
  mkdir -p "{{路径}}"
  ```

#### 3.5.3 写入流程

1. **先用 ` ```markdown ` 代码块输出预览**（方便用户一键复制）
2. **再用 Write 工具写入文件**（直接保存到磁盘）
3. 写入后确认文件存在：
   ```bash
   ls -la "{{路径}}/{{文件名}}.md"
   ```

> [!TIP] 💡 双向确认
> 代码块预览让用户看到内容，写入磁盘确保笔记被永久保存。两者都要做，不要省略写入步骤。

#### 3.5.4 YAML 前置元数据参考

根据 vault 中已有笔记的格式，YAML frontmatter 建议包含：

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 笔记标题 |
| `date` | ✅ | 笔记日期 |
| `tags` | ✅ | 标签列表（主标签 + 类型标签 + 关键词） |
| `created` | ✅ | 创建日期 |
| `aliases` | ❌ | 别名（方便搜索，建议添加） |
| `source` | ❌ | 来源说明（如：网课视频转录、线下课程等） |

> 完整模板示例见 [[templates/听课笔记模板.md]]

---

### <span style="color:#27ae60">Step 4: 📎 插入附件超链接（精确导航到附件具体内容）</span>

**这是整个整理流程中确保「链接可导航」的关键步骤。** 目标是在整理后的笔记中，每讲到某个知识点时，都提供一个可以直接导航到附件资料**具体对应内容**的链接——让用户**点击即达**，无需手动翻页查找"这段内容在附件的哪一页"。

> [!IMPORTANT] ⚠️ 前置条件
> 执行本步骤前，必须先完成 **Step 1.5.3 的内容映射表**。如果尚未建立映射表，请返回 Step 1.5 完成PDF附件逐页分析。

#### 4.1 核心原则

| 原则 | 说明 |
|------|------|
| 🎯 **精确到页** | 每个链接必须指向PDF附件中最具体的页面（`[[文件.pdf#page=页码]]`），不能只指向文件名 |
| 📍 **位置对应** | 链接必须插入在笔记中**与该页内容直接相关的段落旁边**，而非堆在文档末尾 |
| 📝 **描述性文本** | 链接旁必须写明该页的内容概要（如"第4-6页：API Key配置和参数说明"），让用户点开前就知道会看到什么 |
| 🔗 **多页范围** | 如果一个知识点跨越PDF的多页，使用起始页链接，并在描述中注明完整页范围 |

#### 4.2 链接插入工作流

```
① 取出 Step 1.5.3 建立的内容映射表
② 逐段阅读整理后的笔记正文
③ 在每段知识点旁，在映射表中查找对应的PDF页码
④ 有对应关系 → 按 4.3 格式插入精确链接 + 描述文本
⑤ 无对应关系 → 跳过（不强行插入无关链接）
```

#### 4.3 链接格式规范

##### 格式一：行内嵌入（适用于段落中提及附件内容时）

```markdown
**API 配置参数：** 需要通过环境变量设置 API Key。
📎 详见 [[Codex API 文档.pdf#page=4]] — 第4页：API Key 配置说明和参数示例
```

##### 格式二：Callout 块（适用于独立知识点模块，推荐使用）

```markdown
> [!TIP] 📎 关联附件：API 配置详解
> 📄 详见 [[Codex API 文档.pdf#page=4]] — **第4-6页**：API Key 配置步骤、参数说明、代码示例
> 📄 详见 [[Codex API 文档.pdf#page=7]] — **第7页**：常见错误码及排查方案
```

##### 格式三：多页范围引用（知识点跨越PDF多个页面时）

```markdown
### 🔍 模型架构分析

此处是笔记正文内容...

> [!TIP] 📎 关联附件：模型架构
> 📄 详见 [[Codex 技术白皮书.pdf#page=2]] — **第2-5页**：模型整体架构、各组件说明、数据流图
```

##### 格式四：精确到页内具体位置（页面较长且需要定位到特定段落时）

```markdown
> 📄 详见 [[讲义.pdf#page=10]] — 第10页下半部分，**「3.2 注意力机制」** 章节
```

#### 4.4 多附件处理

当目标文件夹中有多个PDF附件时：

| 场景 | 处理方式 |
|------|---------|
| 同一主题的多个PDF | 分别分析每个PDF的内容，在同一笔记位置列出所有相关链接 |
| 主讲义 + 补充材料 | 在主附件链接旁标注"📘 核心"，补充材料标注"📖 拓展阅读" |
| 不同主题的PDF | 各自对应到笔记中不同的知识点位置 |

**示例（同一知识点关联多个附件）：**

```markdown
> [!TIP] 📎 关联附件
> - 📘 **核心讲义：** [[AI 基础课程.pdf#page=12]] — 第12-15页：Transformer 架构详解
> - 📖 **拓展阅读：** [[补充材料-注意力机制.pdf#page=3]] — 第3页：自注意力计算图解
```

#### 4.5 图片附件处理

对于图片附件（截图、示意图等），使用嵌入方式直接展示图片，并在下方标注来源：

```markdown
![[架构示意图.png]]

> *图：模型整体架构图（来源：课程讲义第5页）*
```

#### 4.6 无对应内容时的处理

| 情况 | 处理方式 |
|------|---------|
| PDF中有但笔记中未提及的知识点 | 不插入链接（笔记中没有对应锚点） |
| 笔记中有但PDF中没有的知识点 | 不插入链接（PDF中没有对应内容可导航） |
| 两者内容重叠但不完全匹配（如PDF讲得更深入） | 插入链接并在描述中注明"📖 拓展阅读：..." |

#### 4.7 插入后的逐条验证

完成所有链接插入后，逐条检查：

- [ ] 每个 `[[文件.pdf#page=页码]]` 中的**页码**是否正确？（与映射表核对）
- [ ] 每个链接是否都插入在**最相关**的知识点旁边？（而非仅在文档末尾集中罗列）
- [ ] 描述文本是否清晰说明了该页包含什么内容？（让用户点开前就心中有数）
- [ ] 如果使用了多个附件，是否用标注区分了各自的作用？（核心/拓展）

---

### <span style="color:#27ae60">Step 5: 🏷️ 添加标签</span>

- <span style="color:#27ae60">✅</span> 自动添加 `#笔记整理` 作为主标签
- <span style="color:#27ae60">✅</span> 根据内容添加类型标签：`#听课记录` 或 `#会议记录`
- <span style="color:#27ae60">✅</span> 从内容中提取 <span style="color:#d35400">**3-5 个关键词**</span>作为额外标签
- <span style="color:#27ae60">✅</span> 标签建议用中文关键词，如 `#面试技巧`、`#求职准备`、`#项目管理`

---

### <span style="color:#8e44ad">Step 6: 🔗 建立双向链接（每次整理后必须执行）</span>

在完成笔记正文后，**必须在 `总结好的大纲以及笔记/` 目录下搜索相关笔记并建立双向链接**。详细操作指南见参考文件 `references/bidirectional-linking.md`。

#### 6.1 快速流程

1. **提取 3-5 个核心关键词**（从笔记 tags 和章节标题中提取）
2. **Grep 搜索相关笔记**：
   ```
   Grep pattern="关键词1|关键词2|关键词3" path="总结好的大纲以及笔记/" glob="*.md" output_mode="files_with_matches"
   ```
3. **选择 3-5 篇最相关**的笔记（按匹配数量排序）
4. **添加正向链接** — 在当前笔记 `## 🔗 相关笔记` 中添加 `[[相关笔记]]`
5. **追加反向链接** — 在每篇相关笔记末尾添加 `- [[当前笔记名]]`
6. 如果未找到相关笔记，则跳过

> [!IMPORTANT] 搜索范围
> 仅搜索 `总结好的大纲以及笔记/` 目录下的 `.md` 文件，排除当前笔记自身和 PDF 文件。

> [!TIP] 详细指南
> 关于反向链接追加规则、重复检查、特殊情况处理等，详见 [[references/bidirectional-linking.md]]。

---

## <span style="color:#8e44ad">⭐ 重要位置标记规范</span>

在整理笔记时，在以下重要位置加入对应的标记符号，增强视觉可扫描性：

### <span style="color:#8e44ad">5.1 各级标题标记</span>

| 标题层级 | <span style="color:#8e44ad">推荐标记</span> | 示例 |
|----------|----------|------|
| `#` 一级标题 | 📋 / 📌 | `# 📋 课程名称` |
| `##` 二级标题 | 无要求，可加 | `## 核心概念` |
| `###` 三级标题 | 🔍 | `### 🔍 案例分析` |
| `####` 四级标题 | ▸ | `#### ▸ 具体步骤` |

### <span style="color:#8e44ad">5.2 关键信息标记</span>

| 场景 | 标记 | 用法 |
|------|------|------|
| <span style="color:#c0392b">**核心结论 / 重点**</span> | `📌` | 放在段落开头或 Callout 标题中 |
| <span style="color:#c0392b">**重要提醒 / 必须执行**</span> | `🔴` 或 `⚠️` | 放在注意事项、必须步骤前 |
| <span style="color:#27ae60">**技巧 / 最佳实践**</span> | `💡` | 放在小技巧、优化建议前 |
| <span style="color:#27ae60">**正面示例（正确做法）**</span> | `✅` | 放在正确回答/正确案例前 |
| <span style="color:#c0392b">**反面示例（错误做法）**</span> | `❌` | 放在错误回答/错误案例前 |
| <span style="color:#2980b9">**案例 / 示例**</span> | `📖` | 放在具体案例前 |
| <span style="color:#d35400">**待办事项 / 行动项**</span> | `🎯` | 放在行动计划前 |

### <span style="color:#8e44ad">5.3 正文中的标记使用规范</span>

```markdown
### 🔍 案例分析

<span style="color:#c0392b">📌 **核心要点：**</span> 这里放最重要的结论。

<span style="color:#27ae60">✅ 正确做法：</span>
- 先做 A，再做 B

<span style="color:#c0392b">❌ 常见错误：</span>
- 直接做 C 会导致问题

<span style="color:#2980b9">💡 小技巧：</span>这里放优化建议。

<span style="color:#d35400">🎯 行动项：</span>
- [ ] 完成 X
- [ ] 完成 Y

<span style="color:#8e44ad">📖 示例：</span>这里放具体的案例描述。
```

---

## <span style="color:#2980b9">📐 模板</span>

### <span style="color:#8e44ad">🎓 听课笔记模板</span>

````markdown
```markdown
---
title: "{{课程名称}}"
date: {{YYYY-MM-DD}}
tags:
  - 笔记整理
  - 听课记录
  - {{关键词1}}
  - {{关键词2}}
created: {{YYYY-MM-DD}}
aliases:
  - {{别名1}}
source: "{{来源}}"
---

# 📋 {{课程名称}}

> [!INFO] 📌 课程信息
> - **类型**：课程讲解
> - **日期**：{{date}}
> - **讲师**：{{讲师名（如有）}}
> - **来源**：{{来源}}

## 📑 目录

1. [[#{{主题1}}]]
2. [[#{{主题2}}]]

---

## {{主题1}}

### {{子主题}}

### 🔍 案例 / 示例

{{保留的案例内容}}

> [!TIP] 📎 关联附件
> 📄 详见 [[讲义文件名.pdf#page=页码]] — 第X-Y页：该页内容概要描述

---

## {{主题2}}

{{...}}

---

## 📌 总结

{{核心要点归纳}}

## 🔗 相关笔记

- [[{{相关笔记}}]]
```
````

### <span style="color:#27ae60">🗣️ 会议记录模板</span>

````markdown
```markdown
---
title: "{{会议主题}}"
date: {{YYYY-MM-DD}}
tags:
  - 笔记整理
  - 会议记录
  - {{关键词}}
created: {{YYYY-MM-DD}}
source: "{{来源}}"
---

# 🗣️ {{会议主题}}

> [!INFO] 📌 会议信息
> - **会议**：{{名称}}
> - **日期**：{{date}}
> - **参与人**：{{参与人列表}}

## 💬 讨论内容

### {{议题 1}}

#### ✅ 达成共识

- {{共识点1}}
- {{共识点2}}

### {{议题 2}}

{{...}}

## 🎯 待办事项

- [ ] {{事项}} — @{{负责人}}

## 🔗 相关笔记

- [[{{相关笔记}}]]
```
````

---

## <span style="color:#27ae60">✅ 质量检查清单</span>

在输出最终笔记前，逐项检查以下内容：

### <span style="color:#d35400">前置检查（整理前）</span>

- <span style="color:#8e44ad">[ ] 📦</span> **如果收到多个文件，是否已执行 Stage 0 分组、排序和合并？**
- <span style="color:#8e44ad">[ ] ❓</span> **组内排序是否与用户确认过（如有不确定）？**
- <span style="color:#c0392b">[ ] ❓</span> 是否已询问用户 **存储路径**、**笔记名称** 和 **内容来源**？
- <span style="color:#c0392b">[ ] ❓</span> 如用户只回答了部分问题，是否继续追问了？
- <span style="color:#c0392b">[ ] 📄</span> 如果来源为 PDF，是否执行了 Step 0.5 提取内容？
- <span style="color:#c0392b">[ ] 🧹</span> 如果生成了临时文件，是否记录了清理计划？

### <span style="color:#2980b9">结构检查（整理中）</span>

- <span style="color:#c0392b">[ ] 📄</span> 最终输出是否用 ` ```markdown ` 代码块包裹？
- [ ] 📄 YAML frontmatter 是否完整（title、date、tags、created）？
- [ ] 📄 标题层级是否合理（`#` → `##` → `###` → `####`，不超过四级）？
- [ ] 📄 同级列表的标记符号是否全篇统一？
- [ ] 📄 缩进是否统一（全篇 2 空格或全篇 4 空格）？

### <span style="color:#d35400">内容检查（整理中）</span>

- [ ] 🔍 是否覆盖了原文所有关键内容？
- <span style="color:#c0392b">[ ] 💎</span> 所有案例 / 示例是否完整保留？
- [ ] 🗑️ 重复内容是否已删除（不留占位标记）？
- [ ] 🔧 明显的字幕识别错误是否已修正？
- [ ] ❓ 不确定的修正是否用 `> [!QUESTION]` 标记？
- <span style="color:#c0392b">[ ] 📂</span> **目标文件夹内是否有附件 PDF？** 是否已执行 Step 1.5.3 建立内容映射表？
- <span style="color:#c0392b">[ ] 🔗</span> **是否根据映射表**在笔记对应位置插入了 `[[文件.pdf#page=页码]]` 精确超链接？
- <span style="color:#c0392b">[ ] 📝</span> **每个超链接旁是否有描述性文本**（注明页范围和内容概要，如"第4-6页：API配置参数"）？
- [ ] 🏷️ 标签是否已添加（主标签 + 类型标签 + 3-5 个关键词）？

### <span style="color:#2980b9">格式检查（渲染兼容）</span>

- [ ] 💡 是否使用了合适的 Obsidian callouts（NOTE、TIP、WARNING、CAUTION、QUESTION）？
- [ ] ⭐ 关键位置是否加入了标记符号（📌🔴💡✅❌📖🎯）？
- [ ] 📝 分点是否清晰明确？
- [ ] 🔗 Wiki 链接格式是否正确？

### <span style="color:#c0392b">🔗 双向链接检查（整理后）</span>

- <span style="color:#c0392b">[ ] 🔍</span> **是否已在 `总结好的大纲以及笔记/` 下搜索相关笔记？**
- <span style="color:#c0392b">[ ] 🔗</span> **是否在当前笔记中添加了正向链接？**
- <span style="color:#c0392b">[ ] 🔄</span> **是否在相关笔记中添加了反向链接？**
- <span style="color:#c0392b">[ ] 💾</span> **是否已将文件直接写入磁盘（而非仅代码块输出）？**
- <span style="color:#c0392b">[ ] 🧹</span> **中间产生的临时图片/PDF是否已删除？**

---

## <span style="color:#d35400">🧩 边界情况处理</span>

| <span style="color:#2980b9">情况</span> | <span style="color:#27ae60">处理方式</span> | <span style="color:#d35400">标记</span> |
|------|---------|------|
| 用户只提供了笔记，没有 PDF 讲义 | 跳过链接插入步骤，正常整理笔记 | <span style="color:#27ae60">✅ 正常流程</span> |
| 笔记内容太短 / 信息不足 | 按已有内容尽力整理，不做补充 | <span style="color:#d35400">⚠️ 如实呈现</span> |
| 原文完全没有时间 / 日期信息 | 使用当前日期，在 frontmatter 中注明 | <span style="color:#2980b9">💡 标注"日期未知"</span> |
| <span style="color:#c0392b">转录稿质量极差、大量错误</span> | 尽可能修正，无法判断处用 `> [!QUESTION]` 标注 | <span style="color:#c0392b">🔴 重点标记</span> |
| <span style="color:#c0392b">用户只说了路径没说名字（或反之）</span> | **继续追问**，直到两者都确认 | <span style="color:#c0392b">🔴 必须追问</span> |
| 用户说"随便"或"你定" | 根据笔记内容推断一个合理的名字，并在保存前跟用户确认 | <span style="color:#2980b9">💡 推断+确认</span> |
| 内容包含多个不相关的主题 | 拆分为多个独立笔记，分别整理 | <span style="color:#d35400">📌 分开输出</span> |
| 内容同时包含课程和会议内容 | 按占比更大的类型处理，标签中同时保留 | <span style="color:#8e44ad">🧬 灵活处理</span> |
| <span style="color:#c0392b">输入是 PDF 且文字提取失败（Type3 字体）</span> | 将页面渲染为图片，尝试 OCR 提取；如 OCR 不可用则尽力从碎片文本中理解内容 | <span style="color:#d35400">🔴 按情况降级</span> |
| <span style="color:#c0392b">目标文件夹已有附件 PDF</span> | 执行 Step 1.5.3 逐页分析PDF内容，建立内容映射表，在笔记对应位置插入 `[[文件.pdf#page=页码]]` 精确超链接并附描述文本 | <span style="color:#2980b9">✅ 自动关联</span> |
| <span style="color:#c0392b">搜索 `总结好的大纲以及笔记/` 未找到相关笔记</span> | 跳过反向链接步骤，保留空 `## 🔗 相关笔记` 占位 | <span style="color:#d35400">✅ 正常跳过</span> |
| <span style="color:#c0392b">相关笔记是 PDF 非 .md 文件</span> | 不追加反向链接，仅作为附件引用 | <span style="color:#d35400">✅ 正常跳过</span> |
| 用户通过飞书发送文件 | 按 Step 0.5 流程：搜索消息 → 下载 → 提取内容 → 清理临时文件 | <span style="color:#8e44ad">📋 完整流程</span> |
| <span style="color:#c0392b">用户同时发送多个分段文件（上/中/下）</span> | **必须先执行 Stage 0 合并后再进入 Step 0** | <span style="color:#8e44ad">📦 Stage 0</span> |
| <span style="color:#c0392b">多个分段文件的后缀模式无法识别</span> | **立即停止，询问用户各文件的正确顺序** | <span style="color:#c0392b">🔴 必须询问</span> |
| <span style="color:#c0392b">多个文件但只有部分可识别后缀模式</span> | 识别可分组的部分，无法识别部分询问用户 | <span style="color:#d35400">📌 部分询问</span> |

---

## <span style="color:#8e44ad">⚡ 执行总则（速查）</span>

```
<span style="color:#8e44ad">角色定位</span>  →  <span style="color:#8e44ad">Obsidian 笔记专家</span>
<span style="color:#c0392b">输出格式</span>  →  <span style="color:#c0392b">.md 代码块预览 + 直接写入磁盘</span>
<span style="color:#d35400">核心原则</span>  →  <span style="color:#d35400">结构清晰 + 层级分明 + 格式规范 + 标记醒目</span>
<span style="color:#2980b9">标记规范</span>  →  <span style="color:#c0392b">📌核心</span> <span style="color:#c0392b">🔴重要</span> <span style="color:#2980b9">💡技巧</span> <span style="color:#27ae60">✅正确</span> <span style="color:#c0392b">❌错误</span> <span style="color:#8e44ad">📖案例</span> <span style="color:#d35400">🎯行动</span>
<span style="color:#c0392b">必问问题</span>  →  <span style="color:#c0392b">①存储路径  ②笔记名称  ③内容来源</span>
<span style="color:#c0392b">不可遗漏</span>  →  <span style="color:#c0392b">所有案例/示例必须完整保留</span>
<span style="color:#27ae60">去重要求</span>  →  <span style="color:#27ae60">保留首次完整内容，后续重复直接删除</span>
<span style="color:#d35400">修正原则</span>  →  <span style="color:#d35400">自动修正 + 不确定的用 [!QUESTION] 标记</span>
<span style="color:#c0392b">新增关键步骤</span>  →  <span style="color:#c0392b">Stage 0 多文件合并 + Step 0.5 PDF提取 + Step 1.5 附件检查与内容映射 + Step 3.5 直接写入 + Step 4 精确超链接导航 + Step 6 双向链接</span>
<span style="color:#c0392b">整理后必做</span>  →  <span style="color:#c0392b">搜索「总结好的大纲以及笔记/」建双向链接 + 清理中间临时文件</span>
```
