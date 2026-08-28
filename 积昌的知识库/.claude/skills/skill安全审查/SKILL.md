---
name: skill安全审查
description: "【仅手动触发】skill 安全审查 — 使用 NVIDIA SkillSpector 对 skill 路径/URL/zip 进行安全扫描，检测 prompt 注入、数据外泄、恶意代码等风险，并据扫描结论决定是否允许安装。本技能不自动触发，仅在用户明确调用 /skill安全审查 或明确要求执行安全审查时使用。"
---

# skill安全审查

> ⚠️ **手动触发**：本技能**不会自动触发**。仅当用户明确调用 `/skill安全审查`，或明确要求"对某 skill 做安全审查"时，才执行本流程。

使用 NVIDIA SkillSpector 对 skill 代码进行安全扫描，识别恶意行为与安全风险，并据此决定是否允许安装。

## 何时使用（手动调用场景）

以下场景由用户**主动要求**时使用（不作为自动触发条件）：

- 用户明确要求审查某个 skill 是否安全（本地目录、SKILL.md 文件、zip、Git 仓库、URL）
- 用户明确要求下载/安装前先做安全扫描
- 用户对已安装的 skill 做定期安全审计

## 前置条件

- SkillSpector 已通过 `uv tool install` 安装（`skillspector --version` 验证）
- 扫描静态分析默认**不需要 API key**（`--no-llm`）；如需 LLM 语义增强分析，用户需配置 `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `NVIDIA_INFERENCE_KEY` 等环境变量

## 执行流程

### Step 1：确认扫描目标

| 目标类型 | 示例 |
|---------|------|
| 本地目录（skill 文件夹） | `D:/xxx/skill-folder` |
| 单个 SKILL.md | `D:/xxx/SKILL.md` |
| GitHub 仓库 | `https://github.com/owner/repo` |
| zip 压缩包 | `D:/xxx/skill.zip` |

不确定目标路径时，先向用户确认（"扫描哪个 skill？路径/链接发我"）。

### Step 2：运行扫描

```bash
# 默认静态分析（推荐，无需 API key）
skillspector scan <目标> --no-llm --format markdown

# 全目录递归扫描（含附带脚本）
skillspector scan <目录> --no-llm --format markdown

# 需要 LLM 语义分析时（用户明确要求且已配置 API key）
skillspector scan <目标> --format markdown
```

> 扫描远程 URL 时 SkillSpector 会先克隆/下载到临时目录，自动执行主机白名单、SSRF 防护与大小上限校验。

### Step 3：解析报告

重点读取四个字段：

| 字段 | 含义 |
|------|------|
| **Score** | 0-100 风险评分，越高越危险 |
| **Severity** | LOW / MEDIUM / HIGH / CRITICAL |
| **Recommendation** | SAFE / CAUTION / RISKY / MALICIOUS |
| **Issues** | 具体问题列表（含严重度、置信度、位置、修复建议） |

### Step 4：决策与执行（硬性规则）

| 扫描结论 | 处理方式 |
|---------|---------|
| **SAFE**（0 问题或仅 INFO/LOW） | ✅ 允许安装，可继续正常安装流程 |
| **CAUTION**（有 MEDIUM 以上问题） | ⚠️ **先向用户展示全部风险点**，询问"是否仍要安装"（怎么做类问题），得到确认后才可安装 |
| **RISKY**（高危问题） | 🛑 **拒绝安装**，向用户说明具体风险与原因 |
| **MALICIOUS**（检测到恶意行为） | 🛑 **立即停止安装**，明确告知用户该 skill 存在恶意代码，禁止安装 |

安装后若发现新的高危扫描结果，同样按上表回退处理。

### Step 5：汇报

向用户输出：
1. 扫描结论（评分/严重度/建议）
2. 发现的问题清单（逐条：位置、内容、修复建议）
3. 处置结果（允许安装 / 已停止安装）

## 常用命令速查

```bash
skillspector --version                 # 查看版本
skillspector scan <目标> --no-llm --format terminal   # 终端输出（默认）
skillspector scan <目标> --no-llm --format json       # JSON 输出
skillspector scan <目标> --no-llm --format sarif      # SARIF 输出（可接入 GitHub Code Scanning）
skillspector scan <目标> --no-llm --format markdown   # Markdown 报告
skillspector mcp                        # 以 MCP Server 方式运行（需 mcp extra）
```

## 说明

- 本 skill 由 NVIDIA 官方 SkillSpector v2.5.3（Apache-2.0）驱动，已通过代码安全审查后安装
- 检测能力：68 种漏洞模式 / 17 个类别（prompt 注入、数据外泄、权限提升、供应链攻击、YARA 恶意软件特征、MCP 工具投毒等）
- 静态分析永不执行被扫描的代码（只解析不运行）
