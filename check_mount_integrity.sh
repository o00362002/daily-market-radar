#!/usr/bin/env bash
# check_mount_integrity.sh — portable reality-check for a thin child-mount.
#
# Unlike the mother's tools/check_repo_integrity.sh (which checks the full
# six-layer brain), this checks only what a THIN child needs, by its Level.
# It requires NO mother files, runs on bash 3.2 (macOS default), and stays small.
#
# Usage:  bash check_mount_integrity.sh [path]
# Exit:   0 = ok, 1 = needs "partial change", 2 = bad path
set -u
ROOT="${1:-.}"
cd "$ROOT" || { echo "missing path: $ROOT"; exit 2; }

FAIL=0; WARN=0
fail(){ echo "FAIL  $*"; FAIL=$((FAIL+1)); }
warn(){ echo "WARN  $*"; WARN=$((WARN+1)); }
pass(){ echo "pass  $*"; }
has(){ [ -f "$1" ]; }
refs(){ [ -f "$1" ] && grep -qiE "$2" "$1" 2>/dev/null; }

echo "Child Mount Reality-Check"

# Level detection: prefer brain.manifest.yaml `level:`; default Level 1.
# Strip inline comments (# ...) and quotes; keep the "Level N" value (with its space).
LEVEL="Level 1"
if has brain.manifest.yaml; then
  L=$(grep -Ei '^[[:space:]]*level:' brain.manifest.yaml | head -1 \
      | sed -E 's/#.*$//; s/.*level:[[:space:]]*//I; s/["'\''']//g; s/[[:space:]]+$//')
  [ -n "$L" ] && LEVEL="$L"
fi
# If the placeholder was never replaced, warn instead of silently treating as Level 1.
case "$LEVEL" in
  *'<LEVEL>'*) warn "level not set in brain.manifest.yaml (still <LEVEL>) — defaulting to Level 1"; LEVEL="Level 1" ;;
esac
echo "Detected level: $LEVEL"

# Conflict markers across tracked/listed files.
# core.quotePath=false so non-ASCII (e.g. Chinese) filenames are not octal-escaped/skipped.
HITS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then LIST=$(git -c core.quotePath=false ls-files); else LIST=$(find . -type f -not -path '*/.git/*'); fi
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -qE '^<<<<<<< .' "$f" 2>/dev/null && grep -qE '^>>>>>>> .' "$f" 2>/dev/null; then
    fail "$f has unresolved conflict markers"; HITS=$((HITS+1))
  fi
done <<EOF
$LIST
EOF
[ "$HITS" -eq 0 ] && pass "no unresolved conflict markers"

# Always required: a first entry + an AI execution entry that carries the contract.
has README.md && pass "README.md exists" || fail "README.md missing (every Level needs a first entry)"
if has AGENTS.md; then
  pass "AGENTS.md exists"
  refs AGENTS.md 'Execution Contract|four gates|Entry Gate|partial change' \
    && pass "AGENTS.md carries the execution contract" \
    || fail "AGENTS.md present but missing the execution contract (four gates)"
else
  warn "AGENTS.md missing (recommended whenever AI regularly modifies this repo)"
fi

# Level-scaled recommended memory files (WARN, not FAIL — stays thin/simple).
# *Module* matches "Module Level": a Module Level 2 expects state/decisions memory.
case "$LEVEL" in
  *2*|*3A*|*3B*|*3a*|*3b*|*Module*)
    has CURRENT_STATE.md && pass "CURRENT_STATE.md exists" || warn "CURRENT_STATE.md recommended for $LEVEL"
    { has CURRENT_DECISIONS.md || has DECISIONS.md; } && pass "decisions file exists" || warn "CURRENT_DECISIONS.md recommended for $LEVEL"
    ;;
  *) : ;;  # Level 1 needs only README (+ optional AGENTS)
esac
case "$LEVEL" in
  *3A*|*3B*|*3a*|*3b*)
    has DEPENDENCY_MAP.md && pass "DEPENDENCY_MAP.md exists" || warn "DEPENDENCY_MAP.md recommended for $LEVEL"
    ;;
esac

echo "Result: FAIL=$FAIL WARN=$WARN"
if [ "$FAIL" -gt 0 ]; then echo "partial change required"; exit 1; fi
echo "complete"; exit 0
