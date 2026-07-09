# Daily Push Brief Workflow

Purpose: define the default structured concise daily push version for chat / automation output when a full formal report is not explicitly requested.

This workflow does **not** replace the full `daily_radar_workflow.md`.
Concise means shorter wording per item, not reduced reconnaissance structure.

Required shared rules:

```text
configs/daily_execution_quality_gate.yml
configs/structural_trend_indicators.yml
configs/news_freshness_and_taiwan_news.yml
configs/source_routing_rules.yml
configs/niche_candidate_policy.yml
configs/technology_development.yml
configs/feed_discovery_stack.yml
configs/freshrss_ingestion.yml
SOURCE_LIBRARY_SPEC.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
sources/channel_feed_sources.json
templates/feed_item_candidate_schema.md
```

## name

```text
daily_push_brief_workflow
```

## owner

```text
AGENT_DAILY_PUSH_BRIEF
```

## trigger

```text
每日播報
每日新聞
今天的每日新聞
播報今天的每日新聞
每日推播
今日市場雷達
今天市場雷達
今天新聞
先看今天重點
讀 repo 播報今天
不靠記憶讀 repo 播報今天
quick daily market brief
scheduled daily push
manual concise radar request
morning brief
daily news
daily push
concise brief
簡版
輕量版
```

## mode boundary

```text
Daily Push Brief = default structured concise user-facing radar output.
Full Daily Radar = opt-in full research / archive output.
```

Daily Push Brief may be marked `complete` only for concise mode. It must not claim to satisfy the full formal gate unless it actually does.

Brief means shorter wording per item, but preserves all required sections and uses equal major/candidate quota.

## pre-draft execution quality gate

Before drafting content, load `configs/daily_execution_quality_gate.yml` and execute or disclose gaps for:

```text
source audit before drafting
recent reports dedup
primary-domain assignment for each event
major signal rejection gate
niche candidate fresh-anchor gate
candidate retry / external discovery when quota or novelty is low
Taiwan direct-source audit
Retail fixed matrix
Crypto fixed matrix
Structural Trend Indicator Panel
rejection and retry counts
```

If this gate is skipped, mark `partial concise brief` or `failed gate`.

## source-first rule

Daily Push Brief must check the fixed source library and FreshRSS candidate inbox before generic keyword fallback.

Minimum internal flow:

```text
1. Load configs/daily_execution_quality_gate.yml.
2. Load configs/structural_trend_indicators.yml.
3. Load configs/source_routing_rules.yml.
4. Load configs/niche_candidate_policy.yml.
5. Load configs/technology_development.yml.
6. Load sources/key_media_library.yml.
7. Load sources/official_and_data_sources.yml.
8. Load configs/freshrss_ingestion.yml.
9. Load sources/channel_feed_sources.json and FRESHRSS_SEEDS.opml when feed stack is available.
10. For each of six domains, check global media, Taiwan media, official/data sources, and feed candidates.
11. Build major-signal pool and a separate niche-candidate pool.
12. Assign primary_domain for each event; one event can count in only one domain quota.
13. Expand candidate search beyond mainstream wires into research, startup, product, niche industry, developer, social-first, hiring, on-chain, patent and clinical sources.
14. For retail / consumer / social / fashion / trend domain, also check fashion media, style platforms, runway trend reports, brand official channels, merchandising shifts, assortment changes and street-style / social-style signals.
15. For crypto domain, check BTC/ETH/SOL, ETF flows, stablecoin, RWA, Perp DEX, OI/funding, TVL/fees, regulation and Taiwan crypto fixed sources.
16. Normalize candidates and verify original source.
17. Classify each candidate by candidate_type and formation_level.
18. Use query recipes and keyword search to filter, enrich, or retry gaps.
19. Disclose material source and feed gaps.
```

FreshRSS is a candidate pool. It accelerates discovery but does not replace original-source verification.

