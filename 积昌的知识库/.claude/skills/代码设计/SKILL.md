---
name: 代码设计
description: 代码设计/开发工作流的一体化编排入口。当用户需要设计、规划、开发、重构、调试、审查、验证代码，或提到 superpowers、oh-my-claudecode、OMC、多 Agent 协作、Team 流水线、子代理编排、代码架构、技术方案、代码评审、写代码、开发功能等任何代码相关工作——即使没有点名本 skill——都必须使用本 skill。本 skill 会根据任务类型同时调动 superpowers（软件开发方法论 + 技能库）与 oh-my-claudecode（19 个专业 Agent 的多 Agent 编排）两大引擎，组合出"谁来做 + 怎么做"的完整方案并落地执行。
---

# 🧩 代码设计 — 双引擎多 Agent 编排

> 本 skill 是「代码设计」工作的统一入口：**superpowers 决定"怎么做"，oh-my-claudecode 决定"谁来做"**。两者按任务类型组合，先规划后动手，用多 Agent 并行与两阶段审查保证质量。无论任务大小，先跑一遍下面的"任务拆解"，再决定引擎组合。

---

## 一、两大引擎（按需读取对应文件，不要全文加载）

本 skill 自带两个完整项目（均位于本 skill 目录下，相对路径从 `代码设计/` 解析）：

### 引擎 A：superpowers —— 方法论层（"怎么做"）

- 位置：`superpowers/`（obra/superpowers 完整克隆）
- 作用：一套完整的软件开发方法论 + 可组合技能库，规范"澄清需求 → 写计划 → TDD → 审查 → 收尾"的流程。
- 技能清单（用时按名读取 `superpowers/skills/<技能名>/SKILL.md`）：

| 技能 | 用途 |
|------|------|
| `brainstorming` | 苏格拉底式需求澄清与设计收敛（写代码前先激活） |
| `writing-plans` | 把设计拆成 2–5 分钟可执行的小任务，每任务含文件路径/完整代码/验证步骤 |
| `executing-plans` | 按计划批量执行，带人工检查点 |
| `subagent-driven-development` | 每个任务派发独立子代理，两阶段审查（先规格符合性，再代码质量） |
| `dispatching-parallel-agents` | 并发派发多个子代理处理独立子任务 |
| `test-driven-development` | RED-GREEN-REFACTOR 循环：先写失败测试，再写最小实现，再重构 |
| `systematic-debugging` | 四阶段根因排查（不靠猜） |
| `verification-before-completion` | 声称完成前先验证"真的修好了" |
| `requesting-code-review` | 请求审查前自检清单，按严重度报告问题 |
| `receiving-code-review` | 正确回应审查意见 |
| `using-git-worktrees` | 用 git worktree 开隔离开发分支 |
| `finishing-a-development-branch` | 任务完成后验证测试、决定 merge/PR/保留/丢弃 |
| `writing-skills` / `using-superpowers` | 元技能：写新技能 / 入门 |

- 哲学：**TDD 优先、系统化优于猜测、简化优先、证据优于声明**。

### 引擎 B：oh-my-claudecode —— 编排层（"谁来做"）

- 位置：`oh-my-claudecode/`（yeachan-heo/oh-my-claudecode 完整克隆）
- 作用：19 个专业 Agent + 多种编排模式，把任务分派给最合适的 Agent 并串成流水线。
- **Agent 目录**：`oh-my-claudecode/agents/<名字>.md`（每个 Agent 一份完整提示词，派发子代理时按名读取作为基底）。

| Agent | 模型档位 | 擅长 |
|-------|:---:|------|
| `explore` | haiku | 快速探索代码库/定位 |
| `analyst` | opus | 数据分析、研究、洞察 |
| `architect` | opus | 系统/架构设计 |
| `planner` | opus | 制定实施计划 |
| `debugger` | sonnet | 定位与修复缺陷 |
| `executor` | sonnet | 落地实现代码（复杂用 opus） |
| `verifier` | sonnet | 验证结果是否达标 |
| `tracer` | sonnet | 证据驱动追踪执行 |
| `security-reviewer` | sonnet | 安全审查 |
| `code-reviewer` | opus | 代码质量审查 |
| `test-engineer` | sonnet | 测试设计/编写 |
| `designer` | sonnet | UI/UX 设计 |
| `writer` | haiku | 文档/文案写作 |
| `qa-tester` | sonnet | QA 回归验证 |
| `scientist` | sonnet | 数据科学/实验 |
| `document-specialist` | sonnet | 查官方文档/SDK 用法 |
| `git-master` | sonnet | Git 操作/分支管理 |
| `code-simplifier` | opus | 精简/去冗余 |
| `critic` | opus | 批判性评审、挑毛病 |

