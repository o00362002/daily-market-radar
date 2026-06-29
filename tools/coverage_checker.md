# coverage_checker

## name

```text
coverage_checker
```

## purpose

Check whether the daily radar covers the required topic buckets and marks gaps honestly.

## input

```text
candidate_signal_list
report draft
configs/
memory/watchlist.md
memory/missed_cases.md
```

## operation

```text
1. Compare candidate signals against required buckets.
2. Check whether high-priority buckets are covered.
3. Check whether missed-case watch items were searched.
4. Mark missing buckets as gap notes instead of silently omitting them.
5. Identify duplicated or low-value signals.
```

## output

```text
coverage_table
missing_bucket_notes
duplicate_signal_notes
retry_needed_notes
```

## required_evidence

```text
bucket name
covered? yes / no
source count
gap reason
retry needed? yes / no
```

## failure_condition

```text
Required buckets are missing without gap notes.
Known missed cases are not checked.
Report claims broad coverage without evidence.
```
