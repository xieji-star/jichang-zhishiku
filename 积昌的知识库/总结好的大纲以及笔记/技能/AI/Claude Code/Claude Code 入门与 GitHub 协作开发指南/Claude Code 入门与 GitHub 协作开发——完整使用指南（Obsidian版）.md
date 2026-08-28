---
title: Claude Code 入门与 GitHub 协作开发 —— 完整使用指南
tags:
  - ClaudeCode
  - GitHub
  - AI编程
  - Obsidian
  - 课程笔记
aliases:
  - Claude Code 完整使用指南
  - Claude Code 入门与 GitHub 协作开发
created: 2026-07-09
updated: 2026-07-09
---

# Claude Code 入门与 GitHub 协作开发 —— 完整使用指南

> 基于课程讲义《[[Claude code入门与GitHub协作开发.pdf|Claude code入门与GitHub协作开发.pdf]]》及课堂会议实录整理。
>
> 适用对象：零基础新手，想用 AI 辅助编程并托管项目到 GitHub 的开发者。

> [!NOTE]
> 本文中的课程讲义链接使用 Obsidian 内部链接格式，例如：`[[Claude code入门与GitHub协作开发.pdf#page=1|讲义 PDF 第 1 页]]`。  
> 请将本 Markdown 文件与课程讲义 PDF 放在同一个 Obsidian Vault 文件夹内，并确保 PDF 文件名完全一致。

---

## 目录

