#!/usr/bin/env bash
# check_mount_integrity.sh — portable reality-check for a thin child-mount.
#
# Unlike the mother's tools/check_repo_integrity.sh (which checks the full
# mother-Brain architecture), this checks only what a THIN child needs, by its Level.
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

SESSION_ROOT="$(pwd)"
echo "Child Mount Reality-Check"

# Depth detection: prefer `capabilities:` (canonical, MOUNT_DEPTH.md); else legacy
# `level:` alias; default Level 1. Strip inline comments, quotes, trailing spaces.
CAPS=""
LEVEL="Level 1"
if has brain.manifest.yaml; then
  C=$(grep -Ei '^[[:space:]]*capabilities:' brain.manifest.yaml | head -1 \
      | sed -E 's/#.*$//; s/.*capabilities:[[:space:]]*//I; s/[][]//g; s/[[:space:]]+$//' \
      | tr -d "\"'")
  [ -n "$C" ] && CAPS="$C"
  L=$(grep -Ei '^[[:space:]]*level:' brain.manifest.yaml | head -1 \
      | sed -E 's/#.*$//; s/.*level:[[:space:]]*//I; s/[[:space:]]+$//' \
      | tr -d "\"'")
  [ -n "$L" ] && LEVEL="$L"
fi
# If the placeholder was never replaced, warn instead of silently treating as Level 1.
case "$LEVEL" in
  *'<LEVEL>'*) warn "level not set in brain.manifest.yaml (still <LEVEL>) — defaulting to Level 1"; LEVEL="Level 1" ;;
esac
# Legacy level alias -> capability set (hand-aligned mirror of schema/mount-capabilities.json level_equivalents).
if [ -z "$CAPS" ]; then
  case "$LEVEL" in
    *Module*)   CAPS="entry, state, decisions" ;;
    *3A*|*3a*)  CAPS="entry, state, decisions, routing, dependencies" ;;
    *3B*|*3b*)  CAPS="entry, state, decisions, routing, dependencies, loops, sync, memory-promotion" ;;
    *2*)        CAPS="entry, state, decisions, routing" ;;
    *)          CAPS="entry" ;;
  esac
  echo "Detected level: $LEVEL (alias -> capabilities: $CAPS)"
else
  echo "Detected capabilities: $CAPS"
fi
hascap(){ case ", $CAPS," in *", $1,"*|*",$1,"*) return 0;; *) return 1;; esac; }

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
  refs AGENTS.md 'Execution Contract|gate|Entry Gate|partial change' \
    && pass "AGENTS.md carries the execution contract" \
    || fail "AGENTS.md present but missing the execution contract"
else
  warn "AGENTS.md missing (recommended whenever AI regularly modifies this repo)"
fi

# Capability-scaled memory and routing files (depth = mounted capabilities).
if hascap state; then
  has CURRENT_STATE.md && pass "CURRENT_STATE.md exists" || warn "CURRENT_STATE.md recommended (state capability mounted)"
fi
if hascap decisions; then
  { has CURRENT_DECISIONS.md || has DECISIONS.md; } && pass "decisions file exists" || warn "CURRENT_DECISIONS.md recommended (decisions capability mounted)"
fi
if hascap dependencies; then
  has DEPENDENCY_MAP.md && pass "DEPENDENCY_MAP.md exists" || warn "DEPENDENCY_MAP.md recommended (dependencies capability mounted)"
fi
if hascap routing; then
  if has AGENT_DEFINITION_MAP.md; then
    pass "AGENT_DEFINITION_MAP.md exists"
    refs AGENT_DEFINITION_MAP.md 'AGENT_' \
      && pass "AGENT_DEFINITION_MAP.md contains AGENT_ routing" \
      || fail "AGENT_DEFINITION_MAP.md missing AGENT_ route ids"
  else
    fail "AGENT_DEFINITION_MAP.md missing (routing capability mounted)"
  fi
