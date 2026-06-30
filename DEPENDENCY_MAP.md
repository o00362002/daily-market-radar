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
Agent map and task routing: AGENT_DEFINITION_MAP.md
```

---

## 2. Core dependencies

| Area | Files |
|---|---|
| Entry | README.md, SYSTEM_PROMPT.md, PROJECT_MAP.md, HIGH_LEVEL_INDEX.md, CURRENT_STATE.md, CURRENT_DECISIONS.md, AGENTS.md, AGENT_DEFINITION_MAP.md, brain.manifest.yaml |
| Radar rules | configs/ |
| Memory | memory/ |
| Output | templates/, reports/, content/ |
| Full workflow | workflows/daily_radar_workflow.md |
| Concise push workflow | workflows/daily_push_brief_workflow.md |
| News search workflow | workflows/news_search_content_workflow.md |
| Content workflow | workflows/news_content_workflow.md |
| Backtest | reports/backtests/, evals/cold_read_eval.md |
| Mount check | check_mount_integrity.sh |

---

## 3. Active output modes

```text
Full Daily Radar → templates/daily_report_template.md
Daily Push Brief → templates/daily_push_brief_template.md
News Search Output → templates/news_search_content_template.md
News Content Output → templates/news_content_template.md
```

---

## 4. Routing

```text
Task routing lives inside AGENT_DEFINITION_MAP.md.
No standalone ROUTING.md is active.
```

---

## 5. Frozen dependencies

These files are frozen history and should not drive active routing:

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
```

---

## 6. Sync rule

When radar scope, report format, retry rules, missed-case handling, template, report, workflow, or agent map changes, check:

```text
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENTS.md
AGENT_DEFINITION_MAP.md
brain.manifest.yaml
check_mount_integrity.sh
```

---

## 7. Level

```text
Level 2：Runtime-Lite Brain
```