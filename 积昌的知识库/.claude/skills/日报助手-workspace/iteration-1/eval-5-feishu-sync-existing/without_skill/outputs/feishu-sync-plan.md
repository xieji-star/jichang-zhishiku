# 2026-08-03 日报 → 飞书同步方案（预览版）

> ⚠️ **本文件仅为同步方案，未执行任何飞书写入操作。** 全部命令仅供参考，待用户确认后再实际执行。

---

## 一、同步概览

| 序号 | 同步目标 | 内容 | 操作方式 |
|:---:|---------|------|---------|
| ① | 飞书「日报信息」文档 | 当日日报（标题 + 精华速览列表） | `block_insert_after` 插入文档最前 |
| ② | 「华哥线索统计」多维表格·「每天更新」表 | 当日汇总一行记录 | `+record-batch-create` |
| ③ | 「华哥线索统计」多维表格·「账号数据」表 | 每条发布内容一条记录 | 数据缺失，暂不录入（见说明） |
| ④ | 视图排序 | 两表最新日期在上 | 已设置过，无需重复 |

**身份**：全部命令使用 `--as user`（用户"落日"/谢积昌个人账号，文档增删改查类操作）。

---

## 二、日报数据映射表

### 2.1 精华速览（→ ①「日报信息」文档）

```
- 数字人视频6条（MiniMax+Heygen全链路）
- 长推文31条
- 评论回复20~30次
- 灯塔线索录入5条
- 账号流量3000~5000，互动一般
- 剪辑6条 / 发布视频2条 / 发布长文2条
- 科研脚本31个 / 参考爆款脚本更新2个
- 运营账号：科研华哥、不水论文的华哥
- 复盘：脚本产出量大但流量一般，想优化选题方向
```

### 2.2 「每天更新」表字段映射（→ ②）

| 字段 | 填入值 | 备注 |
|------|:---:|------|
| 时间 | `1785686400000` | 2026-08-03 00:00:00（毫秒时间戳） |
| 剪辑数量 | `6条` | |
| 发布抖音视频 | `2` | |
| 发布抖音长文 | `2` | 非 0，正常填写 |
| 线索数量 | `5` | |
| 科研脚本数量 | `31个` | select 选项可能不足，需先 `+field-update` 添加"31个" |
| 运营 | `谢积昌` | |
| 参考爆款脚本更新 | `2个` | |

### 2.3 「账号数据」表（→ ③）

今日发布视频 2 条、长文 2 条，需**每条发布内容一条记录**（链接/账号/内容形式/播放量/点赞/评论量/涨粉/视频发布日期/运营 共 9 字段）。**本次日报内容中未提供逐条发布数据的明细（抖音链接、播放量、点赞等），为避免编造数据，本表暂不录入**；待用户补充后再执行 ③。

---

## 三、① 「日报信息」文档 — 同步精华速览

- **文档 URL**：`https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh`
- **写入格式**：一级标题 `<h1>8月3日——谢积昌</h1>` + 无序列表 `<ul><li>...</li></ul>`
- **位置**：文档最前（"日期近的在最上"约定）

### 执行步骤（计划）

**步骤 1：定位锚点**（取当前最上方一条日报标题，如 `7月31日——朱柏达` 的 block id）

```bash
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "7月31日——朱柏达" --detail with-ids --as user
```

**步骤 2：在锚点前插入新日报**（`block_insert_after` 插到锚点之后 = 新内容位于锚点之前）

```bash
lark-cli docs +update --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --command block_insert_after \
  --block-id <锚点id> \
  --content '<h1>8月3日——谢积昌</h1><ul><li>数字人视频6条（MiniMax+Heygen全链路）</li><li>长推文31条</li><li>评论回复20~30次</li><li>灯塔线索录入5条</li><li>账号流量3000~5000，互动一般</li><li>剪辑6条 / 发布视频2条 / 发布长文2条</li><li>科研脚本31个 / 参考爆款脚本更新2个</li><li>运营账号：科研华哥、不水论文的华哥</li><li>复盘：脚本产出量大但流量一般，想优化选题方向</li></ul>' \
  --as user
```

**步骤 3：验证**

```bash
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "8月3日" --context-after 15 --as user
```

