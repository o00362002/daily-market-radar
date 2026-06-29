# coverage_check_skill

## purpose

Judge whether the daily radar covers required buckets and known watch items.

## input

```text
candidate_signal_list
approved_claims
configs/
memory/watchlist.md
memory/missed_cases.md
```

## procedure

```text
1. Map candidate signals to required buckets.
2. Check priority buckets and missed-case watch items.
3. Mark missing buckets as explicit gaps.
4. Remove duplicate or low-value signals.
5. Hand off coverage-approved material to report_formatting_skill.
```

## output

```text
coverage_table
missing_bucket_notes
retry_needed_notes
```

## quality_gate

A required bucket may be empty, but it cannot be silently omitted.
