# Daily Market Radar｜PROJECT_MAP

本檔是每日播報系統的專案導航圖，用來讓 AI 在回答或產出報告前，先建立完整上下文。

> 原則：本檔只負責導航，不改寫核心規格。核心規格仍以 `SYSTEM_PROMPT.md`、`HIGH_LEVEL_INDEX.md`、`ADOPTION_LEVELS.md`、`configs/`、`memory/`、`templates/`、`reports/` 為準。

---

## 1. 專案定位

`daily-market-radar` 是「全球每日市場情報雷達系統」的版本控管中心。

目前採用：

```text
Repo Level 2：Long-term AI Project
```

它不是一般新聞摘要資料夾，而是一套每日執行的情報作業系統，包含：

- 雷達覆蓋
- 多語言搜尋
- 來源交叉驗證
- 證據分級
- 固定指標追蹤
- 科技發展路徑
- 漏抓回測
- 舊版 / 新版補漏比對
- 台灣逐領域映射
- 最終趨勢判斷

---

## 2. 回答前固定讀取順序

任何每日播報、規格修改、漏抓檢討、雷達調整、模板修正，都應依序讀取：

1. `SYSTEM_PROMPT.md`
2. `PROJECT_MAP.md`
3. `HIGH_LEVEL_INDEX.md`
4. `CURRENT_STATE.md`
5. `CURRENT_DECISIONS.md`
6. `ADOPTION_LEVELS.md`
7. `configs/radars.yml`
8. `configs/triggers.yml`
9. `configs/evidence.yml`
10. `configs/source_strategy.md`
11. `configs/indicator_tracking.yml`
12. `configs/technology_development.yml`
13. `memory/missed_cases.md`
14. `memory/watchlist.md`
15. `reports/INDEX.md`
16. 近期 `reports/YYYY/YYYY-MM-DD.md`
17. `templates/daily_report_template.md`
18. `templates/final_synthesis_template.md`

若時間或工具限制無法全部讀取，必須明確標示「未完整讀取」，不得假裝已讀取。

---

## 3. 資料夾職責

| 路徑 | 職責 | 使用時機 |
|---|---|---|
| `SYSTEM_PROMPT.md` | 核心任務、輸出規格、硬性規則 | 每次報告與規格討論必讀 |
| `PROJECT_MAP.md` | 專案導航與讀取順序 | 每次進入 repo 時先讀 |
| `HIGH_LEVEL_INDEX.md` | 高階脈絡索引，避免單點回答與漏雷達 | 每次建立全局上下文時必讀 |
| `CURRENT_STATE.md` | 目前版本、最新狀態、有效規格摘要 | 判斷現在該用哪套規格 |
| `CURRENT_DECISIONS.md` | 最近決策、已修正錯誤、不可再犯事項 | 避免回覆回到舊邏輯 |
| `ADOPTION_LEVELS.md` | Repo Level 2 與未來 Module Level 規則 | 判斷是否維持 Level 2 或局部 module 化 |
| `configs/` | 雷達、觸發器、證據、來源、指標、科技路徑 | 執行每日掃描與調整雷達 |
| `memory/` | 漏抓案例、觀察清單、使用者要求 | 做硬檢查與回測 |
| `templates/` | 每日報告與最終彙總格式 | 產出報告時套用 |
| `reports/` | 歷史報告與跨日去重依據 | 產出新報告前檢查 |
| `research/` | 方法論研究與公開參考；採納後才進正式規則 | 研究市場情報方法、來源策略、雷達改版時使用 |
| `archive/` | 舊版或停用資料 | 僅作歷史參考，不優先引用 |

---

## 4. 主要模組

### A. 全球市場與國際局勢

追蹤總體經濟、央行、利率、匯率、地緣政治、股債匯商品與市場風險。

### B. 全球資金流

追蹤 ETF、基金、風險資產、美元流動性、資金輪動、避險資金。