## minimum output shape

```text
0. Read status and mode
1. Hard gate status: concise mode / full gate not attempted or not passed
2. Six-domain coverage matrix
3. Source-library coverage audit, compact version
4. FreshRSS / feed-stack coverage audit, compact version
5. Rejection / retry counters
6. Each core domain: exactly 3 major signals
7. Each core domain: exactly 3 niche / potential candidates
8. Each core domain: 1–2 Taiwan news items directly under the domain, or valid insufficiency disclosure
9. Retail fixed matrix
10. Crypto fixed matrix
11. Structural Trend Indicator Panel
12. New Information / History Duplicate Check
13. Data gaps and retry notes
14. Final indicator status and news synthesis panel
15. Post-brief review inside the final panel
```

## six core domains

```text
1. AI models / agents / workflow replacement
2. Crypto / RWA / agent payments
3. Retail / consumer / social / fashion / trend
4. Global markets / capital flows / geopolitics
5. Technology development / robotics / biotech / energy / semiconductor
6. Labor / consumption pressure / Taiwan local signals
```

## required per-domain fields

Each domain must include:

```text
major_signals: exactly 3
niche_candidates: exactly 3
Taiwan news: 1–2 items or valid insufficiency disclosure
Evidence trace: required for every item
New information check: required for every item
Historical duplication status: required for every item
primary_domain: required for every counted event
Source-library check status: yes / partial / no
FreshRSS candidate check: yes / partial / no / not_available
Keyword fallback: yes / no
```

Candidate items additionally require:

```text
candidate_type: 新領域 / 新應用 / 新概念 / 新趨勢
formation_level: 弱訊號 / 話題形成 / 趨勢形成 / 主流化中
fresh_concrete_anchor
why_niche_or_early
why_it_could_scale
cannot_conclude
next_verification
```

A candidate must be a source-backed early weak signal, not generic trend commentary. At least one fresh concrete anchor is mandatory: company action, product experiment, paper/data, startup funding, developer adoption, on-chain metric, niche-industry event, social/community signal, pilot, hiring shift, patent, clinical trial, prototype, supply-chain anomaly, fashion/style microtrend, brand merchandising shift or assortment change.

## candidate equality and retry rule

```text
Concise target = 3 major + 3 niche candidates per domain.
Candidate target equals major target.
If 3 candidates are not found, do not fabricate.
Run retry / external discovery first.
If candidates are low novelty, run retry before counting them.
If still insufficient, disclose the candidate gap and mark partial concise brief when required.
```

Mainstream wires alone are insufficient for candidate completion. Candidate search must expand into non-English/regional and non-mainstream sources.

## duplicate and primary-domain rule

```text
One event = one primary domain quota.
Other domains may reference the event in mapping / indicator / synthesis, but cannot count it again.
Duplicate or repeated themes require a fresh delta; otherwise reject from quota.
```

Required counters:

```text
duplicate_rejection_count
field_overlap_rejection_count
niche_low_novelty_rejection_count
candidate_retry_paths_used
```

## topic / trend formation rule

```text
Many related reports, repeated media mentions, social discussion or spreading vocabulary = 話題形成.
Many actual applications, pilots, product launches, company actions, investment, hiring, usage data or supply-chain changes = 趨勢形成.
If already commercially broad and measurable, consider upgrading from candidate to major signal.
```

Do not call something a trend just because it has many articles. Many articles without adoption evidence is topic formation, not trend formation.

## Taiwan news rule

Taiwan section must be Taiwan news, not generic Taiwan mapping. If no qualified Taiwan news is found, disclose checked sources, source hits/misses, keywords and next retry. For Taiwan crypto, obey fixed-source and legislative-trigger rules in `configs/source_routing_rules.yml`; if fixed sources were not checked, do not claim no Taiwan crypto news.

Required Taiwan audit fields:

