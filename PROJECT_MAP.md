# Daily Market Radar｜PROJECT_MAP

本檔是每日播報系統的專案導航圖，用來讓 AI 在回答或產出報告前，先建立完整上下文。

> 原則：本檔只負責導航，不改寫核心規格。核心規格仍以 `SYSTEM_PROMPT.md`、`configs/`、`memory/`、`templates/`、`reports/` 為準。

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
3. `CURRENT_STATE.md`
4. `CURRENT_DECISIONS.md`
5. `configs/radars.yml`
6. `configs/triggers.yml`
7. `configs/evidence.yml`
8. `configs/source_strategy.md`
9. `configs/indicator_tracking.yml`
10. `configs/technology_development.yml`
11. `memory/missed_cases.md`
12. `memory/watchlist.md`
13. `reports/INDEX.md`
14. 近期 `reports/YYYY/YYYY-MM-DD.md`
15. `templates/daily_report_template.md`
16. `templates/final_synthesis_template.md`

若時間或工具限制無法全部讀取，必須明確標示「未完整讀取」，不得假裝已讀取。

---

## 3. 資料夾職責

| 路徑 | 職責 | 使用時機 |
|---|---|---|
| `SYSTEM_PROMPT.md` | 核心任務、輸出規格、硬性規則 | 每次報告與規格討論必讀 |
| `PROJECT_MAP.md` | 專案導航與讀取順序 | 每次進入 repo 時先讀 |
| `CURRENT_STATE.md` | 目前版本、最新狀態、有效規格摘要 | 判斷現在該用哪套規格 |
| `CURRENT_DECISIONS.md` | 最近決策、已修正錯誤、不可再犯事項 | 避免回覆回到舊邏輯 |
| `configs/` | 雷達、觸發器、證據、來源、指標、科技路徑 | 執行每日掃描與調整雷達 |
| `memory/` | 漏抓案例、觀察清單、使用者要求 | 做硬檢查與回測 |
| `templates/` | 每日報告與最終彙總格式 | 產出報告時套用 |
| `reports/` | 歷史報告與跨日去重依據 | 產出新報告前檢查 |
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

## 5. 回答品質檢查 Loop

每次產出每日播報或回覆專案問題後，需做以下檢查：

1. 是否有先依讀取順序建立上下文？
2. 是否只回答單點，漏掉雷達系統整體脈絡？
3. 是否引用到舊規格或已修正錯誤？
4. 是否遺漏三桶硬檢查：加密潛力市場、零售/商圈/品牌變化、AI 實際應用？
5. 是否遺漏固定指標追蹤？
6. 是否遺漏科技發展與突破，尤其非 AI 科技突破？
7. 是否遺漏台灣逐領域對應？
8. 是否有來源、時間、證據分級與不確定性標示？
9. 是否有跨日去重與漏抓回測？
10. 是否有下一次如何降低資料缺口的調整建議？

---

## 6. 版本優先順序

回答時優先順序如下：

1. `CURRENT_DECISIONS.md` 的最新決策
2. `CURRENT_STATE.md` 的目前狀態
3. `SYSTEM_PROMPT.md` 的核心規格
4. `configs/` 的結構化設定
5. `memory/` 的漏抓與觀察清單
6. `templates/` 的輸出格式
7. `reports/` 的歷史案例
8. `archive/` 的歷史參考

若不同檔案衝突，應先標示衝突，再以較新的 `CURRENT_DECISIONS.md` 與 `CURRENT_STATE.md` 為準。