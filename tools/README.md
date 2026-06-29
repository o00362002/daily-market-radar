# Tools

Tool 是搜尋、讀取、查詢、整理、檢查或輸出操作，不負責最終情報判斷。

---

## Required Daily Radar Tool Chain

The daily report must follow this order:

```text
1. signal_search_tool
2. claim_risk_checker
3. coverage_checker
4. report_formatter
```

If any required tool is skipped, the report cannot be marked `complete`.

---

## Primary Tools

```text
tools/signal_search_tool.md
tools/claim_risk_checker.md
tools/coverage_checker.md
tools/report_formatter.md
```

---

## Search Tools

- `web_search.tool`：網路搜尋
- `official_source_lookup.tool`：官方公告、監管、公司資料查找
- `news_search.tool`：新聞來源查找
- `social_signal_scan.tool`：社群弱訊號掃描
- `chain_data_lookup.tool`：鏈上資料、ETF、TVL、OI、Fees 等查詢

---

## Repo Tools

- `read_config.tool`：讀取 configs
- `read_memory.tool`：讀取 missed_cases / watchlist
- `read_template.tool`：讀取報告模板
- `read_recent_reports.tool`：讀取近期 reports

---

## Output Tools

- `report_writer.tool`：產出 Markdown 報告
- `report_index_update.tool`：更新 reports/INDEX

---

## Boundary

Tool 只提供資料、檢查或操作。是否重要、是否可信、是否進報告，由 Skill、Workflow 或 Agent 判斷。
