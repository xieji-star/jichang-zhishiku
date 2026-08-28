# 知识库自动化整理项目 交接文档（给 DeepSeek Harness 版）

> 元信息：交接项目「知识库自动化整理项目」｜交接对象 **DeepSeek Harness（L3 对话型）**｜交接日期 2026-08-18
>
> 本版说明：DeepSeek Harness 主要靠对话记忆工作，可能读不到本地文件、上下文有限、容易记岔。因此**本文档把关键代码、配置、命令全部贴进正文**，每步只做一件事、验证靠"请用户代跑"，并附**证据分级（✅确定 / 🔶推断 / ❓待确认）**与**文末用户核对清单**。照着念就能执行，不需要你去读任何文件。

---

## 0. 交接摘要（启动包，500 字速览）

**项目是什么**：一个把"知识库收件箱"自动整理成"已整理好的文件"的 Python 自动化工具。它扫描 `收件箱\` 下的新文件 → 解析内容 → 按 `config.yaml` 的关键字规则分类 → 移动到 `已整理好的文件\` 对应分类 → 最后重建 `自动维护知识库\index.md` 的索引与双向链接。项目目录固定为 **`E:\积昌的知识库 - 副本\自动化整理\`**（以下简写为 `项目根\`）。

**做到哪一步**：整体约 **70%**。✅ 已完成：收件箱扫描、文本解析（md/txt/文本型 PDF）、分类规则引擎（12 类）、归档移动、双向链接与索引重建、一键运行脚本。❌ 未完成 5 件（详见第 5 节接力棒）：**① 扫描版 PDF 缺 OCR 兜底；② 模糊去重误报率高；③ 未注册 Windows 定时任务；④ 周报生成未实现；⑤ 测试只写了 3/8**。

**最关键三件事**：
- 已完成的：核心链路 `scan → parse → categorize → move → link` 能跑通，`run.ps1` 一键执行成功。
- A 没做完的（接力棒）：见上 5 件，每件都写满了七要素。
- B 下一步第一件事：**先接接力棒①（OCR 兜底）**——在 `ingest.py` 的 `parse_pdf()` 抛错分支里加 OCR 调用，然后请用户跑一次扫描验证。

**从哪继续最省力**：先读本文档第 5/6/7 节——接力总览表里每一步都把"该贴的代码"贴好了，你按 #1 的"从哪开始"直接产出代码让用户替换即可，**全程不需要读任何本地文件**。

---

## 1. 项目总览与验收标准

- **一句话定位**：知识库收件箱的自动分拣机器人——把零散放进收件箱的笔记/PDF，自动归位到知识库正确文件夹并刷新索引。
- **最终目标**：用户每天只需把文件丢进 `收件箱\`，跑一次 `run.ps1`，全部文件自动分类归档、索引自动更新、每周自动出一份整理周报。
- **验收标准（做到什么程度算完成）**：
  1. 对任意测试文件跑 `run.ps1` 后，该文件出现在 `已整理好的文件\` 的**正确分类**下，且文件名按规则重命名；
  2. `自动维护知识库\index.md` 的链接清单随每次运行自动更新，无重复链接；
  3. 扫描版（无文字层）PDF 也能提取到正文（OCR 兜底）；
  4. 每周一自动生成上周整理周报，统计条数/耗时/失败清单；
  5. 8 个测试用例全绿。

---

## 2. 文件地图（自包含版：关键文件内容直接贴给你）

> 你读不到本地文件，所以这里把每个关键文件的位置、作用、**核心内容**都贴出来了。路径以 `项目根\` = `E:\积昌的知识库 - 副本\自动化整理\` 表示。

| 文件 | 作用 | 当前状态 | 核心内容（直接贴出） |
|------|------|---------|---------------------|
| `项目根\run.ps1` | 一键运行入口（扫描→解析→分类→归档→索引） | ✅ 已完成 | 见下方【代码块 1】 |
| `项目根\config.yaml` | 分类规则 + 去重参数（**改这里就能加分类**） | ✅ 已完成 | 见下方【代码块 2】 |
| `项目根\ingest.py` | 扫描收件箱 + 解析文件；`parse_pdf()` 第 120 行**是 OCR 兜底要改的地方** | ✅ 基本完成，⚠️ 缺 OCR | 见下方【代码块 3】 |
| `项目根\organize.py` | 分类 + 移动归档；`categorize()` 第 85 行 | ✅ 已完成 | 见下方【代码块 4】 |
| `项目根\linker.py` | 生成 `[[双向链接]]` + 重建 index.md；`update_index()` 第 60 行 | ✅ 已完成 | 功能点见正文 |
| `项目根\tests\test_organize.py` | 测试（只写了 3/8） | ⚠️ 未完成 | 见第 5 节接力棒⑤ |
| `项目根\requirements.txt` | 依赖清单 | ✅ 已完成 | `pypdf, pyyaml, pytest, difflib`（difflib 是标准库） |
| `项目根\logs\organize.log` | 每次运行的日志 | ✅ 存在 | 见第 9 节 |

**【代码块 1】`run.ps1`（已完成，无需改，运行入口）**
```powershell
# 一键整理入口：扫描收件箱 → 解析 → 分类 → 归档 → 重建索引
$ErrorActionPreference = "Stop"
$root = "E:\积昌的知识库 - 副本\自动化整理"
$py = Join-Path $root ".venv\Scripts\python.exe"
Push-Location $root
& $py ingest.py
& $py organize.py
& $py linker.py
Pop-Location
```

**【代码块 2】`config.yaml`（已完成；分类在此配置，共 12 类，摘录 3 类为例）**
```yaml
categories:
  - name: 实习就业
    keywords: [实习, 简历, JD, 求职, 面试, offer, 背调]
    target: 已整理好的文件/实习就业/
  - name: 工作文件
    keywords: [SOP, 业务线, 周报, 述职, 工作流]
    target: 已整理好的文件/工作文件/
  - name: 飞书收集
    keywords: [飞书, 消息, 群聊, 收集箱]
    target: 已整理好的文件/飞书收集/
  # …… 其余 9 类同理（简历模板/会议纪要/脚本资料/受众报告等）