- 编排模式：`team`（团队流水线）、`autopilot`（全自主单 lead）、`ultrawork`（最大并行）、`ralph`（持久验证/修复循环）、`ultraqa`（质量门禁循环）、`deep-interview`（需求深访）。更多技能见 `oh-my-claudecode/skills/`。
- Team 流水线：`team-plan → team-prd → team-exec → team-verify → team-fix`（fix 循环有最大次数上限）。
- 模型路由原则：`haiku` 快查、`sonnet` 标准、`opus` 架构/深度分析。

---

## 二、任务拆解与引擎路由矩阵

**第一步永远是：判断任务类型 → 查下表 → 决定引擎组合**。多数中等以上任务需要**同时**用两大引擎（superpowers 提供流程纪律，OMC 提供 Agent 分派）。

| 任务类型 | 引擎组合 | 要加载的技能 / Agent |
|---------|---------|---------------------|
| 需求模糊 / 新功能前期 | B 为主 + A 辅助 | `oh-my-claudecode/skills/deep-interview` + `superpowers/skills/brainstorming` |
| 架构 / 技术方案设计 | A+B 并用 | `oh-my-claudecode/agents/architect` + `planner` + `superpowers/skills/writing-plans` |
| 多文件功能实现 | A+B 并用 | `superpowers/skills/test-driven-development` + `oh-my-claudecode/agents/executor` + `test-engineer` |
| 大规模自主执行 | B 为主 + A 辅助 | `oh-my-claudecode/skills/autopilot` 或 `ralph` + `superpowers/skills/executing-plans` |
| 并行修复 / 重构 | A+B 并用 | `superpowers/skills/dispatching-parallel-agents` + `oh-my-claudecode/skills/ultrawork` 或 `team` |
| 调试 Bug | A 为主 + B 辅助 | `superpowers/skills/systematic-debugging` + `oh-my-claudecode/agents/debugger` + `tracer` |
| 代码审查 | A+B 并用 | `superpowers/skills/requesting-code-review` + `oh-my-claudecode/agents/code-reviewer` + `critic` |
| 测试 / 质量门禁 | A+B 并用 | `superpowers/skills/test-driven-development` + `oh-my-claudecode/agents/test-engineer` + `qa-tester` 或 `skills/ultraqa` |
| 安全审查 | B 为主 + A 辅助 | `oh-my-claudecode/agents/security-reviewer` + `superpowers/skills/verification-before-completion` |
| 文档 / 说明撰写 | B 为主 | `oh-my-claudecode/agents/writer` + `document-specialist` |
| Git 收尾 / 分支合并 | A 为主 + B 辅助 | `superpowers/skills/finishing-a-development-branch` + `oh-my-claudecode/agents/git-master` |
| 简单单文件改动 | 直接做 | 不必派子代理；如涉及测试再加载 `test-driven-development` |

> 简单任务（单命令、小澄清、单文件小改动）直接在主上下文完成；多文件、重构、调试、审查、规划、研究、验证类任务一律派发子代理。

---

## 三、多 Agent 协作工作流

派发子代理的固定套路（每次按此执行）：

1. **拆解任务**：把用户目标拆成可并行的独立子任务。能并行的就并行（同一轮派发多个 Agent，不要串行等待）。
2. **读取 Agent 定义**：按路由矩阵，从 `oh-my-claudecode/agents/<名字>.md` 读取对应 Agent 的完整提示词，作为派发子代理的基底；同时按需读取 `superpowers/skills/<技能>/SKILL.md` 的方法论。
3. **派发子代理**：用 Agent 工具派发（general-purpose 类型即可，提示词=Agent 定义基底 + 具体任务 + 输入文件 + 期望输出）。**并行子任务务必在同一轮消息里同时派发**。
4. **两阶段审查**（superpowers 的 subagent-driven-development 核心）：每个子代理的产出经过两道关——① **规格符合性**（是否满足计划/需求）→ ② **代码质量**（可读性/测试/是否过度设计）。两个阶段由不同 Agent（或主上下文）执行，禁止"自己写自己审"。
5. **验证收尾**：用 `verifier`/`qa-tester` 验证产出真实达标（有证据，不只是"我认为"），再由 `git-master` 处理分支、按 `finishing-a-development-branch` 决定合并/PR/丢弃。

