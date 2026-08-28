---
name: elegant-reports
description: 生成北欧/斯堪的纳维亚美学的精美 PDF 报告（净化版，纯本地渲染）。适用于将 Markdown 内容排版美化为专业 PDF——执行摘要、分析报告、演示型简报、董事会级汇报等。基于 elegant-reports 北欧设计语言重写，已删除全部云端外发与第三方依赖，改用系统自带 Edge/Chrome 无头模式本地渲染，零网络外发、零外部依赖。
permissions:
  - exec: "运行本地 Node 生成器（列出模板、渲染预览 HTML、生成 PDF 输出）。"
  - file_read: "读取 skill 目录内置的模板、主题、示例与设计参考，以及用户批准的输入 Markdown 文件。"
  - file_write: "在用户批准的工作目录内写入生成的 HTML/PDF 输出与用户要求的模板/主题文件。"
  - env: "仅读取 EDGE_PATH / CHROME_PATH 环境变量，用于定位本地浏览器路径（只读，不写入）。"
  - shell: "通过 Node 的 execFileSync 直接调用本地 Edge/Chrome 无头模式渲染 PDF；不经过 shell 解释器、不访问网络、不执行任意命令。"
---

# elegant-reports（净化版）

将 Markdown 排版美化为北欧/斯堪的纳维亚风格的极简 PDF 报告。

> ⚠️ **安全净化说明**：本版本已从原版 `jdrhyne/agent-skills@elegant-reports` 净化重写——
> - ✅ **删除**：Nutrient DWS 云端渲染（原版会把文档内容上传至 `api.nutrient.io`）、`NUTRIENT_DWS_API_KEY`、`axios`/`form-data`（含已知 CVE 的未固定依赖）、`curl` 外发、shell 命令注入风险
> - ✅ **改为**：系统自带 **Edge/Chrome 无头模式**在本地渲染 HTML→PDF（`--print-to-pdf`），文档内容全程留在本机
> - ✅ **权限**：仅 `exec`/`file_read`/`file_write`，**无 `network` 权限**
> - ✅ **依赖**：仅需 Node.js 18+ 与系统自带的 Edge/Chrome，无 npm 依赖

## 何时使用

当用户需要：
- 精美的执行摘要、董事会级/报告级 PDF
- 从 Markdown 生成演示风格的 PDF
- 北欧极简视觉语言（而非默认的开发风格）
- 可复用的报告模板体系

## 快速开始

无需安装任何 npm 依赖。直接运行：

```bash
cd .claude/skills/elegant-reports
node ./generate.js --list
node ./generate.js examples/sample-executive.md output.pdf --template report --theme light
```

> 本地渲染依赖系统自带 **Microsoft Edge** 或 **Google Chrome**（无头模式）。
> 若浏览器不在默认路径，可通过环境变量指定：`EDGE_PATH` 或 `CHROME_PATH`。

调试时加 `--output-html`，生成器会额外保存渲染后的 HTML 便于检查版面。

## 可用模板

| 模板 | 用途 |
|------|------|
| `report` | 信息密集的多栏分析报告（默认） |
| `presentation` | 一页一观点的大字演示简报 |
| `executive` | 原始执行摘要模板（遗留） |
| `report-demo` | 遗留 report 变体，用于对比/测试 |
| `presentation-demo` | 遗留 presentation 变体，用于对比/测试 |

每个模板支持 `light` / `dark` 主题（可用处）。

## Frontmatter

在 Markdown 顶部添加 YAML frontmatter 控制输出：

```markdown
---
title: Q4 竞品分析
subtitle: 市场情报报告
author: 报告作者
template: report
theme: dark
---

正文内容……
```

## 工作流

1. 从现有模板中选择最接近的，而非从零开始。
2. 编写或润色源 Markdown。
3. 生成 PDF。
4. 如需调整版面，用 `--output-html` 查看生成的 HTML，调整对应模板/主题。
5. 重新生成直到版面干净、PDF 稳定。
6. **页眉页脚规则（硬性）**：每一页的页眉区与页脚区都不得出现正文内容。占满整页的容器（`.page` / `.title-slide`）高度必须用 `calc(100vh − 页边距)` 计算，与 `@page` 边距严格匹配（A4+8mm → `calc(100vh − 16mm)`；Letter+0.5in → `calc(100vh − 1in)`），防止正文溢出到页边距留白区。调整模板/主题时不得破坏该约束。

## 扩展 Skill

创作新的视觉变体时：
- 从最近的内置模板与主题出发
- 保持 token 命名与间距尺度和现有体系一致
- 每次只做一个视觉改动，改完重新生成
- 优先做增量变体，而非重写整个设计语言
- 在替换方案验证通过前，保留遗留/demo 模板

内置的北欧设计研究笔记（`NORDIC_DESIGN_RESEARCH.md`）是该视觉体系的规范参考，需要更深的设计依据时再阅读。

## 安全边界

- **绝不访问网络**：所有渲染均在本地完成，不发送任何文档内容到第三方服务。
- 不浏览任意本地文件，读取范围限于 skill 包与用户批准的输出路径。
- 不覆盖或删除用户工作目录之外的文件。
- 不安装额外软件包、不改动依赖版本、不引入新的外部服务。
- 只有在输出产物确实存在且生成器无错误完成时，才报告生成成功。

## 依赖

- Node.js 18+
- 系统自带的 Microsoft Edge 或 Google Chrome（无头模式）
- 无任何 npm 第三方依赖

## 文件清单

- `generate.js` — 生成器 CLI 与模块入口（净化版）
- `templates/` — 内置 HTML 模板
- `themes/` — 内置视觉主题
- `examples/` — 示例 Markdown 输入
- `references/` — 可选的北欧设计研究文档

## 验证

完成前：
- 运行 `node ./generate.js --list`
- 运行 `npm test`
- 确认 PDF/HTML 产物存在于目标输出路径
