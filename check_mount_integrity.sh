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
  L=$(awk -F: '/^[[:space:]]*level:/ {print $2; exit}' brain.manifest.yaml 2>/dev/null)
  L=${L%%#*}
  L=$(printf '%s' "$L" | xargs 2>/dev/null)
  [ -n "$L" ] && LEVEL="$L"
fi
echo "Detected level: $LEVEL"

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

has README.md && pass "README.md exists" || fail "README.md missing"
has AGENTS.md && pass "AGENTS.md exists" || fail "AGENTS.md missing"
has brain.manifest.yaml && pass "brain.manifest.yaml exists" || fail "brain.manifest.yaml missing"

if has brain.manifest.yaml; then
  refs brain.manifest.yaml 'mother_repo:[[:space:]]*o00362002/Human-AI-Collaboration-Brain' && pass "mother repo set" || fail "mother repo missing"
  refs brain.manifest.yaml 'mother_version:[[:space:]]*v[0-9]+\.[0-9]+(-[A-Za-z0-9._-]+)?' && pass "mother version field present" || warn "mother version field missing or nonstandard"
  refs brain.manifest.yaml 'mother_architecture:[[:space:]]*compact_five_layer|architecture_layers:' && pass "compact five-layer mount present" || warn "compact five-layer mount not yet recorded"
  refs brain.manifest.yaml 'convergence_mode:' && pass "convergence mode field present" || warn "convergence mode field missing"
  refs brain.manifest.yaml 'schema_coverage_policy:' && pass "schema coverage policy field present" || warn "schema coverage policy field missing"
  refs brain.manifest.yaml 'file_governance:' && pass "file governance present" || warn "file governance missing"
  refs brain.manifest.yaml 'backtest_growth_control:' && pass "backtest growth control present" || warn "backtest growth control missing"
  refs brain.manifest.yaml 'adoption_layer:' && fail "legacy adoption_layer key still present" || pass "no legacy adoption_layer key"
  refs brain.manifest.yaml 'adoption_not_execution_edge:' && fail "legacy adoption_not_execution_edge key still present" || pass "no legacy adoption_not_execution_edge key"
  refs brain.manifest.yaml 'adoption_gate_under_interface:' && pass "adoption gate boundary field present" || warn "adoption gate boundary field missing"
fi

if has AGENTS.md; then
  refs AGENTS.md 'Convergence Mount Rules' && pass "AGENTS convergence rules present" || warn "AGENTS missing convergence rules"
  refs AGENTS.md 'Class A = schema-backed enforcement' && pass "AGENTS has schema coverage classes" || warn "AGENTS missing schema coverage classes"
  refs AGENTS.md 'Adoption Layer is not Execution Edge' && fail "AGENTS still has legacy Adoption Layer wording" || pass "no legacy AGENTS Adoption Layer wording"
  refs AGENTS.md 'Adoption Gate belongs under Interface & Integration Layer' && pass "AGENTS protects Adoption Gate" || warn "AGENTS missing Adoption Gate wording"
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

has DEPENDENCY_MAP.md && pass "DEPENDENCY_MAP.md exists" || fail "DEPENDENCY_MAP.md missing"
has AGENT_DEFINITION_MAP.md && pass "AGENT_DEFINITION_MAP.md exists" || fail "AGENT_DEFINITION_MAP.md missing"
has workflows/daily_radar_workflow.md && pass "daily_radar_workflow.md exists" || fail "daily_radar_workflow.md missing"
has workflows/daily_push_brief_workflow.md && pass "daily_push_brief_workflow.md exists" || fail "daily_push_brief_workflow.md missing"
has templates/daily_report_template.md && pass "daily_report_template.md exists" || fail "daily_report_template.md missing"
has templates/daily_push_brief_template.md && pass "daily_push_brief_template.md exists" || fail "daily_push_brief_template.md missing"
[ ! -f workflows/daily_execution_gate.md ] && pass "no separate daily_execution_gate.md" || fail "remove separate daily_execution_gate.md"

if has DEPENDENCY_MAP.md; then
  refs DEPENDENCY_MAP.md 'Full Daily Radar Gate' && pass "DEPENDENCY_MAP has full gate" || fail "DEPENDENCY_MAP missing full gate"
  refs DEPENDENCY_MAP.md 'Daily Push Brief Gate' && pass "DEPENDENCY_MAP has brief gate" || fail "DEPENDENCY_MAP missing brief gate"
  refs DEPENDENCY_MAP.md 'AGENT_RADAR_REPORT' && pass "DEPENDENCY_MAP maps AGENT_RADAR_REPORT" || fail "DEPENDENCY_MAP missing AGENT_RADAR_REPORT"
  refs DEPENDENCY_MAP.md 'AGENT_DAILY_PUSH_BRIEF' && pass "DEPENDENCY_MAP maps AGENT_DAILY_PUSH_BRIEF" || fail "DEPENDENCY_MAP missing AGENT_DAILY_PUSH_BRIEF"
fi

if has AGENT_DEFINITION_MAP.md; then
  refs AGENT_DEFINITION_MAP.md 'DEPENDENCY_MAP\.md / Daily Push Brief Gate' && pass "AGENT map points brief gate to DEPENDENCY_MAP" || fail "AGENT map missing brief gate pointer"
fi

echo "Result: FAIL=$FAIL WARN=$WARN"
if [ "$FAIL" -gt 0 ]; then echo "partial change required"; exit 1; fi
echo "complete"; exit 0
