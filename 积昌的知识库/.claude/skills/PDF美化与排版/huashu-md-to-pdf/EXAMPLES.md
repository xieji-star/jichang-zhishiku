# Markdown to PDF Skill 使用示例

## 示例 1: 基础转换

**用户提问**：
```
帮我把 tech-guide.md 转成 PDF
```

**Claude 执行**：
```bash
python .claude/skills/markdown-to-pdf/scripts/convert.py tech-guide.md
```

**输出**：
```
📖 读取文件: tech-guide.md
📑 提取元数据...
📂 提取目录结构...
   ✓ 找到 5 个主章节
   ✓ 找到 12 个子章节
🎨 处理 Markdown 内容...
📄 生成 HTML...
📝 生成 PDF...
✅ 成功生成: tech-guide.pdf
📊 文件大小: 0.8 MB
```

---

## 示例 2: 自定义输出

**用户提问**：
```
把 README.md 转成 PDF，输出文件名叫"产品说明书.pdf"
```

**Claude 执行**：
```bash
python .claude/skills/markdown-to-pdf/scripts/convert.py README.md -o "产品说明书.pdf"
```

---

## 示例 3: 完整自定义

**用户提问**：
```
转换 whitepaper.md，标题改成"技术白皮书2025"，作者写"技术团队"
```

**Claude 执行**：
```bash
python .claude/skills/markdown-to-pdf/scripts/convert.py whitepaper.md \
  --title "技术白皮书2025" \
  --author "技术团队" \
  -o "技术白皮书2025.pdf"
```

---

## 示例 4: 批量转换

**用户提问**：
```
把当前目录下所有 .md 文件都转成 PDF
```

**Claude 执行**：
```bash
for file in *.md; do
  python .claude/skills/markdown-to-pdf/scripts/convert.py "$file"
done
```

---

## 示例 5: 转换后预览

**用户提问**：
```
转换 guide.md 并告诉我文件在哪
```

**Claude 执行**：
```bash
python .claude/skills/markdown-to-pdf/scripts/convert.py guide.md
```

**Claude 回复**：
```
✅ 已成功生成 PDF: guide.pdf
📍 文件位置: /Users/xxx/Documents/guide.pdf
📊 文件大小: 1.2 MB

你可以直接打开查看，或者用以下命令预览：
open guide.pdf
```

---

## Markdown 文档模板

如果你的文档还没有结构，可以参考这个模板：

```markdown
# 技术文档标题

## 1. 简介
### 1.1 背景
这里写背景介绍...

### 1.2 目标
这里写文档目标...

## 2. 核心概念
### 2.1 概念A
解释概念...

### 2.2 概念B
解释概念...

## 3. 使用方法
### 3.1 安装
安装步骤...

\`\`\`bash
npm install xxx
\`\`\`

### 3.2 配置
配置说明...

| 参数 | 说明 | 默认值 |
|------|------|--------|
| foo  | 配置项 | true |

## 4. 最佳实践
### 4.1 实践A
实践说明...

### 4.2 实践B
实践说明...

## 5. 常见问题
### 5.1 问题1
解答...

### 5.2 问题2
解答...
```

---

## 高级技巧

### 技巧 1: 在脚本中调用

```python
from pathlib import Path
import subprocess

# 批量转换
md_files = Path('.').glob('*.md')
for md_file in md_files:
    subprocess.run([
        'python',
        '.claude/skills/markdown-to-pdf/scripts/convert.py',
        str(md_file)
    ])
```

### 技巧 2: 添加到快捷命令

在 `.bash_profile` 或 `.zshrc` 中添加：

```bash
alias md2pdf='python ~/.claude/skills/markdown-to-pdf/scripts/convert.py'
```

然后就可以直接使用：
```bash
md2pdf document.md
md2pdf report.md -o "2025年度报告.pdf"
```

### 技巧 3: 与 Git Hooks 结合

在 `.git/hooks/pre-commit` 中：

```bash
#!/bin/bash
# 自动生成 PDF 版本
if [ -f README.md ]; then
  python .claude/skills/markdown-to-pdf/scripts/convert.py README.md
  git add README.pdf
fi
```

---

## 真实使用案例

### 案例 1: Claude Skills 白皮书
- **输入**：2万字 Markdown 文档
- **输出**：1.4 MB 专业 PDF
- **特点**：10个主章节，38个子章节，双列目录

### 案例 2: 技术文档
- **输入**：API 文档 Markdown
- **输出**：带目录的技术手册
- **特点**：代码高亮、表格清晰

### 案例 3: 产品说明书
- **输入**：产品介绍 Markdown
- **输出**：专业说明书 PDF
- **特点**：苹果设计风格、易读性强
