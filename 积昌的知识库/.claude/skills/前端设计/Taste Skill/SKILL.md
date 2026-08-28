---
name: Taste Skill
description: 前端设计品味（anti-slop，反 AI 味）技能包的聚合编排入口。当用户需要高质量前端设计、落地页、作品集、网站/App 重设计、品牌视觉套件、设计参考图生成、图片转代码、极简/野兽派/高端视觉风格，或提到 taste-skill、品牌套件、反模板化、去 AI 味设计等时触发。本 skill 会把任务拆解，通过多 Agent 并行编排（需求方向分析 / 参考图生成 / 品牌视觉 / 代码实现 / 审计去 AI 味 / 输出保障）大幅提升效率。
---

# 🎨 Taste Skill — 反 AI 味前端设计 · 多 Agent 协作编排入口

聚合编排 13 个 Taste 系列子技能：**一次触发、自动拆解、多 Agent 并行、串行整合**。

> [!important] 触发后第一步
> **判断任务类型 → 查「第四节 路由矩阵」→ 决定派哪些 Agent 并行**。多数中等以上任务需要多 Agent 并行；小任务可省去多 Agent，直接读 `taste-skill` 主技能完成。

---

## 一、子技能速查（13 个）

目录前缀统一为 `.claude/skills/Taste Skill/skills/`。

| 子技能 | 技能名 | 定位 | 目录 |
|--------|--------|------|------|
| `taste-skill` | design-taste-frontend | **主技能（v2 实验版）**：需求解读 + 设计方向 + 实现规范总纲，一切任务的第一基线 | `skills/taste-skill/` |
| `taste-skill-v1` | design-taste-frontend-v1 | 主技能 v1 旧版（兼容依赖旧行为的项目） | `skills/taste-skill-v1/` |
| `gpt-tasteskill` | gpt-taste | 更严格版：真随机布局、AIDA 结构、强 GSAP 动效（GPT/Codex 场景） | `skills/gpt-tasteskill/` |
| `image-to-code-skill` | image-to-code | 图片→代码流水线：先生成参考图，再按图实现网站 | `skills/image-to-code-skill/` |
| `imagegen-frontend-web` | imagegen-frontend-web | 网页设计参考图生成（每个版块一张横图） | `skills/imagegen-frontend-web/` |
| `imagegen-frontend-mobile` | imagegen-frontend-mobile | 移动端 App 界面概念图生成 | `skills/imagegen-frontend-mobile/` |
| `redesign-skill` | redesign-existing-projects | 现有网站/App 审计升级、去 AI 味 | `skills/redesign-skill/` |
| `output-skill` | full-output-enforcement | 防截断输出，强制完整代码生成 | `skills/output-skill/` |
| `soft-skill` | high-end-visual-design | 高端视觉设计教学（字体/间距/阴影/卡片/动画） | `skills/soft-skill/` |
| `minimalist-skill` | minimalist-ui | 极简编辑风 UI（暖单色、扁平 bento 网格） | `skills/minimalist-skill/` |
| `brutalist-skill` | industrial-brutalist-ui | 工业野兽派 UI（瑞士印刷 + 军事终端风） | `skills/brutalist-skill/` |
| `stitch-skill` | stitch-design-taste | Google Stitch 语义设计系统（生成 DESIGN.md） | `skills/stitch-skill/` |
| `brandkit` | brandkit | 高端品牌套件图片生成（品牌规范板、logo 系统） | `skills/brandkit/` |

---

## 二、多 Agent 协作：为什么快

主 Claude 只做「拆解 + 调度 + 整合」，把可并行环节交给多个子代理**同时**干活：

- **可并行**：需求方向分析、参考图生成、品牌视觉 —— 互不依赖，一次性派发
- **必须串行**：代码实现依赖「方向规格 + 参考图」，接在并行阶段之后
- **可并行把关**：审计去 AI 味、输出完整性保障 —— 在实现完成后并行执行

> 本质：用「多子代理并行」把串行时间压成「最长链路」，而非把所有环节排成一串。

---

## 三、子代理派发规范

