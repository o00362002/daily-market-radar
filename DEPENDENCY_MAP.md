# Daily Market Radar｜DEPENDENCY_MAP

Thin-mount dependency map for the Daily Market Radar repo.

This file is the active source for:

```text
output modes
route → workflow → template chains
mode-specific completion gates
source-library routing gates
sync checks
```

Do not create a separate active execution-gate file for daily output modes. Daily gate rules belong here so dependency and completion logic stay synchronized.

---

## 1. Source of truth

```text
Current mount: brain.manifest.yaml
Execution entry: AGENTS.md
Current state: CURRENT_STATE.md
Current decisions: CURRENT_DECISIONS.md
Agent map and task routing: AGENT_DEFINITION_MAP.md
Dependency and completion gates: DEPENDENCY_MAP.md
Freshness and Taiwan news rules: configs/news_freshness_and_taiwan_news.yml
Source routing rules: configs/source_routing_rules.yml
Source library spec: SOURCE_LIBRARY_SPEC.md
Source library files: sources/key_media_library.yml, sources/official_and_data_sources.yml
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
→ SOURCE_LIBRARY_SPEC.md + sources/
→ DEPENDENCY_MAP.md / Full Daily Radar Gate

Daily Push Brief
→ AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ templates/daily_push_brief_template.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ SOURCE_LIBRARY_SPEC.md + sources/
→ DEPENDENCY_MAP.md / Daily Push Brief Gate

News Search Output
→ AGENT_NEWS_SEARCH
→ workflows/news_search_content_workflow.md
→ templates/news_search_content_template.md or templates/news_search_content_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ SOURCE_LIBRARY_SPEC.md + sources/

News Content Output
→ AGENT_NEWS_CONTENT
→ workflows/news_content_workflow.md
→ templates/news_content_template.md or templates/news_content_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
```

If route, workflow, template, config, and gate disagree, mark the output:

```text
依賴鏈不一致：partial / blocked
```

---

## 3. Routing

```text
Task routing lives inside AGENT_DEFINITION_MAP.md.
No standalone ROUTING.md is active.
```

Default daily news / daily push / brief requests route to:

```text
AGENT_DAILY_PUSH_BRIEF
```

Only route to `AGENT_RADAR_REPORT` when the user explicitly asks for a full formal archive report or `reports/YYYY/YYYY-MM-DD.md` output.

---

## 4. Shared Freshness and Taiwan News Gate

Applies to Daily Push Brief, Full Daily Radar, News Search Output, and News Content Output.

Mandatory rule file:

```text
configs/news_freshness_and_taiwan_news.yml
```

Core rules:

```text
1. 每日情報必須優先提供今日新增資訊。
2. 不得用昨日或歷史已播概念重複填滿新聞欄位。
3. 若重複歷史主題，必須有新數據、新公司動作、新政策、新市場反應、新鏈上數據或新台灣新聞，否則不得列入大型訊號。
4. 台灣段必須優先放台灣新聞，不是模型推論的台灣映射。
5. 台灣影響、台灣推論、台灣產業關聯只能放在結論 / synthesis / final panel，不得取代台灣新聞。
```

Every news item must include ID, event, 今日新增點, source/time, evidence level, historical duplicate status, and uncertainty / next step.

Taiwan news means source-backed Taiwan event, data, company action, policy, market, retail, mall, department store, brand, channel, store opening / closure, commercial district, labor, consumer, credit, or Taiwan-linked international news.

Taiwan implications do not count as Taiwan news.

---

## 5. Shared Source Library Gate

Applies to:

```text
Daily Push Brief
Full Daily Radar
News Search Output
```

Mandatory source files:

