---
name: meeting-summary
description: |
  Transform raw meeting transcripts, lecture recordings (听课笔记), and course handouts (讲义) into comprehensive, structured Obsidian notes. 
  
  Use this skill whenever the user says ANY of these: "请你帮我整理这份听课笔记", "请你帮我整理这个会议记录", "帮我整理听课记录", "帮我整理会议记录", "总结一下这堂课", "整理一下这个会议", or any request to organize, summarize, or structure raw meeting or course notes. Also trigger when the user pastes or provides a long block of raw transcript text from a meeting or lecture and asks for organization.
  
  The skill handles: deduplication of repeated content, auto-correction of speech-to-text transcription errors, insertion of PDF handout hyperlinks at relevant locations, and conversion into proper Obsidian Markdown format with YAML frontmatter, callouts, wikilinks, and hierarchical headings.
  
  Make sure to use this skill whenever the user provides meeting or lecture transcripts, even if they don't explicitly name the skill — if the request involves organizing raw notes into structured format, this skill should trigger.
---

# Meeting & Course Note Organizer（会议/听课笔记整理）

将原始的会议记录、听课笔记和课程讲义整理为**结构化的 Obsidian 笔记**。

---

## 核心工作流

### Step 0: 前置询问（每次整理前必须执行）

在开始整理之前，必须先询问用户以下两个问题，**得到答案后才能继续**：

#### 问题 1：笔记的存储位置
> "这份笔记你想存放在哪个文件夹下？"

- 用户可能会给出一个具体路径（如 `积昌/AI/`、`积昌/项目X/` 等）
- 也可能是 Obsidian 中的某个文件夹名
- **记录这个路径，后续用来存放最终输出**

#### 问题 2：笔记的名称（同时也是文件夹名）
> "这份笔记你想起什么名字？"

- 这个名字将同时作为**文件夹名**和**文件名**
- 最终输出结构为：`{{用户指定的路径}}/{{用户指定的名字}}/{{用户指定的名字}}.md`
- 这样方便用户把附件（PDF 讲义、图片等）也放进同一个文件夹

> [!IMPORTANT]
> 在得到这两个答案之前，**不要开始整理笔记内容**。把问题问清楚再动手。

### Step 1: 识别输入类型

首先判断用户提供的是什么类型的材料：

| 类型 | 特征 |
|------|------|
| **听课笔记 / 课程转录** | 有讲师讲解、知识点教学、案例演示等内容 |
| **会议记录** | 有参与人讨论、决策、待办事项等内容 |
| **混合材料** | 同时包含笔记文本 + PDF 讲义文件引用 |

### Step 2: 清理与预处理

#### 2.1 修正 AI 字幕识别错误

采用**"自动修正 + 标记存疑"两者结合**的模式：

- **自动修正**：根据全文主旨和上下文语义，将明显的识别错误修正为合理内容
  - 示例：`草履虫丝` → `草率了事`，`高扣的` → `Claude Code`，`反重力` → `VS Code`（根据上下文判断）
  - 示例：`点括号的skills` → `.claude/skills`，`6点NBreferencestrips` → `SKILL.md、references、scripts`
  - 示例：`秋之` → `秋之`（品牌名，保留原样），`求职` → `秋之`（上下文是品牌名）
- **标记存疑**：对于不确定的修正，使用 `> [!QUESTION]` 标注出来，说明你的判断依据
  ```markdown
  > [!QUESTION] 修正存疑
  > 原文"XXXX"根据上下文推测可能为"YYYY"，请确认是否正确。
  ```

#### 2.2 去重

删除重复内容，但**注意**：
- 保留第一次出现的完整内容
- 后续重复处直接删除，不做额外标记
- 如果重复内容有细微差异，保留最完整/最准确的那个版本

#### 2.3 保留案例与示例

**所有原文中的案例、代码示例、演示过程必须完整保留**，这是用户明确要求的。即使内容冗长也要保留。

### Step 3: 结构化输出

按以下结构组织笔记。**输出时注意存储结构：**

```
{{用户指定的路径}}/{{用户指定的名字}}/
├── {{用户指定的名字}}.md    ← 整理后的笔记
├── 讲义文件.pdf            ← 如有，可一并放入（由用户后续自行添加）
└── 其他附件...             ← 由用户自行管理
```

> ⚠️ **文件夹名 = 文件名**，两者必须一致。不要直接把 .md 文件丢在目录下。

笔记正文结构如下：

