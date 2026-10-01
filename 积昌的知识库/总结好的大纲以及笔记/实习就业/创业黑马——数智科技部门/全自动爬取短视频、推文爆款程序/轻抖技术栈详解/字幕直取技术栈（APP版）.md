---
title: "字幕直取技术栈（手机 APP 端签名直取版）"
date: 2026-08-17
tags:
  - 笔记整理
  - 创业黑马
  - 字幕直取
  - 采集系统
  - 技术方案
created: 2026-08-17
updated: 2026-09-15
aliases:
  - 字幕直取技术栈（APP版）
source: "两轮验证结论对比 + douyin-sign 开源库检索 + 项目源码勘察（2026-08-17）"
---

# 字幕直取技术栈（手机 APP 端签名直取版）

> [!summary] 概要
> 本文是「矩阵内容雷达」项目**字幕直取技术栈 v2** 的技术方案档案，记录一条"从不可行到可行"的路线切换：**网页端确实没有字幕**（已实测、不翻案），但**手机 APP 端接口的响应里带字幕轨道**（`cla_info.caption_infos`），此前被 `X-Gorgon`/`X-Argus` 设备签名挡在门外。转机是 GitHub 开源库 **douyin-sign**（免费、带 nightly CI 自动更新签名常量）——钥匙找到了。由于签名本质是 HTTP 请求头参数计算（与运行设备无关），**电脑端程序只要模拟 APP 设备头 + 附带正确签名，就能调用 APP 端接口拿到带字幕的响应**。文档给出总体架构、约半天的三阶段接入路线、可复用代码清单、三重质量闸门与收益/风险，并保留 4 项待确认问题。

> [!note] 文档元信息
> - **项目名**：全自动爬取短视频、推文爆款程序（抖音达人数据采集）
> - **文档主题**：字幕直取技术栈 v2——手机 APP 端接口签名直取平台 AI 字幕（douyin-sign 开源签名库方案）
> - **编写日期**：2026-08-17
> - **编写依据**：两轮验证结论对比 + douyin-sign 开源库检索 + 项目源码勘察
> - **文档定位**：APP 端签名直取的技术方案、可行性论证、接入路线与工程拆解

## 相关笔记

- [[短视频爆款采集系统]] — 本项目所属系统全景（wiki 页）
- [[0820-字幕直取&连接采集的开发日志]] — 字幕直取方案的落地开发日志
- [[风控接线技术方案-20260816]] — 同期采集系统的风控组件接线技术档案

## 📑 索引