dedup:
  similarity_threshold: 0.92   # 当前阈值——见接力棒②，误报率高
  ignore_keys: [日期, 时间]     # 去重时忽略的标题字段
```

**【代码块 3】`ingest.py`（核心，OCR 兜底要在这里改）**
```python
INBOX = r"E:\积昌的知识库 - 副本\收件箱"
SUPPORTED = {".md", ".txt", ".pdf"}

def scan_inbox(inbox_dir: str = INBOX) -> list:
    """扫描收件箱，返回待处理文件（按修改时间倒序）"""
    from pathlib import Path
    files = [p for p in Path(inbox_dir).rglob("*")
             if p.suffix.lower() in SUPPORTED and p.is_file()]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

def parse_pdf(path) -> str:
    """提取 PDF 文本；扫描版(无文本层)会抛 PdfTextExtractError —— 这就是接力棒①要加 OCR 的地方"""
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise PdfTextExtractError(f"无可提取文本: {path.name}（疑似扫描版）")
    return text
```

**【代码块 4】`organize.py`（已完成，分类逻辑）**
```python
def categorize(doc: dict):
    """按 config.yaml 关键字规则分派目标目录；未命中返回 None"""
    text = (doc["title"] + "\n" + doc["content"])[:2000]
    for cat in RULES["categories"]:
        if any(k in text for k in cat["keywords"]):
            return cat["target"]
    return None
