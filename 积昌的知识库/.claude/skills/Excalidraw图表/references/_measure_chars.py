# -*- coding: utf-8 -*-
"""用真实字体（Excalidraw 导出时所用的同一套字体栈）实测每个字符的渲染宽度。

用法（在 references/ 目录下，走 uv 环境）：
    uv run python _measure_chars.py <in_chars.json> <out_metrics.json>

in : {"combos":[{"fs":42,"fam":2},...], "chars":["a","字",...]}
out: {"42|2": {"a": 23.1, ...}, ...}   # 单位 = 场景 px（= SVG px）
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#fff}</style></head>
<body><div id="root"></div><div id="fonts" style="position:absolute;left:-99999px;top:0"></div>
<script type="module">
let exportToSvg = null;
try {
  const m = await import("https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle");
  exportToSvg = m.exportToSvg;
  window.__ready = true;
} catch (e) { window.__ready = false; window.__err = e.message; }

function mkText(fam, fs, x) {
  return {type:"text", id:"probe"+fam+"_"+fs, x:x, y:0, width:200, height:40, angle:0,
    strokeColor:"#000000", backgroundColor:"transparent", fillStyle:"solid",
    strokeWidth:1, strokeStyle:"solid", roughness:0, opacity:100, groupIds:[],
    seed:1, version:1, versionNonce:1, isDeleted:false, boundElements:null,
    link:null, locked:false, fontSize:fs, fontFamily:fam, textAlign:"left",
    verticalAlign:"top", containerId:null, lineHeight:1.25, text:"Ag", originalText:"Ag"};
}

// 探测 Excalidraw 导出时给各 fontFamily 实际使用的字体栈。
// 关键：把导出的 svg 挂进文档，导出内嵌的 @font-face（Virgil 等）才会注册生效。
window.probe = async function(combos) {
  const res = {};
  const host = document.getElementById("fonts");
  for (const c of combos) {
    const svg = await exportToSvg({
      elements: [mkText(c.fam, c.fs, 0)],
      appState: {exportBackground:true, viewBackgroundColor:"#ffffff"}, files: {}});
    host.appendChild(svg);                       // ← 注册 @font-face
    const t = svg.querySelector("text");
    res[c.fs + "|" + c.fam] = t ? {
      family: t.getAttribute("font-family"),
      size:   t.getAttribute("font-size"),
      ls:     t.getAttribute("letter-spacing"),
      style:  t.getAttribute("style")
    } : null;
  }
  await document.fonts.ready;                    // ← 等字体真正下载/解析完成
  return res;
};

// 确认字体是否真的可用
window.fontCheck = function() {
  return {
    virgil: document.fonts.check('23px Virgil'),
    loaded: Array.from(document.fonts).map(f => f.family + ":" + f.status)
  };
};

// 按真实字体栈逐个字符量宽
window.measure = function(items, fontByKey) {
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", "6000"); svg.setAttribute("height", "200");
  svg.setAttribute("xmlns", NS);
  document.body.appendChild(svg);
  const out = [];
  for (const it of items) {
    const t = document.createElementNS(NS, "text");
    t.setAttribute("font-family", fontByKey[it.key].family || "sans-serif");
    t.setAttribute("font-size", it.fs + "px");
    // 关键：Excalidraw 导出时给 text 加了 white-space: pre，空格才不会被折叠。
    // 不设这一条，空格量出来是 0，整行宽度会被严重低估。
    t.setAttribute("style", "white-space: pre;");
    if (fontByKey[it.key].ls) t.setAttribute("letter-spacing", fontByKey[it.key].ls);
    t.textContent = it.ch;
    svg.appendChild(t);
    out.push(t.getComputedTextLength());
    svg.removeChild(t);
  }
  svg.remove();
  return out;
};
</script></body></html>
"""


def main():
    inp = Path(sys.argv[1])
    outp = Path(sys.argv[2])
    data = json.loads(inp.read_text(encoding="utf-8"))
    combos = data["combos"]
    chars = data["chars"]

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr); sys.exit(1)

    tmp_html = Path(__file__).parent / "_measure_chars.html"
    tmp_html.write_text(HTML, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 400})
        try:
            # 页面要动态 import esm.sh 上的 excalidraw 包（约数 MB）并下载内嵌字体，
            # 境外 CDN 偶发抽风会让这一句等到 120s 超时 → 重试即可，不必改代码。
            ready = False
            for attempt in range(1, 4):
                try:
                    page.goto(tmp_html.as_uri())
                    page.wait_for_function("window.__ready === true", timeout=120000)
                    ready = True
                    break
                except Exception as e:
                    print(f"[警告] 第 {attempt}/3 次加载超时：{type(e).__name__}: {e}",
                          file=sys.stderr)
                    page = browser.new_page(viewport={"width": 1200, "height": 400})
            if not ready:
                print("ERROR: 连续 3 次都没能加载 excalidraw 模块——"
                      "检查能否访问 https://esm.sh （代理/网络），再重跑本脚本。",
                      file=sys.stderr)
                sys.exit(1)

            err = page.evaluate("window.__err")
            if err:
                print(f"ERROR: excalidraw module failed: {err}", file=sys.stderr); sys.exit(1)

            fontByKey = page.evaluate("(c) => window.probe(c)", combos)
            print("[字体栈探测]")
            for k, v in fontByKey.items():
                print(f"   {k} -> {v}")
            print("[字体加载]", page.evaluate("() => window.fontCheck()"))

            metrics = {}
            for c in combos:
                key = f"{c['fs']}|{c['fam']}"
                items = [{"key": key, "fs": c["fs"], "ch": ch} for ch in chars]
                widths = page.evaluate("([it, fb]) => window.measure(it, fb)",
                                       [items, fontByKey])
                metrics[key] = {ch: round(w, 3) for ch, w in zip(chars, widths)}
                print(f"[OK] {key}: {len(chars)} 字符，最大宽度 {max(widths):.2f}px")
        finally:
            browser.close()
            if tmp_html.exists():
                tmp_html.unlink()

    outp.write_text(json.dumps(metrics, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] 字宽表已写入：{outp}")


if __name__ == "__main__":
    main()