fi
if hascap generation; then
  [ -d skeleton ] && pass "skeleton/ exists" || fail "skeleton/ missing (generation capability mounted)"
  has workflows/generate_custom_doc.md && pass "workflows/generate_custom_doc.md exists" || fail "workflows/generate_custom_doc.md missing (generation capability mounted)"
fi

# Dependency-linked gate hygiene.
# This is intentionally lightweight. Project-specific mode names stay in the child DEPENDENCY_MAP.
if has DEPENDENCY_MAP.md; then
  refs DEPENDENCY_MAP.md 'completion gate|gate|dependency chain|output mode|route.*workflow.*template' \
    && pass "DEPENDENCY_MAP carries dependency/gate language" \
    || warn "DEPENDENCY_MAP has no visible dependency-linked gate language"
  refs DEPENDENCY_MAP.md 'separate active.*gate|second active.*source|DEPENDENCY_MAP.*gate|completion gate source' \
    && pass "DEPENDENCY_MAP protects against split gate authority" \
    || warn "DEPENDENCY_MAP should state that completion gates belong with dependency chains"
fi

# Avoid a common drift pattern: a separate daily gate file becoming a second active authority.
if has workflows/daily_execution_gate.md; then
  warn "workflows/daily_execution_gate.md exists; verify it is checker/projection only and not a second active gate source"
fi

# Process-evidence gate (the single controllable entry = git commit):
# if this run is a pre-commit (staged changes exist) and canonical memory files are
# staged, the SAME commit must stage a new execution-check report — process steps are
# recorded evidence, not optional prose. Escape hatch: SKIP_PROCESS_GATE=1 (logged choice).
if [ "${SKIP_PROCESS_GATE:-}" != "1" ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  STAGED=$(git diff --cached --name-only 2>/dev/null)
  if [ -n "$STAGED" ]; then
    if printf '%s\n' "$STAGED" | grep -qE '^(CURRENT_STATE\.md|CURRENT_DECISIONS\.md|DECISIONS\.md)$'; then
      if printf '%s\n' "$STAGED" | grep -qE '^reports/(execution_checks|backtests)/'; then
        pass "process evidence: memory change ships with an execution-check/backtest record"
      else
        fail "process evidence missing: CURRENT_STATE/DECISIONS staged without a new reports/execution_checks/ record (SKIP_PROCESS_GATE=1 to bypass, bypass is a recorded choice)"
      fi
    fi
  fi
fi

# 連動同步提醒＋文件路徑現實檢查（advisory）。檢查器由母腦複製到 tools/brain/。
if command -v node >/dev/null 2>&1; then
  if [ -f tools/brain/check-sync-matrix.js ]; then
    node tools/brain/check-sync-matrix.js "$SESSION_ROOT" || warn "sync-matrix 有應檢視而未動的檔案（advisory，見上）"
  fi
  if [ -f tools/brain/check-doc-paths.js ]; then
    node tools/brain/check-doc-paths.js "$SESSION_ROOT" || warn "doc-paths：文件宣稱的路徑與檔案樹不一致（advisory，見上）"
  fi
fi

# Mount default: .gitignore should ignore Obsidian's viewer-layer settings (.obsidian/).
# Advisory (warn, not fail): scaffold emits this; a hand-made mount may have forgotten it.
if [ -f .gitignore ] && grep -qE '^\.obsidian/?$' .gitignore; then
  pass "gitignore ignores .obsidian/ (viewer layer won't pollute repo)"
else
  warn ".gitignore missing or does not ignore .obsidian/ (Obsidian settings may pollute the repo; scaffold adds this by default)"
fi

# Avoid thin-mount bloat: future capability placeholders should not be copied into child repos.
for f in docs/rag_policy.md docs/knowledge_graph.md docs/mcp_gateway.md docs/interface_gateway_layer.md; do
  if has "$f"; then
    warn "$f exists; verify it has real content and is not an empty future placeholder"
  fi
done

echo "Result: FAIL=$FAIL WARN=$WARN"
if [ "$FAIL" -gt 0 ]; then echo "partial change required"; exit 1; fi
echo "complete"; exit 0
