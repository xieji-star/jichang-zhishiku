# 2026-08-03 日报飞书同步方案（仅方案，未真实执行）

> 依据「日报助手」skill 的 SKILL.md「第五步：飞书同步工作流」与 `references/feishu-sync.md` 手册制定。
> 本方案仅给出命令/JSON 清单（含 `--dry-run` 演示），**未执行任何真实的飞书写入操作**。

---

## 一、待同步数据摘要（来源：用户提供的日报内容）

| 项目 | 数据 |
|------|------|
| 日期 | 2026-08-03 |
| 运营账号 | 科研华哥、不水论文的华哥 |
| 剪辑数量 | 6 条 |
| 发布抖音视频 | 2 条 |
| 发布抖音长文 | 2 条 |
| 科研脚本数量 | 31 个 |
| 线索数量 | 5 条 |
| 参考爆款脚本更新 | 2 个 |
| 时间戳（毫秒） | `1785686400000`（= 2026-08-03 00:00:00 北京时间，已验证） |
| 账号数据表逐条数据 | **待用户补充**（问题7E：每条发布的视频/长文的链接/播放量/点赞/评论/涨粉） |

> ⚠️ 按照 skill「禁止编造数据」铁律：**「账号数据」表的逐条数据（4条发布内容）需用户提供后方可填写**，本方案提供模板与占位符。

---

## 二、同步①：飞书「日报信息」文档 — 同步精华速览

- **文档 URL**：`https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh`
- **写入格式**：一级标题 `8月3日——谢积昌`（`<h1>`）+ 无序列表（`<ul><li>`，每条一行）
- **位置要求**：文档最前（callout 之后、上一条日报之前），约定"日期近的在最上"

### 步骤 1：定位锚点（先 fetch 取当前最上方日报的 h1 id）

```bash
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "8月" --detail with-ids --as user
# 从返回中取最上方一条日报的 <h1 id="XXX">，记下锚点 id
# （示例锚点如 7月31日——朱柏达，实际以 fetch 结果为准）
```

### 步骤 2：在锚点之前插入新日报（block_insert_after）

```bash
lark-cli docs +update --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --command block_insert_after \
  --block-id <锚点id> \
  --content '<h1>8月3日——谢积昌</h1><ul><li>数字人视频6条（MiniMax+Heygen全链路）</li><li>长推文31条</li><li>评论回复20~30次</li><li>灯塔线索录入5条</li><li>账号流量3000~5000，互动一般</li><li>复盘：脚本产出量大但流量一般，想优化选题方向</li></ul>' \
  --dry-run \
  --as user
# 确认请求体无误后，去掉 --dry-run 执行
```

### 步骤 3：验证

```bash
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "8月3日" --context-after 15 --as user
# 检查新日报结构与衔接（应位于文档最前、上一条日报之上）
```

### 注意事项

- ⚠️ **禁止 `str_replace` 插入块级结构**：XML 模式的 str_replace 仅支持行内文本，`<ul>/<li>` 会被剥离、内容合并进标题；插入块级结构一律用 `block_insert_after`。
- ⚠️ 插入内容必须含完整 `<h1>` 新标题 + `<ul>` 列表；先 fetch 确认锚点 id 再写。
- 文本中的 `&`、`<` 需转义为 `&amp;`、`&lt;`（本日报内容无特殊字符）。

---

## 三、同步②：「华哥线索统计」多维表格「每天更新」表 — 当日汇总

- **Base Token**：`R4HfbCLz1acTChsf6Y1cqrCPnnh`
- **Table ID**：`tbl7edeeXcx04W7O`（每天更新）
- **字段（8个）**：时间 / 剪辑数量 / 发布抖音视频 / 发布抖音长文 / 线索数量 / 科研脚本数量 / 运营 / 参考爆款脚本更新

### 步骤 1：核对字段与选项

```bash
lark-cli base +field-list --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O --as user
# 重点核对：科研脚本数量选项是否已有"31个"；参考爆款脚本更新是否已有"2个"；运营选项
```

### 步骤 2：select 选项不足时先添加（以「科研脚本数量」添加"31个"为例）

```bash
lark-cli base +field-update --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh \
  --table-id tbl7edeeXcx04W7O --field-id <科研脚本数量字段fid> \
  --json '{"name":"科研脚本数量","type":"select","multiple":true,"options":[{"name":"2个"},{"name":"4个"},{"name":"6个"},{"name":"31个","hue":"Green","lightness":"Light"}]}' \
  --yes --as user
```

> ⚠️ select 字段只接受已有选项，写入不存在的选项会报错，必须先 `+field-update` 添加。

### 步骤 3：创建记录

```bash
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh \
  --table-id tbl7edeeXcx04W7O \
  --json '{"create_records":[{"时间":1785686400000,"剪辑数量":"6条","发布抖音视频":"2","发布抖音长文":"2","线索数量":"5","科研脚本数量":"31个","运营":"谢积昌","参考爆款脚本更新":"2个"}]}' \
  --dry-run --as user
# 确认字段与格式无误后，去掉 --dry-run 执行；记录 id 记下用于验证
```

### 步骤 4：验证

```bash
lark-cli base +record-get --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh \
  --table-id tbl7edeeXcx04W7O --record-id <新记录id> --as user
```

