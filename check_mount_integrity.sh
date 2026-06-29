#!/usr/bin/env bash
# check_mount_integrity.sh — portable reality-check for a thin child-mount.
# Check-only. Does not modify files.

set -u
ROOT="${1:-.}"
cd "$ROOT" || { echo "missing path: $ROOT"; exit 2; }

FAIL=0
WARN=0
fail(){ echo "FAIL  $*"; FAIL=$((FAIL+1)); }
warn(){ echo "WARN  $*"; WARN=$((WARN+1)); }
pass(){ echo "pass  $*"; }
has(){ [ -f "$1" ]; }
refs(){ [ -f "$1" ] && grep -qiE "$2" "$1" 2>/dev/null; }

repo_name="daily-market-radar"
echo "Child Mount Reality-Check: $repo_name"

LEVEL="Level 1"
if has brain.manifest.yaml; then
  L=$(grep -Ei '^[[:space:]]*level:' brain.manifest.yaml | head -1 | sed -E 's/#.*$//; s/.*level:[[:space:]]*//I; s/["'\''']//g; s/[[:space:]]+$//')
  [ -n "$L" ] && LEVEL="$L"
fi
echo "Detected level: $LEVEL"

# Conflict markers.
HITS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  LIST=$(git -c core.quotePath=false ls-files)
else
  LIST=$(find . -type f -not -path '*/.git/*')
fi
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -qE '^<<<<<<< .' "$f" 2>/dev/null && grep -qE '^>>>>>>> .' "$f" 2>/dev/null; then
    fail "$f has unresolved conflict markers"
    HITS=$((HITS+1))
  fi
done <<EOF
$LIST
EOF
[ "$HITS" -eq 0 ] && pass "no unresolved conflict markers"

# Required thin mount entries.
has README.md && pass "README.md exists" || fail "README.md missing"
has AGENTS.md && pass "AGENTS.md exists" || fail "AGENTS.md missing"
has brain.manifest.yaml && pass "brain.manifest.yaml exists" || fail "brain.manifest.yaml missing"

if has brain.manifest.yaml; then
  refs brain.manifest.yaml 'mother_repo:[[:space:]]*o00362002/Human-AI-Collaboration-Brain' && pass "mother repo set" || fail "mother repo missing"
  refs brain.manifest.yaml 'mother_version:[[:space:]]*v1\.18-draft' && pass "mother version v1.18-draft" || fail "mother version missing"
  refs brain.manifest.yaml 'convergence_mode:[[:space:]]*inherited_from_mother' && pass "convergence mode inherited" || fail "convergence mode missing"
  refs brain.manifest.yaml 'schema_coverage_policy:[[:space:]]*inherited_from_mother' && pass "schema coverage policy inherited" || fail "schema coverage policy missing"
  refs brain.manifest.yaml 'file_governance:' && pass "file governance present" || fail "file governance missing"
  refs brain.manifest.yaml 'backtest_growth_control:' && pass "backtest growth control present" || fail "backtest growth control missing"
  refs brain.manifest.yaml 'frozen_history_check:[[:space:]]*required' && pass "frozen history check required" || fail "frozen history check missing"
  refs brain.manifest.yaml 'adoption_not_execution_edge:[[:space:]]*true' && pass "adoption boundary protected" || fail "adoption boundary missing"
fi

if has AGENTS.md; then
  refs AGENTS.md 'Convergence Mount Rules' && pass "AGENTS convergence rules present" || fail "AGENTS missing convergence rules"
  refs AGENTS.md 'Frozen history / growth control check' && pass "AGENTS requires frozen history / growth control check" || fail "AGENTS missing frozen history / growth control check"
  refs AGENTS.md 'Class A = schema-backed enforcement' && pass "AGENTS has schema coverage classes" || fail "AGENTS missing schema coverage classes"
  refs AGENTS.md 'Adoption Layer is not Execution Edge' && pass "AGENTS protects Adoption" || fail "AGENTS missing Adoption protection"
fi

case "$LEVEL" in
  *2*|*3A*|*3B*|*3a*|*3b*|*Module*)
    has CURRENT_STATE.md && pass "CURRENT_STATE.md exists" || warn "CURRENT_STATE.md recommended for $LEVEL"
    { has CURRENT_DECISIONS.md || has DECISIONS.md; } && pass "decisions file exists" || warn "decisions file recommended for $LEVEL"
    ;;
  *) : ;;
esac
case "$LEVEL" in
  *3A*|*3B*|*3a*|*3b*)
    has DEPENDENCY_MAP.md && pass "DEPENDENCY_MAP.md exists" || warn "DEPENDENCY_MAP.md recommended for $LEVEL"
    ;;
esac

echo "Result: FAIL=$FAIL WARN=$WARN"
if [ "$FAIL" -gt 0 ]; then echo "partial change required"; exit 1; fi
echo "complete"; exit 0
