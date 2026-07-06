# FreshRSS Ingestion Workflow

Purpose: connect FreshRSS to `daily-market-radar` as an automated candidate source pool. The user should not manually read FreshRSS every day.

Owner:

```text
AGENT_DAILY_PUSH_BRIEF
AGENT_RADAR_REPORT
AGENT_NEWS_SEARCH
```

Required files:

```text
configs/freshrss_ingestion.yml
sources/channel_feed_sources.json
FRESHRSS_SEEDS.opml
templates/feed_item_candidate_schema.md
memory/feed_ingestion_log.json
tools/freshrss/greader_pull_candidates.py
```

---

## Execution position

FreshRSS ingestion runs after fixed source library loading and before keyword fallback.

```text
source library + official/data sources
→ FreshRSS Google Reader API pull
→ FreshRSS feed inbox candidates
→ query recipes and targeted keyword retry
→ external discovery providers when gaps remain
→ potential pool capture
→ output-stage selection
```

FreshRSS is a source-first acceleration layer, not a replacement for source verification.

---

## Trigger

Run this workflow when any of these apply:

```text
daily push brief
full daily radar
news search output
manual request to use FreshRSS feeds
feed stack check
source health check
```

---

## API pull step

When FreshRSS API credentials are available locally, run:

```bash
python3 tools/freshrss/greader_pull_candidates.py
```

The tool reads these environment variables only:

```text
FRESHRSS_BASE_URL
FRESHRSS_DEFAULT_USER
FRESHRSS_API_PASSWORD
```

It writes:

```text
data/freshrss/feed_candidates_latest.json
```

Do not commit API passwords or local feed candidate output unless explicitly needed for a test fixture.

---

## Minimum ingestion loop

```text
1. Load configs/freshrss_ingestion.yml.
2. Load sources/channel_feed_sources.json.
3. Load FRESHRSS_SEEDS.opml or FreshRSS feed list.
4. Pull new FreshRSS items through the Google Reader compatible API when available.
5. Normalize each item using templates/feed_item_candidate_schema.md.
6. Map source_id to domain_ids and feed_category.
7. Dedupe by canonical URL, then title + source_id + published date.
8. Reject stale, duplicate, infrastructure-only, or irrelevant items.
9. Keep accepted items as candidate signals.
10. Pass candidates into Daily Push Brief or Full Daily Radar selection.
11. Record ingestion counts and failures in memory/feed_ingestion_log.json or the post-brief review.
```

---

## Candidate status

```text
new = fresh candidate not yet used
used = selected into output with news ID
duplicate = already covered in prior reports or same run
stale = outside lookback window
rejected = not relevant or not source-backed enough
failed_source = feed or route failed
```

---

## Output integration rule

A FreshRSS item may appear in the final brief only if:

```text
1. source_id is known in sources/channel_feed_sources.json.
2. original_url or canonical URL is present.
3. today_new_information is identified.
4. historical duplication status is checked.
5. evidence trace is preserved.
6. high-risk claims are checked against original source, official source, data source, or trusted media.
```

Infrastructure-only items, such as RSSHub release updates, may be used for feed-stack health notes but must not count as market news.

---

## Audit output

Daily Push Brief should include or internally satisfy:

```text
freshrss_checked: yes / partial / no
freshrss_fetch_window_hours: 24 / 48 / 72
freshrss_feed_hits: number
freshrss_feed_misses: number
freshrss_failed_feeds: list
freshrss_candidates_created: number
freshrss_candidates_used_in_output: number
freshrss_candidates_rejected: number
remaining_feed_gap: text
```

---

## Failure handling

```text
If FreshRSS is unavailable:
  mark freshrss_checked = no
  disclose fallback to source library + query recipes

If a feed fails:
  keep source_id visible
  mark failed_source
  do not silently replace it with generic search

If FreshRSS returns no new items:
  mark zero new feed candidates
  continue source library and query recipe checks
```
