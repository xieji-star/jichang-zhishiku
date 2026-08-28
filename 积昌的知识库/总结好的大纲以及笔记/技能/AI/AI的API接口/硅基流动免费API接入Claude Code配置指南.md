---
title: 硅基流动免费API接入Claude Code配置指南
type: 配置指南
date: 2026-08-06
tags:
  - AI工具
  - API
  - 免费
  - Claude Code
  - 硅基流动
  - 配置指南
source: 联网核实（2026-08-06）+ 免费AI接口大全.md
---

# 硅基流动免费API接入Claude Code配置指南

> [!summary] 概要
> 本文基于 [[免费AI接口大全]] 的三梯队分类，针对「Claude Code 用户 + VPN 不稳定 + 偶尔项目开发」的实际条件，选定 **硅基流动（SiliconFlow）** 作为免费 API 主力渠道，并给出接入 Claude Code 的完整配置方案：Anthropic 兼容端点、免费额度明细、环境变量配置、模型选择与风险提示。

## 相关笔记

- [[免费AI接口大全]] — 免费 AI 接口三梯队总览（本文的选型依据）
- [[Token的计费方式以及如何更好的省Token]] — 省 Token 技巧（免费额度同样适用）
- [[Claude Code 从 0 到 1 完全使用教程（Obsidian版）]] — Claude Code 基础使用教程

## 索引

