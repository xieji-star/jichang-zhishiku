---
name: 前端设计
description: 前端网页设计的一体化聚合入口。当用户需要设计、重设计、优化、打磨、审查前端界面——落地页、官网、Dashboard、产品 UI、组件、表单、设置页、App 外壳、banner、品牌视觉、幻灯片、设计系统——或需要设计规范、配色方案、字体配对、风格参考、UI/UX 指南、反 AI 味设计（anti-slop）、参考图生成、图片转代码、极简/野兽派/高端视觉风格，或提到 frontend-design、impeccable、ui-ux-pro-max、taste-skill、UI/UX 设计、网页设计、前端美化、界面优化、品牌设计等任何与前端视觉设计相关的需求——即使没有点名本 skill——都必须使用本 skill。本 skill 会根据任务场景自动路由到 4 大技能包（frontend-design 美学指导 / impeccable 设计工具箱 / ui-ux-pro-max 设计情报库 / Taste Skill 反 AI 味多 Agent 编排），组合出"先查什么规范、用什么方法、最后由谁实现"的完整方案并落地执行；大型任务叠加多 Agent 并行编排提升效率。
---

# 🎨 前端设计 — 四大技能包聚合编排入口

> 本 skill 是「前端网页设计」工作的统一入口：**先判断场景 → 查路由矩阵 → 读取对应技能包/子技能的 SKILL.md 按其指示执行**。需要大型/多阶段任务时，再叠加多 Agent 并行编排（Taste Skill 模式）大幅提升效率。

---

## 一、四大技能包一览

本 skill 聚合 4 个技能包（均位于 `前端设计/` 目录下），每个技能包解决一个侧面的问题：

| 技能包 | 定位 | 目录 | 一句话能力 |
|--------|------|------|-----------|
| **frontend-design** | 美学指导（"怎么设计才好看"） | `前端设计/frontend-design/` | 视觉方向、排版、反模板化决策 |
| **impeccable** | 设计工具箱（"动手改/审/打磨"） | `前端设计/impeccable/` | 20+ 命令：shape / critique / audit / polish / live 等 |
| **ui-ux-pro-max** | 设计情报库（"查规范/找灵感"） | `前端设计/ui-ux-pro-max/` | 84 风格、192 色板、74 字体配对、98 UX 指南、22 技术栈 |
| **Taste Skill** | 反 AI 味 + 多 Agent 编排（"完整流程"） | `前端设计/Taste Skill/` | 13 个子技能 + 多 Agent 并行协作 |

> 拿不准时：**要"从零做设计"** → frontend-design + ui-ux-pro-max；**要"改现有界面"** → impeccable；**要"完整项目流程/去 AI 味"** → Taste Skill；**要"查数据/规范"** → ui-ux-pro-max。

---

## 二、子技能全清单与路由矩阵（先看这里）

### 2.1 子技能速查表

**frontend-design（1 个）**

| 子技能 | 触发场景 |
|--------|---------|
| `frontend-design` | 新 UI 的视觉方向、美学指导、排版、反模板化 |

**impeccable（1 个）**

| 子技能 | 触发场景 |
|--------|---------|
| `impeccable` | 设计/重设计/审查/打磨/精简/强化/动效/配色 前端界面，20+ 命令（shape·audit·critique·polish·live·bolder·quieter·overdrive 等） |

**ui-ux-pro-max（7 个）**

| 子技能 | 触发场景 |
|--------|---------|
| `ui-ux-pro-max`（主库） | 查风格/色板/字体配对/UX 指南/图表/动效预设 等设计情报数据库 |
| `ui-styling` | 用 shadcn/ui + Tailwind 实现界面、组件、暗色模式、响应式布局 |
| `banner-design` | 社媒/广告/网站 hero 横幅、创意素材、印刷 banner |
| `design` | 品牌标识、logo 生成（55 风格）、企业视觉系统（CIP）、图标、社媒图 |
| `slides` | 战略型 HTML 演示文稿（Chart.js、文案公式） |
| `design-system` | 设计令牌（token）架构、组件规范、三层令牌 |
| `brand` | 品牌声音、视觉识别、消息框架、品牌一致性 |

**Taste Skill（13 个）**

| 子技能 | 触发场景 |
|--------|---------|
| `taste-skill`（v2） | 反 AI 味前端设计默认入口（读 brief → 推设计语言 → 三旋钮） |
| `taste-skill-v1` | 依赖 v1 精确行为时使用 |
| `gpt-tasteskill` | GPT/Codex 严格变体、更强的布局/动效方向 |
| `image-to-code-skill` | 图片 → 分析 → 代码落地流水线 |
| `redesign-skill` | 已有项目的审计 → 修复 → 重设计 |
| `soft-skill` | 高端/柔和/留白/高级感视觉 |
| `output-skill` | 模型输出半成品时，强制完整输出 |
| `minimalist-skill` | 极简编辑风（Notion/Linear 味） |
| `brutalist-skill` | 野兽派工业风、瑞士字体、强烈对比 |
| `stitch-skill` | Google Stitch 兼容规则 |
| `imagegen-frontend-web` | 网站参考图/comps 生成（配合 ChatGPT Images 等） |
| `imagegen-frontend-mobile` | 移动端屏幕/流程 mockup 生成 |
| `brandkit` | 品牌套件板：logo 方向、色板、字体、应用 |

### 2.2 路由矩阵（按用户场景选路）

