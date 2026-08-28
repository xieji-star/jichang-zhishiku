# 项目交接文档：全自动爬取短视频、推文爆款程序

> 交接日期：2026-08-17
> 交接人 A（DeepSeek）：已完成开发 → 交接接收人 B（Claude Code）：继续开发
> 交接状态：**基础链路已通，剩余功能待完成**

---

## 一、项目概览

| 项目项 | 说明 |
|--------|------|
| 项目名称 | 全自动爬取短视频、推文爆款程序 |
| 项目路径 | `D:\全自动爬取短视频、推文爆款程序` |
| 运行环境 | Windows 11 Pro（x64），Python 3.10+ |
| 项目目标 | 全自动采集短视频 / 推文，识别并筛出"爆款"内容 |
| 当前阶段 | 爬虫核心链路已打通，爆款评分模型与全自动调度未完成 |
| 接手方 | Claude Code（B） |

### 交接方已完成的整体链路

```
抖音视频采集 → 主页映射 → ASR 转写 → 本地入库 → 爆款评分（未完成）
推文/热点采集（部分） ────────────┘
```

---

## 二、文件结构与路径

```
D:\全自动爬取短视频、推文爆款程序\
│
├── main.py                  # 程序入口（可手动单次运行）
├── requirements.txt         # Python 依赖清单
├── .env.local               # 密钥/Token 配置（值已脱敏，见 §四）
├── .env.example             # 环境变量模板（可安全提交）
│
├── config\
│   └── settings.py          # 全局配置（采集频率、路径、阈值等）
│
├── crawler\
│   ├── douyin\
│   │   ├── collector.py     # 抖音视频采集器（已实现，链路已通）
│   │   ├── mapper.py        # 主页映射（作者主页 → 作品列表，已实现）
│   │   └── asr.py           # ASR 语音转写（已实现）
│   └── tweet\
│       └── collector.py     # 推文/热点采集器（部分实现，待接调度）
│
├── storage\
│   └── database.py          # 本地入库模块（SQLite，已实现）
│
├── model\
│   ├── __init__.py          # 空文件，模型层占位
│   └── score.py             # ★爆款评分模型（未实现，核心待办）
│
├── scheduler\
│   └── runner.py            # 全自动调度器（部分实现，待接入采集任务）
│
├── scripts\
│   └── run_acceptance.py    # 10 轮验收脚本（已跑 1 轮即被终止）
│
├── tests\
│   └── test_pipeline.py     # 基础链路冒烟测试
│
├── data\                    # 采集结果数据目录
├── logs\                    # 运行日志目录
└── README.md                # 使用说明（简要）
```

> 注：以上结构为当前实际目录的简化描述。接手后第一步应 `ls -R` 复核实际文件树，如有出入以实际为准。

---

## 三、当前进度（完成/未完成清单）

### ✅ 已完成（DeepSeek 交付部分）

1. **爬虫核心**
   - 抖音视频采集 `crawler/douyin/collector.py` — 可采集指定视频/用户作品
   - 主页映射 `crawler/douyin/mapper.py` — 作者主页 → 作品列表映射
   - ASR 转写 `crawler/douyin/asr.py` — 视频语音转写为文本
2. **本地入库** `storage/database.py` — SQLite 落库，基础表结构已建
3. **基础链路验证** — 视频采集 → 映射 → 转写 → 入库 全链路已跑通（冒烟测试通过）

### ❌ 未完成（Claude Code 待办）

| 编号 | 待办项 | 涉及文件 | 优先级 |
|------|--------|----------|:------:|
| T1 | **爆款评分模型层未落地** | `model/score.py`（新建/实现） | 🔴 高 |
| T2 | 部分采集任务未接全自动调度 | `scheduler/runner.py` | 🔴 高 |
| T3 | 10 轮验收仅跑 1 轮即被终止 | `scripts/run_acceptance.py` | 🟡 中 |
| T4 | 根目录尚无 git 基线 | 全项目（`git init`） | 🟡 中 |

### ⚠️ 已知风险 / 注意点

- 10 轮验收仅执行 1 轮即被终止，**后续 9 轮未跑**，稳定性未知，需重跑全量验收。
- `model/` 仅为占位空文件，评分模型逻辑需从零实现（建议先定评分规则再编码）。
- 调度器 `scheduler/runner.py` 只接入了部分任务，抖音采集与推文采集均需接入。
- 全自动调度涉及定时执行，建议先以手动触发方式验证，再上 cron/任务计划。

