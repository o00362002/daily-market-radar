# 2026-06-30｜Agent Routing Runtime Refactor Backtest

## 0. Scope

本紀錄整理 2026-06-30 對 `daily-market-radar` 的每日播報、Agent 路由、精簡版輸出、新聞內容產出與 repo runtime flow 的回測與修正。

本次不是單純修正一份每日報告，而是一次 Runtime 設計回測。

---

## 1. Trigger

使用者在今日每日播報後指出：

```text
1. 報告內容完整度下降。
2. 有 GitHub 規格與程式碼控制，但仍能輸出 incomplete report。
3. 零售、科技發展、潛力訊號、台灣逐段映射不足。
4. 自動每日推播與手動下指令結果不同。
5. 完整 48 則正式閘門對單次聊天模型過重。
6. 每日雷達、指定主題新聞搜尋、已選新聞內容深化被混在一起。
7. Project Understanding、Task Routing、Workflow Selection 的順序需要重新釐清。
```

---

## 2. Observed Failure Modes

### 2.1 Prompt / Spec Drift

Repo 內已有很多 configs、memory、templates、reports 與 workflow 規則，但模型執行時仍可能只根據使用者當次 prompt 與少量已讀內容輸出。

結果：

```text
規格存在 ≠ 規格被完整執行
文件控制 ≠ 程式化控制
```

---

### 2.2 Full Report Too Large for Single-Pass Chat Execution

原正式門檻為：

```text
6 核心領域 × 每領域 5 則大型重要新聞 + 3 則小眾候選 = 48 則訊號
```

單次聊天同時要求：

```text
GitHub 多檔讀取
最新搜尋
48 則訊號
固定指標
歷史去重
台灣映射
證據分級
retry
回測
完整格式輸出
```

會導致模型壓縮、跳區塊、格式變形或只輸出 partial。

---

### 2.3 Task Type Coupling

下列任務原本容易混在一起：

```text
A. 每日市場雷達：跨領域情報與趨勢判斷
B. 指定主題新聞搜尋：例如今天科技新聞 / AI 新聞 / 零售新聞
C. 已選新聞內容深化：把某則新聞寫詳細、轉社群貼文、寫零售觀點
```

若混在同一 workflow，會造成搜尋、判斷、寫作責任不清。

---

### 2.4 Routing Layer Overhead

曾短暫新增 `ROUTING.md` 作為獨立路由層。

回測後判斷：

```text
ROUTING.md 增加了一層不必要讀取負擔。
Task routing 應併入 AGENT_DEFINITION_MAP.md。
```

---

### 2.5 Wrong Order: Routing Before Project Understanding

曾討論是否應在 `AGENTS.md` 後直接讀 routing 選 Agent / Workflow。

回測後修正：

```text
不應只靠使用者一句話先選 workflow。
應先理解專案當前狀態、決策、入口、依賴，再做任務路由。
```

---

## 3. Root Cause

本次根因不是單純搜尋能力不足，而是：

```text
Project Understanding
Task Routing
Workflow Selection
Memory Loading
Output Mode
```

之間的順序與責任邊界不清。

---

## 4. Accepted Runtime Flow

最新版 Runtime Flow：

```text
1. AGENTS.md

2. Project Understanding Layer
   - PROJECT_MAP.md
   - HIGH_LEVEL_INDEX.md
   - CURRENT_STATE.md
   - CURRENT_DECISIONS.md
   - README.md
   - DEPENDENCY_MAP.md
   - brain.manifest.yaml

3. Agent / Task Selection Layer
   - AGENT_DEFINITION_MAP.md

4. Choose Agent / Workflow / Template
   - radar_report_agent
   - news_search_agent
   - news_content_agent

5. Read task-specific context
   - workflows/
   - templates/
   - configs/
   - memory/
   - reports/
   - loops/
   - evals/

6. Execute

7. Completion Check / Backtest / Model Improvement
```

---

## 5. Changes Applied

### 5.1 Daily Push Brief

新增：

```text
workflows/daily_push_brief_workflow.md
templates/daily_push_brief_template.md
```

用途：

