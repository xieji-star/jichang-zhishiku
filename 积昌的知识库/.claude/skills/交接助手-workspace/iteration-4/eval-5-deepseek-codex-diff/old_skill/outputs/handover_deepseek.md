# 知识库自动化整理项目 交接文档（给 DeepSeek Harness 版）

> 项目名：kb-auto-organizer（知识库自动化整理工具）
> 交接对象：DeepSeek Harness（AI 智能体）
> 交接日期：2026-08-18
> 交接关系：A = 前任 Claude Code（做到约一半）→ B = 你（DeepSeek Harness）

---

## 0. 交接摘要（启动包）

**项目是什么**：一个 Python 工具，自动整理 Obsidian 知识库（`E:\积昌的知识库 - 副本`）：把 `收件箱\` 里的散乱文件按内容关键词自动分类，移动到 `已整理好的文件\<分类>\`，并自动补 `[[双向链接]]` 到索引页 `index.md`。

**当前做到哪一步**：A（Claude Code）已完成约 50%。收件箱扫描（`scanner.py` ✅）和关键词分类（`classifier.py` 🔶，只覆盖 3 个分类）可用；主入口 `main.py` 只有骨架；链接（`linker.py`）和移动（`mover.py`）两个模块完全未写。测试 5 条过、2 条挂。

**A 没做完的（接力棒）**，共 5 件：
1. 分类规则从 3 类扩到 6 类（补「会议纪要 / 项目笔记 / 文献笔记」）；
2. 写 `linker.py` 补双向链接；
3. 写 `mover.py` 按分类移动文件（重名加时间戳）；
4. `main.py` 把 linker / mover 接进去跑通全流程；
5. 修 2 条失败测试 + 补新模块测试，全套跑绿。

**B 下一步第一件事**：先扩充 `rules\category_rules.json` 补 3 个分类（推荐规则已直接贴在下方第 6 节 #1 行，可直接照抄），因为 `test_classifier.py` 的 2 条失败就是差这 3 类。

**最省力提示**：你主要靠对话记忆、读不到本地文件、也一般不执行命令。本文档已把所有关键文件内容直接贴在正文（第 2、6 节），你**直接基于正文内容续写代码**即可，不要尝试自己读文件或跑命令。所有验证信号都设计成「请用户代跑命令看输出」的形式（见第 7 节核对清单）。

---

## 1. 项目总览与验收标准

- 一句话定位：把知识库「收件箱」的散乱文件自动分类归位 + 补双向链接的 Python 工具。
- 最终目标：一条 `python main.py` 命令，自动完成「扫描 → 分类 → 补链接 → 归位」，并在 `已整理好的文件\index.md` 生成索引。
- 验收标准（可检验）：
  - ✅ 6 个分类都能正确分到文件；
  - ✅ 每个整理后的文件在 `index.md` 有 `[[链接]]`；
  - ✅ 文件被移动到 `已整理好的文件\<分类>\` 下，重名自动加时间戳；
  - ✅ `python -m pytest tests\ -v` 全部通过。

---

## 2. 文件地图（自包含版——关键内容已直接贴出）

> 🔶 路径信息基于 A 的记录，你读不到文件系统，**路径仅供用户核对**。你直接使用下面贴出的代码内容续写，不要试图打开文件。

```
E:\积昌的知识库 - 副本\kb-auto-organizer\
├── main.py                    # 主入口，骨架已完成，linker/mover 未接
├── core\
│   ├── __init__.py            # 空文件
│   ├── scanner.py             # ✅ 完成：scan_inbox()
│   ├── classifier.py          # 🔶 80%：classify()
│   ├── linker.py              # ❌ 未写：build_links()
│   └── mover.py               # ❌ 未写：move_organized()
├── rules\category_rules.json  # 🔶 只含 3 类，需扩到 6 类
├── tests\
│   ├── test_scanner.py        # ✅ 5 条通过
│   └── test_classifier.py     # 🔶 5 条中 2 条失败
├── config.toml                # ✅ 配置（内容见下）
└── requirements.txt           # ✅ 依赖清单
```

### 关键文件内容（直接贴出，你据此续写）

**config.toml**（✅确定）：
```toml
inbox = "收件箱"
organized_root = "已整理好的文件"
index_file = "已整理好的文件/index.md"
languages = ["中文"]
auto_move = true
```

**core\scanner.py**（✅确定，已完成，勿改）：
```python
from pathlib import Path

