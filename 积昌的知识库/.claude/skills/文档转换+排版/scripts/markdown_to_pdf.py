#!/usr/bin/env python3
"""
文档转换+排版 — Markdown 转 PDF 引擎
根据固定排版模板将结构化 Markdown 转换为精美 PDF。
"""
import os, re, sys, tempfile, argparse, json
import matplotlib
import matplotlib.pyplot as plt
from fpdf import FPDF

matplotlib.rcParams['font.family'] = 'sans-serif'

# ============================================================
# 配置（与 Skill 排版模板一致）
# ============================================================
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD_PATH = r"C:\Windows\Fonts\msyhbd.ttc"
BG_PATH = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\工作文件\PDF资料集/bg_enhanced.jpg"

PAGE_W = 210
PAGE_H = 297
MARGIN_L = 15
MARGIN_R = 15
MARGIN_T = 5
MARGIN_B = 12
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R  # 180mm

# 行距
BODY_FONT_SZ = 11
BODY_LH = 8.0
TITLE_FONT_SZ = 16
TITLE_LH = 12.0
SUB_FONT_SZ = 13
SUB_LH = 10.0

MATH_TOP = 3.5
MATH_BOT = 3.5
MATH_MULTI_LH = 10.0
BULLET_INDENT = 7
BOX_LH = 4.5
BOX_TOP = 2
BOX_BOT = 1.5
SEC_GAP = 2.5
SUB_GAP = 1.5

# 颜色
BLUE_TITLE = (10, 38, 92)
BLUE_SUB = (14, 48, 115)
BLACK = (0, 0, 0)
LOGO_RED = (238, 53, 35)
HL_FILL = (205, 220, 240)
HL_BORDER = (90, 140, 195)


# ============================================================
# 数学公式渲染
# ============================================================
def _render_math(formula, fontsize=20, dpi=200):
    formula = re.sub(r'\\le(?!\w)', r'\\leq', formula)
    fig_test, ax_test = plt.subplots(figsize=(10, 0.5))
    t = ax_test.text(0, 0.5, f'${formula}$', fontsize=fontsize)
    ax_test.axis('off')
    fig_test.canvas.draw()
    renderer = fig_test.canvas.get_renderer()
    bbox = t.get_window_extent(renderer)
    plt.close(fig_test)
    text_w_inch = bbox.width / fig_test.dpi + 0.4
    fig_w = min(text_w_inch, CONTENT_W / 25.4)
    fig_h = 0.7
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.text(0.5, 0.5, f'${formula}$', ha='center', va='center',
            fontsize=fontsize, transform=ax.transAxes)
    ax.axis('off')
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)
    plt.savefig(path, dpi=dpi, bbox_inches='tight',
                transparent=True, pad_inches=0.08)
    plt.close(fig)
    img = matplotlib.image.imread(path)
    h_px, w_px = img.shape[:2]
    mm_per = 25.4 / dpi
    return path, w_px * mm_per, h_px * mm_per


def _render_multiline_math(formulas, fontsize=20, dpi=200):
    formulas = [re.sub(r'\\le(?!\w)', r'\\leq', f) for f in formulas]
    n = len(formulas)
    fig_w = CONTENT_W / 25.4
    fig_h = (MATH_MULTI_LH / 25.4) * (n - 1) + 0.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    spacing = 1.0 / (n + 0.5)
    for i, f in enumerate(formulas):
        y = 1.0 - (i + 0.5) * spacing
        ax.text(0.5, y, f'${f}$', ha='center', va='center',
                fontsize=fontsize, transform=ax.transAxes)
    ax.axis('off')
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)
    plt.savefig(path, dpi=dpi, bbox_inches='tight',
                transparent=True, pad_inches=0.08)
    plt.close(fig)
    img = matplotlib.image.imread(path)
    h_px, w_px = img.shape[:2]
    mm_per = 25.4 / dpi
    return path, w_px * mm_per, h_px * mm_per


