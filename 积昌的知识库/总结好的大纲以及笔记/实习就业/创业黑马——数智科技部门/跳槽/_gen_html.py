# -*- coding: utf-8 -*-
"""从 _doc_new.html 生成渲染用 _doc_render.html：
将 Part9 图文详解中的 __SHOT_*__ 占位符替换为 base64 内嵌截图
"""
import base64, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽"
SRC = os.path.join(BASE, "_doc_new.html")
DST = os.path.join(BASE, "_doc_render.html")

with open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

def b64img(relpath, mime):
    p = os.path.join(BASE, relpath)
    with open(p, "rb") as f:
        b = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b}"

# ---- Part9 截图占位符 -> base64 ----
g = os.path.join("下一任对接文档", "下一任对接文档")
shot_map = {
    "__SHOT_TTS1__": (f"{g}/TTS本地助手使用指南/1.png", "image/png"),
    "__SHOT_TTS2__": (f"{g}/TTS本地助手使用指南/2.png", "image/png"),
    "__SHOT_MM1__":  (f"{g}/Minimax使用指南/1.png", "image/png"),
    "__SHOT_HY1__":  (f"{g}/HeyGen使用指南/1.jpg", "image/jpeg"),
    "__SHOT_HY2__":  (f"{g}/HeyGen使用指南/2.jpg", "image/jpeg"),
    "__SHOT_HY3__":  (f"{g}/HeyGen使用指南/3.png", "image/png"),
    "__SHOT_HY4__":  (f"{g}/HeyGen使用指南/4.png", "image/png"),
    "__SHOT_HY5__":  (f"{g}/HeyGen使用指南/5.jpg", "image/jpeg"),
    "__SHOT_HY6__":  (f"{g}/HeyGen使用指南/6.jpg", "image/jpeg"),
    "__SHOT_HY7__":  (f"{g}/HeyGen使用指南/7.jpg", "image/jpeg"),
    "__SHOT_HY8__":  (f"{g}/HeyGen使用指南/8.jpg", "image/jpeg"),
    "__SHOT_SP1__":  (f"{g}/第6部分第三类用户示例插图.png", "image/png"),
    "__SHOT_G1__":   (f"{g}/6.5节插图.png", "image/png"),
    "__SHOT_FLOW1__": (f"{g}/抖音粉丝群建群流程/1.png", "image/png"),
    "__SHOT_FLOW2__": (f"{g}/抖音粉丝群建群流程/2.png", "image/png"),
    "__SHOT_FLOW3__": (f"{g}/抖音粉丝群建群流程/3.png", "image/png"),
    "__SHOT_FLOW4__": (f"{g}/抖音粉丝群建群流程/4.png", "image/png"),
    "__SHOT_FLOW5__": (f"{g}/抖音粉丝群建群流程/5.png", "image/png"),
}
for ph, (rel, mime) in shot_map.items():
    assert ph in html, f"占位符缺失: {ph}"
    html = html.replace(ph, b64img(rel, mime))
    print(f"  OK  {ph} -> {rel}")

# ---- .scr / .scr-fit CSS（幂等：不存在才插入） ----
# .scr 通用截图：宽 100%，用于横向/矮图；.scr-fit 竖屏长图：等比缩放限高居中，避免跨页拆分
if ".scr { width: 100%;" not in html:
    old_css = "  .shot-grid .shot { flex: 1 1 42%; }"
    new_css = old_css + "\n  .scr { width: 100%; border: 1px solid #d8d4cb; border-radius: 4px; margin: 6px 0 16px; display: block; }"
    new_css += "\n  .scr-fit { max-width: 100%; max-height: 730pt; width: auto; height: auto; border: 1px solid #d8d4cb; border-radius: 4px; margin: 6px auto 16px; display: block; }"
    assert old_css in html, ".shot-grid .shot CSS 未找到"
    html = html.replace(old_css, new_css)

# ---- 残留占位符检查（防漏） ----
import re as _re
leftover = _re.findall(r"__SHOT_[A-Z0-9]+__", html)
if leftover:
    raise SystemExit(f"ERROR: 残留占位符未替换 -> {sorted(set(leftover))}")

with open(DST, "w", encoding="utf-8") as f:
    f.write(html)

print("WROTE", DST)
print("HTML size:", os.path.getsize(DST), "bytes")
