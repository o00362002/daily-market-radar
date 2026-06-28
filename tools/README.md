# Tools

Tool 是搜尋、讀取、查詢、整理或輸出操作，不負責最終情報判斷。

## Search Tools

- `web_search.tool`：網路搜尋
- `official_source_lookup.tool`：官方公告、監管、公司資料查找
- `news_search.tool`：新聞來源查找
- `social_signal_scan.tool`：社群弱訊號掃描
- `chain_data_lookup.tool`：鏈上資料、ETF、TVL、OI、Fees 等查詢

## Repo Tools

- `read_config.tool`：讀取 configs
- `read_memory.tool`：讀取 missed_cases / watchlist
- `read_template.tool`：讀取報告模板
- `read_recent_reports.tool`：讀取近期 reports

## Output Tools

- `report_writer.tool`：產出 Markdown 報告
- `report_index_update.tool`：更新 reports/INDEX

## Boundary

Tool 只提供資料或操作。是否重要、是否可信、是否進報告，由 Skill、Workflow 或 Agent 判斷。