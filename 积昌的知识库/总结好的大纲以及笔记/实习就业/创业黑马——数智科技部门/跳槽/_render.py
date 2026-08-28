# -*- coding: utf-8 -*-
"""用 Edge headless 将 HTML 渲染为 PDF（修复版）"""
import os, subprocess, tempfile
from urllib.parse import quote

BASE = r"F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\创业黑马——数智科技部门\跳槽"
html_path = os.path.join(BASE, "_doc_render.html")
out_pdf = os.path.join(BASE, "_base.pdf")

# Windows file URI: 冒号/斜杠保持字面，空格与中文转义
fwd = html_path.replace("\\", "/")
file_uri = "file:///" + quote(fwd, safe="/:")

edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
profile = tempfile.mkdtemp(prefix="edgeprof_")

if os.path.exists(out_pdf):
    os.remove(out_pdf)

cmd = [
    edge,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    f"--user-data-dir={profile}",
    f"--print-to-pdf={out_pdf}",
    file_uri,
]
print("CMD_ARGS:")
for a in cmd:
    print("  ", a)
r = subprocess.run(cmd, capture_output=True, text=False, timeout=180)
print("returncode:", r.returncode)
err = r.stderr.decode("utf-8", errors="replace") if r.stderr else ""
print("stderr tail:", err[-400:])
if os.path.exists(out_pdf):
    print("OK size:", os.path.getsize(out_pdf))
else:
    print("FAIL: no output pdf")
