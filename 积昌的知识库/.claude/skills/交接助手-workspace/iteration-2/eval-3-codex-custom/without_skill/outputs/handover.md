---
title: "短视频爆款采集系统 → Codex 续作交接单"
type: 交接文档
date: 2026-08-17
recipient: Codex
project: 全自动爬取短视频、推文爆款程序
root: "D:\\全自动爬取短视频、推文爆款程序"
status: 0817 速度优化批已完成，按「待办清单」续作
---

# 短视频爆款采集系统 → Codex 续作交接单

> 给 Codex 的第一句话：这是上一任（DeepSeek 驱动）在 2026-08-09 ~ 08-17 期间做出来的抖音爆款采集系统，停在第 0817 批（速度优化 + 云端 BUG 修复）刚交付的状态。**你的任务是先花 3 分钟把下面「A. 先执行，别信文档」跑完，确认我还活着、跑在预期状态，然后挑「待办清单」里优先级 1 的事开工。** 所有关键结论都给了可验证命令——跑出来的输出才算数。

---

## 0. 项目是什么（一句话）

本地部署 + 云端应急的**抖音短视频爆款采集/评分/口播稿系统**：MediaCrawler 三模式采集 → S/A/B/C 评分 → GPU ASR 转口播稿 → SQLite 落库 → 飞书唯一出口，服务 13 个矩阵账号的选题与竞品分析。全月成本约 ¥0.5。

---

## A. 先执行，别信文档（3 分钟自检）

这些命令的输出决定你后续往哪走。**结果与文档不符就以实际为准**，回来改本文件。

```powershell
# 1. 项目根目录在不在（生产在 D 盘；旧文档里 E:\ 是早期 MediaCrawler 原始位置，已迁）
dir "D:\全自动爬取短视频、推文爆款程序"

# 2. 关键子目录
dir "D:\全自动爬取短视频、推文爆款程序\backend"
dir "D:\全自动爬取短视频、推文爆款程序\MediaCrawler"

# 3. backend 服务活着吗（端口 8000）
curl.exe -s http://127.0.0.1:8000/api/health

# 4. 风控开关现状（应见 CIRCUIT_BREAKER=true / CURL_CFFI=true / STAGGER=true / PROXY=false / NOPECHA=false / BROWSER_ROUTE=patchright）
curl.exe -s http://127.0.0.1:8000/api/risk-control/health

# 5. 当前采集并发档位（应为 1 = 串行）
# 查 .env.local 里 MEDIACRAWLER_CONCURRENT_ACCOUNTS 的值
findstr CONCURRENT "D:\全自动爬取短视频、推文爆款程序\.env.local"
```

自检通过标准：① `dir` 能列出 backend/MediaCrawler；② `/api/health` 返回 200 与 status=ok；③ `/api/risk-control/health` 与下方「风险组件状态表」一致；④ `.env.local` 存在。任一项对不上，先停下来修到一致再继续。

---

## B. 系统地图（谁在哪个端口、代码在哪）

```
D:\全自动爬取短视频、推文爆款程序\
├── start.ps1                     ← 唯一启动入口（守卫旧目录/端口/Edge 窗口卫生）
├── .env.local                    ← 全部运行配置（改这里，别改 config.py 默认值）
├── backend\
│   └── app\
│       ├── main.py               ← FastAPI，/api/*，含 /api/risk-control/health
│       ├── config.py             ← 配置定义（env 可覆盖）
│       ├── risk_control.py       ← 熔断器/curl_cffi/错峰/代理预检/证据截图
│       ├── services\
│       │   ├── collection.py     ← 采集-转录流水线（批线程、账号循环、错峰、熔断）
│       │   ├── sync.py           ← 飞书云端同步（runtime_settings 持久化降噪）
│       │   └── multi_account\
│       │       ├── runner.py     ← 并发池调度（ThreadPoolExecutor）
│       │       └── edge_cleanup.py ← Edge 窗口三层清理（账号/hook/任务级）
│       └── providers\mediacrawler.py ← fork 对接（media_kind 判定、子进程 env 透传）
├── MediaCrawler\                 ← 开源 fork（多账号 4 个 env 注入 + 8 处 isabs 修复 + 二维码弹图根治）
└── _asr_8765.py                  ← GPU ASR 转录服务（同步 endpoint，超时 240s，vad_filter）
```

