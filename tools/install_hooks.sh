#!/usr/bin/env bash
# Install the repository pre-commit gate.
set -u
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not inside a git repository"; exit 1; }
HOOK="$(git rev-parse --git-path hooks)/pre-commit"
mkdir -p "$(dirname "$HOOK")"
cat > "$HOOK" <<'EOF'
#!/bin/sh
[ "${SKIP_BRAIN_HOOK:-}" = "1" ] && exit 0
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT" || exit 0
STAGED=$(git diff --cached --name-only)
[ -z "$STAGED" ] && exit 0

# Core structural capability mapping.
node tools/brain/check-core.js "$ROOT" || exit 1

# Core protected-file confirmation gate.
node tools/brain/check-pre-change-confirmation.js "$ROOT" || exit 1

# Existing process-evidence gate for current state and decisions.
if [ "${SKIP_PROCESS_GATE:-}" != "1" ]; then
  if printf '%s\n' "$STAGED" | grep -qE '^(CURRENT_STATE\.md|CURRENT_DECISIONS\.md)$'; then
    if ! printf '%s\n' "$STAGED" | grep -qE '^reports/'; then
      echo "pre-commit blocked: state/decisions changed without a reports/ record"
      exit 1
    fi
  fi
fi

# Daily Radar domain gate.
node tools/brain/check-domain-packs.js "$ROOT" || exit 1

# Advisory relationship and path checks.
node tools/brain/check-sync-matrix.js "$ROOT" || true
node tools/brain/check-doc-paths.js "$ROOT" --staged || true
exit 0
EOF
chmod +x "$HOOK"
echo "daily-market-radar gate installed -> $HOOK"
