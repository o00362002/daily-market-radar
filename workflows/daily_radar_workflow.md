# Daily Radar Workflow

Purpose: define the minimum daily execution path.

This workflow is owned by `radar_report_agent` in `AGENT_DEFINITION_MAP.md`.

---

## name

```text
daily_radar_workflow
```

## trigger

```text
daily report request
scheduled daily radar run
manual market radar generation
```

---

## ordered_steps

```text
1. Entry read
   - SYSTEM_PROMPT.md
   - PROJECT_MAP.md
   - HIGH_LEVEL_INDEX.md
   - CURRENT_STATE.md
   - CURRENT_DECISIONS.md
   - README.md
   - DEPENDENCY_MAP.md

2. Load radar context
   - configs/
   - memory/watchlist.md
   - memory/missed_cases.md
   - recent reports
   - active templates

3. Run signal_search_tool
   - find candidate signals
   - record source, date, bucket, and inclusion reason
   - mark gaps honestly

4. Run claim_risk_checker
   - check factual claims, numbers, dates, source quality, and AI inference
   - remove or soften unsupported claims

5. Run coverage_checker
   - check required buckets, watchlist items, missed-case items, and duplicates
   - mark missing buckets and retry needs

6. Run report_formatter
   - use active template
   - include sources, dates, coverage notes, gaps, and retry status
   - produce `reports/YYYY/YYYY-MM-DD.md`

7. Run missed_case_backtest_loop when needed
   - if missed case, repeated gap, or rule adjustment evidence exists
   - save evidence to `reports/backtests/`

8. Completion check
   - plan vs actual
   - sync status
   - backtest / adjustment needed? yes / no
   - status
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

The report can be marked `complete` only when:

```text
signal_search_tool complete
claim_risk_checker complete
coverage_checker complete
report_formatter complete
backtest / adjustment need checked
sync impact checked
```

If any required tool or check is skipped, mark:

```text
partial change
```
