# 知识库自动化整理项目 交接文档（给 Codex 版）

> 元信息：交接项目「知识库自动化整理项目」｜交接对象 **Codex（L1 自治型）**｜交接日期 2026-08-18
>
> 本版说明：Codex 能读本地文件、能跑 PowerShell 命令，所以本文档**只给精确路径 + PowerShell 命令 + 函数级定位**，不贴大段代码（你自己读文件补细节）。指令为"目标+要点"式，可紧凑但路径/函数/命令必须精确。**开跑前先检查 `config.toml`**（见 §8）。

---

## 0. 交接摘要（启动包）

- **项目**：知识库收件箱自动整理工具（Python）。扫描 `E:\积昌的知识库 - 副本\收件箱` → 解析 → 按 `config.yaml` 分类 → 移入 `已整理好的文件\` → 重建 `自动维护知识库\index.md` 索引与 `[[双向链接]]`。项目根：`E:\积昌的知识库 - 副本\自动化整理\`（下文 `项目根\`）。
- **当前进度**：约 70%。核心链路 `scan→parse→categorize→move→link` 已跑通，`run.ps1` 一键执行成功（log 末行 `[OK] organize done`）。
- **接力棒（A 未完成 5 件）**：① `ingest.py:parse_pdf()` 扫描版 PDF 缺 OCR 兜底（紧急）；② `config.yaml` 去重阈值 `0.92` 误报率高；③ 未注册 Windows 定时任务；④ `report.py` 周报未实现；⑤ 测试 3/8。
- **第一件事**：接①，在 `ingest.py` 的 `parse_pdf()`（第 120 行）异常分支加 OCR。改完自己跑 `run.ps1` 验证。

---

## 1. 项目总览与验收标准

- **定位**：收件箱分拣机器人——文件丢进收件箱，跑一次自动归位 + 更新索引。
- **验收**：① 任意测试文件经 `run.ps1` 后落在 `已整理好的文件\` 正确分类且重命名；② `自动维护知识库\index.md` 每次运行自动更新、无重复链接；③ 扫描版 PDF 也能提取正文（OCR）；④ 每周自动出周报（条数/耗时/失败清单）；⑤ `python -m pytest` = `8 passed`。

---

## 2. 文件地图（精确路径 · 你自行读文件补细节）

| 文件 | 作用 | 状态 | 关键接续点 |
|------|------|------|-----------|
| `项目根\run.ps1` | 一键入口（scan→parse→categorize→move→link） | ✅ 完成 | 无需改 |
| `项目根\config.yaml` | 分类规则 + 去重参数 | ✅ 完成 | `dedup.similarity_threshold` 待改（接力棒②） |
| `项目根\ingest.py` | 扫描 + 解析 | ⚠️ 缺 OCR | `scan_inbox()` 第 40 行；`parse_pdf()` 第 120 行（接力棒①） |
| `项目根\organize.py` | 分类 + 移动 | ✅ 完成 | `categorize()` 第 85 行；`apply_rules()` 第 150 行；`is_duplicate()` 约第 210 行（接力棒②） |
| `项目根\linker.py` | 链接 + 索引重建 | ✅ 完成 | `update_index()` 第 60 行 |
| `项目根\tests\test_organize.py` | 测试（3/8） | ⚠️ 未完成 | 需补 `test_ingest.py`/`test_linker.py`/`test_dedup.py` |
| `项目根\requirements.txt` | 依赖 | ✅ 完成 | `pypdf, pyyaml, pytest` |
| `项目根\logs\organize.log` | 运行日志 | ✅ | 行首 `[OK]`/`[FAIL]`/耗时字段可解析（周报数据源） |
| `项目根\.venv\Scripts\python.exe` | 虚拟环境 | ✅ | 所有命令用它 |

---

## 3. 已完成工作（全量逐条 · 4 字段）

| # | 做了什么 | 产出物 | 验证 | 关键数据 |
|---|---------|--------|------|---------|
| ✅1 | `scan_inbox()` 扫描收件箱 | `ingest.py:40` | `& "$env:ROOT\.venv\Scripts\python.exe" -c "from ingest import scan_inbox; print(len(scan_inbox()))"` | md/txt/pdf，按 mtime 倒序 |
| ✅2 | 文本解析（md/txt/文本型 PDF） | `ingest.py:120` `parse_pdf()` | 对 1 个文本型 PDF 调 `parse_pdf()` 能返回正文 | 扫描版 0 通过（→①） |
| ✅3 | 分类引擎 | `organize.py:85` `categorize()` + `config.yaml` | `python -m pytest`（现 3 例）3 passed | 12 个分类 |
| ✅4 | 归档移动 + 重命名 | `organize.py:150` `apply_rules()` | 跑 `run.ps1` 后文件进入正确分类 | 命名：`分类_日期_原名` |
| ✅5 | 双向链接 + 索引重建 | `linker.py:60` + `自动维护知识库\index.md` | 跑 `run.ps1` 后 index.md 有新条目 | 无重复链接 |
| ✅6 | 一键脚本 + 日志 | `run.ps1` + `logs\organize.log` | 跑 `run.ps1` 后 log 末行 `[OK] organize done` | 端到端跑通 |

---

## 4. 当前精确进度

- 最后有效操作：`run.ps1` 端到端成功，`logs\organize.log` 末行 `[OK] organize done`。
- 代码状态：`ingest.py` 遇到扫描版 PDF 抛 `PdfTextExtractError` 中断整批（`run.ps1` 的 `$ErrorActionPreference="Stop"` 会停下）。`organize.py` 主循环未做单文件异常隔离。测试 3/8。
- 数据状态：`收件箱\` 约 20 个待整理文件（❓需人工确认）；各分类目录已建好。

---

## 5. A 没做完的事（接力棒 · 全量逐条 · 七要素）

### ① 扫描版 PDF 缺 OCR 兜底 —— 紧急
- **还差什么**：`parse_pdf()` 无文本层直接 raise，整批中断。
- **为什么**：OCR 依赖（tesseract/easyocr）未装、中文识别未验证。
- **前置**：装 tesseract+`chi_sim` 或 `pip install easyocr`。
- **优先级**：紧急。
- **完成定义**：对 1 个扫描版 PDF 调 `parse_pdf()` 返回非空中文。
- **从哪开始**：`ingest.py:120` 的 `if not text.strip(): raise ...` 分支。
- **验证信号**：`run.ps1` 后 log 有 `[OCR] page ok`，且不再因扫描版中断。

### ② 去重误报高 —— 重要
- **还差什么**：`similarity_threshold: 0.92` 把"同题不同日"误判为重复。
- **为什么**：阈值未调优，标题未先剥日期字段。
- **前置**：先用"同题不同日期"样本复现。
- **优先级**：重要。
- **完成定义**：5 组相似不重复样本误报 0；3 组真重复仍识别。
- **从哪开始**：`config.yaml` 的 `dedup` 段 + `organize.py` `is_duplicate()`（约 210 行）。
- **验证信号**：补 `test_dedup.py` 全绿。

### ③ 未注册定时任务 —— 一般
- **还差什么**：无计划任务，`run.ps1` 只能手动跑。
- **为什么**：权限/方式未定搁置。
- **前置**：`run.ps1` 稳定跑通（✅已满足）。
- **优先级**：一般。
- **完成定义**：`schtasks /Query /TN KBAutoOrganize` 可查到，`/Run` 触发有 `[OK]`。
- **从哪开始**：见 §7 步骤 C 的 `schtasks /Create` 命令（管理员身份）。
- **验证信号**：`/Run` 后 log 有 `[OK] organize done`。

### ④ 周报未实现 —— 一般
- **还差什么**：无统计模块，需按周聚合输出 `周报.md`。
- **为什么**：排在 OCR 之后未排上。
- **前置**：① ② 完成后 log 格式稳定。
- **优先级**：一般。
- **完成定义**：`python report.py --week` 生成含条数/耗时/失败清单的 `周报.md`。
- **从哪开始**：新建 `项目根\report.py`，解析 `logs\organize.log`。
- **验证信号**：周报与 log 手工统计一致。

### ⑤ 测试 3/8 —— 重要
- **还差什么**：缺 `test_ingest.py`/`test_linker.py`/`test_dedup.py` 共 5 例。
- **为什么**：功能优先于测试。
- **前置**：① ② 完成后行为稳定。
- **优先级**：重要。
- **完成定义**：`python -m pytest` = `8 passed`。
- **从哪开始**：新建三个测试文件（见 §7 步骤 E）。
- **验证信号**：8 passed。

---

## 6. A→B 接力总览（开工清单 · 入口=PowerShell命令+函数级定位）

| # | A 没做完的（接力棒） | B 要做什么 | 从哪开始 | 做到什么算完成（验证信号） |
|---|--------------------|-----------|---------|---------------------------|
| ① | 扫描版 PDF 缺 OCR | 给 `parse_pdf()` 加 OCR 兜底 | `ingest.py:120`，改 `if not text.strip(): raise ...` 分支为 OCR 调用 | 自己跑 `run.ps1`，log 有 `[OCR] page ok`、不中断 |
| ② | 去重误报高 | 提阈值 + 先剥日期再比 | `config.yaml` `similarity_threshold`→`0.95`；`organize.py:210` `is_duplicate()` | 新建 `test_dedup.py` 跑 5 组样本误报 0 |
| ③ | 未注册定时任务 | `schtasks` 注册每日 22:00 | 管理员 PowerShell 跑 §7 步骤 C 命令 | `schtasks /Query /TN KBAutoOrganize` 可查 + `/Run` 有 `[OK]` |
| ④ | 周报未实现 | 新建 `report.py` 聚合 log | `项目根\report.py`（解析 `logs\organize.log`） | `python report.py --week` 生成周报且数据吻合 |
| ⑤ | 测试 3/8 | 补 5 例 | 新建 `tests\test_ingest.py`/`test_linker.py`/`test_dedup.py` | `python -m pytest` = `8 passed` |

> **接力开工第一步**：改 `ingest.py:120` 的 `parse_pdf()` 异常分支加 OCR → 跑 `powershell -File "E:\积昌的知识库 - 副本\自动化整理\run.ps1"` → 看 `logs\organize.log` 出现 `[OK] organize done`（且扫描版不再中断）即正式接上。

---

## 7. 下一步行动计划（目标+要点 · PowerShell 命令级）

**立即做**：步骤 A、B。**之后做**：步骤 C、D、E。

### 步骤 A（接①）：OCR 兜底
1. 读 `ingest.py:120`，把 `if not text.strip(): raise PdfTextExtractError(...)` 改为：优先 `pytesseract.image_to_string(img, lang="chi_sim")`，或 `easyocr.Reader(["ch_sim","en"], gpu=False).readtext(str(path), detail=0)`；返回非空文本并在 `logging` 记 `[OCR] page ok`。
2. 检查依赖：`& "$env:ROOT\.venv\Scripts\python.exe" -m pip show pytesseract easyocr`，缺则装。
3. 验证：`powershell -File "E:\积昌的知识库 - 副本\自动化整理\run.ps1"`，log 不再中断。

### 步骤 B（接②）：修去重
1. `config.yaml`：`similarity_threshold: 0.92` → `0.95`。
2. `organize.py` `is_duplicate()`（约 210 行）：比对前 `re.sub(r"\d{4}[-年]\d{1,2}[-月]\d{1,2}", "", title)` 剥日期。
3. 新建 `tests\test_dedup.py`：5 组相似不重复（期望不判重）+ 3 组真重复（期望判重）。
4. 验证：`& "$env:ROOT\.venv\Scripts\python.exe" -m pytest` 相关用例绿。

### 步骤 C（接③）：注册计划任务
```powershell
schtasks /Create /TN KBAutoOrganize /TR "powershell -File E:\积昌的知识库 - 副本\自动化整理\run.ps1" /SC DAILY /ST 22:00 /F
schtasks /Query /TN KBAutoOrganize
schtasks /Run /TN KBAutoOrganize
```
验证：`/Query` 可查到、`/Run` 后 log 有 `[OK]`。

### 步骤 D（接④）：写 `report.py`
- 新建 `report.py`：逐行解析 `logs\organize.log`，按行首 `[OK]`/`[FAIL]` 计数、解析耗时字段、收集失败清单，`--week` 按 ISO 周过滤，输出 `自动维护知识库\周报\周报_<date>.md`。`argparse` 实现 `--week`。
- 验证：`& "$env:ROOT\.venv\Scripts\python.exe" report.py --week` 生成文件且数字吻合。

### 步骤 E（接⑤）：补测试
- `tests\test_ingest.py`：`scan_inbox` 返回非空（1 例）、`parse_pdf` 解析文本型 PDF（1 例）。
- `tests\test_linker.py`：链接写入（1 例）、索引去重（1 例）。
- `tests\test_dedup.py`：见步骤 B（1 例）。
- 验证：`& "$env:ROOT\.venv\Scripts\python.exe" -m pytest` = `8 passed`。

---

## 8. 环境与配置依赖（完整清单）

- **运行时**：Python `.venv`（`E:\积昌的知识库 - 副本\自动化整理\.venv\Scripts\python.exe`）；依赖 `pypdf/pyyaml/pytest` 已装；OCR 依赖（`pytesseract`/`easyocr`）待装。
- **⚠️ config.toml 提醒**：本机 Codex 若走第三方模型/供应商，先检查 `C:\Users\asus\.codex\config.toml` 的 model/provider 配置是否可用；若需调 deepseek 等第三方模型，确认其 API 供应商配置正确，避免运行时报模型不可用。
- **网络**：项目纯本地文件操作，无外网依赖；但**安装 OCR 依赖（pip）与下载 tesseract 需联网**，若网络受限先处理代理/分流（参考知识库 Codex 网络故障档案）。
- **密钥**：无任何 token/密钥（纯本地）。
- **会话迁移提示**：如需跨机迁移，复制 `C:\Users\asus\.codex\sessions\*.jsonl` 即可（**不要拷 `auth.json`**）。

---

## 9. 数据与状态快照

- `收件箱\`：约 20 个待整理文件（❓人工确认数量）。
- `logs\organize.log`：多次运行记录，末行 `[OK] organize done`。
- `已整理好的文件\`：分类目录已建、已有归档（❓数量待核）。
- 临时产物：`__pycache__\` 可清；无必须保留的中间数据。

---

## 10. 关键决策与踩坑记录

- **pypdf 而非 pdfplumber**：中文排版简单、依赖轻；对扫描版同样无能为力（故需 OCR）。
- **YAML 配置分类而非硬编码**：便于不改代码加分类。
- **坑：扫描版 PDF 抛错中断整批**——`$ErrorActionPreference="Stop"` 下 `run.ps1` 遇错即停。**建议**：`organize.py` 主循环加单文件 try/except 隔离，随步骤 A 一起改。
- **坑：difflib 直接比标题，同题不同日误判为重复**——先剥日期再比（步骤 B）。
- **放弃方案**：`watchdog` 实时监听 → 常驻进程+开机自启复杂，改计划任务方案。

---

## 11. 风险与待确认项（❓）

- ❓ 收件箱待整理文件数量（约 20）。
- ❓ 本机 tesseract 及 `chi_sim` 是否已装（决定 OCR 走 pytesseract 还是 easyocr）。
- ❓ 用户是否有 `schtasks /Create` 所需管理员权限。
- ❓ `C:\Users\asus\.codex\config.toml` 当前 model/provider 配置是否可用（接任务前自查）。
- 🔶 `organize.py` 主循环缺单文件异常隔离（建议随步骤 A 修）。

---

## 12. 续作启动手册（环境还原 · 你自己跑）

1. 确认环境：`dir "E:\积昌的知识库 - 副本\自动化整理"`、`.venv` 存在；自查 `config.toml`（§8）。
2. 跑 `powershell -File "E:\积昌的知识库 - 副本\自动化整理\run.ps1"`。
3. **验证续上**：`Get-Content "E:\积昌的知识库 - 副本\自动化整理\logs\organize.log" -Tail 5`，看到 `[OK] organize done` 即环境正常、可开始步骤 A；看到 `PdfTextExtractError` 即先做步骤 A。
4. 与 §6 接力总览关系：§6 是"接 A 的活"的开工清单，本节是"把 A 的环境跑起来"的还原步骤。