**角色分工铁律**：
- 作者与评审分离：writer/executor 负责产出，code-reviewer/critic/verifier 另开一条线审查。同一上下文不得自我批准。
- 主上下文担任"编排者"（dispatcher/lead），不亲自陷进每个实现细节，而是派发、检查、汇总裁决。

---

## 四、统一工作流（双引擎合并五阶段）

把两大引擎串成一条完整流水线。**凡是多文件/中大型任务，都按这五阶段走**：

```
阶段 1 理解   → 阶段 2 计划   → 阶段 3 执行   → 阶段 4 验证与审查   → 阶段 5 收尾
```

### 阶段 1：理解（澄清需求，不急着写码）
- 需求模糊 → 加载 `oh-my-claudecode/skills/deep-interview` 做苏格拉底式深访；或 `superpowers/skills/brainstorming` 收敛设计。
- 产出：一份用户确认过的需求/设计说明。

### 阶段 2：计划（把设计变成可执行计划）
- 加载 `oh-my-claudecode/agents/architect`（架构）→ `planner`（拆任务）→ 参考 `superpowers/skills/writing-plans` 的粒度（每任务 2–5 分钟，含文件路径、完整代码、验证步骤）。
- 产出：实施计划（任务清单，含验收标准）。

### 阶段 3：执行（按计划派发实现）
- 加载 `superpowers/skills/test-driven-development`（先写测试）→ `oh-my-claudecode/agents/executor` 落地。
- 并行任务用 `dispatching-parallel-agents` / `ultrawork`；需要全自主用 `autopilot`/`ralph`。
- 产出：实现代码 + 通过测试。

### 阶段 4：验证与审查（证据过关才叫完成）
- 加载 `oh-my-claudecode/agents/code-reviewer` + `critic` 审查 → `verifier` 验证 → `qa-tester` 回归；参考 `superpowers/skills/requesting-code-review`。
- 关键问题阻塞进度，修复后回到阶段 3/4 循环（参考 `ultraqa` 的质量门禁）。
- 产出：审查通过、有验证证据的结果。

### 阶段 5：收尾（合并 / PR / 清理）
- 加载 `oh-my-claudecode/agents/git-master` + `superpowers/skills/finishing-a-development-branch`：验证测试 → 决定 merge/PR/保留/丢弃 → 清理 worktree。

---

## 五、质量守则（贯穿始终）

1. **先写测试再写实现**（TDD）：有测试保护的改动才算完成；禁止"先写一堆代码再补测试"。
2. **证据优于声明**：任何"完成/修好/达标"的结论都要有验证证据（测试输出、运行结果、审查意见）。
3. **系统化优于猜测**：调试走 `systematic-debugging` 四阶段，禁止瞎试。
4. **作者与评审分离**：禁止同一上下文自我批准；审查交给独立 Agent/审查通道。
5. **简化优先（YAGNI/DRY）**：只做需要的功能，不写用不上的抽象；重复代码要抽取。
6. **每个任务有验收标准**：派发子代理前明确"什么算做完"，完成后逐项核对。

---

## 六、执行提示

- **不要全文加载两大项目**：只按路由矩阵按需读取 `superpowers/skills/<技能>/SKILL.md` 与 `oh-my-claudecode/agents/<名字>.md`，节省上下文。
- **两个项目是本地克隆**：需要最新版可 `git -C <子项目> pull`，但禁止修改这两个项目的源码/技能内容（它们是上游仓库，改动会导致下次 pull 冲突）。
- **目标代码目录**：用户的任务目标是哪个项目目录，就以哪个为工作目录；本 skill 只提供方法与编排，不限定目标路径。
- **若环境没有 omc CLI / tmux**：`omc team`、`autopilot` 等需要 CLI/插件运行时；退化为用 Agent 工具派发子代理完成同等编排（在结果中说明采用了降级路径）。
