---
title: "Codex的5.6三大旗舰模型差异"
type: 概念笔记
date: 2026-08-04
tags:
  - AI工具
  - Codex
  - GPT-5.6
  - 模型对比
  - 概念
created: 2026-08-04
aliases:
  - GPT-5.6 Sol Terra Luna
  - Codex 三档模型
  - Codex三大旗舰模型
source: "OpenAI 官方公告、网络公开资料、知识库既有笔记"
---

# Codex的5.6三大旗舰模型差异

> [!summary] 概要
> "5.6"（GPT-5.6）不是单个模型，而是 **Sol / Terra / Luna 三个分层模型**组成的家族，在 Codex、ChatGPT 和 API 里都能选。简单说：**Sol 最聪明最贵（旗舰）、Terra 性价比之王（日常默认）、Luna 最快最便宜（跑量专用）**。本文用大白话讲清三个模型各自有什么用、差别多大、AI 编程小白该怎么选怎么用。

## 相关笔记

- [[Codex 零基础系统入门教程]] — Codex 安装与入门
- [[Codex模型配置方法大全]] — Codex 模型与供应商配置
- [[Claude Code 与 Codex 对比]] — Codex 与 Claude Code 全面对比
- [[Codex++使用教程]] — Codex++ 增强工具使用
- [[Token的计费方式以及如何更好的省Token]] — Token 计费原理与省 Token 技巧

## 索引

