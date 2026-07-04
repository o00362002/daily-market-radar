# SOURCE_LIBRARY_SPEC

本檔定義 `daily-market-radar` 的來源庫優先搜尋方法。

這不是把關鍵字搜尋刪掉，而是把搜尋順序從「keyword-first」改成「source-first」。

```text
Source Library first
→ Topic / keyword query second
→ External discovery third
→ Coverage audit before output
```

---

## 1. Decision summary

每日市場雷達與指定主題新聞搜尋，不應只依賴即時關鍵字搜尋。

原因：

```text
1. 關鍵字搜尋容易被熱門重複新聞、SEO 內容、低品質轉載與搜尋排序污染。
2. 固定來源庫可以提高速度、穩定性、可追溯性與回測能力。
3. 關鍵字仍然必要，但應用於來源庫內搜尋、事件補查、漏抓 retry、新來源發現。
4. 每日報告要能回答：已檢查哪些來源、哪些命中、哪些沒有命中。
5. 來源名稱不等於已檢查所有發布渠道；social-first / channel-first 來源必須做 channel-aware check。
```

---

## 2. Source-first model

### 2.1 Primary flow

```text
1. Read task route and topic scope.
2. Load `configs/source_routing_rules.yml`.
3. Load relevant files under `sources/`.
4. Fetch priority sources by domain and region.
5. Resolve each source's publishing channels and channel priority.
6. Direct-check required channels for social-first / channel-first sources.
7. Search / filter inside collected source items.
8. Use keyword search only as fallback, enrichment, or discovery.
9. Cross-check important claims with official / data / trusted media sources.
10. Output coverage audit, including channel gaps when relevant.
```

### 2.2 Role of keyword search

Keyword search remains active, but it is no longer the first move.

Allowed uses:

```text
- Search within collected source results.
- Expand a confirmed event into related coverage.
- Check if Taiwan has direct source-backed news.
- Discover new sources outside the existing source library.
- Retry a domain when fixed sources return insufficient coverage.
```

Not allowed:

```text
- Using a generic web search result list as if it were complete coverage.
- Replacing Taiwan news with generic Taiwan implications.
- Filling source gaps with synthesis only.
- Marking source library coverage as complete when only keywords were searched.
- Treating a generic search for a source name as proof that its Instagram / Facebook / Threads / LINE / YouTube / podcast / newsletter channels were checked.
```

---

## 3. Source file roles

```text
sources/key_media_library.yml
= global and Taiwan key media library by domain.

sources/official_and_data_sources.yml
= official, regulator, company, exchange, macro, market, chain, and research/data sources.

configs/source_routing_rules.yml
= execution rules for source-first routing, fallback, source health, channel-aware checks, and coverage audit.
```

---

## 4. Source record schema

Each source should use this shape when practical:

```yaml
- source_id: cna_tw
  name: 中央社
  region: Taiwan
  languages: [zh-TW]
  source_type: news_agency
  domains: [taiwan, macro, market, retail, policy]
  priority: high
  evidence_default: high
  fetch_method: rss_or_site_search
  feed_url: check_required
  homepage_url: https://www.cna.com.tw/
  usage_policy: check_required
  paywall: false
  freshness_expectation: daily
  health_status: unknown
  notes: 台灣即時與官方性新聞基礎來源
```

### Required fields

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

### Recommended fields

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

### 4.1 Channel-aware metadata

凡來源可能把重要內容優先發布在社群、影音、Podcast、Newsletter、LINE 或其他非網站渠道，應補 channel metadata，而不是只記來源名稱。

```yaml
- source_id: example_social_first_source
  name: Example Source
  publishing_channels:
    - website
    - instagram
    - threads
    - youtube
    - newsletter
  channel_priority:
    - instagram
    - threads
    - website
    - youtube
    - newsletter
    - generic_search_fallback
  social_first: true
  channel_check_required: true
  channel_access_status: unknown
```

通用判斷規則：

```text
任何來源
→ 讀取 publishing_channels
→ 判斷 channel_priority
→ 若 social_first = true 或 channel_check_required = true
→ 強制 direct channel check
→ 無法存取則標示 unchecked / inaccessible / partial
→ generic search 不得冒充 direct channel check
→ 重大 claim 回查官方 / 數據 / 高證據來源
```

此規則適用所有領域，不只 DA 交易者聯盟或台灣加密，包括但不限於：

```text
- 台灣加密媒體、KOL、交易社群、研究帳號
- 品牌官方 Instagram / Facebook / Threads / TikTok / LINE OA
- 百貨、購物中心、商場官方社群
- AI 開發者社群、產品發布帳號、Discord / forum 公開訊號
- 公司高層公開社群帳號
- Podcast / YouTube-first 產業媒體
- Newsletter-first 研究來源
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

Each domain should include:

```text
- global media sources
- Taiwan media sources when relevant
- official / company / regulator sources
- data or indicator sources when available
- social / channel-first sources when relevant
- fallback discovery method
```

---

## 6. Fetch method priority

Preferred order:

```text
1. official API
2. official RSS / Atom
3. official newsroom / release page
4. verified media RSS / section page
5. trusted news database / aggregator
6. required direct channel check for social-first / channel-first sources
7. generic web search
8. unverified social / community candidates
```

Do not scrape aggressively when RSS, API, or section pages are available.

Direct channel checks are discovery mechanisms, not automatic high evidence. A social post can discover a major event, but policy, law, market, financial, or investment claims still require stronger verification.

---

## 7. Coverage audit requirement

Every Daily Push Brief, Full Daily Radar, and News Search Output should include or internally satisfy:

```text
source_library_checked: yes / partial / no
priority_sources_checked: count or list
keyword_fallback_used: yes / no
external_discovery_used: yes / no
taiwan_sources_checked: yes / partial / no
social_channels_checked_when_required: yes / partial / no / not_required
channel_gaps: none / list
source_gap: none / partial / material
```

If the output is user-facing, disclose source gaps when material.

若來源是 social-first / channel-first，但沒有直接檢查其必要渠道，必須明確標示：

```text
Social/channel-first source not checked directly; generic search may miss posts or channel-native content.
```

---

## 8. Source health loop

After repeated use, update source health through local evidence, not memory guesswork.

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
```

Recommended storage:

```text
memory/source_health_log.json
memory/topic_coverage_log.json
reports/backtests/
```

---

## 9. Governance boundary

This source library is a local child-repo execution module.

It does not change the mother Brain architecture unless it introduces cross-repo governance, reusable source-routing policy, or a new universal memory rule.

Projection files may reference this spec, but durable source-of-truth changes must be recorded through `CURRENT_DECISIONS.md` and dependency checks.
