# Daily Push Brief Workflow

Purpose: define the default structured concise daily push version for chat / automation output when a full formal report is not explicitly requested.

This workflow does **not** replace the full `daily_radar_workflow.md`.
Concise means shorter wording per item, not reduced reconnaissance structure.

Required shared rules:

```text
configs/news_freshness_and_taiwan_news.yml
configs/source_routing_rules.yml
configs/niche_candidate_policy.yml
configs/technology_development.yml
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

## source-first rule

Daily Push Brief must check the fixed source library and FreshRSS candidate inbox before generic keyword fallback.

Minimum internal flow:

```text
1. Load configs/source_routing_rules.yml.
2. Load configs/niche_candidate_policy.yml.
3. Load configs/technology_development.yml.
4. Load sources/key_media_library.yml.
5. Load sources/official_and_data_sources.yml.
6. Load configs/freshrss_ingestion.yml.
7. Load sources/channel_feed_sources.json and FRESHRSS_SEEDS.opml when feed stack is available.
8. For each of six domains, check global media, Taiwan media, official/data sources, and feed candidates.
9. Build major-signal pool and a separate niche-candidate pool.
10. Expand candidate search beyond mainstream wires into research, startup, product, niche industry, developer, social-first, hiring, on-chain, patent and clinical sources.
11. For retail / consumer / social / fashion / trend domain, also check fashion media, style platforms, runway trend reports, brand official channels, merchandising shifts, assortment changes and street-style / social-style signals.
12. Normalize candidates and verify original source.
13. Classify each candidate by candidate_type and formation_level.
14. Use query recipes and keyword search to filter, enrich, or retry gaps.
15. Disclose material source and feed gaps.
```

FreshRSS is a candidate pool. It accelerates discovery but does not replace original-source verification.

## minimum output shape

```text
0. Read status and mode
1. Hard gate status: concise mode / full gate not attempted or not passed
2. Six-domain coverage matrix
3. Source-library coverage audit, compact version
4. FreshRSS / feed-stack coverage audit, compact version
5. Each core domain: exactly 3 major signals
6. Each core domain: exactly 3 niche / potential candidates
7. Each core domain: 1–2 Taiwan news items directly under the domain
8. Retail / fashion focus block with fixed checks
9. New Information / History Duplicate Check
10. Data gaps and retry notes
11. Final indicator status and news synthesis panel
12. Post-brief review inside the final panel
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
Taiwan news: 1–2 items
Evidence trace: required for every item
New information check: required for every item
Historical duplication status: required for every item
Source-library check status: yes / partial / no
FreshRSS candidate check: yes / partial / no / not_available
Keyword fallback: yes / no
```

Candidate items additionally require:

```text
candidate_type: 新領域 / 新應用 / 新概念 / 新趨勢
formation_level: 弱訊號 / 話題形成 / 趨勢形成 / 主流化中
concrete_anchor
why_niche_or_early
why_it_could_scale
cannot_conclude
next_verification
```

A candidate must be a source-backed early weak signal, not generic trend commentary. At least one concrete anchor is mandatory: company action, product experiment, paper/data, startup funding, developer adoption, on-chain metric, niche-industry event, social/community signal, pilot, hiring shift, patent, clinical trial, prototype, supply-chain anomaly, fashion/style microtrend, brand merchandising shift or assortment change.

## candidate equality and retry rule

```text
Concise target = 3 major + 3 niche candidates per domain.
Candidate target equals major target.
If 3 candidates are not found, do not fabricate.
Run retry / external discovery first.
If still insufficient, disclose the candidate gap and mark partial concise brief when required.
```

Mainstream wires alone are insufficient for candidate completion. Candidate search must expand into non-English/regional and non-mainstream sources.

## topic / trend formation rule

```text
Many related reports, repeated media mentions, social discussion or spreading vocabulary = 話題形成.
Many actual applications, pilots, product launches, company actions, investment, hiring, usage data or supply-chain changes = 趨勢形成.
If already commercially broad and measurable, consider upgrading from candidate to major signal.
```

Do not call something a trend just because it has many articles. Many articles without adoption evidence is topic formation, not trend formation.

## Taiwan news rule

Taiwan section must be Taiwan news, not generic Taiwan mapping. If no qualified Taiwan news is found, disclose checked sources, feed candidates, keywords and next retry. For Taiwan crypto, obey fixed-source and legislative-trigger rules in `configs/source_routing_rules.yml`; if fixed sources were not checked, do not claim no Taiwan crypto news.

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

## retail / fashion focus rule

The concise report must preserve:

```text
department store / mall / street retail
brand openings / closures / tenant mix
online retail / marketplace / social commerce
fashion / apparel / style / trend signals
流行趨勢 / 穿搭風格 / 顏色 / 材質 / 版型 / 商品類別變化
fashion inventory / discount / mid-price pressure
Taiwan retail / malls / department stores / brands / fashion channels
```

Retail domain is not only channel news. It must include fashion, apparel, style, trend, assortment and consumer taste shifts when source-backed.

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
```

## completion rule

Concise mode can be marked `complete concise brief` only when:

```text
entry read complete or missing files disclosed
source routing rules read
niche candidate policy read
technology development policy read
source library read or missing files disclosed
feed status checked or unavailable disclosed
six domains covered
all domains contain exactly 3 major signals
all domains contain exactly 3 niche candidates
all candidates contain candidate_type, formation_level, concrete anchor and early-signal fields
all domains contain 1–2 Taiwan news items or explicit valid insufficiency disclosure
all items contain evidence trace
all items contain today_new_information and historical_duplication_status
retail / fashion focus block present
source-library coverage audit present or material gaps disclosed
candidate retry / external discovery executed when quota missed
data gaps disclosed
final indicator and synthesis panel present
post-brief review present
```

If any item is missing, mark `partial concise brief`.
