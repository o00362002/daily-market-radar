#!/usr/bin/env bash
# check_mount_integrity.sh — brain-core child mount 的 CI／人工體檢入口（薄包裝）。
#
# 舊版是母腦 capability 模型的散文式檢查；2026-07-06 換掛 brain-core 後，
# 真正的規則都住在 tools/brain/*.js（資料＋檢查器），本檔只負責把它們串起來，
# 讓 CI（.github/workflows/mount-check.yml）與人工用同一個入口。
#
# Usage:  bash check_mount_integrity.sh [path]
# Exit:   0 = complete, 1 = 結構紅, 2 = bad path
set -u
ROOT="${1:-.}"
cd "$ROOT" || { echo "missing path: $ROOT"; exit 2; }

FAIL=0
echo "Child Mount Reality-Check (brain-core)"

# 衝突標記掃描（cheap、擋）
HITS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then LIST=$(git -c core.quotePath=false ls-files); else LIST=$(find . -type f -not -path '*/.git/*'); fi
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -qE '^<<<<<<< .' "$f" 2>/dev/null && grep -qE '^>>>>>>> .' "$f" 2>/dev/null; then
    echo "FAIL  $f has unresolved conflict markers"; HITS=$((HITS+1)); FAIL=1
  fi
done <<EOF
$LIST
EOF
[ "$HITS" -eq 0 ] && echo "pass  no unresolved conflict markers"

command -v node >/dev/null 2>&1 || { echo "FAIL  node 不存在（檢查器需要 node）"; exit 1; }

# 不變式 4：結構體檢（擋）
node tools/brain/check-core.js "$PWD" || FAIL=1

# 不變式 5：領域包完整性（擋）
node tools/brain/check-domain-packs.js "$PWD" || FAIL=1

# 不變式 2、3：連動提醒＋路徑現實（advisory，不擋）
node tools/brain/check-sync-matrix.js "$PWD" || echo "WARN  sync-matrix 有應檢視而未動的檔案（advisory，見上）"
node tools/brain/check-doc-paths.js "$PWD" || echo "WARN  doc-paths：文件宣稱的路徑與檔案樹不一致（advisory，見上）"

if [ "$FAIL" -gt 0 ]; then echo "Result: partial change required"; exit 1; fi
echo "Result: complete"; exit 0
