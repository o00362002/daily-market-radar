# report_formatting_skill

## purpose

Turn verified and coverage-checked material into the final daily report format.

## input

```text
approved_claims
coverage_table
templates/
recent reports
```

## procedure

```text
1. Load active report template.
2. Preserve required sections and user priority topics.
3. Include sources, dates, and gap notes.
4. Add retry status and backtest / adjustment note when needed.
5. Hand off to report_formatter.
```

## output

```text
final_report_draft
```

## quality_gate

Formatting must not remove source, date, risk, coverage, or gap notes.