---

## 四、密钥与环境变量

- 密钥/Token 存放于项目根目录 **`.env.local`**（当前值**已脱敏**）。
- `.env.example` 为模板，仅含键名与占位符，可安全提交 git。
- **接手后必须**：用真实密钥替换 `.env.local` 中脱敏值后再运行采集（脱敏值形如 `XXXX`，直接运行会鉴权失败）。
- `.env.local` 需加入 `.gitignore`，禁止提交进版本库。

| 键名（示例） | 用途 | 说明 |
|--------------|------|------|
| `DOUYIN_TOKEN` | 抖音接口鉴权 | 脱敏中，需替换 |
| `ASR_API_KEY` | ASR 转写服务密钥 | 脱敏中，需替换 |
| `DATABASE_PATH` | SQLite 数据库路径 | 一般无需改 |

---

## 五、运行方式（现有可用命令）

> 以下命令均在项目根目录 `D:\全自动爬取短视频、推文爆款程序` 下执行（PowerShell / CMD）。

### 1. 安装依赖

```powershell
cd /d D:\全自动爬取短视频、推文爆款程序
pip install -r requirements.txt
```

### 2. 单次手动运行（验证链路）

```powershell
python main.py
```

### 3. 冒烟测试（快速验证基础链路）

```powershell
python -m pytest tests/test_pipeline.py -v
```

### 4. 运行验收脚本（10 轮）

```powershell
python scripts/run_acceptance.py
```

---

## 六、下一步具体命令（Claude Code 接手开工顺序）

> 建议严格按 1→5 顺序执行，每步完成后确认结果再进入下一步。

### Step 1：复核实际文件结构与环境

```powershell
cd /d D:\全自动爬取短视频、推文爆款程序
dir /s /b              # 或 ls -R，列出实际文件树，与 §二 对照
python --version       # 确认 Python 版本 ≥ 3.10
pip install -r requirements.txt
```

### Step 2：建立 git 基线（T4）

```powershell
cd /d D:\全自动爬取短视频、推文爆款程序
git init
git add -A
git commit -m "chore: 建立项目 git 基线（承接 DeepSeek 交付代码）"
```

> 提交前确认 `.gitignore` 已包含 `.env.local`、`logs/`、`data/`、`__pycache__/`。

### Step 3：验证已通链路未被破坏

```powershell
python -m pytest tests/test_pipeline.py -v
python main.py          # 单次手动运行，观察日志是否正常入库
```

> 若 `.env.local` 为脱敏值，先替换为真实密钥再运行。

### Step 4：实现爆款评分模型（T1）

在 `model/score.py` 中实现评分逻辑（建议步骤）：

```powershell
# 1. 先定义评分规则：爆款特征打分（完播率、互动率、转写文本关键词等）
# 2. 实现 score 函数：输入入库记录 → 输出爆款指数
# 3. 接入 storage/database.py，将评分结果写回库
# 4. 运行验收脚本回归验证
python scripts/run_acceptance.py
```

### Step 5：接入全自动调度（T2）

```powershell
# 在 scheduler/runner.py 中把抖音采集、推文采集全部接入调度
# 先手动触发跑通：python -m scheduler.runner --once
# 验证通过后配置定时任务（Windows 任务计划程序 / APScheduler）
python -m scheduler.runner --once
python scripts/run_acceptance.py   # 全量 10 轮验收
```

### Step 6：完成验收并提交新基线

```powershell
python scripts/run_acceptance.py   # 跑满 10 轮，确认全部通过
git add -A
git commit -m "feat: 完成爆款评分模型与全自动调度，通过 10 轮验收"
```

---

## 七、验收标准（交付判定）

- [ ] 基础链路冒烟测试全部通过
- [ ] 爆款评分模型已实现并写回库，能输出爆款指数
- [ ] 抖音采集 + 推文采集均已接入全自动调度
- [ ] `run_acceptance.py` 连续跑满 **10 轮**无失败
- [ ] 项目根目录已有 git 基线，`.env.local` 未入库
- [ ] README.md 已更新至与实际功能一致

---

## 八、交接说明

- 本项目由 **A（DeepSeek）** 完成爬虫核心与入库，**B（Claude Code）** 接手剩余功能开发。
- 交接时未提供旧会话上下文，接手方请以本文档 §二 文件结构、§三 进度清单为准，按 §六 顺序开工。
- 遇到与本文档描述不符之处，先以实际代码为准，并同步更新本文档。
