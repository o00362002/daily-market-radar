# Daily Market Radar

這個專案是「全球每日市場情報雷達系統」的版本控管中心，不是單純存放新聞摘要。

每日播報在執行前，應先讀取本 repo 的入口層、雷達清單、固定指標追蹤、科技發展雷達、特殊應用雷達、搜尋 retry 規則、漏抓案例、歷史報告與回測規則，再進行多語言搜尋與交叉驗證。

---

## 1. 核心定位

- 不是新聞摘要器。
- 不是只挑幾則主觀重要新聞的編輯。
- 不是只整理主流媒體已經大量報導的大眾新聞。
- 是一套「雷達覆蓋 + 固定指標追蹤 + 全球特殊應用搜尋 + 搜尋 retry + 證據分級 + 科技發展路徑 + 回測補漏」的每日市場情報系統。

目標是同時捕捉：

```text
全球大趨勢
資金與政策變化
產業結構變化
AI 工作流替代
AI 產品用量經濟
科技發展與突破
加密與鏈上資金流
零售、品牌、消費、社群、流行與服飾訊號
全球特殊應用、非主流案例、地方試點、早期商業模式、研究原型、開發者工具與社群弱訊號
台灣產業映射
舊版 / 新版播報補漏比對
全指標總和彙總結果
```

---

## 2. Human-AI Collaboration Brain 掛載定位

本 repo 以 `Human-AI-Collaboration-Brain` 作為架構來源，採 active thin mount。

```text
Level: Level 2 Runtime-Lite Brain
Role: recurring intelligence workflow / daily report system
Mother version: v1.18-draft
Mount mode: active thin mount
```

Source of truth：

```text
brain.manifest.yaml
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
DEPENDENCY_MAP.md
AGENT_DEFINITION_MAP.md
```

Projection files create no canonical rules. Frozen history is not current state.

---

## 3. 執行入口

AI 或協作者進入本 repo 時，先讀：

```text
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
README.md
AGENTS.md
brain.manifest.yaml
DEPENDENCY_MAP.md
AGENT_DEFINITION_MAP.md
```

再依任務讀取：

```text
configs/
memory/
templates/
reports/
workflows/
evals/
```

---

## 4. Frozen History

以下舊過渡檔只保留歷史脈絡，不再作為 current routing / source of truth / active rule：

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
```

---

## 5. Output mode routing

每日播報預設走輕量版。

一般說法如「每日播報」、「每日新聞」、「今天的每日新聞」、「播報今天的每日新聞」、「今日市場雷達」、「今天新聞」、「daily news」、「morning brief」、「daily push」，都路由到：

```text
AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ templates/daily_push_brief_template.md
```

只有使用者明確要求「正式版」、「完整版」、「完整正式版」、「Full Daily Radar」、「full report」、「complete report」、「archival report」、「48-signal report」、「5+3」、「完整硬閘門」、「歸檔版」、「產出 reports/YYYY/YYYY-MM-DD.md」時，才路由到：

```text
AGENT_RADAR_REPORT
→ workflows/daily_radar_workflow.md
→ templates/daily_report_template.md
```

若語意不明，預設選 `AGENT_DAILY_PUSH_BRIEF`，並標示：

```text
輸出模式：每日推播精簡版。
完整 48 則正式閘門：未嘗試 / 另需分段研究版。
```

---

## 6. 每日執行順序

1. 讀取入口檔。
2. 依 `AGENT_DEFINITION_MAP.md` 選擇 route。
3. 一般每日播報使用 `workflows/daily_push_brief_workflow.md`。
4. 明確正式版才使用 `workflows/daily_radar_workflow.md`。
5. 讀取 `configs/`、`memory/`、近期 `reports/` 與 active template。
6. 產出時必須標示輸出模式、資料缺口、是否建議升級正式版、今日最終一句話。

---

## 7. 重要規則

- 若資料不足，必須寫「資料不足」。
- 若因果未確認，只能寫「產業訊號」或「待驗證推論」。
- 候選訊號不得因證據不足被刪除。
- 社群討論可列為潛力候選，但必須標示未證實、證據等級、原始連結、官方確認狀態或反向證據。
- 使用者指出的漏抓事件，必須進入 `memory/missed_cases.md` 的硬檢查清單。
- 跨領域事件必須標示受影響的所有雷達。
- 同一週內已播報事件需跨日去重；無新資訊不重播。
- 每日推播精簡版必須輸出固定指標濃縮表與六領域覆蓋矩陣。
- 每日推播精簡版不需要完整 48 則正式閘門；正式版才需要完整硬閘門。
- 報告最後必須輸出資料缺口、是否建議升級正式版、今日最終一句話。

---

## 8. Backtest / Growth Control

Backtest 不只檢查報告成果，也檢查專案是否需要：

```text
keep / revise / delete / archive / add / promote / demote
```

新增規則、模板、workflow 或報告欄位前，先檢查能否用凍結歷史、指回 Core、降權 Projection 或刪減重複段落解決。

---

## 9. 報告索引

完整索引詳見：`reports/INDEX.md`

正式版每日報告建議放在：

```text
reports/YYYY/YYYY-MM-DD.md
```

每日推播精簡版若未要求歸檔，不需要寫入 `reports/`。
