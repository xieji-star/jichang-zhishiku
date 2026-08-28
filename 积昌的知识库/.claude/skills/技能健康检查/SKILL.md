---
name: 技能健康检查
description: |
  检查 `.claude/skills/` 目录下所有 skill 的可调用性，并自动修复问题。确保每个 skill 都拥有有效的 SKILL.md 文件（含 YAML frontmatter：name 和 description），在 settings.json 中注册，并且可以被正常调用。

  触发条件（只要满足任意一条就应触发）：
  - 用户要求检查所有 skill 是否可以正常调用 / 是否正常工作
  - 用户要求"检查 skills 目录"、"修复 skills"、"检修 skill"
  - 用户说"检查 skill 的健康状况"、"做一次 skill 健康检查"
  - 用户安装新 skill 后要求验证
  - 用户发现某个 skill 无法调用并要求排查
  - 用户要求"整理 skills"、"清理 skills"、"维护 skills"
  - 用户说"看看我的 skill 都正常吗"或类似表达

  不要触发此 skill 的场景：
  - 用户要求创建新 skill（请使用 技能创建工具）
  - 用户仅询问某个 skill 的功能说明（直接回答即可，无需检查）
  - 用户要求删除 skill 或清理目录（直接操作即可）
---

# Skill 健康检查工作流

> 本 skill 定义了对 `.claude/skills/` 目录进行全量检查、问题诊断和自动修复的完整流程。
>
> **核心理念**：每个 skill 的核心是 `SKILL.md` 文件，其 YAML frontmatter 必须包含 `name` 和 `description` 两个字段，否则该 skill 无法被系统识别和调用。

## 为什么需要健康检查

Skill 可能因为以下原因变得不可调用：
- SKILL.md 文件丢失（空目录、误删除）
- YAML frontmatter 格式错误（缺少 name/description、语法错误）
- 未在 `.claude/settings.json` 的 `enabledPlugins` 中注册
- 会话缓存未更新（新安装的 skill 需要重启会话）

---

## 操作流程

### Step 1：列出所有 skill 目录

使用 Glob 工具或文件枚举，列出 `.claude/skills/` 下的所有子目录：

```bash
# 推荐方式：使用 Glob
Glob pattern="*" path="F:\积昌的知识库 - 副本\.claude\skills"

# 或使用 Bash
Bash command="python3 -c \"
import os
skills_dir = r'F:\积昌的知识库 - 副本\.claude\skills'
for d in sorted(os.listdir(skills_dir)):
    if os.path.isdir(os.path.join(skills_dir, d)):
        print(d)
\""
```

### Step 2：检查每个 skill 的 SKILL.md

对每个 skill 目录，检查以下内容：

#### 2.1 文件存在性检查
```
SKILL.md 是否存在？  →  不存在 → 标记为"缺失 SKILL.md"
```

#### 2.2 YAML frontmatter 有效性检查

读取 SKILL.md 的前 5-10 行，验证：

```
---
name: <必填>    # skill 的名称标识符
description: <必填>  # skill 的触发描述
---
```

**检查要点：**
- 是否以 `---` 开头和结尾
- `name` 字段是否存在且非空
- `description` 字段是否存在且非空
- 所有字段值是否符合 YAML 语法（引号、缩进、多行字符串等）

**常见问题示例：**
```yaml
# 错误：name 缺失
description: "某个描述"

# 错误：description 为空
name: my-skill
description: ""

# 正确示例
name: my-skill
description: "清晰的描述，说明何时触发此 skill 以及它的功能"
```

#### 2.3 注册状态检查

检查 `.claude/settings.json` 中是否已注册：

```json
{
  "enabledPlugins": {
    "skill-name@skills-dir": true
  }
}
```

### Step 3：记录问题

对每个发现的问题，记录到问题清单中：

| 问题类型 | 严重程度 | 说明 |
|---------|:-------:|------|
| **缺失 SKILL.md** | 高 | 目录存在但无 SKILL.md 文件，skill 完全不可用 |
| **name 字段缺失** | 高 | skill 无法被识别 |
| **description 字段缺失** | 高 | skill 无法被触发 |
| **YAML 语法错误** | 高 | skill 无法被解析 |
| **未注册到 settings.json** | 中 | 可能导致 skill 不可用 |
| **空目录** | 高 | 目录完全为空，无任何内容 |

