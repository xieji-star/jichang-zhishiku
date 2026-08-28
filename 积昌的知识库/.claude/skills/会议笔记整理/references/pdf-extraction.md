# PDF 文件内容提取指南

当会议记录的来源是 PDF 文件时，按以下流程提取文本内容。

## 1. 从飞书下载文件

如果用户在飞书中发送了 PDF，使用 Lark IM 工具搜索并下载：

```bash
# 搜索消息找到文件
lark-cli im +messages-search --query "{{文件名关键词}}" --as user --page-limit 10 --json

# 从结果中找到 message_id 和 file_key，然后下载
lark-cli im +messages-resources-download \
  --message-id {{message_id}} \
  --file-key {{file_key}} \
  --type file \
  --output "lark-im-resources/{{文件名}}" \
  --as user --json
```

> 下载的文件会保存在 `lark-im-resources/` 目录下。

## 2. 使用 PyMuPDF 提取文本（首选方案）

### 2.1 基本提取

```python
import fitz
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

doc = fitz.open('{{PDF文件路径}}')
print(f'Total pages: {doc.page_count}')
for i in range(doc.page_count):
    text = doc[i].get_text('text')
    if text.strip():
        print(f'=== Page {i+1} ===')
        print(text)
doc.close()
```

### 2.2 编码处理

Windows 中文终端使用 GBK 编码，可能导致 UnicodeEncodeError。**务必**：

- 使用 `python3 -X utf8` 参数启动 Python
- 在代码开头添加 `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`
- 如果仍有问题，使用重定向写入文件再读取

```bash
# 将输出重定向到文件避免终端编码问题
python3 -X utf8 -c "
import fitz, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
doc = fitz.open('文件.pdf')
for i in range(doc.page_count):
    text = doc[i].get_text('text')
    if text.strip():
        print(f'=== Page {i+1} ===')
        print(text)
doc.close()
" > pdf_output.txt 2>&1

# 然后直接读取输出文件
```

## 3. 处理 Type3 字体（文字提取为乱码时）

### 3.1 判断标准

当提取的文字出现以下情况，说明 PDF 使用了 Type3 字体：
- 字符显示为 `���` 等乱码
- 中文被替换为 `Y` 等英文字母
- `get_text('text')` 返回空字符串或大量不可读字符
- `get_text('rawdict')` 中 spans 没有 `text` 键，只有 `chars`

### 3.2 降级方案：渲染为图片

```python
import fitz
doc = fitz.open('{{PDF文件路径}}')
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)
    pix.save(f'lark-im-resources/{{文件名}}_page_{i+1}.png')
    print(f'Page {i+1} saved: {pix.width}x{pix.height}')
doc.close()
```

### 3.3 OCR 提取文字

如果安装了 OCR 引擎：

```bash
# 安装 easyocr
python3 -m pip install easyocr -q
```

```python
import easyocr
reader = easyocr.Reader(['ch_sim', 'en'])
for i in range(1, total_pages+1):
    result = reader.readtext(f'page_{i}.png', detail=0)
    print(f'=== Page {i} ===')
    print('\n'.join(result))
```

> **注意**：
> - OCR 结果仍需手动校正
> - 图片文件在任务结束后**必须删除**
> - OCR 安装需要时间，可先在后台安装，同步进行其他步骤

### 3.4 无 OCR 时的降级处理

如果系统没有 OCR 引擎且无法安装，则：
1. 尽量从 PyMuPDF 提取的碎片文本中理解内容
2. 标记无法确定的内容为 `> [!QUESTION]`
3. 向用户说明 PDF 文本提取质量受限

## 4. 清理中间文件

任务结束后必须删除所有临时文件：

```bash
# 删除页面截图
rm -f lark-im-resources/{{文件名}}_page_*.png

# 删除文本提取文件
rm -f lark-im-resources/{{文件名}}_fulltext.txt

# 删除原始 PDF（如果已提取完内容且不再需要）
rm -f "lark-im-resources/{{原始PDF文件名}}"
```

## 5. 快速判断流程

```
内容来源是 PDF 吗？
  ├── 是 → 尝试 PyMuPDF 提取
  │         ├── 文字可读 → 直接使用
  │         └── 文字乱码 → 渲染为图片 → OCR提取 / 碎片理解
  └── 否 → 直接进入 Step 1
```
