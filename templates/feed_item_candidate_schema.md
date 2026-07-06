# Feed Item Candidate Schema

Purpose: normalize FreshRSS / RSSHub / direct RSS items into daily-market-radar candidate signals before Daily Push Brief or Full Daily Radar selection.

FreshRSS items are **candidate evidence**, not final conclusions.

---

## Candidate object

```yaml
candidate_id: "feed::<source_id>::<published_date>::<slug_or_hash>"
source_id: "openai_news_rss"
source_name: "OpenAI News RSS"
feed_category: "AI_OFFICIAL"
domain_ids:
  - ai_agents_workflow
  - technology_development
region: "global"
languages:
  - en

title: ""
url: ""
original_url: ""
published_at: ""
fetched_at: ""
summary: ""

evidence_default: "high_when_official"
evidence_status: "candidate"
ingestion_status: "new | duplicate | stale | rejected | used"

today_new_information: "unknown_until_checked"
historical_duplication_status: "unknown_until_checked"
source_library_match: true
keyword_fallback_used: false

claim_check_required: true
original_source_check_done: false
used_in_output: false
output_news_id: null

notes: ""
```

---

## Required transformations

```text
1. Preserve title, URL, source, published time, and fetched time.
2. Map source_id to domain_ids through sources/channel_feed_sources.json.
3. Mark FreshRSS item as candidate until original source and today_new_information are checked.
4. Dedupe by canonical URL first, then title + source_id + published date.
5. If used in output, assign output_news_id and keep evidence trace.
6. If rejected, keep reason in ingestion log or post-brief review.
```

---

## Evidence boundary

```text
Official direct RSS can start with high_when_official evidence_default.
RSSHub public channel items start lower unless official identity and original post are verified.
FreshRSS itself is never the final source; it is the collection layer.
```

---

## Rejection reasons

```text
stale_item
no_today_new_information
duplicate_of_existing_report
source_not_allowed
feed_summary_without_original_source
infrastructure_only
not_relevant_to_six_domains
needs_manual_verification
```
