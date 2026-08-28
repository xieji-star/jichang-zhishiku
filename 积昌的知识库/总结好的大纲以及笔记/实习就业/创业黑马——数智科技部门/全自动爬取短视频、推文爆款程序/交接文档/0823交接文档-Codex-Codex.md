---
title: 全自动爬取短视频、推文爆款程序 交接文档（给 Codex 版）
aliases:
  - 0823交接文档-Codex-Codex
  - Short-Video and Viral-Post Collector Codex Handoff
date: 2026-08-23
updated: 2026-08-23
project: 全自动爬取短视频、推文爆款程序
handoff_to: Codex 全新对话框
document_type: relay-handoff
status: verified-documentation
language: English-first-and-Simplified-Chinese
tags:
  - handoff
  - codex
  - round-5
  - douyin
  - obsidian
source_notes:
  - "[[0821凌晨-开发日志]]"
  - "[[Codex接力棒]]"
---

# Full-Automation Short-Video and Viral-Post Collector Handoff (for Codex) / 全自动爬取短视频、推文爆款程序 交接文档（给 Codex 版）

> [!summary] Verified launch packet / 已核验启动包
> **EN:** This is a relay continuation, not a new-project plan. The verified Douyin-local track can store creator, video, comment, and transcription data; the Round-4 task closed with 135 videos, 2,376 comments, and 135 transcription records. Link Collection R1–R4C/P2 is frozen at exact source identities, while Subtitle Direct remains frozen/OFF. The latest Round-5 candidate passed a sealed SelfTest, and Collect64 enumerated the exact 64 tests, but Collect64 failed during evidence sealing and therefore remains RED/unsealed.
>
> **中文：** 这是接力续作，不是新项目规划。已核验的抖音本地链路可以保存达人、视频、评论和口播稿数据；第4轮任务以 135 条视频、2,376 条评论和 135 条口播记录闭环。链接采集 R1–R4C/P2 按精确源码身份冻结，字幕直取继续冻结/OFF。最新第5轮候选已通过封印完整的 SelfTest；Collect64 虽精确枚举出 64 项测试，但在证据封印阶段失败，因此仍是 RED/未封印。
>
> <span style="color:#2980b9">Binding truth / 约束事实：standard collection is now open only under the expiring <code>round5_manual_local</code> authorization for the owner's non-commercial local manual test. Live health reports <code>eligible=true</code> and <code>real_collection_ready=true</code>. This is not production approval; simultaneous multi-account, commercial/SaaS, Subtitle Direct, and autonomous Agent initiation remain blocked. / 标准采集现仅在会过期的 <code>round5_manual_local</code> 授权下开放，用于所有者的非商业本机手动测试。在线健康状态返回 <code>eligible=true</code> 与 <code>real_collection_ready=true</code>。这不是生产批准；多账号同时采集、商业/SaaS、字幕直取及 Agent 自主发起继续阻断。</span>
>
> <span style="color:#e74c3c">First manual result / 首次手测结果：the user personally started task <code>cb8873ba4942472bab1063663634674b</code> for creator “华哥聊论文”; it ended <code>failed</code> at 22:12:23 Beijing time. MediaCrawler accepted 15/15 candidate videos, then the 16th comment request exceeded the per-attempt comment budget (<code>16/15</code>); an earlier Argus event caused the backend to expose <code>risk_paused</code>. The authorization problem is fixed, but this new platform/runtime failure is not fixed. / 用户本人已为“华哥聊论文”启动任务 <code>cb8873ba4942472bab1063663634674b</code>；任务于北京时间22:12:23以 <code>failed</code> 终止。MediaCrawler 已接受15/15条候选视频，随后第16次评论请求超过单次评论预算（<code>16/15</code>）；更早的一次Argus事件使后端对外呈现 <code>risk_paused</code>。授权问题已解决，但这一新的平台/运行时失败尚未修复。</span>
>
> <span style="color:#e74c3c">Second terminal result / 第二次终态结果：the user then started task <code>f89d2b9a62744f3695bcaff3eeea338e</code> for “计算机博士迪哥”. It ended <code>failed</code> at 22:33:02 Beijing time after all 9 bounded route attempts. Firefox and Edge each reproduced <code>comment:16/15</code> three times with <code>argus=0</code>; three Chrome child runs exited successfully but returned zero candidates/rows, so the platform truthfully refused to mark the task complete. All 18 immutable captures were hash-verified. / 用户随后为“计算机博士迪哥”启动任务 <code>f89d…</code>；任务于北京时间22:33:02在完成9次有界线路尝试后以 <code>failed</code> 结束。Firefox与Edge各三次均在 <code>argus=0</code> 时复现 <code>comment:16/15</code>；三次Chrome子进程虽成功退出，却返回0候选/0数据，因此平台如实拒绝标记完成。18份不可变日志均已核验哈希。</span>
>
> <span style="color:#2980b9">User-owned decision / 用户决定：the user personally chooses creators and videos for every manual Round-5 retry; agents must not choose or submit them. Collect64 retry remains postponed until a successful or explicitly accepted manual result exists. Link-only collection must not collect creator-profile/homepage data, while the standard collection flow must retain creator-data capability. / 第5轮每次手动重试仍由用户本人选择达人和视频，Agent 不得代选或代提交；Collect64 重试继续推迟，直到形成成功或由用户明确接受的手测结果。链接采集不得采集达人主页/档案数据，但标准采集流程必须保留达人数据能力。</span>

## 0. Handoff Summary / 0. 交接摘要

### 0.1 What this project is / 项目是什么

**EN:** A Windows-local data-collection and analysis platform that uses a FastAPI backend, SQLite state, MediaCrawler/Douyin adapters, local transcription services, and a Miaoda-derived frontend. Its verified implementation focuses on user-selected Douyin creators/videos and a separate multi-link video-only collection route. The project title also mentions viral posts/tweets, but no implemented X/Twitter collection path was found in the inspected core backend, frontend, or README; that scope is marked <span style="color:#e67e22">❓ pending confirmation</span>.

**中文：** 这是一个 Windows 本地数据采集与分析平台，由 FastAPI 后端、SQLite 状态库、MediaCrawler/抖音适配器、本地口播转写服务以及妙搭派生前端组成。当前已核验实现重点是由用户选择的抖音达人/视频，以及独立的多链接“仅视频数据”采集路由。项目名称还包含“推文爆款”，但在已检查的核心后端、前端与 README 中未发现已实现的 X/Twitter 采集链路，因此该范围标记为 <span style="color:#e67e22">❓待确认</span>。

### 0.2 The three facts the next Codex must retain / 新 Codex 必须保留的三项事实

1. **Completed evidence / 已完成证据**
   - **EN:** Round-4 local data exists; Link R1–R4C/P2 and its runtime close-race repair have exact frozen hashes; Subtitle Direct is intentionally OFF; candidate <code>AEF3B3E8…BB52</code> has one sealed SelfTest PASS.
   - **中文：** 第4轮本地数据已存在；Link R1–R4C/P2 及运行时 close 竞态修复具有精确冻结哈希；字幕直取明确关闭；候选 <code>AEF3B3E8…BB52</code> 已有一次封印完整的 SelfTest PASS。
2. **The relay baton / 接力棒**
   - **EN:** The authorization blocker is resolved. Both user-owned Round-5 tasks are terminal failed. The second task reproduced comment request 16/15 on all six Firefox/Edge attempts without Argus; its three Chrome attempts returned zero candidates and zero imported rows. The next baton is a bounded platform fix with regression evidence, followed by a user-owned retry if the user requests it.
   - **中文：** 授权阻断已解决。两次由用户发起的第5轮任务均已失败终止。第二个任务在Firefox/Edge共六次尝试中均无Argus地复现评论请求16/15；三次Chrome尝试返回0候选、0导入。下一根接力棒是有界平台修复与回归证据；若用户要求，再由用户本人重试。
3. **The first next action / 下一步第一件事**
   - **EN:** Confirm task <code>f89d…</code> remains terminal failed and verify its 18 immutable captures, then reproduce the sparse/paginated-comment budget path in tests and decide the intended bounded behavior before editing. Do not raise the budget blindly and do not let an Agent issue a live retry.
   - **中文：** 确认任务 <code>f89d…</code> 仍为失败终态并核验18份不可变日志，然后在测试中复现稀疏/分页评论预算路径，再于修改前确定有界行为。禁止盲目提高预算，也禁止由Agent发起真实重试。

<span style="color:#2980b9">Shortest safe continuation / 最省力的安全续接：start at relay item #1—the captured comment-budget/risk-precedence defect—then return control to the user for the retry. Do not start Collect64 and do not rewrite unrelated platform slices. / 从接力项 #1（已捕获的评论预算/风控优先级缺陷）开始，修复后把重试控制权交还用户；不得先跑 Collect64，也不得重写无关平台切片。</span>

## A. Overall Task Goal Summary / A. 总任务目标总结

### A.1 Precise goal anchor / 精确目标锚点

**EN:** Build a Windows-local platform for the project owner to choose creators, videos, data types, and collection routes, then collect, persist, inspect, and export trustworthy short-video intelligence without fabricated fields. Standard collection must support video data, transcripts, creator data, or all three; the dedicated Link route must accept multiple video links but must not crawl creator profiles/homepages, creator history, comments, avatar assets, search/hot pages, or creator collections. Success means the selected workflow completes with observable task status and database deltas, Round-5 offline evidence is sealed in order, manual acceptance is recorded by the user, and production/multi-account operation remains blocked until its separate safety gates pass. The final deliverables are the working source tree, local SQLite data, detached Round-5 evidence, configuration templates with secrets excluded, and this self-contained handoff.

**中文：** 构建一个 Windows 本地平台，让项目所有者自行选择达人、视频、数据类型和采集路由，并在不补造字段的前提下采集、持久化、查看和导出可信短视频情报。标准采集必须支持“视频数据、口播稿、达人数据、全采集”；独立 Link 路由可接收多个视频链接，但不得抓取达人档案/主页、达人历史、评论、头像资产、搜索/热榜页面或达人收藏。成功标准是：用户所选工作流出现可观察的任务完成状态与数据库增量；第5轮离线证据按顺序完成封印；用户手动验收结果被记录；生产和多账号并发在独立安全门禁通过前继续阻断。最终交付物包括可运行源码、本地 SQLite 数据、第5轮外置证据、不含密钥值的配置模板以及这份自包含交接文档。

### A.2 Service owner and use case / 服务对象与使用场景

- **EN:** Primary user: the project owner performing manual research and acceptance on a local Windows machine.
  **中文：** 主要用户：在本地 Windows 机器上进行手动选材、研究与验收的项目所有者。
- **EN:** Verified current platform scope: Douyin creator/video intelligence. Link collection is video-scoped only.
  **中文：** 当前已核验平台范围：抖音达人/视频情报。链接采集仅限视频维度。
- **EN:** <span style="color:#e67e22">❓ The intended X/Twitter source, fields, authentication, rate limits, and acceptance criteria are not present in verified implementation evidence.</span>
  **中文：** <span style="color:#e67e22">❓ 已核验证据中没有 X/Twitter 的目标数据源、字段、认证、限流与验收标准。</span>

### A.3 Verifiable success criteria / 可检验成功标准

| ID | English acceptance signal | 中文验收信号 |
|---|---|---|
| A1 | The frontend loads at the printed local route; backend/frontend listeners have known ownership; no duplicate unknown services are killed blindly. | 前端可通过打印的本地路由加载；前后端监听者归属明确；不得盲杀未知或重复服务。 |
| A2 | Standard collection exposes and honors <code>video_data</code>, <code>transcript</code>, <code>creator</code>, and <code>all</code>; a user-selected task reaches a terminal state and database counts change exactly as expected. | 标准采集提供并正确执行 <code>video_data</code>、<code>transcript</code>、<code>creator</code>、<code>all</code>；用户所选任务到达终态，数据库计数按预期变化。 |
| A3 | Link collection accepts one task with multiple video links and stores only video-scoped fields; creator-profile/homepage tables do not gain rows because of Link. | Link 可在一个任务中接收多个视频链接，只保存视频维度字段；不得因 Link 导致达人档案/主页表新增记录。 |
| A4 | Round-5 phases complete in contractual order <code>SelfTest → Collect64 → Preflight64 → Full</code>, each under a fresh phase-specific Director permit with nonempty summary, manifest, and seal. | 第5轮按 <code>SelfTest → Collect64 → Preflight64 → Full</code> 契约顺序完成；每阶段均有新的专用总监许可，以及非空 summary、manifest、seal。 |
| A5 | The user—not an agent—chooses the creators/videos and records the manual Round-5 result. | 由用户本人而非 Agent 选择达人/视频，并记录第5轮手动测试结果。 |
| A6 | Parallel multi-account production remains blocked until explicit rate-limit verification changes from false with evidence; legal/license, ACL, credentials, canary, rollback, and monitoring gates are separately closed. | 多账号并发生产在限流验证从 false 变为有证据的通过前继续阻断；法律/许可、ACL、凭据、canary、回滚与监控门禁分别闭环。 |
| A7 | Tweet/X acceptance is either formally removed from this milestone or implemented and tested against a written field/source contract. | 推文/X 范围要么从本里程碑正式移除，要么依据书面字段/数据源契约实现并测试。 |

### A.4 Terminal deliverables / 终极交付物

| Deliverable | Path | State |
|---|---|---|
| Formal source tree / 正式源码树 | <code>D:\全自动爬取短视频、推文爆款程序</code> | Present; root is not a Git repository / 存在；根目录不是 Git 仓库 |
| Frontend Git subrepository / 前端 Git 子仓库 | <code>D:\全自动爬取短视频、推文爆款程序\deployments\miaoda-matrix-radar</code> | Present, dirty, unfrozen / 存在、有未提交改动、未冻结 |
| Local data / 本地数据 | <code>D:\全自动爬取短视频、推文爆款程序\data\radar.sqlite3</code> | Present; preserve / 存在；必须保留 |
| Round-5 harness / 第5轮门禁 | <code>C:\Users\asus\r5h</code> | Present; current bytes identified / 存在；当前字节已识别 |
| Retained evidence / 保留证据 | <code>C:\Users\asus\r5</code> | Present; preserve all named runs / 存在；保留所有指定运行 |
| This handoff / 本交接 | <code>F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\交接文档\0823交接文档-Codex-Codex.md</code> | Final output / 最终产物 |

## B. Current Task Progress Summary / B. 当前任务进度总结

### B.1 Percentage, stage, and basis / 百分比、阶段与依据

**EN:** The **verified Douyin engineering track is approximately 80% complete**. This is a weighted relay estimate, not a test-pass percentage and not a production-release statement. The completion percentage for the entire named “short-video + tweet” project is <span style="color:#e67e22">❓ not truthfully measurable</span> until Tweet/X scope is decided.

**中文：** **已核验的抖音工程链路约完成 80%**。这是用于接力的加权估算，不是测试通过率，也不是生产放行声明。整个“短视频 + 推文”命名项目的完成比例在 Tweet/X 范围定稿前 <span style="color:#e67e22">❓无法诚实量化</span>。

| Weighted component / 加权项 | Earned / Max | Evidence / 证据 |
|---|---:|---|
| Local pipeline and Round-4 data baseline / 本地链路与第4轮数据基线 | 30 / 30 | 135 videos, 2,376 comments, 135 transcriptions; terminal task preserved / 135视频、2,376评论、135口播；终态任务已保留 |
| Link-only product boundary and frozen implementation / Link仅视频边界与冻结实现 | 15 / 15 | R1–R4C/P2 exact identities plus close-race repair / 精确身份与 close 竞态修复 |
| Frontend/manual readiness / 前端与手测可用性 | 11 / 15 | UI and four standard modes exist; scoped authorization is live; first user run reached a truthful failure; runtime defect and provenance remain / UI及四种标准模式存在；范围授权已在线；首次用户任务形成真实失败终态；运行时缺陷与来源冲突仍在 |
| Round-5 offline validation / 第5轮离线验证 | 12 / 20 | Current sealed SelfTest PASS; Collect64 list 64/64 but phase unsealed / 当前SelfTest封印PASS；Collect64列出64/64但阶段未封印 |
| Safety and frozen-scope control / 安全与冻结范围控制 | 8 / 10 | Subtitle OFF, Link frozen, production NO-GO preserved / 字幕关闭、Link冻结、生产NO-GO保留 |
| Production closure / 生产闭环 | 1 / 5 | Fail-closed gates exist; legal/rate/canary/rollback/monitoring incomplete / 已有失败关闭门禁；法律、限流、canary、回滚、监控未闭环 |
| Relay documentation / 接力文档 | 3 / 5 | Prior notes exist; this document completes the current relay package / 已有往期笔记；本文完成当前接力包 |
| **Verified Douyin total / 已核验抖音总计** | **80 / 100** | Engineering estimate only / 仅工程估算 |

### B.2 Current milestone / 当前里程碑

- **Completed / 已走完：** Round-4 dataset closure; Link R1–R4C/P2 source closure; Link runtime close-race repair; Subtitle Direct code-only evidence and OFF/freeze boundary; current AEF3 sealed SelfTest.
- **Current position / 当前所在：** scoped standard collection remains eligible; both human-started Round-5 tasks are terminal <code>failed</code>; active standard and Link counts are both 0. The second task reproduced <code>comment:16/15</code> on six Firefox/Edge attempts with <code>argus=0</code>, then three Chrome attempts returned no candidates/rows. The immediate work is #1. The last attempted offline phase remains AEF3 Collect64: enumeration passed 64/64, evidence sealing failed.
- **Remaining / 还剩：** bounded fix plus a successful or explicitly accepted user retry; Link manual boundary proof if included; post-manual fresh Collect64; Preflight64; Full; frontend provenance/freeze; source/document mismatches; production gates; Tweet/X scope.

### B.3 Full three-state list / 已完成、进行中、未开始全量清单

**Completed / 已完成**

