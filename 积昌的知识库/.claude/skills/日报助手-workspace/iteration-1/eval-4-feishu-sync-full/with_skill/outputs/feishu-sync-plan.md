# 2026-08-04 日报飞书同步方案（命令清单，不真实写入）

> ⚠️ **本文件为同步方案与命令清单**：所有写入命令均以 `--dry-run` 形式预览请求体，**未执行任何真实飞书写入**（未调用 lark-cli 真实写入、未访问飞书 API）。正式执行时去掉 `--dry-run` 参数即可直接运行。
>
> 身份：全部命令使用 `--as user`（谢积昌个人账号），遵循 SKILL.md「第五步：飞书同步工作流」与 `references/feishu-sync.md` 手册。

## 同步数据总览（源自 2026-08-04 日报）

- **精华速览**：脚本4条+数字人视频4条（MiniMax+Heygen全链路）/ 钩子文档4个 / 评论回复约50次 / 灯塔线索录入4条 / 流量1万+、互动一般（评论30/点赞200/分享10）/ 剪辑2条、发布抖音视频2条、长文1条 / 参考爆款脚本更新2个 / 突破：首次独立完成脚本创作
- **当天时间戳**：`2026-08-04 00:00:00`（UTC+8）→ 毫秒 `1785772800000`
- **运营**：谢积昌

---

## ① 飞书「日报信息」文档 — 同步精华速览

- 文档 URL：`https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh`
- 约定：插入到文档最前，日期近的在最上；格式为一级标题 `8月4日——谢积昌`（`<h1>`）+ 无序列表（`<ul><li>`，每条一行）

### 步骤 1：定位锚点（取当前最上方一条日报的一级标题 block id）

```bash
# 以最近一条日报「8月3日——谢积昌」为锚点，用 keyword 获取其 block id
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "8月3日——谢积昌" --detail with-ids --as user --dry-run
# 预期返回 <h1 id="<锚点id>">...</h1>，记录锚点 id 供下一步使用
```

### 步骤 2：在锚点之前插入新日报（block_insert_after 插在锚点后 = 新内容位于锚点前）

```bash
lark-cli docs +update --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --command block_insert_after \
  --block-id <锚点id> \
  --content '<h1>8月4日——谢积昌</h1><ul><li>脚本4条 + 数字人视频4条（MiniMax+Heygen全链路）</li><li>钩子文档4个</li><li>评论回复约50次</li><li>灯塔线索录入4条</li><li>账号总流量1万+，互动一般（评论30/点赞200/分享10）</li><li>剪辑2条，发布抖音视频2条、长文1条</li><li>参考爆款脚本更新2个</li><li>突破：首次独立完成脚本创作</li></ul>' \
  --as user --dry-run
```

### 步骤 3：验证

```bash
lark-cli docs +fetch --doc "https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh" \
  --scope keyword --keyword "8月4日" --context-after 15 --as user --dry-run
```

> ⚠️ 注意事项
> - **禁止用 `str_replace` 插入块级结构**：XML 模式仅支持行内文本，`<ul>/<li>` 会被剥离、内容合并进标题；块级插入一律用 `block_insert_after` / `block_replace`。
> - 插入内容必须含完整 `<h1>` 新标题 + `<ul>` 列表；文本中的 `&`、`<` 需转义为 `&amp;`、`&lt;`（本方案内容无特殊字符）。

---

## ② 「华哥线索统计」多维表格「每天更新」表 — 当日汇总

- Base Token：`R4HfbCLz1acTChsf6Y1cqrCPnnh`
- Table：`tbl7edeeXcx04W7O`（每天更新）
- 字段（8个）：时间 / 剪辑数量 / 发布抖音视频 / 发布抖音长文 / 线索数量 / 科研脚本数量 / 运营 / 参考爆款脚本更新

### 步骤 1：核对字段与选项

```bash
lark-cli base +field-list --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O --as user --dry-run
```

### 步骤 2（select 选项不足时）：先添加选项，再写入

```bash
# 例：若「科研脚本数量」无"4个"选项，先 field-update 添加
lark-cli base +field-update --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --field-id <科研脚本数量字段id> \
  --json '{"name":"科研脚本数量","type":"select","multiple":true,"options":[{"name":"2个"},{"name":"4个"},{"name":"6个"}]}' \
  --yes --as user --dry-run
```

### 步骤 3：创建当日汇总记录（--dry-run 预览请求体）

