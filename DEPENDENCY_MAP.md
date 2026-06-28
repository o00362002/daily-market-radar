# Daily Market Radar｜DEPENDENCY_MAP

Thin-mount dependency map for the Daily Market Radar repo.

This file is not a copy of the mother Brain.

## Core dependencies

| Area | Files |
|---|---|
| Entry | README.md, SYSTEM_PROMPT.md, PROJECT_MAP.md, HIGH_LEVEL_INDEX.md, CURRENT_STATE.md, CURRENT_DECISIONS.md, AGENTS.md, CLAUDE.md |
| Radar rules | configs/ |
| Memory | memory/ |
| Output | templates/, reports/ |
| Workflow | workflows/daily_radar_workflow.md |
| Backtest | reports/backtests/, evals/cold_read_eval.md |

## Sync rule

When radar scope, report format, retry rules, or missed-case handling changes, check the entry files, configs, templates, reports, and this file.

## Level

Level 2：Runtime-Lite Brain.