```

**【代码块 5】`linker.py` 功能点（已完成）**：`collect_links()` 扫描 `已整理好的文件\` 各分类文件 → `update_index(nav)` 第 60 行把 `[[双向链接]]` 写回 `自动维护知识库\index.md`；每次运行先清空旧链接再重建，保证不重复。

---

## 3. 已完成工作（全量逐条 · 每条 4 字段）

| # | 做了什么 | 产出物在哪 | 怎么验证有效 | 关键数据/效果 |
|---|---------|-----------|-------------|--------------|
| ✅1 | 收件箱扫描器 `scan_inbox()` | `项目根\ingest.py` 第 40 行 | 请用户跑 `& "E:\积昌的知识库 - 副本\自动化整理\.venv\Scripts\python.exe" -c "from ingest import scan_inbox; print(len(scan_inbox()))"`，看到数字与收件箱文件数一致 | 支持 md/txt/pdf；按修改时间倒序 |
| ✅2 | 文本解析：md/txt 全文、文本型 PDF | `ingest.py` 的 `parse_pdf()` 第 120 行 | 请用户对 1 个文本型 PDF 跑上面命令改 `print(parse_pdf(Path("该PDF路径")))`，能打印出正文 | 文本型 PDF 全部通过；**扫描版 0 通过（→接力棒①）** |
| ✅3 | 分类规则引擎 `categorize()` | `organize.py` 第 85 行 + `config.yaml` | 请用户跑 `python -m pytest`（只跑现有 3 例），3 passed | 已配置 **12 个分类**、关键字命中率约 90%（🔶推断） |
| ✅4 | 归档移动 + 重命名 | `organize.py`（`apply_rules()` 第 150 行） | 跑 `run.ps1` 后，看收件箱文件是否进入 `已整理好的文件\` 对应分类 | 移动后按「分类_日期_原名」重命名 |
| ✅5 | 双向链接 + 索引重建 | `linker.py` 第 60 行 + `自动维护知识库\index.md` | 跑 `run.ps1` 后请用户打开 index.md，看到新文件条目与 `[[链接]]` | 每次运行重建，无重复 |
| ✅6 | 一键运行脚本 + 日志 | `run.ps1` + `logs\organize.log` | 请用户跑 `powershell -File "E:\积昌的知识库 - 副本\自动化整理\run.ps1"`，log 出现 `[OK] organize done` | 端到端跑通（✅确定） |

---

## 4. 当前精确进度

- **最后一次有效操作**：跑通了 `run.ps1` 端到端链路，`logs\organize.log` 最后一行是 `[OK] organize done`（✅确定）。
- **代码状态**：`ingest.py`/`organize.py`/`linker.py` 主体完成；`parse_pdf()` 遇到扫描版 PDF 会抛 `PdfTextExtractError` 中断整批（这是最需要优先处理的坑）；`tests\test_organize.py` 目前只有 3 个用例。
- **数据状态**：`收件箱\` 尚有约 20 个待整理文件未归档（❓需用户确认数量）；`已整理好的文件\` 各分类目录已建好。

---

## 5. A 没做完的事（接力棒 · 全量逐条 · 每条七要素 + 证据分级）

> 这些是前任（A = Claude Code）留下的接力棒，是 B（你）的起点，不是过错。每条都标注了证据分级：✅确定 / 🔶推断 / ❓待确认。

### 接力棒① 扫描版 PDF 缺 OCR 兜底 —— 优先级：紧急
- **还差什么**：`parse_pdf()` 遇到无文本层 PDF 直接抛错，整批中断；缺一个 OCR 兜底分支，把图片型 PDF 转成文本。
- **为什么没做完**：A 在做完文本型 PDF 后，OCR 依赖（tesseract/EasyOCR）未装好、且中文识别准确率未验证，卡在依赖上（✅确定）。
- **前置条件**：确认本机已装 `tesseract`（含中文 `chi_sim` 语言包）或可安装 `easyocr`；未装需先装。
- **优先级**：紧急（当前一遇扫描版就全批失败）。
- **做到什么算完成**：对 1 个扫描版 PDF 跑 `parse_pdf()`，能返回非空中文文本。
- **从哪开始**：改 `ingest.py` 第 120 行 `parse_pdf()`——在 `if not text.strip():` 分支里，把 `raise` 换成 OCR 调用（参考第 7 节步骤 A 的贴出代码）。
- **验证信号**：请用户跑一次扫描版 PDF 解析，看到返回中文文本、且 `logs\organize.log` 有 `[OCR] page 1 ok` 行。

### 接力棒② 模糊去重误报率高 —— 优先级：重要
- **还差什么**：`config.yaml` 的 `dedup.similarity_threshold: 0.92` 用 difflib 算标题相似度，把"同标题不同日期/不同批次"的文件误判成重复而跳过归档。
- **为什么没做完**：阈值靠拍脑袋定的，未做误报/漏报调优；`ignore_keys` 的过滤只在标题层生效，正文层未生效（🔶推断）。
- **前置条件**：先复现——用一个"标题相同但日期不同"的样本跑一遍去重。
- **优先级**：重要（影响归档完整性）。
- **做到什么算完成**：对 5 组手工构造的"相似但不重复"样本，误报为 0；对 3 组真重复样本，仍能识别。
- **从哪开始**：改 `config.yaml` 的 `dedup` 段 + `organize.py` 的去重函数（`is_duplicate()` 约第 210 行）。
- **验证信号**：请用户跑测试，看到 `test_dedup.py` 全绿（该测试文件待你创建）。

### 接力棒③ 未注册 Windows 定时任务 —— 优先级：一般
- **还差什么**：没有计划任务，`run.ps1` 只能手动跑；需注册为每日 22:00 自动运行。
- **为什么没做完**：A 不确定用 `schtasks` 还是任务计划程序 GUI，且担心管理员权限，一直搁置（✅确定）。
- **前置条件**：`run.ps1` 能稳定跑通（✅已满足）。
- **优先级**：一般（核心链路已可手动用）。
- **做到什么算完成**：运行 `schtasks /Query /TN "KBAutoOrganize"` 能查到该任务，且手动触发一次能跑出 `[OK] organize done`。
- **从哪开始**：请用户用管理员 PowerShell 跑第 7 节步骤 C 贴出的 `schtasks /Create` 命令。
- **验证信号**：任务列表出现 `KBAutoOrganize`，下次到点自动执行（可用 `/Run` 手动触发验证）。

### 接力棒④ 周报生成未实现 —— 优先级：一般
- **还差什么**：没有统计模块；需按周汇总「整理条数 / 耗时 / 失败清单」输出 `周报.md` 到 `自动维护知识库\周报\`。
- **为什么没做完**：排在 OCR（接力棒①）之后，优先级低没排上（✅确定）。
- **前置条件**：① ② 完成后日志格式稳定（`logs\organize.log` 每行已有 `[OK]`/`[FAIL]` 前缀可解析）。
- **优先级**：一般。
- **做到什么算完成**：跑 `python report.py --week` 能生成一份含条数/耗时/失败清单的 `周报.md`。
- **从哪开始**：新建 `项目根\report.py`（解析 `logs\organize.log` 按周聚合）。
- **验证信号**：请用户打开生成的 `周报.md`，数据与 `logs\organize.log` 手工统计一致。

### 接力棒⑤ 测试只写了 3/8 —— 优先级：重要
- **还差什么**：`tests\test_organize.py` 只有 3 个用例；缺 `test_ingest.py`、`test_linker.py`、`test_dedup.py`，共需补 5 个用例到 8 个。
- **为什么没做完**：A 先跑通功能再补测试，测试排在功能之后（✅确定）。
- **前置条件**：① ② 完成后功能行为稳定。
- **优先级**：重要（防止后续改动回归）。
- **做到什么算完成**：`python -m pytest` 输出 `8 passed`。
- **从哪开始**：补 `tests\test_ingest.py`（scan 与 parse 各 1 例）、`test_linker.py`（2 例）、`test_dedup.py`（1 例）。
- **验证信号**：8 passed。

---

## 6. A→B 接力总览（读到就能开工 · 自包含版）

> "从哪开始"列**把关键代码/内容直接贴出来**，你不用读文件；"做到什么算完成"列给的是"请用户代跑什么命令、看到什么输出"。

| # | A 没做完的（接力棒） | B 要做什么 | 从哪开始（贴内容） | 做到什么算完成（验证信号） |
|---|--------------------|-----------|------------------|---------------------------|
| ① | 扫描版 PDF 缺 OCR 兜底 | 在 `parse_pdf()` 抛错分支加 OCR | 改 `ingest.py`，把 `if not text.strip(): raise PdfTextExtractError(...)` 替换成：`try: import easyocr; rdr=easyocr.Reader(["ch_sim","en"]); txt="\n".join(rdr.readtext(str(path), detail=0)); return txt if txt.strip() else ""`（如装 tesseract 则用 `pytesseract.image_to_string`） | 请用户对 1 个扫描版 PDF 跑解析，返回非空中文；log 有 `[OCR] page 1 ok` |
| ② | 模糊去重误报率高 | 调 `config.yaml` 阈值 + 修 `is_duplicate()` | 把 `similarity_threshold: 0.92` 提到 `0.95`；在 `organize.py` 的 `is_duplicate()`（约第 210 行）对标题先剥掉日期字段再比对 | 请用户跑 5 组"相似不重复"样本，误报 0；3 组真重复仍识别 |
| ③ | 未注册定时任务 | 用 `schtasks` 注册每日 22:00 | 请用户以管理员身份跑：`schtasks /Create /TN KBAutoOrganize /TR "powershell -File E:\积昌的知识库 - 副本\自动化整理\run.ps1" /SC DAILY /ST 22:00 /F` | `schtasks /Query /TN KBAutoOrganize` 能查到；`/Run` 后 log 有 `[OK]` |
| ④ | 周报生成未实现 | 新建 `report.py` 解析 log 按周聚合 | 新建 `项目根\report.py`：按 `logs\organize.log` 行首 `[OK]`/`[FAIL]`/耗时 字段分组聚合，输出到 `自动维护知识库\周报\周报_YYYYMMDD.md` | 请用户跑 `python report.py --week`，生成的周报与 log 手工统计一致 |
| ⑤ | 测试只写 3/8 | 补 5 个用例到 8 个 | 新建 `tests\test_ingest.py`（scan+parse 各 1）、`tests\test_linker.py`（2）、`tests\test_dedup.py`（1） | 请用户跑 `& "E:\积昌的知识库 - 副本\自动化整理\.venv\Scripts\python.exe" -m pytest`，`8 passed` |

> **接力开工第一步**：你（B）先产出接力棒①的 `parse_pdf()` OCR 改法，把替换后的完整函数贴给用户 → 用户替换 `ingest.py` 后运行 `powershell -File "E:\积昌的知识库 - 副本\自动化整理\run.ps1"` → 请用户把 log 最后几行贴给你，看到 `[OK] organize done` 即正式接上（✅）。

---

## 7. 下一步行动计划（步骤最小化 · 每步只做一件事 · 验证靠人代跑）

> **立即做** = 步骤 A、B（影响核心链路）；**之后做** = 步骤 C、D、E。每步都只做一件事，做完停下问用户"是否看到指定输出"，再进下一步。

### 步骤 A（立即 · 接接力棒①）：给 `parse_pdf()` 加 OCR 兜底
1. 把 `ingest.py` 中 `parse_pdf()` 整段替换成下面的样子（改动处已注释）：
```python
def parse_pdf(path) -> str:
    """提取 PDF 文本；无文本层时用 easyocr 兜底"""
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if text.strip():
        return text
    # —— OCR 兜底（新增）——
    import easyocr                      # 前置：pip install easyocr
    rdr = easyocr.Reader(["ch_sim", "en"], gpu=False)
    pages_txt = [rdr.readtext(str(path), detail=0)]
    ocr_text = "\n".join("\n".join(p) for p in pages_txt)
    import logging; logging.info("[OCR] page ok")
    return ocr_text
