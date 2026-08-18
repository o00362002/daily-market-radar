# 2026-08-19 weekly radar report-date stability

Change type: Keep one captured Taiwan report date across the weekly live run and every production-quality gate.

Affected files: `.github/workflows/daily-intelligence.yml`, its workflow contract test, and this confirmation record.

Human confirmed: yes — the owner authorized completion of the weekly conversion and the resulting GitHub Actions reliability repair.

Risk level: medium

Mother Brain activated: no — this is a local workflow reliability fix; it does not change governance, sources, report schema, quality criteria, or the Pages boundary.

Rollback note: Revert this commit to restore per-step date resolution. The captured date is a scalar workflow output and requires no data migration.

## Root cause

Run `32156217921` started its live report for Taiwan date `2026-08-18`, but long source collection completed after Taipei midnight. The pre-gate recomputed `2026-08-19` and rejected the otherwise successfully exported report with `report_date_mismatch:2026-08-18!=2026-08-19`. The rejection preserved the previous Pages deployment as designed.

## Validation plan

- Workflow contract test proves the date is captured once and reused by all three date consumers.
- Full local validation and YAML parsing run before merge.
- The corrected main-branch production run must pass the report-date gate; no historical report or source data is modified.
