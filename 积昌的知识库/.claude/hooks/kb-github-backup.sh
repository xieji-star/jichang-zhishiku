#!/usr/bin/env bash
# ============================================================
# 知识库 GitHub 增量备份脚本（单一目录）
# ------------------------------------------------------------
# 用法：bash .claude/hooks/kb-github-backup.sh
# 说明：将知识库备份范围增量同步到本地镜像仓库 F:/jichang-backup
#       的单一目录「积昌的知识库/」，git add -A + commit + push，
#       仅提交变更与新增文件（未改动文件跳过），完成后更新标记。
# 备份范围（固定，与远程最新快照一致）：
#   .claude .claudian .obsidian AGENTS.md CLAUDE.md
#   总结好的大纲以及笔记 自动维护知识库
# 不备份（排除）：
#   lark-resources、lark-im-resources、wecom-resources、
#   飞书智能助手、微信智能助手、收件箱 等大体积/临时资源目录
# ============================================================
set -u

VAULT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_DIR="F:/jichang-backup"
TARGET="$BACKUP_DIR/积昌的知识库"
REPO_URL="https://github.com/xieji-star/jichang-zhishiku.git"

ITEMS=(.claude .claudian .obsidian AGENTS.md CLAUDE.md "总结好的大纲以及笔记" "自动维护知识库")

# 网络重试：应对 GitHub 瞬时 SSL/网络抖动（最多 4 次，间隔 3s）
retry() {
  local n=1 max=4 delay=3
  until "$@"; do
    if [ "$n" -ge "$max" ]; then return 1; fi
    echo "  ⏳ 网络重试第 ${n} 次: $*"
    sleep "$delay"
    n=$((n+1))
  done
}

echo "=== [1/5] 确保镜像仓库 $BACKUP_DIR ==="
if [ ! -d "$BACKUP_DIR/.git" ]; then
  echo "镜像仓库不存在，首次克隆（仅最新提交）..."
  git clone --depth 1 --filter=blob:none --no-checkout "$REPO_URL" "$BACKUP_DIR" || { echo "❌ 克隆失败"; exit 1; }
  git -C "$BACKUP_DIR" sparse-checkout init --cone
  git -C "$BACKUP_DIR" sparse-checkout set "积昌的知识库"
  git -C "$BACKUP_DIR" checkout || { echo "❌ 检出失败"; exit 1; }
fi

echo "=== [2/5] git pull 拉取远端最新 ==="
retry git -C "$BACKUP_DIR" pull --quiet || { echo "❌ git pull 失败"; exit 1; }
mkdir -p "$TARGET"

echo "=== [3/5] 增量同步备份范围（robocopy，经 Python 传中文路径）==="
WIN_VAULT="$(cygpath -w "$VAULT")"
WIN_TARGET="$(cygpath -w "$TARGET")"
ITEMS_STR="$(IFS='|'; echo "${ITEMS[*]}")"
if ! PYTHONUTF8=1 python - "$WIN_VAULT" "$WIN_TARGET" "$ITEMS_STR" <<'PY'
import os, subprocess, sys, shutil
vault, backup, items_str = sys.argv[1], sys.argv[2], sys.argv[3]
items = [i for i in items_str.split("|") if i]

# 敏感/运行态内容排除（不进 GitHub 公开仓库）：
#   ROBO_EXTRA = robocopy 额外参数（优先避免复制）
#   CLEANUP    = 同步后强制清理的相对路径（防 /MIR 残留历史数据）
ROBO_EXTRA = {
    ".claudian": ["/XD", "sessions"],   # Claude 会话运行态目录（含密钥/对话记录）
}
CLEANUP = {
    ".claudian": ["sessions"],
    "总结好的大纲以及笔记": ["实习就业/创业黑马——数智科技部门/全自动爬取短视频、推文爆款程序/本地部署短视频分析程序介绍文档.md"],
    "自动维护知识库": [".obsidian/plugins/infio-copilot/data.json"],
}
failed = 0
for item in items:
    src = os.path.join(vault, item)
    dst = os.path.join(backup, item)
    if not os.path.exists(src):
        print("  ⚠ 跳过（源不存在）:", item)
        continue
    if os.path.isdir(src):
        os.makedirs(dst, exist_ok=True)
        cmd = ["robocopy", src, dst, "/MIR", "/R:2", "/W:2", "/NFL", "/NDL", "/NJH", "/NJS"]
        cmd += ROBO_EXTRA.get(item, [])
        r = subprocess.run(cmd, capture_output=True)
        rc = r.returncode
        if 0 <= rc <= 7:
            print("  ✔ 同步:", item)
        else:
            print("  ❌ 同步失败:", item, "(rc=%d)" % rc)
            failed = 1
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print("  ✔ 同步:", item)
    # 同步后清理敏感/运行态路径（防止 /MIR 不清理已存在的排除项）
    for rel in CLEANUP.get(item, []):
        p = os.path.join(dst, rel)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
            print("  🧹 已排除目录:", rel)
        elif os.path.isfile(p):
            os.remove(p)
            print("  🧹 已排除文件:", rel)
sys.exit(failed)
PY
then
  echo "❌ 同步存在失败项，中止上传"
  exit 1
fi

echo "=== [4/5] git add -A + commit + push ==="
git -C "$BACKUP_DIR" add -A
if git -C "$BACKUP_DIR" diff --cached --quiet; then
  echo "  无变更，跳过提交与推送。"
else
  git -C "$BACKUP_DIR" commit --quiet -m "知识库备份 $(date '+%Y-%m-%d')（增量）" || { echo "❌ commit 失败"; exit 1; }
  retry git -C "$BACKUP_DIR" push --quiet || { echo "❌ push 失败"; exit 1; }
  echo "  已提交并推送变更。"
fi

echo "=== [5/5] 更新 .last-github-backup ==="
echo "$(date '+%Y-%m-%d')" > "$VAULT/.last-github-backup"
echo "✅ 增量备份完成。"