### Step 4：自动修复

根据问题类型执行相应的修复操作：

#### 修复 1：创建缺失的 SKILL.md

如果目录为空或缺失 SKILL.md，创建一个新的 SKILL.md：

```markdown
---
name: skill-name
description: |
  清晰的描述，说明此 skill 的功能和触发条件。
---

# Skill 名称

## 概述

此 skill 的定义内容...
```

**创建时需要考虑：**
- 从项目上下文中推断 skill 的用途（如 `feishu-manual-takeover` 的引用、`CLAUDE.md` 中的规则）
- 如果无法推断，标记为"需用户确认"而不是随意编造
- name 必须与目录名保持一致

#### 修复 2：修复 YAML frontmatter

使用 Edit 工具修复 frontmatter 问题：
- 补充缺失的 `name` 或 `description` 字段
- 修正 YAML 语法错误（引号匹配、缩进问题等）
- 确保 `---` 分隔符正确

#### 修复 3：注册到 settings.json

如果 skill 有有效的 SKILL.md 但未注册，添加到 `enabledPlugins`：

```json
{
  "enabledPlugins": {
    ...现有配置,
    "skill-name@skills-dir": true
  }
}
```

使用 Edit 工具修改 `F:\积昌的知识库 - 副本\.claude\settings.json`。

### Step 5：验证修复

对修复后的 skill 执行验证：

1. **读回确认**：重新读取 SKILL.md 确认 frontmatter 正确
2. **尝试调用**：使用 Skill 工具尝试调用（注意：新注册的 skill 可能需要重启会话才能被识别）

```markdown
Skill skill="skill-name" args="test"
```

3. **记录结果**：记录调用结果（成功/失败及原因）

### Step 6：生成检查报告

检查完成后，生成结构化报告：

```markdown
## Skill 健康检查报告 [YYYY-MM-DD]

### 全量检查结果
| Skill 名称 | SKILL.md | Frontmatter | 已注册 | 可调用 | 备注 |
|-----------|:--------:|:-----------:|:-----:|:-----:|------|
| skill-a   | ✅ 存在  | ✅ 有效      | ✅     | ✅     | -    |
| skill-b   | ✅ 存在  | ❌ 缺 name  | ✅     | ❌     | 已修复 |
| skill-c   | ❌ 缺失  | -           | ❌     | ❌     | 已创建 |

### 发现问题汇总
- **高严重度**：N 个（已修复 N 个）
- **中严重度**：N 个（已修复 N 个）
- **待用户确认**：N 个

### 已修复的问题
- [skill-b] 补充了缺失的 name 字段
- [skill-c] 创建了 SKILL.md 并注册到 settings.json

### 仍存在的问题
- 无（或列出无法自动修复的问题）
```

---

## 注意事项

### 路径规范

- 使用绝对路径访问 `.claude/skills/` 目录
- `settings.json` 路径：`F:\积昌的知识库 - 副本\.claude\settings.json`
- 所有相对路径均相对于 vault 根目录

### 会话缓存限制

**重要：** skill 可用列表在会话启动时编译。在当前会话中新创建或注册的 skill，需要**重启 Claude Code 会话**后才会出现在可用 skill 列表中。在报告中应明确标注这一点。

### 修复原则

1. **只修复有把握的问题** —— 如 SKILL.md 格式错误可以修，但不确定 skill 用途时不随意编造内容
2. **最小修改原则** —— 只修改必要的内容，不改变 skill 原有的功能和逻辑
3. **保留原始内容** —— 修复 frontmatter 时只修改 frontmatter，不修改 body 内容
4. **settings.json 的格式保护** —— 编辑时必须保持 JSON 格式正确，添加逗号分隔

### 常见错误模式

| 错误模式 | 示例 | 修复方法 |
|---------|------|---------|
| description 编码问题 | 中文显示为乱码 | 检查文件编码为 UTF-8 |
| metadata 字段异常 | `metadata:` 后无内容 | 删除空 metadata 或补充内容 |
| 多行字符串格式错误 | 使用 `|` 但缩进不对 | 修正 YAML 多行字符串缩进 |
| 缺少闭包 `---` | 只有开头没有结尾 | 补充 `---` |
