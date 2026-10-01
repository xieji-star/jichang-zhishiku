---
title: "知识库 GitHub 备份脚本 git pull 失败（代理端口写死 4780，实际漂移到 7897）"
type: "知识库 FAQ / 报错记录"
date: 2026-09-28
created: 2026-09-28
updated: 2026-09-28
tags:
  - 报错
  - 知识库FAQ
  - GitHub备份
  - 代理
  - 端口漂移
  - Git
  - 脚本
  - Vortex
  - mihomo
source: "知识库增量备份脚本 .claude/hooks/kb-github-backup.sh；触发任务：2026-09-28（周一）hook 到期的 GitHub 增量上传"
---

# 🧩 知识库 GitHub 备份脚本 git pull 失败（代理端口写死 4780，实际漂移到 7897）

> [!summary] 📊 报错统计速览（截至 2026-09-28）
> 🔥 **本文档共记录 <span style="color:#e74c3c">1 次报错事件</span>**（2026-09-28 首发 1 次，暂无复发记录）。根因为 **「备份脚本把代理端口**写死**成 `4780`，而本机代理（Vortex / mihomo 内核）的实际 mixed 端口已漂移到 `7897`，导致脚本内 git 经一个死端口连 GitHub 而失败」**，属**环境层（代理端口配置与运行态脱节）**问题，非 GitHub 或网络故障。
>
> | 根因 | 台账累计 | 主要发生地 |
> |------|:---:|------|
> | 📊 备份脚本代理端口写死（GIT_PROXY 4780 → 实际 7897） | **1** | 25 |
>
> 📊 完整统计口径见 [[00-报错统计台账]]。

## 🧭 快速索引

