# -*- coding: utf-8 -*-
"""从 _base.pdf 生成最终 版本1.pdf：
- 新页0：封面.png 铺满（无正文）
- base页 i -> 最终页 i+1：背景图(首页.png 或 内容页.png) + show_pdf_page 叠加 base 内容
- 链接手动从 base 页复制（show_pdf_page 在 PyMuPDF 1.28 不复制链接）：
    NAMED(kind=4) -> GOTO(kind=1)，page = base目标页 + 1（0-based 最终页码），to=(0,0)
    LAUNCH(kind=3, file://) -> GOTOR(kind=5) 匹配参考版，file 原样传入（fitz 会自动编码）
    URI(kind=2) 原样保留
- 设置书签（set_toc，1-based 页码 = base页 + 2，因为封面占第 1 页）
"""
import fitz, os, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽"
BG = r"F:\积昌的知识库 - 副本\_preview_bg"
SRC = os.path.join(BASE, "_base.pdf")
DST = os.path.join(BASE, "下一任对接文档", "下一任对接文档", "版本1.pdf")
COVER = os.path.join(BASE, "下一任对接文档", "封面1.png")

d = fitz.open(SRC)

# named destinations: name -> base page (0-based)
nm = d.resolve_names() or {}
name_to_page = {k: v["page"] for k, v in nm.items()}

out = fitz.open()

# ---------- 1) 封面页（最终 0-based 页 0） ----------
p0 = out.new_page(width=595, height=842)
p0.insert_image(fitz.Rect(0.0, 0.5404, 594.96, 841.3796),
                filename=COVER, keep_proportion=False)

cover_img = os.path.join(BG, "首页.png")     # 用于 base 第 0 页（HTML封面）
content_img = os.path.join(BG, "内容页.png")  # 用于 base 第 1+ 页

def copy_links(base_page, out_page):
    """把 base 页链接复制到输出页，做类型/页码转换"""
    for link in base_page.get_links():
        kind = link["kind"]
        rect = link["from"]
        if kind == 4:  # NAMED -> GOTO
            name = link.get("nameddest")
            target = name_to_page.get(name)
            if target is None:
                continue
            out_page.insert_link({
                "kind": 1,
                "from": rect,
                "page": target + 1,        # 0-based 最终页码
                "to": fitz.Point(0, 0),
            })
        elif kind == 3:  # LAUNCH(file://) -> GOTOR，匹配参考版
            f = link.get("file", "")
            if not f:
                continue
            out_page.insert_link({
                "kind": 5,
                "from": rect,
                "file": f,                 # 原样传入，fitz 自动 URL 编码
                "page": 0,
                "to": fitz.Point(0, 0),
            })
        elif kind == 2:  # URI 原样
            out_page.insert_link({
                "kind": 2,
                "from": rect,
                "uri": link["uri"],
            })
        elif kind == 1:  # GOTO 页码整体 +1（封面占位）
            out_page.insert_link({
                "kind": 1,
                "from": rect,
                "page": link["page"] + 1,
                "to": link.get("to", fitz.Point(0, 0)),
            })
        # 其他 kind 忽略

# ---------- 2) 第一遍：先建好所有页（封面 + base 叠加） ----------
for i in range(d.page_count):
    page = out.new_page(width=595, height=842)
    if i == 0:
        page.insert_image(fitz.Rect(-18.24, 0.0, 613.2, 841.92), filename=cover_img, keep_proportion=False)
    else:
        page.insert_image(fitz.Rect(0.0, 0.0, 594.96, 841.92), filename=content_img, keep_proportion=False)
    page.show_pdf_page(fitz.Rect(0, 0, 595, 842), d, i)

# ---------- 3) 第二遍：所有页存在后，复制链接 ----------
for i in range(d.page_count):
    copy_links(d[i], out[i + 1])  # base i -> 最终 0-based 页 i+1

# ---------- 3) 书签：动态检测章节起始页 ----------
# (显示标题, 归一化锚点文本)。正文 h2 不带全角冒号，目录页带冒号，故锚点能跳过目录页。
BOOKMARKS = [
    ("写在前面：先用三句话看懂这份工作", "写在前面先用三句话看懂这份工作"),
    ("第一部分：先搞懂这套业务（业务逻辑）", "第一部分先搞懂这套业务"),
    ("第二部分：账号体系（矩阵账号）", "第二部分账号体系"),
    ("第三部分：一天的工作节奏（总览）", "第三部分一天的工作节奏"),
    ("第四部分：视频制作全流程（重点）", "第四部分视频制作全流程"),
    ("第五部分：图文制作全流程", "第五部分图文制作全流程"),
    ("第六部分：发布后运营（把人聊过来）", "第六部分发布后运营"),
    ("第七部分：线索登记（灯塔系统录入）", "第七部分线索登记"),
    ("第八部分：脚本创作规范", "第八部分脚本创作规范"),
    ("第九部分：工具怎么用（保姆级清单）", "第九部分工具怎么用"),
    ("第十部分：红线清单（这些坑千万别踩）", "第十部分红线清单"),
    ("第十一部分：了解即可（业务线全貌）", "第十一部分了解即可"),
    ("给你的最后一句话", "给你的最后一句话"),
]

norm = lambda s: re.sub(r"\s+", "", s)
page_texts = [norm(d[i].get_text()) for i in range(d.page_count)]

toc = []
for title, key in BOOKMARKS:
    k = norm(key)
    found = [i for i, t in enumerate(page_texts) if i > 1 and k in t]
    if not found:
        raise SystemExit(f"ERROR: 未检测到章节 '{title}' (锚点 {key!r})")
    base = found[0]
    toc.append([1, title, base + 2])  # 1-based 最终页码 = base 页 + 2（封面占第 1 页）
    print(f"  bookmark '{title}' -> final page {base+2} (base {base})")
out.set_toc(toc)

out.save(DST, garbage=4, deflate=True)
out.close()
d.close()
print("WROTE", DST)
v = fitz.open(DST)
print("PAGES:", v.page_count, "size:", os.path.getsize(DST))
print("bookmarks:", len(v.get_toc()))
nlinks = sum(len(v[i].get_links()) for i in range(v.page_count))
print("total links:", nlinks)
v.close()
