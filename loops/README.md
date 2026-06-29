# Loops

Loop 是每日情報系統的品質檢查、漏抓回測與同步修正機制。

---

## Position in execution chain

```text
signal_search_tool
→ claim_risk_checker
→ coverage_checker
→ report_formatter
→ missed_case_backtest_loop, if needed
```

Loops do not replace the required tool chain. They review and improve it.

---

## Daily Quality Loops

- `radar_coverage_check.loop`：確認固定雷達與三桶硬檢查是否完成
- `evidence_quality_check.loop`：證據分級與來源品質檢查
- `cross_day_dedup_check.loop`：跨日去重檢查
- `missing_data_review.loop`：無資料時檢查 retry 是否完成

---

## Learning Loops

- `missed_case_backtest_loop.md`：使用者指出漏抓後，把漏抓案例轉成未來硬檢查
- `watchlist_update.loop`：新增或調整 watchlist
- `template_sync_check.loop`：規格更新後檢查模板是否同步
- `current_decision_update.loop`：重大規格改動後更新 CURRENT_DECISIONS

---

## Human Review

每日報告仍需人工判斷：哪些訊號值得保留，哪些只是低證據候選。

If a loop proposes rule adjustment, route it through the mother Brain's Backtest Decision Gate before changing core rules.
