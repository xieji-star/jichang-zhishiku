# -*- coding: utf-8 -*-
"""提取 版本1.pdf 全文与 _doc_render.html 文本，用于对齐校验"""
import os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

BASE = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽"

# --- PDF 全文 ---
pdf = fitz.open(os.path.join(BASE, "下一任对接文档", "下一任对接文档", "版本1.pdf"))
pdf_chars = 0
with open(os.path.join(BASE, "_align_pdf.txt"), "w", encoding="utf-8") as f:
    for i in range(pdf.page_count):
        t = pdf[i].get_text()
        pdf_chars += len(t)
        f.write(f"\n===== PDF PAGE {i+1} =====\n")
        f.write(t)
pdf.close()

# --- HTML 文本 ---
html = open(os.path.join(BASE, "_doc_render.html"), encoding="utf-8").read()
# 去掉 script/style
html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
# 块级标签换行
html = re.sub(r"<(div|p|h[1-6]|li|tr|br|table|img|span)[^>]*>", "\n", html, flags=re.I)
# 去掉剩余标签
text = re.sub(r"<[^>]+>", "", html)
import html as h
text = h.unescape(text)
# 压缩空行
lines = [ln.rstrip() for ln in text.split("\n")]
out = []
blank = 0
for ln in lines:
    if ln.strip() == "":
        blank += 1
        if blank <= 1:
            out.append("")
    else:
        blank = 0
        out.append(ln)
with open(os.path.join(BASE, "_align_html.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("PDF chars:", pdf_chars)
print("HTML text chars:", sum(len(x) for x in out))