```text
每日可讀、穩定、精簡，不宣稱通過 48-signal formal gate。
```

最低輸出：

```text
6 大領域
每領域 2–3 則大型訊號
每領域 1 則小眾候選
每領域台灣映射直接放在該段
零售 Focus Block
資料缺口與回測面板
```

---

### 5.2 News Search Agent

新增：

```text
news_search_agent
workflows/news_search_content_workflow.md
templates/news_search_content_template.md
```

用途：

```text
可單獨搜尋指定主題新聞並輸出 source-backed news report。
例如：今天科技新聞、AI 新聞、零售新聞、加密新聞、台灣百貨新聞。
```

邊界：

```text
不取代完整 daily market radar。
不需要覆蓋全部 6 大領域。
需標示來源、證據等級、資料缺口與台灣 / 使用者映射。
```

---

### 5.3 News Content Agent

新增 / 調整：

```text
news_content_agent
workflows/news_content_workflow.md
templates/news_content_template.md
```

用途：

```text
將已確認或已標示證據等級的新聞 / 雷達訊號，改寫成新聞摘要、趨勢短文、社群素材、文章草稿或零售觀點。
```

邊界：

```text
不負責廣泛搜尋。
不升級證據。
不把低證據候選寫成已證實事實。
```

---

### 5.4 Routing Merged into Agent Definition

刪除：

```text
ROUTING.md
```

路由責任改由：

```text
AGENT_DEFINITION_MAP.md
```

負責：

```text
Agent 定義
任務類型 → Agent
Agent → Workflow
Workflow → Template
角色邊界
Execution Evidence
```

---

### 5.5 AGENTS.md Flow Update

`AGENTS.md` 已改成：

```text
AGENTS.md
→ Project understanding layer
→ AGENT_DEFINITION_MAP.md
→ choose Agent / Workflow / Template
→ read task-specific configs / memory / reports / templates
→ execute
→ completion check
```

並明確規定：

```text
Do not select a workflow only from the user sentence before understanding the current project state and decisions.
Memory is task-specific execution context. It should be read after the task route is selected, unless the task itself is to inspect or modify memory.
```

---

## 6. Updated Agent Set

```text
radar_report_agent
→ 每日市場雷達 / 每日推播精簡版

news_search_agent
→ 指定主題新聞搜尋與 source-backed output

news_content_agent
→ 已選新聞 / 已分級訊號的內容化與深化
```

---

## 7. Key Design Principles Extracted

本次回測產生的可複用 runtime 原則：

```text
1. Project Understanding must happen before Task Routing.
2. Task Routing belongs in the Agent Definition Layer unless multiple true runtimes exist.
3. Memory is task-specific execution context, not something that must always be fully loaded before routing.
4. Workflow should keep single responsibility: search, radar judgement, and content production should be separated.
5. Full formal report and daily push brief must be separate output modes.
6. Repo rules guide AI, but programmable checks are required for deterministic enforcement.
7. Every architecture change should leave a backtest / decision record.
```

---

## 8. Remaining Risks

```text
1. GitHub 文件仍不是 deterministic runtime。
2. ChatGPT / Claude / Gemini 可能仍只讀部分 context。
3. Daily Push Brief 需實測品質是否比完整 48-signal prompt 穩定。
4. news_search_agent 需測試是否能避免把指定主題新聞寫成完整市場雷達。
5. reports 歷史讀取與去重仍需進一步驗證。
6. 未來若要完整 48-signal formal report，應採分段 / multi-agent / validator 模式。
```

---

## 9. Next Verification

```text
1. 用 daily_push_brief_workflow 重新跑一次每日推播精簡版。
2. 用 news_search_agent 測試「今天科技新聞」。
3. 用 news_content_agent 測試「把這則新聞寫詳細」。
4. 檢查 AGENTS.md → AGENT_DEFINITION_MAP.md → workflow → template 是否能被模型穩定遵守。
5. 後續若仍漏區塊，再決定是否加入 validator，而不是繼續增加 prose rules。
```

---

## 10. Status

```text
Status: accepted runtime refactor backtest
Downstream sync: Human-AI-Collaboration-Brain should record the extracted runtime principles.
```