- Round-4 task <code>12fa1f267316452e9c5b433d51b4c23b</code> reached <code>completed</code>, progress 100.
- Nine creators completed 15 videos each; “毒舌电影” was user-skipped and truthfully excluded from failure counts.
- Standard UI exposes video data, transcript, creator data, and all-data modes.
- Link R1–R4C/P2 exact source identities are present.
- Before the manual runs, the only proven and already-fixed Round-5 platform defect was the Link runtime close race; the later comment-budget defect remains open. / 手测前唯一已证且已修的第5轮平台缺陷是Link运行时close竞态；后来暴露的评论预算缺陷仍开放。
- Subtitle Direct remains frozen/OFF; its former capacity was assigned to Platform Optimization.
- Current candidate AEF3 SelfTest has a nonempty sealed evidence set.
- The expiring non-commercial <code>round5_manual_local</code> authorization is live; 15 bounded tests pass; backend health reports ready.

**In progress or blocked / 进行中或受阻**

- Standard manual collection access: open; two user-selected tasks recorded as <code>failed</code>. The second exposed <code>request_budget_exceeded:comment:16/15:total=39/60</code> six times without Argus across Firefox/Edge, confirming the budget defect is independent of the first task’s earlier Argus signal.
- Round-5 evidence chain: SelfTest complete; Collect64 unsealed; retry deliberately postponed.
- Frontend redesign: functionality exists, but collection CSS provenance conflicts with the prior handoff and the Git subrepo is dirty.
- README/account/default reconciliation: code and docs disagree.

**Not started for the current candidate / 当前候选未开始**

- Fresh post-manual Collect64.
- AEF3 Preflight64.
- AEF3 Full.
- Production canary, rollback exercise, production monitoring closure.
- Verified simultaneous multi-account production.
- Written Tweet/X implementation contract and acceptance.

### B.4 Gap to A and blocking points / 与 A 的差距及阻塞点

1. <span style="color:#e74c3c">Platform/runtime blocker:</span> both user tasks failed. The second reached comment request 16/15 on six Firefox/Edge attempts with argus=0, so this is not merely the first task’s risk signal. Reconcile the 15-call comment budget with sparse/paginated replies and preserve primary/secondary failure causes; also keep the correct “child exit 0 but zero imported rows is failure” invariant from Chrome attempts.
2. <span style="color:#e74c3c">Round-5 blocker:</span> Collect64 evidence is unsealed; current permit expired; retry postponed by the user.
3. <span style="color:#e74c3c">Release blocker:</span> Preflight64 and Full have no current-candidate PASS.
4. <span style="color:#e67e22">Frontend blocker:</span> dirty subrepo and unresolved CSS provenance prevent a global frontend freeze claim.
5. <span style="color:#e67e22">Source risk:</span> duplicate <code>load_accounts()</code> definitions and stale README defaults/counts.
6. <span style="color:#e74c3c">Production blocker:</span> parallel request rate-limit verification is explicitly false; commercial/SaaS authorization, ACL, credentials, canary, rollback, and monitoring are incomplete.
7. <span style="color:#e67e22">Scope blocker:</span> Tweet/X work is not evidenced.

## Related Notes / 相关笔记

- [[0821凌晨-开发日志]] — the immediate prior relay, now superseded only where this document carries later AEF3 evidence and the 2026-08-23 user decisions / 直接上一份接力；仅在本文包含更晚 AEF3 证据与 2026-08-23 用户决定之处被替代。
- [[Codex接力棒]] — older Codex handoff retained for historical background; its Round-4-in-progress status is stale / 更早的 Codex 交接，仅保留历史背景；其中“第4轮进行中”已过时。
- [[0820下午-开发日志]] — predecessor linked through the 0821 handoff / 通过 0821 交接关联的更早记录。

## Index / 索引