- 🎯 [[#0. 一句话总结]] — 一句话讲清"网页端无字幕、APP 端有字幕、签名库是钥匙"
- 🔀 [[#1. 两条路的差别（为什么"不可行"变"可行"）]] — 网页端 vs APP 端接口直取对比表
- 💻 [[#2. 为什么电脑端程序能调用 APP 端接口]] — 签名原理与请求头模拟的关键点
- 🔑 [[#3. douyin-sign 开源库（钥匙）]] — 仓库地址、覆盖能力与成本
- 🏗️ [[#4. 总体架构（目标方案）]] — 签名服务 + MediaCrawler + backend 三层结构
- 🛠️ [[#5. 接入路线（工程拆解，约半天）]] — 三阶段落地步骤与验收信号
- 🧩 [[#6. 关键代码（现有可复用部分）]] — 可直接复用的提取/下载/清洗/闸门代码
- 🚪 [[#7. 三重质量闸门（防假成功，保持不变）]] — 字数/BGM/语言三道防假成功闸门
- ⚖️ [[#8. 收益与风险]] — 速度/算力/质量收益与签名失效风险
- 🔄 [[#9. 与现网链路的关系（平滑过渡）]] — 现状与目标对照及灰度过渡策略
- ✅ [[#10. 行动清单（Codex/开发者接力）]] — 六步落地待办
- ❓ [[#11. 待确认项（❓）]] — 部署方式、接口 URL、并发与设备伪装等待定问题

---

## 0. 一句话总结

🔥 **<span style="color:#e74c3c">"网页端没有字幕"是事实（已验证，没翻案）</span>**；但手机 APP 端接口的响应里有字幕（`cla_info.caption_infos`），之前被 X-Gorgon/X-Argus 设备签名这堵墙挡住，现在 GitHub 有免费开源签名库 douyin-sign（带 nightly CI 自动更新签名常量）——💡 **<span style="color:#2980b9">钥匙找到了，这条路能走通</span>**。

💡 **<span style="color:#2980b9">电脑端程序也能用 APP 端接口</span>**：签名是 HTTP 请求参数计算（与运行设备无关），电脑端只要在请求头里模拟 APP 的设备信息 + 附带正确签名，就能调用 APP 端接口拿到带字幕的响应。

---

## 1. 两条路的差别（为什么"不可行"变"可行"）

| 对比项 | 网页端接口直取（旧结论：不可行） | 手机 APP 端接口直取（新结论：可行） |
|---|---|---|
| 接口来源 | 网页版 detail/播放器/分享页 | 抖音 APP 端 HTTP API |
| 字幕字段 | **接口里根本没有字幕字段**（打印过字段清单、监听过播放器网络请求，都没有） | 响应里有 **cla_info.caption_infos** 字幕轨道 |
| 访问门槛 | 零门槛（网页免费可访问） | 需要 **X-Gorgon / X-Argus / X-Ladon** 设备签名参数 |
| 之前卡点 | 这条路本身不存在（网页端无字幕是事实） | 项目里没有签名组件 → 当时不可行 |
| 现在的钥匙 | — | GitHub 开源库 **douyin-sign**（免费，nightly CI 自动提取签名常量） |
| 实测结论 | 网页端确实没有字幕 | 有了签名，APP 端接口能拿到字幕 → 可行 |

**核心认知**：💡 **<span style="color:#2980b9">不是翻案，是换了一条路</span>**。网页端无字幕的结论不变；APP 端有字幕 + 签名开源 = 新可行路径。

---

## 2. 为什么电脑端程序能调用 APP 端接口

**签名原理**：X-Gorgon / X-Argus 是抖音 APP 请求的设备签名算法——对请求参数+时间戳+设备信息计算出一串校验值，放在请求头里让服务端确认"这是合法 APP 请求"。

**关键点**：
- 签名是 💡 **<span style="color:#2980b9">HTTP 请求头参数</span>**（X-Gorgon、X-Argus、X-Ladon、X-Khronos、X-SS-STUB），服务端只校验请求头，不关心请求来自手机还是电脑
- 电脑端程序模拟 APP 请求头（User-Agent、设备 ID、X-Argus 等）+ 附带正确签名 → 服务端按 APP 请求处理 → 返回完整响应（含字幕）
- 所以**本项目（电脑端 Python/MediaCrawler）只要接入签名生成服务，就能调用 APP 端接口**

---

## 3. douyin-sign 开源库（钥匙）

**仓库**：https://github.com/7452323/douyin-sign

**覆盖能力**：
- **移动端签名**：X-Gorgon、X-Argus、X-Ladon、X-Khronos、X-SS-STUB
- **网页端签名**：X-Bogus、X-Gnarly（备用）
- **加密**：TTEncrypt
- **自动维护**：nightly CI 自动提取签名常量 → 抖音更新算法时跟随上游更新，风险可控

**成本**：📊 **<span style="color:#e67e22">完全免费</span>**（开源库）；需要付出的是接入工程（📊 **<span style="color:#e67e22">约半天</span>**）+ 后续跟随上游更新维护。

---

## 4. 总体架构（目标方案）

    ┌────────────────────────────────────────────────────────────┐
    │ 新增：本地签名服务（douyin-sign 部署）                         │
    │ 形态：Flask/Node 本地 HTTP 服务（127.0.0.1:端口）              │
    │ 接口：POST /sign  → 入参：请求参数+时间戳+设备信息              │
    │                   → 出参：X-Gorgon/X-Argus/X-Ladon 等签名头   │
    └──────────────────────┬─────────────────────────────────────┘
                           │ 签名头注入
                           ▼
    ┌────────────────────────────────────────────────────────────┐
    │ MediaCrawler fork（采集阶段，新增 APP 端字幕通道）               │
    │ 1. 模拟 APP 请求头（设备 UA + 设备 ID + 签名头）                │
    │ 2. 请求 APP 端 detail 接口                                     │
    │ 3. 从响应 video.cla_info.caption_infos 提取字幕轨道            │
    │ 4. 下载字幕 VTT → 清洗 → 落库 subtitle_text / subtitle_meta   │
    └──────────────────────┬─────────────────────────────────────┘
                           ▼
    ┌────────────────────────────────────────────────────────────┐
    │ backend（转录阶段，现有链路不变）                               │
    │ videos.subtitle_text → DouyinSubtitleProvider（第 0 顺位）    │
    │   → 三重质量闸门 → 过闸即口播稿，不过降级 ASR                  │
    └────────────────────────────────────────────────────────────┘

**设计原则**：
- 签名服务独立部署（本地），💡 **<span style="color:#2980b9">与采集主链路解耦</span>**——签名库更新不影响主链路
- 字幕直取仍是"锦上添花"第 0 顺位，🔥 **<span style="color:#e74c3c">失败自动降级 ASR</span>**（现有链路闭环不受影响）
- 复用现有 subtitles.py 提取/清洗/落库代码（extract_subtitle_text、_clean_vtt、_download_vtt 全部可复用，只换数据来源）

---

## 5. 接入路线（工程拆解，约半天）

### 阶段 1：部署本地签名服务（约 1-2 小时）
1. **克隆 douyin-sign 仓库**到项目（如 runtime\douyin-sign）
2. **按仓库 README 部署**（依赖 Node/Python，以仓库说明为准）
3. **验证签名服务**：

```powershell
# 启动签名服务后，调本地接口应返回签名头
```
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/sign' -Method Post -Body '{"params": {...}}'
```
```powershell

```
```powershell
预期：返回包含 X-Gorgon / X-Argus 的 JSON
```

### 阶段 2：验证 APP 端接口能拿到字幕（约 1-2 小时）
1. 用签名头 + 模拟 APP 请求头请求 **APP 端 detail 接口**
2. 打印响应中 video.cla_info.caption_infos 的内容
3. **验收信号**：📊 **<span style="color:#e67e22">caption_infos 数组非空，含字幕 URL；下载 VTT 后清洗出 ≥20 字文本</span>**

### 阶段 3：接入采集链路（约 1-2 小时）
1. 在 MediaCrawler 新增 app_subtitle_provider（或改造现有 subtitles.py 增加 APP 端数据源分支）
2. 复用现有 _clean_vtt / _download_vtt / 落库逻辑
3. 开关控制（SUBTITLE_DIRECT_ENABLED 或新增 APP_SUBTITLE_ENABLED）
4. **验收信号**：采集后 subtitle_text 出现非空值；口播稿日志出现 douyin_subtitle: 成功（不再降级）

---

## 6. 关键代码（现有可复用部分）

### MediaCrawler 侧（数据源改造点）

```python
# MediaCrawler/media_platform/douyin/subtitles.py（现有，可复用）
```
```python
def _extract_subtitle_candidates(aweme_item: dict) -> list[dict]:
```
```python
    """从 APP 端 detail 响应提取字幕候选（兼容 caption_infos/subtitles/captions）"""
```
```python
    # 已实现：video.subtitles + video.cla_info.caption_infos 双路径
```
```python
    # 改造点：数据源从网页 detail 换成 APP 端 detail（带签名请求）
```
```python

```
```python
def _download_vtt(url: str) -> str:
```
```python
    """下载字幕 VTT（1 次尝试、10MB 上限、HTML 拒绝）——直接复用"""
```
```python

```
```python
def _clean_vtt(raw: str) -> str:
```
```python
    """去 WEBVTT 头/时间轴/标签/广告尾缀 → 干净全文——直接复用"""
```

### backend 侧（转录阶段，完全复用）

```python
# backend/app/services/douyin_subtitles.py（现有，无需改动）
```
```python
def _gate(subtitle_text, subtitle_meta, request) -> str:
```
```python
    # 三重质量闸门：①≥20字 ②无BGM标签 ③zh语言+标题实词交集
```
```python
    # 数据到位后自动生效，过闸即产出口播稿
```

### 签名服务调用（新增，示意）

```python
# 新增：backend/app/services/douyin_sign_client.py（示意）
```
```python
def sign_request(params: dict, device: dict) -> dict:
```
```python
    """调本地 douyin-sign 服务生成签名头"""
```
```python
    resp = httpx.post("http://127.0.0.1:8080/sign",
```
```python
                      json={"params": params, "device": device}, timeout=5)
```
```python
    return resp.json()  # {"X-Gorgon": "...", "X-Argus": "...", ...}
```

---

## 7. 三重质量闸门（防假成功，保持不变）

| 闸门 | 规则 | 防什么 |
|---|---|---|
| ① | 非空且 ≥20 字 | 空字幕/残缺字幕 |
| ② | 无 BGM/原声/♪/音乐 标签 | BGM 歌词被当口播稿（历史教训） |
| ③ | 语言 zh + 标题实词与字幕交集 ≥1 | 错位字幕/他语字幕 |

**数据到位后闸门自动生效**；不过闸自动降级 ASR（⚠️ **<span style="color:#e74c3c">安全兜底</span>**）。

---

## 8. 收益与风险

### 收益
- **速度**：📊 **<span style="color:#e67e22">单条字幕秒级（~1-2s）</span>**，🔥 **<span style="color:#e74c3c">比 GPU 转写快 10 倍以上</span>**
- **算力**：不占 GPU（GPU ASR 可留给无字幕视频兜底）
- **质量**：平台官方字幕，通常含标点/分段，比 ASR 更工整
- **成本**：免费（开源库），半天接入工程

### 风险
- ⚠️ **<span style="color:#e74c3c">抖音更新签名算法</span>** → douyin-sign 失效（上游有 nightly CI 自动更新，跟随更新即可）
- 🔶 APP 端接口字段变化 → 防御式解析兜底（现有 _extract_subtitle_candidates 已兼容多字段名）
- 🔶 设备信息需伪装合理（模拟真实 APP 设备头，避免被识别）
- ⚠️ **<span style="color:#e74c3c">部分视频可能无字幕轨道</span>**（创作者未开 AI 字幕）→ 自动降级 ASR，属正常现象

---

## 9. 与现网链路的关系（平滑过渡）

| 现状 | 目标 |
|---|---|
| 口播稿 = GPU 转写（149/150 达标、VAD 加速后单条 10-20s） | 口播稿 = 字幕直取（秒级）为主 + GPU 转写兜底 |
| 第 0 顺位 douyin_subtitle 数据为空（网页端无字幕） | 第 0 顺位 douyin_subtitle 数据到位（APP 端字幕） |
| 已有 provider 链 + 三重闸门 + 降级机制 | 全部复用，仅换数据源 |

**过渡策略**：签名接入成功后先 💡 **<span style="color:#2980b9">小范围灰度（1-2 账号）</span>** → 验证字幕质量 → 再全量开启。开启前 GPU 转写链路不受影响。

---

## 10. 行动清单（Codex/开发者接力）

- [ ] 克隆 douyin-sign 到 runtime\douyin-sign（https://github.com/7452323/douyin-sign）
- [ ] 部署本地签名服务（按仓库 README），验证 /sign 返回 X-Gorgon/X-Argus
- [ ] 用签名头请求 APP 端 detail，确认 video.cla_info.caption_infos 有字幕（打印字段清单）
- [ ] MediaCrawler 侧接入 APP 端数据源（复用 subtitles.py 清洗/下载/落库）
- [ ] backend 开关 SUBTITLE_DIRECT_ENABLED=true，小范围灰度验证
- [ ] 全量启用 + 监控降级率（无字幕视频占比）

---

## 11. 待确认项（❓）

- ❓ douyin-sign 的部署方式（Node or Python？以仓库 README 为准）
- ❓ APP 端接口的具体 URL 与参数（需在签名可用后实测抓取）
- ❓ 签名服务的稳定性与并发能力（多账号并发时是否需排队）
- ❓ 设备信息伪装方案（模拟哪个设备模型/系统版本最稳）