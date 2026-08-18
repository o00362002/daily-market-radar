# 2026-08-18 weekly radar and chat consolidation

Change type: Convert the recurring production radar from daily to weekly and make the owner ChatGPT briefing conversation-only.

Affected files: `daily-intelligence.yml`, the bounded report-window runtime path, unit tests, current state/decision records, and weekly operations documentation.

Human confirmed: yes

Risk level: medium

Mother Brain activated: no — this is a local runtime cadence change under the existing mount and does not alter mount governance.

Rollback note: Revert this commit to restore the daily cron and the existing two-calendar-day report window. The stable workflow name, state branch, quality gates, source registry, Pages boundary, and manual chat-import path remain unchanged.

## Decision

The owner requested a Monday 07:00 Asia/Taipei production run with a real seven-calendar-day data window so the weekly briefing contains meaningful change rather than a daily snapshot delayed by a week. The separate ChatGPT weekly task delivers its synthesis in the conversation; it does not write repository artifacts or trigger a Page deployment.

## Validation

- `python -m pytest -q tests/unit/test_freshness_filter.py tests/unit/test_workflows.py` — 16 passed, using the repository Python 3.12 environment.
- `make validate` with the repository Python 3.12 environment — 324 Python tests plus runtime, source, CLI, document-path and governance checks passed (two pre-existing non-blocking governance warnings).
- `python -m compileall -q src tests` with a task-local Python bytecode cache — passed.
- `git diff --check` — passed.