| 服务 | 端口 | 说明 | 健康检查 |
|------|:----:|------|---------|
| backend（FastAPI） | 8000 | 主 API | `curl.exe -s http://127.0.0.1:8000/api/health` |
| GPU ASR（_asr_8765） | 8765 | 口播稿转录 | 见 backend 日志 `transcription.result` |
| Evil0ctal 下载兜底 API | 18081 | route2 三 provider 之一 | 未启动时转录走 f2/yt-dlp 会变慢 |
| 妙搭 dev:server / dev:client | 3100 / 3000 | 唯一前端 | 浏览器开 `http://localhost:3000/app/app_17bkk0a8pt8/client/index.html#/` |
| MediaCrawler CDP | 9222 | 单账号共享登录态（串行档） | 多账号并发时为每账号独立端口 |

> 前端是**妙搭应用**，旧 vinext 前端已物理删除（780M）。`start.ps1` 守卫：旧目录重现自动清除 + 3000 端口非妙搭进程自动清退。

---

## C. 当前状态（截至 0817 批，全部已交付）

### 已完成且验收过（十轮/五轮实测 100% 的项目）

| 能力 | 状态 | 实证 |
|------|:----:|------|
| 10 轮采集+口播稿批测（0815） | ✅ | 视频 200/200，修正口径口播稿 6-10 轮连续 100%，均耗 3.9min→2.3min |
| 风控组件接入生产（0815） | ✅ | 成功率 76%→100%（argus=1 仍 20/20），248 测试全绿 |
| 多账号并发池 + 图文跳过 + 缺链接优雅跳过（0816） | ✅ | 5 轮 100%，全量回归 264 passed |
| Edge 一次登录克隆（0816） | ✅ | 25/25 账号目录克隆成功 |
| 对抗组件投产（0816 用户决策，风险自担） | ✅ | 十轮终审零账号封锁，详见下方风险组件表 |
| 速度优化批（0817） | ✅ | 转录线 4→6、错峰 15-30s、采集-转录流水线、VAD 提速 30-50% |
| 云端 BUG 修复（0817） | ✅ | 达人选择优先级修复，已部署妙搭 commit b0aff55 |

### 关键环境变量现状（`.env.local`，2026-08-17）

| 变量 | 当前值 | 含义 |
|------|--------|------|
| `RUN_MODE` | `local` | local=本地主力 / cloud=云端应急 |
| `COLLECTION_PROVIDER` | `mediacrawler` | 采集提供方 |
| `MEDIACRAWLER_CONCURRENT_ACCOUNTS` | `1` | **串行**（单账号共享登录态免扫码） |
| `RISK_STAGGER_MIN_SECONDS` / `MAX_SECONDS` | `15` / `30` | 错峰收窄（原 20-60s） |
| `COLLECTION_TRANSCRIPT_WORKERS` | `6` | 转录并行工作线（原 4） |
| `EVIL0CTAL_API_BASE_URL` | `http://127.0.0.1:18081` | 下载兜底 provider |
| `SUBTITLE_DIRECT_ENABLED` | `false` | 字幕直取**默认关**（未灰度） |
| `RISK_PROXY_ENABLED` | `false` | 代理池已停（缺 HTTPS 代理源，源码保留） |
| `RISK_NOPECHA_ENABLED` | `false` | NopeCHA 已卸载 |
| `MEDIACRAWLER_SKIP_QRCODE_DISPLAY` | `true` | 二维码弹图根治 |
| `MEDIACRAWLER_BROWSER_DATA_DIR` | 项目内 D 盘路径 | 默认值已从 C 盘旧路径改到项目内 |

> ⚠️ 想开**并发多账号**：把 `MEDIACRAWLER_CONCURRENT_ACCOUNTS` 改成 >1，但**抖音会把新 Edge profile 当新设备要求扫码**（平台策略，非项目 BUG）——0816 已实测，克隆 Cookie 不保证免验证。串行模式可全自动免扫码。

### 风控/对抗组件状态（2026-08-16 晚终审定格）

