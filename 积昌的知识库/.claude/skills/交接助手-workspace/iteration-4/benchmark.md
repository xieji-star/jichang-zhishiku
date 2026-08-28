# Skill Benchmark: 交接助手

**Model**: <model-name>
**Date**: 2026-08-18T02:32:36Z
**Evals**: 2, 4, 5, 6 (1 run each per configuration)

## Summary

| Metric | With Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 100% ± 0% | +0.00 |
| Time | 140.2s ± 35.4s | 152.8s ± 45.2s | -12.6s |
| Tokens | 63381 ± 3441 | 66351 ± 8693 | -2970 |

## Per-Eval Results

| Eval | Config | Pass | Total | Rate | Time (s) | Tokens |
|------|--------|------|-------|------|----------|--------|
| 2-human-detailed | with_skill | 9 | 9 | 100% | 144.9 | 59588 |
| 2-human-detailed | old_skill | 9 | 9 | 100% | 198.3 | 65908 |
| 4-codex-custom | with_skill | 8 | 8 | 100% | 97.9 | 61361 |
| 4-codex-custom | old_skill | 8 | 8 | 100% | 96.5 | 57003 |
| 5-deepseek-codex-diff | with_skill | 7 | 7 | 100% | 134.1 | 66574 |
| 5-deepseek-codex-diff | old_skill | 7 | 7 | 100% | 138.1 | 64494 |
| 6-four-element-detail | with_skill | 7 | 7 | 100% | 184.0 | 66000 |
| 6-four-element-detail | old_skill | 7 | 7 | 100% | 178.5 | 78000 |

## Key Takeaways

- **通过率**：新版与旧版均 100%（8/8 runs），无回归。
- **耗时**：新版平均 140.2s，比旧版快 12.6s（-8.2%）。
- **Token**：新版平均 63381 tokens，比旧版少 2970 tokens（-4.5%）。
- **本质差异（eval-5 实证）**：同一项目给 DeepSeek（L3）与 Codex（L1）的两份文档，新版 DeepSeek 版 313 行 vs 旧版 244 行——自包含贴代码、人代跑验证、证据分级更强；Codex 版 204 行保持精确路径+PowerShell+函数级定位。证明"AI 差异化适配"落实到了内容密度与指令粒度层面，非改标题。