- 🧾 [[#错误信息|错误信息]]
- ⚠️ [[#现象描述|现象描述]]
- 🔍 [[#根本原因（三层诊断）|根本原因（三层诊断）]]
- 📊 [[#诊断数据|诊断数据]]
- 🛠️ [[#修复过程|修复过程]]
- 📽️ [[#技术栈与涉及工具|技术栈与涉及工具]]
- 🕳️ [[#遇到的问题与坑|遇到的问题与坑]]
- ✅ [[#验证结果|验证结果]]
- 📌 [[#使用建议与遗留事项|使用建议与遗留事项]]

## 错误信息

```
=== [2/5] git pull 拉取远端最新 ===
fatal: unable to access 'https://github.com/xieji-star/jichang-zhishiku.git/':
Failed to connect to github.com port 443 via 127.0.0.1 after 2086 ms: Could not connect to server
  ⏳ 网络重试第 1 次: git -C F:/jichang-backup pull --quiet
  ⏳ 网络重试第 2 次: git -C F:/jichang-backup pull --quiet
  ⏳ 网络重试第 3 次: git -C F:/jichang-backup pull --quiet
❌ git pull 失败
```

> **出现时间**：2026-09-28（周一，hook 到期触发 GitHub 增量上传时）
> **来源**：知识库增量备份脚本 <span style="color:#e67e22">**`.claude/hooks/kb-github-backup.sh`**</span>。
> **触发场景**：执行 `bash .claude/hooks/kb-github-backup.sh`，在第 2 步 `git pull` 时连报 4 次失败（含 3 次重试）后中止。

## 现象描述

脚本前两步一切正常——镜像仓库 `F:/jichang-backup` 存在、进入目录成功——但在第 2 步 `git pull` 时，**每一次都报同一句**：

<span style="color:#e74c3c">**`Failed to connect to github.com port 443 via 127.0.0.1 ... Could not connect to server`**</span>

其关键特征：

- 报错文案里出现了 <span style="color:#e67e22">**`via 127.0.0.1`**</span>——说明 git **确实在走本机代理**（脚本里 `export http_proxy/https_proxy` 生效了），而不是直连被墙；
- 但**走代理仍连不上**——说明"走"的那个代理端口上**没有服务**（端口是死的）；
- 脚本的 `retry()`（最多 4 次、间隔 3s）**全部失败**——不是网络抖动，是**持续性的端口错误**。

> 💡 **<span style="color:#2980b9">认知：</span>** 出现 `via 127.0.0.1` + 重试全败，基本可判定为**"代理端口对不上"**，而非"梯子关了"或"GitHub 挂了"。下一步只需回答一个问题：**脚本走的端口，和代理真正监听的端口，是不是同一个？**

## 根本原因（三层诊断）

按报错修复 skill 的三层法逐层排查，根因落在**第②层环境层（且属"配置写死 + 运行态漂移"型）**：

### ① 文件层（报错对象本身）——正常 ✅

- 脚本第 20~23 行 `VAULT`/`BACKUP_DIR`/`TARGET`/`REPO_URL` 全部解析正常，`F:/jichang-backup/.git` 存在；
- 第 1 步"确保镜像仓库"通过（镜像仓库已存在，无需克隆）；
- 报错发生在 git 访问网络这一步，**与备份范围、文件内容无关**。

### ② 环境层（机器依赖）——**根因所在** ❌

- 脚本第 34 行把代理端口**写死**为 **`4780`**：
  ```bash
  GIT_PROXY="${KB_GIT_PROXY:-http://127.0.0.1:4780}"
  ```
- 而本机代理（**Vortex / mihomo 内核**）的 mixed 端口实际监听在 <span style="color:#e74c3c">**`7897`**</span>（`netstat` 确认 `0.0.0.0:7897 LISTENING`，PID 24968）；
- 端口 **`4780` 上无任何服务**（历史用过，客户端升级/重装后已漂移走）——脚本内的 git 于是**死磕一个不存在的端口**，必然连不上；
- 这也解释了脚本注释里那句预警：<span style="color:#e67e22">**"代理端口会随客户端升级/重装漂移（历史用过 4780）"**</span>——本次正是踩了这句注释预言的老坑。

### ③ 工具/会话层（当前会话能力）——正常 ✅

- git 可用、镜像仓库完好；
- 本机**直连** GitHub 亦可达（curl 直连 `github.com` 返回 200），说明**网络与梯子本身没问题**——纯粹是脚本端口写死造成的"单点配置错误"。

### 故障链条

1. 代理客户端升级/重装 → mixed 端口从 `4780` 漂移到 `7897`；
2. 备份脚本 `GIT_PROXY` 仍写死 `4780`（默认值，未设 `KB_GIT_PROXY` 覆盖）；
3. 脚本 `export http_proxy=http://127.0.0.1:4780` → 内层 git 经**死端口**出网；
4. `git pull` 连报 `Failed to connect ... via 127.0.0.1` → `retry()` 4 次全败 → 脚本 `exit 1` 中止。

## 诊断数据

**① 端口监听与连通性（核心证据）**：

| 检查项 | 命令 | 结果 | 判读 |
|---|---|---|---|
| 监听端口 | `netstat -ano \| findstr LISTENING` | <span style="color:#e67e22">**`0.0.0.0:7897` LISTENING（PID 24968）**</span> | 代理实际在 7897 |
| 4780 是否存活 | 探测 `127.0.0.1:4780` | ❌ **无服务（死端口）** | 脚本走的就是这里 |
| 经 7897 连 GitHub | `curl -x http://127.0.0.1:7897 https://github.com` | ✅ **200** | 正确端口可达 |
| 直连 GitHub | `curl https://github.com` | ✅ 200（约 1.4s） | 网络/梯子本身无恙 |

**② 脚本内代理设置（`kb-github-backup.sh`）**：

| 位置 | 修复前 | 修复后 |
|---|---|---|
| 第 27~31 行（注释） | 提到"历史用过 4780"，未点明现用端口 | 更新为 <span style="color:#2980b9">**"Vortex / mihomo 内核 mixed 端口 7897"**</span> + 漂移预警 |
| 第 34 行（默认值） | `http://127.0.0.1:`<span style="color:#e74c3c">**`4780`**</span> | `http://127.0.0.1:`<span style="color:#e67e22">**`7897`**</span> |

> 🔍 **<span style="color:#e74c3c">与历史报错的区分：</span>** 台账里的 **N16**（机场订阅到期，2026-09-18）也表现为备份脚本 `git pull` 失败，但那是**代理节点被清空**（`proxies: 0`），属"节点全没"；本次是**端口对不上**（节点/网络都正常），根因不同、处置不同——**排查时应先做 `netstat` 端口比对 + `curl -x <端口>` 连通性测试，两条证据即可分流二者。**

## 修复过程

### 第 1 步：定位（三层诊断）

发现报错含 `via 127.0.0.1` → 判定"走代理但端口死" → `netstat` 查出实际端口 **7897** → 对比脚本写死的 **4780** → 锁定根因。

### 第 2 步：改脚本默认端口（一次性根治）

编辑 `.claude/hooks/kb-github-backup.sh`，把默认代理端口从 `4780` 改为 `7897`，并补注释说明现用端口与漂移预警：

```bash
# 修复前
GIT_PROXY="${KB_GIT_PROXY:-http://127.0.0.1:4780}"

# 修复后
GIT_PROXY="${KB_GIT_PROXY:-http://127.0.0.1:7897}"
```

> 💡 脚本仍保留 `KB_GIT_PROXY` 覆盖机制——**日后端口再漂移，无需改脚本**，临时执行 `KB_GIT_PROXY=http://127.0.0.1:<新端口> bash .claude/hooks/kb-github-backup.sh` 即可。

### 第 3 步：验证连通性

```bash
netstat -ano | findstr LISTENING | findstr :7897      # → 0.0.0.0:7897 LISTENING
curl -s -o /dev/null -w "%{http_code}" --max-time 8 \
  -x http://127.0.0.1:7897 https://github.com         # → 200
```

两条均通过，端口修复有效。

## 技术栈与涉及工具

- **知识库增量备份脚本**（`.claude/hooks/kb-github-backup.sh`）：`git pull` → `robocopy` 增量同步 → `git add/commit/push`；
- **Vortex / mihomo**（本机代理客户端与内核）：mixed 端口承担 HTTP/S 代理，端口随版本漂移；
- **git + libcurl**：脚本用 `http_proxy`/`https_proxy` 环境变量让 git 走代理（只对脚本内 git 生效，不改任何 git config）；
- **Windows netstat / curl**：端口监听与代理连通性诊断。

## 遇到的问题与坑

- 🕳️ **<span style="color:#e74c3c">"写死端口"是复发型隐患：</span>** 端口本是**运行态**（随客户端升级/重装漂移），却被**写进脚本默认值**，注定"今天好、哪天客户端一升级就坏"。脚本注释其实早已预警，本次正是预警应验；
- 🕳️ **<span style="color:#e67e22">报错文案会"甩锅"：</span>** `Failed to connect ... via 127.0.0.1` 容易被误读成"梯子/网络不行"，实则**网络完全正常**，只是脚本走错了端口——**先 `netstat` 比端口，别急着骂网络**；
- 🕳️ **与 N16（订阅到期）形似神不同：** 两者都报 `git pull` 失败，但 N16 是**节点清空**、本次是**端口错**；分流靠"端口比对 + `-x` 连通性测试"两把尺子；
- 🕳️ **端口漂移是长效问题：** 历史已出现 `4780 → 7897` 的漂移（N13/N15 里 Firefox 也曾指向 `4780`）。凡"写死端口"处，日后都要按本档案思路复查。

## 验证结果

- ✅ **端口修复有效**：脚本默认端口已改为 `7897`；`netstat` 确认 `7897` 在听、`curl -x 7897` 连 GitHub 返回 **200**（约 2.99s）；
- ⚠️ **端到端备份本轮未复跑**：执行完整 `bash .claude/hooks/kb-github-backup.sh` 被用户中止（<span style="color:#2980b9">用户明确表示"Github 先不用备份"</span>），故 **pull→同步→commit→push 全链路与 `.last-github-backup` 更新未在本次验证**；
- 📌 **现状**：因未复跑，根目录标记文件 `.last-github-backup` 仍为 `2026-09-09`，镜像仓库 `F:/jichang-backup` 最后一次提交仍为 `9094b68 知识库备份 2026-09-09（增量）`——**待下次用户要求备份时复跑即应通过**。

## 使用建议与遗留事项

- 💡 **<span style="color:#2980b9">遇到同款报错直接照方抓药：</span>** ①`netstat -ano | findstr LISTENING` 找实际 mixed 端口 → ②`curl -x http://127.0.0.1:<端口> https://github.com` 验连通 → ③改脚本默认值或临时 `KB_GIT_PROXY=...` 覆盖；
- 📌 **监测对象**：
  - `.claude/hooks/kb-github-backup.sh` 第 34 行默认端口——**代理客户端一旦升级/重装，优先复查此处**；
  - 同类"写死端口"处：Firefox `user.js`（N13/N15 曾指向 4780）等；
- 📌 **遗留（待用户解锁后执行）**：择机复跑一次 `bash .claude/hooks/kb-github-backup.sh`，确认 `git pull` 通过、推送成功、`.last-github-backup` 更新为当天；
- 📎 **关联对象**：[查看脚本：kb-github-backup.sh](.claude/hooks/kb-github-backup.sh)

## 🔁 后续复跑发现的另两层问题（2026-09-28，待备份恢复时处理）

修复端口后那次重跑**没有再报端口错**（`git pull` 已能连通远端），但**又冒出两个新故障点**——与端口**无关**，属另外的根因，记录于此供日后恢复备份时对照：

```
=== [2/5] git pull 拉取远端最新 ===
fatal: could not write multi-pack-index: Permission denied
error: failed to perform geometric repack
error: task 'geometric-repack' failed
=== [3/5] 增量同步备份范围 ===
  ✔ 同步: .claude / .claudian / .obsidian
  🧹 已排除目录: plugins/drawio/webapp
Traceback (most recent call last):
  File "<stdin>", line 57, in <module>
  ...
PermissionError: [WinError 32] 另一个程序正在使用此文件，进程无法访问。
❌ 同步存在失败项，中止上传
```

| 序 | 故障点 | 现象 | 初判根因 | 待验证 |
|:--:|:---|:---|:---|:---|
| ① | 镜像仓库 git 维护 | `could not write multi-pack-index: Permission denied` / `geometric-repack failed` | `F:/jichang-backup` 的几何 repack 维护任务**写索引被拒**（文件被占/权限/并发 git 进程）——**非网络问题**，`git pull` 本身可能已成功 | 复跑看是否偶发；必要时 `git -C F:/jichang-backup maintenance` 相关配置或手动 repack |
| ② | 同步单文件被占用 | `WinError 32 另一个程序正在使用此文件`（脚本 `shutil.copy2` 第 57 行，即文件项 `CLAUDE.md`/`AGENTS.md` 分支） | <span style="color:#e74c3c">**被同步的单文件正被其它进程打开**</span>（很可能 `CLAUDE.md` 正被本轮 Claude 会话持有） | 复跑时若正开着 `CLAUDE.md` 易复现；可改 `robocopy` 文件分支或避开会话占用时段 |

> 💡 **<span style="color:#2980b9">结论：</span>** 本次备份**三重故障叠加**——①端口写死（已修）、②本地 git 维护被拒、③同步文件被占用。**端口那层确已解决**（复跑未再报 `via 127.0.0.1` 失败）；②③待用户恢复备份时再逐层处理。

## 🔗 相关笔记

- [[00-报错统计台账]] — 报错统计权威源（本档案为 **N19** 行）
- [[22-机场订阅到期导致小火箭节点清空（全站境外无法访问）]] — **同形不同因**：也曾表现为备份脚本 `git pull` 失败，但根因是节点清空（N16）
- [[12-GitHub推送被Secret-Scanning拦截（快照含API密钥）]] — 同属 GitHub 备份链路的报错
- [[21-关闭代理软件后浏览器打不开国内网站（Firefox手动代理残留）]] — 同属"代理端口写死/残留致连不上"类（该档 Firefox 亦指向 4780）
- [[15-校园网Firefox不走代理导致境外无法访问]] — 同属"代理端口 4780"历史用例
