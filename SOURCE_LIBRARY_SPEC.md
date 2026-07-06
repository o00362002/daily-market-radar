# SOURCE_LIBRARY_SPEC

本檔定義 `daily-market-radar` 的來源庫優先搜尋方法。

Active order:

```text
Source Library first
→ Query recipes second
→ Verified feed stack third when relevant
→ External discovery fourth when gaps remain
→ Coverage audit before output
```

---

## 1. Decision summary

每日市場雷達與指定主題新聞搜尋，不應只依賴即時關鍵字搜尋。

```text
1. 固定來源庫提高速度、穩定性、可追溯性與回測能力。
2. 固定 query recipes 讓弱模型照抄執行，不依賴模型自行發明查詢。
3. Feed stack 讓公開 channel-first 來源變成可重複檢查的 feed inbox。
4. External discovery providers 只負責發現缺口，不取代原始來源驗證。
5. 每日報告要能回答：已檢查哪些來源、feeds、routes、providers，以及剩下哪些缺口。
```

---

## 2. Primary flow

```text
1. Read task route and topic scope.
2. Load configs/source_routing_rules.yml.
3. Load configs/query_recipes.yml and relevant domain-pack query_recipes.
4. Load SOURCE_LIBRARY_SPEC.md and relevant sources/ files.
5. Fetch priority sources by domain and region.
6. If feed stack is relevant, load configs/feed_discovery_stack.yml and sources/channel_feed_sources.json.
7. Check verified RSSHub routes, direct RSS feeds, and FreshRSS categories when available.
8. Search/filter inside collected source and feed items.
9. Use keyword search only as fallback, enrichment, or discovery.
10. Use GDELT / Media Cloud only when source-library and feed-stack coverage still leave a material gap.
11. Cross-check important claims with official / data / trusted media sources.
12. Output source/feed/discovery coverage audit.
```

Keyword search remains active, but it is not the first move.

Allowed:

```text
- Search within collected source results.
- Search within collected feed results.
- Expand a confirmed event into related coverage.
- Check if Taiwan has direct source-backed news.
- Discover new sources outside the current source library.
- Retry a domain when fixed sources return insufficient coverage.
```

Not allowed:

```text
- Using generic search as complete coverage.
- Replacing Taiwan news with generic Taiwan implications.
- Filling source gaps with synthesis only.
- Marking source coverage complete when only keywords were searched.
- Treating an unverified RSSHub route template as a checked feed.
```

---

## 3. Active source and feed files

```text
sources/key_media_library.yml
= global and Taiwan key media library by domain.

sources/official_and_data_sources.yml
= official, regulator, company, exchange, macro, market, chain, and research/data sources.

configs/source_routing_rules.yml
= execution rules for source-first routing, fallback, source health, and coverage audit.

configs/feed_discovery_stack.yml
= RSSHub + FreshRSS + GDELT + Media Cloud execution boundary and audit fields.

sources/channel_feed_sources.json
= direct RSS and RSSHub route registry. Only verified + enabled entries count as checked feeds.

sources/discovery_providers.yml
= GDELT and Media Cloud provider registry. Discovery only, not final evidence.

FRESHRSS_SEEDS.opml
= seed OPML file for verified starter feeds.
```

---

## 4. Source record schema

Required fields:

```text
source_id
name
region
languages
source_type
domains
priority
evidence_default
fetch_method
usage_policy
freshness_expectation
```

Recommended fields:

```text
feed_url
homepage_url
api_url
paywall
health_status
last_success_at
fail_count
bias_note
notes
publishing_channels
channel_priority
social_first
channel_check_required
channel_access_status
```

Feed/channel rule:

```text
source metadata
→ publishing_channels
→ channel_priority
→ if social_first = true or channel_check_required = true
→ check verified RSSHub route / direct RSS / FreshRSS category when configured
→ mark unchecked / inaccessible / partial when no usable feed route exists
→ generic search must not be treated as direct channel check
→ major claims still require official / data / trusted source verification
```

---

## 5. Domain coverage buckets

The active source library should support at least these six domains:

```text
1. AI models / agents / workflow replacement
2. Crypto / RWA / agent payments
3. Retail / consumer / social / fashion
4. Global markets / capital flows / geopolitics
5. Technology development / robotics / biotech / energy / semiconductor
6. Labor / consumption pressure / Taiwan local signals
```

### 5.1 Domain extension

```text
Scan domain list = six core domains + domains/ packs.
New domain = copy domains/_template/ and fill domain_pack.json + sources.json.
Completeness is checked by tools/brain/check-domain-packs.js.
Domain-pack query_recipes follow the same rule as configs/query_recipes.yml.
```

### 5.2 Feed stack extension

```text
RSSHub = public channel-to-feed adapter.
FreshRSS = self-hosted feed inbox / aggregator.
GDELT = global multilingual discovery provider.
Media Cloud = media ecosystem / source discovery provider.
```

Rules:

```text
1. RSSHub route must be verified in sources/channel_feed_sources.json before it counts as checked.
2. Direct RSS feeds can be enabled for OPML only after feed URL and usage policy are verified.
3. FreshRSS inbox items are collection traces, not final factual proof.
4. GDELT / Media Cloud discoveries must be traced back to original sources before factual use.
5. New concepts, applications, combinations, or trend seeds found through feeds/discovery go into memory/potential_pool.md before output filtering.
```

---

## 6. Fetch method priority

Preferred order:

```text
1. official API
2. official RSS / Atom
3. official newsroom / release page
4. verified media RSS / section page
5. verified RSSHub route or FreshRSS collected feed
6. trusted news database / aggregator
7. required direct channel check for channel-first sources
8. GDELT / Media Cloud discovery when material gaps remain
9. generic web search
10. unverified community candidates
```

Collection routes are discovery mechanisms, not automatic high evidence.

---

## 7. Coverage audit requirement

Every Daily Push Brief, Full Daily Radar, and News Search Output should include or internally satisfy:

```text
source_library_checked: yes / partial / no
priority_sources_checked: count or list
keyword_fallback_used: yes / no
feed_stack_loaded: yes / partial / no
freshrss_checked: yes / partial / no / not_required
rsshub_routes_checked: yes / partial / no / not_required
rsshub_route_gaps: none / list
direct_rss_feeds_checked: yes / partial / no / not_required
external_discovery_used: yes / no
gdelt_used_when_gap: yes / no / not_required
media_cloud_used_when_gap: yes / no / not_required
taiwan_sources_checked: yes / partial / no
social_channels_checked_when_required: yes / partial / no / not_required
potential_pool_capture_done: yes / partial / no
channel_gaps: none / list
source_gap: none / partial / material
```

If the output is user-facing, disclose source/feed/discovery gaps when material.

---

## 8. Source health loop

Track:

```text
last_success_at
last_empty_at
fail_count
duplicate_rate
hit_rate_by_domain
false_positive_notes
usage_policy_notes
channel_access_status
channel_hit_rate
channel_last_success_at
feed_last_success_at
rsshub_route_status
freshrss_category_health
discovery_provider_hit_rate
```

Recommended storage（path-ok；規劃中尚未建立，需要時再建）:

```text
memory/source_health_log.json
memory/topic_coverage_log.json
reports/backtests/
```

---

## 9. Governance boundary

This source library is a local child-repo execution module.

It does not change the mother Brain architecture unless it introduces cross-repo governance, reusable source-routing policy, or a new universal memory rule.

Durable source-of-truth changes must be recorded through `CURRENT_DECISIONS.md` and dependency checks.
