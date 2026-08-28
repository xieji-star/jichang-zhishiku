# Test Wiki CLAUDE.md

## Wiki 目录结构

```
wiki/
├── HTTP错误概述.md
└── 面试技巧.md
```

## 架构三层

| 层级 | 位置 | 角色 |
|------|------|------|
| 原始来源 | `sources/` | 只读 |
| Wiki | `wiki/` | Claude 写权限 |
| Schema | 本文件 | 维护约定 |

## 页面约定

每个 Wiki 页面包含 YAML frontmatter：title、category、tags、source、created、updated。

## 关键原则

1. **原始来源绝不修改**
2. 每次操作后更新 index.md 和 log.md
3. 好的答案归档回 Wiki