- [[#一、Claude Code 是什么？有什么用？]]
- [[#二、Claude Code 安装（Windows 为例）]]
- [[#三、Claude Code 基础操作与常用命令]]
- [[#四、GitHub 协作开发]]
- [[#五、如何高效逛 GitHub（找到优质项目）]]
- [[#六、实战示例：微信机器人项目（课程演示项目）]]
- [[#七、GitHub 提交备注技巧]]
- [[#八、总结与资源链接]]

---

## 一、Claude Code 是什么？有什么用？

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=1|讲义 PDF 第 1 页]]

Claude Code（简称 CC）是一款终端交互式 AI 编程助手，相比云端沙箱，它有四大优势：

- **完整理解项目**：能阅读整个代码库，直接修改代码，而非仅处理片段。
- **核心设计文件 `CLAUDE.md`**：项目启动时自动加载，记录项目背景、目的、你的编码习惯，相当于“老员工”入职即上手。
- **深度协作体验**：终端对话式交互，边讨论边开发，让你更深入理解项目。
- **擅长复杂任务**：执行偏慢，但会主动多问多确认，完成度高。

---

## 二、Claude Code 安装（Windows 为例）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=1|讲义 PDF 第 1 页]]、[[Claude code入门与GitHub协作开发.pdf#page=2|讲义 PDF 第 2 页]]、[[Claude code入门与GitHub协作开发.pdf#page=3|讲义 PDF 第 3 页]]、[[Claude code入门与GitHub协作开发.pdf#page=4|讲义 PDF 第 4 页]]、[[Claude code入门与GitHub协作开发.pdf#page=5|讲义 PDF 第 5 页]]、[[Claude code入门与GitHub协作开发.pdf#page=6|讲义 PDF 第 6 页]]

### 2.1 前置条件：安装 Git

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=1|讲义 PDF 第 1 页]]

- 仅 Windows 用户需要。
- 下载地址：[https://git-scm.com/install/windows](https://git-scm.com/install/windows)
- 安装后可在任意文件夹右键打开 **Git Bash** 或 **PowerShell**（注意：**必须用 PowerShell**，不是 CMD，两者提示符不同：`PS C:\Users\>` 是 PowerShell，`C:\Users\>` 是 CMD）。

### 2.2 安装 Claude Code 本体

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=2|讲义 PDF 第 2 页]]、[[Claude code入门与GitHub协作开发.pdf#page=3|讲义 PDF 第 3 页]]、[[Claude code入门与GitHub协作开发.pdf#page=4|讲义 PDF 第 4 页]]、[[Claude code入门与GitHub协作开发.pdf#page=5|讲义 PDF 第 5 页]]

打开 PowerShell，根据网络情况选择以下一种方式：

#### 方案一（有梯子，且能访问 Claude 官网）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=2|讲义 PDF 第 2 页]]

```powershell
irm https://claude.ai/install.ps1 | iex
```

注意：如果提示 Cloudflare 拦截或无法访问，是因为终端流量未走代理。解决方法：

- 开启梯子的 **虚拟网卡模式（TUN 模式）**，让所有流量走国外。
- 若仍失败，改用 winget 安装：

> Cloudflare 拦截说明对应：[[Claude code入门与GitHub协作开发.pdf#page=3|讲义 PDF 第 3 页]]、[[Claude code入门与GitHub协作开发.pdf#page=4|讲义 PDF 第 4 页]]

```powershell
winget install Anthropic.ClaudeCode
```

#### 方案二（无梯子或官方命令被墙）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=5|讲义 PDF 第 5 页]]

使用国内镜像（安全起见可自行判断）：

```powershell
irm https://daheiai.com/cc.ps1 | iex
```

此命令会通过第三方服务器代理下载。

### 2.3 配置环境变量（仅当使用 irm 方案时需要）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=5|讲义 PDF 第 5 页]]

- 打开“开始菜单” → 输入“环境变量” → 点“编辑系统环境变量”。
- 点击“环境变量” → 在“系统变量”中找到 Path → 双击 → 新建。
- 将 Claude Code 安装成功时显示的安装路径粘贴进去（winget 会自动配置，可跳过）。

### 2.4 安装 ccswitch 接入国内模型（解决 Claude 拒绝访问）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=6|讲义 PDF 第 6 页]]

由于 Anthropic 对国内 IP 限制严格，安装后直接运行 `claude` 可能被拒。推荐安装 ccswitch：

- 下载地址：[https://wwayc.lanzoub.com/iiHKV3n29yhe](https://wwayc.lanzoub.com/iiHKV3n29yhe)
- 配置模型（建议选择 DeepSeek），将请求地址换为国内大模型。
- 配置后，运行 `claude` 不再请求 Anthropic，即可正常使用。

---

## 三、Claude Code 基础操作与常用命令

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=7|讲义 PDF 第 7 页]]、[[Claude code入门与GitHub协作开发.pdf#page=8|讲义 PDF 第 8 页]]、[[Claude code入门与GitHub协作开发.pdf#page=9|讲义 PDF 第 9 页]]、[[Claude code入门与GitHub协作开发.pdf#page=10|讲义 PDF 第 10 页]]

### 3.1 启动与工作目录

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=7|讲义 PDF 第 7 页]]

- 打开你的项目文件夹 → 右键 → “在终端中打开” → 输入 `claude` 回车。
- 首次使用会弹出安全提示，按 Enter 继续即可。

### 3.2 核心斜杠命令（/commands）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=7|讲义 PDF 第 7 页]]、[[Claude code入门与GitHub协作开发.pdf#page=8|讲义 PDF 第 8 页]]

| 命令 | 作用 |
|---|---|
| `/init` | 项目初始化，生成 `CLAUDE.md`，让 CC 快速理解项目结构 |
| `/clear` | 清除当前对话上下文，重新开始（常用于开启新话题） |
| `/compact` | 让 CC 自动压缩上下文（初期可用，成熟项目不建议，可能丢失关键信息） |
| `/cost` | 查看当前上下文占比（超过 60% 时 CC 会变笨，需及时压缩） |
| `/plan` | 开启计划模式，CC 只分析不执行，适合先确认方案再动手 |
| `/help` | 查看所有可用命令 |

切换模式快捷键：`Shift + Tab` 可在 Default（默认，每步询问）、AcceptEdits（自动批准文件修改）、Plan（只读）三种模式间循环。

### 3.3 推荐 Skills（技能包）安装

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=8|讲义 PDF 第 8 页]]、[[Claude code入门与GitHub协作开发.pdf#page=9|讲义 PDF 第 9 页]]

Skills 是 markdown 文件，包含触发条件和流程，可复用。新手建议先装两个：

- **Superpowers**：包含 `/brainstorm`（苏格拉底式提问帮你理清需求）、`/write-plan`（拆解任务为 2~5 分钟小任务）、`/execute-plan`（按计划执行）。适合刚接触项目时规划骨架。
- **Skill Creator（官方）**：通过问答引导你创建自己的 Skills，或优化已有 Skills。

安装方式（直接在 CC 对话中）：

```text
/plugin install 技能名          # 仅在当前项目生效
/plugin install --global 技能名 # 全局生效（不推荐）
```

重要原则：

- 先少装，用够再加，起步只装 Superpowers + Skill Creator。
- 按项目装，不要全局装，保持干净。
- 用斜杠命令强制触发（如 `/brainstorm`），不要等自动识别。

### 3.4 操作习惯与避坑

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=9|讲义 PDF 第 9 页]]、[[Claude code入门与GitHub协作开发.pdf#page=10|讲义 PDF 第 10 页]]

#### ESC 键的用法

- 单按 ESC：中断当前任务，CC 停下等你输入，上下文保留。
- 双按 ESC：直接退出 CC（相当于关闭终端），上下文全部丢失，慎用！

#### 上下文管理流程（重要！）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=9|讲义 PDF 第 9 页]]、[[Claude code入门与GitHub协作开发.pdf#page=10|讲义 PDF 第 10 页]]

当 `/cost` 显示达到 60% 左右时，应主动处理：

1. 让 CC 整理决策日志（复制以下提示发给 CC）：

```text
帮我总结当前对话的决策日志：
【已确定的技术决策】
【已完成的模块】
【当前正在做的任务】
【未解决的问题】
【下一步计划】
```

2. 人工检查并补充修正。
3. 执行 `/clear` 清空对话。
4. 新对话第一条消息粘贴总结，CC 就能继续工作。

核心思想：由你来记忆关键节点，不依赖 CC 自己的记忆。

#### 权限模式选择

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=10|讲义 PDF 第 10 页]]

- **Default**：每次操作都询问，新手推荐。
- **AcceptEdits**：文件修改自动批准，仅 shell 命令需要确认（Shift+Tab 切换）。
- **Plan**：只读，不修改任何文件，用于分析。
- **--dangerously-skip-permissions**：全自动执行（需启动时加参数，谨慎使用）。

#### 引用特定文件

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=10|讲义 PDF 第 10 页]]

在对话中输入 `@文件名` 可让 CC 只看该文件，而非扫描全库，节省上下文：

```text
@App.vue 这个组件的提交逻辑有问题，帮我检查一下
```

---

## 四、GitHub 协作开发

> 讲义对应章节：[[Claude code入门与GitHub协作开发.pdf#page=10|讲义 PDF 第 10 页]] ~ [[Claude code入门与GitHub协作开发.pdf#page=15|第 15 页]]

### 4.1 GitHub 的三大作用

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=10|讲义 PDF 第 10 页]]、[[Claude code入门与GitHub协作开发.pdf#page=11|讲义 PDF 第 11 页]]

- **跳板工具**：将代码托管到 GitHub 后，可一键部署到 Vercel、Netlify、Render 等平台，实现快速上线。
- **存档备份**：每次提交都是版本快照，改崩了可随时回滚。
- **开源协作**：浏览他人项目，学习或复用代码。

### 4.2 将本地项目首次推送到 GitHub

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=11|讲义 PDF 第 11 页]]

#### 步骤一：在 GitHub 网页端新建仓库

- 点击右上角 + → New repository → 填写仓库名 → 点击 Create repository。

#### 步骤二：本地初始化并提交

在项目文件夹中打开终端（PowerShell 或 Git Bash），执行：

```bash
git init                                 # 初始化本地仓库
git add .                                # 将所有文件加入暂存区
git commit -m "first commit"             # 提交，备注信息
```

#### 步骤三：关联远程仓库并推送

```bash
git remote add origin 你的仓库地址       # 仓库地址在 GitHub 新建仓库页可复制
git push -u origin main                  # 第一次推送，-u 建立关联
```

推送成功后，刷新 GitHub 页面即可看到文件。

### 4.3 日常代码更新流程

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=11|讲义 PDF 第 11 页]]

每次修改代码后，只需三步：

```bash
git add .
git commit -m "改了什么功能或修复了什么"
git push
```

备注技巧：让 AI 帮你写备注，你无需自己绞尽脑汁。

### 4.4 常见报错及解决

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=12|讲义 PDF 第 12 页]]

#### 报错 1：网络连接不上

终端默认不走代理，开启梯子的虚拟网卡模式（TUN）。或手动设置代理：

```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

取消代理：

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

#### 报错 2：远端版本高于本地（rejected）

错误提示 `[rejected] main -> main (fetch first)`。

原因：你在 GitHub 网页上直接修改了代码，或别人推送了新版本，导致远端比本地新。

解决：先拉取合并，再推送：

```bash
git pull origin main    # 拉取远端并合并到本地
git push                # 再推送
```

---

## 五、如何高效逛 GitHub（找到优质项目）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=13|讲义 PDF 第 13 页]]、[[Claude code入门与GitHub协作开发.pdf#page=14|讲义 PDF 第 14 页]]

核心思路：把 GitHub 当“抖音”刷，用 AI 替你筛选，人工只看必要部分。

### 5.1 整体流程

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=13|讲义 PDF 第 13 页]]

```text
描述你的项目需求（喂给 AI，如 CLAUDE.md）
         ↓
AI 推荐相关项目 + Awesome 系列辅助
         ↓
快速筛选：Stars 数 + 最近 commit 时间（排除死项目）
         ↓
AI 分析项目健康度（用链接）
         ↓
人工精读 Issue（只看 Closed 和 Bug 类）
```

### 5.2 第一步：让 AI 帮你找相关项目

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=13|讲义 PDF 第 13 页]]

- 将你项目的 `CLAUDE.md`（项目说明）内容复制给大模型（如 Claude、DeepSeek）。
- 提示：“帮我在 GitHub 上找与这个项目强相关的开源项目，列出链接和简介。”
- AI 会返回一批候选，省去你盲目搜索的时间。

### 5.3 第二步：快速筛选——看 Star 和活跃度

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=13|讲义 PDF 第 13 页]]

- **Star 数量**：相当于点赞，含金量较高，可作为质量参考（但也可能有水分，需结合其他指标）。
- **活跃度**：点进项目，查看最近一次 commit 时间。如果超过半年没更新，大概率是“死项目”，不建议依赖。

### 5.4 第三步：AI 健康度审计（深度筛选）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=13|讲义 PDF 第 13 页]]

将项目链接发给 AI，使用以下提示词：

```text
请作为高级架构师，对这个 GitHub 项目 [链接] 进行“健康度审计”。重点检索并分析：
1. 更新频率：过去 6 个月内是否有实质性的代码提交（Commits）？
2. 版本历史：最近一次 Release 是什么时候？是否兼容当前的 Python/Node.js 主流版本？
3. 社区响应：最近 10 个 Issue 的平均回复周期是多少？是否存在大量积压的 Bug 类标签？
4. 维护风险：它是单人维护还是组织维护？
最终结论：请直接告诉我这个项目是“处于活跃期”、“进入维护期”还是“已经脑死亡”。
```

AI 会给出明确结论，帮你决定是否采用。

### 5.5 第四步：人工精读 Issue（评论区）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=14|讲义 PDF 第 14 页]]

为什么要看 Issue：Issue 是项目的“评论区”，能反映真实问题和维护态度。

#### 了解两个基本概念

- **状态（State）**：
  - Open：问题尚未解决。
  - Closed：问题已关闭（可能已解决，也可能维护者决定不修）。
- **标签（Label）**：
  - bug：明确的错误，需重点关注。
  - wontfix：维护者承认问题但不打算修（高价值排雷信息）。
  - duplicate：重复反馈，跳转至主 Issue 追踪。
  - help wanted / good first issue：适合外部贡献者参与。
  - question：普通提问。

#### 人工看什么？

- 看 Closed 中带绿色对勾（已完成）的：了解功能是否已实现。
- 看 Closed 中带斜杠圆圈（未计划关闭）的：了解哪些问题被放弃修复，可能影响你的使用。
- 看所有带 bug 标签的 Issue：了解系统已知缺陷，评估风险。

这是唯一需要人工精读的部分，因为 AI 难以准确判断 Issue 内容对你的具体影响。

---

## 六、实战示例：微信机器人项目（课程演示项目）

> 本部分对应课程实录后半段，项目基于 wx4py 骨架开发。  
> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=15|讲义 PDF 第 15 页]]、[[Claude code入门与GitHub协作开发.pdf#page=16|讲义 PDF 第 16 页]]、[[Claude code入门与GitHub协作开发.pdf#page=17|讲义 PDF 第 17 页]]

### 6.1 项目功能

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=15|讲义 PDF 第 15 页]]

- 群消息自动总结：记录群聊消息，过滤后生成摘要。
- @问答：在群中 @机器人，可进行实时联网问答。
- 定时任务：每天零点自动总结，早上 8 点推送 AI 早报（需配置 Tavily 密钥）。

### 6.2 环境与依赖

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=16|讲义 PDF 第 16 页]]、[[Claude code入门与GitHub协作开发.pdf#page=17|讲义 PDF 第 17 页]]

- Python 3.10 ~ 3.12（验证命令：`python --version`）
- 核心依赖：`wx4py`、`pywinauto`、`pywin32`、`pillow`、`requests`
- 可选依赖（联网搜索）：`tavily`（需注册 Tavily 和 Serper 获取 API 密钥）

安装依赖：

```bash
pip install wx4py pywinauto pywin32 pillow requests tavily
```

### 6.3 配置文件 config.py（关键）

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=17|讲义 PDF 第 17 页]]

```python
DEEPSEEK_API_KEY = "sk-你的密钥"           # 必填，模型接口
TAVILY_API_KEY = "tvlv-你的Tavily密钥"    # 可选，联网搜索
SERPER_API_KEY = "你的Serper密钥"         # 可选，备用搜索
LISTEN_GROUPS = ["你要监听的群名"]        # 目前仅支持一个群
BOT_NAME = "机器人的微信昵称"             # 小号昵称
```

说明：DeepSeek 密钥必填。两个搜索密钥都不填则联网功能静默跳过；填任意一个则联网搜索可用，但早报功能仅认 Tavily。

### 6.4 启动流程

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=17|讲义 PDF 第 17 页]]、[[Claude code入门与GitHub协作开发.pdf#page=18|讲义 PDF 第 18 页]]、[[Claude code入门与GitHub协作开发.pdf#page=19|讲义 PDF 第 19 页]]

1. 登录微信 PC 客户端，目标群聊窗口必须可见（不能最小化），并置顶（方便程序抓取）。
2. 在项目文件夹打开终端，运行：

```bash
python main.py
```

看到 `机器人启动中...` 即成功。若未配置 Tavily，会打印 `未配置 Tavily API key，跳过AI早报调度器`，属正常行为。

### 6.5 注意事项

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=18|讲义 PDF 第 18 页]]、[[Claude code入门与GitHub协作开发.pdf#page=19|讲义 PDF 第 19 页]]

- 目前仅支持监听 **一个群聊**（后续版本扩展）。
- 需要电脑持续开机运行（可后续部署到云端）。
- 微信官方对自动化打击较严，建议使用 **小号** 降低风险。

---

## 七、GitHub 提交备注技巧

> 课程讲义对应：[[Claude code入门与GitHub协作开发.pdf#page=11|讲义 PDF 第 11 页]]

课堂问题：为什么 commit 要写备注？

- 备注会显示在 GitHub 仓库的提交历史右侧，方便你快速定位版本状态。
- 你无需自己思考备注内容，让 AI 帮你生成备注，你复制粘贴即可。
- 这样每次更新都能清晰记录改动点，便于日后回滚或比较。

---

## 八、总结与资源链接

### 关键命令速查

| 操作 | 命令 |
|---|---|
| 安装 CC（镜像） | `irm https://daheiai.com/cc.ps1 \| iex` |
| 启动 CC | 项目文件夹终端输入 `claude` |
| 初始化项目 | `/init` |
| 查看上下文占比 | `/cost` |
| 压缩上下文 | `/compact` |
| 清空对话 | `/clear` |
| 切换模式 | `Shift + Tab` |
| Git 首次推送 | `git init → git add . → git commit -m "..." → git remote add origin ... → git push -u origin main` |
| Git 日常更新 | `git add . → git commit -m "..." → git push` |
| 解决远端领先 | `git pull origin main → git push` |

### 参考资源

- 课程讲义：[[Claude code入门与GitHub协作开发.pdf|Claude code入门与GitHub协作开发.pdf]]（需与本文件同目录）
- 微信机器人项目（课堂演示）：详见讲义及课堂实录，项目文件已随课下发。
- 两个搜索 API 平台（用于联网功能）：
  - [Tavily](https://app.tavily.com/)
  - [Serper](https://serper.dev/)

最后提醒：AI 工具迭代迅速，遇到问题多问 CC 本身，让它帮你安装新 Skills 或排查错误。保持“先少装，用够再加”的原则，把精力放在项目本身而非工具上。

---

## Obsidian 链接检查

> [!IMPORTANT]
> 如果讲义页码链接无法跳转，请检查以下两点：
>
> 1. PDF 文件名必须完全等于：`Claude code入门与GitHub协作开发.pdf`
> 2. PDF 必须和本 Markdown 文件在同一个 Obsidian Vault 文件夹中。
>
> 本文使用的 PDF 页码跳转格式为：
>
> ```markdown
> [[Claude code入门与GitHub协作开发.pdf#page=1|讲义 PDF 第 1 页]]
> ```

---

## 相关笔记

- [[Codex++使用教程]]
- [[Claude Code 从 0 到 1 完全使用教程（Obsidian版）]]
- [[Codex模型配置方法大全]]
- [[SKILL的定义以及使用]]
- [[Codex使用教程]] — Codex 安装与使用指南
