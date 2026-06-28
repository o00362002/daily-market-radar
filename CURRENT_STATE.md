# Daily Market Radar｜CURRENT_STATE

本檔記錄每日播報系統的目前有效狀態。它是入口狀態檔，不取代 `SYSTEM_PROMPT.md`、`HIGH_LEVEL_INDEX.md` 與 `configs/`。

最後整理日期：2026-06-28

---

## 1. 目前狀態摘要

每日市場情報播報目前已升級為：

> 雷達覆蓋與證據分級型每日市場情報系統。

核心不再是列新聞，而是每天固定掃描多個雷達桶，標示訊號強弱、證據等級、資料缺口、台灣映射、跨日去重、漏抓回測與下一次修正方向。

---

## 2. Adoption Level

目前指定：

```text
Repo Level 2：Long-term AI Project
```

本 repo 維持 Level 2，不預設升級為 Agent / Product System。若未來新增 radar module、搜尋 retry module 或回測 module，應用 Module Level 管理，不直接把整個 repo 升成 Level 3。

---

## 3. 目前有效入口檔

每日執行前應優先讀取：

1. `SYSTEM_PROMPT.md`
2. `PROJECT_MAP.md`
3. `HIGH_LEVEL_INDEX.md`
4. `CURRENT_STATE.md`
5. `CURRENT_DECISIONS.md`
6. `ADOPTION_LEVELS.md`
7. `configs/`
8. `memory/`
9. `templates/`
10. `reports/`

---

## 4. 目前有效核心規格

- 多語言搜尋：至少英文、繁體中文、簡體中文。
- 優先官方資料、監管機構、公司公告、財報、交易所資料、鏈上資料、權威媒體、可信產業媒體與研究機構。
- 每則重要事件需盡量附來源、發布時間或事件時間。
- 證據分級必須清楚：高 / 中 / 低 / 資料不足。
- 不得把候選訊號刪除，應標示候選、未證實或資料不足。
- 無法確認因果時，只能寫「產業訊號」或「待驗證推論」。
- 每個主領域都要做台灣對應檢查。
- 每日需做跨日去重，避免重複播報。
- 每日需有推播後回測與模型調整面板。

---

## 5. 每日必掃主雷達

1. 全球市場與國際局勢
2. 全球資金流
3. 區塊鏈 / 加密貨幣
4. AI 模型、Agent 與企業應用
5. AI 工作流替代
6. 科技發展與突破
7. 科技發展過熱指標
8. 零售、品牌、消費、社群媒體、流行與服飾
9. 真分眾 vs 假分眾
10. 勞動與消費結構壓力
11. 台灣本地訊號總表與跨領域缺口

---

## 6. 三桶硬檢查

每日播報必須特別檢查三桶，不得省略。

### A. 加密潛力市場

- RWA
- tokenized stocks / pre-IPO
- AI agents x crypto
- x402 / agent payments
- Perp DEX
- Solana / Monad / Base / Hyperliquid 等生態
- 隱私幣與 ZK privacy
- ETF、OI、TVL、Fees、Revenue、Stablecoin 指標
- 交易所產品與新敘事

### B. 零售通路 / 商圈 / 品牌變化

- 街邊店
- 高街
- 百貨 / 購物中心
- 商圈洗牌
- 品牌展店 / 收店 / 旗艦店
- tenant mix
- 體驗型門市
- 台灣商場開幕與國際品牌動向
- OMO、CDP、CRM、LBS、Retail Media、AI 導購

### C. AI 實際應用

- AI Agent 客服
- 企業 Agent 導入
- 權限治理
- 身份管理
- MCP / 工具層
- 零售 / 客服 / BI / 營運 / 內容工作流
- AI 產品用量經濟：token、credit、quota、usage limit、pricing、promo code、gift / transfer、free trial、enterprise subsidy

---

## 7. 規格更新同步規則

之後任何規格、雷達、模板、記憶、漏抓、報告輸出格式有更新時，不能只改單一檔案，必須檢查是否需要同步修改以下檔案：

1. `SYSTEM_PROMPT.md`：是否影響核心指令、每日必讀檔、輸出規格、硬性規則。
2. `PROJECT_MAP.md`：是否影響專案地圖、資料夾職責、讀取順序、模組分類。
3. `HIGH_LEVEL_INDEX.md`：是否影響高階脈絡、核心雷達、易漏面向與不可誤判事項。
4. `CURRENT_STATE.md`：是否影響目前有效版本、目前狀態、每日必掃雷達、三桶硬檢查。
5. `CURRENT_DECISIONS.md`：是否需要新增最近決策、廢止舊規則、記錄不可再犯錯誤。
6. `ADOPTION_LEVELS.md`：是否影響 Repo Level 或 Module Level。
7. `configs/`：是否需要新增或調整雷達、觸發器、證據分級、來源策略、固定指標、科技發展路徑。
8. `templates/`：是否需要調整每日報告格式、最終彙總格式、回測面板格式。
9. `memory/`：是否需要新增漏抓案例、watchlist、硬檢查清單。
10. `reports/INDEX.md`：若新增報告或重要回測，是否需要更新索引。
11. `reports/`：是否需要讓新報告呈現更新後規格。
12. `research/`：若是方法論研究或公開參考，是否先放入研究層再決定是否採納。
13. `archive/`：若有舊規格停用，是否需要移入或標註歷史參考。
