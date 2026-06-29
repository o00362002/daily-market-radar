# daily-market-radar｜RUNBOOK

本檔是每日市場情報的硬性執行流程。每日報告不得只參考 README 或 configs 後直接輸出，必須依本 runbook 逐步執行。

---

## 0. Execution Rule

```text
若 RUNBOOK / CHECKLIST / loops/daily_report_quality_loop.yml 未完成，不得輸出正式每日報告。
若因工具限制無法完成，必須在報告最上方明確列出未完成項目與影響。
```

---

## 1. Load Context

依 `CONTEXT_ROUTING.md` 讀取入口、configs、memory、templates、reports 與 Execution Edge 文件。

必須特別確認：

```text
reports/INDEX.md
recent reports/YYYY/YYYY-MM-DD.md
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
configs/indicator_tracking.yml
memory/missed_cases.md
memory/watchlist.md
```

---

## 2. Build Preflight Checklist

開始搜尋前，先建立本次執行檢查表：

```text
repo_context_loaded: pass/fail
reports_index_loaded: pass/fail
recent_reports_loaded: pass/fail
missed_cases_loaded: pass/fail
indicator_tracking_loaded: pass/fail
edge_case_discovery_loaded: pass/fail
search_retry_loaded: pass/fail
templates_loaded: pass/fail
```

此檢查表必須在報告前段或回測面板中呈現濃縮版。

---

## 3. Run Main Radar Search

依 `configs/radars.yml`、`configs/triggers.yml`、`configs/source_strategy.md` 執行多語言搜尋。

最低語言：

```text
English
繁體中文
簡體中文
```

特定區域事件可補：日文、韓文、歐洲語系、事件所在地語言。

---

## 4. Run Mandatory Indicator Tracking

依 `configs/indicator_tracking.yml` 輸出固定指標追蹤總表。

每一大桶至少包含：

```text
指標
目前狀態
方向
異常訊號
來源與時間
下一步驗證
```

若查無資料，必須標示資料缺口，不得省略該桶。

---

## 5. Run Edge Case Discovery

依 `configs/edge_case_discovery.yml` 每日輸出至少 5 則全球特殊應用 / 邊緣案例候選。

硬性要求：

```text
至少 5 則候選
至少涵蓋 3 個不同領域
每則標示來源類型、地區、證據等級、為什麼可能重要、不能下的結論、下一步驗證
低證據不可刪除，只能降級為候選
```

---

## 6. Run Search Retry

若任何必掃雷達沒有重大訊號、只抓到主流新聞、或沒有特殊候選，必須依 `configs/search_retry_protocol.yml` 至少 retry 3 種方法。

可用 retry 類型：

```text
change_keywords
change_language
change_source_type
change_level
change_time_window
search_negative_space
search_metrics_instead_of_news
```

輸出時必須說明已嘗試哪些 retry。不得直接用「無資料」結束。

---

## 7. Generate Report

使用：

```text
templates/daily_report_template.md
templates/final_synthesis_template.md
```

報告必須包含：

```text
系統資料讀取狀態
今日雷達覆蓋矩陣
固定指標追蹤總表
今日 3–5 個潛力架構 / 早期敘事候選
今日必看訊號
全球特殊應用 / 邊緣案例候選，至少 5 則
各主領域國際訊號 + 台灣映射
資料不足與 retry 狀態
舊版 / 新版補漏比對
推播後回測與模型調整面板
```

---

## 8. Final Quality Gate

送出前執行 `CHECKLIST.md` 與 `loops/daily_report_quality_loop.yml`。

若任一硬性項目 fail：

```text
不得假裝完成。
必須在報告最上方標示 fail 項目。
可輸出「部分完成版」，但不得標示為完整每日報告。
```