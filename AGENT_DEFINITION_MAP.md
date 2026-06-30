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

## 2. Agent Router

詳細路由規則見：

```text
ROUTING.md
```

簡化規則：

```text
每日市場情報 / 全域雷達 → radar_report_agent
每日推播精簡版 → radar_report_agent + daily_push_brief_workflow
指定主題新聞搜尋 → news_search_agent
已選新聞 / 已分級訊號改寫與深化 → news_content_agent
```

---

## 3. Primary Agent

### radar_report_agent

| 欄位 | 內容 |
|---|---|
| name | `radar_report_agent` |
| purpose | 產出每日市場雷達報告，並確保搜尋、主張風險、覆蓋率、格式與回測紀錄可檢查 |
| full workflow | `workflows/daily_radar_workflow.md` |
| concise workflow | `workflows/daily_push_brief_workflow.md` |
| full template | `templates/daily_report_template.md` |
| concise template | `templates/daily_push_brief_template.md` |
| skills | `signal_search_skill`, `claim_risk_check_skill`, `coverage_check_skill`, `report_formatting_skill` |
| tools | `signal_search_tool`, `claim_risk_checker`, `coverage_checker`, `report_formatter` |
| loops | `missed_case_backtest_loop` |
| outputs | `reports/YYYY/YYYY-MM-DD.md`, `reports/backtests/` when needed |
| failure_mode | 若工具鏈任一必要步驟未完成，只能標記 `partial change`；若使用精簡版，需明確標示 `每日推播精簡版`，不得宣稱通過完整 48 則正式閘門 |

---

## 4. News Search Agent

### news_search_agent

| 欄位 | 內容 |
|---|---|
| name | `news_search_agent` |
| purpose | 搜尋指定主題的最新新聞，進行來源檢查、證據分級、重要度排序、台灣 / 使用者映射，並可直接輸出主題新聞報告 |
| input | 使用者指定主題，例如科技新聞、AI 新聞、零售新聞、加密新聞、台灣百貨新聞、某公司 / 某政策 / 某事件 |
| workflow | `workflows/news_search_content_workflow.md` |
| template | `templates/news_search_content_template.md` |
| outputs | 聊天輸出，或 `content/YYYY/YYYY-MM-DD-*-search.md` when needed |
| boundary | 不負責完整 daily market radar，不必覆蓋 6 大領域；但需對指定主題做搜尋、來源時間、證據分級與資料缺口揭露 |
| failure_mode | 若搜尋未完整或來源不足，標示 `news search partial`；不得把低證據或查無來源的內容寫成事實 |

使用時機：

```text
1. 使用者問「今天科技新聞」「AI 新聞」「零售新聞」「加密新聞」。
2. 使用者指定單一主題，需要最新資訊與來源。
3. 使用者需要一份可獨立閱讀的主題新聞摘要，而不是完整市場雷達。
```

---

## 5. Content Agent

### news_content_agent

| 欄位 | 內容 |
|---|---|
| name | `news_content_agent` |
| purpose | 將已確認或已標示證據等級的新聞 / 雷達訊號，改寫成可讀新聞內容、趨勢短文、社群素材或文章草稿 |
| input | `radar_report_agent` 或 `news_search_agent` 產出的已確認訊號、候選訊號、台灣映射、資料缺口，或使用者提供的新聞來源 |
| workflow | `workflows/news_content_workflow.md` |
| template | `templates/news_content_template.md` |
| outputs | `content/YYYY/YYYY-MM-DD-*.md` 或聊天輸出 |
| boundary | 不負責全域搜尋、不負責判定訊號是否真實、不把低證據候選寫成事實、不取代 radar_report_agent 或 news_search_agent |
| failure_mode | 若來源訊號證據不足，必須標示為候選 / 待驗證，不得包裝成確定新聞 |

使用時機：

```text
1. 每日雷達已產出後，要轉成短文 / 新聞稿 / 社群貼文。
2. 使用者指定某一則訊號，要整理成詳細內容。
3. 需要為「零售不靠感覺啦」或其他內容專案產出可讀素材。
```

---

## 6. Required execution order for radar_report_agent

完整研究版：

```text
1. signal_search_tool
2. claim_risk_checker
3. coverage_checker
4. report_formatter
5. missed_case_backtest_loop, if missed case / adjustment evidence exists
```

精簡推播版：

```text
1. Entry read
2. Load radar context
3. Scan six core domains
4. Produce 2–3 major signals per domain
5. Produce 1 niche candidate per domain
6. Add Taiwan mapping under each domain
7. Add retail focus block
8. Add data gaps and post-brief review
```

Do not run `report_formatter` before `claim_risk_checker` and `coverage_checker` are complete in full report mode.

---

## 7. Required execution order for news_search_agent

```text
1. Identify requested topic and scope.
2. Read minimal repo context and evidence policy.
3. Search current sources in relevant languages.
4. Cross-check important claims with source type and source time.
5. Separate major news, potential / niche signals, background, and insufficient data.
6. Rank by relevance to the user's topic.
7. Add Taiwan / user relevance when meaningful.
8. Output topic news report.
9. Suggest whether to hand off to news_content_agent for deeper content.
```

---

## 8. Required execution order for news_content_agent

```text
1. Receive selected radar signal, news search output, or user-provided source.
2. Check source status and evidence label.
3. Choose content format: news brief / trend note / social post / article draft / retail angle.
4. Rewrite for readability without changing claim strength.
5. Preserve uncertainty labels and source notes.
6. Output content draft.
```

---

## 9. Supporting Radar Agents

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
| News Search Agent | 指定主題新聞搜尋與分級 | 可單獨搜尋科技、AI、零售、加密、台灣商業等主題新聞 |
| News Content Agent | 新聞內容與社群素材產出 | 將已分級訊號轉成可讀內容，但不負責搜尋與證據判定 |

---

## 10. Non-Agent List

| 名稱 | 目前身份 | 原因 |
|---|---|---|
| `configs/` | Rules / Configs | 定義規格，不是任務執行角色 |
| `memory/watchlist.md` | Memory / Watchlist | 觀察清單，不是 Agent |
| `memory/missed_cases.md` | Loop Memory | 漏抓回測資料，不是 Agent |
| `templates/` | Output Template | 輸出格式，不做判斷 |
| `reports/` | Report Archive | 歷史報告，不是 Agent |
| Web search | Tool | 搜尋操作，不等於情報判斷 |
| `ROUTING.md` | Routing guide | 路由規則，不是 Agent |

---

## 11. Execution evidence

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

For concise push brief, also answer:

```text
Mode: Daily Push Brief
Six domains covered? yes / no
Taiwan mapping under each domain? yes / no
Retail focus block present? yes / no
Full 48-signal gate attempted? yes / no
Status: concise complete / partial concise brief
```

For news search output, also answer:

```text
Requested topic:
Search mode:
Sources searched:
Claims labelled? yes / no
Taiwan / user relevance included? yes / no
Status: news search complete / news search partial
```

For news content output, also answer:

```text
Input signal source:
Evidence label preserved? yes / no
Uncertainty preserved? yes / no
Content type:
Status: draft / ready for review
```

---

## 12. Boundary Rule

不要把每個雷達指標都升級成 Agent。Agent 應負責完整情報目標，指標、搜尋語、模板與報告欄位應維持 Skill / Tool / Config / Loop。

`news_search_agent` 不得替代 `radar_report_agent`。指定主題新聞搜尋不等於完整每日市場雷達。

`news_content_agent` 不得替代 `radar_report_agent` 或 `news_search_agent`。內容好讀不代表訊號已驗證。