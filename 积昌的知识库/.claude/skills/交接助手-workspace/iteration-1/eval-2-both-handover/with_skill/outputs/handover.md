---
项目名：积昌的知识库（LLM Wiki 个人知识库项目）
交接对象：两者（先给人，后给 AI）
交接日期：2026-08-17
---

# 积昌的知识库 交接文档（给人版）

> 一句话定位：一套跑在 Obsidian 上、由 Claude 作为"有纪律的 wiki 维护者"持续管理的个人知识库——既收录从大学到实习期间的所有学习/求职/工作资料，又挂着两个自动化消息助手（飞书、企业微信），让 AI 能真正"接手日常"。

## 1. 项目总览

- **项目名称**：积昌的知识库（简称"知识库"）
- **物理位置**：`F:\积昌的知识库 - 副本`（注意：vault 内的规则文件写的是 `E:\积昌的知识库 - 副本`，但当前机器上实际目录在 `F:\`，详见"风险与待确认项"）
- **定位**：个人第二大脑 / 求职学习作战库 / 自动化消息助手控制中心
- **最终目标**：让 Claude 成为一个**有纪律的 wiki 维护者**（Karpathy《LLM Wiki》方法论落地），输入新资料→自动整理成结构化的 wiki 页面→随时能被检索问答；同时通过飞书/企业微信两个助手，让 Claude 在"被动的等待指令"之外，还能主动接收消息、处理文件、回复结果。
- **整体完成度估算**：约 **85%**。wiki 三层架构已稳定运行（61 个页面、10 大类，最近一次 2026-08-17 全库迭代无孤儿页、无遗漏页）；两个消息助手已能收发消息、处理 PDF、落盘整理；剩余主要是「待办流程的稳定化、规则文档与实际目录不一致的清理、以及日常持续 ingest 新资料」。

## 2. 背景与来去龙脉

- **为什么做**：项目主人是一位在校生→实习中的同学，资料散落在飞书、微信、直播课、PDF 里，靠"存进文件夹"永远找不到。2026-07-11 依据 Karpathy《LLM Wiki》方法论（`自动维护知识库/LLM Wiki.md`）正式初始化，把"散落资料"升级成"可被 AI 维护和检索的 wiki"。
- **要解决的问题**：① 资料进来后自动归类、去重、沉淀；② 想用的时候能"先读索引→定位→深读"，不浪费 token 全库扫；③ 实习/求职/脚本创作等场景需要 AI 深度参与，需要一个持续在线的入口（消息助手）。
- **怎么来的**：7 月 11 日初始化 wiki（20 页）→ 7 月中旬持续 ingest（实习训练营、面试课、学术裁缝、智灌云联项目）→ 7 月中下旬搭建飞书智能助手与企业微信智能助手 → 8 月全库 lint 迭代（8-13 补录孤儿页、8-17 短视频采集系统大版本更新）→ 持续接入技能（当前 27 个 skill）。
- **关键用户偏好 / 前置信息**：
  - 全局**已开放全部权限**，等价于 `claude --dangerously-skip-permissions` 启动，任何操作不需要再要授权；
  - 输出语言优先简体中文；文档创建/编辑一律走「/文档转换+排版」skill；
  - `已整理好的文件/` 视为**只读归档区**，未获明确指令不得改动；`自动维护知识库/` 与 `收件箱/` 可自由维护；
  - 飞书文档增删改查用个人账号"落日"（`--as user`），文档总结/读书笔记用 bot"谢积昌的飞书CLI"（`--as bot`）。

## 3. 当前进度

- wiki 层：**61 个页面、10 大类**，最近一次全库迭代（2026-08-17）确认 index.md 与磁盘文件完全一致、无孤儿页、收件箱为空。
- 技能层：`.claude/skills/` 下**27 个 skill**，覆盖飞书全家桶、企业微信、文档转换+排版、华哥脚本撰写、模拟面试、JD深度剖析、交接助手等。
- 消息助手层：
  - 飞书智能助手（`飞书智能助手/server.py`）：已能收消息、收文件、按 CLAUDE.md 规则落盘与回复；restart.bat 提供一键重启。
  - 企业微信/微信智能助手（`微信智能助手/server.py`）：FastAPI + 内网穿透隧道，回调 `/wecom/callback`，`current-tunnel-url.txt` 记录当前隧道地址。
- 自动化维护：hook（`.claude/hooks/kb-maintenance-check.sh`）每天检查两个周期任务——**GitHub 每周备份**（标记 `.last-github-backup`，当前=2026-08-17 已备份）与**LLM Wiki 每 3 天迭代**（标记 `.last-wiki-maintain`，当前=2026-08-17 已完成）。

## 4. 已完成工作（全量逐条）

按时间/模块分组：

- **Wiki 初始化（07-11）**：按 LLM Wiki 方法论创建 `自动维护知识库/` 三层架构（CLAUDE.md、index.md、log.md + 20 页初始 wiki）。
- **核心知识域录入（07-11~07-14）**：
  - 实习求职：简历制作、投递策略、面试技巧、JD拆解方法论、校园大使、招聘平台分析；
  - 实习训练营：总览、岗位叫法大全、行业与公司调研、高价值实习岗位、向上管理与汇报、求职实战问答；
  - 智灌云联项目：项目总览、LSTM预测模型、智能Agent决策、硬件架构、数据与算法、概念解析×10、技术问答×3、论文笔记（水肥一体机文献综述）；
  - 学术裁缝（选导师/选方向/读书目的）、销售方法论、自媒体运营总览与内容创作方法论。
- **Wiki 结构重组（07-11）**：按"实体页/概念页/对比页/问答页/论文笔记"多维分类重构目录，竞品对比独立为对比分析模块。
- **飞书智能助手（07-14~至今）**：搭建 `飞书智能助手/server.py` 双模式接管系统（个人账号/管理员远程控制）、claude-settings.json、restart.bat、admin.py 管理界面。
- **企业微信智能助手（07-14~至今）**：FastAPI 架构 + 内网穿透（`start-with-tunnel.bat`）、回调处理、`wecom-resources/` 落盘。
- **自动化 hook（持续）**：`kb-maintenance-check.sh` 实现 GitHub 每周备份 + LLM Wiki 每 3 天迭代的到期提示。
- **全库 lint/ingest 迭代（08-13、08-17）**：补录 7 个孤儿页、修正统计（50→61 页，主题文件夹 9→6）、清理 4 个空目录；08-17 短视频爆款采集系统大版本更新（多账号并发池、Edge 一次登录、风控对抗组件、速度优化、GPU ASR 字幕直取等，来源 3→7）。
- **技能库搭建**：当前 27 个 skill，含交接助手、文档转换+排版、华哥脚本撰写、模拟面试、知识库报错修复等，均有独立 SKILL.md。

## 5. 未完成事项（全量逐条）

| # | 事项 | 为什么没完成 | 前置条件 | 优先级 |
|---|------|------------|---------|--------|
| 1 | **规则路径与物理路径不一致**（规则写 `E:\`，实际在 `F:\`） | 可能做过盘符变更/迁移，规则未同步 | 人工确认实际盘符 | 🔴 紧急 |
| 2 | `收件箱/`、`已整理好的文件/` 目录在根目录**不存在**，但 CLAUDE.md 反复引用 | 实际实现里原始来源放在 `总结好的大纲以及笔记/`，"收件箱/已整理"可能是设计态而非落地态 | 确认是否需要补齐目录或在规则中修正 | 🟠 重要 |
| 3 | 企业微信隧道 URL 每次重启会变，需手动回填到企业微信后台 API 接收地址 | 内网穿透方案未固定公网域名 | 如需长期稳定，考虑固定域名/云服务器 | 🟠 重要 |
| 4 | 两个助手服务**不在开机自启**中 | 需手动跑 restart.bat/restart-service.bat（均需管理员权限） | 如需 7×24 在线，需注册 Windows 服务或计划任务 | 🟡 一般 |
| 5 | 日常 ingest 依赖人工丢新资料进 `总结好的大纲以及笔记/`，无自动采集 | 部分采集（短视频爆款）已自动化，其余仍靠手动 | 视需要扩展采集范围 | 🟡 一般 |
| 6 | 交接文档本身尚未归档到知识库对应位置 | 本次生成的输出在 skill 工作区 | 确认后归档 | 🟢 低 |

## 6. 下一步计划

1. **（立即）确认盘符**：核实知识库到底在 `E:\` 还是 `F:\`，并把 `.claude/CLAUDE.md`、`CLAUDE.md`、`自动维护知识库/CLAUDE.md` 里的路径统一为实际盘符。
2. **（立即）核对目录**：确认 `收件箱/`、`已整理好的文件/` 是否需要创建，或将规则修正为指向 `总结好的大纲以及笔记/`。
3. **（之后）验证两个助手在线**：重启飞书服务、重启企业微信服务，确认消息收发、PDF 处理、落盘全链路正常。
4. **（之后）把本交接文档归档**：经用户确认后放入知识库项目文件夹（如 `总结好的大纲以及笔记/` 下合适位置），并让下一个 AI 读取启动包继续日常维护。
5. **（之后）持续 ingest**：有新资料进来时按 ingest 工作流写入 wiki，保持 index/log 同步。

## 7. 关键决策与踩坑记录

- **选型 LLM Wiki 而非 RAG/embedding**：页面规模约 100 来源、数百页以内，纯 index 检索足够，无需 embedding/RAG 基建（见 `.claude/LLM-WIKI-SCHEMA.md`）。
- **三层权限设计**：原始层（可编辑、待整理）→ wiki 层（Claude 自由维护）→ schema 层（规则）。`已整理好的文件/` 设计为只读归档，防止 AI 误改成品。
- **消息助手身份分离**：飞书"增删改查=落日个人账号"、"总结/读书笔记=bot"；企业微信任务禁飞书操作，直接执行。
- **踩坑①——taskkill 全杀 Python**：restart.bat 用 `taskkill /f /im python.exe`，会杀掉所有 Python 进程（含 Claude 自己）。所以规则明确：启动飞书服务用 `python server.py`，不要用 restart.bat。
- **踩坑②——Codex 网络故障分环境**：公寓（DNS 污染/出口风控）与青旅（Vortex mode:direct + TUN off）是不同故障，排查先 `curl /configs` 看 mode，修复 `PATCH /configs {"mode":"rule"}`；文档按环境分开（知识库FAQ 04/05/06/09/10）。
- **踩坑③——飞书文档置顶**：新日期脚本块要放文档顶部，`block_insert_after` 用 `--block-id "page_id"` 会返回 degrade_code=1011，只能用 `block_move_after` 定位文档开头。
- **放弃的方案**：曾按 9 个主题文件夹组织来源，实际收敛为 6 个（学术裁缝/浪尖训练营/实习就业/技能/学校/知识库FAQ）；空目录与孤儿页在 8-13 迭代中清理。

## 8. 风险与待确认项

- ❓ **盘符存疑**：规则文件写 `E:\积昌的知识库 - 副本`，当前实际在 `F:\积昌的知识库 - 副本`。任何脚本/服务若硬编码 E: 路径会失效，需人工确认并统一。
- ❓ **收件箱/已整理好的文件不存在**：CLAUDE.md 反复引用但根目录无此二目录，可能是设计态。使用这些路径的技能/规则可能落盘失败，需确认。
- ❓ **两个助手当前是否在线**：未在本会话验证服务进程，接手后先跑 `lark-cli auth status` 与 `tasklist | findstr python` 确认。
- ❓ **隧道稳定性**：企业微信走内网穿透，重启后 URL 变化需人工回填企业微信后台。
- ⚠️ **权限已全开**：全库操作默认不再询问授权，接手方务必按 CLAUDE.md 的文件夹权限规则（只读/可写）操作，避免误改成品归档。

## 9. 资源与文件清单

| 资源 | 位置（相对 vault 根） | 一句话说明 |
|------|---------------------|-----------|
| 规则文件（schema 层） | `.claude/CLAUDE.md`、`.claude/LLM-WIKI-SCHEMA.md` | 先读这两个再干活 |
| Wiki 索引 | `自动维护知识库/index.md` | 61 页目录，先读它定位 |
| Wiki 时间线 | `自动维护知识库/log.md` | 只追加，记录每次 ingest/query/lint |
| Wiki 页面 | `自动维护知识库/wiki/` | 10 大类的结构化页面 |
| 原始来源（只读） | `总结好的大纲以及笔记/` | 6 个主题文件夹，来源材料 |
| 飞书助手服务 | `飞书智能助手/`（server.py、restart.bat、admin.py、config.json、logs/） | 飞书消息监听与文档操作 |
| 企业微信助手服务 | `微信智能助手/`（server.py、restart-service.bat、nssm.exe、current-tunnel-url.txt） | 企业微信回调 + 内网穿透 |
| 技能库 | `.claude/skills/`（27 个 skill） | 交接助手、文档转换+排版、华哥脚本撰写等 |
| Hook | `.claude/hooks/kb-maintenance-check.sh` | 驱动 GitHub 备份与 wiki 迭代提醒 |
| 备份标记 | `.last-github-backup`、`.last-wiki-maintain` | 记录最近一次执行日期 |
| 消息落盘 | `lark-resources/`、`wecom-resources/`、`lark-im-resources/` | 飞书/企业微信上传文件与中间产物 |
| 本轮交接产物 | `.claude/skills/交接助手-workspace/` | 交接文档工作区（含本文件） |

---

---

# 积昌的知识库 交接文档（给 AI 版 / 启动包）

> 下面的内容是给下一个 AI 智能体的**启动包**，可直接整段复制给 Claude / DeepSeek / Codex 作为上下文。目标是让 AI 读完即能无缝续作。

## 0. 交接摘要（启动包，500 字内）

项目是"积昌的知识库"——一个运行在 `F:\积昌的知识库 - 副本` 的 Obsidian vault，按 LLM Wiki 方法论由 AI 持续维护：原始来源在 `总结好的大纲以及笔记/`，AI 整理的 wiki 在 `自动维护知识库/`，规则在 `.claude/`。当前 wiki 61 页、10 大类、无孤儿页；挂载两个消息助手（飞书 `飞书智能助手/server.py`、企业微信 `微信智能助手/server.py`）；27 个 skill；GitHub 每周备份 + wiki 每 3 天迭代由 hook 驱动（`.claude/hooks/kb-maintenance-check.sh`）。

**最关键三件事**：
1. ✅ 已完成：wiki 三层架构稳定运行，2026-08-17 全库迭代完毕；
2. 🚧 卡在：规则文档写 `E:\` 但实际在 `F:\`，且 `收件箱/`、`已整理好的文件/` 目录不存在但被规则引用——需要人工确认；
3. ▶️ 下一步第一件事：先读 `自动维护知识库/index.md` 和 `.claude/CLAUDE.md`，再跑 `lark-cli auth status` 确认飞书助手是否在线。

从"确认盘符路径 + 验证两个助手在线"续最省力，不要重做 wiki。

## 1. 项目总览与验收标准

- 定位：AI 持续维护的个人知识库 + 消息助手控制中心。
- 最终目标：新资料进入 `总结好的大纲以及笔记/` 后，AI 能按 ingest 工作流整理进 wiki、更新 index/log；用户提问时按 query 工作流检索回答；消息助手 7×24 接收飞书/企业微信消息。
- **验收标准**：① 三层目录结构清晰、index.md 与实际页面一致（本次已达成 61/61）；② 对任一新增来源能跑通 ingest（读→写 wiki→更新 index→追加 log）；③ 飞书与企业微信各能收发一条测试消息并落盘。

## 2. 文件地图（精确路径）

根目录 = `F:\积昌的知识库 - 副本`（下文相对路径均以此为准）：

| 路径 | 作用 | 状态 |
|------|------|------|
| `CLAUDE.md` | 根规则文件 | 已存在（内含路径写 E:，需修正） |
| `.claude/CLAUDE.md` | 契约层规则（LLM Wiki 维护指令） | 已存在 |
| `.claude/LLM-WIKI-SCHEMA.md` | Wiki 维护规范（三层架构、工作流、页面规范） | 已存在 |
| `.claude/hooks/kb-maintenance-check.sh` | 每天检查 GitHub 备份 + wiki 迭代到期 | 已存在 |
| `.claude/skills/` | 27 个 skill | 已存在 |
| `自动维护知识库/index.md` | 内容目录（先读它） | 已完成（61 页） |
| `自动维护知识库/log.md` | 时间线日志（只追加） | 已完成 |
| `自动维护知识库/wiki/` | 全部 wiki 页面 | 已完成（61 页） |
| `自动维护知识库/LLM Wiki.md` | Karpathy 方法论原文 | 已完成 |
| `总结好的大纲以及笔记/` | 原始来源（学校/实习就业/技能/浪尖训练营/知识库FAQ/学术裁缝） | 只读，持续新增 |
| `飞书智能助手/` | 飞书服务（server.py、restart.bat、admin.py、config.json、logs/） | 已存在 |
| `微信智能助手/` | 企微服务（server.py、restart-service.bat、nssm.exe、config.json、current-tunnel-url.txt、logs/） | 已存在 |
| `wecom-resources/`、`lark-resources/`、`lark-im-resources/` | 消息文件落盘 | 已存在 |
| `.last-github-backup` | 最近 GitHub 备份日期 | 2026-08-17 |
| `.last-wiki-maintain` | 最近 wiki 迭代日期 | 2026-08-17 |
| `收件箱/`、`已整理好的文件/` | 规则中引用但当前不存在 | ❓ 待确认 |

## 3. 已完成工作（全量逐条）

- wiki 初始化与重构（07-11）：三层架构 + 多维分类目录。
- 核心知识录入（07-11~07-14）：实习求职 6 页、实习训练营 9 页、智灌云联项目 19 页、学术裁缝 4 页、自媒体运营 8 页、AI 与技术工具 8 页、行业知识 3 页、对比分析 1 页、编程 1 页、销售技能 1 页 = 共 61 页。
- 飞书智能助手（07-14 起）：server.py 双模式接管、admin 管理、restart.bat。
- 企业微信智能助手（07-14 起）：FastAPI + 内网穿透 + `python server.py --with-tunnel`。
- 自动化 hook（持续）：GitHub 每周备份 + wiki 每 3 天迭代到期提醒。
- 全库 lint/ingest（08-13、08-17）：补录 7 孤儿页、清理空目录、短视频爆款采集系统大版本更新（来源 3→7）。

## 4. 当前精确进度

- 最后一步有效操作（08-17）：`自动维护知识库/log.md` 记录"ingest/lint | 全库迭代：短视频爆款采集系统大版本更新"；index.md 统计 61 页、10 大类；收件箱为空。
- 备份/迭代标记：`.last-github-backup` = `.last-wiki-maintain` = `2026-08-17`（均已到期处理）。
- wiki 状态：61/61 页与 index 完全一致，无孤儿页、无遗漏页。

## 5. 未完成事项（全量逐条）

| # | 事项 | 阻塞原因 | 前置条件 | 完成标准 | 优先级 |
|---|------|---------|---------|---------|--------|
| 1 | 统一盘符路径 E:→F: | 规则文档与实际目录不一致 | 人工确认 | `.claude/CLAUDE.md`、`CLAUDE.md` 等全部改为实际路径 | 🔴 |
| 2 | 处理收件箱/已整理好的文件缺失 | 设计态 vs 落地态不一致 | 用户确认 | 补齐目录或修正规则引用 | 🟠 |
| 3 | 验证两助手在线 | 未在本会话验证 | 跑服务 | 各收发一条测试消息 | 🟠 |
| 4 | 隧道 URL 固定 | 内网穿透方案限制 | 决策是否上云 | 后台回调长期有效 | 🟡 |
| 5 | 服务开机自启 | 未配置 | 注册服务 | 重启后服务自动拉起 | 🟡 |

## 6. 下一步行动计划（命令级）

1. **读规则**：`Read F:\积昌的知识库 - 副本\.claude\CLAUDE.md` + `Read F:\积昌的知识库 - 副本\自动维护知识库\index.md`。
2. **确认飞书助手在线**：`lark-cli auth status`；再 `tasklist /fi "imagename eq python.exe"` 看有无 `server.py` 进程。未运行则 `cd F:\积昌的知识库 - 副本\飞书智能助手 && python server.py`（**不要用 restart.bat，会全杀 python**）。
3. **确认企微助手在线**：检查 `F:\积昌的知识库 - 副本\微信智能助手\server_pid.txt` 与 `current-tunnel-url.txt`；如需重启用 `restart-service.bat`（管理员）或 `python server.py --with-tunnel`。
4. **处理盘符/目录问题**：向用户确认 `E:` 还是 `F:`，确认后统一修正规则文件中的路径；确认 `收件箱/`、`已整理好的文件/` 是否创建。
5. **日常维护**：新资料进 `总结好的大纲以及笔记/` 后按 ingest 工作流写 wiki、更新 index.md、追加 log.md（格式 `## [YYYY-MM-DD] ingest | 标题`）。
6. **预期产出**：路径一致、两助手在线可收发、wiki 保持同步。

