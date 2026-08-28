---
title: "GitHub 推送被 Secret Scanning 拦截（快照含 API 密钥）：GH013 推送保护拒绝"
type: "知识库 FAQ / 报错修复"
date: 2026-08-23
created: 2026-08-23
updated: 2026-08-28
tags:
  - GitHub
  - Secret Scanning
  - 推送保护
  - API密钥
  - git
  - 知识库备份
  - 快照
aliases:
  - GitHub推送被拦截
  - GH013
  - Secret Scanning拦截推送
  - 快照含密钥
  - 备份推送报错
source: "2026-08-23 知识库上传 GitHub 时 `git push origin main` 被拒的真实报错与修复记录"
---

# 🔴 GitHub 推送被 Secret Scanning 拦截（快照含 API 密钥）

> [!summary] 📊 报错统计速览（截至 2026-08-28）
> 🔥 **本文档共记录 <span style="color:#e74c3c">2 次报错事件</span>**（2026-08-23 首发 1 次，2026-08-28 增量备份脚本复发 1 次）。主根因为 **「GitHub 推送被 Secret Scanning 拦截（快照含 API 密钥）」**，另含 2 个伴生根因（快照目录双层嵌套、Windows 删除目录报 Device busy）。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 🔴 GitHub 推送被 Secret Scanning 拦截（快照含 API 密钥） | **2** | 12 |
> | 🟠 备份快照目录双层嵌套（git 树结构错误） | **1** | 12 |
> | 🟡 Windows 目录删除 Device or resource busy（文件被占用） | **1** | 12 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

> [!SUMMARY] 📌 结论摘要
> 2026-08-23 执行知识库例行上传 GitHub 时，<span style="color:#ff0000">`git push origin main` 被远端整体拒绝</span>：GitHub 仓库启用了 **Secret Scanning 推送保护**，扫描到快照 `积昌的知识库0823` 里混入了 <span style="color:#ff8c00">DeepSeek / ApiZero / Stripe / SiliconFlow 4 组真实 API 密钥</span>（藏在笔记配置文档与 `.claudian` 会话缓存中），返回 `GH013: Repository rule violations`。修复 = <span style="color:#1e90ff">① 密钥打码 + ② 移除会话缓存目录 + ③ git plumbing 重建树修正"双层嵌套"结构 + ④ 重挂父提交跳过含密钥的被拒提交</span>，最终推送成功 `7a3b7ed..b994cfa`。核心教训：**知识库备份本质是"把私有内容推到远端"，推送保护是最后一道防线，密钥消毒必须在打包阶段完成**。

## 🧭 快速索引