| 组件 | 状态 | 说明 |
|------|:----:|------|
| 熔断器 / curl_cffi / 随机错峰 / 指数退避 / mss 截图 / patchright / CloakBrowser / fingerprintjs | ✅ 投产 | 全部免费且十轮实测零封锁 |
| 代理轮换 / NopeCHA | ❌ 已停 | 缺 HTTPS 代理源 / 无 API Key，2026-08-16 用户决策卸载释放硬盘 |
| nodriver / Botright / haipproxy | ❌ 已删 | 无法稳定投产 |

> 合规背景：2026-08-16 用户明确决策突破原合规红线，对抗组件全部投入使用，风险自担。本项目个人使用，不设红线。**改这些开关前先和用户确认**。

---

## D. 待办清单（接续位置，按优先级排序）

> 接手先做这里。每条都给了「做完怎么算成功」。

### 🔥 P1｜10 轮验收测试重跑（串行模式）

- **背景**：0816 首轮并发模式被抖音新环境验证阻断，串行重跑被用户中途终止。测试脚本已删。
- **做法**：按 `总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\开发日志\0816-多账号并发与Edge登录态.md` 第 7 节重写脚本：每轮随机 10 账号 × 20 视频，`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1` 串行，`video_limit=20`、`content_mode=transcript`、`transcription_mode=all`、`range=all`；轮间冷却 30s，90 分钟/轮上限。
- **每轮循环**：读 `collection_logs` + `error_logs` + `collection_job_items` 失败明细 → 优化 → 备份 → 清数据 → 下一轮。
- **验证通过标准**：10 轮全部 completed，视频成功率 100%，修正口径口播稿成功率 100%。
- **清数据 SQL**（每轮优化后执行，先备份到 `backups/`）：
  ```sql
  DELETE FROM videos; -- 业务库共 9 表：videos/collection_logs/collection_job_items/accounts/account_tasks/error_logs/creator_profile_snapshots/...
  DELETE FROM douyin_aweme; DELETE FROM douyin_aweme_statistics; -- MediaCrawler 侧 2 表
  ```

### 🔥 P2｜抖音号 → sec_uid 自动解析

- **背景**：creator 模式必需 `creator_url`（抖音号 ≠ sec_uid），缺链接账号目前只能跳过。
- **方案（架构 Agent 已设计，未实施）**：fork 侧 search hook（参考 `mediacrawler_profile_hook.py` 的 runpy+monkeypatch 模式），`client.search_info_by_keyword`（USER 频道 `aweme_user_web`，`field.py:28`）→ 响应 `data[].user_list[].user_info` 含 sec_uid/short_id/unique_id → 校验匹配后输出 JSON → 后端 `call_with_policy` 限速 + 三层缓存回填 `accounts.json creator_url`。
- **验证**：未填 creator_url 的账号能自动补齐并成功采集；每账号仅 1 次请求、sec_uid 永久缓存。
- 完成后：collection.py 过滤条件恢复放行 `sec_user_id`。

### 🟡 P3｜字幕直取 Phase 0 实测（覆盖率验证）

- **背景**：已评估**抖音 web 端无字幕数据源**（detail 接口无字幕字段、播放器无字幕请求、分享页无 videoInfoRes，多轮实测）；口播稿现走「下载 + GPU ASR」已闭环 149/150。
- **做法**：fork client 有界采样 300 条 detail，统计 `video.subtitles` 存在率；**≥20% 才投产**。
- **通过标准**：覆盖率报告写清存在率；不达标就维持现状（ASR 已是主路径）。

### 🟡 P4｜字幕直取灰度（若 P3 达标）

- `SUBTITLE_DIRECT_ENABLED` 开 20% → 50% → 100%，每级 3 天，每级检查口播稿正确率不降。

### ⚪ P5｜遗留开放项（可做可不做）

- **proxy_pool HTTPS 代理源**：`RISK_PROXY_ENABLED=true` 需 `RISK_PROXY_POOL_URL` 指向运行中的服务（Redis+代理源），现无 HTTPS 源。
- **clone 脚本自动刷新真实验证**：需要一次「共享重登 → 启动 → 自动克隆」场景。
- **NopeCHA Key**：如要自动打码需重新购买并接线（当前已卸载）。
- **抖音 APP 签名直取（X-Gorgon）**：开源项目 douyin-sign / TikTok-Encryption 可支撑，接入为中等工程，**待用户拍板**。

