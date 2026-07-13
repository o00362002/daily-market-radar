#!/usr/bin/env bash
# CI and manual validation entry.
set -u
ROOT="${1:-.}"
cd "$ROOT" || { echo "missing path: $ROOT"; exit 2; }
FAIL=0

echo "daily-market-radar reality check"

HITS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  LIST=$(git -c core.quotePath=false ls-files)
else
  LIST=$(find . -type f -not -path '*/.git/*')
fi
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -qE '^<<<<<<< .' "$f" 2>/dev/null && grep -qE '^>>>>>>> .' "$f" 2>/dev/null; then
    echo "FAIL  $f has unresolved conflict markers"; HITS=$((HITS+1)); FAIL=1
  fi
done <<EOF
$LIST
EOF
[ "$HITS" -eq 0 ] && echo "pass  no unresolved conflict markers"

command -v node >/dev/null 2>&1 || { echo "FAIL  node is required"; exit 1; }

# Core governance checks.
node tools/brain/check-core.js "$PWD" || FAIL=1
node tools/brain/check-pre-change-confirmation.js "$PWD" || FAIL=1

# Daily Radar domain checks.
node tools/brain/check-domain-packs.js "$PWD" || FAIL=1

# Advisory checks.
node tools/brain/check-sync-matrix.js "$PWD" || echo "WARN  sync review advisory"
node tools/brain/check-doc-paths.js "$PWD" || echo "WARN  doc-path advisory"

if [ "$FAIL" -gt 0 ]; then echo "Result: partial change required"; exit 1; fi
echo "Result: complete"; exit 0
