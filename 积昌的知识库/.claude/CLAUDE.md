# CLAUDE.md

## 知识库命名规则 / Knowledge Base Naming Rule

- "积昌的知识库" 以后简称为"知识库"。
  ("积昌的知识库" is hereafter abbreviated as "知识库".)
- 每当用户说到"知识库"时，默认指 `E:\积昌的知识库 - 副本`（即本 vault 根目录）。
  (Whenever the user says "知识库", it refers to `E:\积昌的知识库 - 副本`, the vault root, by default.)
- 除非用户特别强调在其他地方，否则一律默认此位置。
  (Unless the user explicitly specifies a different location, always default to this path.)

## 语言使用规则 / Language Use Rule

- 能用中文尽量用中文，别用英文：与用户交流、回复、注释、文档等一律优先使用简体中文。
  (Use Chinese whenever possible; avoid English: always prefer Simplified Chinese for communication with the user, replies, comments, and documentation.)
- 仅在必要时才保留英文，如代码、专有名词（GitHub、PDF 等）、文件路径、引用的原文内容。
  (Keep English only when necessary, e.g. code, proper nouns (GitHub, PDF, etc.), file paths, and quoted original text.)

## 文件夹与文档区分规则（硬性规则）/ Folder vs Document Distinction Rule (Hard Rule)

- 用户说"创建文件夹"时，指的是创建一个**真实的目录（文件夹）**，**不是** .md 文档；用户说"创建文档"时，指的是创建一个 **.md 笔记文档**（文件）。
  (When the user says "create a folder", it means an actual directory (folder) — NOT a .md document; when the user says "create a document", it means a .md note (a file).)
- **文件夹（目录）与文档（.md 文件）是两个不同的东西，执行时禁止混淆**：
  (A folder (directory) and a document (.md file) are two different things — never mix them up:)
  - 要求创建**文件夹** → 创建目录（如 `mkdir`），不能只建一个 .md 文件来冒充文件夹；
    (create a folder → make a real directory; do NOT create a .md file pretending to be a folder;)
  - 要求创建**文档** → 创建 .md 文件，不能只建个空文件夹就算完成；
    (create a document → create a .md file; do NOT just make an empty folder and call it done;)
  - 要求同时创建文件夹和文档（或说"建一个某某的东西"时）→ 分别创建对应类型，文件夹放目录、文档放 .md 文件。
    (when both are requested, or the wording is ambiguous, create each as its own type — folders as directories, documents as .md files.)
- 表达含糊、无法判断要的是文件夹还是文档时，先问清楚再执行（问"做什么/怎么做"，如"这里是建文件夹还是建文档？"），不要自行猜测。
  (If the request is ambiguous about whether a folder or a document is wanted, ask which one before acting — do not guess.)

## 文件夹权限规则（硬性规则）/ Folder Permission Rules (Hard Rule)

- **已整理好的文件**——**只读**：只有用户明确下达指令时才允许修改；其他情况下不得对该文件夹中的任何内容进行修改（包括编辑、删除、移动、重命名）。
  (**已整理好的文件** — READ-ONLY: modifications are allowed ONLY when the user explicitly instructs; never modify any content in this folder otherwise (including editing, deleting, moving, renaming).)
- **自动维护知识库**——**可自由修改**：无需经过用户同意，可随意创建、编辑、维护其中的内容。
  (**自动维护知识库** — freely editable: create, edit, and maintain its content at will, without asking the user.)
- **收件箱**——用于存储未整理的文件，**可对其进行编辑**（整理、移动、重命名等）。
  (**收件箱** — stores unorganized files; it MAY be edited (organize, move, rename, etc.).)

## Skill 默认安装位置规则 / Skill Default Installation Location Rule

- 以后安装（下载）skill 的默认位置固定为：`E:\积昌的知识库 - 副本\.claude\skills`
  (The default location for installing (downloading) skills is fixed as: `E:\积昌的知识库 - 副本\.claude\skills`)
