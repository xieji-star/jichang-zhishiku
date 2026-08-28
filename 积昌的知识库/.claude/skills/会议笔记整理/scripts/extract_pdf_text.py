#!/usr/bin/env python3
"""
PDF Text Extractor for meeting-summary skill
提取 PDF 文本内容，支持编码处理和 Type3 字体降级。

Usage:
    python3 extract_pdf_text.py <pdf_path> [--output <output_path>] [--render-images]

Options:
    --output <path>      将文本保存到文件（避免终端编码问题）
    --render-images      当文字提取为乱码时，将页面渲染为图片
    --dpi <dpi>          图片渲染分辨率（默认 200）
"""

import fitz
import sys
import os
import argparse


def extract_text(pdf_path: str, output_path: str = None):
    """从 PDF 提取文本内容"""
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    print(f"Total pages: {total_pages}", file=sys.stderr)

    all_text = []
    for i in range(total_pages):
        text = doc[i].get_text('text')
        all_text.append(f"=== Page {i+1} ===\n{text}" if text.strip() else f"=== Page {i+1}: [No text] ===")

    doc.close()

    output = '\n\n'.join(all_text)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Text saved to: {output_path}", file=sys.stderr)
    else:
        print(output)

    return output


def render_pages(pdf_path: str, output_dir: str, dpi: int = 200):
    """将 PDF 页面渲染为图片（用于 OCR 降级）"""
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pages = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.png")
        pix.save(img_path)
        pages.append(img_path)
        print(f"Saved: {img_path} ({pix.width}x{pix.height})", file=sys.stderr)

    doc.close()
    print(f"\nRendered {len(pages)} pages to: {output_dir}", file=sys.stderr)
    return pages


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF files")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Output text file path")
    parser.add_argument("--render-images", action="store_true",
                        help="Render pages as images even if text extraction succeeds")
    parser.add_argument("--dpi", type=int, default=200,
                        help="DPI for image rendering (default: 200)")
    parser.add_argument("--check-type3", action="store_true",
                        help="Check if PDF uses Type3 fonts")

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: File not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    # 先尝试提取文本
    print(f"Extracting text from: {args.pdf_path}", file=sys.stderr)
    text = extract_text(args.pdf_path, args.output)

    # 检查是否包含太多不可读字符
    garbled_ratio = sum(1 for c in text if ord(c) > 0xFFFD or c == '�') / max(len(text), 1)
    print(f"Garbled character ratio: {garbled_ratio:.2%}", file=sys.stderr)

    if garbled_ratio > 0.05 or args.render_images:
        print("\nText may be garbled (Type3 fonts detected). Rendering pages as images...", file=sys.stderr)
        output_dir = os.path.join(os.path.dirname(args.output) if args.output else '.',
                                  f"{os.path.splitext(os.path.basename(args.pdf_path))[0]}_pages")
        render_pages(args.pdf_path, output_dir, args.dpi)
    else:
        print(f"Text extraction successful. {len(text)} characters.", file=sys.stderr)


if __name__ == "__main__":
    main()
