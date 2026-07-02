# Daily Radar Workflow

Purpose: define the full formal daily market radar execution path.

Owner: `AGENT_RADAR_REPORT` in `AGENT_DEFINITION_MAP.md`.

General daily news requests should use `workflows/daily_push_brief_workflow.md` unless the user explicitly asks for a full, formal, or archive report.

Required shared rules:

```text
configs/news_freshness_and_taiwan_news.yml
configs/source_routing_rules.yml
SOURCE_LIBRARY_SPEC.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

Full reports must enforce:

```text
台灣段必須優先放台灣新聞，不得只用台灣影響或台灣推論補位。
每則大型訊號與小眾候選都必須標示今日新增點。
歷史重複主題只有在有新數據、新公司動作、新政策、新市場反應、新鏈上數據或新台灣新聞時，才能計入正式 5+3。
只有背景概念或歷史重播，不得計入 5+3。
固定來源庫必須先於 generic keyword search 檢查。
```

---

## name

```text
daily_radar_workflow
```

## trigger

```text
explicit full daily radar report request
scheduled full daily radar run
manual full market radar generation
formal archive report request
5+3 hard-gate report request
48-signal report request
archive output request
```

## non_trigger

```text
每日播報
每日新聞
今天的每日新聞
播報今天的每日新聞
今日市場雷達
今天市場雷達
今天新聞
每日推播
morning brief
daily news
daily push
quick daily market brief
```

Non-trigger phrases route to `AGENT_DAILY_PUSH_BRIEF` unless the user explicitly asks for formal, complete, or archival output.

---

## ordered_steps

```text
1. Entry read.
2. Load full radar context.
3. Read configs/news_freshness_and_taiwan_news.yml.
4. Read configs/source_routing_rules.yml.
5. Read SOURCE_LIBRARY_SPEC.md.
6. Read sources/key_media_library.yml and sources/official_and_data_sources.yml.
7. Build six-domain source plan from source library.
8. Collect priority source candidates by domain, region, and language.
9. Filter collected source items with topic keywords and radar rules.
10. Cross-check high-risk claims with official / data sources.
11. Use generic keyword search only as fallback / enrichment / discovery.
12. If 5+3 is not met, run retry and external discovery.
13. Check source, date, claim risk, and 今日新增點.
14. Check Taiwan news validity by domain.
15. Check coverage and historical duplicates.
16. Remove background-only / historical-replay items from 5+3 count.
17. Format with the full daily report template.
18. Output source-library coverage matrix and retry notes.
19. Run missed-case backtest loop when needed.
20. Complete final status check.
```

---

## required_tools

```text
source_library_loader
source_router
source_fetcher
signal_search_tool
claim_risk_checker
coverage_checker
freshness_checker
taiwan_news_checker
report_formatter
```

---

## required_checks

```text
source library check
priority source coverage check
source / date check
search retry check before gap
claim risk check
new information check
historical duplicate check
Taiwan news validity check
coverage check
gap note check
missed-case backtest check
```

---

## source-first rule

Full Daily Radar must not start from generic keyword search.

It must first check relevant priority sources from:

```text
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

Generic web search is allowed only after one of these conditions is true:

```text
priority source results are insufficient
source coverage needs event expansion
Taiwan news gap requires retry
external discovery is needed to meet 5+3
```

---

## Taiwan news rule

Allowed Taiwan news:

```text
台灣官方資料 / 政策 / 統計
台灣公司公告 / 財報 / 法說 / 重大動作
台灣媒體報導的本地產業事件
台灣百貨 / 商場 / 品牌 / 通路 / 展店 / 撤櫃 / 商圈新聞
台灣市場數據 / 匯率 / 勞動 / 消費 / 信用資料
國際新聞明確包含台灣公司、台灣供應鏈、台灣市場或台灣政策
```

Not Taiwan news:

```text
國際新聞可能影響台灣
台灣企業應注意
台灣品牌可以學
模型推論的台灣關聯
```

If Taiwan news is not found, write:

```text
台灣新聞不足
已查來源：
已查關鍵字：
下一步補查：
```

---

## freshness rule

Every counted major signal / niche candidate must include:

```text
ID
事件
今日新增點
來源 / 時間
證據等級
是否重複歷史主題
不確定點 / 下一步
```

Items without new information must not count toward 5+3.

---

## source coverage matrix requirement

Full reports must include a source-library coverage matrix or equivalent audit:

```text
核心領域
priority sources checked
source hits
source misses
keyword fallback used
external discovery used
official / data cross-check used
Taiwan sources checked
remaining source gap
```

If this audit is missing, mark the report:

```text
partial full report
```

---

## output_path

```text
reports/YYYY/YYYY-MM-DD.md
reports/backtests/ when needed
```

---

## completion_rule

The report can be marked `complete` only when the required source-library checks, tools, and freshness / Taiwan news checks are complete.

If any required tool or check is skipped, mark:

```text
partial full report
```

---

## practical interpretation

This workflow is for formal research and archive output. The default daily user-facing output is the push brief workflow.