## 7. 环境与配置依赖（完整清单）

- **运行环境**：Windows 11 Pro；Python 3.13（另有 3.11）位于 `C:\Users\asus\AppData\Local\Programs\Python\`。
- **CLI 工具**：`lark-cli`（`C:\Users\asus\AppData\Roaming\npm\lark-cli.cmd`）；`nssm`（`C:\Users\asus\AppData\Local\Microsoft\WinGet\Packages\NSSM...`）。
- **服务**：飞书服务 `飞书智能助手/server.py`；企微服务 `微信智能助手/server.py`（`--with-tunnel` 走内网穿透）。
- **Hook**：`.claude/hooks/kb-maintenance-check.sh`（UserPromptSubmit 触发）。
- **GitHub**：账号 `xieji-star`；仓库 `https://github.com/xieji-star/jichang-zhishiku`；每周一/距上次≥7 天备份，每次新建 `积昌的知识库<MMDD>/` 日期文件夹，仅留最近 10 版。
- **密钥/token**：飞书/企微的 app_secret、token 等存放在 `飞书智能助手/config.json`、`微信智能助手/config.json`（值已脱敏，**只引用位置，不要打印明文**）。

## 8. 数据与状态快照

- wiki：61 页文本（`自动维护知识库/wiki/`），index 与 log 同步至 08-17。
- 消息落盘：`lark-resources/`（飞书）、`wecom-resources/`（企微）内为历史上传文件，**保留勿删**（用户可能后续使用）。
- 日志：`飞书智能助手/logs/`、`微信智能助手/logs/`（含 lark-service.log、tunnel.log、service-output.log）。
- 临时/测试文件：根目录存在 `_*.txt`（`_p1_out.txt`、`_persona_raw.txt` 等）、`_test_*.pdf`、`*.py`（`积昌的知识库 - 副本_update_doc_20260816.py`）等疑似中间产物，**按 CLAUDE.md 临时文件规则处理后清理，不确定的询问用户**。
- 需保留的中间产物：`.last-github-backup`、`.last-wiki-maintain`、`server_pid.txt`、`current-tunnel-url.txt`。