```text
Taiwan_qualified_item_count_after_audit
Taiwan_direct_sources_checked
Taiwan_source_hits
Taiwan_source_misses
Taiwan_remaining_gap
```

## news freshness rule

Every counted item must identify:

```text
今日新增點
是否重複歷史主題
```

Background concepts, old research without new relevance, model synthesis, generic Taiwan implications, historical replay, and unverified feed items do not count.

## news vs synthesis rule

Indicators, themes, conclusions, Taiwan implications, model inference and cross-domain summaries do not count as news or niche candidates. Every synthesis statement should point back to supporting IDs.

## technology rule

Technology domain must obey `configs/technology_development.yml`. AI domain cannot consume Technology quota. At least six non-AI technology subdomains must be scanned; otherwise mark Technology coverage partial.

## retail fixed matrix

The concise report must preserve:

```text
cost_pressure
channel_offline_department_store_mall_street
channel_online_marketplace_social_commerce
product_fashion_style_assortment_material_fit_category
inventory_markdown_mid_price_pressure
membership_CRM_loyalty_retail_media
social_commerce_content_discovery_AI_referral
true_vs_fake_segmentation
Taiwan_retail_commercial_district_department_store_brand
```

Retail domain is not only channel news. It must include fashion, apparel, style, trend, assortment, consumer taste shifts, true/fake segmentation, and Taiwan local retail signals when source-backed. If evidence is missing, disclose the gap.

## crypto fixed matrix

The concise report must preserve:

```text
BTC_ETH_SOL_market_structure
ETF_flows
stablecoin_supply_and_dry_powder
RWA_tokenized_assets
Perp_DEX_volume_OI_funding
TVL_fees_revenue
regulation_policy
Taiwan_crypto_fixed_sources
```

Crypto section must not rely only on price headlines. If quantitative data is not checked, mark crypto indicator coverage partial.

## structural trend indicator rule

The concise report must include a Structural Trend Indicator Panel covering:

```text
生產力便車無法共享的 K 型經濟
AI 泡沫 / 過度投資趨勢
品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾
```

Each thesis must include current direction, confidence, supporting signal IDs, counter signals or none, missing data, one-sentence read, and next verification. These are cumulative direction meters, not single-day conclusions.

## final indicator and synthesis panel rule

Fixed indicator tracking is required at the end and must not count toward the per-domain 3+3 quota.

## output status wording

```text
輸出模式：每日推播精簡版。
精簡版狀態：complete concise brief / partial concise brief。
完整正式閘門：未嘗試 / 未通過 / 另需分段研究版。
結構閘門狀態：通過 / 未通過。
新資訊密度狀態：通過 / 偏低 / 未通過。
台灣新聞狀態：通過 / 不足 / 未完整。
來源庫檢查狀態：通過 / partial / 未完成。
FreshRSS / feed-stack 狀態：通過 / partial / 未完成 / not_available。
每日執行品質閘門：通過 / partial / failed。
```

## completion rule

Concise mode can be marked `complete concise brief` only when:

```text
entry read complete or missing files disclosed
daily execution quality gate read and executed
structural trend indicators read and output
source routing rules read
niche candidate policy read
technology development policy read
source library read or missing files disclosed
feed status checked or unavailable disclosed
six domains covered
all domains contain exactly 3 major signals
all domains contain exactly 3 niche candidates
all counted events have primary_domain and pass duplicate gate
all candidates contain candidate_type, formation_level, fresh concrete anchor and early-signal fields
all domains contain 1–2 Taiwan news items or explicit valid insufficiency disclosure
all items contain evidence trace
all items contain today_new_information and historical_duplication_status
retail fixed matrix present
crypto fixed matrix present
source-library coverage audit present or material gaps disclosed
candidate retry / external discovery executed when quota or novelty is low
data gaps disclosed
final indicator status and news synthesis panel present
post-brief review present with required counters
```

If any item is missing, mark `partial concise brief`.
