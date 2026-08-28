# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import fitz

PDF = r'F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽\下一任对接文档\下一任对接文档\下一任对接文档-新版-背景版-优化版_修复版.pdf'
doc = fitz.open(PDF)
print(f'总页数: {len(doc)}')
for i, page in enumerate(doc):
    print(f'\n===== PAGE {i+1} =====')
    text = page.get_text('text')
    print(text)
