---
title: 多账号的并发池设计
type: 技术方案蓝图
date: 2026-08-14
tags:
  - 多账号并发
  - 并发池
  - 零依赖
  - 标准库
  - 施工蓝图
  - Codex交接
  - 受控并发
  - 登录态隔离
  - 全局限速
  - 串行写队列
source: 本文为 Codex 施工蓝图（2026-08-14），基于 backend\app\services\collection.py + backend\app\providers\mediacrawler.py + backend\app\db.py + backend\app\config.py + start.ps1 六文件代码审计
---

# 🏗️ 多账号的并发池设计：给 Codex 的零依赖施工蓝图（每一步做什么、怎么做）

> [!summary] 概要
> 本文档是"自研多账号并发池"的**施工蓝图**，交付给 Codex 按图施工。核心目标：**在不新增任何 pip 依赖的前提下，把项目现有的"账号严格串行"升级为"账号级受控并发池（2 路起步）"**，全程只使用 Python 标准库（`concurrent.futures` / `threading` / `time` / `queue`）+ 项目已有的 SQLite WAL。蓝图共 **6 个施工步骤**：① config.py 加 4 个配置项 → ② 新建 `multi_account` 包（6 个模块，含完整可抄代码）→ ③ db.py 加 `account_tasks` 表 + 3 个函数 → ④ collection.py 改造 4 处 → ⑤ mediacrawler.py 改造 4 处 → ⑥ start.ps1 支持浏览器按需动态拉起。每一步都写清**做什么 / 怎么做 / 交付物 / 验收点**，最后给出自研组件单测、P0→P4 分阶段验收与安全自检。全程遵循"稳定优先"铁律：**账号并发 2 起步 + 全局限速 1/s + 每账号独立浏览器配置 + 集中串行写库**，绝不"复制 N 路并联"。

## 相关笔记

- [[多账号并发池相关技术栈]] — 本蓝图的调研与选型依据（现成软件技术栈 + GitHub 高Star清单 + 零依赖结论）
- [[多账号不同视频同时采集的技术栈要求]] — 姊妹篇（需装 aiolimiter+tenacity 的插件版改造方案）
- [[多并发池的批量化采集规则]] — 论证篇：为什么现在不能、三座大山、正确姿势
- [[多worker并发池设计思路]] — 母方案：14 条稳定性红线（并发/限速/重试/缓存/断点）
- [[自研平台批量化处理路线]] — 为什么不能"并联 10 路"、瓶颈定性
- [[如何解决人机验证问题]] — 多账号并发的最大风险：风控放大 → 人机验证
- [[3条线路设计]] — 三线路架构（字幕直取→接口级→浏览器）
- [[0814-还没配置好的内容]] — P0 硬缺口、P2 风控组件未集成
- [[Codex对话迁移方案]] — 给 Codex 交接的实施约定
- [[0811-开发日志]] — 实证：5/12 账号失败、120s 硬上限、稳定优先教训

## 索引

