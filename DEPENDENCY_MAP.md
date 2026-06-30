# Daily Market Radar｜DEPENDENCY_MAP

Thin-mount dependency map for the Daily Market Radar repo.

This file is not a copy of the mother Brain.

This file is the active source for:

```text
output modes
route → workflow → template chains
mode-specific completion gates
sync checks
```

Do not create a separate active execution-gate file for daily output modes. Daily gate rules belong here so dependency and completion logic stay synchronized.

---

## 1. Source of truth

```text
Current mount: brain.manifest.yaml
Execution entry: AGENTS.md
Current state: CURRENT_STATE.md
Current decisions: CURRENT_DECISIONS.md
Agent map and task routing: AGENT_DEFINITION_MAP.md
Dependency and completion gates: DEPENDENCY_MAP.md
```

---

## 2. Core dependencies

| Area | Files |
|---|---|
| Entry | README.md, SYSTEM_PROMPT.md, PROJECT_MAP.md, HIGH_LEVEL_INDEX.md, CURRENT_STATE.md, CURRENT_DECISIONS.md, AGENTS.md, AGENT_DEFINITION_MAP.md, brain.manifest.yaml |
| Radar rules | configs/ |
| Memory | memory/ |
| Output | templates/, reports/, content/ |
| Full workflow | workflows/daily_radar_workflow.md |
| Concise push workflow | workflows/daily_push_brief_workflow.md |
| News search workflow | workflows/news_search_content_workflow.md |
| Content workflow | workflows/news_content_workflow.md |
| Backtest | reports/backtests/, evals/cold_read_eval.md |
| Mount check | check_mount_integrity.sh |

---

## 3. Active output modes and dependency chains

```text
Full Daily Radar
→ AGENT_RADAR_REPORT
→ workflows/daily_radar_workflow.md
→ templates/daily_report_template.md
→ DEPENDENCY_MAP.md / Full Daily Radar Gate

Daily Push Brief
→ AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ templates/daily_push_brief_template.md
→ DEPENDENCY_MAP.md / Daily Push Brief Gate

News Search Output
→ AGENT_NEWS_SEARCH
→ workflows/news_search_content_workflow.md
→ templates/news_search_content_template.md

News Content Output
→ AGENT_NEWS_CONTENT
→ workflows/news_content_workflow.md
→ templates/news_content_template.md
```

Route, workflow, template, and gate must form one consistent dependency chain.

If they disagree, mark the output:

```text
依賴鏈不一致：partial / blocked
```

---

## 4. Routing

```text
Task routing lives inside AGENT_DEFINITION_MAP.md.
No standalone ROUTING.md is active.
```

If user asks for today’s brief, daily news, daily push, concise output, or lightweight report, route to:

```text
AGENT_DAILY_PUSH_BRIEF
```

Only route to `AGENT_RADAR_REPORT` when the user explicitly asks for a full formal archive report or `reports/YYYY/YYYY-MM-DD.md` output.

---

## 5. Mode-specific completion gates

### 5.1 Full Daily Radar Gate

Applies only to:

```text
AGENT_RADAR_REPORT
Full Daily Radar
formal archive report
reports/YYYY/YYYY-MM-DD.md
```

Completion requirements:

```text
6 大核心領域皆達 5 則大型重要新聞 + 3 則小眾潛力候選
已完成必要 repo 檔案讀取
已完成搜尋
已完成最近 7 日 reports 去重
已完成高風險 claim 檢查
已輸出 Coverage Matrix
已輸出 Data Gaps / Retry Notes
已輸出 post-report backtest / model adjustment panel
```

Only if all requirements pass, mark:

```text
完整正式播報：通過
```

If any requirement is missing, mark:

```text
完整正式播報：未通過
不可視為完整正式播報
```

### 5.2 Daily Push Brief Gate

Applies only to:

```text
AGENT_DAILY_PUSH_BRIEF
Daily Push Brief
concise user-facing daily push
chat daily news brief
```

Completion requirements:

```text
已讀取必要入口檔，或明確揭露缺失
6 大核心領域皆有覆蓋
每一核心領域包含 2–3 則大型訊號
每一核心領域包含 1 則小眾 / 潛力候選
每一核心領域包含台灣映射
Retail Focus Block 存在
Data Gaps and Retry Notes 存在
Post-brief Review 存在
```

Daily Push Brief must write:

```text
輸出模式：每日推播精簡版。
精簡版狀態：complete / partial concise brief。
完整 48 則正式閘門：未嘗試 / 未通過 / 另需分段研究版。
```

Do not use the Full Daily Radar 5+3 gate to mark Daily Push Brief as failed.

---

## 6. Coverage Matrix rules

### Full Daily Radar

| 核心領域 | 大型新聞數 | 小眾候選數 | 是否達標 | 缺口 |
|---|---:|---:|---|---|
| AI 模型 / Agent / 工作流替代 | >=5 | >=3 |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | >=5 | >=3 |  |  |
| 零售 / 消費 / 社群 / 服飾 | >=5 | >=3 |  |  |
| 全球市場 / 資金流 / 地緣政治 | >=5 | >=3 |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | >=5 | >=3 |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | >=5 | >=3 |  |  |

### Daily Push Brief

| 核心領域 | 大型訊號數 | 小眾候選數 | 台灣映射 | 精簡版狀態 | 漏抓風險 |
|---|---:|---:|---|---|---|
| AI 模型 / Agent / 工作流替代 | 2–3 | 1 | required |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | 2–3 | 1 | required |  |  |
| 零售 / 消費 / 社群 / 服飾 | 2–3 | 1 | required |  |  |
| 全球市場 / 資金流 / 地緣政治 | 2–3 | 1 | required |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | 2–3 | 1 | required |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | 2–3 | 1 | required |  |  |

---

## 7. High-risk claim gate

All modes must apply the same evidence check for high-risk claims.

High-risk claims include:

```text
精確數字
重大政策
公司重大事件
新技術突破
加密資金流
台灣本地判斷
外部模型提供的陌生訊號
```

Evidence handling:

```text
官方、權威媒體、多來源交叉驗證 → 可採用
可信媒體但資料不完整 → 可採用，但標中證據與不確定點
只有社群或模型敘事 → 只能列候選
查不到來源 → 不得放入事實區
來源支持方向但不支持數字 → 方向保留，數字降級或不採用
來源支持舊事件但不是今日新事件 → 標示為背景訊號或歷史已播
```

External model outputs are scouts, not judges:

```text
外部模型輸出 → 拆成高風險 claim → 查來源 → 證據分級 → 採用 / 降級 / 不採用 → 回補到報告或規則
```

---

## 8. Frozen dependencies

These files are frozen history and should not drive active routing:

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
archive/
```

---

## 9. Sync rule

When radar scope, report format, retry rules, missed-case handling, template, report, workflow, agent map, active output mode, or completion gate changes, check:

```text
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENTS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
templates/
brain.manifest.yaml
check_mount_integrity.sh
```

Required sync chain:

```text
AGENT_DEFINITION_MAP.md
→ DEPENDENCY_MAP.md
→ workflows/
→ templates/
→ check_mount_integrity.sh
```

No workflow or template change is considered complete unless `DEPENDENCY_MAP.md` recognizes the same output mode and completion gate.

No separate active daily execution gate file should be introduced. If a separate gate file exists, it is historical / deprecated and must not drive active routing.

---

## 10. Level

```text
Level 2：Runtime-Lite Brain
```
