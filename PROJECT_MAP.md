# Daily Market Radar｜PROJECT_MAP

本檔是每日播報系統的專案導航圖，用來讓 AI 在回答或產出報告前，先建立完整上下文。

> 原則：本檔只負責導航，不改寫核心規格。核心規格仍以 `SYSTEM_PROMPT.md`、`HIGH_LEVEL_INDEX.md`、`configs/`、`memory/`、`templates/`、`reports/` 為準。

---

## 1. 專案定位

`daily-market-radar` 是「全球每日市場情報雷達系統」的版本控管中心。

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
6. `configs/radars.yml`
7. `configs/triggers.yml`
8. `configs/evidence.yml`
9. `configs/source_strategy.md`
10. `configs/indicator_tracking.yml`
11. `configs/technology_development.yml`
12. `memory/missed_cases.md`
13. `memory/watchlist.md`
14. `reports/INDEX.md`
15. 近期 `reports/YYYY/YYYY-MM-DD.md`
16. `templates/daily_report_template.md`
17. `templates/final_synthesis_template.md`

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

### C. 加密與區塊鏈

追蹤 BTC / ETH ETF、穩定幣、Perp DEX、RWA、tokenized stocks / pre-IPO、AI agents x crypto、x402 / agent payments、潛力鏈生態與鏈上指標。

### D. AI 模型、Agent 與企業應用

追蹤模型、Agent、企業導入、工作流替代、權限治理、成本、token / credit / quota / pricing / usage limit。

### E. 科技發展與突破

獨立主雷達。包含 AI 驅動突破與非 AI 的單獨科技突破，例如生物、物理、化學、材料、能源、機器人、半導體、醫療、製造、太空、量子。

### F. 零售、品牌、消費、社群、流行與服飾

追蹤百貨、購物中心、街邊店、OMO、CDP、CRM、LBS、Retail Media、AI 導購、社群商務、KOL 轉銷售平台、服飾與消費分化。

### G. 勞動與消費結構壓力

追蹤就業、薪資、消費信心、K 型經濟、職能替代、消費降級與實體零售影響。

### H. 台灣本地映射

每個主領域都必須檢查台灣本地訊號、產業關聯、資料缺口與下一步查證。

---

## 5. 規則更新同步檢查

任何規則更新都不能只改單一檔案。更新前後必須檢查下列同步關係：

| 更新類型 | 必須同步檢查 |
|---|---|
| 新增或刪除雷達分類 | `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`configs/radars.yml`、`templates/daily_report_template.md`、`README.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` |
| 新增跨領域觸發器 | `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`configs/triggers.yml`、`templates/daily_report_template.md`、`CURRENT_DECISIONS.md` |
| 修改證據分級 | `SYSTEM_PROMPT.md`、`configs/evidence.yml`、`templates/`、`CURRENT_DECISIONS.md` |
| 新增固定指標 | `SYSTEM_PROMPT.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`configs/indicator_tracking.yml`、`templates/daily_report_template.md`、`CURRENT_DECISIONS.md` |
| 新增科技發展追蹤規則 | `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`configs/technology_development.yml`、`templates/final_synthesis_template.md`、`CURRENT_DECISIONS.md` |
| 使用者指出漏抓 | `memory/missed_cases.md`、`memory/watchlist.md`、必要時更新 `HIGH_LEVEL_INDEX.md`、`configs/`、`templates/`、`CURRENT_DECISIONS.md` |
| 報告格式調整 | `templates/`、`SYSTEM_PROMPT.md`、`README.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` |
| 歷史報告新增 | `reports/YYYY/YYYY-MM-DD.md`、`reports/INDEX.md`、必要時更新 `CURRENT_STATE.md` |
| 舊規格停用 | `archive/` 或原檔標註、`CURRENT_DECISIONS.md`、必要時更新 `CURRENT_STATE.md`、`HIGH_LEVEL_INDEX.md` |

---

## 6. AI Project OS 採用狀態

本 repo 已採用 `Reference-Implementation-of-AI-Project-Operating-System` 的核心入口層：

```text
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
README.md
```

後續任何新增研究、規格或雷達改版，都應先判斷是否影響 `HIGH_LEVEL_INDEX.md` 與同步規則。