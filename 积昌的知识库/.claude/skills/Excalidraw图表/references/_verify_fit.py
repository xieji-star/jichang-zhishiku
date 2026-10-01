# -*- coding: utf-8 -*-
"""校验：把场景渲染成 SVG 后，检查每个 text 节点的真实包围盒是否被其所属批注框完全包住。

用法：uv run python _verify_fit.py <scene.excalidraw> <box_width>
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#fff}</style></head>
<body><div id="root"></div>
<script type="module">
let exportToSvg = null;
try {
  const m = await import("https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle");
  exportToSvg = m.exportToSvg;
  window.__ready = true;
} catch (e) { window.__ready = false; window.__err = e.message; }

window.analyze = async function(scene) {
  const svg = await exportToSvg({
    elements: scene.elements,
    appState: Object.assign({}, scene.appState, {exportBackground: true}),
    files: scene.files || {}
  });
  document.getElementById("root").innerHTML = "";
  document.getElementById("root").appendChild(svg);

  // 用 getBoundingClientRect 取得经全部 transform 后的真实屏幕坐标，
  // 再减去 svg 原点，得到 SVG 用户坐标（1 单位 = 1 CSS px，无缩放）。
  const origin = svg.getBoundingClientRect();
  const nodes = Array.from(svg.querySelectorAll("text"));
  const out = nodes.map(function(t){
    const r = t.getBoundingClientRect();
    return {x: r.left - origin.left, y: r.top - origin.top,
            r: r.right - origin.left, bot: r.bottom - origin.top,
            text: (t.textContent||"").slice(0,26)};
  });
  return {nodes: out, svg_w: +svg.getAttribute("width"), svg_h: +svg.getAttribute("height")};
};
</script></body></html>
"""


def main():
    scene_path = Path(sys.argv[1])
    box_w = float(sys.argv[2])
    scene = json.loads(scene_path.read_text(encoding="utf-8"))

    from playwright.sync_api import sync_playwright
    tmp = Path(__file__).parent / "_verify_fit.html"
    tmp.write_text(HTML, encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 2200})
        try:
            page.goto(tmp.as_uri())
            page.wait_for_function("window.__ready === true", timeout=120000)
            res = page.evaluate("(s) => window.analyze(s)", scene)
        finally:
            browser.close()
            if tmp.exists():
                tmp.unlink()

    PAD0 = 10.0   # exportPadding，场景坐标 -> SVG 坐标的平移量
    # 批注框（场景坐标 -> SVG 坐标）
    boxes = []
    for e in scene["elements"]:
        if e.get("type") == "rectangle" and abs(e.get("width", 0) - box_w) < 1:
            boxes.append((e["x"] + PAD0, e["y"] + PAD0, e["width"], e["height"]))

    bad = []
    checked = 0
    max_h_margin = 1e9
    min_r_slack = 1e9
    min_r_where = ""
    for n in res["nodes"]:
        sx, sy = n["x"], n["y"]                    # SVG 坐标（= 场景坐标 + 10）
        # 找包住它顶边的框
        cand = [b for b in boxes if b[1] - 0.6 <= sy <= b[1] + b[3] + 0.6]
        if not cand:
            continue
        bx, by, bw, bh = min(cand, key=lambda b: abs(b[1] - sy))
        checked += 1
        issues = []
        if sx < bx - 0.6:
            issues.append(f"左溢出 {(bx - sx):.1f}px")
        if n["r"] > bx + bw + 0.6:
            issues.append(f"右溢出 {(n['r'] - (bx + bw)):.1f}px")
        if (bx + bw) - n["r"] < min_r_slack:
            min_r_slack = (bx + bw) - n["r"]
            min_r_where = n["text"]
        if sy < by - 0.6:
            issues.append(f"上溢出 {(by - sy):.1f}px")
        if n["bot"] > by + bh + 0.6:
            issues.append(f"下溢出 {(n['bot'] - (by + bh)):.1f}px")
        else:
            max_h_margin = min(max_h_margin, (by + bh) - n["bot"])
        if issues:
            bad.append((n["text"], issues, round(sx, 1), round(n["r"], 1), round(bx, 1), round(bx + bw, 1)))

    print(f"[{scene_path.name}] 框 {len(boxes)} 个，受检文本 {checked} 个，"
          f"框底最小余量 {max_h_margin:.1f}px，框右最小余量 {min_r_slack:.1f}px  {min_r_where!r}")
    if bad:
        print(f"   !! {len(bad)} 处文字未被框包住：")
        for t, iss, sx, r, bx, br in bad:
            print(f"      {t!r}  x[{sx},{r}] 框[{bx},{br}]  {' / '.join(iss)}")
    else:
        print("   ✓ 全部文字均被批注框完整包住")


if __name__ == "__main__":
    main()