```markdown
---
title: "{{课程名称 / 会议主题}}"
date: {{YYYY-MM-DD}}
tags:
  - {{课程标签 / 会议标签}}
  - {{关键词1}}
  - {{关键词2}}
created: {{YYYY-MM-DD}}
---

# {{标题}}

> [!INFO] 基本信息
> - **类型**：{{课程 / 会议}}
> - **日期**：{{date}}
> - **时长**：{{duration（如有）}}
> - **讲师/参与人**：{{name（如有）}}

## 目录

{{自动生成的目录/概览}}

## 正文

### {{主题 1}}

{{详细笔记内容}}

### {{主题 2}}

{{详细笔记内容}}

> [!TIP] 关联讲义
> 详见 [[讲义文件名.pdf#page=页码]]（如果提供了PDF附件）

### {{主题 3}}

{{详细笔记内容}}

{{... 以此类推}}

## 总结

{{核心要点归纳}}

## 相关笔记

- [[{{相关笔记1}}]]
- [[{{相关笔记2}}]]
```

### Step 4: 插入讲义超链接

**如果用户提供了 PDF 讲义文件或讲义链接**：
- 在笔记中对应的知识点位置，插入格式为 `[[讲义文件名.pdf#page=页码]]` 的 wikilink
- 每一处链接都应指向讲义中与该段内容相关的最具体的页面
- 上下文合适时可用 `> [!TIP] 关联讲义` 标注块

### Step 5: 添加标签

- 自动添加 `#笔记整理` 作为主标签
- 根据内容添加类型标签：`#听课记录` 或 `#会议记录`
- 从内容中提取 3-5 个关键词作为额外标签

### Step 6: 格式规范

始终遵循以下 Obsidian 格式要求：
- **YAML frontmatter**：必须包含 `title`、`date`、`tags`、`created`
- **标题层级**：`#` → `##` → `###` → `####`，按逻辑递进
- **列表**：用 `-` 无序列表和 `1.` 有序列表，分点明确
- **加粗**：关键术语用 `**粗体**`
- **代码块**：代码/命令用 ``` ``` 包裹并标注语言
- **Callouts**：用 `> [!NOTE]`、`> [!TIP]`、`> [!WARNING]`、`> [!QUESTION]` 等
- **Wiki 链接**：讲义引用用 `[[文件名.pdf#page=页码]]` 格式
- **分隔线**：主要章节之间用 `---` 分隔

---

## 模板

### 听课笔记模板

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
---

# {{课程名称}}

> [!INFO] 课程信息
> - **课程**：{{名称}}
> - **日期**：{{date}}

## 目录

1. [[#{{主题1}}]]
2. [[#{{主题2}}]]

---

## {{主题1}}

### {{子主题}}

{{详细笔记内容}}

> [!TIP] 关联讲义
> 详见 [[讲义文件名.pdf#page=页码]]

### 案例 / 示例

{{保留的案例内容}}

---

## {{主题2}}

{{...}}

---

## 总结

{{核心要点归纳}}

## 相关笔记

- [[{{相关笔记}}]]
```

### 会议记录模板

```markdown
---
title: "{{会议主题}}"
date: {{YYYY-MM-DD}}
tags:
  - 笔记整理
  - 会议记录
  - {{关键词}}
created: {{YYYY-MM-DD}}
---

# {{会议主题}}

> [!INFO] 会议信息
> - **会议**：{{名称}}
> - **日期**：{{date}}

## 讨论内容

### {{议题 1}}

{{详细讨论记录}}

### {{议题 2}}

{{...}}

## 待办事项

- [ ] {{事项}} — @{{负责人}}
- [ ] {{事项}} — @{{负责人}}

## 相关笔记

- [[{{相关笔记}}]]
```

---

## 质量检查清单

在输出最终笔记前，检查以下各项：

- [ ] 是否已询问用户**存储路径**和**笔记名称**？
- [ ] 文件夹名是否与文件名一致？
- [ ] 是否覆盖了原文所有关键内容？
- [ ] 所有案例/示例是否完整保留？
- [ ] 重复内容是否已删除？
- [ ] 明显的字幕识别错误是否已修正？
- [ ] 不确定的修正是否用 `[!QUESTION]` 标记？
- [ ] PDF 讲义超链接是否已插入对应位置？
- [ ] YAML frontmatter 是否完整？
- [ ] 标题层级是否合理？
- [ ] 是否使用了合适的 Obsidian callouts？
- [ ] 分点是否清晰明确？
- [ ] 标签是否已添加？

---

## 边界情况处理

| 情况 | 处理方式 |
|------|---------|
| 用户只提供了笔记，没有PDF讲义 | 跳过链接插入步骤，正常整理笔记 |
| 笔记内容太短/信息不足 | 按已有内容尽力整理，不做补充 |
| 原文完全没有时间/日期信息 | 使用当前日期，在 frontmatter 中注明 |
| 转录稿质量极差、大量错误 | 尽可能修正，无法判断处用 `[!QUESTION]` 标注 |
| 用户只说了路径没说名字（或反之） | 继续追问，直到两者都确认 |
| 用户说"随便"或"你定" | 根据笔记内容推断一个合理的名字，并在保存前跟用户确认 |