def scan_inbox(inbox_dir: str) -> list[dict]:
    """扫描收件箱，返回待整理文件清单。"""
    items = []
    for entry in Path(inbox_dir).rglob("*"):
        if entry.is_file() and entry.suffix.lower() in {".md", ".pdf", ".docx"}:
            items.append({
                "path": str(entry),
                "name": entry.name,
                "mtime": entry.stat().st_mtime,
                "size": entry.stat().st_size,
            })
    return items
```

**core\classifier.py**（🔶80%，配合新规则即可用，勿大改）：
```python
from pathlib import Path

def classify(path: str, rules: dict) -> str:
    """按关键词规则给文件打分，返回最高分分类名。"""
    name = Path(path).name
    head = ""
    if path.endswith(".md"):
        head = "\n".join(Path(path).read_text(encoding="utf-8").splitlines()[:20])
    text = name + " " + head
    best, best_score = "未分类", 0
    for category, kw in rules.items():
        score = sum(text.count(k) for k in kw)
        if score > best_score:
            best, best_score = category, score
    return best
```

**rules\category_rules.json**（🔶当前内容，需扩充）：
```json
{
  "工作文档": ["周报", "日报", "SOP", "排期", "会议"],
  "学习笔记": ["课程", "教程", "笔记", "方法论"],
  "灵感碎片": ["灵感", "想法", "TODO", "待办"]
}
```

**main.py**（🔶骨架，`main()` 第 12 行有 TODO）：
```python
import json
import tomllib
from pathlib import Path
from core.scanner import scan_inbox
from core.classifier import classify

def main():
    cfg = tomllib.loads(Path("config.toml").read_text(encoding="utf-8"))
    items = scan_inbox(cfg["inbox"])
    rules = json.loads(Path("rules/category_rules.json").read_text(encoding="utf-8"))
    for it in items:
        it["category"] = classify(it["path"], rules)
        # TODO: 接入 linker.build_links() 和 mover.move_organized()（未完成）
    return items

if __name__ == "__main__":
    main()
