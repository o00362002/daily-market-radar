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

## 5. 每日執行順序

1. 讀取入口檔。
2. 讀取 `configs/radars.yml`。
3. 讀取 `configs/triggers.yml`。
4. 讀取 `configs/evidence.yml`。
5. 讀取 `configs/source_strategy.md`。
6. 讀取 `configs/indicator_tracking.yml`。
7. 讀取 `configs/technology_development.yml`。
8. 讀取 `configs/edge_case_discovery.yml`。
9. 讀取 `configs/search_retry_protocol.yml`。
10. 讀取 `memory/missed_cases.md` 與 `memory/watchlist.md`。
11. 讀取近期 `reports/` 內的歷史報告，避免跨日重複與漏抓。
12. 使用 `templates/daily_report_template.md` 產出每日報告。
13. 使用 `templates/final_synthesis_template.md` 產出最後總和彙總、舊版 / 新版比對、科技發展路徑判斷。
14. 報告最後更新推播後回測與模型調整面板。

---

## 6. 重要規則

- 若資料不足，必須寫「資料不足」。
- 若因果未確認，只能寫「產業訊號」或「待驗證推論」。
- 候選訊號不得因證據不足被刪除。
- 社群討論可列為潛力候選，但必須標示未證實、證據等級、原始連結、官方確認狀態或反向證據。
- 使用者指出的漏抓事件，必須進入 `memory/missed_cases.md` 的硬檢查清單。
- 跨領域事件必須標示受影響的所有雷達。
- 同一週內已播報事件需跨日去重；無新資訊不重播。
- 每日必須輸出固定指標追蹤總表；即使資料不足，也要標示資料缺口，不得省略。
- 每日必須輸出「科技發展與突破」段落，並分成「AI 驅動突破」與「非 AI / 單獨科技突破」。
- 每日必須輸出至少 5 則全球特殊應用 / 邊緣案例候選，且至少涵蓋 3 個不同領域。
- 若某雷達只抓到主流新聞或無資料，必須依 `configs/search_retry_protocol.yml` 至少換 3 種搜尋方法後，才可標示資料不足。
- 報告最後必須輸出舊版 / 新版補漏比對、全指標總和彙總、科技發展路徑判斷、搜尋 retry 狀態與今日最終一句話。

---

## 7. Backtest / Growth Control

Backtest 不只檢查報告成果，也檢查專案是否需要：

```text
keep / revise / delete / archive / add / promote / demote
```

新增規則、模板、workflow 或報告欄位前，先檢查能否用凍結歷史、指回 Core、降權 Projection 或刪減重複段落解決。

---

## 8. 報告索引

完整索引詳見：`reports/INDEX.md`

每日報告建議放在：

```text
reports/YYYY/YYYY-MM-DD.md
```
