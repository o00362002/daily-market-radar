# Daily Market Radar｜Agent Definition Map

本檔定義 `daily-market-radar` 中誰被視為 Agent、哪些只是 Workflow / Skill / Tool / Loop。

本 repo 目前不是正式 Agent runtime，而是每日市場情報雷達系統的規格與報告作業中心。

---

## Agent 判斷公式

```text
完整情報任務目標 → Agent
固定情報流程 → Workflow
可重複判斷能力 → Skill
搜尋、讀取、匯總操作 → Tool
檢查、去重、回測、人工審核 → Loop
```

---

## Agents

| Agent | 定位 | 為什麼是 Agent |
|---|---|---|
| Radar Orchestrator Agent | 每日情報總入口與任務分派 | 負責決定今日要跑哪些雷達、缺口與報告結構 |
| Global Market Agent | 全球市場、資金流、政策與地緣政治 | 有獨立搜尋範圍、指標與輸出段落 |
| Crypto Radar Agent | 加密、鏈上、ETF、RWA、Perp DEX、AI x crypto | 有專屬 watchlist、指標與弱訊號判斷 |
| AI Application Agent | AI 實際應用、Agent、工具層、企業導入 | 負責避免 AI 段落只剩模型 / 基建新聞 |
| Technology Breakthrough Agent | 科技發展與突破 | 獨立追蹤 AI 與非 AI 科技突破 |
| Retail Trend Agent | 零售、品牌、百貨、商圈、社群商務、服飾趨勢 | 服務使用者零售營運與商業化觀察 |
| Taiwan Mapping Agent | 台灣逐領域映射 | 把全球訊號轉成台灣產業關聯與資料缺口 |
| Report Assembly Agent | 報告組裝與格式輸出 | 將各雷達結果組成每日報告與最終綜合判斷 |

---

## Non-Agent List

| 名稱 | 目前身份 | 原因 |
|---|---|---|
| `configs/` | Rules / Configs | 定義規格，不是任務執行角色 |
| `memory/watchlist.md` | Memory / Watchlist | 觀察清單，不是 Agent |
| `memory/missed_cases.md` | Loop Memory | 漏抓回測資料，不是 Agent |
| `templates/` | Output Template | 輸出格式，不做判斷 |
| `reports/` | Report Archive | 歷史報告，不是 Agent |
| Web search | Tool | 搜尋操作，不等於情報判斷 |

---

## Upgrade Candidates

| Candidate | 目前身份 | 升級條件 |
|---|---|---|
| Edge Case Discovery Agent | Workflow candidate | 若全球特殊應用搜尋成為獨立雷達與回測閉環，可升級 |
| Source Quality Agent | Loop candidate | 若來源可信度評估獨立管理，可升級 |
| Indicator Tracking Agent | Workflow candidate | 若固定指標自動化與異常偵測成熟，可升級 |

---

## Boundary Rule

不要把每個雷達指標都升級成 Agent。Agent 應負責完整情報目標，指標、搜尋語、模板與報告欄位應維持 Skill / Tool / Config / Loop。