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

## maintenance principle

Keep this workflow as the process skeleton.

Detailed rules should stay in:

```text
AGENTS.md = agent entry
SYSTEM_PROMPT.md = thin quality policy
configs/ = radar parameters, retry, source and evidence rules
tools/ = tool behavior
skill_specs/ = reusable judgement capabilities
templates/ = output shape
memory/ = watchlist and missed cases
reports/ = history and evidence
```

Do not turn this workflow into another long prompt.

---

## ordered_steps

```text
1. Entry read
   - AGENTS.md
   - SYSTEM_PROMPT.md
   - PROJECT_MAP.md
   - HIGH_LEVEL_INDEX.md
   - CURRENT_STATE.md
   - CURRENT_DECISIONS.md
   - README.md
   - DEPENDENCY_MAP.md
   - brain.manifest.yaml

2. Load radar context
   - configs/
   - memory/watchlist.md
   - memory/missed_cases.md
   - recent reports
   - active templates

3. Run signal_search_tool
   - find candidate signals
   - record source, date, bucket, source type, and inclusion reason
   - if no useful signal is found, switch method using configs/search_retry_protocol.yml
   - mark gaps only after retry or documented access limitation

4. Run claim_risk_checker
   - check factual claims, numbers, dates, source quality, and AI inference
   - treat news as an information source, not a professional audit report
   - tag / downgrade / soften / rewrite first
   - remove only high-risk unsupported claims that would mislead if kept

5. Run coverage_checker
   - check required buckets, watchlist items, missed-case items, and duplicates
   - mark missing buckets and retry needs

6. Run report_formatter
   - use active template
   - include sources, dates, coverage notes, retry trace, gaps, and claim risk labels
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
search retry check before gap
claim risk label / rewrite check
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

---

## practical interpretation

A daily radar report is allowed to include low-evidence or single-source items as candidate signals when clearly labelled.

The workflow should block only misleading certainty, hidden gaps, missing retry, or high-risk unsupported claims.

Do not downgrade the whole report just because some signals are ordinary news rather than official data.