# ============================================================
# PDF 生成器
# ============================================================
class FormattedPDF(FPDF):
    def __init__(self):
        super().__init__(unit='mm', format='A4')
        self.set_auto_page_break(True, MARGIN_B)
        self.set_margins(MARGIN_L, MARGIN_T, MARGIN_R)
        self.set_top_margin(MARGIN_T)
        self.add_font('CN', '', FONT_PATH)
        self.add_font('CN', 'B', FONT_BOLD_PATH)
        self._temp_files = []

    def _cleanup(self):
        for f in self._temp_files:
            try:
                if os.path.exists(f): os.remove(f)
            except: pass

    def _add_temp(self, path):
        self._temp_files.append(path)
        return path

    def _reset_x(self):
        self.set_x(MARGIN_L)

    def header(self):
        if os.path.exists(BG_PATH):
            self.image(BG_PATH, x=0, y=0, w=PAGE_W, h=PAGE_H)

    def main_title(self, text, subtitle='', author=''):
        """文档大标题：22pt 深蓝加粗居中"""
        self._reset_x()
        self.set_font('CN', 'B', 22)
        self.set_text_color(*BLUE_TITLE)
        self.multi_cell(CONTENT_W, 16, text, align='C')
        if subtitle:
            self._reset_x()
            self.set_font('CN', 'B', 12)
            self.set_text_color(*BLACK)
            self.multi_cell(CONTENT_W, 7, subtitle, align='C')
            self.ln(3)
        if author:
            self._reset_x()
            self.set_font('CN', '', TITLE_FONT_SZ)
            self.set_text_color(120, 120, 120)
            self.cell(CONTENT_W, 10, author, align='C', new_x="LMARGIN")
            self.ln(14)
        self.set_text_color(*BLACK)

    def sec_title(self, number, title):
        """一级标题：16pt 深蓝加粗"""
        self._reset_x()
        self.set_font('CN', 'B', TITLE_FONT_SZ)
        self.set_text_color(*BLUE_TITLE)
        label = f'{number}  {title}' if number else title
        self.multi_cell(CONTENT_W, TITLE_LH, label, align='L')
        self._reset_x()
        self.ln(SEC_GAP)
        self.set_text_color(*BLACK)

    def sub_title(self, number, title):
        """二级标题：13pt 中蓝加粗"""
        self._reset_x()
        self.set_font('CN', 'B', SUB_FONT_SZ)
        self.set_text_color(*BLUE_SUB)
        label = f'{number} {title}' if number else title
        self.multi_cell(CONTENT_W, SUB_LH, label, align='L')
        self._reset_x()
        self.ln(SUB_GAP)
        self.set_text_color(*BLACK)

    def text(self, text):
        """正文：11pt 纯黑"""
        self._reset_x()
        self.set_font('CN', '', BODY_FONT_SZ)
        t = text.replace('ᵈ', '^d')
        self.multi_cell(CONTENT_W, BODY_LH, t, align='L')
        self._reset_x()

    def label(self, text):
        """加粗标签"""
        self._reset_x()
        self.set_font('CN', 'B', BODY_FONT_SZ)
        self.set_text_color(*BLACK)
        self.multi_cell(CONTENT_W, BODY_LH, text, align='L')
        self._reset_x()

    def bullet(self, text):
        """要点"""
        self._reset_x()
        self.set_font('CN', '', BODY_FONT_SZ)
        self.set_x(MARGIN_L + BULLET_INDENT)
        self.multi_cell(CONTENT_W - BULLET_INDENT, BODY_LH, '● ' + text, align='L')
        self._reset_x()

    def numbered(self, num, text):
        """编号列表项：11pt 纯黑，独立段落"""
        self._reset_x()
        self.set_font('CN', '', BODY_FONT_SZ)
        t = f'{num} {text}'
        self.multi_cell(CONTENT_W, BODY_LH, t, align='L')
        self._reset_x()

    def math(self, formula):
        """公式居中"""
        self.ln(MATH_TOP)
        path, w_mm, h_mm = self._add_temp(_render_math(formula))
        if w_mm > CONTENT_W:
            s = CONTENT_W / w_mm
            w_mm *= s; h_mm *= s
        x_offset = (CONTENT_W - w_mm) / 2
        self.set_x(MARGIN_L + x_offset)
        self.image(path, w=w_mm, h=h_mm)
        self.ln(h_mm + MATH_BOT)
        self._reset_x()

    def math_multi(self, formulas):
        """多行公式"""
        self.ln(MATH_TOP)
        path, w_mm, h_mm = self._add_temp(_render_multiline_math(formulas))
        if w_mm > CONTENT_W:
            s = CONTENT_W / w_mm
            w_mm *= s; h_mm *= s
        x_offset = (CONTENT_W - w_mm) / 2
        self.set_x(MARGIN_L + x_offset)
        self.image(path, w=w_mm, h=h_mm)
        self.ln(h_mm + MATH_BOT)
        self._reset_x()

    def highlight(self, text):
        """高亮框"""
        self.set_font('CN', 'B', BODY_FONT_SZ)
        cpl = max(1, int((CONTENT_W - 6) / (BODY_FONT_SZ * 0.3528 * 0.55)))
        est_lines = max(1, (len(text) + cpl - 1) // cpl)
        est_h = est_lines * BOX_LH + BOX_TOP + BOX_BOT + 1.0
        if self.get_y() + est_h > self.h - MARGIN_B:
            self.add_page()
        self.ln(BOX_TOP)
        y0 = self.get_y()
        self.set_x(MARGIN_L + 3)
        self.multi_cell(CONTENT_W - 6, BOX_LH, text, align='L')
        y1 = self.get_y()
        box_h = y1 - y0 + 1.0
        self.set_fill_color(*HL_FILL)
        self.set_draw_color(*HL_BORDER)
        self.rect(MARGIN_L, y0, CONTENT_W, box_h, style='DF')
        self.set_xy(MARGIN_L + 3, y0 + 0.5)
        self.multi_cell(CONTENT_W - 6, BOX_LH, text, align='L')
        self._reset_x()
        self.ln(BOX_BOT)

    def writing_reminder(self, title='写作提醒', lines=None):
        """红色写作提醒"""
        if lines is None:
            lines = []
        self.ln(4)
        self.set_x(MARGIN_L)
        self.set_text_color(*LOGO_RED)
        self.set_font('CN', 'B', TITLE_FONT_SZ)
        self.multi_cell(CONTENT_W, TITLE_LH, title, align='C')
        self.set_text_color(*LOGO_RED)
        self.set_font('CN', '', BODY_FONT_SZ)
        for line in lines:
            self.set_x(MARGIN_L)
            # 先测宽度：能一行显示就用 cell()，超宽再用 multi_cell() 自动换行
            if self.get_string_width(line) <= CONTENT_W:
                self.cell(CONTENT_W, BODY_LH, line, align='L',
                          new_x="LMARGIN", new_y="NEXT")
            else:
                self.multi_cell(CONTENT_W, BODY_LH, line, align='L')


# ============================================================
# 内联 Markdown 清洗 — 去除文本中的 **、` 等语法符号
# ============================================================
def clean_inline_markdown(text):
    """去除文本中的内联 Markdown 语法符号，保留纯文本内容。"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold** → bold
    text = re.sub(r'`([^`]+)`', r'\1', text)       # `code` → code
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'\1', text)  # *italic* → italic
    return text


def clean_content(content):
    """对解析后的内容列表应用清洗，去除 Markdown 语法符号。"""
    for item in content:
        if item['type'] == 'text':
            item['text'] = clean_inline_markdown(item['text'])
        elif item['type'] == 'bullet':
            item['text'] = clean_inline_markdown(item['text'])
        elif item['type'] == 'numbered':
            item['text'] = clean_inline_markdown(item['text'])
        elif item['type'] == 'label':
            item['text'] = clean_inline_markdown(item['text'])
        elif item['type'] == 'highlight':
            item['text'] = clean_inline_markdown(item['text'])
        elif item['type'] == 'writing_reminder':
            item['title'] = clean_inline_markdown(item['title'])
            item['lines'] = [clean_inline_markdown(l) for l in item['lines']]
        elif item['type'] == 'sub_title':
            item['title'] = clean_inline_markdown(item['title'])
        elif item['type'] == 'sec_title':
            item['title'] = clean_inline_markdown(item['title'])
        # math / math_multi 类型不处理（保留公式内容）
    return content


# ============================================================
# Markdown 解析器
# ============================================================
def parse_markdown(filepath):
    """解析 Markdown 文件，返回结构化内容列表。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    content = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # 空行
        if not line:
            i += 1
            continue

        # 文档大标题 (h1 with #)
        if line.startswith('# ') and not line.startswith('## '):
            text = line[2:].strip()
            # Check for subtitle on next line
            subtitle = ''
            author = ''
            if i + 1 < len(lines) and lines[i+1].strip().startswith('-- '):
                subtitle = lines[i+1].strip()[3:]
                i += 1
            if i + 1 < len(lines) and lines[i+1].strip().startswith('著作人：'):
                author = lines[i+1].strip()  # 保留"著作人："前缀
                i += 1
            elif i + 1 < len(lines) and lines[i+1].strip().startswith('编著：'):
                author = lines[i+1].strip()  # 保留"编著："前缀
                i += 1
            elif i + 1 < len(lines) and lines[i+1].strip().startswith('作者：'):
                author = lines[i+1].strip()[3:]  # 兼容"作者："前缀，去除前缀
                i += 1
            content.append({'type': 'main_title', 'text': text,
                           'subtitle': subtitle, 'author': author})
            i += 1
            continue

        # 一级标题 (##)
        if line.startswith('## '):
            text = line[3:].strip()
            # Extract number prefix like "第1部分" or "1."
            number = ''
            title_text = text
            # Try to match "数字. " or "第X部分" pattern
            m = re.match(r'^(第[\d]+部分|\d+[\.、])\s*(.*)', text)
            if m:
                number = m.group(1)
                title_text = m.group(2)
            content.append({'type': 'sec_title', 'number': number, 'title': title_text})
            i += 1
            continue

        # 二级标题 (###)
        if line.startswith('### '):
            text = line[4:].strip()
            number = ''
            title_text = text
            m = re.match(r'^([\d]+\.[\d]+)\s*(.*)', text)
            if m:
                number = m.group(1)
                title_text = m.group(2)
            content.append({'type': 'sub_title', 'number': number, 'title': title_text})
            i += 1
            continue

        # 公式 $$ ... $$（支持同行或跨行）
        if line.startswith('$$'):
            remainder = line[2:].strip()
            formulas = []
            # Check if closing $$ is on the same line
            if '$$' in remainder:
                formula_text = remainder.replace('$$', '').strip()
                if formula_text:
                    formulas.append(formula_text)
                i += 1
            else:
                if remainder:
                    formulas.append(remainder)
                i += 1
                while i < len(lines):
                    line = lines[i].strip()
                    if line.startswith('$$'):
                        break
                    if line:
                        formulas.append(line)
                    i += 1
                i += 1
            if len(formulas) == 1:
                content.append({'type': 'math', 'formula': formulas[0]})
            else:
                content.append({'type': 'math_multi', 'formulas': formulas})
            continue

        # 高亮块 >highlight
        if line.startswith('>highlight'):
            text_after = line[len('>highlight'):].strip()
            texts = [text_after] if text_after else []
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line or line.startswith('#'):
                    break
                texts.append(line)
                i += 1
            content.append({'type': 'highlight', 'text': '\n'.join(texts)})
            continue

        # 分隔符 --- 作为写作提醒标记
        if line.strip() == '---':
            i += 1
            # 跳过空行，找到实际的标题行
            while i < len(lines) and not lines[i].strip():
                i += 1
            title_line = ''
            body_lines = []
            if i < len(lines):
                title_line = lines[i].strip()
                i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                # 遇到下一级标题或另一个分隔符 → 停止，让外层循环处理
                if line.startswith('#') or line == '---':
                    break
                body_lines.append(line)
                i += 1
            content.append({'type': 'writing_reminder',
                           'title': title_line or '写作提醒',
                           'lines': body_lines})
            continue

        # 列表项 -
        if line.startswith('- '):
            text = line[2:].strip()
            content.append({'type': 'bullet', 'text': text})
            i += 1
            continue

        # 编号列表项（如 "1. ", "2. "）— 独立段落，不合并
        m = re.match(r'^(\d+\.)\s+(.*)', line)
        if m:
            num = m.group(1)
            text = m.group(2)
            content.append({'type': 'numbered', 'number': num, 'text': text})
            i += 1
            continue

        # **加粗标签** — 支持 **标签：** 内容... 格式
        if line.startswith('**') and '**' in line[2:]:
            close_pos = line.find('**', 2)
            if close_pos != -1:
                label_text = line[2:close_pos].strip()
                rest_text = line[close_pos+2:].strip()
                if rest_text:
                    text = label_text + ' ' + rest_text
                else:
                    text = label_text
            else:
                text = line.strip('*').strip()
            content.append({'type': 'label', 'text': text})
            i += 1
            continue

        # 普通正文（合并相邻行）
        para_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i].rstrip()
            if not next_line or next_line.startswith('#') or \
               next_line.startswith('$$') or next_line.startswith('>') or \
               next_line.startswith('- ') or next_line.startswith('**') or \
               next_line.strip() == '---':
                break
            para_lines.append(next_line)
            i += 1
        text = ''.join(para_lines)
        if text.strip():
            content.append({'type': 'text', 'text': text.strip()})

    return content


