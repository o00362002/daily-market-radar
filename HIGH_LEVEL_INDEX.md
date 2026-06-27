# Daily Market Radar｜HIGH_LEVEL_INDEX

本檔是 `daily-market-radar` 的高階索引，用來讓 AI 在產出每日市場情報或回答規格問題前，先建立完整脈絡。

---

## 1. 一句話定位

`daily-market-radar` 是一套「全球每日市場情報雷達系統」，不是新聞摘要器，而是用雷達覆蓋、固定指標、證據分級、漏抓回測與台灣映射來產出每日情報。

---

## 2. 核心目標

- 每日掃描全球市場、AI、加密、零售、科技突破、勞動與消費結構。
- 避免只挑主觀重要新聞，改用雷達覆蓋檢查。
- 保留弱訊號與候選訊號，但標示證據等級。
- 對使用者的零售、AI 工具化、加密觀察與職能發展提供可行動提醒。
- 透過漏抓回測與同步規則持續改善。

---

## 3. 核心雷達模組

| 模組 | 作用 | 詳細資料位置 |
|---|---|---|
| 全球市場與國際局勢 | 追蹤總體、央行、利率、匯率、地緣政治 | `SYSTEM_PROMPT.md`、`configs/radars.yml` |
| 全球資金流 | 追蹤 ETF、基金、美元流動性、風險資產輪動 | `configs/indicator_tracking.yml` |
| 加密與區塊鏈 | 追蹤 ETF、穩定幣、RWA、Perp DEX、AI x crypto、潛力鏈 | `configs/radars.yml`、`memory/watchlist.md` |
| AI 模型、Agent 與企業應用 | 追蹤模型、Agent、工作流替代、企業導入、用量經濟 | `configs/triggers.yml`、`configs/indicator_tracking.yml` |
| 科技發展與突破 | 獨立主雷達，追蹤 AI 與非 AI 科技突破 | `configs/technology_development.yml` |
| 零售、品牌、消費、社群與服飾 | 追蹤百貨、商圈、品牌展撤店、OMO、社群商務、服飾趨勢 | `configs/radars.yml`、`memory/watchlist.md` |
| 台灣逐領域映射 | 每個主領域都要檢查台灣本地訊號、產業關聯與資料缺口 | `SYSTEM_PROMPT.md`、`templates/` |
| 漏抓回測 | 記錄漏抓案例、下次硬檢查與搜尋調整 | `memory/missed_cases.md` |

---

## 4. 回答時必須考慮的面向

- 這不是新聞摘要，而是雷達覆蓋與證據分級系統。
- 固定三桶硬檢查不可漏：加密潛力市場、零售通路 / 商圈 / 品牌變化、AI 實際應用。
- AI 段落不能只寫模型或基建，必須檢查企業應用、Agent、工作流與用量經濟。
- 零售段落不能只寫宏觀消費，必須檢查百貨、街邊店、商圈、品牌、社群商務與服飾。
- 科技發展與突破是獨立主雷達，不可併入 AI 公司新聞。
- 每個主領域都需要台灣對應檢查。
- 無資料也要標示資料缺口與下次降低缺口的方法。

---

## 5. 容易遺漏的面向

- 只看新聞熱度，沒有做固定雷達覆蓋。
- AI 段落被模型發布、晶片或融資新聞吃掉，漏掉實際應用。
- 零售段落只談消費數據，漏掉百貨、商圈與品牌展撤店。
- 加密段落只看 BTC / ETH，漏掉 RWA、tokenized stocks、Perp DEX、AI agents x crypto、x402。
- 科技突破只寫 AI，不檢查非 AI 科技突破。
- 台灣映射只放最後一段，沒有逐領域檢查。
- 使用舊報告重複播報，沒有跨日去重。

---

## 6. 不可誤判事項

- 不得把低證據社群討論寫成已確認事實。
- 不得因資料不足就刪掉候選訊號，應標示證據等級。
- 不得假裝已讀取 repo 檔案。
- 不得把 `archive/` 或舊報告當成最新規則。
- 不得忽略 `CURRENT_DECISIONS.md` 的最新硬檢查。

---

## 7. 詳細資料位置

| 類型 | 路徑 |
|---|---|
| 最高規格 | `SYSTEM_PROMPT.md` |
| 專案導航 | `PROJECT_MAP.md` |
| 目前狀態 | `CURRENT_STATE.md` |
| 最新決策 | `CURRENT_DECISIONS.md` |
| 雷達與觸發器 | `configs/` |
| 漏抓與觀察清單 | `memory/` |
| 報告模板 | `templates/` |
| 歷史報告 | `reports/` |
| 舊版參考 | `archive/` |