> ⚠️ **禁止用 `str_replace` 插入块级结构**：XML 模式仅支持行内文本，`<ul>/<li>` 会被剥离。块级结构一律用 `block_insert_after`。

---

## 四、② 「每天更新」表 — 当日汇总记录

- **Base Token**：`R4HfbCLz1acTChsf6Y1cqrCPnnh`
- **Table**：`tbl7edeeXcx04W7O`（每天更新）

### 执行步骤（计划）

**步骤 1：核对字段与选项**（重点：`科研脚本数量` 是否有 "31个" 选项）

```bash
lark-cli base +field-list --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O --as user
```

**步骤 2（条件执行）：选项不足时先添加**

```bash
lark-cli base +field-update --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --field-id <科研脚本数量字段id> \
  --json '{"name":"科研脚本数量","type":"select","multiple":true,"options":[{"name":"2个"},{"name":"4个"},{"name":"6个"},{"name":"31个","hue":"Green","lightness":"Light"}]}' \
  --yes --as user
```

**步骤 3：创建当日记录**

```bash
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --json '{"create_records":[{"时间":1785686400000,"剪辑数量":"6条","发布抖音视频":"2","发布抖音长文":"2","线索数量":"5","科研脚本数量":"31个","运营":"谢积昌","参考爆款脚本更新":"2个"}]}' \
  --as user
```

**步骤 4：验证**

```bash
lark-cli base +record-get --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O --record-id <新记录id> --as user
```

> ⚠️ select 字段只接受已有选项；发布长文为 0 时才留空，本次为 2 条需正常填写。

---

## 五、③ 「账号数据」表 — 逐条内容数据（待数据补充）

- **Table**：`tbl2exdwZlTQfLjl`（账号数据）
- **字段（9个）**：链接 / 账号 / 内容形式 / 播放量 / 点赞 / 评论量 / 涨粉 / 视频发布日期 / 运营

**待办**：请提供今日发布内容（2 视频 + 2 长文）逐条的：账号、抖音分享链接、内容形式（案例类/选题/长文/真人实拍/咨询结尾）、播放量、点赞、评论量、涨粉。

提供后将按以下模板录入（每条内容 = 一条记录，链接含 `#` `&` 等字符时写临时 JSON 文件用 `@file` 传参，用后即删）：

```bash
# _create_records.json 示例（UTF-8）：
# {"create_records":[{"链接":"https://v.douyin.com/xxx/","账号":"科研华哥   ","内容形式":"案例类","播放量":"","点赞":"","评论量":"","涨粉":"","视频发布日期":1785686400000,"运营":"谢积昌"}, ...]}
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl2exdwZlTQfLjl \
  --json @_create_records.json --as user
rm -f _create_records.json
```

> ⚠️ 账号选项 `科研华哥` 自带 3 个尾部空格（`"科研华哥   "`），须原样匹配，避免误建重复选项。

---

## 六、④ 视图排序（无需本次重复执行）

- 「每天更新」按「时间」降序：`vew2FYX1w9`
- 「账号数据」按「视频发布日期」降序：`vew7d8iKhF`

```bash
lark-cli base +view-set-sort --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id <table> --view-id <view> \
  --json '{"sort_config":[{"field":"时间","desc":true}]}' --as user
```

已设置过则新记录自动排最上，无需重复操作。

---

## 七、执行前检查清单

- [ ] 确认飞书服务/lark-cli 可用，身份为 `--as user`
- [ ] 步骤 ② 前用 `+field-list` 核对「科研脚本数量」是否有 "31个" 选项
- [ ] 步骤 ① 前 fetch 确认最新锚点标题（如 `7月31日——朱柏达`）及其 block id
- [ ] 发布长文 2 条非 0，需正常填写「发布抖音长文」字段
- [ ] 「账号数据」表数据待用户补充后另行录入，禁止编造
- [ ] 写入前可用 `--dry-run` 预览请求体
- [ ] 全部写入后向用户汇报三处结果（文档位置、记录条数、各表数据）

---

## 八、执行后预期结果

1. 飞书「日报信息」文档顶部新增 `8月3日——谢积昌` 标题及精华速览列表；
2. 「每天更新」表新增 1 条 2026-08-03 汇总记录；
3. 「账号数据」表待补充数据后新增 4 条记录（2 视频 + 2 长文）；
4. 两表最新日期自动排在最上。