- [[#🚨 报错概况（原文）|🚨 报错概况（原文）]]
- [[#🧩 根因分析（三层）|🧩 根因分析（三层）]]
- [[#🔬 诊断数据|🔬 诊断数据]]
- [[#🛠️ 修复过程|🛠️ 修复过程]]
- [[#🧰 技术栈与术语|🧰 技术栈与术语]]
- [[#🧱 排查中遇到的问题|🧱 排查中遇到的问题]]
- [[#✅ 验证结果|✅ 验证结果]]
- [[#🛡️ 使用建议与遗留事项|🛡️ 使用建议与遗留事项]]
- [[#🔗 相关文件与附件|🔗 相关文件与附件]]

## 🚨 报错概况（原文）

### 主报错：`GH013: Repository rule violations`

执行 `git push origin main` 后，远端返回（关键行节选）：

```text
remote: warning: File 2642e1a6b7c3ee1c2a620aa0e8e737c5a3fae369 is 68.07 MB; this is larger than GitHub's recommended maximum file size of 50.00 MB
remote: warning: GH001: Large files detected. You may want to try Git Large File Storage - https://git-lfs.github.com.
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote:
remote: - GITHUB PUSH PROTECTION
remote:   —————————————————————————————————————————
remote:     Resolve the following violations before pushing again
remote:
remote:     - Push cannot contain secrets
remote:
remote:       —— DeepSeek API Key ——————————————————————————————————
remote:        locations:
remote:          - commit: a3626df0edc814c99fc600c8e4cbca31f71d5076
remote:            path: 积昌的知识库0823/积昌的知识库0823/总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/本地部署短视频分析程序介绍文档.md:389
remote:
remote:       —— Stripe API Key ————————————————————————————————————
remote:        locations:
remote:          - commit: a3626df0edc814c99fc600c8e4cbca31f71d5076
remote:            path: 积昌的知识库0823/积昌的知识库0823/.claudian/sessions/conv-1786522127698-otv1njux8.meta.json:436
remote:            path: 积昌的知识库0823/积昌的知识库0823/.claudian/sessions/conv-1786522127698-otv1njux8.meta.json:4613
remote:            path: 积昌的知识库0823/积昌的知识库0823/.claudian/sessions/conv-1786522127698-otv1njux8.meta.json:5227
remote:
To https://github.com/xieji-star/jichang-zhishiku.git
 ! [remote rejected] main -> main (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/xieji-star/jichang-zhishiku.git'
```

> [!TIP] 报错文案变体
> 同一根因在不同场景可能表现为：`GH013: Repository rule violations`、`Push cannot contain secrets`、`secret scanning alert`、`commit contains secrets`。<span style="color:#ff8c00">**以扫描结果定位的路径为准**</span>，不要被文案字眼误导。

### 伴生报错 1：快照目录双层嵌套

修复过程中用 `git ls-tree` 检查被拒提交的树，发现快照结构多套了一层：

```text
积昌的知识库0823/积昌的知识库0823/.claude
积昌的知识库0823/积昌的知识库0823/总结好的大纲以及笔记
...
```

而磁盘上 `.temp_repo/积昌的知识库0823/` 是**平铺**的（7 个顶层项直接位于其下）。即 **git 树里的路径比磁盘多一层**，导致上面 GitHub 报错里的路径也带上了双份 `积昌的知识库0823/积昌的知识库0823/`。

### 伴生报错 2：删除临时目录报 `Device or resource busy`

清理临时克隆目录时，git-bash 的 `rm -rf .temp_repo` 失败：

```text
rm: cannot remove '.temp_repo': Device or resource busy
```

改用 PowerShell `Remove-Item -Recurse -Force` 后成功删除。

## 🧩 根因分析（三层）

### ① 内容层（主根因）：快照文件混入真实 API 密钥

| # | 文件 | 密钥 | 位置 | 说明 |
|---|------|------|------|------|
| 1 | `总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序/本地部署短视频分析程序介绍文档.md` | DeepSeek `sk-<已打码>...` | 表格 + `.env` 块，各 1 处 | 部署文档把**真实密钥写进了笔记** |
| 2 | 同上 | ApiZero `sk_test_<已打码>...` | 表格 + `.env` 块，各 1 处 | 同上 |
| 3 | `.claudian/sessions/conv-1786522127698-*.meta.json` | Stripe Key | 第 436 / 4613 / 5227 行 | **会话缓存**记录了对话中含密钥的内容 |
| 4 | `自动维护知识库/.obsidian/plugins/infio-copilot/data.json` | SiliconFlow `sk-<已打码>...` | `siliconflowProvider.apiKey` | Obsidian 插件配置文件存了真实 key |

> [!IMPORTANT] 深层根因
> 备份时<span style="color:#e74c3c">没有做密钥消毒</span>，把「笔记里的真实密钥」「插件配置里的真实 key」「会话缓存」一并<span style="color:#ff8c00">打进了快照</span>。其中 `.claudian/sessions/` 是<span style="color:#e74c3c">会话缓存目录，历史备份（如 0817）从不包含它</span>——本次误纳入，正是 Stripe 密钥的来处。

### ② 流程层（伴生根因）：快照树双层嵌套

- 本次备份用 **blobless partial clone + 临时索引**（`GIT_INDEX_FILE=.git/idx_snapshot git add "积昌的知识库0823/"`）暂存快照。
- 暂存出的树变成了 `积昌的知识库0823/积昌的知识库0823/...`，而磁盘目录是平铺的——<span style="color:#ff8c00">「磁盘结构正确 ≠ git 树正确」</span>。
- 此 bug 未被早期"文件数=1695"的验证发现（嵌套后文件总数不变），直到推送被拒、按报错路径回查才暴露。

### ③ 环境层（伴生根因）：Windows 目录占用删除失败

- `.temp_repo` 内含 git 对象库，推送后仍有进程句柄占用。
- git-bash 的 `rm -rf` 走 POSIX 语义，遇到被占用目录报 `Device or resource busy`；
- PowerShell `Remove-Item` 走 Windows API 删除，能绕过该占用完成删除。

## 🔬 诊断数据

| 诊断项 | 数据 |
|--------|------|
| 触发命令 | `git push origin main`（在 `.temp_repo` 内） |
| 远端返回码 | `[remote rejected] main -> main` |
| 扫描到的密钥 | DeepSeek、Stripe（GitHub 命中）；ApiZero、SiliconFlow（人工 grep 补查命中） |
| 被拒提交 | `a3626df0edc814c99fc600c8e4cbca31f71d5076` |
| 原始 main（被拒提交的父） | `7a3b7ed309598a5bcedbcf44f764dec0b2c5248a`（2026-08-17 备份） |
| 修复后提交 | `b994cfa058c40d52fb99c511cdd0b71e6126220f`（知识库备份 2026-08-23） |
| 修复后 main 树 | `4715fbd95fbd5badaaa4dc186e6069cee7f07f9e` |
| 快照顶层项 | `.claude` / `.claudian` / `.obsidian` / `AGENTS.md` / `CLAUDE.md` / `总结好的大纲以及笔记` / `自动维护知识库`（7 项，平铺） |
| 大文件警告 | 68.07 MB（>50 MB 推荐上限，<100 MB 硬上限，仅警告） |
| 密钥复查范围 | 全快照 grep `sk-[A-Za-z0-9]{16,}` / `sk_live_` / `sk_test_` → 修复后无命中 |

> [!NOTE] <span style="color:#e74c3c">为什么"被拒提交不能留作父提交"</span>
> Git 推送会把**新提交的所有祖先对象**一并上传。若修复提交以 `a3626df` 为父，即使新提交本身已消毒，`a3626df` 里的密钥 blob 仍会作为祖先被推送到远端，再次触发扫描。因此必须**重挂父提交到 `7a3b7ed`**，让 `a3626df` 变成不可达（孤儿提交），推送时即被排除。

## 🛠️ 修复过程

### 1. 备份（已执行）

- 台账备份：`总结好的大纲以及笔记/知识库FAQ/原始文件备份/00-报错统计台账-20260823-before-edit.md`
- 快照为临时产物（`.temp_repo`），修复后整体删除，无原件丢失风险。

### 2. 密钥打码（3 个文件 5 处）

| 文件 | 替换前 | 替换后 |
|------|--------|--------|
| `本地部署短视频分析程序介绍文档.md`（表格 + `.env`） | `sk_test_<已打码>...`（×2） | `sk_test_<已打码>` |
| 同上 | `sk-<已打码>...`（×2） | `sk-<已打码>` |
| `自动维护知识库/.obsidian/plugins/infio-copilot/data.json` | `sk-<已打码>...`（×1） | `sk-<已打码>` |

> ⚠️ 打码值里使用 `<已打码>` 占位，保留文件结构与字段名，不影响文档阅读；<span style="color:#e74c3c">**不要在 FAQ 文档里回填真实密钥原文**</span>。

### 3. 移除会话缓存目录

删除快照中的 `.claudian/sessions/`，使 `.claudian/` 仅保留 `claudian-settings.json`（与历史备份 0817 完全一致）。

### 4. git plumbing 重建树（修正嵌套 + 应用打码）

不重新 `git add` 全部 1695 文件，而是用底层对象命令做**外科手术式重建**：

```bash
# ① 把已打码文件写入对象库
NEW_MD=$(git hash-object -w "$SNAP/总结好的大纲以及笔记/.../本地部署短视频分析程序介绍文档.md")
NEW_JSON=$(git hash-object -w "$SNAP/自动维护知识库/.../infio-copilot/data.json")

# ② 沿目录链逐层重建 tree（mktree），替换对应 blob/tree 条目
#    总结好的大纲以及笔记/实习就业/全自动爬取短视频、推文爆款程序 → T3_new → T2_new → T1_new
#    自动维护知识库/.obsidian/plugins/infio-copilot → A3_new → A2_new → A1_new → A0_new

# ③ 重建 .claudian 树（去掉 sessions）：CL_new = 仅 claudian-settings.json
# ④ 重建快照树：从内层正确树 INNER 出发，替换 3 个顶层条目
# ⑤ 重建根树：替换 积昌的知识库0823 条目 → ROOT_new=4715fbd9
# ⑥ 提交
NEW_COMMIT=$(git commit-tree "$ROOT_new" -p "$ORIG" -m "知识库备份 2026-08-23")
git update-ref refs/heads/main "$NEW_COMMIT"
```

关键点：`INNER` 取被拒提交里"内层那棵正确树"（含 7 项平铺内容）作为基底，只改 3 处（`.claudian`、`总结好的大纲以及笔记`、`自动维护知识库`），即可一步修正嵌套。

### 5. 重挂父提交（跳过被拒提交）

```bash
ORIG=$(git rev-parse a3626df^)          # 7a3b7ed（原 main）
NEW2=$(git commit-tree 4715fbd9... -p "$ORIG" -m "知识库备份 2026-08-23")
git update-ref refs/heads/main "$NEW2"  # main → b994cfa
```

### 6. 重新推送 + 收尾

```bash
git push origin main        # 成功：7a3b7ed..b994cfa main -> main
# 更新 .last-github-backup 为 2026-08-23
# 删除临时目录：git-bash rm 报 Device busy → PowerShell Remove-Item -Recurse -Force 成功
```

## 🧰 技术栈与术语

| 项目 | 说明 |
|------|------|
| git | 2.54.0.windows.1；`core.longpaths=true`、`core.autocrlf=false`、`core.safecrlf=false` |
| 克隆方式 | blobless partial clone：`git clone --filter=blob:none --no-checkout`（只拉 commits+trees，不拉历史 blob，避免 1GB+ 全量下载） |
| 暂存方式 | 临时索引：`GIT_INDEX_FILE=.git/idx_snapshot git add "积昌的知识库0823/"`（避免刷新旧索引条目卡死） |
| git plumbing | `hash-object -w` / `ls-tree` / `mktree` / `commit-tree` / `update-ref` / `write-tree` |
| GitHub 侧 | Secret Scanning + 推送保护（push protection）、GH001 大文件警告、GH013 规则违规拒绝 |
| 凭据 | Git Credential Manager（`credential.helper=manager`） |
| 网络 | 本地 HTTP 代理 `127.0.0.1:7897` 转发 git 流量 |
| 术语 | **Secret Scanning**=GitHub 对提交内容的密钥扫描；**push protection**=命中即拒绝推送的规则；**GH013**=仓库规则违规拒绝码；**GH001**=大文件提示码 |

## 🧱 排查中遇到的问题

1. **嵌套目录 bug 逃过"文件数验证"**：早期用 `git ls-tree -r | wc -l` 验证"1695 个文件"，数量正确但**没检查路径层级**，嵌套问题被漏过。教训：验证快照要同时看**顶层结构**（`git ls-tree` 非递归）与文件数。
2. **被拒提交留在祖先链上会"复活"密钥**：初次修复提交以被拒提交为父，一旦推送，密钥 blob 随祖先对象上传 → 又被拦。必须**重挂父**跳过。
3. **git-bash 删不掉被占用目录**：`rm -rf` 报 `Device or resource busy`；PowerShell `Remove-Item -Recurse -Force` 可删。这是 Windows 下常见坑。
4. **密钥藏在"不起眼"的文件里**：`.claudian/sessions/*.meta.json`（会话缓存）、`infio-copilot/data.json`（插件配置）都是易被忽略的藏密钥点，仅靠肉眼检查会漏。
5. **临时索引 + 中文长路径组合**：`git add` 首次在 partial clone 上会卡死（刷新旧索引条目 + CRLF 转换 + 长路径），须用临时索引 + `core.autocrlf=false` + `core.longpaths=true` 组合规避。

## ✅ 验证结果

- ✅ **提交内已消毒**：`git show b994cfa:...本地部署短视频分析程序介绍文档.md` 中仅剩 `sk_test_<已打码>` / `sk-<已打码>`；`git show b994cfa:...infio-copilot/data.json` 中 `apiKey` 为 `sk-<已打码>`。
- ✅ **无会话缓存**：`git ls-tree -r b994cfa -- 积昌的知识库0823/.claudian/` 仅 `claudian-settings.json`。
- ✅ **全快照密钥复查干净**：grep 5 类密钥模式（含 4 组真实 key 的完整值）无命中。
- ✅ **推送成功**：<span style="color:#1e90ff">`7a3b7ed..b994cfa main -> main`，退出码 0</span>。
- ✅ **远端 API 复核**：main=`b994cfa`；`积昌的知识库0823/` 平铺 7 个顶层项；`.claudian/` 仅 settings。
- ✅ **收尾**：`.last-github-backup`=2026-08-23；`.temp_repo` 已删除；远端共 6 个快照（0801/0802/0803/0804/0817/0823），未超 10 个无需清理。

## 🛡️ 使用建议与遗留事项

1. **备份打包前做密钥扫描**（新增固定动作）：打包快照后、`git add` 前，先跑
   `grep -rIln -E "sk-[A-Za-z0-9]{16,}|sk_live_|sk_test_[A-Za-z0-9]{16,}" <快照目录>`
   命中即先打码，再进暂存。
2. **快照排除 `.claudian/sessions/`**：会话缓存属临时/敏感产物，历史备份模式即不含它，应列入排除清单（与 `.git`、`.venv`、`node_modules`、`__pycache__` 并列）。
3. **被拦截后的正确姿势**：修复提交<span style="color:#e74c3c">**不要以被拒提交为父**</span>（否则密钥随祖先仍被推送），用 `git rev-parse 被拒提交^` 找到原 main 重挂父。
4. **验证快照结构**：推送前用非递归 `git ls-tree <提交> -- 积昌的知识库<MMDD>/` 确认顶层平铺，别只看文件数。
5. **大文件 68.07 MB 遗留**：已超过 GitHub 50 MB 推荐上限（未超 100 MB 硬上限，仅警告）。后续若继续增长，建议将该附件纳入 **Git LFS** 管理，或考虑裁剪。
6. **Windows 删除被占用目录**：git-bash `rm -rf` 报 `Device or resource busy` 时，改用 PowerShell `Remove-Item -LiteralPath '<路径>' -Recurse -Force`。
7. **长期密钥卫生**：笔记/配置里不再存真实 key；确需记录时用 `<已打码>` 占位 + 单独保管（如密码管理器）。

## 🔁 复发记录（2026-08-28）：增量备份脚本推送再被 Secret Scanning 拦截

> 2026-08-28 新增量备份脚本 `kb-github-backup.sh` 首次建立单一目录 `积昌的知识库` 基准时，`git push` **再次被推送保护拒绝**。与 08-23 **同根因**：备份范围重新纳入了含真实密钥的文件。本次修复改为**备份脚本自动排除**（从源头杜绝），而非事后打码。

### 报错概况（原文关键行）

```text
remote: - Push cannot contain secrets
remote:   —— DeepSeek API Key ——————————————————————
remote:    - commit: 35c7a7828c899fa34dac556956ce491ec5d50515
remote:      path: 积昌的知识库/总结好的大纲以及笔记/实习就业/创业黑马——数智科技部门/全自动爬取短视频、推文爆款程序/本地部署短视频分析程序介绍文档.md:389
remote:   —— Stripe API Key ———————————————————————
remote:    - commit: 35c7a7828c899fa34dac556956ce491ec5d50515
remote:      path: 积昌的知识库/.claudian/sessions/conv-1786522127698-otv1njux8.meta.json:436,4613,5227
 ! [remote rejected] main -> main (push declined due to repository rule violations)
```

### 与 08-23 的差异点

| 差异点 | 08-23 | 08-28 |
|--------|-------|-------|
| 备份机制 | 手动打包日期快照 | 增量备份脚本 robocopy 同步到单一目录 |
| 含密钥文件 | 笔记 + 会话缓存 + 插件配置 | 笔记(DeepSeek/ApiZero) + `.claudian/sessions/`(Stripe) + `infio-copilot/data.json`(多套 LLM key) |
| 处理方式 | 打码 + git plumbing 重建树 + 重挂父 | **脚本排除表**（`ROBO_EXTRA`/`CLEANUP`）自动剔除 + 撤销被拒提交重跑 |

### 修复过程

1. **GBK 编码崩溃**：脚本 Python 打印 `✔`/`❌` 在 GBK stdout 下抛 `UnicodeEncodeError` → 调用处加 `PYTHONUTF8=1` 强制 UTF-8。
2. **新增排除**：`.claudian/sessions/`（robocopy `/XD sessions` + 清理残留）、含 DeepSeek/ApiZero 密钥的笔记、`infio-copilot/data.json`（同步后强制删除）。
3. **撤销被拒提交**：`git reset --mixed HEAD~1` 回到干净提交 `11dbeef`，重跑脚本。
4. **网络抖动容错**：`git pull`/`git push` 包 `retry` 函数（最多 4 次、间隔 3s），应对瞬时 SSL/TLS 握手失败。

### 验证结果

- ✅ 推送成功：`11dbeef..2204dc0 main -> main`，退出码 0。
- ✅ 远端树确认无 `.claudian/sessions/`、无 DeepSeek 笔记、无 `infio-copilot/data.json`。
- ✅ 根目录仅单一 `积昌的知识库`；`.last-github-backup`=2026-08-28。

## 🔗 相关文件与附件

- 台账：[[00-报错统计台账]]（F12/F13/F14 已登记，F12 累计 2 次）
- 被拒提交：`a3626df0edc814c99fc600c8e4cbca31f71d5076`（孤儿，未推送）
- 修复提交：`b994cfa058c40d52fb99c511cdd0b71e6126220f`（main）
- 台账备份：`总结好的大纲以及笔记/知识库FAQ/原始文件备份/00-报错统计台账-20260823-before-edit.md`
- 远程仓库：`https://github.com/xieji-star/jichang-zhishiku`
- 历史参考：[[01-Obsidian反复报错Request too large]]（同为"推送/文件内容"类排查思路）；[[07-报告frontmatter标签YAML注释符报错]]（同为"内容层校验"类案例）