- 🌞 [[#1. 一句话总览：三个模型分别是谁]] — 三模型定位与价格速览
- 🧠 [[#2. 大白话解读：Sol / Terra / Luna 各是什么]] — 用生活类比讲清三个模型
- 📊 [[#3. 核心差别：能差多少？数据说话]] — 编码/操作/长上下文/安全基准对比
- 🎯 [[#4. 什么时候用哪个：场景选择指南]] — 按任务类型选模型
- 🚀 [[#5. AI 编程小白怎么用：上手路线]] — 从 Terra 起步的省钱建议
- 🛠️ [[#6. 在 Codex 里怎么切换模型]] — /model 命令与配置方法
- ⚠️ [[#7. 重要提醒与坑]] — 容易踩的雷
- 📌 [[#8. 总结：记住这几点]] — 核心结论
- 🔗 [[#9. 资料来源]] — 参考链接

## 1. 一句话总览：三个模型分别是谁

> 5.6 = 第 5.6 代 GPT 模型；Sol / Terra / Luna 是这一代里的三个"配置版本"（tier），**未来每一代都会沿用这三个名字**（比如以后会有 gpt-5.7-sol）。Codex 的相关概念与配置见 [[Claude Code 与 Codex 对比]] 与 [[Codex模型配置方法大全]]。

| 模型 | 定位 | 一句话理解 | 价格（每 100 万 tokens 输入/输出） |
|------|------|-----------|----------------------------------|
| **Sol**（太阳） | 旗舰款 | 最聪明、最能干复杂活，也最贵 | $5 / $30 |
| **Terra**（地球） | 均衡款 | 性价比之王，日常干活首选 | $2.5 / $15 |
| **Luna**（月亮） | 轻快款 | 最快最便宜，适合批量跑量 | $1 / $6 |

- 📊 **<span style="color:#e67e22">三者共用 105 万 tokens（1.05M）的超长上下文窗口，最大单次输出 12.8 万 tokens</span>**——都能"读"很长的代码库，区别在于读得好不好（见第 3 节）。
- 🔥 **<span style="color:#e74c3c">重要：裸写 "gpt-5.6" 会默认路由到最贵的 Sol！</span>** 想用便宜档，必须写完整模型 ID：`gpt-5.6-sol` / `gpt-5.6-terra` / `gpt-5.6-luna`。
- 💡 模型 ID 说明：`gpt-5.6-sol` 的别名就是 `gpt-5.6`（即裸写 = Sol）。

## 2. 大白话解读：Sol / Terra / Luna 各是什么

### 2.1 🌞 Sol —— 旗舰款（最强大脑，最贵）

- **定位**：复杂编程、架构设计、大型项目重构、深度研究、安全类任务
- **类比**：像团队里那位**经验最丰富的高级工程师**——最难啃的骨头交给他，他啃得动，但请他的价钱也最高
- **特点**：
  - Codex 的默认 **Power 模式**用的就是 `gpt-5.6-sol`（搭配 Medium 推理档位）
  - **<span style="color:#2980b9">在"电脑操作类"任务上优势巨大</span>**（OSWorld 2.0：62.6%，比 Terra 高 12 个点）——因为它能自己"看"屏幕渲染结果再判断下一步
  - 安全/攻防类任务（ExploitBench 73.5%）只有它值得用

### 2.2 🌍 Terra —— 均衡款（日常主力，性价比之王）

- **定位**：日常写代码、修 bug、代码审查、项目分析、自动化任务
- **类比**：像**全能型普通工程师**——大部分日常活干得又快又好，价格只有 Sol 的一半
- **特点**：
  - 🔥 **<span style="color:#e74c3c">编码能力与 Sol 只差 1.2 个点（SWE-Bench Pro 63.4% vs 64.6%），价格却便宜一半</span>**
  - **免费/Go 套餐用户默认就是 Terra**——OpenAI 官方"理智默认"的选择
  - 长文档、大代码库场景的**最低保障**（Luna 在长上下文上会崩，见 3.4）

### 2.3 🌙 Luna —— 轻快款（最快最便宜，跑量专用）

- **定位**：分类、信息提取、格式转换、批量结构化内容、简单代码修改、重复性自动化
- **类比**：像**手脚麻利的实习生**——简单的活干得飞快、收费最低，但别指望他处理太复杂或太长的事情
- **特点**：
  - 三者中**速度最快、价格最低**（输入仅 $1/百万 tokens；2026-07-30 降价后更是低至 $0.2）
  - ⚠️ **<span style="color:#e74c3c">致命短板：长上下文"读了白读"——256K~512K 长文召回率崩到 41.3%</span>**（Sol 91.5%、Terra 89.6%）

## 3. 核心差别：能差多少？数据说话

（数据来源：OpenAI 官方公布基准，数值越高越好）

### 3.1 写代码能力

- 📊 **<span style="color:#e67e22">编码能力三档差距很小</span>**——日常写代码真的没必要上 Sol：

| 基准 | Sol | Terra | Luna | 说明 |
|------|:---:|:-----:|:----:|------|
| SWE-Bench Pro（真实代码任务） | 64.6% | 63.4% | — | Sol 与 Terra 仅差 1.2 个点 |
| Coding Agent Index（编码智能体） | 80 | 77.4 | 74.6 | 三档差距不大 |
| Terminal-Bench 2.1（终端操作） | 88.8% | 87.4% | 84.7% | 差距温和 |

### 3.2 电脑操作能力（差距最大的领域之一）

| 基准 | Sol | Terra | Luna |
|------|:---:|:-----:|:----:|
| OSWorld 2.0（操作电脑完成任务） | 62.6% | 50.2% | 45.6% |

- 💡 **<span style="color:#2980b9">Sol 能自己查看渲染输出（"看屏幕"）再决定下一步，这是它的结构性优势</span>**——让它"操作电脑"这类任务，别用 Terra/Luna 硬顶。

### 3.3 网络安全能力（差距最大的领域之二）

| 基准 | Sol | Terra | Luna |
|------|:---:|:-----:|:----:|
| ExploitBench（安全攻防） | 73.5% | 52.9% | 33.2% |

- 🔴 **<span style="color:#e74c3c">安全/攻防类任务只有 Sol 值得评估</span>**，Terra/Luna 差距过大。

### 3.4 长上下文召回（最容易踩的坑）

| 基准（256K–512K 长文） | Sol | Terra | Luna |
|------|:---:|:-----:|:----:|
| MRCR 召回率 | 91.5% | 89.6% | **41.3%** |

- ⚠️ **<span style="color:#e74c3c">Luna 接受长输入但"不真正使用"它们</span>**——长文档、大代码库任务至少要用 Terra，这是硬底线。

### 3.5 推理档位（和模型分层是两回事）

- 三个模型都支持 6 档推理力度：`none / low / medium / high / xhigh / max`（max 是新增的最高档）
- 🔥 **<span style="color:#e74c3c">Terra + high 推理 ≈ Sol + medium 的质量，价格只要一半</span>**——"选模型"和"调推理档位"是两个独立旋钮，先拧档位再换模型。
- 💡 **<span style="color:#2980b9">Ultra 模式（多智能体并行，默认 4 个、最多 16 个）仅 Sol 可用</span>**——约 4 倍 token 消耗，能把 Terminal-Bench 从 88.8% 提到 91.9%，是追求极限性能时才开的模式。

## 4. 什么时候用哪个：场景选择指南

| 任务类型 | 推荐模型 | 理由 |
|---------|---------|------|
| 常规写代码、修 bug、代码审查 | **Terra** | 与 Sol 差距极小，价格一半 |
| 大型项目重构、架构设计 | **Sol** | 复杂任务完成质量最高 |
| 多步骤自主任务（agentic 长周期） | **Sol** | 需要长程规划与自我检查 |
| 深度研究、安全/攻防类 | **Sol** | 唯一值得评估的档位 |
| 长文档、大代码库分析 | **Terra 起步** | Luna 长上下文会崩 |
| 批量处理、格式转换、信息提取 | **Luna** | 快、便宜、任务简单 |
| 简单重复的自动化 | **Luna** | 跑量首选 |
| 极难问题（"世纪难题"） | **Sol + max 推理** | 兜底大招，日常别用 |

## 5. AI 编程小白怎么用：上手路线

> 🎯 **核心建议：从 Terra 起步，跑通之后再升级。别一上来就 Sol + max 烧钱。** Codex 的安装与入门见 [[Codex 零基础系统入门教程]]。

### 5.1 第一步：先确认自己的套餐

| 套餐 | 能用什么模型 |
|------|-------------|
| **Free / Go** | Terra（默认） |
| **Plus** | Sol / Terra / Luna 全可选（Sol 从 medium 推理档位起） |
| **Pro / Business / Enterprise** | 全都有，另有 Sol Pro |
| **Ultra 模式** | Codex Plus 及以上（仅 Sol） |

### 5.2 第二步：按任务难度选模型

- **日常 80% 的活**（写函数、改 bug、问问题）→ **Terra**，默认 medium 推理就够
- **卡了很久的大 bug / 重构 / 设计** → 升级 **Sol**，推理档位提到 high/xhigh
- **批量简单活**（整理数据、格式转换、批量改名）→ **Luna**
- **长文档/长代码库** → 保底 **Terra**，千万别用 Luna

### 5.3 第三步：学会"先便宜后贵"的省钱姿势

1. 先用 **Terra** 把任务跑通，看效果
2. 效果不满意 → 先把**推理档位调高**（high），而不是直接换 Sol
3. 还不行 → 换 **Sol**（推理档位可回调到 medium）
4. 只有极难任务才 **Sol + max**
5. 简单重复任务无脑 **Luna**

### 5.4 小白常见误区

- ❌ **误区 1**：觉得"最贵的 Sol 一定最好"——日常任务 Terra 和它没差别，纯浪费钱
- ❌ **误区 2**：把长文档丢给 Luna——它"读了但没记住"，结果会离谱
- ❌ **误区 3**：每次都用 max 推理——慢且贵，绝大多数任务 medium 足够

## 6. 在 Codex 里怎么切换模型

三种方式（任选其一）：

1. **对话内切换**：输入 `/model` 命令，选 `gpt-5.6-sol` / `gpt-5.6-terra` / `gpt-5.6-luna`
2. **配置文件**：在 `config.toml` 里写 `model = "gpt-5.6-terra"`（完整配置方法见 [[Codex模型配置方法大全]]）
3. **启动参数**：`codex --model gpt-5.6-terra`

> ⚠️ 再次强调：**<span style="color:#e74c3c">不要裸写 "gpt-5.6"——它指向最贵的 Sol</span>**；要用便宜档务必写完整 ID。

## 7. 重要提醒与坑

1. 🔴 **裸 `gpt-5.6` = Sol（最贵）**：想省钱必须写明 `gpt-5.6-terra` / `gpt-5.6-luna`
2. 🔴 **Luna 长上下文会"失忆"**：MRCR 召回率 41.3%，长文档至少用 Terra
3. 💡 **推理档位是另一个省钱旋钮**：Terra + high ≈ Sol + medium，价格减半
4. 💡 **Ultra 模式烧 token**：约 4 倍消耗，只在需要并行多智能体时开
5. 📊 **价格变动（2026-07-30 起）**：API 价格再次下调——Terra 降至 $2/$12，Luna 降至 $0.2/$1.2，Sol 维持 $5/$30（每百万 tokens 输入/输出）
6. 📌 **三个名字是持久分层**：未来 gpt-5.7 也会沿用 Sol/Terra/Luna 命名，学会一次受用终身

## 8. 总结：记住这几点

>highlight 【一句话记忆】日常 Terra，难题 Sol，批量跑量 Luna；长文档保底 Terra；裸写 gpt-5.6 会花冤枉钱，务必写全名。

- 🌞 **Sol** = 太阳：最强最贵，复杂任务、安全、电脑操作找它
- 🌍 **Terra** = 地球：日常居住地，性价比之王，小白默认选择
- 🌙 **Luna** = 月亮：小而快，批量跑量首选，但别让它"读长文"
- 🔥 省钱公式：**先 Terra → 调高推理档位 → 不行再上 Sol → 极难才 Sol+max**

## 9. 资料来源

- [OpenAI 官方公告：Advancing the price-performance frontier with GPT-5.6](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/)
- [apidog：GPT-5.6 Sol vs Terra vs Luna: which model should you use?](https://apidog.com/blog/gpt-5-6-sol-vs-terra-vs-luna/)
- [极客公园：GPT-5.6 发布之夜，Codex/ChatGPT 合二为一](https://w.geekpark.net/news/367104)
- [LayerLens：GPT-5.6 Benchmark Review: Sol, Terra, Luna](https://layerlens.ai/blog/gpt-5-6-benchmark-review-sol-terra-luna)
- [腾讯云开发者社区：Codex 一行配置启用最新版 GPT-5.6](https://cloud.tencent.com.cn/developer/article/2706970)
- [HKU SPACE AI Hub：Get started with OpenAI GPT-5.6 on Amazon Bedrock](https://aihub.hkuspace.hku.hk/2026/07/24/get-started-with-openai-gpt-5-6-sol-terra-and-luna-on-amazon-bedrock/)
- [businessmodelanalyst：OpenAI Ships GPT-5.6 as Three Tiers](https://businessmodelanalyst.com/openai-gpt-5-6-sol-terra-luna/)
