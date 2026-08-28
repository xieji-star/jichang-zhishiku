# 飞书同步工作流（已验证，2026-08-03 案例固化）

> ⚠️ **身份铁律（最高优先级）**：本工作流**必须全程使用用户本人账号（`--as user`，即"落日"/谢积昌）**；**严禁使用 bot 身份（`--as bot`，即"飞书智能助手"/"谢积昌的飞书CLI"应用）**。所有命令示例已带 `--as user`，复制执行时不得删除或改写为 `--as bot`；适用于本文档内全部命令（含文档、多维表格、视图等所有读写操作）。理由：操作记录须归属本人账号，权限以本人授权为准。

> ⚠️ **数据操作边界（硬性）**：在飞书多维表格（「每天更新」「账号数据」等）的记录操作中，**只能对自己（运营=谢积昌）的数据及文字内容进行新增、修改、删除**；**严禁增删改其他运营（如朱柏达）的记录及其文字内容**（record-create/update/delete、字段值修改、批量导入、视图内改动等一切写操作一律禁止）；如需对比分析他人数据，仅允许读取（record-list/search/get），不得写入或改动。理由：表格为多人共用，他人数据与文字归其本人所有，未经授权不得改动。

日报确认后，将数据同步到飞书三处（使用 `--as user` 身份）。本文件为详细命令手册；流程概览见 SKILL.md「第五步」。

## ① 飞书「日报信息」文档 — 同步单行汇总

- **文档 URL**：`https://brothers.feishu.cn/docx/Kz6Wdi6NAo70K5x8RjictFbqnRh`
- **写入格式**：一级标题 `8月7日——谢积昌`（`<h1>`）+ 单个段落（**非列表**），内容为一行汇总：
  `谢积昌：发布xx条视频，xx图文，今日灯塔录入主动咨询线索xx条，截止目前总共xxx条； 截止目前总GMVxxx元`
- **位置要求**：插入到文档**最前**（callout 提示之后、上一条日报之前），文档约定"日期近的在最上"
- ⚠️ **不再同步精华速览**：日报文档只写这一行汇总，不再写 `<ul>` 精华速览列表

### 标准步骤

1. 定位锚点：取当前最上方一条日报的一级标题文本（如 `8月7日——朱柏达`），用 keyword 获取其 block id：
   ```bash
   lark-cli docs +fetch --doc "<URL>" --scope keyword --keyword "8月7日——朱柏达" --detail with-ids --as user
   # 返回 <h1 id="XXX">...</h1>，记下锚点 id
   ```
2. 用 `block_insert_after` 插入新日报（命令语义：新块紧跟锚点块**之后**；锚点取「当前最上方日报标题」时，新日报紧挨其下方、位于所有旧日报上方；若位置不符预期，改用 `block_insert_before` 或选文档更靠顶部的块作锚点）：
   ```bash
   lark-cli docs +update --doc "<URL>" --command block_insert_after \
     --block-id <锚点id> \
     --content '<h1>8月7日——谢积昌</h1><p>谢积昌：发布2条视频，0图文，今日灯塔录入主动咨询线索2条，截止目前总共30条； 截止目前总GMV0元</p>' \
     --as user
   ```
3. **验证（必做）**：`docs +fetch --scope keyword --keyword "8月7日" --context-after 15`，检查新日报是否位于文档最前（callout 提示之后、旧日报上方）。若不在最上方，改用 `block_insert_before`（锚点=旧最上方日报标题）重新插入。

### 注意事项

- ⚠️ **禁止用 `str_replace` 插入块级结构**：XML 模式的 str_replace 只支持行内文本，块级结构会被剥离。插入块级结构一律用 `block_insert_after` / `block_replace`。
- ⚠️ 插入内容必须含完整 `<h1>` 新标题 + `<p>` 单行汇总，先 fetch 确认锚点 id 再写。
- ⚠️ **插入方向**：`block_insert_after` 将新块插在锚点块之后（下方）。锚点取「当前最上方日报标题」即让新日报位于旧日报上方；插入后必须 fetch 验证位置，若不在最上方改用 `block_insert_before`。
- 块级标签语法：`<h1>` 标题、`<p>文本</p>` 段落；文本中的 `&` `<` 需转义为 `&amp;` `&lt;`。

