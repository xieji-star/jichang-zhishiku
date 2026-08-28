#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF 体检脚本：诊断 PDF 是否处于 Read 工具读取风险区（32MB 请求上限）。
用法: python pdf_diagnose.py <pdf路径>
输出: 页数 / 页面尺寸 / 文字字符 / 图片数 / 最大图宽 / 总像素 / 1x 1.5x 2x 渲染PNG体积 / 风险判定
依赖: PyMuPDF (pip install pymupdf)
"""
import sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import fitz  # PyMuPDF

MB = 1048576


def main():
    if len(sys.argv) < 2:
        print("用法: python pdf_diagnose.py <pdf路径>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"文件不存在: {path}")
        sys.exit(1)

    doc = fitz.open(path)
    pages = len(doc)
    rect = doc[0].rect
    text_chars = 0
    total_px = 0
    max_w = 0
    img_count = 0
    for page in doc:
        text_chars += len(page.get_text())
        for img in page.get_images(full=True):
            info = doc.extract_image(img[0])
            w, h = info["width"], info["height"]
            total_px += w * h
            max_w = max(max_w, w)
            img_count += 1

    sizes = {}
    for z in (1.0, 1.5, 2.0):
        sizes[z] = sum(
            len(doc[i].get_pixmap(matrix=fitz.Matrix(z, z)).tobytes("png"))
            for i in range(pages)
        )

    file_mb = os.path.getsize(path) / MB
    mb1x = sizes[1.0] / MB
    mb15x = sizes[1.5] / MB
    mb2x = sizes[2.0] / MB
    b64_1x = mb1x * 4 / 3

    print("=" * 50)
    print(f"文件: {os.path.basename(path)}")
    print(f"文件大小: {file_mb:.1f} MB")
    print(f"页数: {pages} 页, 页面尺寸: {rect.width:.0f}x{rect.height:.0f}pt")
    print(f"可选中文字: {text_chars} 字符")
    print(f"内嵌图片: {img_count} 张, 最大图宽: {max_w}px, 总像素: {total_px / 1e6:.1f} MP")
    print(f"渲染体积: 1x={mb1x:.1f}MB  1.5x={mb15x:.1f}MB  2x={mb2x:.1f}MB")
    if b64_1x >= 32:
        verdict = "❌ 高危: 单次读取必然报 Request too large, 需压缩+拆分"
    elif mb1x >= 20:
        verdict = f"⚠️ 中危: base64 后约 {b64_1x:.0f}MB, 逼近 32MB 上限, 建议预防性拆分"
    elif pages > 10:
        verdict = f"⚠️ 注意: 页数 {pages} > 10, 但渲染体积在安全线内 (base64 ~{b64_1x:.0f}MB)"
    else:
        verdict = f"✅ 安全: 渲染体积 base64 后约 {b64_1x:.0f}MB, 在读取范围内"
    print(f"风险判定: {verdict}")
    print("=" * 50)
    doc.close()


if __name__ == "__main__":
    main()