```
2. **完成信号**：请用户替换后跑 `powershell -File "E:\积昌的知识库 - 副本\自动化整理\run.ps1"`，把 log 贴给你——看到 `[OK] organize done` 且之前中断的扫描版文件也被处理，步骤 A 完成。

### 步骤 B（立即 · 接接力棒②）：修去重误报
1. 改 `config.yaml` 的 `dedup.similarity_threshold`：`0.92` → `0.95`。
2. 在 `organize.py` 的 `is_duplicate()`（约第 210 行）比对前，先对标题执行"剥日期"：`title = re.sub(r"\d{4}[-年]\d{1,2}[-月]\d{1,2}", "", title)`。
3. **完成信号**：请用户构造 5 组"标题同但日期不同"的文件丢进收件箱跑一遍，确认都不被误判为重复（🔶：若仍误报，再提到 `0.96`）。

### 步骤 C（之后 · 接接力棒③）：注册定时任务
1. 把第 6 节接力棒③ 的 `schtasks /Create` 命令完整贴给用户，请其以管理员身份在 PowerShell 运行。
2. **完成信号**：请用户跑 `schtasks /Query /TN KBAutoOrganize`，看到任务存在即完成。

### 步骤 D（之后 · 接接力棒④）：写 `report.py`
1. 新建 `项目根\report.py`：逐行读 `logs\organize.log`，按行首 `[OK]`/`[FAIL]` 统计条数、按时间字段计算耗时、收集 `[FAIL]` 行为失败清单；按 `--week` 参数过滤本周，输出 Markdown 到 `自动维护知识库\周报\周报_<日期>.md`。
2. **完成信号**：请用户跑 `python report.py --week`，打开生成的周报核对数字与 log 一致。

### 步骤 E（之后 · 接接力棒⑤）：补测试
1. 依次新建 `tests\test_ingest.py`（scan 返回非空、parse 能解析文本型 PDF 各 1 例）、`tests\test_linker.py`（链接写入、去重各 1 例）、`tests\test_dedup.py`（相似不重复不被判重 1 例）。
2. **完成信号**：请用户跑 `python -m pytest`，输出 `8 passed`。

---

## 8. 环境与配置依赖（关键配置直接贴出）

- **Python**：`E:\积昌的知识库 - 副本\自动化整理\.venv\`（虚拟环境，已建好 ✅）。
- **依赖**：`pypdf`、`pyyaml`、`pytest` 已装 ✅；`easyocr` / `pytesseract` **未装**（接力棒① 前置，需用户装）。
- **系统**：Windows（PowerShell）；OCR 若用 tesseract 需装中文语言包 `chi_sim`（❓未确认是否已装）。
- **配置值（已贴出）**：`config.yaml` 的 `similarity_threshold: 0.92`（接力棒② 要改成 0.95）；收件箱路径 `E:\积昌的知识库 - 副本\收件箱`。
- **密钥/token**：本项目无任何 API 密钥（纯本地文件操作，✅确定，无需脱敏）。

---

## 9. 数据与状态快照

- `收件箱\`：尚有约 20 个待整理文件未归档（❓需用户确认数量）。
- `logs\organize.log`：已有多次运行记录，末行为 `[OK] organize done`（✅）。
- `已整理好的文件\`：各分类目录已建好，已有部分归档文件（❓数量待核对）。
- 临时产物：`__pycache__\` 可清可不清，无硬性要求；不涉及需保留的中间数据。

---

## 10. 关键决策与踩坑记录

- **选 Python + pypdf 而非 pdfplumber**：本项目 PDF 多为中文排版简单，pypdf 够用且依赖轻（✅确定）；pdfplumber 更重、对扫描版也无能为力，已弃用。
- **分类规则用 YAML 配置而非硬编码**：方便用户不改代码加分类（✅确定）。
- **踩坑：扫描版 PDF 抛错中断整批**——`parse_pdf()` 未做异常兜底，`run.ps1` 一到扫描版就 `Stop`。**规避方案**：接力棒① 加 OCR；在 `organize.py` 主循环用 try/except 单文件隔离失败（🔶建议顺带做）。
- **踩坑：difflib 直接比标题会把"同题不同日"误判为重复**——规避见接力棒② 先剥日期再比。
- **放弃方案**：曾考虑用 `watchdog` 做实时监听自动触发，因占用常驻进程、开机自启复杂而放弃，改用"计划任务每日定时跑"方案（✅确定）。

---

## 11. 风险与待确认项（逐条 ❓）

- ❓ 收件箱待整理文件的确切数量（约 20 个）。
- ❓ 本机是否已装 tesseract 及中文语言包（决定 OCR 用 easyocr 还是 pytesseract）。
- ❓ 归档文件的现有数量与命名是否符合预期（需要一次人工核对）。
- ❓ `schtasks` 注册是否需要管理员权限 / 用户是否有该权限。
- 🔶 `organize.py` 主循环当前对单个文件失败会中断整批（需加 try/except 隔离，建议随接力棒①一起改）。

---

## 12. 续作启动手册（验证"续上了"靠用户代跑）

> 本手册教你（DeepSeek）接手后如何确认环境是好的——**你跑不了命令，所以全部改成"请用户代跑"**。

1. **请用户运行**：`powershell -File "E:\积昌的知识库 - 副本\自动化整理\run.ps1"`
2. **请用户把 log 贴给你**：`logs\organize.log` 最后 5 行。
3. **判断是否续上**：
   - 看到 `[OK] organize done` → 环境 ✅ 正常，可以开始接力棒①（步骤 A）。
   - 看到 `PdfTextExtractError ... 疑似扫描版` → 正是接力棒① 的报错，按步骤 A 加 OCR 后重跑。
   - 看不到文件 / 报 `python not found` → 让用户确认 `.venv` 是否存在（`dir "E:\积昌的知识库 - 副本\自动化整理\.venv"`）。

### 给用户的核对清单（请用户逐条确认，防你记岔）

| # | 请用户核对 | 期望结果 | 勾选 |
|---|-----------|---------|------|
| 1 | `E:\积昌的知识库 - 副本\自动化整理\` 目录是否存在 | 存在，含 ingest.py/organize.py/linker.py/config.yaml/run.ps1 | ☐ |
| 2 | `.venv\Scripts\python.exe` 是否存在 | 存在 | ☐ |
| 3 | `收件箱\` 是否有待整理文件 | 有（约 20 个） | ☐ |
| 4 | 是否已装 tesseract（含 chi_sim）或愿意 `pip install easyocr` | 二选一可 | ☐ |
| 5 | 跑一次 `run.ps1` 后 log 是否出现 `[OK] organize done` | 出现 | ☐ |
| 6 | `config.yaml` 的 `similarity_threshold` 当前是否为 `0.92` | 是 | ☐ |
| 7 | `自动维护知识库\index.md` 是否已有链接清单 | 有 | ☐ |

> 以上核对若任一项不符，以用户实际反馈为准，不要照抄本文档的假设值。