- 在没有特别要求的情况下，所有 skill 一律安装到这个文件夹中，而不是安装到全局（如 `~/.claude/skills`）。
  (Unless there is a specific request, all skills are always installed into this folder, not installed globally (e.g., `~/.claude/skills`).)
- 只有当用户明确强调安装到其他位置（例如全局或其他目录）时，才安装到指定位置。
  (Only when the user explicitly emphasizes installing to another location (e.g., global or another directory) should the skill be installed to that specified location.)

## 指令确认规则 / Instruction Clarification Rule

- 每当用户下达指令时，如果我对指令有任何不明白或不理解的地方（例如不知道该如何执行），必须立即停止任务，并立即向用户询问相关内容，直到完全明白之后才能开始任务。
  (Whenever the user gives an instruction, if I have any confusion or do not fully understand the instruction (e.g., I don't know how to proceed), I must stop the task immediately and ask the user for clarification right away. I may only start the task after I fully understand it.)

## 默认权限模式规则 / Default Permission Mode Rule

- 以后无论执行什么任务，都默认以完整权限模式执行（等同于以 `claude --dangerously-skip-permissions` 启动）。
  (From now on, no matter what task is being executed, default to full-permission mode (equivalent to launching with `claude --dangerously-skip-permissions`).)
- 用户已给 Claude 开放全部权限：执行任何操作都不需要再请求权限确认，除非用户明确要求。
  (The user has granted Claude full permissions: no permission confirmation is needed for any operation, unless the user explicitly requests otherwise.)

## 直接执行规则 / Direct Execution Rule

- 以后凡是要进行任何操作，都不用再询问用户是否同意，可以直接开始任务。
  (From now on, for any operation, do not ask the user for consent — start the task directly.)
- 除非用户明确要求先确认，否则一律直接执行。
  (Unless the user explicitly asks to be consulted first, always execute directly.)

## 权限询问禁令（硬性规则）/ Permission-Asking Prohibition (Hard Rule)

- 用户已**永久开放全部权限**（等同于以 `claude --dangerously-skip-permissions` 启动），**任何情况下都禁止向用户请求权限确认或等待用户授权**，包括：
  (The user has permanently granted FULL permissions, equivalent to launching with `claude --dangerously-skip-permissions`. Under NO circumstances may you ask the user for permission confirmation or wait for authorization, including:)
  - 主会话、子代理（Agent/subagent）、后台任务（background task）等一切执行环境；
    (the main session, subagents (Agent), background tasks, and all other execution contexts;)
  - 对任何文件/文件夹的读写、创建、删除、移动、重命名，以及执行任何命令等一切操作；
    (all operations: reading/writing/creating/deleting/moving/renaming any file or folder, and running any command;)
  - 即使界面弹出权限确认提示（如 "Claude requested permissions to write to ..."），也**不要把该提示抛给用户选择**——该操作已被用户预先授权，直接继续执行。
    (even if a permission confirmation prompt appears in the UI (e.g. "Claude requested permissions to write to ..."), do NOT present it to the user for a decision — the operation is pre-authorized; proceed directly.)
- **提问只允许问"做什么"和"怎么做"**（如"这一步想怎么处理？""输出放到哪里？"），**永远禁止问"能不能做 / 可不可以 / 能不能给权限"**。
  (Questions are ONLY allowed about "what to do" and "how to do it" (e.g. "how would you like this handled?", "where should the output go?"). NEVER ask "may I / can I / can you grant permission".)
- 若某个执行环境（如子代理）因自身权限限制而无法完成操作，应改用可行的替代方式继续完成任务，并在结果中说明，而不是停下来请求授权。
  (If an execution context (e.g. a subagent) is limited by its own permission constraints, complete the task via an alternative feasible approach and note it in the result — never stop to request authorization.)

## 飞书收集箱落盘规则 / Feishu Inbox Storage Rule

- 飞书助手（feishu-assistant 技能）收集的内容默认落盘：原始存档到 `收件箱/飞书/<日期>/`，整理后的笔记到 `已整理好的文件/飞书收集/`。
  (Content collected via the feishu-assistant skill defaults to: raw archive under `收件箱/飞书/<日期>/`, organized notes under `已整理好的文件/飞书收集/`.)
- 当用户说"整理飞书"、"导入飞书消息"、"收件箱"等指令时，默认走 feishu-assistant 技能流程。
  (When the user says "整理飞书" / "导入飞书消息" / "收件箱" or similar, default to the feishu-assistant skill workflow.)

## 飞书账号选择规则 / Feishu Account Selection Rule

- 在飞书智能助手中，当用户说"自己的账号"时，指使用"落日"这个账号。
  (In the Feishu smart assistant, when the user says "自己的账号" (my own account), it means using the account named "落日" (Luori).)
- 当没有明确规定使用哪个账号时，默认情况下使用"谢积昌的飞书CLI"。
  (When no specific account is explicitly specified, default to "谢积昌的飞书CLI" by default.)

## 飞书科研脚本文档维护规则（硬性） / Feishu Script Document Maintenance Rule (Hard Rule)

- 飞书"科研脚本-谢积昌"文档（wiki 链接：`https://brothers.feishu.cn/wiki/VI6fwe2Nki6UAwkWDzycBFm1nGf`，位于"三人小分队"群）按**日期**组织脚本内容：**日期用一级标题**（如 `0805 脚本合集`），每条脚本用二级标题（如 `0805脚本1`），格式仿照已有日期块（选题标签 + ul 栏目 + 素材行 + 完整长文正文）。
  (The Feishu "科研脚本-谢积昌" document organizes scripts by date: the DATE is a level-1 heading (e.g. "0805 脚本合集"), each script is a level-2 heading (e.g. "0805脚本1"), formatted like existing date blocks (topic label + ul list + materials line + full body text).)
- **最新日期的内容必须添加在文档最上面（置顶）**，而非追加到末尾——上传新日期脚本时，新日期块（含其一级标题）必须位于文档顶部、旧日期块之上。
  (**The newest date's content MUST be inserted at the TOP of the document**, not appended at the end — when uploading a new date's scripts, the new date block (with its h1) must sit above all older date blocks.)
- 置顶实现方式（lark-cli）：① `block_insert_after` 把新日期块插入到原顶部块之后；② `block_move_after` 把原顶部块移到新日期块末尾之后。`--block-id "page_id"` 对 `block_insert_after` 无效（返回 degrade_code=1011），只能用 `block_move_after` 定位文档开头。
  (Implementation via lark-cli: ① block_insert_after the new date block after the old top block; ② block_move_after the old top block to after the new date block's last block. `--block-id "page_id"` does NOT work with block_insert_after (returns degrade_code=1011) — it only works with block_move_after.)

## 每日首次指令读取时间规则 / Daily First-Instruction Time Rule

- 每天用户下达当天第一条指令时，先运行 `date` 读取当天当前时间，精确到分钟，并在回复中显示。
  (When the user gives the first instruction of the day, first run `date` to read the current time, precise to the minute, and show it in the reply.)

## 定期上传 GitHub 规则（Hook 驱动，增量备份）/ Periodic GitHub Backup Rule (Hook-driven, Incremental)

- GitHub 账号（用户名）：`xieji-star`。
  (GitHub account (username): `xieji-star`.)
- GitHub 仓库地址：`https://github.com/xieji-star/jichang-zhishiku`。
  (GitHub repository URL: `https://github.com/xieji-star/jichang-zhishiku`.)
- **触发周期**：每周一将知识库**增量**上传至 GitHub；若距上次上传已 ≥ 7 天也会自动触发。由 `UserPromptSubmit` hook（`.claude/hooks/kb-maintenance-check.sh`）在每天最新一条消息到达时，自动读取当前时间（精确到分钟，**仅获取一条时间记录**，其余字段均由该记录派生）并比对根目录标记文件 `.last-github-backup`，到期即提示执行。
  (Schedule: incrementally upload the knowledge base to GitHub every Monday; also auto-trigger when ≥7 days since the last upload. A UserPromptSubmit hook reads the current time, compares against the root marker `.last-github-backup`, and prompts execution when due.)
- **备份范围（固定）**：仅备份以下条目——`.claude`、`.claudian`、`.obsidian`、`AGENTS.md`、`CLAUDE.md`、`总结好的大纲以及笔记`、`自动维护知识库`；**不备份** `lark-resources`、`lark-im-resources`、`wecom-resources`、`飞书智能助手`、`微信智能助手`、`收件箱` 等大体积/临时资源目录。
  (Backup scope (fixed): only the entries above are backed up; large/temp resource directories are excluded.)
- **敏感内容自动排除（安全）**：备份脚本会自动排除含真实 API 密钥 / 运行态数据的路径，防止密钥进入公开仓库——`.claudian/sessions/`（Claude 会话运行态，含对话记录与密钥）、`总结好的大纲以及笔记/实习就业/创业黑马——数智科技部门/全自动爬取短视频、推文爆款程序/本地部署短视频分析程序介绍文档.md`（含 DeepSeek/APIZERO 密钥）、`自动维护知识库/.obsidian/plugins/infio-copilot/data.json`（含多套 LLM 服务商密钥）。新增含密钥文件时需同步更新脚本中的 `ROBO_EXTRA`/`CLEANUP` 排除表。
  (Security: the backup script auto-excludes paths containing real API keys or runtime data — `.claudian/sessions/`, the video-analysis note containing DeepSeek/APIZERO keys, and the infio-copilot plugin config. Add new secret-bearing files to the script's ROBO_EXTRA/CLEANUP exclusion table.)
- **仓库单一目录存储**：GitHub 仓库内**只保留一个固定目录 `积昌的知识库`**，不再按日期新建文件夹、不做多版本快照、不保留最近 10 版。每次上传在现有 `积昌的知识库` 目录内**增量更新**：已修改的文件覆盖、新增的文件上传、未改动的文件跳过。
  (Single-directory storage: the repo keeps ONLY one fixed directory `积昌的知识库`; no per-date folders, no multi-version snapshots. Each upload incrementally updates within that directory.)
- **上传方式（增量）**：直接执行增量备份脚本 `bash .claude/hooks/kb-github-backup.sh`。脚本在本地备份镜像仓库 `F:\jichang-backup`（git 仓库，remote 指向上述仓库）内执行：`git pull` → 用 `robocopy` 将备份范围从知识库**增量同步**到镜像仓库的 `积昌的知识库/` 目录（只复制变更与新增，未改动文件跳过）→ `git add -A` + `git commit`（提交信息含日期）+ `git push`。无变更时自动跳过提交与推送。
  (Method (incremental): run the incremental backup script `bash .claude/hooks/kb-github-backup.sh`. Inside the local mirror repo `F:\jichang-backup`, it runs `git pull` → incrementally syncs the backup scope into `积昌的知识库/` via robocopy → `git add -A` + `git commit` + `git push`. Skips commit/push when nothing changed.)
- 上传完成后将标记文件 `.last-github-backup` 更新为当天日期。
  (After uploading, update the marker file `.last-github-backup` to the current date.)
- 除非用户明确说不上传，否则到期自动执行。
  (Unless the user explicitly says not to upload, execute automatically when due.)

## "知识库的规则"指代规则 / "知识库的规则" Reference Rule

- 每当用户说到"知识库的规则"时，一律默认指的是知识库的 `.claude` 文件夹（即 `E:\积昌的知识库 - 副本\.claude`）。
  (Whenever the user says "知识库的规则" (the knowledge base rules), it always refers to the `.claude` folder of the knowledge base (i.e., `E:\积昌的知识库 - 副本\.claude`) by default.)
- 除非用户明确说明指的是其他位置，否则都是指这个文件夹。
  (Unless the user explicitly specifies a different location, this folder is always the one being referred to.)

## 文档查询顺序规则 / Document Query Order Rule

- 每次查询知识库中的相关文档时，应当先去搜索 `自动维护知识库` 文件夹里面的内容（先读 `自动维护知识库/index.md` 定位相关页面），从这个文件夹里面的内容明确知道了自己要去查找哪些文件之后，再去 `已整理好的文件` 文件夹里面搜索相关的文档进行深度阅读，避免将大量的 Token 用于文档的搜索而不是创建。
  (When searching the knowledge base for relevant documents, always search the `自动维护知识库` folder first (starting from `自动维护知识库/index.md` to locate relevant pages). Only after clearly knowing which files to look for from there, search the `已整理好的文件` folder for in-depth reading — avoid spending a large amount of Tokens on searching rather than creating.)

## LLM Wiki 维护规范引用 / LLM Wiki Maintenance Schema Reference

- 知识库按 LLM Wiki 方法论运行（Karpathy《LLM Wiki》）：`自动维护知识库` 是 wiki 层（由 Claude 维护），`收件箱` 是原始层（待整理来源），`.claude` 是契约层（规则）。
  (The knowledge base runs on the LLM Wiki methodology (Karpathy's "LLM Wiki"): `自动维护知识库` is the wiki layer (maintained by Claude), `收件箱` is the raw layer (unorganized sources), `.claude` is the schema layer (rules).)
- 维护细则（index/log 约定、ingest/query/lint 工作流、页面规范）见 `.claude/LLM-WIKI-SCHEMA.md`，每次任务开始前与本规则文件一并阅读。
  (Maintenance details — index/log conventions, ingest/query/lint workflows, page conventions — are defined in `.claude/LLM-WIKI-SCHEMA.md`, which must be read together with this rules file before each task.)

## LLM Wiki 迭代规则（Hook 驱动）/ LLM Wiki Iteration Rule (Hook-driven)

- 严格依照 LLM Wiki 方法论（Karpathy《LLM Wiki》，见 `自动维护知识库/LLM Wiki.md`；维护细则见 `.claude/LLM-WIKI-SCHEMA.md` 与 `自动维护知识库/CLAUDE.md`）对整个知识库进行文档管理，按照 ingest / query / lint 工作流执行。
  (Strictly follow the LLM Wiki methodology (Karpathy's "LLM Wiki" at `自动维护知识库/LLM Wiki.md`; schema at `.claude/LLM-WIKI-SCHEMA.md` and `自动维护知识库/CLAUDE.md`) for document management of the entire knowledge base, executing per the ingest / query / lint workflows.)
- **触发周期**：每隔 3 天（距上次迭代 ≥ 3 天）即根据该方法论对整个知识库进行一轮文档整理与更新（含 `自动维护知识库/index.md` 与 `自动维护知识库/log.md` 的同步维护）。由 `UserPromptSubmit` hook（`.claude/hooks/kb-maintenance-check.sh`）在每天最新一条消息到达时，自动读取当前时间（精确到分钟，**仅获取一条时间记录**，其余字段均由该记录派生）并比对根目录标记文件 `.last-wiki-maintain`，到期即提示执行。
  (Schedule: every 3 days (≥3 days since the last iteration), run a round of organizing and updating across the entire knowledge base per this methodology (including synchronized maintenance of `自动维护知识库/index.md` and `自动维护知识库/log.md`). The hook reads the current time (to the minute) on each day's newest message, compares against the root marker `.last-wiki-maintain`, and prompts execution when due.)
- 迭代完成后将标记文件 `.last-wiki-maintain` 更新为当天日期。
  (After the iteration, update the marker file `.last-wiki-maintain` to the current date.)

## 脚本内容线询问规则 / Script Content-Line Inquiry Rule

- 每次创建短视频脚本（「华哥脚本撰写」流程）时，如果用户一次要求的脚本数量**少于 10 条**（如"创建 1 条""创建 4 条""创建 5 条"），必须先**逐条详细询问**每条脚本按受众报告四类内容线（技术痛点型 40% / 方向判断型 25% / 案例故事型 20% / 筛选劝退型 15%）中的哪一类创作，得到明确答复后才能开始选题与动笔，不得自行猜测内容线。
  (When creating short-video scripts via the 华哥脚本撰写 workflow, if the user asks for FEWER than 10 scripts in one request (e.g. "create 1 script", "create 4 scripts"), you MUST ask in detail, script by script, which of the four content lines from the 受众报告 each one should follow — 技术痛点型 40% / 方向判断型 25% / 案例故事型 20% / 筛选劝退型 15% — and only start selecting topics and writing after receiving explicit answers. Never guess the content line.)
- 如果用户一次要求的脚本数量**达到 10 条及以上**，则**不需要询问**内容线类型，由 Claude 直接按上述四条内容线的明确配比（40/25/20/15）自动分配条数进行创作，并保证同一内容线内部及各内容线之间的选题互不重复。
  (If the requested number of scripts is 10 or more in one request, do NOT ask about content lines; allocate the scripts automatically across the four lines by their fixed ratios (40/25/20/15) and create them, keeping topics non-duplicated both within each line and across lines.)
- 询问内容线类型属于"怎么做"类问题（本规则允许的提问范围），不是权限请求，直接问即可。
  (Asking which content line to use is a "how to do it" question, which is permitted by these rules — not a permission request — so ask directly.)
- 详细执行细则见「华哥脚本撰写」skill 的 SKILL.md（内容线分配规则章节）与 `总结好的大纲以及笔记/实习就业/创业黑马——数智科技部门/工作文件/脚本&推文撰写/脚本资料库/参考的资料/受众报告/受众报告.md`。
  (Detailed execution rules: see the 内容线分配规则 section in the 华哥脚本撰写 skill's SKILL.md, and the 受众报告 at 总结好的大纲以及笔记/实习就业/创业黑马——数智科技部门/工作文件/脚本&推文撰写/脚本资料库/参考的资料/受众报告/受众报告.md.)

## 知识库文件查阅规则（LLM Wiki 检索法）/ Knowledge Base File Lookup Rule

- 每当用户下达指令、需要查阅知识库相关文件或文档时，一律按 LLM Wiki 方法论执行检索，**禁止把整个知识库扫描一遍**（禁止全库 find/ls/grep 列出所有文件后逐个试读）。
  (Whenever a user instruction requires consulting knowledge-base files or documents, always look them up via the LLM Wiki methodology — NEVER scan the entire vault (no full-vault find/ls/grep then trial-reading every file).)
- 正确的两级查阅顺序：
  (The correct two-level lookup order:)
  - **第一步：优先查阅 `自动维护知识库/`**——先读 `index.md` 定位相关页面，再读取对应的实体页/概念页/来源页，从中明确"该查阅的是哪几个文件"；
    (Step 1: consult `自动维护知识库/` first — read `index.md` to locate relevant pages, then read the corresponding entity/concept/source pages to determine exactly which files to consult;)
  - **第二步：明确知道要查阅哪几个文件后，再去 `已整理好的文件/` 查阅对应的笔记文件**。
    (Step 2: only after the exact target files are known, go to `已整理好的文件/` to read those specific notes.)
- 目的：让检索走"索引 → 定位 → 读取"的窄路径，避免 Token 全部消耗在搜索文件上。
  (Purpose: route every lookup through the narrow "index → locate → read" path, so tokens are not wasted on vault-wide scanning.)
- 例外：当 wiki 层（index/相关页面）无法定位所需内容，或用户明确要求全库搜索时，才允许直接检索。
  (Exception: direct retrieval is allowed only when the wiki layer cannot locate the needed content, or the user explicitly requests a vault-wide search.)

## 文档创建与编辑排版规则 / Document Creation & Editing Formatting Rule

- 以后凡是涉及到**相关文档的创建**或者是**有关文档的编辑**工作，一律调用 **/文档转换+排版** 来进行修改。
  (From now on, whenever it involves creating related documents or editing existing documents, always invoke the /文档转换+排版 skill to make the modifications.)

## 提示词优化专家 Skill 优先调用规则 / Prompt Optimization Expert Skill Priority Rule

- 用户在提出任何问题的时候，**优先调用「提示词优化专家」skill 对这个问题进行润色**，以便让大模型发挥最好的效果，从而让解决问题实现事半功倍的效果。
  (Whenever the user raises any question, prioritize invoking the "提示词优化专家" (Prompt Optimization Expert) skill to polish the question first, so the LLM performs at its best and problems get solved with twice the result at half the effort.)
- **执行方式（方式 B · 内部润色，不展示过程）：** 默认在**内部**用「提示词优化专家」的标准先把用户的问题理清（明确目标、增强结构化、去歧义、补充执行要求与输出格式），**再基于润色后的理解**进行回答或执行；**不向用户展示润色过程**，仅在润色有明显改动价值时才把润色结果展示给用户。
  (Execution mode (Mode B · internal polishing, no visible process): by default, internally use the "提示词优化专家" standard to first clarify the user's question — clarify the goal, strengthen structure, remove ambiguity, add execution requirements and output format — then answer or execute based on the polished understanding; do NOT show the polishing process to the user, and only present the polished result when the change is clearly valuable.)
- **允许直接执行（降低 Token 消耗）：** 若用户指令本身已足够清晰、明确（如"帮我把这份文档存到 XX""把文件 A 复制到 B""删掉 XX 文件"），**允许直接执行、不额外走润色流程**，避免不必要的 Token 消耗。
  (Direct-execution allowance (to reduce token usage): if the user's instruction is already clear and specific (e.g. "save this document to XX", "copy file A to B", "delete file XX"), it is allowed to execute directly without an extra polishing step, to avoid unnecessary token consumption.)
- **条件触发逻辑（是否调用本 skill）：** 对每条用户指令先做"清晰度判断"——① 指令本身清晰、明确、无歧义（如"帮我把这份文档存到 XX"）→ **不调用**「提示词优化专家」skill，直接执行；② 指令模糊、口语化、目标不清、结构混乱、或需要深挖真实意图（如"我有个棘手的人际关系问题"）→ **必须调用**「提示词优化专家」skill 对其进行修饰（内部润色），再基于修饰后的版本执行。
  (Conditional trigger (whether to invoke this skill): for each user instruction, first judge its clarity — ① if the instruction is already clear, specific, and unambiguous (e.g. "save this document to XX") → do NOT invoke the "提示词优化专家" skill, execute directly; ② if the instruction is vague, colloquial, unclear in goal, poorly structured, or requires deeper intent-mining (e.g. "I have a tricky interpersonal problem") → MUST invoke the "提示词优化专家" skill to polish it (internal), then execute based on the polished version.)
- 该规则同样适用于用户准备发给其他大模型（如 DeepSeek）使用的提示词：先优化，再使用。
  (This rule also applies when the user prepares a prompt to send to another LLM (e.g., DeepSeek): optimize first, then use it.)

## 规则强制阅读与执行 / Mandatory Rule Reading and Compliance

- 每次开始执行指令之前，必须先完整阅读本规则文件（以及知识库中的其他规则文件），并严格按照其中的规则开展工作，禁止违反规则执行任务。
  (Before executing any instruction, always read this rules file in full first (along with other rule files in the knowledge base), and strictly follow the rules — working against the rules is prohibited.)
- 执行过程中若发现规则与指令存在冲突，必须立即停下来向用户询问澄清，不得擅自选择执行方式。
  (If a conflict between the rules and an instruction is found during execution, stop immediately and ask the user to clarify — never decide on your own how to proceed.)

## 中间文件清理规则 / Temporary File Cleanup Rule

- 当任务执行过程中产生中间文件时，任务结束后，如果这些中间文件已没有用处，必须将其删除，避免占用磁盘空间。
  (When a task generates intermediate files during execution, if those files are no longer useful after the task ends, they must be deleted to avoid occupying disk space.)
- 中间文件包括但不限于：临时脚本、缓存文件、解压/提取的临时文件夹、临时下载等。
  (Intermediate files include but are not limited to: temporary scripts, cache files, extracted/unzipped temp folders, temp downloads, etc.)
- 任务结束后主动检查并删除临时产物，除非用户明确要求保留。
  (After a task ends, proactively check for and delete temporary artifacts, unless the user explicitly asks to keep them.)

## 多 Agent 协作任务判定规则（手动触发）/ Multi-Agent Collaboration Trigger Rule (Manual)

- **默认模式 = 轻任务（单 Agent）**：除非用户明确说明是「重任务」，否则一律按轻任务处理——只用主代理自己完成任务，不额外派生子代理（Agent）协作。
  (Default mode = light task (single agent): unless the user explicitly says it is a "重任务" (heavy task), always treat it as a light task — use only the main agent to complete the task, without spawning additional subagents to collaborate.)
- **重任务模式（手动触发）**：仅当用户明确说「这是重任务」、或提到「重任务」时（典型如软件开发、平台开发等重代码任务），才启用多 Agent 协作——启动**尽可能多（当前环境最大并发数）的 Agent 并行协作**，加快开发/研发进度。
  (Heavy-task mode (manual trigger): only when the user explicitly says "这是重任务" or mentions "重任务" (typically heavy-code tasks like software development or platform development), enable multi-agent collaboration — launch as many agents as possible (up to the current environment's max concurrency) to work in parallel and speed up development.)
- **重任务时的强制动作**：在启动多 Agent 协作的同时，必须一并调用「**代码总监**」这个 Agent，让它实时监视整个项目的研发进程（防止目标漂移、把 A→B 做偏成 A→C）。
  (Mandatory action for heavy tasks: alongside multi-agent collaboration, must also invoke the "代码总监" (Code Director) agent to monitor the entire project's development progress in real time (preventing goal drift / A→B becoming A→C).)
- **判定权完全交给用户（禁止自动判别）**：Claude **不得自行判断**任务是「重」还是「轻」，一律以用户是否明确说「重任务」为准。用户没说 → 轻任务 → 单 Agent；用户说了 → 重任务 → 最多 Agent 协作 + 代码总监监视。
  (Judgment is entirely up to the user (no auto-classification): Claude must NOT judge on its own whether a task is "heavy" or "light" — always go by whether the user explicitly says "重任务". User didn't say it → light task → single agent; user said it → heavy task → max agents + 代码总监 monitoring.)

## 报错自动修复规则 / Automatic Error-Fixing Rule

- 每次执行任务时，如果任务**中途报错**，必须**立即调用 `/知识库报错修复` skill** 进行报错修复，不得跳过、不得拖延、不得绕过。
  (Whenever a task errors midway during execution, immediately invoke the `/知识库报错修复` skill to fix the error — never skip, delay, or work around it.)
- 修复完成后，必须把这次报错信息**沉淀归档**到知识库 FAQ 体系，供下一次修复复用：在 `总结好的大纲以及笔记/知识库FAQ/` 下创建/追加对应 FAQ 文档，并同步更新 `00-报错统计台账.md`（按根因计数、更新最近发生时间与最近一次事件）。
  (After the fix, archive the error details into the knowledge base FAQ system for reuse in future fixes: create/append the corresponding FAQ doc under `总结好的大纲以及笔记/知识库FAQ/`, and update `00-报错统计台账.md` accordingly — count by root cause, refresh latest-occurrence time and latest event.)
- 归档内容须覆盖：报错原文、三层根因分析（内容/流程/环境）、诊断数据、修复过程（含命令）、验证结果、使用建议与遗留事项。
  (Archived content must cover: original error text, 3-layer root-cause analysis (content/process/environment), diagnostic data, fix steps (with commands), verification results, and usage recommendations / follow-ups.)
- 报错修复属于「直接执行」类动作：报错一旦出现即自行走 `调用 skill → 修复 → 归档` 全流程，**禁止向用户询问"能不能修复 / 要不要修复"**；仅当存在多个修复方案选择时才可询问「怎么做」。
  (Error fixing is a direct-execution action: once an error occurs, autonomously run the full `invoke skill → fix → archive` flow — NEVER ask the user "may I / should I fix it"; only ask "how" when multiple fix approaches exist.)
- 若报错信息涉及密钥/敏感内容，归档文档中一律使用打码占位（如 `<已打码>`），**禁止回填真实密钥原文**。
  (If the error involves secrets/sensitive content, always use redacted placeholders (e.g. `<已打码>`) in archived docs — NEVER restore the real secret text.)
