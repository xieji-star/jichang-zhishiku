#!/usr/bin/env bash
# ============================================================
# 知识库中间文件自动清理脚本（SessionEnd hook）
# ------------------------------------------------------------
# 触发时机：每次工作结束（会话结束）时自动运行
# 清理对象：
#   1) 知识库根目录的临时输出/测试文件（_*.txt、_test_*.pdf、_test_*.png、_preview_bg/、临时_* 等）
#   2) 根目录损坏路径文件（F:积昌的知识库）、临时脚本（*_update_doc_*.py）、
#      命名错误的重名 .md、未完成的模型下载（*.part）
#   3) 中间文件/lark-resources 下的中间产物（认证二维码、学员案例提取、群消息图片、近期爆款 dump）
#   4) 中间文件/lark-im-resources 下的所有下载/转换中间文件（保留空目录）
#   5) 全库范围内名为 _pdf_img 的 PDF 转图中间产物文件夹（page-*.png 逐页渲染图，
#      可随时由源 PDF 重新生成；源文件/ 保留目录除外）
# 保留对象：
#   - 中间文件/lark-resources/数字人口播脚本发音处理.html （TTS 纠错工具，业务在用）
#   - 根目录标记文件 .last-github-backup / .last-wiki-maintain / .last-maintenance-prompt
#   - 其余所有已整理笔记、技能、配置
# 安全：所有 rm 均带 -f，文件不存在时不报错；set -u 仅防未定义变量。
# ============================================================
set -u

VAULT="$(cd "$(dirname "$0")/../.." && pwd)"
[ -n "$VAULT" ] || exit 0

# ---- 1. 根目录临时输出 / 测试文件 ----
rm -f "$VAULT"/_*.txt 2>/dev/null
rm -f "$VAULT"/_test_*.pdf 2>/dev/null
rm -f "$VAULT"/_test_*.png 2>/dev/null
rm -f "$VAULT"/临时_* 2>/dev/null
rm -f "$VAULT"/_preview_*.png 2>/dev/null
rm -rf "$VAULT"/_preview_bg 2>/dev/null

# ---- 2. 根目录损坏/临时/重复文件 ----
rm -f "$VAULT/F:积昌的知识库" 2>/dev/null
rm -f "$VAULT"/积昌的知识库\ -\ 副本_update_doc_*.py 2>/dev/null
rm -f "$VAULT"/积昌的知识库\ -\ 副本总结好的大纲* 2>/dev/null
rm -f "$VAULT"/.yolov8m-seg.pt.*.part 2>/dev/null

# ---- 3. 中间文件/lark-resources 中间产物（保留 数字人口播脚本发音处理.html）----
rm -f "$VAULT"/中间文件/lark-resources/_*.png 2>/dev/null
rm -f "$VAULT"/中间文件/lark-resources/近期爆款-3人小组.txt 2>/dev/null
rm -f "$VAULT"/中间文件/lark-resources/近期爆款-可读版.txt 2>/dev/null
rm -rf "$VAULT"/中间文件/lark-resources/学员案例提取 2>/dev/null
rm -rf "$VAULT"/中间文件/lark-resources/学员案例打包文件 2>/dev/null
rm -rf "$VAULT"/中间文件/lark-resources/群消息图片 2>/dev/null

# ---- 4. 中间文件/lark-im-resources 下载/转换中间文件（保留空目录）----
if [ -d "$VAULT/中间文件/lark-im-resources" ]; then
  rm -rf "$VAULT"/中间文件/lark-im-resources/* 2>/dev/null
fi

# ---- 5. 全库 PDF 转图中间产物文件夹 _pdf_img（源文件/ 保留目录除外，直接剪枝跳过整棵子树）----
find "$VAULT" -path "$VAULT/源文件" -prune -o -type d -name "_pdf_img" -prune -exec rm -rf {} + 2>/dev/null

exit 0
