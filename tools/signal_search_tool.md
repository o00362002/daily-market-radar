# signal_search_tool

## name

```text
signal_search_tool
```

## purpose

Find candidate signals for the daily market radar across configured radar buckets.

This tool should not stop at the first failed search.

When useful signals are not found, it must switch search method before marking a gap.

---

## maintenance principle

Keep this tool easy to maintain:

```text
signal_search_tool = find candidate signals and record search trace
configs/search_retry_protocol.yml = retry method details
coverage_checker = check whether required domains are covered
claim_risk_checker = tag / downgrade / rewrite claim risk
```

Do not copy all retry examples into this file. Use `configs/search_retry_protocol.yml` as the detailed source.

---

## input

```text
AGENTS.md
SYSTEM_PROMPT.md
configs/
memory/watchlist.md
memory/missed_cases.md
recent reports
user priority topics
current date
```

---

## operation

```text
1. Load radar configs, watchlists, missed cases, and recent reports.
2. Search recent signals across required buckets.
3. Prefer primary / official / high-quality sources when available.
4. Record source, date, topic, source type, and why the signal matters.
5. If no useful signal is found, run retry using configs/search_retry_protocol.yml before marking a gap.
6. Keep ordinary news as a candidate source when labelled correctly.
7. Mark gaps only after retry is attempted or explicitly impossible.
```

---

## retry rule

Finding nothing is not the end of the search.

If a bucket, radar, or required signal type is missing, switch method before declaring a gap.

Minimum retry directions:

```text
change_keywords
change_language
change_source_type
change_level
change_time_window
search_negative_space
search_metrics_instead_of_news
check_history_reports
```

Use `configs/search_retry_protocol.yml` for detailed examples and minimum retry requirements.

---

## source flexibility rule

The tool should not search only official or elite sources.

For radar discovery, acceptable inputs include:

```text
official sources
authoritative media
industry media
local media
company blogs
research labs
startup posts
GitHub / developer sources
Product Hunt / Hacker News style sources
social discussion
Reddit / X / Threads / forum weak signals
metrics dashboards
```

Low-evidence sources should be passed forward with labels, not silently discarded.

`claim_risk_checker` will decide whether the final wording should be fact, inference, candidate signal, weak signal, or removed high-risk claim.

---

## output

```text
candidate_signal_list
source_list
bucket_coverage_notes
search_gap_notes
retry_trace
history_dedup_notes
```

---

## required_evidence

```text
source URL or source citation
publish / event date when available
bucket tag
source type
reason for inclusion
retry method used when initial search failed
history status: new / duplicate / updated / not checked
```

---

## gap rule

A gap can be marked only when at least one of the following is true:

```text
Required retry methods were attempted and still no useful signal was found.
The source environment is unavailable or inaccessible.
The result is duplicate with recent reports and has no new update.
The available result is too low-quality even for candidate use, and this is documented.
```

Do not write `no data` only because the first keyword or first source type failed.

---

## failure_condition

```text
No sources searched.
Only one bucket searched.
Candidate signals have no source or date when available.
Search gaps are hidden instead of marked.
A gap is marked before retry or method switching.
Only official / mainstream sources are checked when the task needs edge signals.
Retry trace is omitted when minimum coverage is not met.
```
