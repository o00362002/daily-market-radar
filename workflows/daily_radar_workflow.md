# Daily Radar Workflow

Purpose: define the full formal daily market radar execution path.

Owner: `AGENT_RADAR_REPORT` in `AGENT_DEFINITION_MAP.md`.

General daily news requests should use `workflows/daily_push_brief_workflow.md` unless the user explicitly asks for a full, formal, or archive report.

---

## name

```text
daily_radar_workflow
```

## trigger

```text
explicit full daily radar report request
scheduled full daily radar run
manual full market radar generation
formal archive report request
5+3 hard-gate report request
48-signal report request
archive output request
```

## non_trigger

```text
每日播報
每日新聞
今天的每日新聞
播報今天的每日新聞
今日市場雷達
今天市場雷達
今天新聞
每日推播
morning brief
daily news
daily push
quick daily market brief
```

Non-trigger phrases route to `AGENT_DAILY_PUSH_BRIEF` unless the user explicitly asks for formal, complete, or archival output.

---

## ordered_steps

```text
1. Entry read
2. Load full radar context
3. Search candidate signals with retry
4. Check source, date, and claim risk
5. Check coverage and duplicates
6. Format with the full daily report template
7. Run missed-case backtest loop when needed
8. Complete final status check
```

---

## required_tools

```text
signal_search_tool
claim_risk_checker
coverage_checker
report_formatter
```

---

## required_checks

```text
source / date check
search retry check before gap
claim risk check
coverage check
gap note check
cross-day duplicate check
missed-case backtest check
```

---

## output_path

```text
reports/YYYY/YYYY-MM-DD.md
reports/backtests/ when needed
```

---

## completion_rule

The report can be marked `complete` only when the required tools and checks are complete.

If any required tool or check is skipped, mark:

```text
partial full report
```

---

## practical interpretation

This workflow is for formal research and archive output. The default daily user-facing output is the push brief workflow.
