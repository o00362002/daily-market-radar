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
Execution gate: workflows/daily_execution_gate.md
```

---

## 2. Core dependencies

| Area | Files |
|---|---|
| Entry | README.md, SYSTEM_PROMPT.md, PROJECT_MAP.md, HIGH_LEVEL_INDEX.md, CURRENT_STATE.md, CURRENT_DECISIONS.md, AGENTS.md, AGENT_DEFINITION_MAP.md, brain.manifest.yaml |
| Radar rules | configs/ |
| Memory | memory/ |
| Output | templates/, reports/, content/ |
| Execution gate | workflows/daily_execution_gate.md |
| Full workflow | workflows/daily_radar_workflow.md |
| Concise push workflow | workflows/daily_push_brief_workflow.md |
| News search workflow | workflows/news_search_content_workflow.md |
| Content workflow | workflows/news_content_workflow.md |
| Backtest | reports/backtests/, evals/cold_read_eval.md |
| Mount check | check_mount_integrity.sh |

---

## 3. Active output modes

```text
Full Daily Radar → AGENT_RADAR_REPORT → workflows/daily_radar_workflow.md → templates/daily_report_template.md → Full Daily Radar Gate
Daily Push Brief → AGENT_DAILY_PUSH_BRIEF → workflows/daily_push_brief_workflow.md → templates/daily_push_brief_template.md → Daily Push Brief Gate
News Search Output → AGENT_NEWS_SEARCH → workflows/news_search_content_workflow.md → templates/news_search_content_template.md
News Content Output → AGENT_NEWS_CONTENT → workflows/news_content_workflow.md → templates/news_content_template.md
```

Execution gates live in:

```text
workflows/daily_execution_gate.md
```

The gate must recognize every active output mode above.

---

## 4. Routing

```text
Task routing lives inside AGENT_DEFINITION_MAP.md.
No standalone ROUTING.md is active.
```

Execution route, workflow, template, and gate must form one consistent dependency chain.

If they disagree, mark the output:

```text
依賴鏈不一致：partial / blocked
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

When radar scope, report format, retry rules, missed-case handling, template, report, workflow, agent map, active output mode, or execution gate changes, check:

```text
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENTS.md
AGENT_DEFINITION_MAP.md
workflows/daily_execution_gate.md
templates/
brain.manifest.yaml
check_mount_integrity.sh
```

Required sync chain:

```text
AGENT_DEFINITION_MAP.md
→ DEPENDENCY_MAP.md
→ workflows/
→ templates/
→ workflows/daily_execution_gate.md
→ check_mount_integrity.sh
```

No workflow or template change is considered complete unless the execution gate recognizes the same output mode.

No execution gate change is considered complete unless the dependency map and mount integrity check can detect the same output-mode chain.

---

## 7. Level

```text
Level 2：Runtime-Lite Brain
```