- 🎯 [[#1. 蓝图目标与验收总纲]] — 改造要达成什么样、哪些层不许动
- 🔒 [[#2. 改造铁律：Codex 必须遵守的 5 条红线]] — 零依赖 / 接口隔离 / 稳定优先 / 合规 / 安全
- 🗺️ [[#3. 施工总览：6 步走完，每步交付什么]] — 施工地图 + 依赖顺序
- ⚙️ [[#4. 第 1 步：config.py 新增 4 个配置项]] — 做什么 + 完整代码 + 验收
- 🧩 [[#5. 第 2 步：新建 multi_account 包（6 个模块 + 完整代码）]] — 核心施工区，含全部可抄代码
- 🗄️ [[#6. 第 3 步：db.py 新增 account_tasks 表 + 3 个 db 函数]] — 建表 SQL + 函数代码 + 幂等迁移
- ✏️ [[#7. 第 4 步：collection.py 改造 4 处]] — 主战场逐处改法
- 🌐 [[#8. 第 5 步：mediacrawler.py 改造 4 处]] — 采集子进程参数化
- 🚀 [[#9. 第 6 步：start.ps1 支持浏览器按需动态拉起]] — 方案 A 落地
- 🧪 [[#10. 自研组件单测（防"自研 = 不稳"）]] — 3 组单测钉死正确性
- 🪜 [[#11. 分阶段验收（P0→P4）与安全自检]] — 稳定逐级放开 + 3 组放量实验
- 📋 [[#12. 给 Codex 的交付清单与安全注意事项]] — 施工 check-list + 红线提醒

---

## 1. 蓝图目标与验收总纲

### 1.1 改造要达成什么样

| 层级 | 改造前（现状） | 改造后（目标） |
|:--:|------|------|
| **任务级** | `ThreadPoolExecutor(max_workers=1)` + `CollectionBusyError`，同一时刻只允许一个采集任务 | **保持不变**（仍是单任务，任务内部才并发账号） |
| **账号级** | `for index, name in enumerate(accounts)` 严格串行 | **账号级受控并发池**：`ThreadPoolExecutor(2~3)`，一次放 2~3 个账号同时采各自的多个视频 |
| **单账号内视频级** | `--max_concurrency_num 1`（backend 真实传参，见附录） | **保持不变**（每账号仍是一个子进程、内部视频并发暂为 1；是否放开需 P 阶段全绿后另行调参） |
| **浏览器/登录态** | 单一 Edge + 9222 + 单一 `cdp_dy_user_data_dir` | **每账号独立** user-data-dir + 独立 CDP 端口 |
| **采集库** | 多进程共用 `MediaCrawler\database\sqlite_tables.db` | **每账号独立采集库** |
| **业务库写入** | 各账号各自 `save_video_snapshot` | **集中串行写队列**，worker 只算不写库 |
| **限速** | 无跨账号全局限速 | **全局 RateLimiter** 跨账号共享（1 req/s 起步） |

### 1.2 验收总纲（最终验收，Codex 施工完必须逐条打勾）

- ✅ 2 账号并行（backend 现传参 `--max_concurrency_num 1`，即每账号内部视频并发 1），跑 3 轮：**无 `database is locked`**；
- ✅ 登录态不串味：账号 A 的请求绝不带账号 B 的 Cookie（独立 user-data-dir 生效）；
- ✅ 全局限速生效：日志无瞬时并发尖峰，`RateLimiter` 日志可证；
- ✅ 单账号失败不影响其他账号，最终失败清单准确（`result_json.accounts_failed`）；
- ✅ 任务级互斥仍生效：并发进行中发起第二个任务 → `CollectionBusyError`；
- ✅ **全程零新增 pip 依赖**（`pip list` 前后对比无新增）；
- ✅ 3 组单测全绿（见 [[#10. 自研组件单测（防"自研 = 不稳"）]]）。

### 1.3 为什么任务级锁不能动

- 📌 **<span style="color:#e67e22">`start()` 里的 `get_active_task()` + `CollectionBusyError` 是"单任务互斥"，防止两个任务同时写同一个 `collection_tasks` 任务表和同一批账号数据。</span>**
- 多账号并发是"**一个任务内部**的并发"，不是"两个任务同时跑"——任务级锁**必须保留**，否则两个任务都调度同一批账号会重复采集、重复落库、进度互相覆盖。

---

## 2. 改造铁律：Codex 必须遵守的 5 条红线

> 🔥 **<span style="color:#e74c3c">以下是施工前必须通读的硬约束。违反任何一条 = 验收不通过。</span>**

| # | 铁律 | 说明 |
|:-:|------|------|
| ① | **零新增 pip 依赖** | 只 import 标准库 + 项目内已有模块（`..db` / `..config` / `..providers.mediacrawler`）。**禁止** `pip install aiolimiter / tenacity / redis / anyio`。若发现必须引第三方库才能实现，停下来问，不要擅自装 |
| ② | **接口隔离** | 所有自研组件封装成独立模块，外部只依赖"稳定的接口名"（`allocate_profile` / `global_limiter.acquire()` / `with_retry` / `submit_write` / `drain` / `run_accounts`）。未来换库只改模块内部，调用点一行不动 |
| ③ | **稳定优先** | 账号并发默认 **2 起步**、全局限速默认 **1/s 起步**。所有可调参数走 `config.py`，硬编码禁止。绝不"一次性 12 路并联" |
| ④ | **合规红线** | 不得自动破解/绕过验证码。MediaCrawler 已强制"自动求解禁用、人工处理"。多账号并发只做"降低触发概率 + 人工完成真验证" |
| ⑤ | **安全红线** | 浏览器登录态目录（唯一落点 `<DEPLOY_ROOT>\data\browser_data`，迁移前 `%LOCALAPPDATA%\MediaCrawler\browser_data`，内含 `cdp_*_user_data_dir`）含 Cookie，**禁止提交 Git / 上传网盘 / 粘贴进工单**；`.env.local` 只读密钥名、不读值、不外发 |

> 💡 **<span style="color:#2980b9">为什么敢说零依赖可行：并发池用项目已在用的 `ThreadPoolExecutor`、限速用自研 25 行同步漏桶、重试用自研 20 行退避、写库用现有 SQLite WAL + 自研串行队列——全部是标准库能力，见 [[多账号并发池相关技术栈]] 第 4 章。</span>**

---

## 3. 施工总览：6 步走完，每步交付什么

| 步骤 | 做什么 | 涉及文件 | 交付物 | 前置依赖 |
|:--:|------|---------|--------|---------|
| **第 1 步** | 加 4 个并发配置项 | `config.py` | 4 个常量 | 无 |
| **第 2 步** | 新建 `multi_account` 包 | 新建 7 个文件 | 6 个模块（含代码） | 第 1 步 |
| **第 3 步** | 加账号级任务表 + 3 函数 | `db.py` | `account_tasks` 表 | 无 |
| **第 4 步** | 主战场改造 | `collection.py` | `_run` 换调度器、`_collect_account` 拆两半 | 第 2、3 步 |
| **第 5 步** | 采集子进程参数化 | `mediacrawler.py` | 独立端口/独立采集库 | 第 2 步 |
| **第 6 步** | 浏览器按需动态拉起 | `start.ps1` | 方案 A 落地 | 第 5 步 |

> 📌 **<span style="color:#e67e22">施工顺序不可乱：第 4 步依赖第 2、3 步的模块存在，第 5 步依赖第 2 步的 `BrowserProfile`。建议严格按 1→2→3→4→5→6 执行，每步做完跑一次语法检查（`python -m py_compile`）再进下一步。</span>**

---

## 4. 第 1 步：config.py 新增 4 个配置项

### 4.1 做什么

在 `backend\app\config.py` 末尾追加 4 个多账号并发配置常量，全部支持 `.env.local` 环境变量覆盖，默认值保守。

### 4.2 怎么做（完整代码，追加到 config.py 末尾）

```python
# ========== 多账号并发采集配置（零依赖，全部走 .env.local 可覆盖） ==========

# 补齐：后端读取浏览器数据根目录（默认对齐 start.ps1 的真实默认 %LOCALAPPDATA%\MediaCrawler\browser_data；
# 三目录迁移后改为 <DEPLOY_ROOT>\data\browser_data，登录态唯一落点见"更新迭代"文档）
MEDIACRAWLER_BROWSER_DATA_DIR = Path(
    os.getenv(
        "MEDIACRAWLER_BROWSER_DATA_DIR",
        Path(os.getenv("LOCALAPPDATA", str(ROOT / "data"))) / "MediaCrawler" / "browser_data",
    )
).resolve()

# 账号级并发度：默认 2 起步，硬上限 4（稳定优先，全绿再放宽）
MEDIACRAWLER_CONCURRENT_ACCOUNTS = max(
    1, min(4, int(os.getenv("MEDIACRAWLER_CONCURRENT_ACCOUNTS", "2"))))

# 跨账号全局限速：默认 1 请求/秒 起步
MEDIACRAWLER_GLOBAL_RATE_PER_SECOND = max(
    0.1, float(os.getenv("MEDIACRAWLER_GLOBAL_RATE_PER_SECOND", "1")))

# CDP 端口起始值：第 1 个账号 9222，第 2 个 9223，第 3 个 9224 ...
MEDIACRAWLER_BROWSER_BASE_PORT = int(os.getenv("MEDIACRAWLER_BROWSER_BASE_PORT", "9222"))
```

### 4.3 验收点

- ✅ `python -c "from app.config import MEDIACRAWLER_CONCURRENT_ACCOUNTS; print(MEDIACRAWLER_CONCURRENT_ACCOUNTS)"` 输出 `2`；
- ✅ `config.py` 顶部已 import `os` 与 `Path`（若缺，补 `import os` 与 `from pathlib import Path`）；
- ✅ 不破坏现有配置引用：其余 `MEDIACRAWLER_*` 常量不变。

> 💡 **<span style="color:#2980b9">为什么默认这么保守：`CONCURRENT_ACCOUNTS=2`、`RATE=1/s` 是"稳定优先"起步值，验证全绿后才由用户在 `.env.local` 调大（[[多worker并发池设计思路]] 红线 14）。</span>**

---

## 5. 第 2 步：新建 multi_account 包（6 个模块 + 完整代码）

### 5.1 做什么

在 `backend\app\services\` 下新建包目录 `multi_account\`，内含 7 个文件。这是整个并发池的核心施工区。

```
backend\app\services\multi_account\
├── __init__.py            # 空文件（包标识）
├── browser_profiles.py    # ① 每账号独立 user-data-dir + CDP 端口 + 独立采集库
├── global_limiter.py      # ② 跨账号全局限速（自研同步漏桶，替代 aiolimiter）
├── retry.py               # ③ 指数退避重试（自研，替代 tenacity）
├── account_pool.py        # ④ 账号级受控并发池（ThreadPoolExecutor 2~3）
├── wal_queue.py           # ⑤ SQLite 集中串行写队列
└── runner.py              # ⑥ 多账号调度器（替代 _run 里的 for 循环）
```

> ⚠️ **<span style="color:#e74c3c">所有模块只 import：标准库 + `..config` / `..db`。严禁 import 任何未安装的第三方库。</span>**

### 5.2 `__init__.py`（新建）

```python
"""多账号并发池包：零依赖（仅标准库 + 项目内已有模块）。
对外暴露的稳定接口见各子模块 docstring。"""
```

### 5.3 `browser_profiles.py`（新建）—— 登录态隔离的地基

**做什么：** 为每个账号分配独立的浏览器数据目录、CDP 端口、独立采集库路径，并登记/回收。**这是"账号 A 的请求绝不带账号 B 的 Cookie"的唯一保证。**

```python
"""每账号独立浏览器 profile + CDP 端口 + 独立采集库（登录态隔离的地基）。
仅标准库。账号并发必须做到"每账号独立浏览器配置"，否则 Cookie 串味、风控一锅端。"""
import re
import threading
from dataclasses import dataclass
from pathlib import Path

from ..config import (
    MEDIACRAWLER_BROWSER_DATA_DIR,
    MEDIACRAWLER_BROWSER_BASE_PORT,
    MEDIACRAWLER_DB,
)

@dataclass(frozen=True)
class BrowserProfile:
    account_name: str
    user_data_dir: Path     # data/browser_data\cdp_<key>_user_data_dir（登录态唯一落点）
    cdp_port: int           # 9222 / 9223 / 9224 ...
    mc_db_path: Path        # <MEDIACRAWLER_DB 所在目录>\<key>_sqlite_tables.db（跟随迁移后的 MEDIACRAWLER_DB）

_profiles_root = Path(MEDIACRAWLER_BROWSER_DATA_DIR)
_port_lock = threading.Lock()
_used_ports: set[int] = set()

def allocate_profile(account_name: str) -> BrowserProfile:
    """为账号分配独立 profile。线程安全：端口自增分配、采完回收复用。"""
    key = re.sub(r"[^\w一-鿿]", "_", account_name)   # 中文账号名安全转文件名
    with _port_lock:
        port = int(MEDIACRAWLER_BROWSER_BASE_PORT)
        while port in _used_ports:
            port += 1
        _used_ports.add(port)
    return BrowserProfile(
        account_name=account_name,
        user_data_dir=_profiles_root / f"cdp_{key}_user_data_dir",
        cdp_port=port,
        mc_db_path=Path(MEDIACRAWLER_DB).parent / f"{key}_sqlite_tables.db",
    )

def release_profile(profile: BrowserProfile) -> None:
    """账号采完回收端口，供下一个账号复用。"""
    with _port_lock:
        _used_ports.discard(profile.cdp_port)
```

**验收点：** `python -c "from app.services.multi_account.browser_profiles import allocate_profile, release_profile; p=allocate_profile('华哥组01'); print(p.cdp_port, p.user_data_dir); release_profile(p)"` 输出端口 `9222`、目录含 `cdp_华哥组01_user_data_dir`。

> 🔥 **<span style="color:#e74c3c">没有这条隔离，多账号并发 = 数据张冠李戴 + 风控一锅端（[[多并发池的批量化采集规则]] 5.1）。这是整份蓝图里最不能省的一步。</span>**

### 5.4 `global_limiter.py`（新建）—— 跨账号全局限速

**做什么：** 一个全局共享的同步漏桶，所有账号"发起平台请求前"都调 `acquire()`，保证跨账号总请求速率受控（默认 1 req/s）。**同步版，零 async 改造。**

```python
"""跨账号全局限速：自研同步漏桶（替代 aiolimiter），仅标准库约 25 行。
漏桶是全局的，天然"公平分配"——2 个账号并发时谁先到谁先用。
为什么不用 aiolimiter：项目是同步线程模型，aiolimiter 仅支持 async。"""
import threading
import time
from ..config import MEDIACRAWLER_GLOBAL_RATE_PER_SECOND

class RateLimiter:
    def __init__(self, rate_per_second: float = 1.0):
        self.min_interval = 1.0 / max(0.1, rate_per_second)
        self._lock = threading.Lock()
        self._last = 0.0

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._last + self.min_interval - now
            if wait > 0:
                time.sleep(wait)
                now = time.monotonic()
            self._last = now

# 全局单例：所有账号共享同一个漏桶
global_limiter = RateLimiter(float(MEDIACRAWLER_GLOBAL_RATE_PER_SECOND))
```

**验收点：** 见 [[#10. 自研组件单测（防"自研 = 不稳"）]] 的 `test_rate_limiter_min_interval`。

> 💡 **<span style="color:#2980b9">"全局限速"和"每账号各自限速"的本质区别：全局漏桶是跨账号共享的，2 个账号不会各发 1/s 合计 2/s——全局就是 1/s，真正控住了"叠加到同一 IP 的总请求量"。</span>**

### 5.5 `retry.py`（新建）—— 指数退避重试

**做什么：** 只对**瞬态错误**（超时/429/5xx）退避重试，业务失败直接抛给上层——防止把"账号真的被风控"也当瞬态错误无限重试。

```python
"""自研指数退避重试（替代 tenacity），仅标准库约 20 行。
只重试瞬态错误（Timeout/429/5xx），业务失败直接抛给上层。
用法：data = with_retry(fn, retryable=(TimeoutError, ConnectionError))"""
import random
import time

def with_retry(fn, *, attempts=3, base=1.0, factor=2.0, max_delay=8.0,
               retryable=(TimeoutError, ConnectionError), logger=None):
    """fn() 抛 retryable 内异常时退避重试；其余异常直接抛给上层。"""
    delay = base
    for i in range(1, attempts + 1):
        try:
            return fn()
        except retryable as exc:
            if i == attempts:
                raise
            jitter = random.uniform(0, 0.5) * delay          # 随机抖动，避免机械节奏
            time.sleep(delay + jitter)
            delay = min(delay * factor, max_delay)           # 1s → 2s → 4s
            if logger:
                logger.warning("第 %d/%d 次重试：%s", i, attempts, exc)
```

**验收点：** 见 [[#10. 自研组件单测（防"自研 = 不稳"）]] 的 `test_retry_transient_then_success` 与 `test_retry_business_error_not_retried`。

### 5.6 `account_pool.py`（新建）—— 账号级受控并发池

**做什么：** 用线程池把账号并发度钉死在 2~3 路（先 2 起步），每个账号一个 worker。**与项目现用的 `ThreadPoolExecutor` 同款，零新语法。**

```python
"""账号级受控并发池：ThreadPoolExecutor(2~3) + 全局限速。仅标准库。
与项目现有 collection.py 的 ThreadPoolExecutor 同款，零新语法。"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..config import MEDIACRAWLER_CONCURRENT_ACCOUNTS

class AccountPool:
    def __init__(self, max_accounts: int | None = None):
        self.max_accounts = max_accounts or int(MEDIACRAWLER_CONCURRENT_ACCOUNTS)
        self.executor = ThreadPoolExecutor(
            max_workers=self.max_accounts, thread_name_prefix="account"
        )

    def run(self, jobs: list) -> list:
        """jobs: list of callable，每个代表一个账号任务。
        单账号失败必须在内部捕获并记录，不向这里冒泡（失败隔离）。"""
        futures = [self.executor.submit(job) for job in jobs]
        return [f.result() for f in as_completed(futures)]   # 每个 result 是 {name: status}
```

**验收点：** `MEDIACRAWLER_CONCURRENT_ACCOUNTS=2` 时 `AccountPool().executor._max_workers == 2`。

> ⚠️ **<span style="color:#e74c3c">账号并发 2~3 × 账号内视频并发 1（backend 现传参 `--max_concurrency_num 1`）= 最高 2~3 路请求。要放开账号内视频并发，需在 P 阶段全绿后另行调参；绝不要"12 个账号 12 路并联"（[[自研平台批量化处理路线]] 的结论）。</span>**

### 5.7 `wal_queue.py`（新建）—— SQLite 集中串行写队列

**做什么：** 所有写业务库的操作（`save_video_snapshot` / `save_video_comments` / 任务计数）提交到单线程消费队列，worker 只算不写库——彻底避免多账号并发下的 `database is locked`。

```python
"""SQLite WAL + 集中串行写队列：worker 只算，写库单线程。仅标准库。"""
import queue
import threading
from ..db import connect

_write_queue: queue.Queue = queue.Queue()
_thread = None

def submit_write(fn, *args, **kwargs) -> None:
    """fn 签名统一为 fn(con, *args, **kwargs)，con 由写线程提供。
    若现有 db 函数第一个参数不是 con，则包一层 lambda con: db_fn(con, ...)。"""
    _write_queue.put((fn, args, kwargs))
    _ensure_worker()

def _ensure_worker() -> None:
    global _thread
    if _thread is None or not _thread.is_alive():
        _thread = threading.Thread(target=_write_worker, daemon=True, name="db-write")
        _thread.start()

def _write_worker() -> None:
    while True:
        fn, args, kwargs = _write_queue.get()
        try:
            with connect() as con:
                fn(con, *args, **kwargs)
        except Exception:
            pass                                   # 单条写失败不影响队列
        finally:
            _write_queue.task_done()

def drain() -> None:
    _write_queue.join()                            # 等所有写任务落库再返回
```

> 🔥 **<span style="color:#e74c3c">这是业务库 `data\radar.sqlite3` 在多账号并发下"不锁死"的命门。现有 `save_video_snapshot` 是独立事务，2 个账号同时写就有排队风险——包进串行队列后写锁零竞争。</span>**

> 📌 **<span style="color:#e67e22">给 Codex 的适配注意：`submit_write` 要求 fn 的第一个参数是 `con`（由写线程通过 `with connect() as con` 提供）。请对照 `db.py` 里 `save_video_snapshot` / `save_video_comments` 的实际签名：若第一参不是 con，在调用处包 `lambda con: save_video_snapshot(con, data)`。</span>**

### 5.8 `runner.py`（新建）—— 多账号调度器

**做什么：** 账号任务入队 → 分配 profile → 提交账号池 → 收结果 → 汇总。**`_run` 主流程的进度/暂停/取消/汇总逻辑一行不用改，只把 for 循环换成 `run_accounts(...)`。**

```python
"""多账号调度器：替代 collection.py _run 里的 for 串行循环。仅标准库。"""
import random
import time
from ..db import add_log, increment_task_result
from .browser_profiles import allocate_profile, release_profile
from .account_pool import AccountPool
from .wal_queue import drain

def run_accounts(task_id: str, accounts: list[str], payload: dict,
                 collect_one: callable) -> dict:
    """collect_one(task_id, name, profile, payload) -> None（单账号失败内部捕获）。
    返回 {"succeeded": [...], "failed": [...]}。"""
    pool = AccountPool()
    results = {"succeeded": [], "failed": []}

    def one(name: str, idx: int):
        if idx > 0:                                        # 非首个账号：随机错峰 20~60s
            time.sleep(random.uniform(20, 60))             # 避免多账号同一瞬间启动的机械节奏
        profile = allocate_profile(name)
        try:
            add_log(task_id, f"账号 {name} 分配 profile：端口 {profile.cdp_port}，目录 {profile.user_data_dir}")
            collect_one(task_id, name, profile, payload)
            results["succeeded"].append(name)
            increment_task_result(task_id, accounts_succeeded=1)
        except Exception as exc:
            results["failed"].append(name)
            increment_task_result(task_id, accounts_failed=1)
            add_log(task_id, f"{name} 采集失败，已继续其他账号：{exc}", "error")
        finally:
            release_profile(profile)

    pool.run([lambda n=name, i=i: one(n, i) for i, name in enumerate(accounts)])
    drain()                                  # 等所有串行写落库
    return results
```

**验收点：** 2 账号任务运行时，`add_log` 出现两条"分配 profile"日志，端口分别为 9222 与 9223；`result_json` 里 `accounts_succeeded + accounts_failed == 提交账号数`。

> 📌 **<span style="color:#e67e22">`collect_one` 就是改造后的 `_collect_account_isolated`（见 [[#7. 第 4 步：collection.py 改造 4 处]]）。随机错峰 20~60s 是风控缓解的关键（[[如何解决人机验证问题]] 第 7 章）。</span>**

---

## 6. 第 3 步：db.py 新增 account_tasks 表 + 3 个 db 函数

### 6.1 做什么

在业务库 `data\radar.sqlite3` 新增一张账号级任务表 `account_tasks`（记录任务内每个账号的 pending/doing/done/failed + 分配端口 + 采集库路径 + 进度），并新增 3 个操作函数，支撑账号级状态展示与断点续跑。

### 6.2 怎么做：建表 SQL（放到 `db.py` 的 SCHEMA 常量区）

```sql
CREATE TABLE IF NOT EXISTS account_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT NOT NULL REFERENCES collection_tasks(id),
  account_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',        -- pending/doing/done/failed
  profile_dir TEXT NOT NULL DEFAULT '',          -- 分配的 user-data-dir
  cdp_port INTEGER,                              -- 分配的 CDP 端口
  mc_db_path TEXT NOT NULL DEFAULT '',           -- 账号独立采集库
  progress INTEGER NOT NULL DEFAULT 0,
  stage TEXT NOT NULL DEFAULT '等待调度',
  error TEXT NOT NULL DEFAULT '',
  attempts INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(task_id, account_name)
);
CREATE INDEX IF NOT EXISTS idx_account_tasks_task_status
  ON account_tasks(task_id, status);
```

### 6.3 怎么做：3 个 db 函数（追加到 db.py）

```python
def save_account_task(task_id, account_name, profile):
    """任务开始时登记：pending + profile/port/db 路径。"""
    now = datetime.utcnow().isoformat()
    with connect() as con:
        con.execute(
            "INSERT INTO account_tasks "
            "(task_id, account_name, status, profile_dir, cdp_port, mc_db_path, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?) "
            "ON CONFLICT(task_id, account_name) DO UPDATE SET updated_at=excluded.updated_at",
            (task_id, account_name, "pending",
             str(profile.user_data_dir), profile.cdp_port,
             str(profile.mc_db_path), now, now),
        )

def update_account_task(task_id, account_name, *, status=None, progress=None,
                        stage=None, error=None):
    """账号级进度/状态更新。只更新传入的非 None 字段。"""
    sets, vals = [], []
    if status is not None:
        sets.append("status=?"); vals.append(status)
    if progress is not None:
        sets.append("progress=?"); vals.append(progress)
    if stage is not None:
        sets.append("stage=?"); vals.append(stage)
    if error is not None:
        sets.append("error=?"); vals.append(error)
    if not sets:
        return
    sets.append("updated_at=?")
    vals.append(datetime.utcnow().isoformat())
    vals += [task_id, account_name]
    with connect() as con:
        con.execute(
            f"UPDATE account_tasks SET {', '.join(sets)} "
            "WHERE task_id=? AND account_name=?",
            vals,
        )

def list_account_tasks(task_id):
    """返回任务内各账号状态列表（给前端账号级进度展示）。"""
    with connect() as con:
        rows = con.execute(
            "SELECT account_name, status, progress, stage, error, cdp_port "
            "FROM account_tasks WHERE task_id=? ORDER BY id",
            (task_id,),
        ).fetchall()
    return [dict(row) for row in rows]
```

### 6.4 幂等迁移（随 `initialize()` 一起跑）

```python
# db.py initialize() 内追加
with connect(path) as connection:
    connection.execute("PRAGMA journal_mode=WAL")          # 已有
    connection.executescript(SCHEMA)                       # 已有
    # —— 新增 ——
    connection.execute(ACCOUNT_TASKS_SCHEMA)               # 幂等 CREATE TABLE IF NOT EXISTS
```

### 6.5 验收点

- ✅ 确认 `db.py` 已 `import datetime`（若缺，补 `from datetime import datetime`）；
- ✅ 老库启动自动加表，`list_account_tasks('任意不存在的id')` 返回空列表不报错；
- ✅ 现有 `collection_tasks` / `collection_job_items` 结构不变，前端已读接口全部兼容。

> ✅ **<span style="color:#2980b9">迁移是幂等的：老库启动自动加表，无需手工 SQL；新库一次性建全。这与 GitHub 项目 xhs_matrix_system 的账号级任务表设计同款（见 [[多账号并发池相关技术栈]] 第 3 章 ③）。</span>**

---

## 7. 第 4 步：collection.py 改造 4 处

> 🔥 **<span style="color:#e74c3c">这是主战场。改前先备份 `collection.py` 一份（如 `collection.py.bak`）。每处改动都对照原代码行号确认。</span>**

### 7.1 改动点 ①：`_run()` 账号 for 循环 → `run_accounts()`

**原代码（`collection.py` 的 `_run` 真实片段，全文仅 62 行）：**
```python
for index, name in enumerate(accounts):
    progress = 5 + int(index / max(len(accounts), 1) * 85)
    update_task(task_id, status="running", progress=progress, stage="正在采集", current_account=name)
    imported = 0
    for video, metrics in provider.collect_account(account_by_name(name), payload["range"]):
        save_video_snapshot(video, metrics)
        imported += 1
    add_log(task_id, f"{name} 导入 {imported} 条作品数据")
```

**改成：**
```python
from .services.multi_account.runner import run_accounts
...
# 用多账号调度器替换 for 串行循环；外部进度/暂停/取消/汇总逻辑保留
ma_result = run_accounts(task_id, accounts, payload, self._collect_account_isolated)
succeeded_accounts.extend(ma_result["succeeded"])
failed_accounts.extend(ma_result["failed"])
```

**给 Codex 的说明：** 进度、暂停、取消、汇总逻辑都在 `_run` 主流程里（不在 for 内部），所以**只替换循环体**，别动外部逻辑。`_wait_control` 的暂停/取消检查仍由主流程每账号后调用。

### 7.2 改动点 ②：`_collect_account` 拆成 `_collect_account_isolated`（加 profile 参数）

**做什么：** 原单账号逻辑改为接收 runner 已分配的 `profile`，内部所有采集调用传 profile。

**改成（在类内新增方法，原 `_collect_account` 可保留为薄封装或删除）：**
```python
def _collect_account_isolated(self, task_id, name, profile, payload):
    """单账号采集（多账号并发版）：profile 由 runner 分配，含独立端口/采集库。"""
    # —— 账号级进度登记（第 3 步新增的 db 函数） ——
    save_account_task(task_id, name, profile)
    update_account_task(task_id, name, status="doing", stage="开始采集")
    try:
        # 原 _collect_account 内部逻辑，关键改 3 处：
        # ① 达人资料 / 采集调用传入 profile
        provider.collect_account(name, range_key, profile=profile)
        # ② 平台请求前调全局限速（第 2 步模块）
        global_limiter.acquire()
        # ③ 写库走串行队列（第 2 步模块），不再直接 save_video_snapshot
        submit_write(_wrap_save_snapshot, video_data)
    finally:
        update_account_task(task_id, name, status="done", stage="完成")
```

**给 Codex 的说明：**
- `profile` 的分配/回收由 runner 负责，`_collect_account_isolated` 内**不要再**调 `allocate_profile`；
- `_wrap_save_snapshot` 是适配函数（因 `save_video_snapshot` 签名可能不以 con 开头）：
  ```python
  def _wrap_save_snapshot(con, data):
      from ..db import save_video_snapshot
      save_video_snapshot(con, data)
  ```
- 若原 `_collect_account` 内部有 `_wait_control`（暂停检查），保留在账号 worker 内，实现账号级暂停。

### 7.3 改动点 ③：若后续接入 ASR 转录，需单独封顶 worker（当前无此代码）

**审计结论：** 当前 `collection.py` 全文 62 行，**不含任何转录/GPU 逻辑**，只有账号级采集循环 + `save_video_snapshot` 落库。若后续接入 ASR 转录（见 [[关于字幕提取相关的插件]]），转录是 CPU/GPU 密集型，**必须**单独封顶 worker（如 `min(4, N)`），防止账号并发把转录请求翻倍超载。此处无"原代码"可改，仅作施工提醒，不是本次改动点。

### 7.4 改动点 ④：写库统一走 wal_queue

**做什么：** 凡是账号 worker 线程内写业务库的操作（`save_video_snapshot` / `save_video_comments` / 计数），全部改成 `submit_write(...)` 提交，不在账号线程内直接 `with connect()`。

**验收点（第 4 步整体）：**
- ✅ 2 账号并行任务运行，`sqlite3` 无 `database is locked` 报错日志；
- ✅ 任务正常结束，`result_json` 里 `accounts_succeeded/accounts_failed` 正确；
- ✅ 原有"单任务互斥"仍生效：任务进行中再 start → `CollectionBusyError`。

> 📌 **<span style="color:#e67e22">第 4 步是"接线"：新增模块负责并发池 + 隔离 + 限速 + 重试 + 串行写，collection.py 只负责把它们接进现有流程。目标是不动 `_run` 的外部骨架。</span>**

---

## 8. 第 5 步：mediacrawler.py 改造 4 处

> 🔥 **<span style="color:#e74c3c">三座大山里"浏览器 CDP 隔离 + 数据库并发写"两座山的直接解法，全在这 4 处。</span>**

### 8.1 改动点 ①：`collect_account()` 加 `profile` 参数

**原代码（`mediacrawler.py` `collect_account` 真实片段，全文仅 109 行）：**
```python
started_ms = int(time.time() * 1000) - 1000
command = [
    str(MEDIACRAWLER_PYTHON), str(MEDIACRAWLER_ROOT / "main.py"),
    "--platform", "dy", "--lt", MEDIACRAWLER_LOGIN_TYPE,
    "--type", "creator", "--creator_id", creator_url,
    "--get_comment", "no", "--get_sub_comment", "no",
    "--headless", "no", "--save_data_option", "sqlite",
    "--max_concurrency_num", "1",
]
```

**改成：**
```python
def collect_account(self, account, range_key, profile=None):
    ...
    started_ms = int(time.time() * 1000) - 1000
    command = [
        str(MEDIACRAWLER_PYTHON), str(MEDIACRAWLER_ROOT / "main.py"),
        "--platform", "dy", "--lt", MEDIACRAWLER_LOGIN_TYPE,
        "--type", "creator", "--creator_id", creator_url,
        "--get_comment", "no", "--get_sub_comment", "no",
        "--headless", "no", "--save_data_option", "sqlite",
        "--max_concurrency_num", "1",
    ]
    env = os.environ.copy()
    if profile is not None:
        # 独立 user-data-dir（若 MediaCrawler 支持 --user_data_dir 则加参数；
        # 不支持则用环境变量注入，让子进程 _read_changed 读到独立库）
        command += ["--user_data_dir", str(profile.user_data_dir)]
        env["MEDIACRAWLER_ACCOUNT_DB"] = str(profile.mc_db_path)
    ...
    subprocess.run(command, cwd=MEDIACRAWLER_ROOT, env=env, ...)
```

**给 Codex 的说明：** 需确认 MediaCrawler `main.py` 是否支持 `--user_data_dir` 参数（查其 CLI 定义）。若不支持，**最低可用方案**是：只通过环境变量注入独立采集库路径（见改动点 ②），user-data-dir 隔离靠第 6 步的独立 Edge 实例实现。

### 8.2 改动点 ②：`_read_changed()` 读账号独立采集库

**原代码（真实 `_read_changed` 片段）：** `with sqlite3.connect(MEDIACRAWLER_DB) as connection:` 读共享库。

**改成：**
```python
def _read_changed(self, ...):
    db_path = self.account_db or MEDIACRAWLER_DB     # self.account_db 来自 profile.mc_db_path
    con = sqlite3.connect(db_path)
    ...
```

**为什么：** 一箭双雕——解决"多进程写同一 SQLite 锁死" + "`started_ms` 时间戳串味"（多进程共用采集库时，各自按启动时刻过滤新增数据，会互相读到对方的数据）。独立库后互不干扰。

### 8.3 改动点 ③：浏览器生命周期由 MediaCrawler main.py 子进程管理（backend 无 _monitor_browser）

**审计结论：** 当前 `mediacrawler.py` 全文 109 行，**不存在 `_monitor_browser()` 方法**——浏览器/CDP/人机验证监控完全由 MediaCrawler `main.py` 子进程内部负责（playwright 拉起 Edge、扫码、轮询 CDP）。backend 只做 `subprocess.run` 拉起 main.py 并等它结束。

**对多账号并发的含义：** 每账号一个 MediaCrawler 子进程 = 一个独立 playwright 浏览器实例；端口/登录态隔离由 MediaCrawler 的 `--user_data_dir`（若支持）或独立 profile 环境变量保证。**不要在 backend 里臆造 `_monitor_browser`。** 若需判断子进程是否卡在人机验证，改为监控 main.py 的 stdout/stderr 关键字（如"登录成功/验证码"）。

### 8.4 改动点 ④：端口占用预检

**在启动子进程前加：**
```python
if profile is not None and _port_in_use(profile.cdp_port):
    raise RuntimeError(f"CDP 端口 {profile.cdp_port} 已被占用，检查是否有重复 Edge 实例")
```

**为什么：** 防止两账号抢同一浏览器；同时避免重复启动同一 user-data-dir 导致 Edge profile 单实例锁死。

**验收点（第 5 步整体）：**
- ✅ 2 账号并行，各自 Edge 实例端口不同（CDP `http://127.0.0.1:9222/json` 与 9223 各自返回不同标签页）；
- ✅ 账号 A 的 `_read_changed` 只读到 A 库数据，不混入 B 的数据；
- ✅ 端口被占时抛 `RuntimeError`，不静默复用。

---

## 9. 第 6 步：start.ps1 支持浏览器按需动态拉起

### 9.1 做什么

**审计澄清（重要）：** `start.ps1` 全文仅 44 行，**只启动两个进程**——uvicorn（backend，127.0.0.1:8000）+ npm（frontend，127.0.0.1:3000）；它**从不拉起 Edge**。真实链路：用户点采集 → backend `MediaCrawlerProvider.collect_account` → `subprocess.run` 拉起 `MediaCrawler\main.py` → main.py 内部用 playwright 拉起 Edge 并扫码登录（单一 user-data-dir，默认 `%LOCALAPPDATA%\MediaCrawler\browser_data`）。

因此多账号并发时，第 2、3 个账号的浏览器**天然由各自 MediaCrawler 子进程拉起**，无需 start.ps1 参与；只需保证各子进程用独立 user-data-dir 与端口（第 2 步 `allocate_profile` 已保证）。

**start.ps1 真实全文（44 行，审计基准）：**
```powershell
param([switch]$Install)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$mediaCrawlerRoot = Join-Path $projectRoot "MediaCrawler"
$mediaCrawlerPython = Join-Path $mediaCrawlerRoot ".venv\Scripts\python.exe"
$frontend = Join-Path $projectRoot "frontend"
$logs = Join-Path $projectRoot "logs"
$envFile = Join-Path $projectRoot ".env.local"
New-Item -ItemType Directory -Force $logs | Out-Null

if (Test-Path -LiteralPath $envFile) {
  foreach ($line in Get-Content -LiteralPath $envFile -Encoding UTF8) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) { continue }
    $parts = $trimmed.Split("=", 2)
    [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
  }
}

if ($Install) {
  if (-not (Test-Path -LiteralPath $backendPython)) { python -m venv (Join-Path $projectRoot ".venv") }
  & $backendPython -m pip install -r (Join-Path $projectRoot "backend\requirements.txt")
  if (-not (Test-Path -LiteralPath $mediaCrawlerPython)) { python -m venv (Join-Path $mediaCrawlerRoot ".venv") }
  & $mediaCrawlerPython -m pip install -r (Join-Path $mediaCrawlerRoot "requirements.txt")
  Push-Location $frontend
  try { npm.cmd ci } finally { Pop-Location }
}

if (-not (Test-Path -LiteralPath $backendPython)) { throw "Run .\start.ps1 -Install first" }
if (-not (Test-Path -LiteralPath $mediaCrawlerPython)) { throw "MediaCrawler virtual environment is missing; run .\start.ps1 -Install first" }

if (-not $env:COLLECTION_PROVIDER) { $env:COLLECTION_PROVIDER = "mediacrawler" }
if (-not $env:MEDIACRAWLER_ROOT) { $env:MEDIACRAWLER_ROOT = $mediaCrawlerRoot }
if (-not $env:MEDIACRAWLER_PYTHON) { $env:MEDIACRAWLER_PYTHON = $mediaCrawlerPython }
if (-not $env:MEDIACRAWLER_LOGIN_TYPE) { $env:MEDIACRAWLER_LOGIN_TYPE = "qrcode" }
if (-not $env:MEDIACRAWLER_TIMEOUT_SECONDS) { $env:MEDIACRAWLER_TIMEOUT_SECONDS = "1800" }
if (-not $env:MEDIACRAWLER_BROWSER_DATA_DIR) { $env:MEDIACRAWLER_BROWSER_DATA_DIR = Join-Path $env:LOCALAPPDATA "MediaCrawler\browser_data" }

Start-Process -FilePath $backendPython -ArgumentList "-m","uvicorn","backend.app.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory $projectRoot -RedirectStandardOutput (Join-Path $logs "backend.out.log") -RedirectStandardError (Join-Path $logs "backend.err.log") -WindowStyle Hidden
Start-Process -FilePath "npm.cmd" -ArgumentList "run","dev","--","--host","127.0.0.1","--port","3000" -WorkingDirectory $frontend -RedirectStandardOutput (Join-Path $logs "frontend.out.log") -RedirectStandardError (Join-Path $logs "frontend.err.log") -WindowStyle Hidden

Write-Host "Started: frontend http://127.0.0.1:3000  backend http://127.0.0.1:8000/api/health"
Write-Host "A real collection opens an Edge login window; scan the QR code on first use."
```

### 9.2 方案 A（推荐）落地

- **start.ps1 不参与浏览器拉起**（它只启 uvicorn + npm，现有 44 行逻辑不动）；
- **第 2、3 账号的浏览器**由 runner 的 `allocate_profile` 之后、`collect_one` 之前动态拉起。

**在 `mediacrawler.py` 的 `collect_account`（或 runner 的 one() 内）加一个 PowerShell 调用：**

```powershell
# 动态拉起第 N 个账号的 Edge（在 PowerShell 中执行）
Start-Process msedge `
  --remote-debugging-port=<profile.cdp_port> `
  --user-data-dir="<profile.user_data_dir>" `
  "https://www.douyin.com/"
```

**Python 侧调用（用标准库 `subprocess`）：**
```python
import subprocess

def _ensure_browser(profile) -> None:
    """按需拉起独立 Edge 实例。若端口已被占用则跳过（说明已在运行）。"""
    if _port_in_use(profile.cdp_port):
        return
    cmd = ["msedge", f"--remote-debugging-port={profile.cdp_port}",
           f"--user-data-dir={str(profile.user_data_dir)}",
           "https://www.douyin.com/"]
    subprocess.Popen(cmd, shell=True)
```

### 9.3 硬性注意

> 📌 **<span style="color:#e67e22">必须保证"一个 user-data-dir 只被一个 Edge 实例使用"——两个 Edge 共用一个 user-data-dir 会互相锁死（Chrome/Edge 的 profile 单实例锁）。这也是为什么每个账号必须独立 user-data-dir（第 2 步 `allocate_profile` 已保证）。</span>**

**验收点（第 6 步）：**
- ✅ 2 账号任务运行时，任务栏出现 **2 个独立 Edge 图标**（9222 与 9223 各一个）；
- ✅ 两个 Edge 窗口各自可独立扫码登录（首次）或各自已有独立登录态；
- ✅ 账号采完，对应 Edge 实例被回收（或保持复用，但绝不串用）。

---

## 10. 自研组件单测（防"自研 = 不稳"）

> 🔥 **<span style="color:#e74c3c">自研组件最大的疑虑是"自己写的不够稳"。用 3 组 pytest 完全钉死正确性，交付 Codex 时一并写入 `backend\tests\test_multi_account.py`。</span>**

```python
"""多账号并发池自研组件单测：限速器 + 重试器。仅标准库 + pytest。"""
import time
import pytest

from app.services.multi_account.global_limiter import RateLimiter
from app.services.multi_account.retry import with_retry


# —— ① 限速器：10 次 acquire 的总耗时 ≥ 9s（1 req/s 下限）——
def test_rate_limiter_min_interval():
    limiter = RateLimiter(rate_per_second=1.0)
    t0 = time.monotonic()
    for _ in range(10):
        limiter.acquire()
    assert time.monotonic() - t0 >= 9.0


# —— ② 重试器：瞬态错误重试 3 次后成功，不提前失败 ——
def test_retry_transient_then_success():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("transient")
        return "ok"

    assert with_retry(flaky, attempts=3) == "ok"
    assert calls["n"] == 3


# —— ③ 重试器：业务失败（非瞬态）直接抛，不白等退避 ——
def test_retry_business_error_not_retried():
    with pytest.raises(ValueError):
        with_retry(lambda: (_ for _ in ()).throw(ValueError("bad")), attempts=3)
```

**验收点：** `pytest backend\tests\test_multi_account.py -v` → 3 passed。

---

## 11. 分阶段验收（P0→P4）与安全自检

> 🔥 **<span style="color:#e74c3c">铁律：每一阶段跑稳、验收过了，才进下一阶段。永远不要"一次性写满并发"（[[多worker并发池设计思路]] 5 节）。</span>**

| 阶段 | 做什么 | 验收标准 |
|:--:|------|---------|
| **P0** | 保持现状，零改动 | 连续 3 轮零崩溃、无锁冲突（当前已达标，勿破坏） |
| **P1** | 按本蓝图第 1~6 步施工完（2 账号并发框架） | **2 账号并行**（各内部视频并发 1）跑 3 轮：无人机验证卡死、无 `database is locked`、登录态不串味 |
| **P2** | 接入全局限速 + 指数退避（模块已含，接进请求路径） | 偶发 429/超时自动退避成功；`account_tasks` 状态可恢复（断点续跑） |
| **P3** | 失败隔离汇总 + 前端账号级展示 | 单账号失败不影响其他账号；全局限速生效（日志可证）；前端可见每账号 pending/doing/done/failed |
| **P4（可选）** | 账号并发放开到 3~4 | 需 P1~P3 全绿才做；仍维持全局限速，日志无瞬时并发尖峰 |

### 11.1 每次放量前的安全自检（三组实验，来自 [[自研平台批量化处理路线]] 3 节）

1. **2 账号串行**（间隔 20~60s 随机）→ 成功？确认是"并发触发风控"还是"串行本身问题"；
2. **2 账号并发**（限速 1/s）→ 观察 429/403/验证码出现率；
3. **逐级放量**：2 → 3 → 4，每级稳定跑 2~3 轮再放宽，出现异常立即回退一级。

---

## 12. 给 Codex 的交付清单与安全注意事项

### 12.1 施工 check-list（Codex 逐项打勾）

| # | 检查项 | 完成 |
|:-:|--------|:--:|
| 1 | `config.py` 4 个配置项已加，默认值 2 / 1 / 9222 | ☐ |
| 2 | `multi_account` 包 7 个文件已建，只 import 标准库 | ☐ |
| 3 | `db.py` `account_tasks` 表 + 3 函数 + 幂等迁移 | ☐ |
| 4 | `collection.py` 4 处改完，`_run` 外部骨架未动 | ☐ |
| 5 | `mediacrawler.py` 4 处改完，端口/采集库已参数化 | ☐ |
| 6 | `start.ps1` 方案 A 落地，动态拉起独立 Edge | ☐ |
| 7 | 3 组单测全绿 | ☐ |
| 8 | `python -m py_compile` 全部改动文件零报错 | ☐ |
| 9 | `pip list` 前后对比：**零新增依赖** | ☐ |
| 10 | P1 验收：2 账号并行 × 3 并发跑 3 轮全绿 | ☐ |
| 11 | 未提交任何含 Cookie 的目录、未外发 `.env.local` 值 | ☐ |

### 12.2 安全注意事项（Codex 必须遵守）

- ⚠️ **<span style="color:#e74c3c">登录态/Cookie 目录（唯一落点 `<DEPLOY_ROOT>\data\browser_data\cdp_*_user_data_dir`，迁移前 `%LOCALAPPDATA%\MediaCrawler\browser_data\`）：禁止提交 Git、禁止上传网盘、禁止粘贴进工单/日志片段。</span>**
- ⚠️ **<span style="color:#e67e22">`.env.local` 只读密钥名、不读值、不外发；新增配置项只往 `.env.local` 写键名与默认值。</span>**
- ⚠️ 不得实现任何"自动破解验证码"逻辑；多账号并发只做"降低触发概率 + 人工完成真验证"。
- ⚠️ 若 MediaCrawler `main.py` 不支持 `--user_data_dir`，**不要改 MediaCrawler 本体**（保持其独立仓库干净），改用环境变量注入独立采集库 + 独立 Edge 实例实现隔离（见 [[#8. 第 5 步：mediacrawler.py 改造 4 处]] 8.1）。

### 12.3 施工完成后的回归清单

- ✅ 原"单账号串行"模式仍可用（`MEDIACRAWLER_CONCURRENT_ACCOUNTS=1` 即退化为串行）；
- ✅ 任务级互斥仍生效（第二个任务被 `CollectionBusyError` 拒绝）；
- ✅ 前端现有任务卡片接口（`get_recent_collection_logs` 等）不破坏；
- ✅ 采集库 `<MEDIACRAWLER_DB 所在目录>`（迁移后为 `<DEPLOY_ROOT>\data\`）下新增的账号独立库按预期生成。

---

## 附：真实文件全文（审计基准，Codex 施工前必须对照）

> 以下全文摘自 2026-08-14 实测的 `F:\全自动爬取短视频、推文爆款程序`，作为本蓝图所有"原代码/改动点"的**唯一事实基准**。若你手上文件与以下不一致，以你手上的为准并回填。

### collection.py 全文（backend\app\services\collection.py，62 行）

```python
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from uuid import uuid4

from ..accounts import account_by_name
from ..config import COLLECTION_PROVIDER, DOUYIN_CLIENT_KEY, DOUYIN_CLIENT_SECRET
from ..db import add_log, create_task, get_active_task, get_task, save_video_snapshot, update_task
from ..providers.demo import DemoProvider
from ..providers.douyin import DouyinOfficialProvider
from ..providers.mediacrawler import MediaCrawlerProvider


class CollectionBusyError(RuntimeError):
    pass


def _provider(task_id: str):
    if COLLECTION_PROVIDER == "mediacrawler":
        return MediaCrawlerProvider(logger=lambda message: add_log(task_id, message))
    if COLLECTION_PROVIDER == "douyin_official":
        return DouyinOfficialProvider(DOUYIN_CLIENT_KEY, DOUYIN_CLIENT_SECRET)
    return DemoProvider()


class CollectionService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="collector")
        self.start_lock = Lock()

    def start(self, payload: dict) -> dict:
        for name in payload["accounts"]:
            account_by_name(name)
        with self.start_lock:
            active = get_active_task()
            if active:
                raise CollectionBusyError(f"已有采集任务正在运行：{active['id']}")
            task_id = uuid4().hex
            create_task(task_id, payload)
            self.executor.submit(self._run, task_id, payload)
        return get_task(task_id)

    def _run(self, task_id: str, payload: dict) -> None:
        try:
            provider = _provider(task_id)
            accounts = payload["accounts"]
            add_log(task_id, f"任务启动，共 {len(accounts)} 个账号")
            for index, name in enumerate(accounts):
                progress = 5 + int(index / max(len(accounts), 1) * 85)
                update_task(task_id, status="running", progress=progress, stage="正在采集", current_account=name)
                imported = 0
                for video, metrics in provider.collect_account(account_by_name(name), payload["range"]):
                    save_video_snapshot(video, metrics)
                    imported += 1
                add_log(task_id, f"{name} 导入 {imported} 条作品数据")
            update_task(task_id, status="completed", progress=100, stage="采集完成")
            add_log(task_id, "任务完成")
        except Exception as exc:
            add_log(task_id, str(exc), "error")
            update_task(task_id, status="failed", progress=0, stage="采集失败", error=str(exc))


service = CollectionService()
```

### 关于 provider 接口（backend\app\providers\base.py）

```python
from typing import Protocol


class Provider(Protocol):
    def collect_account(self, account: dict, range_key: str) -> list[tuple[dict, dict]]: ...
```

> 📎 相关落地参考：[[多账号并发池相关技术栈]]（选型依据）· [[多账号不同视频同时采集的技术栈要求]]（插件版对照）· [[多并发池的批量化采集规则]]（方案论证）· [[多worker并发池设计思路]]（14 红线）· [[自研平台批量化处理路线]]（放量实验）· [[Codex对话迁移方案]]（交接约定）· [[0814-还没配置好的内容]]（P0/P2 待办）· [[关于爬虫项目的后续优化迭代与升级]]（三目录分离/增量更新总方案）
