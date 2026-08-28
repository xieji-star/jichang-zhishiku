---
name: PDF美化与排版
description: PDF 排版美化的统一入口（聚合 skill），把 3 个 PDF 子 skill 打包为一个可同时调用的技能组：① pdf —— Anthropic 官方 PDF 全能处理（读取/提取文字表格/合并/拆分/旋转/加水印/创建/表单填写/OCR）；② huashu-md-to-pdf —— Markdown 转苹果设计风格专业白皮书（自动封面/目录/页眉页脚）；③ elegant-reports —— Markdown 转北欧极简风格精美 PDF 报告（多模板多主题、纯本地渲染）。当用户提到"PDF 排版"、"PDF 美化"、"PDF 生成"、"PDF 处理"、"白皮书"、"精美 PDF 报告"、"执行摘要"、"合并/拆分 PDF"、"加水印"、"填表单"、"PDF OCR"等任何与 PDF 相关的需求时，务必使用本 skill，由它自动路由到对应子 skill 执行；当任务需要多个子 skill 协作（如先从 PDF 提取内容再排版成精美报告）时，本 skill 负责编排串联。
---

# PDF美化与排版（聚合 Skill）

将知识库中 3 个 PDF 子 skill 统一包装为**一个入口**，实现"一次触发、自动路由、可串联调用"。

> 触发本 skill 后：**先判断任务类型 → 路由到对应子 skill → 读取该子 skill 的 SKILL.md 并按其指示执行**。若任务涉及多个环节，按"组合工作流"串联多个子 skill。

## 一、3 个子 skill 一览

| 子 skill | 定位 | 目录 |
|---------|------|------|
| `pdf` | PDF **全能处理**（Anthropic 官方）：读取/提取文本与表格、合并、拆分、旋转、加水印、创建、表单填写、加密解密、图片提取、扫描件 OCR | `.claude/skills/PDF美化与排版/pdf/` |
| `huashu-md-to-pdf` | **Markdown → 苹果风格专业白皮书**：自动封面、可点击目录、页眉页脚、书籍级排版 | `.claude/skills/PDF美化与排版/huashu-md-to-pdf/` |
| `elegant-reports` | **Markdown → 北欧极简风格精美报告**：多模板（report/presentation/executive）多主题（light/dark）、纯本地渲染 | `.claude/skills/PDF美化与排版/elegant-reports/` |

## 二、路由规则（先看这里）

| 用户需求 | 路由到 | 说明 |
|---------|--------|------|
| 处理已有 PDF：读取、提取文字/表格、合并、拆分、旋转、加水印、创建、填表单、OCR、加密解密 | **`pdf`** | 读取该子 skill 的 SKILL.md 按其指示操作 |
| 用 Markdown 生成**专业白皮书/技术文档**（技术指南、产品白皮书、教程） | **`huashu-md-to-pdf`** | 苹果设计风格，`convert.py` 一条命令 |
| 用 Markdown 生成**精美报告/演示简报**（执行摘要、分析报告、董事会汇报、北欧极简风） | **`elegant-reports`** | `generate.js` 一条命令，支持模板/主题 |
| 先把 PDF 内容提取出来，再排版成精美 PDF | **`pdf` → `elegant-reports` 或 `huashu-md-to-pdf`** | 组合工作流（见第四节） |

> 拿不准时：用户要"处理/操作 PDF 文件本身"→ `pdf`；要"从 Markdown/文字生成漂亮的 PDF 文档"→ 看风格（苹果风 → `huashu-md-to-pdf`，北欧极简风 → `elegant-reports`）。

## 三、子 skill 调用方法

### 1）`pdf`（PDF 全能处理）

1. 读取 `.claude/skills/PDF美化与排版/pdf/SKILL.md`（按需再读 `REFERENCE.md`、`FORMS.md`）。
2. 按其中指示，用 Python 库（pypdf / pdfplumber / reportlab / pytesseract）或命令行工具（qpdf / pdftotext / pdftk）完成任务。
3. 需要填表单时先读 `FORMS.md`；需要高级特性/JavaScript 方案时读 `REFERENCE.md`。

### 2）`huashu-md-to-pdf`（苹果风格白皮书）

1. 读取 `.claude/skills/PDF美化与排版/huashu-md-to-pdf/SKILL.md`。
2. 首次使用需安装依赖：`pip3 install markdown2 weasyprint`（macOS 额外 `brew install pango`）。
3. 执行转换（Markdown 章节需用 `## 1. 标题` / `### 1.1 标题` 格式，才能正确提取目录）：

   ```bash
   python ".claude/skills/PDF美化与排版/huashu-md-to-pdf/scripts/convert.py" <输入.md> -o <输出.pdf> [--title "标题" --author "作者"]
   ```

### 3）`elegant-reports`（北欧极简风格）

1. 读取 `.claude/skills/PDF美化与排版/elegant-reports/SKILL.md`。
2. 需要 Node.js 18+ 与系统自带 Edge/Chrome；无 npm 依赖。
3. 支持在 Markdown frontmatter 写 `title` / `subtitle` / `author` / `template` / `theme` 控制输出。
4. 执行：

   ```bash
   cd ".claude/skills/PDF美化与排版/elegant-reports"
   node ./generate.js --list                                            # 查看全部模板
   node ./generate.js <输入.md> <输出.pdf> --template report --theme light
   ```

## 四、组合工作流（串联多个子 skill）

当任务需要多个环节时按顺序串联，每个环节完成后进入下一个：

**示例 1：把一份扫描 PDF 整理成精美报告**
1. `pdf`：OCR 识别扫描件 → 提取文本；
2. 整理为 Markdown；
3. `elegant-reports`：生成北欧风格报告。

**示例 2：把几份 PDF 合并后做成白皮书**
1. `pdf`：合并/提取内容；
2. 整理为 Markdown；
3. `huashu-md-to-pdf`：生成苹果风格白皮书。

**示例 3：批量美化一批 Markdown 文档**
1. `huashu-md-to-pdf` 或 `elegant-reports` 逐份生成；
2. `pdf`：用 pypdf 将多份结果合并为一个 PDF 文件。

## 五、注意事项

- 每个子 skill 都有独立的依赖与命令，**调用前务必读取对应 SKILL.md**，不要凭记忆操作。
- `huashu-md-to-pdf` 依赖 weasyprint（HTML→PDF 渲染）；`elegant-reports` 依赖 Edge/Chrome 无头模式。
- `elegant-reports` 为**纯本地渲染**：不联网、不把任何文档内容发送到第三方服务；输出 HTML/PDF 到用户指定目录。
- 生成的中间文件（临时 .md、临时 HTML、临时 PDF）在任务结束后按知识库规则清理。
- **页眉页脚排版规则（硬性）**：生成的 PDF 中，**每一页的页眉区与页脚区都不得出现正文内容**——正文必须严格约束在页边距（页眉/页脚留白）之外的内容区内。两个生成子 skill（`huashu-md-to-pdf`、`elegant-reports`）均已按此规则设置：占满整页的容器高度一律用 `calc(100vh − 页边距)` 计算（如 A4+8mm 边距 → `calc(100vh − 16mm)`），与 `@page` 边距严格匹配，避免正文溢出到页眉页脚留白区。
