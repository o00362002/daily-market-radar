# report_formatter

## name

```text
report_formatter
```

## purpose

Turn checked signals into the final daily radar report format.

## input

```text
approved_signal_list
claim_risk_table
coverage_table
templates/
recent reports
```

## operation

```text
1. Load the active report template.
2. Use only signals that passed claim risk and coverage checks.
3. Include source / date / gap notes where required.
4. Preserve required sections and user priority topics.
5. Add retry status, missed-case notes, and next watch items.
```

## output

```text
reports/YYYY/YYYY-MM-DD.md
```

## required_evidence

```text
template used
claim risk check completed? yes / no
coverage check completed? yes / no
backtest / adjustment needed? yes / no
```

## failure_condition

```text
Report is formatted before claim risk check.
Report is formatted before coverage check.
Required report sections are missing.
Sources, dates, or gap notes are removed during formatting.
```
