# Daily Radar Workflow

Purpose: define the full formal daily market radar execution path.

Owner: `AGENT_RADAR_REPORT` in `AGENT_DEFINITION_MAP.md`.

General daily news requests should use `workflows/daily_push_brief_workflow.md` unless the user explicitly asks for a full, formal, or archive report.

Required shared rule:

```text
configs/news_freshness_and_taiwan_news.yml
```

Full reports must enforce:

```text
台灣段必須優先放台灣新聞，不得只用台灣影響或台灣推論補位。
每則大型訊號與小眾候選都必須標示今日新增點。
歷史重複主題只有在有新數據、新公司動作、新政策、新市場反應、新鏈上數據或新台灣新聞時，才能計入正式 5+3。
只有背景概念或歷史重播，不得計入 5+3。
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
1. Entry read
2. Load full radar context
3. Read configs/news_freshness_and_taiwan_news.yml
4. Search candidate signals with retry
5. Check source, date, claim risk, and 今日新增點
6. Check Taiwan news validity by domain
7. Check coverage and historical duplicates
8. Remove background-only / historical-replay items from 5+3 count
9. Format with the full daily report template
10. Run missed-case backtest loop when needed
11. Complete final status check
```

---

## required_tools

```text
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

## output_path

```text
reports/YYYY/YYYY-MM-DD.md
reports/backtests/ when needed
```

---

## completion_rule

The report can be marked `complete` only when the required tools and checks are complete, including new information and Taiwan news checks.

If any required tool or check is skipped, mark:

```text
partial full report
```

---

## practical interpretation

This workflow is for formal research and archive output. The default daily user-facing output is the push brief workflow.