# ============================================================
# 构建 PDF
# ============================================================
def build_pdf_from_content(content, output_path):
    pdf = FormattedPDF()
    pdf.add_page()

    for item in content:
        t = item['type']
        if t == 'main_title':
            pdf.main_title(item['text'], item.get('subtitle', ''),
                          item.get('author', ''))
        elif t == 'sec_title':
            pdf.sec_title(item['number'], item['title'])
        elif t == 'sub_title':
            pdf.sub_title(item['number'], item['title'])
        elif t == 'text':
            pdf.text(item['text'])
        elif t == 'label':
            pdf.label(item['text'])
        elif t == 'bullet':
            pdf.bullet(item['text'])
        elif t == 'numbered':
            pdf.numbered(item['number'], item['text'])
        elif t == 'math':
            pdf.math(item['formula'])
        elif t == 'math_multi':
            pdf.math_multi(item['formulas'])
        elif t == 'highlight':
            pdf.highlight(item['text'])
        elif t == 'writing_reminder':
            pdf.writing_reminder(item.get('title', '写作提醒'),
                                item.get('lines', []))

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    pdf.output(output_path)
    pdf._cleanup()
    return output_path


# ============================================================
# 主入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='Markdown → 排版 PDF')
    parser.add_argument('--input', '-i', required=True,
                        help='输入 Markdown 文件路径')
    parser.add_argument('--output', '-o', required=True,
                        help='输出 PDF 文件路径')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'错误：输入文件不存在：{args.input}')
        sys.exit(1)

    content = parse_markdown(args.input)
    content = clean_content(content)  # 去除内联 Markdown 语法符号
    result = build_pdf_from_content(content, args.output)
    print(f'PDF 已生成：{result}')


if __name__ == '__main__':
    main()
