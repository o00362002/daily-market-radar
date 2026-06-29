# Daily Market Radar｜AGENT_DEFINITION_MAP

本檔定義 `daily-market-radar` 中誰被視為 Agent、哪些只是 Workflow / Skill / Tool / Loop。

本 repo 目前不是正式 Agent runtime，而是 Level 2 Runtime-Lite 的每日市場情報雷達系統。

Agent map 用來讓執行順序可讀、可檢查、可掛載，不代表升級成 Level 3B。

---

## 1. Agent 判斷公式

```text
完整情報任務目標 → Agent
固定情報流程 → Workflow
可重複判斷能力 → Skill
搜尋、讀取、檢查、格式化操作 → Tool
檢查、去重、回測、人工審核 → Loop
```

---

## 2. Primary Agent

### radar_report_agent

| 欄位 | 內容 |
|---|---|
| name | `radar_report_agent` |
| purpose | 產出每日市場雷達報告，並確保搜尋、主張風險、覆蓋率、格式與回測紀錄可檢查 |
| workflow | `workflows/daily_radar_workflow.md` |
| skills | `signal_search_skill`, `claim_risk_check_skill`, `coverage_check_skill`, `report_formatting_skill` |
| tools | `signal_search_tool`, `claim_risk_checker`, `coverage_checker`, `report_formatter` |
| loops | `missed_case_backtest_loop` |
| outputs | `reports/YYYY/YYYY-MM-DD.md`, `reports/backtests/` when needed |
| failure_mode | 若工具鏈任一必要步驟未完成，只能標記 `partial change` |

---

## 3. Required execution order

```text
1. signal_search_tool
2. claim_risk_checker
3. coverage_checker
4. report_formatter
5. missed_case_backtest_loop, if missed case / adjustment evidence exists
```

Do not run `report_formatter` before `claim_risk_checker` and `coverage_checker` are complete.

---

## 4. Supporting Radar Agents

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

## 5. Non-Agent List

| 名稱 | 目前身份 | 原因 |
|---|---|---|
| `configs/` | Rules / Configs | 定義規格，不是任務執行角色 |
| `memory/watchlist.md` | Memory / Watchlist | 觀察清單，不是 Agent |
| `memory/missed_cases.md` | Loop Memory | 漏抓回測資料，不是 Agent |
| `templates/` | Output Template | 輸出格式，不做判斷 |
| `reports/` | Report Archive | 歷史報告，不是 Agent |
| Web search | Tool | 搜尋操作，不等於情報判斷 |

---

## 6. Execution evidence

Every completed report should be able to answer:

```text
Read set:
Signals searched:
signal_search_tool complete? yes / no
claim_risk_checker complete? yes / no
coverage_checker complete? yes / no
report_formatter complete? yes / no
Backtest / adjustment needed? yes / no
Status: complete / partial change / No downstream sync required
```

---

## 7. Boundary Rule

不要把每個雷達指標都升級成 Agent。Agent 應負責完整情報目標，指標、搜尋語、模板與報告欄位應維持 Skill / Tool / Config / Loop。
