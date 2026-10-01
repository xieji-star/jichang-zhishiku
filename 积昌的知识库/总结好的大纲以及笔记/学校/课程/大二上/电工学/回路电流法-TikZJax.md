# 回路电流法 · 电路图（TikZJax 版）

> 由 **TikZJax**（`obsidian-tikzjax`）渲染：下方 `tikz` 代码块会被 Obsidian **自动渲染成矢量图**，改代码即改图，可由 AI 直接生成与修改。
> 代码块标识：` ```tikz `　·　原版必须写 `\begin{document}` / `\end{document}`

---

```tikz
\usepackage{circuitikz}
\begin{document}
\begin{circuitikz}[scale=1.1]
  % 上支路：R1、R2
  \draw (0,3) to[R, l=$R_1$, i=$I_1$] (3,3)
              to[R, l=$R_2$, i=$I_2$] (6,3);
  % 左支路：E1
  \draw (0,0) to[battery1, l=$E_1$, invert] (0,3);
  % 右支路：E2
  \draw (6,3) to[battery1, l=$E_2$] (6,0);
  % 中支路：R3
  \draw (3,3) to[R, l=$R_3$, i=$I_3$] (3,0);
  % 下支路
  \draw (0,0) to[short] (3,0) to[short] (6,0);
  % 回路电流 I_Ⅰ / I_Ⅱ（红色弯箭头）
  \draw[->, red, thick] (1.0,1.1) to[bend left=50] (2.1,1.1);
  \node[red] at (1.55,1.65) {$I_{\mathrm{I}}$};
  \draw[->, red, thick] (4.0,1.1) to[bend left=50] (5.1,1.1);
  \node[red] at (4.55,1.65) {$I_{\mathrm{II}}$};
\end{circuitikz}
\end{document}
```

---

**对应方程**（黑板原式）：

- KVL：$(R_1+R_3)I_{\mathrm{I}} - R_3 I_{\mathrm{II}} = E_1$　；　$-R_3 I_{\mathrm{I}} + (R_2+R_3)I_{\mathrm{II}} = -E_2$
- KCL：$I_1 = I_{\mathrm{I}}$　；　$I_2 = -I_{\mathrm{II}}$　；　$I_3 = I_{\mathrm{I}} - I_{\mathrm{II}}$
