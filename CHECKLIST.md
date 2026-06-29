# daily-market-radar｜CHECKLIST

本檔是每日市場情報輸出前的硬性檢查表。

---

## 1. Preflight Context Checklist

| Check | Required | Pass / Fail |
|---|---:|---|
| 已讀 `SYSTEM_PROMPT.md` | yes |  |
| 已讀 `README.md` | yes |  |
| 已讀 `PROJECT_MAP.md` / `HIGH_LEVEL_INDEX.md` | yes |  |
| 已讀 `CURRENT_STATE.md` / `CURRENT_DECISIONS.md` | yes |  |
| 已讀 `CONTEXT_ROUTING.md` / `RUNBOOK.md` / `CHECKLIST.md` | yes |  |
| 已讀核心 configs | yes |  |
| 已讀 `memory/missed_cases.md` / `memory/watchlist.md` | yes |  |
| 已讀 `reports/INDEX.md` | yes |  |
| 已嘗試讀近期 `reports/YYYY/YYYY-MM-DD.md` | yes |  |
| 已讀 templates | yes |  |

---

## 2. Output Checklist

| Check | Required | Pass / Fail |
|---|---:|---|
| 報告最上方有資料讀取狀態 | yes |  |
| 有今日雷達覆蓋矩陣 | yes |  |
| 有固定指標追蹤總表 | yes |  |
| 有 3–5 個潛力架構 / 早期敘事候選 | yes |  |
| 有至少 5 則 edge cases | yes |  |
| edge cases 至少涵蓋 3 領域 | yes |  |
| 每個 edge case 有證據等級與不能下的結論 | yes |  |
| 無資料雷達有 retry 狀態 | yes |  |
| 每個主領域有台灣映射或台灣資料缺口 | yes |  |
| 有舊版 / 新版補漏比對 | yes |  |
| 有推播後回測與模型調整面板 | yes |  |

---

## 3. Search Retry Checklist

若任何雷達出現以下情況，必須啟動 retry：

```text
無重大訊號
只有主流新聞
只有英文主流媒體
只有大公司新聞
沒有特殊應用 / 邊緣案例候選
使用者曾指出同類漏抓
```

每個觸發 retry 的雷達至少記錄 3 種方法：

```text
change_keywords
change_language
change_source_type
change_level
change_time_window
search_negative_space
search_metrics_instead_of_news
```

---

## 4. Fail Rule

```text
硬性項目 fail 時，不得輸出「完整每日市場情報報告」。
只能輸出「部分完成版」，並列出 fail 項目、原因、補救方式。
```

---

## 5. Minimal Completion Definition

每日報告最低完成標準：

```text
context loaded or failure disclosed
indicator tracking present
edge case discovery present
search retry status present
Taiwan mapping present
post-report review present
```

少任一項即為 partial。