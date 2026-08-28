# 2026-08-04 日报飞书同步方案（命令清单，未执行）

> ⚠️ 本文档仅为同步方案与命令清单（含 `--dry-run` 预览），**未执行任何飞书写入操作**。确认无误后，移除 `--dry-run` 并逐条执行即可。

- **身份**：全部命令使用 `--as user`（落日/谢积昌个人账号）
- **同步时间**：2026-08-04
- **运营**：谢积昌

---

## ① 飞书「日报信息」文档 — 同步精华速览

- **文档**：`https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh`

### 1. 定位锚点（取当前最上方一条日报的一级标题，如 `8月3日——谢积昌`）

```bash
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "8月3日" --detail with-ids --as user
# 返回 <h1 id="XXX">...</h1>，记下锚点 block id
```

### 2. 在锚点之前插入今日日报（`block_insert_after` 插在锚点后 = 新内容位于锚点前）

```bash
lark-cli docs +update --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --command block_insert_after \
  --block-id <锚点id> \
  --content '<h1>8月4日——谢积昌</h1><ul><li>脚本4条（首次独立创作）+ 数字人视频4条（MiniMax+Heygen全链路）</li><li>钩子文档4个</li><li>评论回复约50次</li><li>灯塔线索录入4条</li><li>账号总流量1万+，互动一般</li><li>剪辑2条，发布抖音视频2条 + 长文1条</li><li>参考爆款脚本更新2个</li><li>突破：首次独立完成脚本创作</li></ul>' \
  --dry-run --as user
```

> ⚠️ 禁止 `str_replace` 插入块级结构（XML 模式会剥离 `<ul>/<li>`）；文本中 `&` `<` 需转义。

### 3. 验证

```bash
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "8月4日" --context-after 15 --as user
```

---

## ② 「华哥线索统计」多维表格「每天更新」表 — 当日汇总

- **Base Token**：`R4HfbCLz1acTChsf6Y1cqrCPnnh`
- **Table**：`tbl7edeeXcx04W7O`（每天更新）
- **字段（8个）**：时间 / 剪辑数量 / 发布抖音视频 / 发布抖音长文 / 线索数量 / 科研脚本数量 / 运营 / 参考爆款脚本更新

### 1. 核对字段与选项（必须先做）

```bash
lark-cli base +field-list --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O --as user
```

**本日数据 → 字段对照**：

| 字段 | 值 | 说明 |
|------|----|------|
| 时间 | `1785772800000` | 2026-08-04 00:00:00（毫秒时间戳） |
| 剪辑数量 | `2条` | |
| 发布抖音视频 | `2` | |
| 发布抖音长文 | `1条` | 若选项无"1条"，需先添加选项 |
| 线索数量 | `4` | |
| 科研脚本数量 | `4个` | 若选项无"4个"，需先添加选项 |
| 运营 | `谢积昌` | |
| 参考爆款脚本更新 | `2个` | |

### 2. select 选项不足时先添加（按需执行，例如科研脚本数量缺"4个"选项）

```bash
lark-cli base +field-update --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --field-id <科研脚本数量字段id> \
  --json '{"name":"科研脚本数量","type":"select","multiple":true,"options":[{"name":"4个"},{"name":"2个"},{"name":"6个"}]}' \
  --yes --dry-run --as user
```

### 3. 创建记录（dry-run 预览）

```bash
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --json '{"create_records":[{"时间":1785772800000,"剪辑数量":"2条","发布抖音视频":"2","发布抖音长文":"1条","线索数量":"4","科研脚本数量":"4个","运营":"谢积昌","参考爆款脚本更新":"2个"}]}' \
  --dry-run --as user
```

> ⚠️ select 字段只接受已有选项，写入不存在的选项会报错，必须先 `+field-update` 添加。
> ⚠️ 「科研华哥」账号选项名自带 3 个尾部空格（`"科研华哥   "`），须原样匹配。

---

## ③ 「华哥线索统计」多维表格「账号数据」表 — 逐条内容数据

- **Table**：`tbl2exdwZlTQfLjl`（账号数据）
- **字段（9个）**：链接 / 账号 / 内容形式 / 播放量 / 点赞 / 评论量 / 涨粉 / 视频发布日期 / 运营
- **规则**：每条发布内容 = 一条记录（今日共 2 条）

### 本日记录（数据全部来自用户提供，未编造）

| 链接 | 账号 | 内容形式 | 播放量 | 点赞 | 评论量 | 涨粉 | 视频发布日期 |
|------|------|---------|:---:|:---:|:---:|:---:|:---:|
| https://v.douyin.com/abc/ | 科研华哥   | 案例类 | 763 | 6 | 0 | 1 | 1785772800000 |
| https://v.douyin.com/def/ | 不水论文的华哥 | 长文 | 1200 | 15 | 3 | 2 | 1785772800000 |

> 内容形式选项：案例类 / 选题 / 长文 / 真人实拍 / 咨询结尾（用户说"案例"统一填"案例类"）；运营填"谢积昌"。

### 1. 链接含特殊字符时写临时 JSON 文件传参（`@file`，用后即删）

```bash
# 写 _create_records.json（UTF-8）：
# {"create_records":[
#   {"链接":"https://v.douyin.com/abc/","账号":"科研华哥   ","内容形式":"案例类","播放量":"763","点赞":"6","评论量":"0","涨粉":"1","视频发布日期":1785772800000,"运营":"谢积昌"},
#   {"链接":"https://v.douyin.com/def/","账号":"不水论文的华哥","内容形式":"长文","播放量":"1200","点赞":"15","评论量":"3","涨粉":"2","视频发布日期":1785772800000,"运营":"谢积昌"}
# ]}
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl2exdwZlTQfLjl \
  --json @_create_records.json --dry-run --as user
rm -f _create_records.json   # 用后即删
```

### 2. 验证

```bash
lark-cli base +record-get --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl2exdwZlTQfLjl \
  --record-id <新记录id> --as user
```

---

## ④ 视图排序 — 两表最新日期在上（若此前已设置可跳过）

- 「每天更新」按「时间」降序（view `vew2FYX1w9`）；「账号数据」按「视频发布日期」降序（view `vew7d8iKhF`）

```bash
lark-cli base +view-set-sort --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --view-id vew2FYX1w9 --json '{"sort_config":[{"field":"时间","desc":true}]}' --dry-run --as user

lark-cli base +view-set-sort --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl2exdwZlTQfLjl \
  --view-id vew7d8iKhF --json '{"sort_config":[{"field":"视频发布日期","desc":true}]}' --dry-run --as user
```

> 视图 ID 以 `+view-list` 实际返回为准。

---

## 执行清单汇总（确认后按序执行）

1. `docs +fetch` 定位「8月3日」锚点 → 2. `docs +update block_insert_after` 插入今日精华速览 → 3. `base +field-list` 核对「每天更新」选项 → 4. （按需）`base +field-update` 补选项 → 5. `base +record-batch-create` 写入「每天更新」1 条 → 6. `base +record-batch-create` 写入「账号数据」2 条 → 7. `+view-set-sort` 设置/确认排序 → 8. 汇报三处结果并注明"以后每日自动同步"。