---

## E. 踩坑记录（改代码前必读，全是血泪）

1. **start.ps1 编码**：PowerShell 5.1 按 GBK 解析无 BOM UTF-8——脚本内中文注释会被误读导致语法错误。**新加逻辑用纯 ASCII，注释不要写中文。**
2. **MediaCrawler fork 的 `%` 格式化**：`USER_DATA_DIR % config.PLATFORM` 在注入**绝对路径**时必崩（`TypeError: not all arguments converted`）——8 处已统一 isabs 守卫。**以后往 fork 里加 `%` 格式化路径，先判断 isabs。**
3. **图文笔记假成功**：`aweme_type=163` 图文无音频，硬转录会把 BGM 歌词当口播稿（历史假成功教训）。判 `media_kind=image_text` 后**跳过转录记日志**，正确率按「可转录视频数」统计。**宁可真失败，不要假成功。**
4. **backend 8000 端口来源混淆**：偶发 Anaconda python 实例在跑（有守护进程），功能一致但排查时注意解释器来源；**生产应跑项目 `.venv` + 从 `.env.local` 加载**。
5. **Edge 新设备验证**：新 profile 克隆 Cookie 后抖音仍可能要求扫码——平台策略，非 BUG。多账号自动化的现实路径是串行（共享登录态）。
6. **转录超时根因**：8765 事件循环阻塞 → `_asr_8765.py` 已改同步 endpoint + 240s 超时。**转录出 timed out 先查 8765 是否在跑、是否阻塞。**
7. **字幕直取结论**：抖音 web 端无字幕数据源，别再花时间找 web 端字幕字段；要做就做 APP 签名直取（待拍板）。

---

## F. 参考资料（都在知识库，读原始日志比问用户快）

| 主题 | 路径 |
|------|------|
| 主开发日志 0809 | `F:\积昌的知识库 - 副本\总结好的大纲以及笔记\实习就业\全自动爬取短视频、推文爆款程序\开发日志\0809-爬虫开发日志.md` |
| 0816 多账号/Edge/字幕直取（含交接清单第 8 节） | `...\开发日志\0816-多账号并发与Edge登录态.md` |
| 0817 速度优化批 | `...\开发日志\0817-速度优化批与云端修复.md` |
| 10 轮批测报告（清数据 SQL/口径） | `...\开发日志\0815-项目测试.md` |
| 风控组件生产接线 | `...\开发日志\0815-风控组件接入生产.md` |
| 对抗组件终审/卸载记录 | `...\开发日志\0816-对抗组件全面启用.md` |
| 缺链接/% 格式化修复 | `...\报错修复日志\0815-多账号采集与缺链接报错修复.md` |
| 方案总览（改良版） | `...\本地部署短视频分析程序介绍文档（改良版）.md` |
| 并发池设计蓝图 | `...\MediaCrawler深度分析与结合改进方案.md`（及 wiki 页 `自动维护知识库\wiki\自媒体运营\短视频爆款采集系统.md`） |

> 规则：知识库的 `已整理好的文件` 只读，`自动维护知识库` 可自由改。参考日志只读，别改。

---

## G. 给你的第一条开工指令（Codex 上手动作）

1. 先跑「A. 先执行，别信文档」自检，把结果贴给用户确认基线。
2. 读一次 `D:\全自动爬取短视频、推文爆款程序\start.ps1` 和 `.env.local`，确认启动链路与上面表格一致。
3. 确认无异议后，从 **P1（10 轮验收测试重跑）** 开工——先按 0816 日志第 7 节重写测试脚本，跑第一轮串行验收，把结果与「通过标准」对照。
4. 每完成一条待办，回来更新本文件的状态标记，并向用户汇报「做了啥 / 怎么验证的 / 下一件做什么」。

> 交接人：上一任 AI（DeepSeek 驱动）。有什么对不上的，先执行、再改文档、再动手——**输出比文档更可信。**