```bash
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --json '{"create_records":[{"时间":1785772800000,"剪辑数量":"2条","发布抖音视频":"2","发布抖音长文":"1","线索数量":"4","科研脚本数量":"4个","运营":"谢积昌","参考爆款脚本更新":"2个"}]}' \
  --as user --dry-run
```

### 步骤 4：验证（正式执行后）

```bash
lark-cli base +record-get --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O --record-id <新记录id> --as user
```

> ⚠️ 注意事项
> - select 字段只接受已有选项，写入不存在的选项会报错，必须先 `+field-update` 添加。
> - 发布长文为 0 时留空不填（本日长文 1 条，正常填写 `"1"`）。
> - 「科研华哥」账号选项名自带 3 个尾部空格（`"科研华哥   "`），须原样匹配，避免误建重复选项（本表「运营」字段填"谢积昌"）。

---

## ③ 「华哥线索统计」多维表格「账号数据」表 — 逐条内容数据

- Base Token：`R4HfbCLz1acTChsf6Y1cqrCPnnh`
- Table：`tbl2exdwZlTQfLjl`（账号数据）
- 字段（9个）：链接 / 账号 / 内容形式 / 播放量 / 点赞 / 评论量 / 涨粉 / 视频发布日期 / 运营
- 规则：**每条发布内容 = 一条记录**（今日共 2 条）

### 步骤 1：写临时 JSON 文件（长链接含特殊字符时用 `@file` 传参，用后即删）

`_create_records.json`（UTF-8 编码）：

```json
{"create_records":[
  {"链接":"https://v.douyin.com/abc/","账号":"科研华哥   ","内容形式":"案例类","播放量":"763","点赞":"6","评论量":"0","涨粉":"1","视频发布日期":1785772800000,"运营":"谢积昌"},
  {"链接":"https://v.douyin.com/def/","账号":"不水论文的华哥","内容形式":"长文","播放量":"1200","点赞":"15","评论量":"3","涨粉":"2","视频发布日期":1785772800000,"运营":"谢积昌"}
]}
```

### 步骤 2：批量创建记录（--dry-run 预览请求体）

```bash
lark-cli base +record-batch-create --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl2exdwZlTQfLjl \
  --json @_create_records.json --as user --dry-run
rm -f _create_records.json   # 用后即删
```

### 步骤 3：验证（正式执行后）

```bash
lark-cli base +record-get --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl2exdwZlTQfLjl --record-id <新记录id> --as user
```

> ⚠️ 注意事项
> - 「账号」选项：`科研华哥   `（带 3 个尾部空格）/ 搞科研的华哥 / 华哥聊论文 / 发论文的华哥；**「不水论文的华哥」若不在现有选项中，须先 `+field-update` 添加该选项（select 选项不足时先添加），再写入记录，避免误建重复选项**。
> - 「内容形式」选项：案例类 / 选题 / 长文 / 真人实拍 / 咨询结尾；用户说"案例"统一填"案例类"。
> - 链接含 `#`、`&` 等特殊字符时用临时 JSON 文件 + `@file` 传参。

---

## ④ 视图排序 — 两表最新日期在上

```bash
# 「每天更新」按「时间」降序（视图 vew2FYX1w9）
lark-cli base +view-set-sort --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl7edeeXcx04W7O \
  --view-id vew2FYX1w9 --json '{"sort_config":[{"field":"时间","desc":true}]}' --as user --dry-run

# 「账号数据」按「视频发布日期」降序（视图 vew7d8iKhF）
lark-cli base +view-set-sort --base-token R4HfbCLz1acTChsf6Y1cqrCPnnh --table-id tbl2exdwZlTQfLjl \
  --view-id vew7d8iKhF --json '{"sort_config":[{"field":"视频发布日期","desc":true}]}' --as user --dry-run
```

> 视图 ID 以 `+view-list` 实际返回为准（手册固化值：「每天更新」= `vew2FYX1w9`，「账号数据」= `vew7d8iKhF`）。设置后新记录自动排在最上。

---

## 正式执行后的汇报模板

- ① 日报信息文档：已在最上方插入「8月4日——谢积昌」精华速览
- ② 每天更新表：新增 1 条记录（时间 2026-08-04 / 剪辑2条 / 发视频2 / 长文1 / 线索4 / 脚本4个 / 爆款脚本2个）
- ③ 账号数据表：新增 2 条记录（科研华哥-案例类-播放763 / 不水论文的华哥-长文-播放1200）
- ④ 视图排序：两表已按最新日期降序
- 注明"以后每日自动同步"
