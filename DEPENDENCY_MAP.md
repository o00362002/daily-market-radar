# Daily Market Radar｜DEPENDENCY_MAP

Thin-mount dependency map for the Daily Market Radar repo.

This file is the active source for:

```text
output modes
route → workflow → template chains
mode-specific completion gates
source-library routing gates
feed-stack routing gates
FreshRSS ingestion gate addendum
sync checks
```

---

## 1. Source of truth

```text
Current mount: brain.manifest.yaml
Execution entry: AGENTS.md
Current state: CURRENT_STATE.md
Current decisions: CURRENT_DECISIONS.md
Agent map and task routing: AGENT_DEFINITION_MAP.md
Dependency and completion gates: DEPENDENCY_MAP.md
FreshRSS ingestion gate addendum: DEPENDENCY_MAP_FRESHRSS_INGESTION_GATE.md
Freshness and Taiwan news rules: configs/news_freshness_and_taiwan_news.yml
Source routing rules: configs/source_routing_rules.yml
Feed discovery stack: configs/feed_discovery_stack.yml
Source library spec: SOURCE_LIBRARY_SPEC.md
Source library files: sources/key_media_library.yml, sources/official_and_data_sources.yml
Feed registry: sources/channel_feed_sources.json
Discovery provider registry: sources/discovery_providers.yml
FreshRSS seed OPML: FRESHRSS_SEEDS.opml
```

---

## 2. Active output modes and dependency chains

```text
Full Daily Radar
→ AGENT_RADAR_REPORT
→ workflows/daily_radar_workflow.md
→ templates/daily_report_template.md or templates/daily_report_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ configs/feed_discovery_stack.yml when feed/discovery stack is relevant
→ DEPENDENCY_MAP_FRESHRSS_INGESTION_GATE.md when FreshRSS candidates are used
→ SOURCE_LIBRARY_SPEC.md + sources/
→ DEPENDENCY_MAP.md / Full Daily Radar Gate

Daily Push Brief
→ AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ templates/daily_push_brief_template.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ configs/feed_discovery_stack.yml when feed/discovery stack is relevant
→ DEPENDENCY_MAP_FRESHRSS_INGESTION_GATE.md when FreshRSS is available
→ SOURCE_LIBRARY_SPEC.md + sources/
→ DEPENDENCY_MAP.md / Daily Push Brief Gate

News Search Output
→ AGENT_NEWS_SEARCH
→ workflows/news_search_content_workflow.md
→ templates/news_search_content_template.md or templates/news_search_content_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ configs/feed_discovery_stack.yml when feed/discovery stack is relevant
→ DEPENDENCY_MAP_FRESHRSS_INGESTION_GATE.md when FreshRSS candidates are requested
→ SOURCE_LIBRARY_SPEC.md + sources/

News Content Output
→ AGENT_NEWS_CONTENT
→ workflows/news_content_workflow.md
→ templates/news_content_template.md or templates/news_content_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
```

If route, workflow, template, config, and gate disagree, mark:

```text
依賴鏈不一致：partial / blocked
```

---

## 3. Shared Source Library Gate

Mandatory files:

```text
configs/source_routing_rules.yml
SOURCE_LIBRARY_SPEC.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
configs/query_recipes.yml
```

Core requirements:

```text
1. Fixed source library before generic keyword fallback.
2. Query recipes before free-form queries.
3. Official/data cross-check for important claims when available.
4. Material source gaps disclosed.
5. Source health recorded through memory/source_health_log.json, memory/topic_coverage_log.json, or reports/backtests/ when implemented.
```

Audit fields:

```text
source_library_checked
priority_sources_checked
source_hits
source_misses
keyword_fallback_used
official_or_data_crosscheck_used
taiwan_sources_checked_when_relevant
external_discovery_used_when_needed
remaining_source_gap
```

---

## 4. Shared Feed Stack Gate

Applies when feed collection, RSSHub, FreshRSS, GDELT, Media Cloud, or discovery gaps are relevant.

Mandatory files:

```text
configs/feed_discovery_stack.yml
sources/channel_feed_sources.json
sources/discovery_providers.yml
FRESHRSS_SEEDS.opml when importing starter feeds
DEPENDENCY_MAP_FRESHRSS_INGESTION_GATE.md when FreshRSS candidates are used
```

Core requirements:

```text
1. RSSHub and FreshRSS improve collection coverage, not evidence strength.
2. Only route_status = verified and enabled_for_opml = true may be imported into OPML.
3. Route templates do not count as checked feeds.
4. GDELT and Media Cloud are discovery providers; original sources still need verification.
5. New weak signals found through feeds/discovery enter memory/potential_pool.md before output-stage filtering.
6. Material feed/discovery gaps disclosed.
```

