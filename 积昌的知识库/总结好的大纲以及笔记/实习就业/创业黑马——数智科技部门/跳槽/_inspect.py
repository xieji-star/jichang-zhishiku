# -*- coding: utf-8 -*-
import fitz, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

src = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽\下一任对接文档\下一任对接文档\版本1.pdf"
d = fitz.open(src)
print("PAGES:", d.page_count)
print("TOC (bookmarks):")
for t in d.get_toc():
    print("   ", t)
print("--- per-page info ---")
for i in range(d.page_count):
    page = d[i]
    imgs = page.get_images(full=True)
    pix_rect = page.get_image_rects(imgs[0][0]) if imgs else []
    links = page.get_links()
    info = {"rect": str(page.rect), "n_images": len(imgs)}
    if pix_rect:
        info["first_img_rect"] = str(pix_rect[0])
    if links:
        info["n_links"] = len(links)
        info["first_link"] = {k: v for k, v in links[0].items() if k != "rect"}
    print(i, info)
d.close()
