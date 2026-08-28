# ui-ux-pro-max

> **来源仓库：** `nextlevelbuilder/ui-ux-pro-max-skill`（GitHub，v2.11.0）
> **类型：** UI/UX 设计智能技能套件（1 个主技能 + 6 个配套技能）

本文件夹是 **ui-ux-pro-max** 这一个 skill 的完整套件，主技能与配套技能、数据、测试脚本均收拢于此，不对外平铺。

## 目录结构

```
ui-ux-pro-max/
├── SKILL.md                      # 主技能：设计智能核心（84 种风格 / 192 配色 / 74 字体 / 98 UX 指南 / 25 图表 / 22 技术栈）
├── data/                         # 设计数据库（CSV）
├── references/                   # 参考文档（pro-rules、quick-reference）
├── scripts/                      # 搜索与设计系统脚本（search.py、design_system.py 等）
├── banner-design/                # 配套：多平台横幅设计（22 种风格）
├── brand/                        # 配套：品牌形象
├── design/                       # 配套：综合设计（logo、CIP、海报等）
├── design-system/                # 配套：设计系统与设计令牌
├── slides/                       # 配套：HTML 演示文稿
└── ui-styling/                   # 配套：shadcn/ui 界面样式
```

## 使用方式

- **主技能** `ui-ux-pro-max` 已激活，可被自动识别，直接调用即可。
- **配套技能**（banner-design、brand、design、design-system、slides、ui-styling）收拢在本文件夹内，由 Claude 按需直接读取对应子目录的 `SKILL.md` 使用。
- 主技能搜索命令：

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain>
```

> 详细用法见 `CLAUDE.md`（英文）、`README.zh.md`（中文）。
