# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-07-06

---

## 2026-07-06：換掛 brain-core（舊母腦退役）

### Decision

本 repo 的治理掛載從 `Human-AI-Collaboration-Brain`（母腦 v2.0-draft thin mount）
換成 `brain-core`（蒸餾核）。不再使用 Level / capability 散文模型；
改為五原則（P1–P5）＋ 五條不變式，每條不變式都有機器消費者。

### Why

母腦終局檢驗（2026-07-06，見 brain-core/DECISIONS.md）量化證明散文治理失效：
入口稅 38.8K tokens、23 條規則 13 條零消費。brain-core 把規則寫成資料＋檢查器，
在 commit 關口自動出現——不靠人記、不靠 AI 自律讀。本 repo 是 brain-core 第一個
真實掛載專案（對照協議見 brain-core/COMPARE.md）。

### Result

```text
改：brain.manifest.yaml / AGENTS.md / CLAUDE.md / PROJECT_OS_MOUNT.md / README.md /
    PROJECT_MAP.md / HIGH_LEVEL_INDEX.md / CONTEXT_ROUTING.md / CURRENT_STATE.md /
    schema/sync-matrix.json / check_mount_integrity.sh（薄包裝，CI 不用改）
增：tools/brain/check-core.js / tools/brain/check-domain-packs.js / tools/install_hooks.sh
證據：reports/execution_checks/2026-07-06_brain_core_mount_and_domain_extension.md
不動：configs/ sources/ workflows/ templates/ memory/ 的內容規則（雷達行為不變）
```

---

## 2026-07-06：多領域擴充機制＋潛力池不預篩＋固定查詢配方

### Decision

```text
1. 新領域一律用 domains/<domain_id>/ 領域包掛載（domain_pack.json + sources.json），
   複製 domains/_template/ 填完即生效；完整性由 check-domain-packs 在 commit 關口驗。
   六大核心領域維持在 configs/radars.yml + sources/key_media_library.yml（canonical 不動）。
2. 蒐集階段不做預先篩選：新概念/新應用/新場景/新商業模式/新組合/新趨勢苗頭一律入
   memory/potential_pool.md，不得以「太小/證據弱/看起來不重要/主流已報導/與現有領域無關」
   為由丟棄。篩選與 5+3 計數只發生在輸出階段；被淘汰項目留池改狀態，定期聚類回顧。
3. 弱模型可執行的固定查詢配方：configs/query_recipes.yml（核心六領域）與領域包內
   query_recipes。配方照抄執行，模型自由發想的查詢只能補充且需在 coverage audit 揭露。
```

### Why

外部研究（research/global_news_trend_projects_2026-07-06.md）：
DEFRA horizon scanning 實務證明蒐集階段的價值過濾會系統性漏掉早期訊號
（本 repo 的虛擬資產服務法漏抓即同型錯誤）；structured-output 研究證明
小模型在固定管線＋固定 schema 下準確率僅損失約 2%；商業媒體監測業的共同架構
是「引擎領域無關、領域＝配置」。

### Result

```text
增：domains/README.md / domains/_template/{domain_pack.json,sources.json} /
    configs/query_recipes.yml / memory/potential_pool.md /
    research/global_news_trend_projects_2026-07-06.md
改：configs/edge_case_discovery.yml（capture_no_prefilter）/
    SOURCE_LIBRARY_SPEC.md（§5.1 domain extension）/
    AGENT_DEFINITION_MAP.md（query recipes 順序＋domain extension boundary）
```

---

## 2026-07-02：Search Agent adopts source-library-first method

### Decision

每日市場雷達與指定主題新聞搜尋的 Search Agent 方法，從「keyword-first」調整為「source-library-first」。

Active source-library files:

```text
SOURCE_LIBRARY_SPEC.md
configs/source_routing_rules.yml
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

New execution order:

```text
固定來源庫
→ 來源內關鍵字與主題過濾
→ 外部關鍵字 fallback
→ 新來源 discovery
→ coverage audit
```

### Rules

```text
1. AGENT_RADAR_REPORT、AGENT_DAILY_PUSH_BRIEF、AGENT_NEWS_SEARCH 必須先檢查固定來源庫，再使用 generic keyword search。
2. 關鍵字搜尋保留，但降級為來源內過濾、事件補查、缺口 retry、外部 discovery。
3. 每個核心領域要能回溯已查來源、命中來源、未命中來源、是否使用 fallback。
4. 台灣新聞仍必須是 source-backed Taiwan event / data / company action / policy / market news，不得用台灣推論補位。
5. 官方 / 數據 / 公司公告來源應用於高風險 claim 與指標變化交叉驗證。
6. source library 是可維護的活表，不是死表；來源健康需透過後續回測與使用紀錄調整。
```

### Reason

只靠關鍵字搜尋容易被熱門重複新聞、SEO 內容、低品質轉載與搜尋排序污染，也難以回答「這些總結根據哪些新聞」。固定來源庫能提高速度、穩定性、可追溯性與回測能力。

### Result

已新增或調整：

```text
SOURCE_LIBRARY_SPEC.md
configs/source_routing_rules.yml
sources/README.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
configs/source_strategy.md
workflows/daily_radar_workflow.md
workflows/daily_push_brief_workflow.md
workflows/news_search_content_workflow.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
```

後續仍需：

```text
1. 逐一驗證來源 RSS / API / usage policy。
2. 補 `memory/source_health_log.json` 與 `memory/topic_coverage_log.json` 實作。
3. 跑一次 Daily Push Brief 測試，觀察來源庫檢查是否真的被執行。
4. 回測是否減少「總結沒有可追溯新聞」的問題。
```

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