每个子代理 = 一次 Agent/Task 调用，必须遵循：

1. **派发指令要自包含**：明确告诉子代理——
   - 读取哪个子技能 SKILL.md（用完整相对路径，如 `.claude/skills/Taste Skill/skills/taste-skill/SKILL.md`）
   - 任务输入（用户需求 + 上游产出物）
   - 期望输出格式（结构化：设计规格 / 参考图清单 / 代码 / 审计报告）
2. **模型档位**：
   - 方向分析 / 架构 / 审计 → `opus`（`taste-skill`、`redesign-skill`）
   - 代码实现 / 常规执行 → `sonnet`（`image-to-code-skill`）
   - 参考图生成 / 快速探查 → `haiku` 或 `sonnet`（`imagegen-*`）
3. **有依赖的任务禁止并行**：实现 Agent 必须等方向/参考图 Agent 完成后才派发。
4. 子代理输出交给主 Claude **统一整合**，最终交付含文件路径与关键说明的完整结果。

---

## 四、路由矩阵（核心）

| 任务类型 | 阶段1 · 并行 | 阶段2 · 串行 | 阶段3 · 并行把关 |
|---------|------------|------------|----------------|
| **从零做落地页 / 作品集 / 新页面** | A 方向(`taste-skill`) ‖ B 参考图(`imagegen-frontend-web`) ‖ C 品牌(`brandkit`, 如需) | D 实现(`image-to-code-skill`) | E 审计(`redesign-skill`) ‖ F 完整输出(`output-skill`) |
| **现有网站 / App 重设计** | A 审计现状(`redesign-skill`) ‖ B 参考图(`imagegen-frontend-web` 新方案) | D 实现(`image-to-code-skill`) | E 复审(`redesign-skill`) ‖ F 完整输出(`output-skill`) |
| **移动端 App 概念图** | A 方向(`taste-skill`) ‖ B 概念图(`imagegen-frontend-mobile`) | — | 整合输出 |
| **特定风格页面**（极简 / 野兽派 / 高端） | A 风格(`minimalist-skill` / `brutalist-skill` / `soft-skill`) ‖ B 方向(`taste-skill`) | D 实现(`image-to-code-skill`) | E 审计(`redesign-skill`) |
| **品牌视觉套件** | A 品牌(`brandkit`) ‖ B 方向(`taste-skill`) | — | 整合输出 |
| **给 GPT / Codex 用的严格版** | A 严格版(`gpt-tasteskill`) | — | 整合输出 |

> 拿不准时：**第一优先读 `taste-skill/SKILL.md` 作为基线**；有图片生成需求 → 加 `imagegen-*`；有现有代码/网站要改 → 加 `redesign-skill`；要保证不截断 → 加 `output-skill`。

---

## 五、执行流程

1. **拆解**：根据用户需求判断任务类型（查第四节路由矩阵），写出阶段1的并行 Agent 清单
2. **阶段1 · 并行派发**：一次调用多个 Agent/Task，每个子代理读取对应子技能 SKILL.md 并产出结构化结果
3. **阶段2 · 串行**：阶段1全部完成后，派发实现 Agent（读 `image-to-code-skill`），按「设计规格 + 参考图」产出完整代码
4. **阶段3 · 并行把关**：并行派发审计 Agent（`redesign-skill`）+ 输出保障 Agent（`output-skill`）
5. **整合交付**：主 Claude 汇总各子代理产出，向用户交付完整结果（文件路径、设计说明、关键决策）

---

## 六、注意事项

- 按需读取子技能 SKILL.md，**不要全文加载**所有 13 个子技能（节省 token）
- 子技能 SKILL.md 是**方法论指令**：每个子代理先读自己负责的 SKILL.md，再执行
- 尊重子技能内部规则：`taste-skill` 的 pre-flight 检查、`redesign-skill` 的 audit-first 等
- 任务规模很小时（如单页改色、小修），省去多 Agent，直接读 `taste-skill` 主技能完成即可
- 本文件夹含 `.git`（上游 `Leonxlnx/taste-skill` 克隆），对子技能的改动可用 git 追踪
