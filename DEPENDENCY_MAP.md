# Daily Market Radar｜DEPENDENCY_MAP

Thin-mount dependency map for the Daily Market Radar repo.

This file is not a copy of the mother Brain.

---

## 1. Source of truth

```text
Current mount: brain.manifest.yaml
Execution entry: AGENTS.md
Current state: CURRENT_STATE.md
Current decisions: CURRENT_DECISIONS.md
```

---

## 2. Core dependencies

| Area | Files |
|---|---|
| Entry | README.md, SYSTEM_PROMPT.md, PROJECT_MAP.md, HIGH_LEVEL_INDEX.md, CURRENT_STATE.md, CURRENT_DECISIONS.md, AGENTS.md, brain.manifest.yaml |
| Radar rules | configs/ |
| Memory | memory/ |
| Output | templates/, reports/ |
| Workflow | workflows/daily_radar_workflow.md |
| Backtest | reports/backtests/, evals/cold_read_eval.md |
| Mount check | check_mount_integrity.sh |

---

## 3. Frozen dependencies

These files are frozen history and should not drive active routing:

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
```

---

## 4. Sync rule

When radar scope, report format, retry rules, missed-case handling, template, report, or workflow changes, check:

```text
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENTS.md
brain.manifest.yaml
check_mount_integrity.sh
```

---

## 5. Level

```text
Level 2：Runtime-Lite Brain
```