```

---

## 3. 已完成工作（全量逐条）

| # | 做了什么 | 产出物 | 证据/状态 |
|---|---------|--------|----------|
| 1 | 收件箱扫描模块 | `core\scanner.py` 的 `scan_inbox()` | ✅ test_scanner.py 5 条通过 |
| 2 | 关键词规则分类器 | `core\classifier.py` 的 `classify()` | 🔶 基本可用，缺新分类规则致 2 条测试挂 |
| 3 | 主入口骨架 | `main.py` 的 `main()` | 🔶 只走 scanner→classifier，linker/mover 未接 |
| 4 | 基础配置与依赖 | `config.toml`、`requirements.txt` | ✅ 内容见第 2 节 |
| 5 | 初始分类规则 | `rules\category_rules.json`（3 类） | 🔶 需扩到 6 类 |

---

## 4. 当前精确进度

- 最后一步有效操作（🔶按 A 的记录）：A 写完 `classify()`，跑了一次 `pytest`，`test_scanner.py` 5 过，`test_classifier.py` 3 过 2 挂（缺「会议纪要」类规则）。
- 当前代码状态：`main()` 里 linker / mover 是 TODO；运行 `main.py` 目前只会打印分类结果、不会真正移动文件。

---

## 5. A 没做完的事（接力棒，全量逐条）

> 以下 5 件是 A 留给你的「接力棒」，是你的起点，不是你的过错。优先级：🔴紧急 = 阻塞后续；🟡重要 = 核心功能；一般 = 收尾。

| # | 还差什么 | 为什么没做完（阻塞原因） | 前置条件 | 优先级 | 做到什么算完成 |
|---|---------|------------------------|---------|--------|---------------|
| 1 | `category_rules.json` 补「会议纪要/项目笔记/文献笔记」3 类 | A 时间不够，只建了 3 类 | 无 | 🔴紧急 | 6 个分类都能分到文件 |
| 2 | 写 `core\linker.py` 的 `build_links()` | 未排到 | #1 完成 | 🔴紧急 | 整理后文件在 index.md 有 `[[链接]]` |
| 3 | 写 `core\mover.py` 的 `move_organized()` | 未排到 | #1 完成 | 🔴紧急 | 文件移入 `<分类>\`，重名加时间戳 |
| 4 | `main()` 接入 linker/mover 跑通全流程 | #2 #3 未写，无法接线 | #2 #3 | 🟡重要 | `python main.py` 一条命令全流程 |
| 5 | 修 2 条失败测试 + 补 linker/mover 测试 | 模块未写完无法测 | #2 #3 #4 | 🟡重要 | `pytest` 全绿 |

---

## 6. A→B 接力总览（自包含版，读到就能开工）

> 你读不到文件，所以「从哪开始」列已把关键内容直接贴进来。验证信号需要用户帮你代跑命令，用户看到什么算成功见「做到什么算完成」列。

| # | A 没做完的（接力棒） | 你要做什么 | 从哪开始（关键内容已贴出） | 做到什么算完成（验证信号） |
|---|--------------------|-----------|--------------------------|---------------------------|
| 1 | 分类规则只有 3 类 | 把 `category_rules.json` 扩到 6 类 | 在现有 JSON 上新增 3 组（直接复制下面推荐规则）：`"会议纪要": ["例会", "复盘", "议题", "决议"]`、`"项目笔记": ["项目", "里程碑", "需求", "进度"]`、`"文献笔记": ["论文", "文献", "doi", "引用"]` | 🔶 用户代跑 `python -c "import json;print(list(json.load(open('rules/category_rules.json'))))"`，应输出 6 个分类名 |
| 2 | linker.py 未写 | 新建 `core\linker.py`，实现 `build_links(organized, index_path)`：读取 index.md 文本，为每个整理文件追加一行 `- [[文件名去扩展名]]` | 用第 2 节贴出的 `config.toml` 里 `index_file` 配置；函数签名与 `main.py` 风格保持一致（见第 2 节） | 🔶 用户代跑 `python main.py` 后打开 `已整理好的文件\index.md`，能看到新增 `[[xxx]]` 链接行 |
| 3 | mover.py 未写 | 新建 `core\mover.py`，实现 `move_organized(items, organized_root)`：按 `item["category"]` 移动，重名时文件名追加 `_时间戳` | 用第 2 节贴出的 `config.toml` 里 `organized_root` 与 `auto_move=true`；用标准库 `shutil.move` | 🔶 用户代跑后，`收件箱\` 文件消失，`已整理好的文件\<分类>\` 出现对应文件 |
| 4 | main() 未接线 | 在 `main()` 的 TODO 处（第 2 节贴出的 main.py 第 12 行）依次调用 `linker.build_links()`、`mover.move_organized()` | 改 main.py：在 `for` 循环外、`return items` 之前插入两个调用；函数名要与 #2 #3 里你定的签名一致 | ✅ 用户代跑 `python main.py` 不报错且完成移动 |
| 5 | 测试不全/有挂 | 修 `test_classifier.py` 2 条用例（补新分类断言）+ 新增 `test_linker.py`、`test_mover.py` | 测试目录在 `tests\`，参考 `test_scanner.py` 的写法（用临时目录 fixture） | ✅ 用户代跑 `python -m pytest tests\ -v`，全部 passed |

**接力开工第一步**：先把 #1 的 3 组新分类规则写进 `category_rules.json`（照本表格直接贴）→ 请用户代跑 #1 的验证命令 → 看到输出 6 个分类名，就算正式接上了。

---

## 7. 给用户的核对清单（请用户逐条代跑/核对）

> 因为你读不到文件、不能执行命令，以下每条都需要**用户**帮你在本地确认。这是针对「读不到文件的智能体」的兜底机制。

- ❓ **核对路径**：确认项目确实在 `E:\积昌的知识库 - 副本\kb-auto-organizer\`。若有出入，把第 2 节路径与本表改对再继续。
- ❓ **代跑测试**：在项目目录执行 `python -m pytest tests\ -v`，把输出贴回对话（当前应看到 `5 passed, 2 failed`）。
- ❓ **代跑验证**：每完成一个接力项，按第 6 节「验证信号」把命令输出贴回来，一起判断是否算完成。
- ❓ **环境确认**：`requirements.txt` 里是 `pytest`；若用户机器没装 pytest，代跑 `pip install pytest`。
- ❓ **Python 版本**：`main.py` 用了 `tomllib`（需 Python 3.11+），请用户代跑 `python --version` 核对；版本过低则第 2 节 main.py 里的 `import tomllib` 需改成 `import tomli`。

---

## 8. 环境与配置依赖（自包含）

- 语言/依赖：Python 3.11+（`tomllib` 需 3.11+）、pytest。`requirements.txt` 内容（✅确定）：`pytest>=7.0`
- 模型/API：无。本工具纯本地运行，不调任何大模型 API。
- 密钥/token：无。
- ⚠️ 注意：`tomllib` 是 Python 3.11 新增，若用户版本过低需改用 `tomli`（见第 7 节核对项）。

---

## 9. 数据与状态快照

- 数据位置：`收件箱\`（待整理源）、`已整理好的文件\`（归位目标）。
- 当前状态：收件箱里应有若干 `.md` 待整理文件（🔶 具体数量需用户 `Get-ChildItem 收件箱 -Recurse -File` 核对）。
- 临时/中间产物：无，无需清理。

---

## 10. 关键决策与踩坑记录

- 选 Python 而非 PowerShell 脚本：跨平台 + 文本处理方便（✅ A 已定，勿改）。
- 分类用「关键词打分取最高分」而非硬性命中：容错更高，A 已验证可用（🔶 若后续误分类多，可改为「关键词权重」）。
- 踩坑：`classify()` 只读 .md 的前 20 行，PDF 因读不了文本会永远「未分类」（❓ 本期接受，后续是否接 PDF 文本提取待用户确认）。

---

## 11. 风险与待确认项

- ❓ 路径信息来自 A 的记忆，可能不准，务必让用户按第 7 节核对。
- ❓ PDF 分类当前为「未分类」，本期接受，下期再处理。
- ❓ `auto_move=true` 表示自动移动；若用户想先预览再移动，可改成 `false`（需用户确认偏好）。

---

## 12. 按 DeepSeek Harness 定制的附加内容

本文档已按 `references/agent-profiles.md` 第 3 节（DeepSeek Harness 档案）定制：

- **自包含**：关键代码、配置、规则内容全部贴进正文（第 2、6 节），你无需读文件即可续写；
- **证据分级**：每条信息标注 ✅确定 / 🔶推断 / ❓待确认，防止你「记岔」后用户难以识别哪些要复核；
- **人工代跑验证**：验证信号全部设计成「用户代跑命令看输出」，弥补你不能执行命令的短板；
- **人工核对清单**：第 7 节单独给出给用户的核对清单，让路径/环境偏差能被兜住；
- **精简高密度**：优先写「当前状态 + 下一步」，历史流水账已压缩，节省你有限的上下文。