```text
configs/source_routing_rules.yml
SOURCE_LIBRARY_SPEC.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

Core rules:

```text
1. Search routes must check the fixed source library before generic keyword fallback.
2. Keyword search remains active, but as source-scoped filtering, fallback, event expansion, retry, or discovery.
3. Important claims should be cross-checked with official / data / company / regulator sources when available.
4. Material source gaps must be disclosed.
5. Source health changes should be recorded through memory/source_health_log.json, memory/topic_coverage_log.json, or reports/backtests/ when implemented.
```

Coverage audit fields:

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

## 6. Full Daily Radar Gate

Completion requirements:

```text
6 大核心領域皆達 5 則大型重要新聞 + 3 則小眾潛力候選
已完成必要 repo 檔案讀取
已讀取 freshness / Taiwan news rules
已讀取 source routing rules, SOURCE_LIBRARY_SPEC.md, and sources/
已完成來源庫優先檢查
已完成必要搜尋與 fallback
已完成最近 7 日 reports 去重
已完成高風險 claim 檢查
已完成今日新增點檢查
已完成歷史重複主題檢查
已完成台灣新聞有效性檢查
已輸出 Coverage Matrix
已輸出 Source Library Coverage Matrix 或等效來源覆蓋審計
已輸出 Data Gaps / Retry Notes
已輸出 post-report backtest / model adjustment panel
```

If any requirement is missing, mark:

```text
完整正式播報：未通過
不可視為完整正式播報
```

---

## 7. Daily Push Brief Gate

Completion requirements:

```text
已讀取必要入口檔，或明確揭露缺失
已讀取 freshness / Taiwan news rules
已讀取 source routing rules, SOURCE_LIBRARY_SPEC.md, and sources/，或明確揭露缺失
6 大核心領域皆有覆蓋
每一核心領域包含 exactly 3 則大型訊號
每一核心領域包含 exactly 1 則小眾 / 潛力候選
每一核心領域包含 1–2 則台灣新聞，或明確標示台灣新聞不足
每則新聞 / 訊號包含 evidence trace
每則新聞 / 訊號包含今日新增點
每則新聞 / 訊號標示是否重複歷史主題
Retail Focus Block 五項固定檢查存在
Source-library coverage audit 存在或 material gaps 已揭露
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
```

If any structural, freshness, Taiwan-news, or source-library requirement is missing, mark `partial concise brief`.

---

## 8. News Search Gate

Completion requirements:

```text
topic identified
source-library route checked or missing files disclosed
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

## 9. News Content Gate

Completion requirements:

```text
input signal identified
source / evidence label preserved
today_new_information preserved or marked missing
historical duplication status preserved or marked missing
Taiwan news vs Taiwan implication separated
uncertainty not removed
output ready for human review
```

If missing, mark:

```text
content draft partial
```

---

## 10. Coverage Matrix rules

### Full Daily Radar

| 核心領域 | 大型新聞數 | 小眾候選數 | 台灣新聞 | Source Library | New Info Check | 是否達標 | 缺口 |
|---|---:|---:|---|---|---|---|---|
| AI 模型 / Agent / 工作流替代 | >=5 | >=3 | required | required | required |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | >=5 | >=3 | required | required | required |  |  |
| 零售 / 消費 / 社群 / 服飾 | >=5 | >=3 | required | required | required |  |  |
| 全球市場 / 資金流 / 地緣政治 | >=5 | >=3 | required | required | required |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | >=5 | >=3 | required | required | required |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | >=5 | >=3 | required | required | required |  |  |

### Daily Push Brief

| 核心領域 | 大型訊號數 | 小眾候選數 | 台灣新聞數 | Source Library | Evidence Trace | New Info Check | 精簡版狀態 | 漏抓風險 |
|---|---:|---:|---:|---|---|---|---|---|
| AI 模型 / Agent / 工作流替代 | 3 | 1 | 1–2 | required | required | required |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | 3 | 1 | 1–2 | required | required | required |  |  |
| 零售 / 消費 / 社群 / 服飾 | 3 | 1 | 1–2 | required | required | required |  |  |
| 全球市場 / 資金流 / 地緣政治 | 3 | 1 | 1–2 | required | required | required |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | 3 | 1 | 1–2 | required | required | required |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | 3 | 1 | 1–2 | required | required | required |  |  |

---

## 11. Sync rule

When radar scope, report format, retry rules, missed-case handling, template, report, workflow, agent map, active output mode, completion gate, freshness rule, source-library rule, source routing rule, Taiwan news rule, or Memory Trigger Check gate changes, check:

```text
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENTS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
templates/
configs/
sources/
SOURCE_LIBRARY_SPEC.md
brain.manifest.yaml
check_mount_integrity.sh
```
