# Skill Spec｜read_context

## Purpose

讀取每日市場情報執行前必須載入的 repo 脈絡，並輸出讀取狀態。

---

## Inputs

```text
repository: o00362002/daily-market-radar
current_date: YYYY-MM-DD
```

---

## Required Files

```text
SYSTEM_PROMPT.md
README.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
ADOPTION_LEVELS.md
CONTEXT_ROUTING.md
RUNBOOK.md
CHECKLIST.md
configs/radars.yml
configs/triggers.yml
configs/evidence.yml
configs/source_strategy.md
configs/indicator_tracking.yml
configs/technology_development.yml
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
memory/missed_cases.md
memory/watchlist.md
templates/daily_report_template.md
templates/final_synthesis_template.md
workflows/daily_report_runbook.md
loops/daily_report_quality_loop.yml
```

---

## Output

```text
loaded_files:
missing_files:
failed_files:
fallback_used:
execution_status: complete | partial
```

---

## Rules

- 不得假裝已讀取不存在或讀取失敗的檔案。
- 若部分檔案缺漏，仍可產出 partial，但必須列出影響。
- 若缺漏 RUNBOOK / CHECKLIST / edge_case_discovery / search_retry_protocol，不能產出完整報告。