### 注意事项

- 发布长文为 0 时该字段留空不填；**今日发布长文为 2 条，正常填写"2"**。
- 「运营」字段按已验证案例填写"谢积昌"。
- ⚠️ 若「运营」字段为账号类选项，注意「科研华哥」选项名自带 3 个尾部空格（`"科研华哥   "`），须原样匹配，避免误建重复选项（本案例「运营」填"谢积昌"，不受影响）。

---

## 四、同步③：「华哥线索统计」多维表格「账号数据」表 — 逐条内容数据

- **Table ID**：`tbl2exdwZlTQfLjl`（账号数据）
- **字段（9个）**：链接 / 账号 / 内容形式 / 播放量 / 点赞 / 评论量 / 涨粉 / 视频发布日期 / 运营
- **规则**：每条发布内容 = 一条记录（数据来自采集问题7E）

> ⚠️ **今日发布 2 条视频 + 2 条长文 = 共 4 条记录**，但逐条数据（链接/播放量/点赞/评论量/涨粉）用户暂未提供。**真实同步前必须先向用户收集问题7E数据，禁止编造**。以下为 4 条记录的模板（占位符 `<...>` 处替换为用户提供的数据）。

### 步骤 1：组装记录（占位示例，4 条）

```json
{
  "create_records": [
    {
      "链接": "<视频1抖音分享链接>",
      "账号": "科研华哥   ",
      "内容形式": "<案例类/选题/长文/真人实拍/咨询结尾>",
      "播放量": "<数字>",
      "点赞": "<数字>",
      "评论量": "<数字>",
      "涨粉": "<数字>",
      "视频发布日期": 1785686400000,
      "运营": "谢积昌"
    },
    {
      "链接": "<视频2抖音分享链接>",
      "账号": "不水论文的华哥",
      "内容形式": "<内容形式>",
      "播放量": "<数字>",
      "点赞": "<数字>",
      "评论量": "<数字>",
      "涨粉": "<数字>",
      "视频发布日期": 1785686400000,
      "运营": "谢积昌"
    },
    {
      "链接": "<长文1抖音分享链接>",
      "账号": "<账号>",
      "内容形式": "长文",
      "播放量": "<数字>",
      "点赞": "<数字>",
      "评论量": "<数字>",
      "涨粉": "<数字>",
      "视频发布日期": 1785686400000,
      "运营": "谢积昌"
    },
    {
      "链接": "<长文2抖音分享链接>",
      "账号": "<账号>",
      "内容形式": "长文",
      "播放量": "<数字>",
      "点赞": "<数字>",
      "评论量": "<数字>",
      "涨粉": "<数字>",
      "视频发布日期": 1785686400000,
      "运营": "谢积昌"
    }
  ]
}
```

### 步骤 2：链接含特殊字符时用 @file 传参（用后即删）

```bash
# 将上面 JSON 写入 _create_records.json（UTF-8），然后：
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh \
  --table-id tbl2exdwZlTQfLjl --json @_create_records.json --dry-run --as user
# 确认无误后去掉 --dry-run 执行，然后：
rm -f _create_records.json
```

### 步骤 3：验证

```bash
lark-cli base +record-get --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh \
  --table-id tbl2exdwZlTQfLjl --record-id <新记录id> --as user
# 确认账号选项未产生重复、日期正确
```

### 注意事项

- 「账号」选项：`科研华哥   `（带 3 个尾部空格）/ 搞科研的华哥 / 华哥聊论文 / 发论文的华哥（「不水论文的华哥」如不在选项中需先 `+field-update` 添加）。
- 「内容形式」选项：案例类 / 选题 / 长文 / 真人实拍 / 咨询结尾（用户说"案例"统一填"案例类"）。

---

## 五、同步④：视图排序 — 两表最新日期在上

```bash
# 「每天更新」表按「时间」降序（视图 vew2FYX1w9）
lark-cli base +view-set-sort --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh \
  --table-id tbl7edeeXcx04W7O --view-id vew2FYX1w9 \
  --json '{"sort_config":[{"field":"时间","desc":true}]}' --as user

# 「账号数据」表按「视频发布日期」降序（视图 vew7d8iKhF）
lark-cli base +view-set-sort --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh \
  --table-id tbl2exdwZlTQfLjl --view-id vew7d8iKhF \
  --json '{"sort_config":[{"field":"视频发布日期","desc":true}]}' --as user
```

> 视图 ID 以 `+view-list` 实际返回为准；设置后新记录自动排在最上，无需每次手动调整。

---

## 六、身份与安全约束

- 全部命令使用 **`--as user`**（落日/谢积昌个人账号）。
- 写入前可用 **`--dry-run`** 预览请求体，确认字段与格式无误后再实际执行。
- 本方案仅为演示/清单，**未执行任何真实的飞书写入**（未调用 lark-cli 真实写入、未访问飞书 API）。
- 真实执行时按顺序：① 文档精华速览 → ② 每天更新记录 → ③ 账号数据记录（先补齐问题7E数据）→ ④ 视图排序 → 向用户汇报三处结果（文档位置、记录条数、各表数据），并注明"以后每日自动同步"。