| 用户场景 | 路由到 | 说明 |
|---------|--------|------|
| 从零设计新落地页/官网/Dashboard/产品 UI | **frontend-design** + **ui-ux-pro-max** | 先定美学方向，再查风格/色板/字体支撑决策 |
| 现有界面优化/审查/打磨/重塑 | **impeccable** | critique → audit → shape → polish 全流程 |
| 现有项目整体重设计 | **Taste Skill/redesign-skill**（或 impeccable） | 先审计 UI，再修布局/间距/层级 |
| 反 AI 味 / 通用高质量前端设计 | **Taste Skill/taste-skill** | 读 brief、推设计语言、调三旋钮 |
| 查设计规范/找灵感（风格/配色/字体/UX/图表） | **ui-ux-pro-max** 主库 | 本地数据库直接检索 |
| 用 shadcn/ui + Tailwind 实现界面 | **ui-ux-pro-max/ui-styling** | 组件级实现、暗色模式、主题 |
| 品牌视觉/logo/企业视觉系统 | **ui-ux-pro-max/brand** + **design** + **Taste Skill/brandkit** | 品牌声音 → 视觉识别 → 套件板 |
| 幻灯片/演示文稿 | **ui-ux-pro-max/slides** | HTML 演示 + Chart.js 图表 |
| 设计系统/令牌架构 | **ui-ux-pro-max/design-system** | 三层令牌、组件规范 |
| Banner / 社媒素材 / 广告图 | **ui-ux-pro-max/banner-design** | 多风格多平台 |
| 生成设计参考图（网站/移动端） | **Taste Skill/imagegen-frontend-web** / **imagegen-frontend-mobile** | 产出图片 → 交给编码 agent 实现 |
| 图片转代码 | **Taste Skill/image-to-code-skill** | 生成参考 → 分析 → 实现 |
| 特定风格（极简/野兽派/高端柔和） | **Taste Skill/minimalist-skill** / **brutalist-skill** / **soft-skill** | 视觉方向已定，直接套风格 |
| 模型输出半成品 | **Taste Skill/output-skill** | 强制完整输出、禁止占位符 |
| 大型完整项目（多阶段/多模块） | **Taste Skill 多 Agent 编排**（见第四节） | 并行派发子代理 |
| 需工程化实现/后端联动 | 转 **/代码设计** skill | 前端设计出方案，代码设计落地 |

---

## 三、执行流程（固定套路）

每次触发本 skill 按此执行：

1. **判断场景**：把用户需求归入上方路由矩阵的某一类（可多类组合）。
2. **读取目标技能包**：按矩阵路由，读取对应子技能的 SKILL.md（`前端设计/<技能包>/<子技能>/SKILL.md`），按其指示执行。**不要全文加载无关技能包**，节省上下文。
3. **组合编排**：多环节任务按"情报 → 方法 → 实现"串联——
   - 先查 `ui-ux-pro-max` 拿风格/色板/字体/UX 规范（数据支撑）；
   - 再用 `frontend-design` / `Taste Skill` 定美学与反 AI 味方向；
   - 用 `impeccable` 或 `Taste Skill` 子技能落地/重设计；
   - 最后如涉及代码实现，转 `/代码设计`。
4. **验证交付**：检查输出是否满足需求（响应式、可访问性、反 AI 味、无占位符）；若用 `impeccable` 的 `critique` 或 `audit` 自检一遍。

---

## 四、多 Agent 协作（大型任务专用）

当任务规模大（多页面、多风格探索、品牌 + 落地页 + 移动端全案）时，按 Taste Skill 的多 Agent 编排模式并行派发子代理，主上下文担任编排者：

1. **拆解任务**：按技能包/页面/风格拆成可并行子任务。
2. **并行派发**：同一轮用 Agent 工具派发多个子代理（general-purpose 即可），各自读对应子技能 SKILL.md 执行。
3. **典型分工**：
   - 情报代理 → 查 `ui-ux-pro-max` 数据库，输出风格/色板/字体方案；
   - 视觉代理 → 按 `frontend-design` / `taste-skill` 定美学方向；
   - 参考图代理 → 用 `imagegen-*` 生成 comps；
   - 实现代理 → 用 `ui-styling` / 转 `/代码设计` 落地代码；
   - 审查代理 → 用 `impeccable` 的 critique/audit 挑毛病、去 AI 味。
4. **两阶段审查**：每份产出先过"规格符合性"再过"质量/去 AI 味"，审查与产出分开，禁止自我批准。
5. **汇总收尾**：主上下文汇总裁决，输出最终方案/代码。

> 说明：Taste Skill 本身自带聚合 SKILL.md 与 13 子技能，多 Agent 编排细节可直接读 `前端设计/Taste Skill/SKILL.md` 第四节；本 skill 是其上层的更广入口，覆盖全部 4 个技能包。

---

## 五、注意事项

- **按需读取**：只读路由到的子技能 SKILL.md，不要全文加载整个技能包。
- **尊重子技能自洽**：每个子技能都有独立规则（如 `taste-skill` 的硬性 em-dash 禁令、`output-skill` 的完整输出要求），调用前先读其 SKILL.md，不凭记忆操作。
- **图片生成技能只出图**：`imagegen-*`、`brandkit` 仅产出参考图，不产出代码；配 ChatGPT Images / Codex 图像模式使用，然后把图交给编码 agent 实现。
- **外部依赖**：`taste-skill` 等依赖 GSAP/GreenSock 与框架无关的设计规则，不影响 React/Vue/Svelte；实现时如遇工程问题转 `/代码设计`。
- **与 /代码设计 的关系**：本 skill 负责"视觉设计"这一层；涉及架构、多文件实现、TDD、代码审查的工程环节，路由到 `/代码设计`（superpowers + oh-my-claudecode 双引擎）。
