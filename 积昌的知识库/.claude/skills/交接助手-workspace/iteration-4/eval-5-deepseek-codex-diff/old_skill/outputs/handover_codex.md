# 知识库自动化整理项目 交接文档（给 Codex 版）

> 项目名：kb-auto-organizer（知识库自动化整理工具）
> 交接对象：Codex（OpenAI 智能体）
> 交接日期：2026-08-18
> 交接关系：A = 前任 Claude Code（做到约一半）→ B = 你（Codex）

---

## 0. 交接摘要（启动包）

- **项目**：`E:\积昌的知识库 - 副本\kb-auto-organizer\`，Python 工具，自动把 Obsidian 知识库 `收件箱\` 的文件分类归位到 `已整理好的文件\<分类>\` 并补 `[[双向链接]]`。
- **当前进度**：约 50%。`scanner.py` ✅、`classifier.py` 🔶（3/6 分类）、`main.py` 骨架（`main.py:12` 有 TODO，linker/mover 未接）、`tests` 5 过 2 挂。
- **A 没做完的（接力棒）**：扩分类规则到 6 类 → 写 `linker.py` → 写 `mover.py` → `main()` 接线 → 修测试跑绿。
- **B 下一步第一件事**：从第 6 节 #1 开始，先 Read `rules\category_rules.json`，补 3 个分类，再跑 `python -m pytest tests\test_classifier.py -v` 验证 2 条失败转绿。
- **你的能力**：能读本地文件、能跑 PowerShell。直接按第 7 节命令级计划执行；动手前先 Read 目标文件再改。

---

## 1. 项目总览与验收标准

- 一句话定位：见上。
- 验收标准（可检验）：
  - ✅ 6 个分类正确分类；
  - ✅ `已整理好的文件\index.md` 有新增 `[[链接]]`；
  - ✅ 文件移入 `<分类>\`，重名自动加时间戳；
  - ✅ `python -m pytest tests\ -v` 全绿。

---

## 2. 文件地图（精确路径）

| 路径 | 作用 | 状态 |
|------|------|------|
| `kb-auto-organizer\main.py` | 主入口，`main()` | 🔶 骨架，TODO 在 main.py:12 |
| `kb-auto-organizer\core\scanner.py` | `scan_inbox()` 扫描收件箱 | ✅ 完成 |
| `kb-auto-organizer\core\classifier.py` | `classify()` 关键词分类 | 🔶 80%，打分逻辑在 classify() 第 8-10 行 |
| `kb-auto-organizer\core\linker.py` | `build_links()` 补双向链接 | ❌ 未创建 |
| `kb-auto-organizer\core\mover.py` | `move_organized()` 移动归位 | ❌ 未创建 |
| `kb-auto-organizer\rules\category_rules.json` | 分类规则 | 🔶 仅 3 类 |
| `kb-auto-organizer\tests\test_scanner.py` | 扫描测试 | ✅ 5 过 |
| `kb-auto-organizer\tests\test_classifier.py` | 分类测试 | 🔶 2 挂 |
| `kb-auto-organizer\config.toml` | 配置 | ✅ |
| `kb-auto-organizer\requirements.txt` | 依赖 | ✅ |

> 三个入口优先 Read：`main.py:8-13`（接线点）、`core\classifier.py:4-12`（分类逻辑）、`rules\category_rules.json`（规则数据）。

---

## 3. 已完成工作（全量逐条）

| # | 做了什么 | 产出物/位置 | 验证 |
|---|---------|------------|------|
| 1 | 扫描模块 | `core\scanner.py` 的 `scan_inbox()` | `python -m pytest tests\test_scanner.py -v` 5 过 |
| 2 | 分类器 | `core\classifier.py` 的 `classify()` | 🔶 3/5 过，缺类规则 |
| 3 | 主入口骨架 | `main.py` 的 `main()` | 🔶 运行只打印分类、不移动 |
| 4 | 配置/依赖 | `config.toml`、`requirements.txt` | ✅ |
| 5 | 初始规则 | `rules\category_rules.json` | 🔶 3 类 |

---

## 4. 当前精确进度

- 最后有效操作（🔶）：A 写完 `classify()`，跑 `pytest` 得 `test_scanner.py` 5 过、`test_classifier.py` 3 过 2 挂。
- 当前代码状态：`main.py:12` 处 TODO（linker/mover 未接）；`classify()` 只读 .md 前 20 行；PDF 会分类为「未分类」。

---

## 5. A 没做完的事（接力棒，全量逐条）

| # | 还差什么 | 为什么没做完 | 前置条件 | 优先级 |
|---|---------|-------------|---------|--------|
| 1 | 分类规则扩到 6 类（补会议纪要/项目笔记/文献笔记） | A 只建了 3 类 | 无 | 🔴紧急 |
| 2 | 新建 `core\linker.py` 实现 `build_links()` | 未排到 | #1 | 🔴紧急 |
| 3 | 新建 `core\mover.py` 实现 `move_organized()` | 未排到 | #1 | 🔴紧急 |
| 4 | `main.py:12` TODO 接入 linker/mover | #2 #3 未写 | #2 #3 | 🟡重要 |
| 5 | 修 test_classifier 2 挂 + 补 linker/mover 测试 | 模块未写完 | #2 #3 #4 | 🟡重要 |

---

## 6. A→B 接力总览（PowerShell + 函数级定位）

| # | A 没做完的（接力棒） | 你要做什么 | 从哪开始（命令/文件:行号/函数） | 做到什么算完成（验证信号） |
|---|--------------------|-----------|------------------------------|---------------------------|
| 1 | 分类规则只有 3 类 | 在 `rules\category_rules.json` 追加 3 组关键词：会议纪要 / 项目笔记 / 文献笔记 | Read `rules\category_rules.json`，仿照现有 3 组的 JSON 结构追加（数组值：`["例会","复盘","议题","决议"]`、`["项目","里程碑","需求","进度"]`、`["论文","文献","doi","引用"]`） | 跑 `python -m pytest tests\test_classifier.py -v`，2 条失败转绿 |
| 2 | linker.py 未写 | 新建 `core\linker.py`：`build_links(organized: list[dict], index_path: str)`，读取 index.md，对每个 item 追加 `- [[文件名去扩展名]]` | 参考 `main.py:5` 的 `index_file` 配置；文件放 `core\linker.py` | 跑 `python main.py` 后，`Get-Content '已整理好的文件\index.md'` 能看到 `[[` 链接行 |
| 3 | mover.py 未写 | 新建 `core\mover.py`：`move_organized(items, organized_root)`，用 `shutil.move`，重名时文件名加 `_YYYYMMDD_HHMMSS` | 参考 `config.toml` 的 `organized_root` 与 `auto_move`；用标准库 `shutil` | 跑 `python main.py` 后，`Get-ChildItem '已整理好的文件' -Directory` 能看到 6 个分类目录 |
| 4 | main() 未接线 | 在 `main.py:12` TODO 处，先 `from core.linker import build_links`、`from core.mover import move_organized`，循环结束后依次调用 | 编辑 `main.py`（Read 后改第 9-14 行） | `python main.py` 退出码 0、无 traceback |
| 5 | 测试不全/有挂 | 修 `tests\test_classifier.py` 失败用例（断言新分类）+ 新建 `tests\test_linker.py`、`tests\test_mover.py` | 仿 `tests\test_scanner.py` 的临时目录 fixture 写法 | `python -m pytest tests\ -v` 全部 passed |

**接力开工第一步**：
```
cd E:\积昌的知识库 - 副本\kb-auto-organizer; python -m pytest tests\test_classifier.py -v
```
看到 `2 failed` 的报错（这就是 #1 的起点）→ 改 `rules\category_rules.json` 补 3 类 → 再跑同一条命令转绿即接上。

---

## 7. 下一步行动计划（命令级，PowerShell）

**立即做：**
1. `cd E:\积昌的知识库 - 副本\kb-auto-organizer`
2. Read `rules\category_rules.json` → 追加 3 组分类 → 跑 `python -m pytest tests\test_classifier.py -v` 直到绿。
3. Read `main.py`、`core\classifier.py` → 按第 6 节 #2 #3 新建 `core\linker.py`、`core\mover.py`。
4. 改 `main.py:12` 接线，跑 `python main.py` 验证全流程。
5. 补测试，跑 `python -m pytest tests\ -v` 全绿。

**之后做：**
6. 可选：处理 PDF 分类（`classify()` 目前对 PDF 返回「未分类」，可接 `pypdf` 提取文本）。❓ 需用户确认是否本期要做。

---

## 8. 环境与配置依赖

- **Python**：3.11+（`main.py` 用 `tomllib`）。先跑 `python --version` 核实。
- **依赖**：见 `requirements.txt`（`pytest>=7.0`）。
- ⚠️ **模型配置（Codex 专用提醒）**：本工具本身不调 API，但注意 `C:\Users\asus\.codex\config.toml` —— 若你的 Codex 配置了第三方模型（如 deepseek），确认已配好，避免你自己无法运行。
- **网络**：本工具纯本地，无外网依赖；若你的 Codex 环境访问 OpenAI 需走专用节点，保持既有代理/分流即可，与项目无关。
- **会话迁移（可选）**：本机 Codex 会话在 `C:\Users\asus\.codex\sessions\*.jsonl`；跨机迁移拷 sessions 即可，**不要拷 auth.json**。
- **密钥/token**：项目无密钥；你自己的认证凭据不要外泄。

---

## 9. 数据与状态快照

- 源：`收件箱\`（含若干 .md，具体数量跑 `(Get-ChildItem '收件箱' -Recurse -File).Count` 核对）。
- 目标：`已整理好的文件\` 下按分类建目录。
- 中间产物：无。运行后 `收件箱\` 应为空。

---

## 10. 关键决策与踩坑记录

- 选 Python 而非 PowerShell 脚本：跨平台 + 文本处理方便（✅ A 已定，勿改）。
- 分类算法：关键词打分取最高分，容错高（🔶 若误分类多可改权重）。
- 坑：`classify()` 只读 .md 前 20 行，PDF 恒为「未分类」；本期接受，见第 7 节「之后做」。
- 坑：`tomllib` 需 Python 3.11+，机器版本需先核实（`python --version`）。

---

## 11. 风险与待确认项

- ❓ 收件箱文件数量/样本需你 Read 核对后，确认分类规则关键词是否合理。
- ❓ PDF 分类本期做不做，需用户确认。
- ❓ `auto_move=true` 为自动移动；用户是否要先预览再移动（可临时改 `false`）。

---

## 12. 按 Codex 定制的附加内容

本文档已按 `references/agent-profiles.md` 第 2 节（Codex 档案）定制：

- **PowerShell 命令**：全文命令为 Windows 风格（`cd ...; python ...`、`Get-Content`、`Get-ChildItem`、`(Get-ChildItem ...).Count`）；
- **函数级定位**：接力总览「从哪开始」列给 `文件:行号` + 函数名 + 命令（如 `main.py:12`、`build_links()`、`classify()` 第 8-10 行），你直接基于现状续改；
- **config.toml 提醒**：第 8 节提醒检查 `C:\Users\asus\.codex\config.toml` 模型配置；
- **会话可迁移**：第 8 节说明 sessions 迁移方式（拷 sessions 不拷 auth.json）；
- **网络注意事项**：第 8 节标注代理/分流要求；
- **明确当前代码状态**：第 4 节写清 `main.py:12` TODO、`classify()` 对 PDF 的行为，便于你续接。
