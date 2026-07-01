# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-07-01

---

## 2026-07-01：Adopt mother Brain Post-Execution Backtest-to-Memory Flow

This child repo follows the mother Brain post-execution governance flow.

Canonical mother Brain references:

```text
Human-AI-Collaboration-Brain/MEMORY_UPDATE_POLICY.md
Human-AI-Collaboration-Brain/loops/backtest_improvement_loop.md
Human-AI-Collaboration-Brain/templates/BACKTEST_CHECK_TEMPLATE.md
Human-AI-Collaboration-Brain/CHILD_REPO_MOUNTS.md
```

Local flow:

```text
Execution Loop
→ Post-Execution Record
→ Backtest Evidence Loop
→ Failure Attribution
→ Dependency / Sync Impact Check
→ Memory Patch Candidate
→ Local Project Brain Update or Mother Brain sync candidate
→ Human / Decision Gate when required
```

Rules:

```text
Evidence is not durable memory by default.
Local evidence should stay in this repo, normally under reports/backtests/ or the repo's equivalent evidence path.
Local radar learnings should stay local unless they affect cross-repo governance, source-of-truth boundary, reusable governance rule, or mother Brain memory policy.
Memory Patch Candidate must not be merged into durable source of truth without review.
```

Multi-agent / model-brain rule:

```text
Agents do not share hidden reasoning.
Agents coordinate through externalized state, local decisions, dependency maps, backtest evidence, and Memory Patch Candidates.
```

---

## 2026-06-29：外部模型回測紀錄，不調整架構

### Decision

新增模型回測紀錄：

```text
memory/model_backtests.md
```

本次只記錄 Gemini / Grok 快速模型測試結果，不新增新的流程鎖，不調整核心報告設計，不把本次測試視為正式播報成果。

重要修正：先前一份被誤判為 Claude 快速回答的樣本，經使用者更正，實際上仍為 Gemini 產出。因此目前不能把該樣本列為 Claude 表現；Claude 尚未有獨立有效樣本，不應下結論。

### Reason

使用者指出目前根本問題不是再增加複雜度，而是要先看清楚：LLM 會把 repo 規則當成方向與寫作參考，但不一定會像程式一樣精確執行。

本次多模型測試顯示：

```text
Gemini：方向感、敘事能力與弱訊號探索較強，但容易硬給完整報告感，且高風險 claim 多。
Grok：比較願意承認搜尋未完整與硬閘門未通過，但內容密度低、偏泛。
Claude：目前尚未有獨立樣本，不能評估。
```

更精準的模型能力判斷：

```text
免費 / 快速模型通常只能吸收架構局部。
能力不足時，有些模型會誠實降級，有些模型會硬給漂亮答案。
```

### Result

已新增：

```text
memory/model_backtests.md
```

目前對 daily-market-radar 的修正理解：

```text
daily-market-radar repo 可以讓 AI 朝正確情報方向前進，
但不能保證 AI 像程式一樣精確照程序執行。
```

目前暫不調整架構設計。下一階段若要提升可靠度，應優先思考：

```text
AI 負責探索、推論、產出草稿。
程式 / validator 負責檢查格式、數量、硬閘門與高風險 claim。
人負責最終採用與規則修正。
```

---

## 2026-06-29：每日執行最小閘門測試版

### Decision

新增測試版最小執行閘門：

```text
workflows/daily_execution_gate.md
```

此檔不是新增完整複雜流程，而是把既有 Loop / 強制規則濃縮成三個每日輸出前不可省略的檢查：

```text
1. 硬閘門狀態
2. 6 大核心領域 Coverage Matrix
3. 高風險 claim 檢查表
```

使用原則：

- 不增加大量新表格。
- 不要求所有新聞都拆成 claim table，只針對高風險 claim。
- 若任一核心領域未達 5 則大型新聞 + 3 則小眾候選，必須標示未通過。
- 若未完整檢查最近 7 日 reports，必須標示歷史去重未完整。
- 若高風險 claim 查不到來源，不得放入事實區。
- 外部模型輸出不得直接併入正式報告，需先拆 claim、查來源、分級、採用 / 降級 / 不採用。

### Reason

使用者指出 repo 原本已經有驗證流程、Loop 確認與強制規則；若再加過多鎖，可能讓每日播報變得太複雜，反而因 token / 上下文壓縮造成 AI 跳過或假裝完成。

因此本次不新增大型 validator 架構，只新增最小可測試閘門，目標是讓 AI 更難跳過最重要的合規條件，同時保持系統輕量。

### Result

已新增：

```text
workflows/daily_execution_gate.md
```

測試觀察項目：

```text
1. AI 是否會在報告開頭正確標示硬閘門狀態。
2. AI 是否會輸出 6 大核心領域 Coverage Matrix。
3. AI 是否會對高風險 claim 做來源 / 證據等級 / 採用狀態判斷。
4. AI 是否仍會把未完成報告寫成完整正式播報。
5. 此最小閘門是否增加過多執行負擔。
```