## 9. 关键决策与踩坑记录

- 选 LLM Wiki 而非 RAG：规模小，纯 index 检索足够。
- 身份分离：飞书 CRUD 用"落日"，总结/读书笔记用 bot"谢积昌的飞书CLI"；企微任务禁飞书操作。
- 踩坑：`restart.bat` 的 `taskkill /f /im python.exe` 会杀掉所有 python（含 Claude）→ 改用 `python server.py`。
- 踩坑：Codex 网络故障分环境（公寓 DNS/出口风控 vs 青旅 mode:direct+TUN off），排查 `curl /configs`、修复 `PATCH /configs {"mode":"rule"}`。
- 踩坑：飞书文档置顶需用 `block_move_after`（`block_insert_after --block-id "page_id"` 返回 degrade_code=1011）。

## 10. 风险与待确认项

- ❓ 盘符 `E:` vs `F:` 不一致，所有硬编码 E: 的脚本可能失效。
- ❓ `收件箱/`、`已整理好的文件/` 不存在但被规则引用，涉及这些目录的技能/流程可能落盘失败。
- ❓ 两助手当前在线状态未验证，接手后先跑命令确认。
- ⚠️ 权限全开，操作前先读 CLAUDE.md 的文件夹权限规则（只读/可写），勿误改归档。

