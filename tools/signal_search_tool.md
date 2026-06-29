# signal_search_tool

## name

```text
signal_search_tool
```

## purpose

Find candidate signals for the daily market radar across configured radar buckets.

## input

```text
SYSTEM_PROMPT.md
configs/
memory/watchlist.md
memory/missed_cases.md
recent reports
user priority topics
current date
```

## operation

```text
1. Load radar configs and watchlists.
2. Search recent signals across required buckets.
3. Prefer primary / official / high-quality sources when available.
4. Record source, date, topic, and why the signal matters.
5. Mark gaps when no high-quality signal is found.
```

## output

```text
candidate_signal_list
source_list
bucket_coverage_notes
search_gap_notes
```

## required_evidence

```text
source URL or source citation
publish / event date when available
bucket tag
reason for inclusion
```

## failure_condition

```text
No sources searched.
Only one bucket searched.
Candidate signals have no source or date.
Search gaps are hidden instead of marked.
```