- 🎯 [[#1. 选型背景：为什么选硅基流动]] — 三个条件的交集筛选结论
- ❌ [[#2. 排除清单：其他渠道为什么不合适]] — 逐家排除的理由
- 💰 [[#3. 免费额度明细（2026-08 核实）]] — 注册福利 + 0 元模型 + 月度额度
- 🔧 [[#4. Claude Code 接入配置（Windows）]] — 环境变量 + 跳过登录 + 验证
- 🧠 [[#5. 免费模型选择建议]] — 开发场景的模型搭配
- ⚠️ [[#6. 风险提示与注意事项]] — 清单轮换、速率限制、错峰

## 1. 选型背景：为什么选硅基流动

### 1.1 用户实际条件

- 主力工具：**Claude Code**（需要 Anthropic 兼容端点，或自行搭建协议转换网关）
- 网络环境：**VPN 不稳定**（海外服务不可靠，必须国内直连）
- 使用频率：**偶尔进行项目开发**（轻度用量，免费额度够用）

### 1.2 结论：硅基流动是唯一最优解

🔥 **<span style="color:#e74c3c">在「免费 + Claude Code 可直连 + 国内稳定」三个条件的交集里，硅基流动几乎是唯一选项。</span>**

| 你的条件 | 硅基流动的表现 |
|---------|---------------|
| 用 Claude Code | 提供 **Anthropic 兼容 API**（`https://api.siliconflow.cn/v1/anthropic`），环境变量一配即用，无需网关转换 |
| VPN 不稳定 | 国内站点 `api.siliconflow.cn` **直连，完全不需要代理** |
| 偶尔开发（轻度） | 注册送 ¥14 额度 + 0 元永久免费模型 + 大模型月度免费额度，轻度用量绰绰有余 |

> 选型依据来自 [[免费AI接口大全]] 的三梯队分类：第一梯队（英伟达 NIM、Cloudflare、魔塔）与第二梯队（Trae、OpenRouter、硅基流动、Hugging Face）中，只有硅基流动同时满足上述三个条件。

## 2. 排除清单：其他渠道为什么不合适

| 渠道 | 排除原因 |
|------|---------|
| 英伟达 NIM | 海外服务，VPN 不稳 → 请求随时断，编程场景体验极差 |
| Cloudflare Workers AI | 海外 + 它是 Workers 平台而非现成对话 API，接入 Claude Code 门槛高 |
| 魔塔社区（ModelScope） | 国内直连可用，但只有 OpenAI 兼容（需自搭转换网关），且约 2000 字/天额度对「项目开发」杯水车薪 → 仅作后备 |
| Trae | 是 IDE 工具不是 API，无法接入 Claude Code |
| OpenRouter | 海外，VPN 不稳直接出局 |
| Hugging Face | 海外，免费额度偏紧、高峰排队 |
| MiMo Code / OpenCode | 独立客户端，免费限时/限额不透明，当不了 Claude Code 的 API 后端 |
| Free AI API 聚合项目 | Docker 折腾 + OpenAI 兼容需转换 + 质量参差，与「偶尔开发」不匹配 |

## 3. 免费额度明细（2026-08 核实）

### 3.1 新用户注册福利

- 📊 **<span style="color:#e67e22">注册送约 ¥14 免费额度（≈2000 万 Token）</span>**，手机号实名认证即可领取，**无需绑定信用卡**，支持微信/支付宝充值
- 国际站（siliconflow.com）注册送约 $1，可用 Google/GitHub 账号注册

### 3.2 永久免费（0 元）模型

- 💡 **<span style="color:#2980b9">部分小参数模型永久免费（约 9B 参数以下）</span>**：
  - Qwen2.5-7B-Instruct、Qwen3-8B、DeepSeek-R1-Distill-Qwen-7B、GLM-4-Flash、DeepSeek-OCR 等

### 3.3 带月度免费额度的大模型

📊 **<span style="color:#e67e22">大模型月度免费额度（按月更新、未使用不累积）</span>**

| 模型 | 上下文 | 免费额度/月 |
|------|--------|------------|
| DeepSeek-V3 | 128K | 100 万 Token |
| Qwen2.5-72B-Instruct | 128K | 200 万 Token |
| GLM-4-9B-Chat | 128K | 500 万 Token |
| CodeLlama-34B-Instruct | 16K | 100 万 Token |
| Whisper-large-v3（语音） | — | 1000 分钟 |
| BGE-M3（嵌入） | 8K | 1000 万 Token |

> ⚠️ 免费模型清单会随平台调整轮换，**使用前务必以控制台「模型广场」实时显示为准**。

## 4. Claude Code 接入配置（Windows）

### 4.1 注册与获取 Key

1. 硅基流动官网用**手机号注册 + 实名认证**，领取 ¥14 免费额度
2. 控制台 → API 密钥 → 新建 API Key（`sk-` 开头）

### 4.2 设置环境变量

⚠️ **<span style="color:#e74c3c">必须用 `ANTHROPIC_AUTH_TOKEN`（Bearer Token 方式），不能用 `ANTHROPIC_API_KEY`（x-api-key 方式），混用会导致 401 报错</span>**

| 变量名 | 值 |
|--------|-----|
| `ANTHROPIC_BASE_URL` | `https://api.siliconflow.cn` |
| `ANTHROPIC_AUTH_TOKEN` | `sk-你的密钥` |
| `ANTHROPIC_MODEL` | `Qwen/Qwen2.5-72B-Instruct` |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `Qwen/Qwen2.5-72B-Instruct` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `Qwen/Qwen2.5-72B-Instruct` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `Qwen/Qwen3-8B` |

- 🔥 **<span style="color:#e74c3c">Opus/Sonnet/Haiku 三个层级变量必须都配置</span>**：第三方平台没有这三个模型别名，不配全 Claude Code 内部调用会直接报错
- Windows 设置方式：系统属性 → 环境变量 → 新建用户变量，或终端执行 `setx` 命令

### 4.3 跳过官方登录校验

- 执行以下命令，跳过 Anthropic 官方登录验证（国内厂商接入必需）：
  ```bash
  echo '{"hasCompletedOnboarding": true}' > ~/.claude.json
  ```

### 4.4 生效与验证

1. 📌 **<span style="color:#2980b9">完全重启终端 / VS Code 后配置才生效</span>**（Claude Code 插件需在 settings.json 的 `claudeCode.environmentVariables` 中配置）
2. 启动 Claude Code 后执行 `/status` 查看连接状态
3. 发送一条简单消息验证对话是否走通

> Claude Code 的基础使用方式见 [[Claude Code 从 0 到 1 完全使用教程（Obsidian版）]]

## 5. 免费模型选择建议

### 5.1 开发场景的模型搭配

- 🧠 **<span style="color:#2980b9">主力对话（Sonnet 层）：DeepSeek-V3（100 万 Token/月免费）或 Qwen2.5-72B（200 万 Token/月免费）</span>** — 编码能力强
- 轻量任务（Haiku 层）：Qwen3-8B / GLM-4-Flash（永久 0 元）
- 注册送的 ¥14 未烧完前，可临时使用 **Kimi-K2.6 / GLM-4.7** 等更强编码模型，用完再切回免费档

### 5.2 省 Token 配合

- 💡 **<span style="color:#2980b9">免费额度有限，「省着用 = 变相扩容」</span>**：精简上下文、控制输出长度等技巧见 [[Token的计费方式以及如何更好的省Token]]

## 6. 风险提示与注意事项

- ⚠️ **<span style="color:#e74c3c">免费模型清单会轮换</span>**：以注册后控制台「模型广场」实时显示的免费列表为准，遇到模型下架及时切换
- ⚠️ **<span style="color:#e74c3c">速率限制</span>**：DeepSeek 系列免费档约 30 次请求/小时，高峰期可能限流——「偶尔开发」够用，连续重度编码时错峰即可
- 📌 免费额度用完可充值继续用（按量计费），无需绑卡也可设置消费上限
- 📌 免费层在欧盟/英国/瑞士不可用（中国大陆不受影响）

## 原始材料

- 本文数据来源：2026-08-06 联网核实（硅基流动官方文档 + 第三方汇总）
- 选型依据笔记：[[免费AI接口大全]]
