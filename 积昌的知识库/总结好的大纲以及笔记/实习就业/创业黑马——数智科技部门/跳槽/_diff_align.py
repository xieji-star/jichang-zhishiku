# -*- coding: utf-8 -*-
"""HTML 文本 vs 对齐版PDF文本 差异报告（行级、去空白）"""
import os, sys, io, re, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽"

def norm_line(s):
    s = re.sub(r"\s+", "", s)
    return s

def read_lines(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    lines = []
    for ln in raw.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        # 跳过 PDF 页码标记
        if ln.startswith("===== PDF PAGE"):
            continue
        # 跳过 TOC 上的页码数字行（纯数字）
        if re.fullmatch(r"\d{1,2}", ln):
            continue
        lines.append(norm_line(ln))
    return lines

html_lines = read_lines(os.path.join(BASE, "_align_html.txt"))
pdf_lines = read_lines(os.path.join(BASE, "_align_pdf.txt"))

sm = difflib.SequenceMatcher(None, html_lines, pdf_lines, autojunk=False)
opcodes = sm.get_opcodes()

diff_path = os.path.join(BASE, "_diff_align.txt")
with open(diff_path, "w", encoding="utf-8") as out:
    out.write(f"HTML lines={len(html_lines)}, PDF lines={len(pdf_lines)}\n")
    out.write(f"ratio={sm.ratio():.3f}\n\n")
    n_hunks = 0
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            continue
        n_hunks += 1
        out.write(f"----- {tag}: HTML[{i1}:{i2}] vs PDF[{j1}:{j2}] -----\n")
        for i in range(max(i1 - 2, 0), i2):
            out.write(f"  H> {html_lines[i]}\n" if i >= i1 else f"  H> {html_lines[i]}\n")
        out.write("  ---\n")
        for j in range(max(j1 - 2, 0), j2):
            out.write(f"  P> {pdf_lines[j]}\n" if j >= j1 else f"  P> {pdf_lines[j]}\n")
        out.write("\n")
    out.write(f"TOTAL HUNKS: {n_hunks}\n")
print("hunks:", n_hunks, "ratio:", round(sm.ratio(), 3))