---

## 2026-06-29：台灣新聞與商業觀點來源補強

### Decision

每日播報涉及台灣市場、台灣產業、零售、百貨、服飾、消費、AI 導入、企業管理或品牌經營時，繁體中文來源策略需固定納入：

```text
商業周刊 / Business Weekly Taiwan
HBR 哈佛商業評論 / Harvard Business Review 繁體中文版
```

使用規則：

- 商業周刊與 HBR 哈佛商業評論主要作為 B 級來源，用於補足台灣商業案例、管理觀點、產業趨勢、消費洞察與零售經營脈絡。
- 若內容包含官方數據、財報、明確調查或具名受訪者，可提升為中高證據，但仍需標示原始資料或口徑。
- 若內容屬評論、專欄或管理觀點，不得單獨寫成已證實事實，需標示為觀點、產業解讀或待驗證推論。
- 台灣即時新聞不足時，需使用上述來源補充掃描，但不得用觀點文章硬補成重大新聞。

### Reason

台灣本地訊號若只依賴即時新聞，容易漏掉企業管理、零售經營、消費心理、品牌策略與中長期產業觀察。商業周刊與 HBR 哈佛商業評論能補上商業案例與管理觀點，但證據層級需和官方資料、財報、統計、主流新聞區分。

### Result

已同步或需同步檢查：

```text
configs/source_strategy.md
configs/evidence.yml
configs/radars.yml
templates/daily_report_template.md
reports/INDEX.md
```

---

## 2026-06-29：每日訊號硬閘門，大型重要新聞 5 則 + 小眾候選 3 則

### Decision

每日正式播報必須同時滿足兩個最低量：

```text
每個核心領域至少 5 則大型重要新聞 / 主流重大訊號
每個核心領域至少 3 則小眾潛力候選訊號
6 個核心領域合計每日最低 30 則大型重要新聞 + 18 則小眾潛力候選訊號
```

此規則只可多不可少。大型重要新聞與小眾潛力候選訊號是兩個不同層級，不可互相替代：

- 不得用大型重要新聞假裝已完成小眾候選訊號。
- 不得用小眾候選訊號補足大型重要新聞最低量。
- 若任一核心領域未達 5 + 3，必須逐領域至少 retry 3 種搜尋方法。
- 若 retry 後仍不足，必須明確標示「未通過每日訊號硬閘門」，不能寫成正式完整播報。

### Reason

使用者指出前次播報不是只有「小眾候選未達標」，而是每個核心領域都沒有完整輸出 3 則小眾候選；並進一步確認每日播報基本規則應為「大型重要新聞每領域 5 則，小眾候選每領域 3 則」，只可多不可少。

此修正避免三種錯誤：

1. 報告退化成少量新聞摘要。
2. 用主流大新聞硬補小眾候選。
3. 用小眾候選取代主流重大訊號，造成覆蓋不足。

### Result

已同步或需同步檢查：

```text
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
templates/daily_report_template.md
SYSTEM_PROMPT.md
memory/missed_cases.md
reports/INDEX.md
```

---

## 2026-06-29：小眾潛力候選訊號與歷史去重規則

### Decision

每日播報的「今日候選訊號」改為「今日小眾潛力候選訊號」。候選訊號不得只是主流新聞摘要，必須優先抓小眾、早期、地方試點、小公司、研究原型、開發者工具、特殊商業模式、產業邊緣案例、失敗案例、反面成本或尚未被主流市場充分定價的弱訊號。

每個核心領域每日需嘗試抓 3 則小眾潛力候選訊號，並附可回查來源。若某領域今日沒有合格候選，需明確寫「無合格候選更新」，不得用大眾新聞硬補。

每日輸出前必須檢查近期歷史報告。已播過的事件不得重複重播，除非有新官方公告、新數據、新資金流、新監管進展、新企業導入、新就業證據、新台灣映射，或候選訊號升級 / 降級。

整體輸出必須維持「大到小、上到下」：上層結構 → 中層變化 → 具體事件 → 小眾潛力候選 → 指標驗證 → 台灣 / 使用者映射 → 下一步追蹤。

### Reason

使用者希望每日播報維持完整全球雷達，同時避免候選訊號被主流新聞吃掉。候選訊號的價值在於補主流雷達盲區，而不是重述大眾新聞。

### Result

已同步或需同步檢查：

```text
SYSTEM_PROMPT.md
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
templates/daily_report_template.md
memory/missed_cases.md
reports/INDEX.md
```

---

## 2026-06-28：指定 repo Level 與 thin mount 架構

### Decision

本 repo 指定為：

```text
Level 2 runtime-lite
```

並以 `Human-AI-Collaboration-Brain` 作為 framework source，採 thin mount。

### Reason

```text
具備固定 workflow、configs、memory、templates、reports 與 loop checklist，但不需要升級成 Agent Product System。
```

### Result

後續新增或升級 module / workflow / tool / provider / data contract 時，需檢查入口層是否同步。
