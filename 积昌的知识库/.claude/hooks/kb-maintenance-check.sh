#!/usr/bin/env bash
# ============================================================
# 知识库自动维护触发检查（UserPromptSubmit hook）
# ------------------------------------------------------------
# 触发时机：每天最新一条消息到达时自动运行
# 逻辑：
#   1) 读取当前时间（精确到分钟）与星期几
#   2) 与标记文件比对：
#      - 距上次 LLM Wiki 迭代 >= 3 天        → 提示自动迭代
#      - 距上次 GitHub 上传 >= 7 天，或今天是周一 → 提示自动上传
#   3) 无到期任务，或当天已提示过 → 静默退出
# 输出（到期时）：JSON
#   { "systemMessage": "...",
#     "hookSpecificOutput": { "hookEventName": "UserPromptSubmit",
#                             "additionalContext": "..." } }
# ============================================================
set -u

VAULT="$(cd "$(dirname "$0")/../.." && pwd)"
[ -n "$VAULT" ] || exit 0

# 仅获取一条时间记录（当前时间，精确到分钟），其余字段均由该记录派生
NOW_MIN="$(date '+%Y-%m-%d_%H:%M')"
TODAY="${NOW_MIN:0:10}"
MMDD="${NOW_MIN:5:2}${NOW_MIN:8:2}"
WEEKDAY="$(date -d "$TODAY" '+%u')"
EPOCH_NOW="$(date -d "$TODAY" '+%s')"

M_WIKI="$VAULT/.last-wiki-maintain"
M_GH="$VAULT/.last-github-backup"
M_PROMPT="$VAULT/.last-maintenance-prompt"

# 标记文件缺失或为空时，初始化为久远日期，保证首次触发
for m in "$M_WIKI" "$M_GH"; do
  [ -s "$m" ] || echo "2000-01-01" > "$m"
done

to_epoch() {
  local d="${1//[$'\t\r\n ']/}"   # 去掉空白字符
  [ -n "$d" ] || d="2000-01-01"    # 空值 → 久远日期，保证触发
  date +%s -d "$d" 2>/dev/null || echo 0
}

wiki_days=$(( (EPOCH_NOW - $(to_epoch "$(<"$M_WIKI")")) / 86400 ))
gh_days=$(( (EPOCH_NOW - $(to_epoch "$(<"$M_GH")")) / 86400 ))
[ "$wiki_days" -lt 0 ] && wiki_days=0
[ "$gh_days" -lt 0 ] && gh_days=0

need_wiki=0
need_gh=0
[ "$wiki_days" -ge 3 ] && need_wiki=1
{ [ "$gh_days" -ge 7 ] || [ "$WEEKDAY" -eq 1 ]; } && need_gh=1

# 无到期任务 → 静默退出
if [ "$need_wiki" -eq 0 ] && [ "$need_gh" -eq 0 ]; then
  exit 0
fi

# 当天已提示过 → 退出（避免同一天重复刷屏）
if [ -s "$M_PROMPT" ] && [ "$(<"$M_PROMPT")" = "$TODAY" ]; then
  exit 0
fi

# ---- 组装到期任务说明 ----
TASKS=""
if [ "$need_wiki" -eq 1 ]; then
  TASKS="1. 【LLM Wiki 迭代】距上次知识库迭代已 ${wiki_days} 天（≥3 天）。请依据「自动维护知识库/LLM Wiki.md」方法论与「自动维护知识库/CLAUDE.md」规范，执行一轮 ingest/query/lint 迭代优化，同步维护「自动维护知识库/index.md」与「自动维护知识库/log.md」，完成后将标记文件「.last-wiki-maintain」更新为 ${TODAY}。"
fi
if [ "$need_gh" -eq 1 ]; then
  if [ "$WEEKDAY" -eq 1 ]; then
    gh_reason="今天是周一（每周例行）"
  else
    gh_reason="距上次上传已 ${gh_days} 天（≥7 天）"
  fi
  [ -n "$TASKS" ] && TASKS="${TASKS}"$'\n'
  TASKS="${TASKS}2. 【GitHub 增量上传】${gh_reason}。请执行增量备份脚本「bash .claude/hooks/kb-github-backup.sh」：在本地镜像仓库 F:/jichang-backup 内 git pull → 用 robocopy 将备份范围（.claude、.claudian、.obsidian、AGENTS.md、CLAUDE.md、总结好的大纲以及笔记、自动维护知识库）增量同步到单一目录「积昌的知识库/」→ git add -A + commit（提交信息含日期）+ push，仅提交变更与新增文件、不新建日期文件夹；无变更则跳过提交。完成后将标记文件「.last-github-backup」更新为 ${TODAY}。"
fi

# 记录当天已提示
echo "$TODAY" > "$M_PROMPT"

# ---- 转义为 JSON：先转义反斜杠与引号，再把实际换行转成 \n ----
ESC="$(printf '%s' "$TASKS" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk '{printf "%s\\n", $0}')"

printf '{"systemMessage":"[知识库自动维护触发] 当前时间：%s，检测到到期维护任务（详见提示）。","hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"[知识库自动维护触发] 当前时间：%s。到期任务如下：\\n%s"}}' "$NOW_MIN" "$NOW_MIN" "$ESC"