Audit fields:

```text
feed_stack_loaded
freshrss_checked
rsshub_routes_checked
rsshub_route_gaps
direct_rss_feeds_checked
gdelt_used_when_gap
media_cloud_used_when_gap
potential_pool_capture_done
official_or_data_crosscheck_done
remaining_channel_gap
```

---

## 5. Full Daily Radar Gate

Completion requirements:

```text
6 大核心領域皆達 5 則大型重要新聞 + 3 則小眾潛力候選
已完成必要 repo 檔案讀取
已讀取 freshness / Taiwan news rules
已讀取 source routing rules, SOURCE_LIBRARY_SPEC.md, and sources/
已完成來源庫優先檢查
已完成必要搜尋與 fallback
已完成 feed stack check when relevant
已完成 FreshRSS ingestion gate when FreshRSS candidates are used
已完成最近 7 日 reports 去重
已完成高風險 claim 檢查
已完成今日新增點檢查
已完成歷史重複主題檢查
已完成台灣新聞有效性檢查
已輸出 Coverage Matrix
已輸出 Source Library Coverage Matrix 或等效來源覆蓋審計
已輸出 Feed Stack Coverage Audit when relevant
已輸出 FreshRSS Ingestion Audit when FreshRSS candidates are used
已輸出 Data Gaps / Retry Notes
已輸出 post-report backtest / model adjustment panel
```

If any requirement is missing, mark:

```text
完整正式播報：未通過
不可視為完整正式播報
```

---

## 6. Daily Push Brief Gate

Completion requirements:

```text
已讀取必要入口檔，或明確揭露缺失
已讀取 freshness / Taiwan news rules
已讀取 source routing rules, SOURCE_LIBRARY_SPEC.md, and sources/，或明確揭露缺失
已讀取 FreshRSS ingestion addendum when FreshRSS is available
6 大核心領域皆有覆蓋
每一核心領域包含 exactly 3 則大型訊號
每一核心領域包含 exactly 1 則小眾 / 潛力候選
每一核心領域包含 1–2 則台灣新聞，或明確標示台灣新聞不足
每則新聞 / 訊號包含 evidence trace
每則新聞 / 訊號包含今日新增點
每則新聞 / 訊號標示是否重複歷史主題
Source-library coverage audit 存在或 material gaps 已揭露
Feed stack audit 存在或 material feed gaps 已揭露 when relevant
FreshRSS ingestion audit 存在或 FreshRSS unavailable 已揭露 when relevant
Data Gaps and Retry Notes 存在
Final Indicator Status and News Synthesis Panel 存在且放在最後
Post-brief Review 存在
指標狀態與結論不得計入 3+1 新聞數量
指標狀態與結論必須回指上方新聞 ID
```

Daily Push Brief must write:

```text
輸出模式：每日推播精簡版。
精簡版狀態：complete concise brief / partial concise brief。
完整 48 則正式閘門：未嘗試 / 未通過 / 另需分段研究版。
結構閘門狀態：通過 / 未通過。
新資訊密度狀態：通過 / 偏低 / 未通過。
台灣新聞狀態：通過 / 不足 / 未完整。
來源庫檢查狀態：通過 / partial / 未完成。
Feed stack 狀態：通過 / partial / 未完成 / not_required。
FreshRSS ingestion 狀態：通過 / partial / 未完成 / not_available。
```

If any structural, freshness, Taiwan-news, source-library, required feed-stack, or required FreshRSS ingestion item is missing, mark `partial concise brief`.

---

## 7. News Search Gate

Completion requirements:

```text
topic identified
source-library route checked or missing files disclosed
feed-stack relevance checked or marked not_required
FreshRSS candidate gate checked or marked not_available when relevant
priority sources searched
keyword fallback used only after source checks or disclosed as exception
claims labelled
major news and candidates separated
today_new_information included for each news item
historical duplication status included
Taiwan news searched or Taiwan news insufficiency disclosed when relevant
data gaps disclosed
handoff suggestion included
```

If missing, mark:

```text
news search partial
```

---

## 8. Sync rule

When radar scope, report format, retry rules, missed-case handling, template, report, workflow, agent map, active output mode, completion gate, freshness rule, source-library rule, feed-stack rule, FreshRSS ingestion rule, source routing rule, Taiwan news rule, or Memory Trigger Check gate changes, check:

```text
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENTS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
DEPENDENCY_MAP_FRESHRSS_INGESTION_GATE.md
templates/
configs/
sources/
SOURCE_LIBRARY_SPEC.md
brain.manifest.yaml
check_mount_integrity.sh
```
