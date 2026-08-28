# -*- coding: utf-8 -*-
"""检测基础 PDF 各部分起始页（base 0-based index）与截图数量"""
import os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

BASE = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽"
d = fitz.open(os.path.join(BASE, "_base.pdf"))
print("BASE PAGES:", d.page_count)

# 需要检测的锚点（按顺序）
anchors = [
    ("cover", "下一任对接文档"),
    ("toc", "目 录"),
    ("foreword", "先用三句话看懂这份工作"),
    ("part1", "第一部分：先搞懂这套业务"),
    ("part2", "第二部分：账号体系"),
    ("part3", "第三部分：一天的工作节奏"),
    ("part4", "第四部分：视频制作全流程"),
    ("part5", "第五部分：图文制作全流程"),
    ("part6", "第六部分：发布后运营"),
    ("part7", "第七部分：线索登记"),
    ("part8", "第八部分：脚本创作规范"),
    ("part9", "第九部分：工具怎么用"),
    ("part10", "第十部分：红线清单"),
    ("part11", "第十一部分：了解即可"),
    ("ending", "给你的最后一句话"),
]

norm = lambda s: re.sub(r"\s+", "", s)
page_texts = [norm(d[i].get_text()) for i in range(d.page_count)]

for name, needle in anchors:
    key = norm(needle)
    found = [i for i, t in enumerate(page_texts) if key in t]
    print(f"{name:10s} '{needle}' -> base idx {found[:2]}")

# 截图统计（非满页图片 = 截图）
total_shots = 0
for i in range(d.page_count):
    page = d[i]
    imgs = page.get_images(full=True)
    nbg = 0
    for x in imgs:
        rects = page.get_image_rects(x[0])
        for r in rects:
            if abs(r.width - 595) > 1 or abs(r.height - 842) > 1:
                nbg += 1
    if nbg:
        print(f"  page {i}: nonbg_images={nbg}")
    total_shots += nbg
print("TOTAL SCREENSHOTS:", total_shots)

# 每页链接统计
for i in range(d.page_count):
    links = d[i].get_links()
    if links:
        kinds = {}
        for l in links:
            k = l["kind"]
            kinds[k] = kinds.get(k, 0) + 1
        print(f"  page {i}: links {kinds}")
d.close()
