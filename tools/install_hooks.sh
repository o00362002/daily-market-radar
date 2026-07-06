#!/usr/bin/env bash
# install_hooks.sh — 安裝 brain-core 式 commit 關口（child mount 版，自足）。
# 用法：bash tools/install_hooks.sh
# 整體跳過一次：SKIP_BRAIN_HOOK=1 git commit …
# 只跳過流程證據閘：SKIP_PROCESS_GATE=1 git commit …（跳過本身是被看見的選擇）
set -u
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "不在 git repo 內"; exit 1; }
HOOK="$(git rev-parse --git-path hooks)/pre-commit"
mkdir -p "$(dirname "$HOOK")"
cat > "$HOOK" <<'EOF'
#!/bin/sh
# daily-market-radar pre-commit（tools/install_hooks.sh 產生，brain-core child mount）
[ "${SKIP_BRAIN_HOOK:-}" = "1" ] && exit 0
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT" || exit 0
STAGED=$(git diff --cached --name-only)
[ -z "$STAGED" ] && exit 0

# 不變式 4：結構體檢（擋——必備檔＋入口預算＋不變式數量鎖）
node tools/brain/check-core.js "$ROOT" || {
  echo "pre-commit 擋下：結構體檢紅（見上）。整體跳過一次：SKIP_BRAIN_HOOK=1"; exit 1; }

# 不變式 5：領域包完整性（擋——新領域填不完整不放行）
node tools/brain/check-domain-packs.js "$ROOT" || {
  echo "pre-commit 擋下：領域包不完整（見上）。整體跳過一次：SKIP_BRAIN_HOOK=1"; exit 1; }

# 不變式 1：流程證據閘（擋；逃生門 SKIP_PROCESS_GATE=1）
if [ "${SKIP_PROCESS_GATE:-}" != "1" ]; then
  if printf '%s\n' "$STAGED" | grep -qE '^(CURRENT_STATE\.md|CURRENT_DECISIONS\.md)$'; then
    if ! printf '%s\n' "$STAGED" | grep -qE '^reports/'; then
      echo "pre-commit 擋下：動了 CURRENT_STATE/CURRENT_DECISIONS 但沒附 reports/ 紀錄（不變式 1）"
      echo "補一份紀錄再 commit；真要略過：SKIP_PROCESS_GATE=1 git commit …"
      exit 1
    fi
  fi
fi

# 不變式 2、3：提醒（不擋）
node tools/brain/check-sync-matrix.js "$ROOT" || true
node tools/brain/check-doc-paths.js "$ROOT" --staged || true
exit 0
EOF
chmod +x "$HOOK"
echo "brain-core child 關口已安裝 → $HOOK"