- [[#0. Handoff Summary / 0. 交接摘要]]
- [[#A. Overall Task Goal Summary / A. 总任务目标总结]]
- [[#B. Current Task Progress Summary / B. 当前任务进度总结]]
- [[#1. Project Overview and Acceptance / 1. 项目总览与验收标准]]
- [[#2. File Map / 2. 文件地图]]
- [[#3. Completed Work / 3. 已完成工作]]
- [[#4. Exact Current Progress / 4. 当前精确进度]]
- [[#5. Unfinished Relay Batons / 5. A 没做完的事（接力棒）]]
- [[#6. A-to-B Relay Overview / 6. A→B 接力总览]]
- [[#7. Command-Level Action Plan / 7. 下一步行动计划（命令级）]]
- [[#8. Environment and Configuration / 8. 环境与配置依赖]]
- [[#9. Data and State Snapshot / 9. 数据与状态快照]]
- [[#10. Decisions and Pitfalls / 10. 关键决策与踩坑记录]]
- [[#11. Risks and Pending Confirmations / 11. 风险与待确认项]]
- [[#12. From-Zero Continuation Manual / 12. 续作启动手册（从零恢复）]]
- [[#13. Codex-Specific Addendum / 13. 按 Codex 定制的附加内容]]
- [[#Pre-Delivery Self-Check / 交稿前自查]]
- [[#Legacy Unknowns Summary / 遗留不确定项（❓）汇总]]

## 1. Project Overview and Acceptance / 1. 项目总览与验收标准

### 1.1 One-sentence positioning / 一句话定位

**EN:** A local-first Douyin research platform that lets the owner choose collection targets and data modes, persists trustworthy structured data in SQLite, and presents it through a local web interface, with a separately constrained multi-link video-only workflow.

**中文：** 一个本地优先的抖音研究平台，让所有者选择采集目标与数据模式，将可信结构化数据保存到 SQLite，并通过本地 Web 界面呈现，同时提供边界独立、仅采视频数据的多链接工作流。

### 1.2 Architecture in plain language / 白话架构

| Layer | Role | Verified entry |
|---|---|---|
| Frontend / 前端 | User selection, task display, data inspection / 用户选材、任务显示、数据查看 | <code>deployments\miaoda-matrix-radar\client</code> |
| Miaoda local server / 妙搭本地服务 | Hosts application server and frontend integration / 承载应用服务及前端集成 | Port 3100 |
| FastAPI backend / FastAPI后端 | Standard collection, Link APIs, task control, data APIs / 标准采集、Link接口、任务控制、数据接口 | <code>backend\app\main.py</code>, port 8000 |
| Providers / Provider层 | MediaCrawler/Douyin routing and deployment eligibility / MediaCrawler抖音路由与投产资格 | <code>backend\app\providers\mediacrawler.py</code> |
| State / 状态层 | SQLite task/data persistence / SQLite任务与数据持久化 | <code>data\radar.sqlite3</code> |
| Transcription / 转写 | Local ASR/transcript processing / 本地ASR与口播处理 | Port 8765 when active |
| Detached gate / 外置门禁 | Source mirroring, immutable candidate identity, offline phase evidence / 源码镜像、候选身份、离线阶段证据 | <code>C:\Users\asus\r5h</code> and <code>C:\Users\asus\r5</code> |

### 1.3 Product invariants / 产品不变量

- **EN:** Standard collection may collect creator data. The user explicitly clarified that “do not collect creator data” applies **only** to Link collection.
  **中文：** 标准采集可以采集达人数据。用户已明确：“不采集达人数据”**仅适用于 Link 链接采集**。
- **EN:** Link records may retain author name or Douyin ID when those are metadata of the video record; this is not permission to fetch a creator homepage/profile.
  **中文：** Link 视频记录可以保留作为视频元数据的作者名或抖音号；这不等于允许抓取达人主页/档案。
- **EN:** No agent selects Round-5 creators/videos for the user.
  **中文：** 任何 Agent 都不得替用户选择第5轮达人/视频。
- **EN:** “Service is listening” is not equivalent to “collection is eligible,” “Round 5 passed,” or “production released.”
  **中文：** “服务正在监听”不等于“采集具备资格”“第5轮通过”或“生产放行”。
- **EN:** Independent Code Director remains permanently independent and must never be merged into Platform Optimization or another implementation group.
  **中文：** 独立代码总监永久保持独立，禁止并入平台优化组或任何实现小组。

### 1.4 Acceptance checklist mapped to A / 映射到 A 的验收清单

- [ ] A1 local service ownership and route verified at execution time.
- [ ] A2 user-selected standard collection completes after reviewed authorization closure.
- [ ] A3 Link-only task proves zero creator-profile/homepage side effects.
- [ ] A4 all four Round-5 phases have fresh, ordered, sealed PASS evidence.
- [ ] A5 user manual result is recorded with chosen inputs and observed output.
- [ ] A6 production and parallel-account gates have separate evidence.
- [ ] A7 Tweet/X scope is formally decided and, if included, implemented and tested.

- [ ] A1 执行时本地服务归属与路由完成核验。
- [ ] A2 书面授权闭环后，用户所选标准采集完成。
- [ ] A3 Link-only 任务证明达人档案/主页零副作用。
- [ ] A4 四个第5轮阶段都有全新、按序、封印 PASS 证据。
- [ ] A5 记录用户手动选择的输入与观察结果。
- [ ] A6 生产及多账号并发门禁有独立证据。
- [ ] A7 Tweet/X 范围正式定稿；若纳入，则完成实现与测试。

### 1.5 Glossary / 术语表

| Term | English meaning | 中文含义 |
|---|---|---|
| Standard collection / 标准采集 | Creator-oriented workflow capable of video, transcript, creator, or all modes. | 面向达人的工作流，可采视频、口播、达人或全量。 |
| Link collection / 链接采集 | A separate workflow receiving video links and constrained to video-scoped data. | 接收视频链接的独立工作流，仅限视频维度数据。 |
| Candidate identity / 候选身份 | Hash-derived identity of exact harness/contract/guard/source-closure bytes. | 由精确门禁、契约、守卫与源码闭包字节派生的身份。 |
| Source closure / 源码闭包 | Exact set of source files included in the detached test candidate. | 外置测试候选包含的精确源码文件集合。 |
| Permit / 许可 | Phase-specific, candidate-bound, expiring Code Director authorization. | 绑定阶段、候选且会过期的代码总监授权。 |
| Seal / 封印 | Summary plus payload manifest and seal proving evidence completeness. | 由摘要、载荷清单与封印组成，证明证据完整。 |
| Fail-closed / 失败关闭 | Refuse execution when authorization or evidence is absent/invalid. | 授权或证据缺失/无效时拒绝执行。 |
| NO-GO | Explicitly not released for that phase or environment. | 对指定阶段或环境明确不放行。 |

## 2. File Map / 2. 文件地图

### 2.1 Formal roots / 正式根路径

| Relative path from project root / 项目根相对路径 | Absolute path / 绝对路径 | Purpose / 用途 | Current state / 当前状态 |
|---|---|---|---|
| <code>.</code> | <code>D:\全自动爬取短视频、推文爆款程序</code> | Sole formal source/data root / 唯一正式源码与数据根 | Present; not a Git repo / 存在；非Git仓库 |
| <code>README.md</code> | <code>D:\全自动爬取短视频、推文爆款程序\README.md</code> | Operator overview / 操作概览 | Present but stale on account count and transcript default / 存在，但账号数和默认口播数过时 |
| <code>start.ps1</code> | <code>D:\全自动爬取短视频、推文爆款程序\start.ps1</code> | Canonical local launcher / 标准本地启动脚本 | PowerShell parser reports 0 errors; not executed during handoff / 解析0错误；交接时未执行 |
| <code>.env.local</code> | <code>D:\全自动爬取短视频、推文爆款程序\.env.local</code> | Local secret/config values / 本地密钥与配置值 | Authorization path configured at line 22; all other values remain redacted / 第22行已配置授权路径；其他值继续脱敏 |
| <code>.env.example</code> | <code>D:\全自动爬取短视频、推文爆款程序\.env.example</code> | Config key template / 配置键模板 | Present / 存在 |
| <code>backend\requirements.txt</code> | <code>D:\全自动爬取短视频、推文爆款程序\backend\requirements.txt</code> | Backend pinned dependencies / 后端固定依赖 | Present / 存在 |
| <code>backend\config\accounts.json</code> | <code>D:\全自动爬取短视频、推文爆款程序\backend\config\accounts.json</code> | 51 enabled account definitions / 51个启用账号定义 | Present; differs from README / 存在；与README不一致 |
| <code>data\radar.sqlite3</code> | <code>D:\全自动爬取短视频、推文爆款程序\data\radar.sqlite3</code> | Live local project data and task state / 本地项目数据与任务状态 | 11,620,352 bytes at verification; preserve / 核验时11,620,352字节；保留 |

### 2.2 Core standard collection / 标准采集核心

| Relative path | Purpose | Key verified location | State |
|---|---|---|---|
| <code>backend\app\models.py</code> | API request models / API请求模型 | <code>CollectionRequest</code> line 142; effective transcript default logic lines 183–188 | Active |
| <code>backend\app\accounts.py</code> | Account loading/lookup / 账号加载与查找 | duplicate <code>load_accounts()</code> lines 37 and 54; <code>account_by_name()</code> line 66 | Active with source risk |
| <code>backend\app\services\collection.py</code> | Standard task lifecycle / 标准任务生命周期 | scoped eligibility gate line 125; <code>CollectionService.start()</code> line 569; call line 574 | Active for strict-serial local manual scope |
| <code>backend\app\providers\mediacrawler.py</code> | Provider and authorization preflight / Provider与授权预检 | scoped reviewed map line 50; <code>deployment_authorization_status()</code> line 886 | Eligible until 2026-08-31T15:59:59Z; production false |
| <code>backend\app\config.py</code> | Environment-backed config / 环境配置 | authorization path lines 110–112 | Key declared; exact document path is active through <code>.env.local:22</code> / 已声明配置键；精确路径通过.env.local生效 |
| <code>backend\app\main.py</code> | FastAPI routes / FastAPI路由 | Link start around line 930; standard collection POST line 983 | Active |
| <code>backend\app\services\multi_account\runner.py</code> | Multi-account scheduling / 多账号调度 | rate-limit proof false line 28; enforcement line 80 | Parallel production blocked |

### 2.3 Link collection frozen map / Link采集冻结地图

| Layer | Relative source | Relative test | Source SHA-256 | Test SHA-256 |
|---|---|---|---|---|
| R1 | <code>backend\app\models.py</code> | <code>backend\tests\test_link_collection_models.py</code> | <code>482614EBE3E5307D5B677970258A9209116587FA236F3564A2D6D381C9320ADC</code> | <code>2BCAD2532D08E170CCE8F6EA1F478D4AF8ED40FDD4D6FCCB8F7E56EC736A11E5</code> |
| R2 | <code>backend\app\services\link_collection.py</code> | <code>backend\tests\test_link_collection.py</code> | <code>12C37032D9033F7C383C6451BF50BA1210CDD45D7B075470EE8FC194D6DEE0C4</code> | <code>D1D5C9876C7DF3166F0CEAF30C96D43585A4BDE8136D01191E937CCC9A75536C</code> |
| R3/P2 | <code>backend\app\services\link_collection_service.py</code> | <code>backend\tests\test_link_collection_service.py</code> | <code>A057A4BDC4586A965BD43B8D12143D6194DCA02915DE766E1FC213E2586BD868</code> | <code>C276890FD153F7790D98BB24BF150C264FEB5F3509E14C8A6503A1A7D66E0C4B</code> |
| R4A | <code>backend\app\db.py</code> | <code>backend\tests\test_database.py</code> | <code>B99678FC2D78BB758BC5A13DE4712305831EE94747320A8EEEE27FF4CDFACA86</code> | <code>5E948DC2CFE724C9387C9BC1B0C58C5A5E7CD125F99A35D63BBB5E12295FD853</code> |
| R4B | <code>backend\app\services\link_collection_store.py</code> | <code>backend\tests\test_link_collection_store.py</code> | <code>0E27CBE1EC811C4D72A505100D5FC47E4CA4E1B4E708D6B179854A7E27FDE779</code> | <code>7357303A302CFD2C46CCAC00B55A86362794EA9D955CDC1BE09134E167B5DA29</code> |
| R4C API | <code>backend\app\main.py</code> | — | <code>7F1B5F71363ECB7909923D5D57497D285989A7D6FE627F55F97C8C131FCE6767</code> | — |
| R4C runtime repair | <code>backend\app\services\link_collection_runtime.py</code> | <code>backend\tests\test_link_collection_api_runtime.py</code> | <code>A50F85F52BE2B140B1AB575AA75F6EB89277C5D23CEB213EF2758DF9EA88EA7B</code> | <code>4B26D8B48DB4EF09ADA8726F06FA6D433E1AF0C0E23AA0B3BD6A0CD9581F3786</code> |

Key functions / 关键函数：

- <code>LinkCollectionRequest</code> — <code>backend\app\models.py:55</code>.
- URL validation — <code>backend\app\services\link_collection.py:89</code>.
- <code>_normalize_video_data()</code> — line 164.
- <code>LinkCollectionRunner</code> — line 203; <code>run()</code> — line 228.
- Link service <code>run()</code> — <code>backend\app\services\link_collection_service.py:514</code>.
- <code>_SerializedStore</code> — <code>backend\app\services\link_collection_runtime.py:233</code>; <code>close()</code> — line 521.

### 2.4 Frontend map / 前端地图

| Relative path from frontend subrepo / 前端子仓相对路径 | Purpose | State |
|---|---|---|
| <code>client\src\pages\DashboardPage\LocalCollectionPanel.tsx</code> | Standard collection choices; lines 237–240 expose four modes / 标准采集选择；237–240行提供四模式 | Implemented, unfrozen |
| <code>client\src\pages\DashboardPage\collection-workflow.css</code> | Collection workflow styling / 采集工作流样式 | 34,727 bytes; SHA <code>9808B2E6…15F3</code>; provenance conflict |
| <code>client\src\pages\DashboardPage\video-assets.css</code> | Video asset presentation / 视频资产呈现 | Modified, unfrozen |
| <code>client\src\components\Layout.tsx</code> | Navigation/layout / 导航与布局 | Modified, unfrozen |
| <code>shared\api.interface.ts</code> | Shared API shape / 共享API结构 | Modified |
| <code>package.json</code> | Node scripts and engines / Node脚本与版本要求 | Version 2.2.5 |

The frontend subrepository is on <code>sprint/default</code>, HEAD <code>c88a1e7341f271373c1c5523c002ab5562989fd6</code>, ahead of upstream by 1. At the final inventory it had 21 modified and 13 untracked paths; preserve them and do not reset.

前端子仓库位于 <code>sprint/default</code>，HEAD 为 <code>c88a1e7341f271373c1c5523c002ab5562989fd6</code>，领先上游 1 个提交。最终清点时有 21 个修改路径与 13 个未跟踪路径；必须保留，禁止 reset。

### 2.5 Subtitle frozen map / 字幕冻结地图

| Relative source | SHA-256 | State |
|---|---|---|
| <code>MediaCrawler\media_platform\douyin\app_subtitles.py</code> | <code>3E54F91231EF96EE9CEA411C91F56DEB0E8E9E495E976815AED765241D9B7922</code> | Frozen/OFF |
| <code>MediaCrawler\media_platform\douyin\subtitles.py</code> | <code>A880FD5207F09DF91B8E8EB1EDE52C1CB95B1AEEA07A39EF8AD989AA85F030E4</code> | Frozen/OFF |
| <code>backend\app\services\douyin_subtitles.py</code> | <code>39F93649E4FD2164806C59EDD76D2EA6F735360F862602ED3CD0DD0048E514A8</code> | Frozen/OFF |

### 2.6 Detached Round-5 map / 第5轮外置地图

| Absolute path | Bytes | SHA-256 | Purpose |
|---|---:|---|---|
| <code>C:\Users\asus\r5h\round5-detached-v2.ps1</code> | 87,561 | <code>502DDAC80AA30E842308CB25E378CCF2620895DC1DCC49A6F12941C037B9B3E6</code> | Runner |
| <code>C:\Users\asus\r5h\contracts\round5.json</code> | 12,383 | <code>BDAA2BF874725DE0F2C448C15F406043C092383CA4FDDEA06E6CEBCF3261BCE4</code> | Contract |
| <code>C:\Users\asus\r5h\contracts\failed-64.json</code> | 5,645 | <code>239A141384A9C20673078947F67B61EF3E99B198E69A734A97CF751BECA9648E</code> | Exact failed-64 list |
| <code>C:\Users\asus\r5h\guards\sitecustomize.py</code> | 30,567 | <code>5E45DFE8281A7FE37412075BB657489B7588DF78C7D2AA10EDB826D76D5D71E4</code> | Python guard |
| <code>C:\Users\asus\r5h\guards\network-guard.cjs</code> | 56,236 | <code>1EFD4F89C1B441BF947F5C28BA44A298AEF884EFB5ED9779B442AA7336A59CA4</code> | Node guard |

- Candidate / 候选：<code>AEF3B3E8103A0F3751122E6AFDCBE3FEC4216F123D9DBAF41E8FD1F9EA73BB52</code>.
- Source closure / 源码闭包：337 files; digest <code>B40BDE9A96BD35D89E6D067D60AA5D4CAB2303C5853BA0C426A6039267CFD301</code>.
- Backend-18 digest / 后端18文件摘要：<code>B006F4600F4D58C11F164610A2E0F18DF875F62C727C209DCA82BEE55F601599</code>.

Runner function anchors / Runner函数锚点：

- <code>Get-TextDigest</code> line 241; <code>Get-SelectedManifest</code> line 295.
- <code>Assert-ContractInputs</code> line 416; <code>Get-CandidateIdentity</code> line 470.
- <code>Get-SourceClosurePaths</code> line 591.
- <code>Invoke-SelfTest</code> line 1091; <code>Invoke-Collect64</code> line 1475.
- <code>Invoke-Preflight64</code> line 1508; <code>Invoke-Full</code> line 1521.
- Phase dispatch lines 1687–1692; summary lines 1790–1815; manifest/seal lines 1817–1833; seal-failure rewrite lines 1835–1840.

## 3. Completed Work / 3. 已完成工作

The table below is the full verified completed-work inventory available from the current conversation, prior handoffs, source bytes, database, and retained evidence. Each row gives the required four fields.

下表是依据当前对话、往期交接、源码字节、数据库与保留证据形成的已完成工作全量清单；每行均包含要求的四个字段。

| ID | What was done / 做了什么 | Output and purpose / 产出物与用途 | How to verify / 如何验证 | Key data/effect / 关键数据与效果 |
|---|---|---|---|---|
| C01 | Formal Windows-local platform layout and canonical launcher established. / 已建立正式Windows本地平台布局与标准启动脚本。 | <code>D:\全自动爬取短视频、推文爆款程序</code>; <code>start.ps1</code> launches backend/frontend/local components. / 正式根与启动入口。 | Parse <code>start.ps1</code> through PowerShell AST; expected 0 parser errors. / 用PowerShell AST解析，预期0错误。 | Local routes target ports 3000/3100/8000; ASR may use 8765. |
| C02 | Round-4 collection task reached a terminal completed state. / 第4轮采集任务到达完成终态。 | <code>data\radar.sqlite3</code>; task <code>12fa1f267316452e9c5b433d51b4c23b</code>. | Open DB in immutable read-only mode and query <code>collection_tasks</code>. / 以immutable只读模式查询任务表。 | Status completed, progress 100; created 2026-08-18T06:46:31Z, updated 2026-08-18T17:42:36Z. |
| C03 | Round-4 persisted creator/video/comment/transcription baseline. / 第4轮持久化达人、视频、评论与口播基线。 | <code>data\radar.sqlite3</code>; project’s current local evidence baseline. | Run the verified read-only count command in section 7. / 执行第7节只读计数命令。 | 135 videos; 2,376 comments; 135 transcriptions; 129 succeeded and 6 skipped; 8 creator profiles; 13 creator snapshots. |
| C04 | Nine selected creators completed 15 videos each; one creator was user-skipped truthfully. / 9位达人各完成15条；1位按用户决定如实跳过。 | <code>account_tasks</code> and related task records in SQLite. | Query task/account status read-only and confirm 9 done plus “毒舌电影” skipped. / 只读确认9个done及“毒舌电影”skipped。 | 9 × 15 = 135 videos; skipped stage says user skipped and was not counted as failure. |
| C05 | Standard collection’s four content modes are implemented in API model and UI. / 标准采集四种内容模式已在API模型与UI实现。 | <code>backend\app\models.py:142</code>; <code>LocalCollectionPanel.tsx:237-240</code>. | Inspect enum/validation and four UI buttons. / 检查枚举与四个按钮。 | <code>video_data</code>, <code>transcript</code>, <code>creator</code>, <code>all</code>; default transcript UI says 2. |
| C06 | Link R1–R4C/P2 was implemented and frozen at exact file identities. / Link R1–R4C/P2已实现并按精确文件身份冻结。 | Thirteen source/test identities in section 2.3; supports validation, resolver, deadline/cancel, exact-once coordination, persistence, API/runtime. | Recompute SHA-256 and compare all 13 identities. / 重算13项SHA-256并逐项比对。 | Prior bounded evidence: R1 backend 39/39 and frontend 9/9; R2+SocialKit 101/101; R3 68/68. No tests were rerun for this handoff. |
| C07 | Link product boundary was clarified and retained. / Link产品边界已澄清并保留。 | <code>_normalize_video_data()</code> at <code>link_collection.py:164</code>; Link request/API paths. | Inspect normalized fields and ensure Link path has no creator-profile expansion. / 检查标准化字段并确认Link无达人档案扩展。 | Multi-link tasks can carry video author metadata but must not crawl creator homepage/profile/history/comments. |
| C08 | The proven Link runtime close race was repaired. / 已修复被证实的Link运行时close竞态。 | <code>link_collection_runtime.py</code> with <code>_SerializedStore</code> at line 233 and <code>close()</code> at line 521; paired runtime tests. | Compare frozen hashes and inspect serialized locking/close path. / 比对冻结哈希并检查串行锁与关闭路径。 | Before the 2026-08-23 manual tests, this was the only Round-5 issue classified as a proven platform defect and it was fixed. The later comment-budget defect is separately open. External DB contention remains fail-fast by design. / 在2026-08-23手测前，这是唯一已证且已修的平台缺陷；后来暴露的评论预算缺陷仍独立开放。 |
| C09 | Subtitle Direct code-only validation was retained while the feature was frozen/OFF. / 字幕直取仅代码验证已保留，同时功能冻结/OFF。 | Three exact subtitle sources in section 2.5; startup defaults guard identity before enabling. | Compare three hashes; inspect <code>start.ps1:40-74</code> for default-off eligibility behavior. / 比对哈希并检查默认关闭逻辑。 | Prior evidence: 141/141 focused, 204/204 adjacent, 24/24 quality, 92 disjoint health/master, 2/2 logging. No production approval. |
| C10 | Subtitle team capacity was reassigned to Platform Optimization without reopening subtitle scope. / 字幕组产能已转入平台优化，未重开字幕范围。 | Binding ownership/freeze records in [[0821凌晨-开发日志]] and this note. | Check ownership map in section 10. / 查看第10节归属图。 | Subtitle source stays no-touch; Code Director remains independent. |
| C11 | Detached Round-5 harness, exact candidate identity, source closure, and phase order were established. / 已建立第5轮外置门禁、精确候选身份、源码闭包与阶段顺序。 | Five files under <code>C:\Users\asus\r5h</code>; retained runs under <code>C:\Users\asus\r5</code>. | Compare exact five hashes, candidate, closure count/digest, and contract phase dependency chain. / 比对五文件、候选、闭包与阶段依赖链。 | Current candidate AEF3; 337-file closure; strict order SelfTest→Collect64→Preflight64→Full. |
| C12 | Current AEF3 SelfTest completed with sealed evidence. / 当前AEF3 SelfTest已形成封印证据。 | <code>C:\Users\asus\r5\16e095fb6489\e</code>. | Verify nonempty <code>summary.json</code>, <code>evidence-manifest.tsv</code>, <code>seal.json</code> and hashes in section 9. / 核验非空摘要、清单、封印与哈希。 | Phase PASS; 21 payload manifest rows; source/dependency/Vite before-after equality; no sentinel delta; node_modules detached; no leak/timeout. |
| C13 | AEF3 Collect64 subprocess exactly enumerated the contractual 64 tests. / AEF3 Collect64子进程精确枚举契约64项。 | <code>C:\Users\asus\r5\91f4c16e80ad\e\collected-64.json</code>. | Hash file and inspect ordered unique node IDs plus collection output. / 核验哈希、顺序唯一节点与采集输出。 | 64/64 unique ordered; subprocess exit 0; “64 tests collected in 3.88s”; no test bodies ran. This sub-result is complete, but the phase is not complete because sealing failed. |
| C14 | Retained evidence and phase boundaries were preserved rather than rewritten. / 保留证据及阶段边界未被重写。 | All named directories in section 9; 24 expired permit files under <code>C:\Users\asus\r5h\permits</code>. | Read-only inventory and hashes; current-valid count is 0. / 只读清点与哈希；当前有效许可数0。 | No cleanup, in-place repair, backfill, or evidence deletion occurred during this handoff. |
| C15 | Independent review boundaries remain documented. / 独立审查边界持续记录。 | Actual agent definition: <code>F:\积昌的知识库 - 副本\.claude\agents\代码总监.md</code>; handoffs and permit files. | Confirm actual path and read binding verdicts; do not infer phase approval. / 确认真实路径并读取裁定；不得推定阶段批准。 | The path without <code>.md</code> is not a file. The Code Director is review-only and permanently independent. |
| C16 | The standard collection button was opened through an expiring, scope-enforced non-commercial authorization. / 标准采集按钮已通过会过期、代码强制范围的非商业授权开放。 | <code>docs\authorizations\mediacrawler-round5-manual-local-20260823.md</code>; provider/service/tests; <code>.env.local</code> path. | Verify document SHA <code>49B99810…08D67</code>; run the 15 bounded tests; read live health without POST. / 核验文档哈希、15项测试与在线健康状态，不发送POST。 | 15/15 passed, exit 0 after backend isolation; live <code>eligible=true</code>, <code>real_collection_ready=true</code>, scope local-manual, production/parallel/agent initiation false. The implementation worker created no task. |
| C17 | The first human-started Round-5 attempt was captured without rewriting its outcome. / 首个由用户启动的第5轮尝试已完整留证，未篡改结果。 | Task <code>cb8873ba4942472bab1063663634674b</code>; API/SQLite terminal row; two immutable crawler captures in section 9. | GET the task and logs; hash both captures; compare current DB counts to the preserved baseline. / GET任务与日志，核验两份不可变日志哈希，并对比数据库基线。 | User selected “华哥聊论文”, <code>video_data</code>, 7d, comments on; terminal <code>failed</code>; 15/15 candidates accepted internally, comment request 16/15 failed, DB remains 135/2,376/135, Link rows remain zero. |
| C18 | The second human-started Round-5 attempt completed all nine bounded routes and its full evidence set was preserved. / 第二个用户启动的第5轮尝试完成全部九次有界线路并保留完整证据。 | Task <code>f89d2b9a62744f3695bcaff3eeea338e</code>; terminal API/SQLite row; 18 immutable captures listed in section 9.3B. | GET the terminal task, verify nine route-history entries, then compare every reported capture size/SHA with disk. / GET终态任务，核验九条线路历史，并逐份比对日志大小与SHA。 | Firefox ×3 and Edge ×3 reproduced <code>comment:16/15</code> with argus=0; Chrome ×3 returned zero candidates/rows; task failed truthfully; all 18 capture hashes matched; active standard/Link counts ended at 0. |

## 4. Exact Current Progress / 4. 当前精确进度

### 4.1 Last valid operations / 最后有效操作

- **Last fully sealed current-candidate operation / 当前候选最后完整封印操作：** AEF3 SelfTest at <code>C:\Users\asus\r5\16e095fb6489\e</code>, PASS.
- **Last attempted offline phase / 最近一次离线阶段尝试：** AEF3 Collect64 at <code>C:\Users\asus\r5\91f4c16e80ad\e</code>. The test-list subprocess succeeded, but C-drive free space reached zero during sealing; <code>summary.json</code> is 0 bytes, no manifest/seal exists, and after-snapshots are incomplete. Therefore the phase verdict remains RED/unsealed.
- **First human-started operation / 首个用户启动操作：** task <code>cb8873ba4942472bab1063663634674b</code>, created at <code>2026-08-23 22:08:43.854973 +08:00</code> and terminal <code>failed</code> at <code>22:12:23.996808 +08:00</code>. It accepted 15/15 candidate videos inside MediaCrawler, exhausted the comment endpoint at request <code>16/15</code>, imported no new platform rows, and ended <code>risk_paused</code> because an earlier Argus event was also detected.
- **Newer terminal human operation / 更新的用户终态操作：** task <code>f89d2b9a62744f3695bcaff3eeea338e</code> for “计算机博士迪哥”, created <code>22:12:40.196946 +08:00</code>, terminal failed <code>22:33:02.387218 +08:00</code>. Attempts 1–6 reproduced <code>comment:16/15</code> (Firefox ×3, Edge ×3, all argus=0); attempts 7–9 on Chrome produced no valid works, and the platform correctly kept the overall task failed. Active task counts are now zero.
- **Last user decision / 用户最后决定：** do not retry Collect64 now. Every live retry remains user-owned; Agent must first fix the captured platform issue, then return control to the user.
- **Last implementation/documentation actions / 最后实现与文档动作：** add and independently review the exact expiring local-manual authorization, run 15 bounded tests, reload only the verified backend listener, verify health, then read the user task/log/database state and write this relay. No Collect64, Preflight64, Full, production, canary, live-DB mutation, cleanup, or Agent-issued collection POST was performed.

### 4.2 Current runtime snapshot / 当前运行快照

At the read-only snapshot on 2026-08-23 Beijing time:

| Port | Address | PID | Observed command ownership | Interpretation |
|---:|---|---:|---|---|
| 3000 | 127.0.0.1 | 34632 | Node/Vite under the frontend subrepo | Frontend listener present |
| 3100 | ::1 | 48360 | Node <code>dist\server\main</code> | Miaoda local server present |
| 8000 | 127.0.0.1 | 9820 | Python/Uvicorn <code>backend.app.main:app</code> | Reloaded backend; scoped authorization live |
| 8765 | 127.0.0.1 | 20420 | Python/Uvicorn <code>app:app</code> | ASR listener present |
| 18880 | — | — | No listener observed | Signer absent |
| 9222 | — | — | No listener observed | CDP absent |

<span style="color:#e67e22">Runtime state is volatile. Re-run the read-only ownership command before relying on these PIDs. A listener alone does not authorize collection. / 运行状态会变化。依赖这些PID前必须重跑只读归属命令；监听存在不代表采集获批。</span>

### 4.3 Current standard-collection gate / 当前标准采集门禁

The gate was resolved after the owner explicitly affirmed non-commercial learning/research use. The verified live authorization result is:

    {
      "eligible": true,
      "reason": "reviewed_written_authorization",
      "scope": "round5_manual_local",
      "document_sha256": "49B99810CD70A15D9E0F8B55F2DDF6056C05214113D5B635D3A1058DD7F08D67",
      "production_eligible": false,
      "parallel_accounts_allowed": false,
      "agent_initiation_allowed": false,
      "expires_utc": "2026-08-31T15:59:59Z"
    }

Current source chain:

1. <code>docs\authorizations\mediacrawler-round5-manual-local-20260823.md</code> — 9,512 bytes; exact authorization document.
2. <code>mediacrawler.py:50</code> — binds that digest to scope, issuance, expiry, and explicit false production/parallel/Agent flags.
3. <code>deployment_authorization_status():886</code> — retains exact-hash, regular-file, identity, size, reparse-point, scope-record, and expiry checks.
4. <code>collection.py:_require_collection_deployment_eligibility():125</code> — requires the local-manual scope and <code>strict_account_order=true</code>.
5. <code>CollectionService.start():569-574</code> and <code>resume():609-617</code> — apply the gate before creation/resume mutation.
6. <code>.env.local:22</code> — configures the exact document path.
7. <code>start.ps1</code> reloaded only the missing backend after active standard/Link task counts were verified as zero.

<span style="color:#2980b9">Verification / 核验：15 bounded offline tests passed with exit code 0 after isolating the backend; direct preflight returned ready=true; live health returned status=ok and real_collection_ready=true on 127.0.0.1:8000. The implementation worker sent no collection POST and created no task. Later, the browser UI sent <code>OPTIONS</code> followed by <code>POST /api/collections 202</code> when the user personally began task <code>cb887…</code>; its failure is documented separately and does not mean the gate stayed closed. / 隔离后端后，15项有界离线测试以退出码0通过；直接预检返回ready=true；127.0.0.1:8000在线健康状态返回status=ok及real_collection_ready=true。实现Agent未发送采集POST、未创建任务。其后用户本人通过浏览器UI发起任务时出现 <code>OPTIONS</code> 后接 <code>POST /api/collections 202</code>；该任务失败另行记录，并不表示权限仍被封锁。</span>

The earlier HTTP 422 screenshot is explained by the superseded empty-authorization state. Response bodies for the historical 422 log lines remain <span style="color:#e67e22">❓ not retained</span>; the current live health result supersedes that state.

先前截图中的 HTTP 422 来自已被替代的空授权状态。历史 422 日志的响应体仍 <span style="color:#e67e22">❓未保留</span>；当前在线健康状态已替代该状态。

### 4.4 Source and documentation mismatches / 源码与文档不一致

| Item | Current source truth | Stale/conflicting statement | Consequence |
|---|---|---|---|
| Accounts | 51 enabled: 13 internal, 38 benchmark; groups 32/4/7/5/3 | README says 12 internal accounts | New Codex must trust current config, not stale README |
| Transcript default | Effective/UI default is 2 | README says 10 | Manual expectations must use 2 unless user chooses custom/all |
| Account loader | Two <code>load_accounts()</code> functions at lines 37 and 54; second overwrites first | Callers may assume name cleanup from first implementation | Source-level correctness risk |
| Frontend CSS | SHA <code>9808B2E6…15F3</code> | Prior handoff cited a different <code>9E9E…</code> identity | Frontend is UNFROZEN |
| Tweet/X | No implementation found in inspected core | Project title includes tweets | Scope/acceptance unresolved |

### 4.5 Current release status / 当前放行状态

| Scope | Status | Reason |
|---|---|---|
| UI process availability / UI进程可用 | Listening, volatile / 正在监听、会变化 | Ports 3000/3100/8000/8765 observed |
| Standard manual collection / 标准手动采集 | <span style="color:#e74c3c">OPEN; TWO USER TESTS FAILED / 已开放；两次用户测试失败</span> | Both terminal; second reproduced budget failure six times and then zero-row Chrome results |
| Link code identity / Link代码身份 | Frozen / 冻结 | Exact R1–R4C/P2 hashes retained |
| Link local manual use / Link本地手测 | User-initiated local scope only / 仅用户发起的本地范围 | Video-only boundary remains binding; no creator profile expansion |
| Subtitle Direct | <span style="color:#e74c3c">OFF/FROZEN</span> | Legal/signing/identity/canary/rollback evidence incomplete |
| AEF3 SelfTest | PASS, sealed | Current-candidate evidence exists |
| AEF3 Collect64 | <span style="color:#e74c3c">RED/unsealed</span> | Seal failure despite 64/64 enumeration |
| AEF3 Preflight64 | Not passed | Dependency phase incomplete |
| AEF3 Full | Not passed | Preflight incomplete |
| User manual Round 5 | <span style="color:#e74c3c">TWO FAILED, RECORDED / 两次失败并留证</span> | <code>cb887…</code> and <code>f89d…</code> terminal; active standard/Link counts 0 |
| Production/live/multi-account | <span style="color:#e74c3c">NO-GO</span> | Separate gates incomplete; rate-limit proof false |

### 4.6 Remaining progress trajectory / 剩余进度轨迹

If Tweet/X is excluded from the current milestone, the planned **Douyin engineering estimate** progresses as follows: #1 80→84%, #2 84→85%, #3 85→88%, #4 88→91%, #5 91→94%, #6 94→96%, #7 96→97%, #8 97→100%. Item #9 determines whether a new Tweet/X denominator is required; no honest automatic 100% claim is possible if implementation is included.

若 Tweet/X 不属于本里程碑，计划中的**抖音工程估算**依次推进：#1 80→84%，#2 84→85%，#3 85→88%，#4 88→91%，#5 91→94%，#6 94→96%，#7 96→97%，#8 97→100%。接力项 #9 用于决定是否需要新增 Tweet/X 工作总量；若纳入实现，不能诚实地自动宣称100%。

## 5. Unfinished Relay Batons / 5. A 没做完的事（接力棒）

Every item below is unfinished. Its number is reused without change in sections 6 and 7.

以下每项均未完成；编号在第6、7节中保持一致。

### #1 Round-5 comment-budget and failure-precedence closure / 第5轮评论预算与失败优先级闭环

- **What is missing / 还差什么：** A bounded repair for the real task failure, plus a successful or explicitly user-accepted retry. The code currently permits a 15-video/comment request while the child has only 15 comment API calls; sparse or paginated comments can require more than one call per video. The final budget exception is then obscured by an earlier Argus signal in the account-facing error. / 缺少对真实任务失败的有界修复，以及一次成功或由用户明确接受的重试。当前代码允许15条视频并采评论，但子进程只有15次评论API额度；评论稀疏或分页时，一条视频可能消耗多次。最终预算异常又被更早的Argus信号遮蔽在账号对外错误中。
- **Why unfinished / 为什么没做完：** The defect was exposed only after the user opened Round 5. No repair or retry was authorized inside the handoff-writing turn, and the user reserved live input selection to themself. / 缺陷在用户开启第5轮后才暴露；交接撰写阶段未获授权直接修复或重试，且用户明确保留真实输入选择权。
- **Preconditions / 前置条件：** Preserve both tasks <code>cb887…</code> and <code>f89d…</code>, their DB rows, the first task’s 2 immutable captures, and the second task’s 18 immutable captures; verify active standard/Link counts are 0; do not modify the reviewed authorization document; define whether budget exhaustion must reject early, checkpoint partial video data, or stay within the bound; keep strict serial/local-manual scope. / 保留两次任务、数据库行、首任务2份与第二任务18份不可变日志；核验两类活动数为0；不得修改已审授权文档；先定义预算耗尽应提前拒绝、保留部分视频检查点，还是在额度内完成；继续严格串行与本地手测范围。
- **Priority / 优先级：** **Urgent / 紧急**.
- **Done definition / 做到什么算完成：** Regression tests cover sparse/paginated top-level comments across 15 accepted videos and prove no 16th call is attempted unless a compatible larger reviewed allowance exists; provider/account status preserves the primary budget reason alongside any Argus evidence; bounded tests pass; then the user personally starts a retry that reaches the intended terminal result with explainable DB deltas. / 回归测试覆盖15条候选上的稀疏/分页顶层评论，并证明在没有兼容且经过评审的更大额度时不会发起第16次请求；Provider/账号状态同时保留预算主因与Argus证据；有界测试通过；随后由用户本人发起重试并形成预期终态及可解释的数据增量。
- **Start point / 从哪开始：** <code>MediaCrawler\media_platform\douyin\client.py:_AttemptRequestBudget.reserve():91</code> and <code>get_aweme_all_comments():360</code>; <code>core.py:batch_get_note_comments()/get_comments():353-410</code>; fixed budget <code>backend\app\providers\mediacrawler.py:67,528</code>; terminal summarization <code>:1765-1804</code>; account decision <code>backend\app\services\multi_account\runner.py:291-303</code>; existing regression <code>MediaCrawler\tests\test_douyin_comment_budget.py:54</code>. / 从上述预算、评论分页、汇总、账号状态与测试入口开始。
- **Verification signal / 验证信号：** A focused test reproduces the old <code>comment:16/15</code> failure before the fix and passes afterward; no budget/safety gate is simply removed; GET of the next user task reports the designed terminal state; platform counts change only within the user-selected scope. / 聚焦测试先复现旧的 <code>comment:16/15</code>，修复后通过；不得直接移除预算/安全门禁；下一次用户任务GET返回设计终态；平台计数仅按用户范围变化。
- **Goal/progress anchor / 总目标与进度：** Serves A2 and A5; A5 input ownership is already proven, while A2 remains open. Completing the repair and accepted retry advances verified Douyin progress **80%→84%**. / 服务A2、A5；A5的输入归属已证明，A2仍开放。修复并完成可接受重试后估算 **80%→84%**。

### #2 User-owned Link video-only manual result / 用户本人Link仅视频手测结果

- **What is missing / 还差什么：** A live local manual proof that Link accepts the user-selected video links while producing no creator-profile/homepage expansion. / 缺少 Link 接收用户所选视频链接且不扩展达人档案/主页的本地手测证据。
- **Why unfinished / 为什么没做完：** R1–R4C/P2 code evidence exists, but no current user-owned live result is recorded. / 已有代码证据，但没有当前用户本人执行的真实结果。
- **Preconditions / 前置条件：** User chooses the links; Link frozen hashes still match; baseline counts for <code>creator_profiles</code> and <code>creator_profile_snapshots</code> are captured read-only before starting. / 用户本人选链接；冻结哈希一致；开始前只读记录达人表基线。
- **Priority / 优先级：** **Important / 重要**; if the user does not include Link in Round 5, keep A3 explicitly open. / 若用户本轮不测Link，A3必须继续开放。
- **Done definition / 做到什么算完成：** Link task reaches a truthful terminal state; requested videos are represented as expected; creator-profile/snapshot counts do not increase because of the Link task; no comments/homepage/history expansion occurs. / Link任务到达真实终态；视频结果符合输入；达人档案/快照表不因Link增加；无评论、主页或历史扩展。
- **Start point / 从哪开始：** Route <code>...#/links</code>; <code>LinkCollectionRequest</code> at <code>models.py:55</code>; <code>_normalize_video_data()</code> at <code>link_collection.py:164</code>; API at <code>main.py:930</code>. / 从链接页及上述函数开始。
- **Verification signal / 验证信号：** Link task/item tables gain only the expected video-scoped rows, while creator-profile tables retain the baseline counts. / Link任务/条目表仅增加预期视频维度行，达人表计数保持基线。
- **Goal/progress anchor / 总目标与进度：** Serves A3; estimated verified Douyin progress **84%→85%**. / 服务 A3；抖音工程估算 **84%→85%**。

### #3 Fresh Collect64 after the manual result / 手测结果后的全新Collect64

- **What is missing / 还差什么：** A fresh, sealed Collect64 PASS for candidate AEF3 or a newly reviewed successor identity. / 缺少AEF3或新复审后继候选的全新、封印Collect64 PASS。
- **Why unfinished / 为什么没做完：** The 64-test subprocess succeeded, but evidence sealing failed when C drive reached zero. The user explicitly postponed retry until after manual testing. / 64项枚举成功，但C盘归零导致封印失败；用户明确推迟重试。
- **Preconditions / 前置条件：** #1 has a successful or explicitly user-accepted terminal record; #2 is recorded if Link is in the user's test scope; independent Director reattests exact candidate/five files/337-file closure; fresh phase-specific permit; fresh C-drive free-space reading at least 2 GiB; new mirror path. / #1形成成功或用户明确接受的终态记录；若本轮含Link则完成#2；总监复核、新许可、C盘至少2GiB与全新镜像。
- **Priority / 优先级：** **Important / 重要**, strictly after manual result / 严格位于手测结果之后。
- **Done definition / 做到什么算完成：** New evidence root contains nonempty <code>summary.json</code>, <code>evidence-manifest.tsv</code>, and <code>seal.json</code>; phase verdict PASS; exact 64 ordered unique node IDs; source/sentinel integrity unchanged. / 新证据根有非空摘要、清单、封印，阶段PASS，64项顺序唯一且源码/哨兵不变。
- **Start point / 从哪开始：** Preserve <code>C:\Users\asus\r5\91f4c16e80ad</code>; runner <code>Invoke-Collect64:1475</code>; parameter contract <code>-Phase Collect64 -DirectorPermit</code>. / 保留旧失败目录，从runner入口开始。
- **Verification signal / 验证信号：** Exit 0 is insufficient by itself; all three evidence files and their internal candidate/closure/permit identities must validate. / 仅退出码0不够；三类证据及内部身份必须全部通过。
- **Goal/progress anchor / 总目标与进度：** Serves A4; estimated progress **85%→88%**. / 服务 A4；估算 **85%→88%**。

### #4 Fresh Preflight64 / 全新Preflight64

- **What is missing / 还差什么：** Current-candidate Preflight64 PASS. / 缺少当前候选Preflight64 PASS。
- **Why unfinished / 为什么没做完：** Contract requires sealed Collect64 first; prior runs were superseded or failed due harness/ACL conditions. / 契约要求先有封印Collect64；历史运行已被替代或因门禁/ACL失败。
- **Preconditions / 前置条件：** #3 sealed PASS; separate fresh Director permit tied to exact candidate and prior Collect64 artifact; no source/harness mutation. / #3封印PASS、独立新许可、无字节变化。
- **Priority / 优先级：** **Important / 重要**.
- **Done definition / 做到什么算完成：** All 64 contracted test bodies run under the detached guard and produce sealed PASS with no production mutation, network, dependency drift, process leak, or timeout. / 64项测试体在外置守卫下运行并形成封印PASS，无生产变动、联网、依赖漂移、进程泄漏或超时。
- **Start point / 从哪开始：** <code>Invoke-Preflight64:1508</code>; prior failures <code>e8cb9b668819</code> and <code>272d6d7bcbd8</code> are diagnostic evidence, not retry targets. / 从函数入口开始，旧目录只作诊断。
- **Verification signal / 验证信号：** Sealed phase PASS references the exact #3 summary; expected count is 64 executed tests, not collection-only enumeration. / 封印PASS引用#3摘要，并实际执行64项而非仅枚举。
- **Goal/progress anchor / 总目标与进度：** Serves A4; estimated progress **88%→91%**. / 服务 A4；估算 **88%→91%**。

### #5 Fresh Full gate / 全新Full门禁

- **What is missing / 还差什么：** Current-candidate Full PASS and independent post-evidence verdict. / 缺少当前候选Full PASS及独立证据后裁定。
- **Why unfinished / 为什么没做完：** Preflight64 is not complete and no Full permit exists. / Preflight64未完成，且无Full许可。
- **Preconditions / 前置条件：** #4 sealed PASS; separate Full permit; exact unchanged candidate; sufficient disk; Director-approved phase scope. / #4封印PASS、单独许可、候选不变、空间充足。
- **Priority / 优先级：** **Important / 重要**.
- **Done definition / 做到什么算完成：** Full phase produces a sealed PASS across the contract’s backend/frontend checks with immutable source/dependency/sentinel state and no leaks; independent Director records the verdict. / Full形成跨前后端的封印PASS，源码/依赖/哨兵不变且无泄漏，总监记录裁定。
- **Start point / 从哪开始：** <code>Invoke-Full:1521</code>; dispatch at 1687–1692; seal at 1817–1840. / 从Full函数、分发与封印入口开始。
- **Verification signal / 验证信号：** Fresh summary/manifest/seal validate and reference #4; no phase escalation is inferred from exit code alone. / 新摘要、清单、封印通过且引用#4；不得仅凭退出码推定。
- **Goal/progress anchor / 总目标与进度：** Serves A4; estimated progress **91%→94%**. / 服务 A4；估算 **91%→94%**。

### #6 Frontend provenance and unified freeze / 前端来源与统一冻结

- **What is missing / 还差什么：** A reviewed, unified frontend baseline covering navigation, collection workflow, video assets, responsive behavior, and provenance. / 缺少导航、采集工作流、视频资产、响应式与来源统一复审基线。
- **Why unfinished / 为什么没做完：** Frontend subrepo is dirty; collection CSS hash conflicts with the prior handoff; no global visual freeze exists. / 前端子仓有脏改动；CSS哈希与旧交接冲突；无整体视觉冻结。
- **Preconditions / 前置条件：** Preserve all 21 modified and 13 untracked paths; resolve authorship/provenance without reset; finish or explicitly exclude Round-5 manual observations. / 保留全部改动，不reset；解决来源；纳入或明确排除手测观察。
- **Priority / 优先级：** **Important / 重要**, but do not mix it into a running gate phase. / 不得混入运行中的门禁阶段。
- **Done definition / 做到什么算完成：** One reviewed source identity set, no unresolved conflicting hash, responsive/manual visual acceptance recorded, type-check/build/test evidence produced under an authorized isolated workflow. / 形成统一复审身份，无冲突哈希，记录响应式/手工视觉验收，并在获批隔离流程生成检查证据。
- **Start point / 从哪开始：** Frontend HEAD <code>c88a1e…9fd6</code>; <code>collection-workflow.css</code> SHA <code>9808B2E6…15F3</code>; <code>LocalCollectionPanel.tsx</code>. / 从当前HEAD与关键文件开始。
- **Verification signal / 验证信号：** Cleanly documented diff ownership and one frozen manifest; no user changes lost. / 改动归属与冻结清单清晰，用户改动零丢失。
- **Goal/progress anchor / 总目标与进度：** Serves A1/A2 presentation; estimated progress **94%→96%**. / 服务A1/A2呈现；估算 **94%→96%**。

### #7 Account-loader and documentation reconciliation / 账号加载与文档对账

- **What is missing / 还差什么：** Resolve duplicate <code>load_accounts()</code>; reconcile 51-vs-12 accounts and 2-vs-10 transcript defaults; decide whether README is historical or current. / 解决重复加载函数并对账账号数、默认口播数和README定位。
- **Why unfinished / 为什么没做完：** These issues were discovered during handoff verification and were not part of the authorization hotfix. / 交接核验时发现，不属于本次授权热修。
- **Preconditions / 前置条件：** Define intended name-cleaning behavior and account contract; preserve current 51-account config; write tests before deleting either implementation. / 定义名称清洗与账号契约，保留51账号配置，先测后删。
- **Priority / 优先级：** **Important / 重要**.
- **Done definition / 做到什么算完成：** Exactly one <code>load_accounts()</code> remains; name lookup tests pass; README/account/default statements match code or are explicitly labeled historical. / 仅保留一个加载函数，名称查找测试通过，文档与代码一致或明确标旧。
- **Start point / 从哪开始：** <code>accounts.py:37,54,66</code>; <code>accounts.json</code>; <code>models.py:183-188</code>; <code>README.md</code>. / 从函数、配置、默认值与README开始。
- **Verification signal / 验证信号：** Read-only config count remains 51 enabled; exact lookup behavior has regression tests; README no longer claims false defaults. / 51个启用账号保持，查找行为有回归测试，README无错误默认值。
- **Goal/progress anchor / 总目标与进度：** Serves A2 maintainability/truth; estimated progress **96%→97%**. / 服务A2可维护性与真实性；估算 **96%→97%**。

### #8 Production and simultaneous multi-account closure / 生产与多账号并发闭环

- **What is missing / 还差什么：** Separate commercial/vendor authorization if needed, verified per-request rate limiting, protected identity/ACL, credential governance, canary, rollback, monitoring, and incident criteria. / 缺少必要的商业/版权方授权、逐请求限流、身份/ACL、凭据治理、canary、回滚、监控与事故标准。
- **Why unfinished / 为什么没做完：** Current grant explicitly excludes production/commercial/SaaS; <code>PARALLEL_REQUEST_RATE_LIMIT_VERIFIED=False</code>. / 当前授权明确排除生产/商业/SaaS，且并发限流验证为False。
- **Preconditions / 前置条件：** All offline/manual milestones; written commercial permission or licensed replacement if use becomes commercial; formal production design review. / 全部门禁与手测完成；商业时需版权方授权或商业替代；正式生产评审。
- **Priority / 优先级：** **Important / 重要**, but not a shortcut for the current manual test. / 不得借当前手测绕过。
- **Done definition / 做到什么算完成：** Each gate has independent evidence; parallel mode is enabled only after verified request-level enforcement; authorized canary and rollback succeed; monitoring detects and explains failures. / 各门禁有独立证据；逐请求限流通过后才启用并行；canary与回滚成功；监控可检测解释失败。
- **Start point / 从哪开始：** <code>multi_account\runner.py:28,80</code>; <code>MediaCrawler\LICENSE</code>; <code>TECHNICAL_STACK_CONFIGURATION.md</code>; production design artifacts <span style="color:#e67e22">❓ absent</span>. / 从并发门禁、许可证与技术栈文档开始；生产设计资料缺失。
- **Verification signal / 验证信号：** Independent production release verdict explicitly says GO; local manual grant must never be reused as that verdict. / 独立生产裁定明确GO；不得复用本地手测授权。
- **Goal/progress anchor / 总目标与进度：** Serves A6; if Tweet/X is out of scope, estimated Douyin progress **97%→100%**. / 服务A6；若Tweet/X不在本期，估算 **97%→100%**。

### #9 Tweet/X scope decision and implementation contract / Tweet/X范围决定与实现契约

- **What is missing / 还差什么：** A written decision on whether Tweet/X is in this milestone; if included, source/API/auth/fields/rate/privacy/storage/UI/test contracts and implementation are absent. / 缺少是否纳入本期的书面决定；若纳入，数据源、认证、字段、限流、隐私、存储、UI、测试契约及实现均缺。
- **Why unfinished / 为什么没做完：** No matching implementation was found in inspected core files, while the project title alone is not an executable requirement. / 核心文件未发现实现，项目标题不能替代可执行需求。
- **Preconditions / 前置条件：** User writes an acceptance contract and chooses a lawful source/API; credentials must be user-owned and kept redacted. / 用户书面定义验收并选择合法数据源/API；凭据归用户且脱敏。
- **Priority / 优先级：** **General until scope decision / 定稿前一般**; becomes important if included. / 纳入后转重要。
- **Done definition / 做到什么算完成：** Either a signed scope exclusion for this milestone, or an implemented and tested Tweet/X workflow meeting its written contract. / 本期正式排除，或按书面契约完成实现与测试。
- **Start point / 从哪开始：** Read project title/README and run the verified source search in section 7; do not infer an API. / 从标题、README与第7节源码搜索开始，不得自行猜API。
- **Verification signal / 验证信号：** One authoritative scope decision; if included, observable task/data/UI/test evidence exists. / 形成唯一权威范围决定；若纳入，存在任务、数据、UI与测试证据。
- **Goal/progress anchor / 总目标与进度：** Serves A7. If excluded, the verified Douyin denominator remains valid; if included, recompute total progress before coding. / 服务A7；排除则沿用抖音总量，纳入则编码前重算。

## 6. A-to-B Relay Overview / 6. A→B 接力总览

Completing #1–#8 advances the verified Douyin estimate from 80% toward 100% in the sequence shown in section 5. Item #9 determines whether the overall project needs a larger Tweet/X denominator.

完成 #1–#8 会按第5节顺序把已核验抖音工程估算从80%推进到100%；#9 决定总项目是否需要新增Tweet/X工作总量。

| # | A unfinished baton / A没做完的接力棒 | What B must do / 接手方要做什么 | Exact start point / 精确入口 | Observable completion / 可观察完成信号 |
|---:|---|---|---|---|
| 1 | First task failed at <code>comment:16/15</code> with earlier argus=2; second task reproduced it six times with argus=0, then Chrome ×3 returned zero rows / 首任务在更早argus=2下出现评论16/15；第二任务无Argus复现六次，Chrome三次零数据 | Preserve all 20 captures and both task rows; add failing regression; implement one bounded behavior without weakening zero-row truth; obtain review; return retry to user / 保留20份日志及两次任务，补失败回归，实现有界行为且不削弱零数据判失败，复审后交还用户重试 | <code>client.py:91,360</code>; <code>core.py:353-410</code>; <code>mediacrawler.py:67,528,1765-1804</code>; <code>runner.py:291-303</code>; focused commands below | Six no-Argus budget reproductions covered; safety budget and zero-row failure invariant retained; user retry reaches designed terminal state with explainable delta |
| 2 | No current Link live boundary proof / 无当前Link真实边界证据 | User starts selected links; compare Link and creator-table deltas / 用户启动所选链接并比较表增量 | <code>...#/links</code>; <code>_normalize_video_data:164</code>; Link tables | Expected video rows; zero creator-profile side effects |
| 3 | Collect64 unsealed and retry deferred / Collect64未封印且推迟 | After manual record, obtain fresh Director permit and run one fresh Collect64 / 手测后取得新许可并运行一次新Collect64 | <code>Invoke-Collect64:1475</code>; hash/free-space command; exact phase template | New nonempty summary/manifest/seal; 64/64; PASS |
| 4 | Preflight64 absent / 缺Preflight64 | Obtain separate permit and execute after #3 / #3后另取许可执行 | <code>Invoke-Preflight64:1508</code> | 64 executed tests; sealed PASS referencing #3 |
| 5 | Full absent / 缺Full | Obtain separate permit and execute after #4 / #4后另取许可执行 | <code>Invoke-Full:1521</code>; seal lines 1817–1840 | Sealed PASS + independent Director verdict |
| 6 | Frontend provenance/freeze unresolved / 前端来源与冻结未解 | Preserve dirty work, reconcile provenance, create reviewed freeze manifest / 保留改动、对账来源、形成冻结清单 | Frontend Git status; CSS SHA <code>9808…15F3</code> | One reviewed baseline; visual/responsive acceptance; zero lost changes |
| 7 | Duplicate account loader and stale docs / 重复加载函数与旧文档 | Test intended behavior, consolidate loader, reconcile README / 测试后合并并对账README | <code>accounts.py:37,54,66</code>; config count command | One loader; tests pass; 51/2 truths documented |
| 8 | Production gates incomplete / 生产门禁未闭环 | Run a separate licensed production-readiness program / 独立推进有许可的生产准备 | <code>runner.py:28,80</code>; license and design artifacts | Explicit independent production GO; rate/canary/rollback/monitoring evidence |
| 9 | Tweet/X scope absent / Tweet/X范围缺失 | Exclude formally or define lawful written contract, then implement/test / 正式排除或定契约后实现测试 | Source-search command; user acceptance contract | Authoritative decision; evidence if included |

**Relay first action / 接力开工第一步：** GET task <code>f89d2b9a62744f3695bcaff3eeea338e</code>, confirm its <code>failed</code> terminal state and 9-attempt history, then compare its 18 hash-verified captures with the frozen <code>cb887…</code> stderr. Seeing six independent <code>comment:16/15</code> reproductions with argus=0, while active counts remain zero, means the new Codex has formally reattached to the real blocker. / GET任务 <code>f89d…</code>，确认失败终态与9次尝试，再把18份已核验日志与 <code>cb887…</code> stderr对比；看到6次无Argus的 <code>comment:16/15</code> 且活动数保持0，即正式接上真实阻断点。

## 7. Command-Level Action Plan / 7. 下一步行动计划（命令级）

> [!important] Command truth / 命令真实性
> **EN:** Every read-only diagnostic command shown as “verified” below was executed successfully on 2026-08-23. The canonical <code>start.ps1</code> reload was also executed successfully. The Collect64/Preflight64/Full commands are explicitly marked controlled future templates and were not run because the user postponed Collect64 and later phases lack permits.
>
> **中文：** 下方标记“已核验”的只读命令均于2026-08-23实际成功执行；标准 <code>start.ps1</code> 重载也已成功执行。Collect64/Preflight64/Full 命令明确标为受控未来模板，因用户推迟Collect64且后续阶段无许可，本文未执行。

### 7.1 Immediate: task #1 / 立即执行：任务#1

1. **Protect and reattach to the newer user task / 保护并接上更新的用户任务（verified / 已核验）**

       $taskTask = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/collections/f89d2b9a62744f3695bcaff3eeea338e' -TimeoutSec 15
       [pscustomobject]@{
         Id = $taskTask.id
         Status = $taskTask.status
         Stage = $taskTask.stage
         Error = $taskTask.error
         ProcessState = $taskTask.account_progress[0].process_state
       }

   Correct signal / 正确信号：<code>Status=failed</code>, stage “采集失败：全部账号均未完成”, nine route attempts retained, final account error says no valid work was imported. Then GET <code>cb8873ba4942472bab1063663634674b</code> to retain the first task’s <code>failed/risk_paused/argus=2</code> comparison. If the backend is offline, read both IDs from SQLite in step 3; do not restart solely to obtain GET. / 应看到失败终态、九次尝试与“未导入任何有效作品”；再GET首个任务对比；后端离线时只读SQLite。

2. **Verify retained primary evidence / 核验保留的主因证据（verified / 已核验）**

       $stderrTask = 'D:\全自动爬取短视频、推文爆款程序\runtime\logs\immutable-captures\mediacrawler\2026-08-23\mediacrawler-20260823T140847126921Z-5d9330e208804620b3cd8f9ed09f66bc.stderr.log'
       (Get-FileHash -LiteralPath $stderrTask -Algorithm SHA256).Hash
       rg -n 'request_budget_exceeded:comment:16/15|Blocked by ArgusSecurityPlugin|accepted target reached: 15/15' -- $stderrTask

   Correct signal / 正确信号：SHA-256 is <code>F7D5EDC95E7AD30914EB7D01D9A67B3EB0CC71C450BCF0AF97D9D95BEECDFC4F</code>; all three events are present. Do not edit or “repair” this log. / 三类事件均存在；不得编辑或“修复”日志。

3. **Read database delta and active-task truth / 读取数据库增量与活动任务真值（verified / 已核验）**

       $projectTask = 'D:\全自动爬取短视频、推文爆款程序'
       $pythonTask = Join-Path $projectTask '.venv\Scripts\python.exe'
       $env:HANDOFF_DB_PATH = Join-Path $projectTask 'data\radar.sqlite3'
       & $pythonTask -c 'import json,os,sqlite3; u="file:"+os.environ["HANDOFF_DB_PATH"].replace(chr(92),"/")+"?mode=ro"; c=sqlite3.connect(u,uri=True); q={"videos":c.execute("select count(*) from videos").fetchone()[0],"comments":c.execute("select count(*) from video_comments").fetchone()[0],"transcriptions":c.execute("select count(*) from video_transcriptions").fetchone()[0],"active_standard":c.execute("select count(*) from collection_tasks where status in (''pending'',''running'',''paused'')").fetchone()[0],"active_link":c.execute("select count(*) from link_collection_task_state where status_code in (''pending'',''running'',''paused'')").fetchone()[0]}; print(json.dumps(q,sort_keys=True)); c.close()'

   Final signal / 最终信号：<code>videos=135</code>, <code>comments=2376</code>, <code>transcriptions=135</code>, <code>active_standard=0</code>, <code>active_link=0</code>. Use <code>mode=ro</code>, not <code>immutable=1</code>, because current truth may be in the WAL. / 必须使用 <code>mode=ro</code> 读取WAL真值。

4. **Write a failing regression before changing behavior / 修改行为前先补失败回归**
   - Extend <code>MediaCrawler\tests\test_douyin_comment_budget.py</code> with sparse/paginated top-level comment responses across 15 videos. The current test at line 54 assumes every first page yields all 20 comments and therefore misses the live path.
   - Add provider/runner coverage showing that a final <code>RequestBudgetExceeded</code> remains observable even when an earlier recoverable Argus event exists.
   - Correct pre-fix signal: the new test reproduces the 16th-call failure or the misleading primary status. / 修复前正确信号：新测试能复现第16次调用或主因被遮蔽。

5. **Implement one reviewed bounded contract / 实现一种经评审的有界契约**
   - Acceptable design families: allocate comment calls from the requested workload with a proven upper bound; stop comment pagination gracefully and checkpoint completed video data when the allowance ends; or reject an incompatible request before task creation.
   - Forbidden shortcut: deleting the budget, making it unlimited, hiding <code>RequestBudgetExceeded</code>, or treating all Argus text as harmless. / 禁止删除/无限提高预算、隐藏预算异常或把所有Argus文本当作无害。
   - After each project-code edit, invoke <code>/simplify</code> if available. It was unavailable in this session; the fallback used here was AST/diff review plus the permanently independent Code Director. / 每次项目代码修改后若可用必须调用 <code>/simplify</code>；本会话不可用，替代方案为AST/diff审查与永久独立代码总监。

6. **Run bounded regression and independent review / 运行有界回归并独立复审**
   - Run only the changed comment-budget/provider/runner tests first; preserve an explicit transcript. The expected count must be taken from collection output, not invented in advance.
   - Ask the independent Code Director to compare the fix against A2, confirm no Link/Subtitle/production/harness drift, and remain separate from implementation.

7. **Return live control to the user / 把真实控制权交还用户**
   - Verify health and zero active tasks. Tell the user the fix is ready.
   - The user—not Codex—selects the retry inputs and presses Start.
   - Record exact task/request/timestamps/status/DB deltas. Only a successful or explicitly accepted terminal result completes #1 and allows #3 consideration. / 仅成功或用户明确接受的终态才完成#1并允许考虑#3。

### 7.2 Immediate only if the user includes Link: task #2 / 仅用户本轮包含Link时立即执行：任务#2

1. Record immutable baseline counts for <code>creator_profiles</code>, <code>creator_profile_snapshots</code>, and Link tables using the section 9 snapshot command.
2. User opens <code>...#/links</code>, supplies chosen video links, and presses Start.
3. Record terminal Link state and compare counts.
4. Correct signal: expected video-scoped Link rows; no creator-profile/snapshot delta caused by Link.
5. If the user does not test Link, write “A3 remains open” rather than claiming PASS.

### 7.3 After the user’s manual result: task #3 / 用户手测结果后：任务#3

1. **Recheck exact candidate and disk / 复核候选与磁盘（verified read-only form / 已核验只读形式）**

       $gateFilesTask = @(
         'C:\Users\asus\r5h\round5-detached-v2.ps1',
         'C:\Users\asus\r5h\contracts\round5.json',
         'C:\Users\asus\r5h\contracts\failed-64.json',
         'C:\Users\asus\r5h\guards\sitecustomize.py',
         'C:\Users\asus\r5h\guards\network-guard.cjs'
       )
       $gateFilesTask | ForEach-Object {
         $itemTask = Get-Item -LiteralPath $_
         [pscustomobject]@{ Path = $_; Bytes = $itemTask.Length; SHA256 = (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash }
       }
       [math]::Round((Get-PSDrive -Name C).Free / 1GB, 3)

2. Independent Code Director reattests the five hashes, candidate, 337-file closure, manual record, and free space; then creates a fresh Collect64-only permit.
3. **Controlled future template—do not run without that permit / 受控未来模板——无许可禁止运行**

       & 'C:\Users\asus\r5h\round5-detached-v2.ps1' -Phase Collect64 -DirectorPermit '<fresh-absolute-permit-path>'

4. Validate new summary/manifest/seal; never repair <code>91f4c16e80ad</code> in place.

### 7.4 After #3: task #4 / #3之后：任务#4

1. Director validates #3 seal and creates a Preflight64-only permit.
2. **Controlled future template / 受控未来模板**

       & 'C:\Users\asus\r5h\round5-detached-v2.ps1' -Phase Preflight64 -DirectorPermit '<fresh-absolute-permit-path>'

3. Correct signal: sealed PASS with 64 executed tests; no production sentinel delta.

### 7.5 After #4: task #5 / #4之后：任务#5

1. Director validates #4 and creates a Full-only permit.
2. **Controlled future template / 受控未来模板**

       & 'C:\Users\asus\r5h\round5-detached-v2.ps1' -Phase Full -DirectorPermit '<fresh-absolute-permit-path>'

3. Correct signal: sealed Full PASS plus independent Director evidence verdict.

### 7.6 After gate work is stable: task #6 / 门禁稳定后：任务#6

1. **Preserve and inventory frontend / 保留并清点前端（verified / 已核验）**

       $frontendTask = 'D:\全自动爬取短视频、推文爆款程序\deployments\miaoda-matrix-radar'
       git -C $frontendTask status --short
       git -C $frontendTask branch --show-current
       git -C $frontendTask rev-parse HEAD
       Get-FileHash -LiteralPath (Join-Path $frontendTask 'client\src\pages\DashboardPage\collection-workflow.css') -Algorithm SHA256

2. Attribute every dirty/untracked path; do not reset or clean.
3. Run visual/responsive and toolchain checks only under a separately authorized isolated workflow.
4. Produce one frontend freeze manifest and reviewer verdict.

### 7.7 Task #7 / 任务#7

1. **Locate conflict / 定位冲突（verified / 已核验）**

       rg -n 'def load_accounts|def account_by_name' 'D:\全自动爬取短视频、推文爆款程序\backend\app\accounts.py'
       rg -n 'return 2|默认 2 条|12 个|10 条' 'D:\全自动爬取短视频、推文爆款程序\backend' 'D:\全自动爬取短视频、推文爆款程序\README.md'

2. Add tests for normalization/lookup intent.
3. Consolidate to one implementation; run the focused suite; update README to current truth.
4. Correct signal: one definition, 51 enabled accounts retained, default 2 documented.

### 7.8 Task #8 / 任务#8

1. Confirm <code>PARALLEL_REQUEST_RATE_LIMIT_VERIFIED=False</code> remains fail-closed.
2. Obtain separate commercial/vendor authorization if use changes from the owner-affirmed non-commercial scope.
3. Write production rate, ACL/identity, credential, canary, rollback, monitoring, and incident contracts.
4. Execute only after independent authorization; local-manual health is not evidence for this task.

### 7.9 Task #9 / 任务#9

1. **Verify current absence / 核验当前缺失（verified / 已核验）**

       rg -n -i 'twitter|tweet|x\.com|推文' 'D:\全自动爬取短视频、推文爆款程序\backend' 'D:\全自动爬取短视频、推文爆款程序\deployments\miaoda-matrix-radar\client' 'D:\全自动爬取短视频、推文爆款程序\README.md'

2. User decides “excluded from current milestone” or supplies a written lawful source/API and acceptance contract.
3. If included, re-estimate the denominator before implementation; keep credentials <code>&lt;redacted&gt;</code>.

## 8. Environment and Configuration / 8. 环境与配置依赖

### 8.1 Verified runtime versions / 已核验运行版本

| Component | Version/state | Requirement/meaning |
|---|---|---|
| Windows PowerShell / PowerShell | 7.6.4 | Commands in this handoff use PowerShell syntax |
| Backend Python | 3.12.4 | <code>D:\...\ .venv\Scripts\python.exe</code>; exact path has no space between ellipsis in reality |
| Node.js | v24.15.0 | Frontend requires Node ≥22 |
| npm | 11.12.1 | Frontend requires npm ≥10 |
| Frontend package | 2.2.5 | Scripts include dev server/client, build, test, typecheck, stylelint |
| Frontend Git | branch <code>sprint/default</code>; HEAD <code>c88a1e…9fd6</code> | Ahead 1; dirty; preserve |

### 8.2 Backend pinned dependencies / 后端固定依赖

FastAPI 0.116.1; uvicorn 0.35.0; pydantic 2.11.7; python-dotenv 1.1.1; httpx 0.28.1; aiolimiter 1.2.1; tenacity 9.1.4; SQLAlchemy 2.0.52; sqlmodel 0.0.39; openpyxl 3.1.5; psutil 7.0.0.

### 8.3 Port contract / 端口契约

| Port | Service | Binding requirement | Final observed state |
|---:|---|---|---|
| 3000 | Vite frontend | loopback/local | 127.0.0.1, PID 34632 |
| 3100 | Miaoda server | loopback/local | ::1, PID 48360 |
| 8000 | FastAPI backend | **127.0.0.1 only** | 127.0.0.1, PID 9820 |
| 8765 | Local ASR | 127.0.0.1 | PID 20420 |
| 18880 | Subtitle signer | must remain absent while Subtitle Direct OFF | no listener |
| 9222 | CDP | engine-dependent; absent in current Firefox mode | no listener |

### 8.4 Authorization configuration / 授权配置

| Item | Exact value/state |
|---|---|
| Authorization document | <code>D:\全自动爬取短视频、推文爆款程序\docs\authorizations\mediacrawler-round5-manual-local-20260823.md</code> |
| Document bytes/SHA | 9,512 / <code>49B99810CD70A15D9E0F8B55F2DDF6056C05214113D5B635D3A1058DD7F08D67</code> |
| Authorization ID | <code>MC-R5-MANUAL-LOCAL-20260823-01</code> |
| Scope | <code>round5_manual_local</code> |
| Expiry | <code>2026-08-31T15:59:59Z</code> / Beijing <code>2026-08-31T23:59:59+08:00</code> |
| Production/parallel/Agent initiation | false / false / false |
| Config location | <code>.env.local:22</code>; value is the document path |
| Provider binding | <code>backend\app\providers\mediacrawler.py:50</code> |
| License | <code>MediaCrawler\LICENSE</code>, Non-Commercial Learning License 1.1, SHA <code>AEFF21DE…2A33</code> |

### 8.5 Secret-bearing configuration / 含密钥配置

<code>.env.local</code> exists and must never be copied into documentation with values. Relevant key classes include browser paths/engine, Miaoda API key, sync token, CAPTCHA/vendor keys, ASR URL/model/key, proxy flags, transcription settings, and subtitle signing/provenance fields. All values are <code>&lt;redacted&gt;</code>.

<code>.env.example</code> is the shareable key template. Do not place actual cookie, token, authorization header, API key, client secret, session, or browser-profile contents into a handoff.

### 8.6 External access and provider boundary / 外部访问与Provider边界

- Standard/Link manual collection may access public Douyin content only when the human user initiates it under the current local non-commercial grant.
- Human verification is required for platform challenges.
- Automated CAPTCHA solving, stealth changes, proxy pools, and large-scale crawling remain prohibited.
- <span style="color:#e67e22">❓ Current proxy/split-tunnel operational requirement was not evidenced as necessary for the local UI; do not invent one.</span>
- Social Media Toolkit is an adjacent public-metadata/media resolver, not proof of a Tweet/X implementation.

### 8.7 Configuration revocation / 配置撤销

When the user completes or cancels Round 5, or by the expiry time, remove the authorization path or reviewed digest, reload only the backend, and verify <code>eligible=false</code>. This is a state-changing operation and must be explicitly authorized at that time.

当用户完成或取消第5轮，或授权到期时，移除授权路径或已审摘要，仅重载后端并核验 <code>eligible=false</code>。该操作会改变状态，届时必须取得明确授权。

## 9. Data and State Snapshot / 9. 数据与状态快照

> [!warning] WAL and live-task rule / WAL与活动任务规则
> **EN:** The SQLite database uses WAL. For current truth, use URI <code>mode=ro</code>; <code>immutable=1</code> can omit committed state still represented through the WAL. Both known Round-5 tasks are terminal at the final snapshot, but counts and file sizes remain runtime state. Never checkpoint, vacuum, copy over, delete, or “clean” the database without an explicit scoped reason.
>
> **中文：** SQLite 使用 WAL。读取当前真值必须使用 URI <code>mode=ro</code>；<code>immutable=1</code> 可能忽略仍由 WAL 表示的已提交状态。最终快照时两次已知第5轮任务均已终态，但计数与文件大小仍属于运行状态。没有明确且有界的理由时，禁止checkpoint、vacuum、覆盖复制、删除或“清理”数据库。

### 9.1 Current local database / 当前本地数据库

Final snapshot / 最终快照：2026-08-23 22:33:02 Beijing time, after the second user task terminated naturally.

| Item / 项目 | Verified state / 已核验状态 | Meaning / 含义 |
|---|---:|---|
| <code>data\radar.sqlite3</code> | 11,862,016 bytes | Main database; preserve / 主库；保留 |
| <code>data\radar.sqlite3-wal</code> | 4,124,152 bytes | Current terminal state represented through WAL; preserve / WAL承载当前终态；保留 |
| <code>data\radar.sqlite3-shm</code> | 32,768 bytes | WAL shared memory; do not remove while live / WAL共享内存；在线时不得删除 |
| <code>videos</code> | 135 | Same as preserved Round-4 baseline / 与第4轮基线相同 |
| <code>video_comments</code> | 2,376 | Same as baseline / 与基线相同 |
| <code>video_transcriptions</code> | 135 | 129 succeeded, 6 skipped in the preserved baseline / 基线中129成功、6跳过 |
| <code>video_snapshots</code> | 135 | Preserved / 已保留 |
| <code>creator_profiles</code> | 8 | Standard-flow creator data exists / 标准流程达人数据存在 |
| <code>creator_profile_snapshots</code> | 13 | Preserved / 已保留 |
| <code>collection_tasks</code> | 3 | One Round-4 complete, two Round-5 failed / 一次第4轮完成、两次第5轮失败 |
| <code>account_tasks</code> | 12 | Includes both current Round-5 account records / 包含两次当前第5轮账号记录 |
| <code>collection_logs</code> | 26,861 | Final task-log count at 22:33:02; preserve / 22:33:02最终日志计数；保留 |
| Link task/item/stable rows | 0 / 0 / 0 | No Link live task/result yet / 尚无Link真实任务与结果 |

Read-only current-count command, executed successfully / 当前计数只读命令，已成功执行：

    $projectTask = 'D:\全自动爬取短视频、推文爆款程序'
    $pythonTask = Join-Path $projectTask '.venv\Scripts\python.exe'
    $env:HANDOFF_DB_PATH = Join-Path $projectTask 'data\radar.sqlite3'
    & $pythonTask -c 'import json,os,sqlite3; u="file:"+os.environ["HANDOFF_DB_PATH"].replace(chr(92),"/")+"?mode=ro"; c=sqlite3.connect(u,uri=True); names=["videos","video_comments","video_transcriptions","creator_profiles","creator_profile_snapshots","collection_tasks","account_tasks","collection_logs","link_collection_task_state","link_collection_items","link_collection_stable_videos"]; print(json.dumps({n:c.execute("select count(*) from "+n).fetchone()[0] for n in names},sort_keys=True)); c.close()'

Correct use / 正确用法：run again before development or testing and record the new values; never force them to match this snapshot. / 开发或测试前重跑并记录新值；禁止强行匹配旧快照。

### 9.2 Standard-task ledger / 标准任务台账

| Task | User selection / 用户选择 | State and evidence / 状态与证据 |
|---|---|---|
| <code>12fa1f267316452e9c5b433d51b4c23b</code> | Round-4 multi-creator baseline / 第4轮多达人基线 | <code>completed</code>, progress 100; nine creators × 15 videos; “毒舌电影” user-skipped; 135 videos, 2,376 comments, 135 transcriptions. |
| <code>cb8873ba4942472bab1063663634674b</code> | “华哥聊论文”; <code>video_data</code>; 7d; comments on; comment_limit 20; strict serial | Created 22:08:43.854973; failed 22:12:23.996808. Internally accepted 15/15 candidates; primary exception <code>comment:16/15</code>; earlier Argus caused <code>risk_paused</code>; platform imported zero new rows. |
| <code>f89d2b9a62744f3695bcaff3eeea338e</code> | “计算机博士迪哥”; <code>video_data</code>; 7d; comments on; comment_limit 20; strict serial | Created 22:12:40.196946; failed 22:33:02.387218. Firefox ×3 and Edge ×3 each reproduced <code>comment:16/15</code> with argus=0; Chrome ×3 exited successfully but returned 0 candidates/rows; 9/9 routes exhausted, no platform data delta. |

Accounts configuration truth / 账号配置真值：51 enabled accounts; 13 internal and 38 benchmark. Group counts are 对标32、华哥4、矩阵7、七哥5、鱼哥3. Preserve IDs and profile URLs; never paste login tokens or cookies into documentation.

账号配置真值：启用51个账号，其中内部13、对标38；分组为对标32、华哥4、矩阵7、七哥5、鱼哥3。保留ID与主页URL；严禁把登录令牌或Cookie写入文档。

### 9.3 Immutable evidence for task cb887… / 任务cb887…不可变证据

| Capture / 日志 | Bytes | SHA-256 | Interpretation / 解释 |
|---|---:|---|---|
| <code>D:\全自动爬取短视频、推文爆款程序\runtime\logs\immutable-captures\mediacrawler\2026-08-23\mediacrawler-20260823T140847109241Z-3fe34c4822924c399e0763760e35fe27.stdout.log</code> | 0 | <code>E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855</code> | Empty stdout is the retained truth, not missing evidence / 空stdout本身就是保留真值 |
| <code>D:\全自动爬取短视频、推文爆款程序\runtime\logs\immutable-captures\mediacrawler\2026-08-23\mediacrawler-20260823T140847126921Z-5d9330e208804620b3cd8f9ed09f66bc.stderr.log</code> | 46,532 | <code>F7D5EDC95E7AD30914EB7D01D9A67B3EB0CC71C450BCF0AF97D9D95BEECDFC4F</code> | Primary diagnostic capture / 主诊断证据 |

The stderr evidence proves / stderr证据证明：

1. one profile request, one list request, and 21 detail requests were reserved;
2. 15 candidates were accepted;
3. 15 comment calls were reserved, total 38/60;
4. the next call raised <code>request_budget_exceeded:comment:16/15:total=39/60</code>;
5. one earlier detail request logged <code>Blocked by ArgusSecurityPlugin Uifid Not Found</code>, and the summary counted two textual Argus occurrences;
6. no platform import delta was committed for the task.

对应中文：已使用1次profile、1次list、21次detail；接受15条候选；评论调用到15次、总调用38/60；下一次抛出 <code>comment:16/15</code>；更早的一次detail出现真实Argus拦截文本；最终该任务未向平台库导入增量。

The task log also records a cookie-export warning: the ytdlp cookie export path was not in a dedicated vault below or outside the shared browser-data directory. Other Firefox state was synchronized. This warning did not prevent discovery of 15 candidates, but it remains a separate configuration hardening item.

任务日志还记录了Cookie导出警告：ytdlp Cookie导出路径未位于共享浏览器数据目录下的专用保险库或该目录之外。其他Firefox状态已同步。该警告没有阻止发现15条候选，但仍是独立的配置加固项。

### 9.3B Immutable evidence for task f89d… / 任务f89d…不可变证据

Common directory / 公共目录：<code>D:\全自动爬取短视频、推文爆款程序\runtime\logs\immutable-captures\mediacrawler\2026-08-23</code>.

All 18 files were re-read from disk; every actual size/SHA matched the task log. / 已从磁盘重读全部18份文件；实际大小与SHA均和任务日志一致。

| Attempt / 尝试 | Route / 线路 | Stdout basename, bytes, SHA-256 | Stderr basename, bytes, SHA-256 | Result / 结果 |
|---:|---|---|---|---|
| 1 | Firefox | <code>mediacrawler-20260823T141243033877Z-0ba9a4c888444187967beba25f70cc71.stdout.log</code>; 0; <code>E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855</code> | <code>mediacrawler-20260823T141243043917Z-dbb3b7e30a504a6889e3a2f99494ac97.stderr.log</code>; 39,313; <code>F72B32F2185369DC0452ACF3934B528A91BE44D51F3ED7E788C09C6D26228A86</code> | 15 accepted; <code>comment:16/15</code>; argus=0 |
| 2 | Firefox | <code>mediacrawler-20260823T141514340127Z-fc0fe8218cb54a4f8ee1d45759a90a54.stdout.log</code>; 0; <code>E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855</code> | <code>mediacrawler-20260823T141514349008Z-df6f56ab1d98468793ae28e96ddd0dfb.stderr.log</code>; 38,055; <code>A30442406371C725C36C32D42807442C45607E918DCF1E0FC936848CE18B41FD</code> | Same primary failure / 同一主因 |
| 3 | Firefox | <code>mediacrawler-20260823T141739606373Z-5edceb663a214fd69e8fa66b94637d18.stdout.log</code>; 0; <code>E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855</code> | <code>mediacrawler-20260823T141739616541Z-47e4f234b7c0402eb20c9ed53d336b6c.stderr.log</code>; 38,972; <code>FC89F4064F39724EAE28CB5528EA3588AE2AA342533BB8FDF2FAFAFF30951DFF</code> | Same; route switched afterward / 同因；随后换线 |
| 4 | Edge | <code>mediacrawler-20260823T142027619189Z-4a69142f970440dc87278f5e2c9bec7e.stdout.log</code>; 45; <code>004E12C6AE31B97732D5890B2AB11DE69F79EF89A14085F4D66712C6151A72E9</code> | <code>mediacrawler-20260823T142027628491Z-4380be2ec1bb4b858e8110576c6d9a95.stderr.log</code>; 35,973; <code>A3572871966567CACBDBCA903BC2DB8A9EEEF914A6F9579075F5592D91AF5F12</code> | 15 accepted; <code>comment:16/15</code>; argus=0 |
| 5 | Edge | <code>mediacrawler-20260823T142437291936Z-cb101ba490cf467db00528513a620681.stdout.log</code>; 45; <code>004E12C6AE31B97732D5890B2AB11DE69F79EF89A14085F4D66712C6151A72E9</code> | <code>mediacrawler-20260823T142437304543Z-11f7feda8cde4d9c98741a3dd11eacbe.stderr.log</code>; 35,994; <code>1D019368E66B61C3937F46E47FE13026D605469C09D2A672A065F7FC1AED01B8</code> | Same primary failure / 同一主因 |
| 6 | Edge | <code>mediacrawler-20260823T142748266610Z-413a0c3402844b6db6046e30172384ea.stdout.log</code>; 45; <code>004E12C6AE31B97732D5890B2AB11DE69F79EF89A14085F4D66712C6151A72E9</code> | <code>mediacrawler-20260823T142748274766Z-fa6eeba331594a29a9c728f0a8048673.stderr.log</code>; 35,994; <code>A3A63DD3F64490FB3F86E843D870EE11E6E12AE62B3A91E5D53D8B2CD25245DD</code> | Same; route switched afterward / 同因；随后换线 |
| 7 | Chrome | <code>mediacrawler-20260823T143014395932Z-d61a93337ed648f1884cdaa787f92ba0.stdout.log</code>; 190; <code>40451532D75B873008191FD6A43AA7A74D9D080D5504E2FFE71DD6DC0756B4BB</code> | <code>mediacrawler-20260823T143014405450Z-76980ce8648041d6b7102a95f93925c5.stderr.log</code>; 4,102; <code>7FEB767FC45EDEE6C21ECD83901F1C600B9E58B3FC33123B0BA6FEBC9C5958B7</code> | Child outcome succeeded; 0 candidates/rows; platform rejected completion |
| 8 | Chrome | <code>mediacrawler-20260823T143122276276Z-08906de1bf2d4db1bcf434ec6f9186af.stdout.log</code>; 190; <code>40451532D75B873008191FD6A43AA7A74D9D080D5504E2FFE71DD6DC0756B4BB</code> | <code>mediacrawler-20260823T143122285257Z-ab3eb7d46a6045108518743a887380f5.stderr.log</code>; 4,102; <code>D27B392ADC81BDD8A73391524B54D05110FE50F1AB20A0D32F7AB1AAED90B835</code> | Same zero-result outcome / 同样零结果 |
| 9 | Chrome | <code>mediacrawler-20260823T143212249354Z-84d9a795ea1d4c4ab85e5c07739ba8b0.stdout.log</code>; 190; <code>40451532D75B873008191FD6A43AA7A74D9D080D5504E2FFE71DD6DC0756B4BB</code> | <code>mediacrawler-20260823T143212259727Z-f5f2849dda1e40729486f25011758bca.stderr.log</code>; 4,102; <code>4068647373B7E80B55B209F9C5AFDDA4E06DA57264A30033A6E1C622034D8137</code> | Same; 9/9 exhausted; task failed truthfully |

The “succeeded” capture outcome on Chrome means only that the child process exited without a provider exception. It does **not** mean task success. The platform correctly enforced the invariant that zero imported valid works cannot be marked complete.

Chrome日志中的“succeeded”仅表示子进程未抛Provider异常退出，并不代表任务成功。平台正确执行了“未导入有效作品不得标记完成”的不变量。

### 9.4 Scoped authorization and changed-file identities / 范围授权与改动文件身份

| File / 文件 | Bytes | SHA-256 | State / 状态 |
|---|---:|---|---|
| <code>docs\authorizations\mediacrawler-round5-manual-local-20260823.md</code> | 9,512 | <code>49B99810CD70A15D9E0F8B55F2DDF6056C05214113D5B635D3A1058DD7F08D67</code> | Reviewed immutable authorization bytes; do not edit / 已审授权字节；禁止修改 |
| <code>backend\app\providers\mediacrawler.py</code> | 104,829 | <code>8AABB8F6375C6C2FFCB70BB8D52577EEF1CAC663DC2FDDC77D9C6575C4A3CC90</code> | Scoped digest/expiry/preflight binding |
| <code>backend\app\services\collection.py</code> | 143,669 | <code>EE33BCA5642CFCB8B81E012EB9B8DEC9ABAF86BEF64E5D84B85E1AE0325F24DF</code> | Start/resume strict-serial scope enforcement |
| <code>.env.local</code> | 3,719 | <code>F9B88513A34172EF45D0AE5299AB4A087A9DC9E9EDAB667C66A7BC4B0247093C</code> | Secret-bearing; hash may be recorded, values remain redacted / 含密钥；仅记录哈希，值继续脱敏 |
| <code>backend\tests\test_mediacrawler_licensing.py</code> | 8,940 | <code>EA2D73E289D2D27C1AED6D0E7F445529F6243F92378590C1D45FB2B39D85AFE8</code> | Scope/tamper/expiry/metadata tests |
| <code>backend\tests\test_collection.py</code> | 85,216 | <code>02BCD3B37BF829AB9B0A40F689DB84972D55D9F3B8A45E8CE04BB33F19DE6E5D</code> | Start/resume/parallel rejection/serial reachability tests |

The independent Code Director issued **GREEN only for this scoped authorization change**. It did not grant production, Collect64, Preflight64, Full, Link expansion, Subtitle Direct, or automatic retries.

独立代码总监仅对本次范围授权变更给出 **GREEN**；它没有批准生产、Collect64、Preflight64、Full、Link扩展、字幕直取或自动重试。

### 9.5 Frozen Link, Subtitle, and frontend state / Link、字幕与前端状态

- **Link / Link：** the authoritative exact R1–R4C/P2/runtime source and paired-test hashes are in section [[#2.3 Link collection frozen map / Link采集冻结地图]]. All were rechecked unchanged during authorization review. Link remains video-only; standard collection retains creator-data capability.
- **Subtitle Direct / 字幕直取：** exact three hashes are in [[#2.5 Subtitle frozen map / 字幕冻结地图]]. Live health reported disabled, boot admission false, and runtime master false. Former Subtitle team capacity belongs to Platform Optimization, but subtitle files remain no-touch.
- **Frontend / 前端：** subrepo <code>sprint/default</code>, HEAD <code>c88a1e7341f271373c1c5523c002ab5562989fd6</code>, ahead 1, with 21 modified and 13 untracked paths. <code>collection-workflow.css</code> is 34,727 bytes, SHA <code>9808B2E6…15F3</code>. It conflicts with prior provenance and is <span style="color:#e67e22">UNFROZEN / 未冻结</span>. Never reset or discard user changes.

### 9.6 Current Round-5 candidate and sealed evidence / 当前第5轮候选与封印证据

- Candidate / 候选：<code>AEF3B3E8103A0F3751122E6AFDCBE3FEC4216F123D9DBAF41E8FD1F9EA73BB52</code>.
- Five-file harness identity / 五文件门禁身份：listed exactly in [[#2.6 Detached Round-5 map / 第5轮外置地图]].
- Source closure / 源码闭包：337 files, <code>B40BDE9A96BD35D89E6D067D60AA5D4CAB2303C5853BA0C426A6039267CFD301</code>.
- Backend-18 digest / 后端18文件摘要：<code>B006F4600F4D58C11F164610A2E0F18DF875F62C727C209DCA82BEE55F601599</code>.
- Permit inventory / 许可清单：24 files under <code>C:\Users\asus\r5h\permits</code>; current-valid count 0. A historical permit never authorizes a new phase.

| Artifact / 工件 | Bytes | SHA-256 | Verdict / 裁定 |
|---|---:|---|---|
| <code>C:\Users\asus\r5\16e095fb6489\e\summary.json</code> | 1,215 | <code>018DE14621A1DC73C4DACA0BDB2CA2CBB5E7F8C11B05B4457B549E5DEDC989A8</code> | AEF3 SelfTest phase PASS |
| <code>...\evidence-manifest.tsv</code> | 2,002 | <code>6DF4A265CE84F1B53039D949A1C5F19FBB8BDE8114C9BEB553CC92C2D1839B20</code> | 21 payload rows |
| <code>...\seal.json</code> | 519 | <code>3DBE5624E75CADDB84AE74F6E91366DD6002745DBC5CF5E592E56479F9231784</code> | Seal present |
| <code>C:\Users\asus\r5\91f4c16e80ad\e\collected-64.json</code> | 7,349 | <code>551C4E7C88FC63CB5CB10161F83D4D1CBBFB471A2259DBC4FC35807B33979650</code> | 64/64 ordered unique enumeration; subprocess exit 0 |
| <code>...\summary.json</code> | 0 | <code>E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855</code> | Collect64 phase RED/unsealed; no manifest/seal |

The SelfTest artifact’s own director field remains <code>RED_PENDING_DIRECTOR</code>; a standalone immutable post-artifact Director verdict file was not found. Thread-level reviews treat the sealed SelfTest evidence as valid, but that does not create a permit for Collect64.

SelfTest工件内部的总监字段仍为 <code>RED_PENDING_DIRECTOR</code>；未发现独立、不可变的证据后总监裁定文件。对话级复审认可封印证据有效，但这不会自动生成Collect64许可。

### 9.7 Chronological detached-harness attempts / 外置门禁尝试时间序列

| Evidence root / 证据根 | Candidate prefix / 候选前缀 | Outcome / 结果 | Classification / 归类 |
|---|---|---|---|
| <code>bd2902a39655</code> | F7E991 | SelfTest denied probe | Harness-only / 仅门禁 |
| <code>7e831062c1d5</code> | 8FC1 | executable none | Harness-only |
| <code>1c922a2bb656</code> | 8433 | numeric loopback DNS | Harness-only |
| <code>c0fadcc9f6ed</code> | E1749 | undefined port | Harness-only |
| <code>a8c2e752f927</code> | F2F95 | ticket mismatch | Harness-only |
| <code>2f2be3c4be3</code> | 6AEF | child identity | Harness-only |
| <code>58732b3adedf</code> | 2D9A | descendant leak | Harness-only |
| <code>5acd688a9e20</code> | B38D | missing <code>spawnSync</code> | Harness-only |
| <code>dd2b79b86c12</code> | 439C | SelfTest PASS, superseded | Retained historical evidence / 保留历史证据 |
| <code>032938238093</code> | 439C | Collect NUL denied | Harness-only |
| <code>54c3f8cc4ab7</code> | 31DD | SelfTest PASS, superseded | Retained historical evidence |
| <code>8824d3b3cd3f</code> | 31DD | Collect 63 | Harness/contract mismatch |
| <code>e7816da4b1b6</code> | 080C | SelfTest PASS | Superseded evidence |
| <code>a20d8e563fa3</code> | 080C | Collect PASS | Superseded evidence |
| <code>e8cb9b668819</code> | 080C | Preflight 19/45 errors | Harness/test environment diagnostic |
| <code>805c4cd9c8d3</code> | 70B | SelfTest PASS | Superseded evidence |
| <code>0f90a134be5f</code> | 70B | Collect PASS | Superseded evidence |
| <code>272d6d7bcbd8</code> | 70B | Preflight 41/23 SocialKit ACL | Harness/ACL, not a proven platform defect |
| <code>16e095fb6489</code> | AEF3 | Current sealed SelfTest PASS | Current authoritative phase evidence |
| <code>91f4c16e80ad</code> | AEF3 | Collect enumerated 64; seal failed at zero disk | Current RED/unsealed; preserve |

Fresh C-drive snapshot during handoff: 2,322,845,696 bytes free (2.163 GiB). This only barely exceeds the old 2 GiB precondition and is not durable headroom. Collect64 remains postponed by user decision; do not consume the remaining space with a gate run.

交接期间C盘新快照：可用2,322,845,696字节（2.163 GiB）。这仅勉强超过旧的2 GiB前置线，不构成稳定余量。Collect64仍按用户决定推迟，禁止用门禁运行消耗剩余空间。

### 9.8 Retention and cleanup / 保留与清理

- Preserve all <code>C:\Users\asus\r5</code> evidence roots, all permit files, current SQLite/WAL/SHM, immutable crawler captures, frontend dirty paths, browser profiles, and account configuration.
- Do not delete zero-byte evidence; a zero-byte output can be the truthful failure artifact.
- Do not mutate <code>cb887…</code> or any evidence belonging to <code>f89d…</code>.
- No cleanup is currently authorized. When cleanup is later requested, resolve exact targets and prefer recoverable, narrow operations.

保留所有门禁证据根、许可文件、SQLite/WAL/SHM、不可变爬虫日志、前端脏改动、浏览器profile与账号配置。零字节证据也不得删除；当前未授权任何清理。

## 10. Decisions and Pitfalls / 10. 关键决策与踩坑记录

### 10.1 Binding product decisions / 约束性产品决定

1. **Human input ownership / 人工输入归属：** the user personally selects creators/videos and presses Start for Round 5. Agents may diagnose, implement, test in bounded isolation, and report readiness; they may not issue the live collection POST.
2. **Standard versus Link / 标准与Link：** standard collection may collect creator data. Link collection is video-only and must not crawl creator profiles/homepages, creator history, comments, avatars, search/hot pages, or collections.
3. **Collect64 order / Collect64顺序：** retry only after #1 has a successful or explicitly accepted user result. A live failure record alone does not authorize the gate retry.
4. **Subtitle / 字幕：** Subtitle Direct remains OFF/frozen. Its former team capacity is assigned to Platform Optimization without reopening subtitle files.
5. **Code Director / 代码总监：** permanently independent, review-only, never merged into Platform, Link, Subtitle, frontend, or harness implementation.
6. **Production / 生产：** the local-manual grant is not a production/commercial/SaaS grant. Production, canary, simultaneous multi-account, and autonomous initiation remain NO-GO.

### 10.2 Disjoint ownership and freeze map / 不相交归属与冻结图

| Owner / 归属 | Owns now / 当前负责 | Must not touch / 禁止触碰 |
|---|---|---|
| Platform Optimization / 平台优化组 | Task #1 budget/failure-precedence repair; standard collection; authorization lifecycle; account/docs reconciliation; frontend provenance once live task is terminal | Link frozen source identities; Subtitle source; detached evidence; Code Director verdicts |
| Link Collection / 链接采集组 | Read-only frozen-hash verification and user-owned Link manual boundary proof | Standard creator-data removal; creator-profile expansion in Link; Subtitle; platform budget code unless formally reassigned |
| Former Subtitle capacity / 原字幕产能 | Already reassigned to Platform Optimization / 已转平台优化 | All frozen subtitle source and runtime enable flags |
| Detached Round-5 gate executor / 外置门禁执行 | Fresh phase only with exact current bytes and a phase-specific permit | Project feature development; live/production mutation; prior evidence rewrite |
| Independent Code Director / 独立代码总监 | A→B alignment, architecture/freeze review, exact-byte verdicts, integration coordination | Implementation ownership or merger into any group |

When a non-Director group finishes its disjoint assignment, its available capacity may join Platform Optimization, matching the user’s instruction. The Code Director is the sole permanent exception.

非总监小组完成独立任务后，可按用户要求把空闲产能并入平台优化组；代码总监是唯一永久例外。

### 10.3 Platform defects versus harness-only defects / 平台缺陷与门禁专属缺陷

| Finding / 发现 | Classification / 归类 | Current action / 当前动作 |
|---|---|---|
| Link runtime store close race | Proven platform defect, fixed / 已证平台缺陷，已修 | Keep frozen hashes; do not reopen casually |
| <code>comment:16/15</code> across sparse/paginated comments | Proven current platform/runtime defect / 已证当前平台运行时缺陷 | Active counts are 0; fix directly under #1 with a failing regression and independent review / 活动数为0；按#1以失败回归和独立复审直接修复 |
| Earlier Argus counted twice and shown as primary account error | Platform error-precedence/observability question; Argus event itself was genuine / 平台错误优先级与可观测性问题；Argus事件本身真实 | Preserve both causes; do not erase safety signal |
| Duplicate <code>load_accounts()</code>, stale README defaults/counts | Platform source/document defect / 平台源码与文档缺陷 | Task #7 |
| Frontend CSS provenance mismatch | Integration/provenance defect / 集成与来源缺陷 | Task #6; preserve dirty tree |
| Numeric loopback DNS, undefined port, ticket mismatch, child identity, descendant leak, missing spawnSync | Harness-only defects / 门禁专属缺陷 | Historical; do not “fix” platform code for them |
| SocialKit ACL in prior Preflight | Harness/environment ACL, not proven platform defect / 门禁环境ACL，并非已证平台缺陷 | Diagnose only during a permitted fresh Preflight |
| AEF3 Collect64 seal failure at zero disk | Harness evidence-retention failure / 门禁证据保留失败 | Preserve; fresh mirror/permit/headroom after manual success |

### 10.4 Authorization design decision / 授权设计决定

The button was not opened with a global boolean, demo mode, monkeypatch, removed gate, or fake success. The implementation binds exact document bytes to a code-reviewed record with scope, issue/expiry time, and false production/parallel/Agent flags; start and resume both recheck the scope before mutation. The document must not be edited because one byte changes its digest.

按钮不是通过全局布尔值、演示模式、monkeypatch、删除门禁或伪造成功来开放。实现把授权文档精确字节绑定到代码评审记录，并强制范围、签发/到期时间及生产/并行/Agent发起均为false；start与resume均在变更状态前复核。授权文档不得再编辑，因为任意字节变化都会改变摘要。

### 10.5 Test isolation pitfall / 测试隔离踩坑

The first bounded authorization test run reported all assertions passing but returned exit 1 because the isolation guard detected that the live backend wrote a production log during pytest. After confirming zero active tasks at that earlier moment and stopping only the verified port-8000 backend leaf, the exact 15-test selection passed in 3.25 seconds with exit 0. The backend was then restarted through <code>start.ps1</code> and verified loopback-only.

首次有界授权测试的断言全部通过，但pytest期间在线后端写生产日志，隔离守卫因此返回exit 1。此前确认活动任务为0后，仅停止经核验的8000端口后端叶进程；同一15项测试随后在3.25秒内全部通过、exit 0。之后通过 <code>start.ps1</code> 重启后端并核验仅回环监听。

That stop sequence was intentionally not repeated while task <code>f89d…</code> was active. It is terminal now, but every future restart still requires a fresh zero-active-task check. / 任务 <code>f89d…</code> 活动时没有重复停止流程；现虽已终态，每次未来重启仍需重新确认活动任务为0。

### 10.6 Simplification review constraint / 简化审查约束

Repository instructions require <code>/simplify</code> after project-code edits. That skill was not present in this session’s available-skill catalog, so it could not be invoked. The fallback was Python AST parsing, focused diff/test review, and a separate independent Code Director review. A future Codex must invoke <code>/simplify</code> immediately after each code edit if it is available; if unavailable, state the limitation and repeat an equivalent bounded review.

仓库要求项目代码每次修改后调用 <code>/simplify</code>。本会话可用技能列表中没有该skill，因此无法调用；替代措施为Python AST解析、聚焦diff/测试审查和独立代码总监复审。新Codex若可用必须在每次代码修改后立即调用；若仍不可用，需明确说明并执行等价有界审查。

## 11. Risks and Pending Confirmations / 11. 风险与待确认项

| ID | Risk or unknown / 风险或未知 | How to resolve / 解决方式 |
|---|---|---|
| ❓R1 | Whether the user considers the two failed manual records sufficient for Round-5 diagnosis or requires a post-fix acceptance retry is not explicitly recorded. / 用户是否把两次失败记录视为足够诊断，还是要求修复后再验收，尚未明确记录。 | Treat #1 as incomplete; prepare the bounded fix, report readiness, and let the user decide and start any retry. |
| ❓R2 | Product decision for comment-budget exhaustion is not written: reject early, cap pagination/checkpoint partial video data, or compute a compatible bound. / 评论预算耗尽的产品行为未定稿。 | Reproduce in tests; choose one bounded contract with the user/product intent; obtain independent review. |
| ❓R3 | Tweet/X is named but no verified implementation/source/auth/field/rate/privacy contract exists. / 项目名含推文/X但无已核验实现契约。 | User formally excludes it from this milestone or supplies a lawful written contract. |
| ❓R4 | Frontend CSS provenance conflicts with the prior handoff; global frontend freeze is absent. / 前端CSS来源冲突且无整体冻结。 | Preserve all dirty paths; perform provenance review and one manifest under task #6. |
| ❓R5 | README says 12 internal accounts and transcript default 10; source/config say 51 enabled and effective default 2. / README与源码不一致。 | Resolve duplicate loader and update/labelling under task #7. |
| ❓R6 | Production design artifacts for commercial authorization, ACL, credential governance, request-level rate proof, canary, rollback, monitoring, and incidents were not found. / 未发现生产闭环资料。 | Separate production program; do not reuse local grant. |
| ❓R7 | No proxy or split-tunnel requirement was proven for the local UI. / 未证明本地UI需要代理或分流。 | Inspect only redacted environment key presence and actual provider error; do not invent routing. |
| ❓R8 | Historical HTTP 422 response bodies were not retained. / 历史422响应体未保留。 | Treat current eligible health and task acceptance as superseding authorization evidence; keep historical body unknown. |
| ❓R9 | No standalone immutable post-artifact Code Director verdict file was found for current SelfTest. / 当前SelfTest缺少独立不可变的证据后总监裁定文件。 | Require a fresh phase-specific permit/verdict before Collect64; do not rewrite old evidence. |
| ❓R10 | Project root and bundled MediaCrawler have no local Git history; provenance cannot be recovered through Git there. / 项目根与MediaCrawler无Git历史。 | Preserve byte hashes and handoffs; never invent commit ancestry. |
| ❓R11 | C drive had only 2.163 GiB free during handoff and may fall below the gate threshold. / C盘空间仅2.163GiB且会变化。 | Measure immediately before any permitted gate; create a fresh evidence root; do not clean without exact authorization. |
| ❓R12 | Cookie-export vault placement warning remains. / Cookie导出保险库路径警告仍在。 | Inspect the exporter’s dedicated-vault contract after the live task is terminal; never copy browser cookies into documentation. |

## 12. From-Zero Continuation Manual / 12. 续作启动手册（从零恢复）

> [!danger] First gate / 第一门禁
> **EN:** Before cleanup, restart, testing, or editing runtime-sensitive code, query the active standard and Link tasks. If either is active, monitor only. At the final handoff snapshot both counts were zero; this is a point-in-time fact, not permission to skip the check.
>
> **中文：** 在清理、重启、测试或修改运行时敏感代码前，先查询标准与Link活动任务。任一活动时只能监看。最终交接快照中两类活动数均为0，但这只是时间点事实，不能据此跳过复查。

### 12.1 Reattach without mutation / 无状态变更地续接

1. Open PowerShell 7.6.4 and locate the project / 打开PowerShell并定位项目：

       $projectTask = 'D:\全自动爬取短视频、推文爆款程序'
       Test-Path -LiteralPath $projectTask
       Set-Location -LiteralPath $projectTask

   Correct signal / 正确信号：<code>True</code>; current directory is the exact project root.

2. Read the active tasks / 读取活动任务（verified / 已核验）：

       $activeStandardTask = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/collections/active' -TimeoutSec 15
       $activeStandardTask | ConvertTo-Json -Depth 12

   Final handoff signal is <code>null</code>. If a future call returns any active task, do not run steps 12.2–12.4; GET its task/log endpoint only. / 最终交接信号为 <code>null</code>；未来若返回活动任务，禁止执行12.2–12.4，只可GET任务与日志。

3. Inspect listener ownership / 检查监听归属（verified / 已核验）：

       Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
         Where-Object LocalPort -in 3000,3100,8000,8765,18880,9222 |
         Sort-Object LocalPort |
         Select-Object LocalAddress,LocalPort,OwningProcess

       Get-CimInstance Win32_Process |
         Where-Object { $_.CommandLine -match 'backend\.app\.main:app|MediaCrawler\\main\.py' } |
         Select-Object ProcessId,ParentProcessId,Name,CommandLine

   Correct signal / 正确信号：backend is loopback <code>127.0.0.1:8000</code>; any MediaCrawler child corresponds to the active user task. Never bulk-kill <code>python.exe</code>, Node, browser, or wrappers.

4. Re-read the two known Round-5 tasks / 重读两次已知第5轮任务：

       Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/collections/cb8873ba4942472bab1063663634674b' -TimeoutSec 15 | ConvertTo-Json -Depth 12
       Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/collections/f89d2b9a62744f3695bcaff3eeea338e' -TimeoutSec 15 | ConvertTo-Json -Depth 12

   Reattached signal / 续上信号：the first remains failed; the second’s current/terminal result is recorded without alteration; immutable capture paths and hashes are retained.

### 12.2 Conditional residual-process cleanup / 有条件的残留进程处理

Only after both active counts are zero and only when a verified backend restart is necessary, resolve the current port-8000 listener again. This controlled template is state-changing and was **not executed while the second task was active**.

仅当两类活动数均为0且确需重启时，重新解析当前8000监听。该模板会改变状态，在第二个任务活动期间**没有执行**。

    $listenerTask = Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction Stop
    if (@($listenerTask).Count -ne 1) { throw 'Expected exactly one port-8000 listener / 预期恰好一个8000监听' }
    $backendPidTask = [int]$listenerTask.OwningProcess
    $backendProcessTask = Get-CimInstance Win32_Process -Filter "ProcessId=$backendPidTask"
    if ($backendProcessTask.CommandLine -notmatch 'uvicorn\s+backend\.app\.main:app') { throw 'Refusing unknown listener / 拒绝未知监听' }
    Stop-Process -Id $backendPidTask
    while (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue) { Start-Sleep -Milliseconds 250 }

Do not reuse PID 9820 or any PID from this document; PIDs are volatile. Do not stop parent wrappers or unrelated Python processes. / 禁止复用文档中的PID；PID会变化。禁止停止父包装器或无关Python进程。

### 12.3 Start the local stack / 启动本地栈

The canonical command was executed successfully during authorization reload / 标准命令已在授权重载时成功执行：

    Set-Location -LiteralPath 'D:\全自动爬取短视频、推文爆款程序'
    .\start.ps1

Expected output / 预期输出：the script prints the Firefox login/profile directory plus frontend and backend URLs. It starts only missing listeners; if port 8000 is already occupied, it does not reload the old backend configuration.

脚本会打印Firefox登录/profile目录及前后端URL，并仅启动缺失服务；8000已占用时不会重载旧后端配置。

### 12.4 Verify that continuation succeeded / 核验已续上

    $healthTask = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 15
    [pscustomobject]@{
      Status = $healthTask.status
      Ready = $healthTask.real_collection_ready
      Authorization = $healthTask.mediacrawler.deployment_authorization.eligible
      Scope = $healthTask.mediacrawler.deployment_authorization.scope
      Production = $healthTask.mediacrawler.deployment_authorization.production_eligible
      Parallel = $healthTask.mediacrawler.deployment_authorization.parallel_accounts_allowed
      AgentInitiation = $healthTask.mediacrawler.deployment_authorization.agent_initiation_allowed
      Expires = $healthTask.mediacrawler.deployment_authorization.expires_utc
    }

Correct signal / 正确信号：<code>Status=ok</code>, <code>Ready=True</code>, authorization <code>True</code>, scope <code>round5_manual_local</code>, and all three production/parallel/Agent flags <code>False</code>. If expired, do not re-enable automatically; ask the user and independent Code Director for a new exact grant.

Open / 打开：<code>http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/collection</code>. The old red <code>written_authorization_not_reviewed</code> message must be absent while the grant is valid. A visible page does not prove the comment-budget defect is fixed.

### 12.5 Continue development after the live task is terminal / 活动任务终态后继续开发

1. Execute section 7.1 steps 1–4 and capture the failing regression.
2. Modify only the files required by the selected bounded budget contract.
3. Invoke <code>/simplify</code> immediately after each project-code edit if available; otherwise document the fallback.
4. Run focused tests first; retain output; then obtain independent Code Director review.
5. Verify live health and zero active tasks.
6. Tell the user the platform fix is ready. The user chooses and starts the next live task.
7. Only after an accepted manual result may #3 Collect64 be considered with a fresh permit.

对应中文：先复现失败回归，再做最小有界修改；每次修改后执行简化审查；跑聚焦测试并由独立总监复审；确认无活动任务后通知用户，由用户本人启动；形成可接受手测结果后才可考虑Collect64。

## 13. Codex-Specific Addendum / 13. 按 Codex 定制的附加内容

### 13.1 Codex configuration / Codex配置

Verified local presence / 已核验本地存在：

- <code>C:\Users\asus\.codex\config.toml</code>: present.
- <code>C:\Users\asus\.codex\sessions</code>: present.
- <code>C:\Users\asus\.codex\auth.json</code>: present; never include it in migration or documentation.
- Non-secret config selectors observed: <code>model = "gpt-5.6-sol"</code>, <code>model_provider = "openai"</code>.

Safe presence check, executed successfully / 安全存在性检查，已成功执行：

    $codexConfigTask = Join-Path $env:USERPROFILE '.codex\config.toml'
    [pscustomobject]@{
      Config = Test-Path -LiteralPath $codexConfigTask
      Sessions = Test-Path -LiteralPath (Join-Path $env:USERPROFILE '.codex\sessions')
      Auth = Test-Path -LiteralPath (Join-Path $env:USERPROFILE '.codex\auth.json')
    }

If the next machine uses a third-party OpenAI-compatible provider such as DeepSeek, verify <code>model_provider</code>, model name, base URL, and environment-variable reference in <code>config.toml</code>. Never paste an API-key value into this handoff; represent it as <code>&lt;redacted&gt;</code>. Current verified selector is OpenAI, not DeepSeek.

若新机器改用DeepSeek一类OpenAI兼容供应商，需检查 <code>config.toml</code> 中的provider、模型名、base URL及环境变量引用；API key值必须写成 <code>&lt;redacted&gt;</code>。当前已核验选择器为OpenAI，并非DeepSeek。

### 13.2 Session migration / 会话迁移

Copy the <code>sessions</code> directory only after choosing and validating a destination. Do **not** copy <code>auth.json</code>; authenticate separately on the destination account/machine. A destination was not supplied, so no migration command was executed and the destination is <span style="color:#e67e22">❓ pending confirmation</span>.

仅在确认目标目录后复制 <code>sessions</code>；**不得**复制 <code>auth.json</code>，目标账号/机器需独立登录。当前未提供目标路径，因此没有执行迁移命令，目标位置标记为 <span style="color:#e67e22">❓待确认</span>。

Controlled future template / 受控未来模板：

    $sourceSessionsTask = Join-Path $env:USERPROFILE '.codex\sessions'
    $destinationSessionsTask = '<validated-destination>\sessions'
    robocopy $sourceSessionsTask $destinationSessionsTask /E /COPY:DAT /DCOPY:DAT /R:1 /W:1

Validate the resolved destination first and ensure it is not a workspace root, home root, or authorization directory. / 执行前必须核验目标绝对路径，且不得指向工作区根、用户主目录根或授权目录。

### 13.3 Proxy and network discipline / 代理与网络纪律

- The local UI/backend use loopback and did not require a documented proxy.
- Douyin access is external and must remain user-initiated under the grant.
- Inspect only whether proxy environment keys are present; do not print their values.
- Do not add stealth, CAPTCHA bypass, proxy pools, high concurrency, or automated challenge solving.
- Tweet/X provider access is undefined until ❓R3 is resolved.

本地UI/后端使用回环地址，没有已记录的代理要求；抖音外部访问必须由用户在授权范围内发起。仅检查代理键是否存在，不打印值；禁止增加隐匿、验证码绕过、代理池、高并发或自动解挑战。

### 13.4 New-Codex relay prompt / 新Codex续接提示

Use this exact starting instruction / 使用以下启动指令：

> Read <code>F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\交接文档\0823交接文档-Codex-Codex.md</code> completely. First GET task <code>f89d2b9a62744f3695bcaff3eeea338e</code>, confirm it remains terminal failed, verify the 18 listed captures, and confirm both active counts are zero. Then execute relay item #1 from its exact functions/tests. Keep the Code Director independent, Link frozen/video-only, Subtitle OFF, production NO-GO, and Collect64 postponed until the user accepts a manual result. Never issue the live collection POST.
>
> 完整阅读上述交接文档。首先GET任务 <code>f89d2b9a62744f3695bcaff3eeea338e</code>，确认仍为失败终态，核验所列18份日志，并确认两类活动数均为0；然后从接力项#1的精确函数与测试入口开始。代码总监保持独立，Link冻结且仅视频，字幕关闭，生产NO-GO；用户接受手测结果前继续推迟Collect64。禁止Agent发起真实采集POST。

### 13.5 Files changed in this handoff turn / 本次交接回合改动文件

Project/runtime changes / 项目与运行配置改动：

1. <code>docs\authorizations\mediacrawler-round5-manual-local-20260823.md</code> — new reviewed authorization.
2. <code>backend\app\providers\mediacrawler.py</code> — scoped digest, metadata, expiry enforcement.
3. <code>backend\app\services\collection.py</code> — scoped start/resume enforcement.
4. <code>.env.local</code> — authorization path only; other values remain secret.
5. <code>backend\tests\test_mediacrawler_licensing.py</code> — authorization tests.
6. <code>backend\tests\test_collection.py</code> — collection-scope tests.

Documentation changes / 文档改动：

7. <code>F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\交接文档\0823交接文档-Codex-Codex.md</code> — this handoff.
8. <code>F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\开发日志\0821凌晨-开发日志.md</code> — minimal reciprocal Obsidian backlink only, if absent.

No Link, Subtitle, frontend, detached-harness, evidence, account, or database source file was edited. The user-created live task wrote ordinary runtime/database state; that is not an Agent-issued collection action.

未修改Link、字幕、前端、外置门禁、证据、账号或数据库源码。用户创建的真实任务写入正常运行时/数据库状态，但这不是Agent发起的采集操作。

## Pre-Delivery Self-Check / 交稿前自查

- [x] A/B anchors contain goal, user/use case, measurable acceptance, deliverables, percentage, stage, three-state inventory, gaps, and blockers. / A/B锚点完整。
- [x] A maps to section 1; B maps to section 4; section 0 states both cores. / A、B与正文映射完整。
- [x] Every unfinished baton states its goal subitem and projected progress. / 每根接力棒均绑定总目标与进度。
- [x] Completed items have result/path/verification/data; unfinished items have all seven required fields. / 已完成四字段、未完成七字段齐全。
- [x] Sections 5, 6, and 7 use the same #1–#9 numbering and command/function-level entrypoints. / 三节编号一致。
- [x] The A→B table contains observable completion signals and a concrete relay first action. / 接力表与第一步完整。
- [x] All 14 AI sections 0–13 are present. / 0–13节齐全。
- [x] No unfinished work is hidden behind “continue later” wording. / 无一笔带过。
- [x] Paths, functions, hashes, task IDs, counts, and conclusions were locally verified or marked ❓. / 信息已核验或标❓。
- [x] All commands labelled <code>verified / 已核验</code> were executed successfully. State-changing future templates are explicitly labelled and were not falsely claimed as executed. / 已核验命令真实执行；状态变更模板明确标注未执行。
- [x] Function anchors and line numbers were opened and checked against current bytes. / 函数与行号已核对。
- [x] The document is self-contained for a new Codex. / 文档自包含。
- [x] <code>config.toml</code>, provider configuration, proxy discipline, session migration, and <code>auth.json</code> exclusion are documented. / 配置、代理、会话迁移已写明。
- [x] Secret values are redacted; no cookies/tokens/API keys are reproduced. / 密钥值已脱敏。
- [x] The first actionable step requires no external material: read the active task, retain evidence, then begin #1 only after terminal. / 第一行动无需外部资料。
- [x] The scoped authorization is distinguished from production approval, and platform defects are distinguished from harness-only defects. / 授权边界与缺陷归类清晰。
- [x] The independent Code Director remains separate. / 代码总监持续独立。
- [x] Collect64 remains postponed until an accepted user manual result. / Collect64继续推迟。

## Legacy Unknowns Summary / 遗留不确定项（❓）汇总

1. ❓ Whether the user requires a post-fix acceptance retry or treats the two failed attempts as sufficient diagnostic completion. / 用户是否要求修复后再验收，还是把两次失败尝试视为足够诊断。
2. ❓ Intended bounded behavior when requested comment work cannot fit the fixed endpoint-call allowance. / 评论工作超出固定调用额度时的产品行为。
3. ❓ Tweet/X inclusion, lawful source/API, fields, authentication, rate/privacy, storage, UI, and tests. / Tweet/X范围与实现契约。
4. ❓ Frontend CSS provenance and unified freeze identity. / 前端CSS来源与统一冻结身份。
5. ❓ Whether README should be current truth or an explicitly historical document after account/default reconciliation. / README应作为当前真值还是历史文档。
6. ❓ Production/commercial permission and all production safety artifacts. / 生产/商业许可及安全资料。
7. ❓ Proxy/split-tunnel need for any future provider. / 未来Provider代理/分流需求。
8. ❓ Historical HTTP 422 response bodies. / 历史422响应体。
9. ❓ Standalone immutable post-artifact Code Director verdict for current SelfTest. / 当前SelfTest独立不可变总监裁定。
10. ❓ Safe disk headroom for a future permitted Collect64. / 未来Collect64安全磁盘余量。
11. ❓ Dedicated cookie-vault destination and migration behavior. / Cookie专用保险库目标与迁移行为。
12. ❓ Destination for any Codex <code>sessions</code> migration; <code>auth.json</code> remains excluded. / Codex会话迁移目标；继续排除auth.json。

> [!success] Relay close / 交接收口
> **EN:** The collection permission is genuinely open within its narrow local-research scope, and two terminal user-driven attempts exposed a reproducible platform comment-budget defect. The next Codex must confirm zero active tasks and preserve the evidence, then fix #1 with a failing regression and independent review. It must not spend the relay by rerunning Collect64, reopening subtitles, expanding Link, or claiming production readiness.
>
> **中文：** 采集权限已在严格的本地研究范围内真实开放；两次已终态的用户尝试暴露了可复现的平台评论预算缺陷。新Codex必须先确认活动任务为0并保留证据，再以失败回归和独立复审完成#1；不得用Collect64重跑、重开字幕、扩展Link或宣称生产就绪来消耗接力窗口。