## 11. 续作启动手册（从零恢复）

1. **先读**：`F:\积昌的知识库 - 副本\.claude\CLAUDE.md` → `.claude/LLM-WIKI-SCHEMA.md` → `自动维护知识库/index.md` → `自动维护知识库/log.md`（先看最近条目了解在做什么）。
2. **确认环境**：`cd F:\积昌的知识库 - 副本`；`lark-cli auth status` 看飞书身份；`where python` 看解释器。
3. **启动/重启飞书助手**：`cd 飞书智能助手` 后 `python server.py`（后台）；日志在 `logs/lark-service.log`。
4. **启动/重启企微助手**：`cd 微信智能助手` 后 `python server.py --with-tunnel`（后台）；观察 `logs/tunnel.log` 生成 `current-tunnel-url.txt`。
5. **验证"续上了"**：看到飞书日志出现 `开始监听飞书消息` + `lark-cli 进程 PID` 行 = 飞书续上；企微侧给机器人发 `/帮助` 能收到回复 = 企微续上；`grep "^## \[" 自动维护知识库/log.md | tail -5` 能看到最近的维护记录 = wiki 续上。
6. **接一个真实任务**：丢一份新 PDF 到 `总结好的大纲以及笔记/`，跑通一遍 ingest（读→写 wiki→更新 index→追加 log），即证明交接完成。
