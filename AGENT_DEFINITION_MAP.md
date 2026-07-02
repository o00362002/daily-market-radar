# AGENT_DEFINITION_MAP

Route map for `daily-market-radar`.

Select exactly one primary `AGENT_` route before execution.

All routes that output news, search results, or content must apply:

```text
configs/news_freshness_and_taiwan_news.yml
```

Routes that perform search or radar collection must also apply:

```text
configs/source_routing_rules.yml
SOURCE_LIBRARY_SPEC.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

These rules prevent three recurring failures:

```text
1. Repeating historical concepts as if they are new daily news.
2. Replacing Taiwan news with generic Taiwan implications.
3. Starting from broad keyword search while skipping the fixed source library.
```

---

## AGENT_ routes

| Route id | Use when |
|---|---|
| `AGENT_RADAR_REPORT` | explicit full daily market radar report / formal archive report |
| `AGENT_DAILY_PUSH_BRIEF` | default daily news broadcast / concise daily push brief / chat daily news push |
| `AGENT_NEWS_SEARCH` | specific topic news search |
| `AGENT_NEWS_CONTENT` | rewrite checked signals into content |
| `AGENT_COVERAGE_BACKTEST` | missed case, gap, coverage, or adjustment review |
| `AGENT_RADAR_CONFIG` | config, trigger, evidence, retry, freshness, Taiwan news, source library, or watchlist change |

---

## Route selection rules

Default daily output is lightweight.

Route to `AGENT_DAILY_PUSH_BRIEF` when the user asks:

```text
今天播報
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
morning brief
daily news
daily push
concise brief
簡版
輕量版
```

Do not route to `AGENT_RADAR_REPORT` unless the user explicitly asks:

```text
正式版
完整版
完整正式版
完整研究歸檔版
正式每日雷達
完整每日雷達
Full Daily Radar
full report
complete report
archival report
48-signal report
完整 48 則
5+3
完整硬閘門
產出 reports/YYYY/YYYY-MM-DD.md
完整寫入 reports
歸檔版
```

If user wording is ambiguous between daily push and full archive, choose `AGENT_DAILY_PUSH_BRIEF` and disclose:

```text
輸出模式：每日推播精簡版。
完整 48 則正式閘門：未嘗試 / 另需分段研究版。
```

General words such as 每日 / 播報 / 新聞 / 市場雷達 / today / brief do not upgrade the route to the full archive workflow.

---

## Dependency chain

Each route must follow the active output-mode chain in `DEPENDENCY_MAP.md`.

```text
AGENT_RADAR_REPORT
→ workflows/daily_radar_workflow.md
→ templates/daily_report_template.md or templates/daily_report_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ SOURCE_LIBRARY_SPEC.md + sources/
→ DEPENDENCY_MAP.md / Full Daily Radar Gate

AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ templates/daily_push_brief_template.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ SOURCE_LIBRARY_SPEC.md + sources/
→ DEPENDENCY_MAP.md / Daily Push Brief Gate

AGENT_NEWS_SEARCH
→ workflows/news_search_content_workflow.md
→ templates/news_search_content_template.md or templates/news_search_content_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
→ configs/source_routing_rules.yml
→ SOURCE_LIBRARY_SPEC.md + sources/

AGENT_NEWS_CONTENT
→ workflows/news_content_workflow.md
→ templates/news_content_template.md or templates/news_content_template_v2.md
→ configs/news_freshness_and_taiwan_news.yml
```

Route, workflow, template, config, and gate must match. If they do not match, mark the output as:

```text
依賴鏈不一致：partial / blocked
```

Do not use a separate active daily execution-gate file for route completion rules. Daily output completion gates live in `DEPENDENCY_MAP.md`.

---

## Source-library search boundary

For `AGENT_RADAR_REPORT`, `AGENT_DAILY_PUSH_BRIEF`, and `AGENT_NEWS_SEARCH`:

```text
- Fixed source library must be checked before generic keyword fallback.
- Keyword search can filter, expand, retry, or discover sources, but must not replace source-library coverage.
- Material source gaps must be disclosed in the output or final status panel.
- Official / data sources should be used to verify high-risk claims and indicator changes.
```

---

## News freshness and Taiwan news boundary

For `AGENT_RADAR_REPORT`, `AGENT_DAILY_PUSH_BRIEF`, `AGENT_NEWS_SEARCH`, and `AGENT_NEWS_CONTENT`:

```text
- Every news item must include 今日新增點.
- Every news item must mark whether it repeats a historical theme.
- Repeated themes need new data / company action / policy / market reaction / chain metric / Taiwan news to count as current news.
- Taiwan news must be source-backed Taiwan event / data / company action / policy / market news.
- Taiwan implication is model inference and must not be counted as Taiwan news.
```

---

## Multi-agent handoff rule

Agents do not share hidden reasoning.

Agents hand off through externalized repo state:

```text
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
reports/backtests/
Post-Execution Record
Memory Patch Candidate
```

Select exactly one primary route before execution.

After execution, use the Post-Execution Backtest-to-Memory Gate when the task affects files, state, decisions, routes, evidence, dependency gates, radar corrections, or reusable workflow behavior.

---

## Boundary

Agent owns a complete task goal. Workflow orders steps. Skill judges. Tool operates. Loop reviews and improves.