## ② 「华哥线索统计」多维表格「每天更新」表 — 当日汇总

- **Base Token**：`R4HfbCLz1acTChsf6Y1cqrCPnnh`
- **Table**：`tbl7edeeXcx04W7O`（每天更新）
- **字段（8个）**：时间 / 剪辑数量 / 发布抖音视频 / 发布抖音长文 / 线索数量 / 科研脚本数量 / 运营 / 参考爆款脚本更新

### 步骤

1. 计算当天时间戳（毫秒）：
   ```bash
   date -d "2026-08-03 00:00:00" +%s   # 秒，×1000 转毫秒
   ```
2. 先 `+field-list` 核对字段与选项；select 选项不足时先添加：
   ```bash
   lark-cli base +field-update --base-token <token> --table-id <table> --field-id <fid> \
     --json '{"name":"科研脚本数量","type":"select","multiple":true,"options":[{"name":"2个"},{"name":"4个"},{"name":"6个"},{"name":"31个","hue":"Green","lightness":"Light"}]}' \
     --yes --as user
   ```
3. 创建记录（`create_records` 数组，每元素为字段 Map）：
   ```bash
   lark-cli base +record-batch-create --base-token <token> --table-id <table> \
     --json '{"create_records":[{"时间":1785686400000,"剪辑数量":"2条","发布抖音视频":"2","线索数量":"5","科研脚本数量":"31个","运营":"谢积昌","参考爆款脚本更新":"2个"}]}' \
     --as user
   ```
4. 用 `+record-get --record-id <新id>` 验证。

### 注意事项

- ⚠️ **select 字段只接受已有选项**：写入不存在的选项会报错，必须先 `+field-update` 添加。
- ⚠️ **发布长文为 0 时留空不填**（该字段无 0 选项）。
- ⚠️ **「科研华哥」账号选项名自带 3 个尾部空格**（`"科研华哥   "`），须原样匹配，避免误建重复选项。

## ③ 「华哥线索统计」多维表格「账号数据」表 — 逐条内容数据

- **Table**：`tbl2exdwZlTQfLjl`（账号数据）
- **字段（9个）**：链接 / 账号 / 内容形式 / 播放量 / 点赞 / 评论量 / 涨粉 / 视频发布日期 / 运营
- **规则**：每条发布内容 = 一条记录（数据来自采集问题7E）

### 步骤

1. 逐条组装记录；链接含 `#`、`&` 等特殊字符时，先写临时 JSON 文件再用 `@file` 传参：
   ```bash
   # 写 _create_records.json（UTF-8），内容：
   # {"create_records":[{"链接":"...抖音分享链接...","账号":"科研华哥   ","内容形式":"案例类","播放量":"763","点赞":"6","评论量":"0","涨粉":"1","视频发布日期":1785686400000,"运营":"谢积昌"}, ...]}
   lark-cli base +record-batch-create --base-token <token> --table-id <table> --json @_create_records.json --as user
   rm -f _create_records.json   # 用后即删
   ```
2. `+record-get` 验证（确认账号选项未产生重复、日期正确）。

### 注意事项

- 「账号」选项：`科研华哥   `（带空格）/ 搞科研的华哥 / 华哥聊论文 / 发论文的华哥
- 「内容形式」选项：案例类 / 选题 / 长文 / 真人实拍 / 咨询结尾（用户说"案例"统一填"案例类"）

## ④ 视图排序 — 两表最新日期在上

- 「每天更新」表按「时间」降序；「账号数据」表按「视频发布日期」降序
- 视图 ID 以 `+view-list` 实际返回为准（「每天更新」=`vew2FYX1w9`，「账号数据」=`vew7d8iKhF`）

```bash
lark-cli base +view-set-sort --base-token <token> --table-id <table> --view-id <view> \
  --json '{"sort_config":[{"field":"时间","desc":true}]}' --as user
```

设置后新记录自动排在最上，无需每次手动调整。

---

## 常用身份与检查

- ⚠️ **身份铁律**：全部命令**必须**使用 `--as user`（落日/谢积昌个人账号），**禁止**使用 `--as bot`（飞书智能助手/谢积昌的飞书CLI 应用）。执行前检查命令尾部是否带 `--as user`，缺失则补上，错误则改正。
- 写入前可用 `--dry-run` 预览请求体，确认字段与格式无误
