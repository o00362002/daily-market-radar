# AGENT_DEFINITION_MAP

Route map for `daily-market-radar`.

Select exactly one primary `AGENT_` route before execution.

---

## AGENT_ routes

| Route id | Use when |
|---|---|
| `AGENT_RADAR_REPORT` | explicit full daily market radar report / formal archive report |
| `AGENT_DAILY_PUSH_BRIEF` | default daily news broadcast / concise daily push brief / chat daily news push |
| `AGENT_NEWS_SEARCH` | specific topic news search |
| `AGENT_NEWS_CONTENT` | rewrite checked signals into content |
| `AGENT_COVERAGE_BACKTEST` | missed case, gap, coverage, or adjustment review |
| `AGENT_RADAR_CONFIG` | config, trigger, evidence, retry, or watchlist change |

---

## Route selection rules

Default daily output is lightweight.

Route to `AGENT_DAILY_PUSH_BRIEF` when the user asks:

```text
今天播報
每日播報
每日新聞
今天的每日新聞
播報今天的每日新聞
每日推播
今日市場雷達
今天市場雷達
今天新聞
先看今天重點
讀 repo 播報今天
不靠記憶讀 repo 播報今天
quick daily market brief
morning brief
daily news
daily push
concise brief
簡版
輕量版
```

Do not route to `AGENT_RADAR_REPORT` unless the user explicitly asks:

```text
正式版
完整正式版
完整版
完整研究歸檔版
正式每日雷達
完整每日雷達
Full Daily Radar
full report
complete report
archival report
48-signal report
完整 48 則
5+3
完整硬閘門
產出 reports/YYYY/YYYY-MM-DD.md
完整寫入 reports
歸檔版
```

If user wording is ambiguous between daily push and full archive, choose `AGENT_DAILY_PUSH_BRIEF` and disclose:

```text
輸出模式：每日推播精簡版。
完整 48 則正式閘門：未嘗試 / 另需分段研究版。
```

General words such as 每日 / 播報 / 新聞 / 市場雷達 / today / brief do not upgrade the route to the full archive workflow.

---

## Dependency chain

Each route must follow the active output-mode chain in `DEPENDENCY_MAP.md`.

```text
AGENT_RADAR_REPORT
→ workflows/daily_radar_workflow.md
→ templates/daily_report_template.md
→ DEPENDENCY_MAP.md / Full Daily Radar Gate

AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ templates/daily_push_brief_template.md
→ DEPENDENCY_MAP.md / Daily Push Brief Gate
```

Route, workflow, template, and gate must match. If they do not match, mark the output as:

```text
依賴鏈不一致：partial / blocked
```

Do not use a separate active daily execution-gate file for route completion rules. Daily output completion gates live in `DEPENDENCY_MAP.md`.

---

## Multi-agent handoff rule

Agents do not share hidden reasoning.

Agents hand off through externalized repo state:

```text
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
reports/backtests/
Post-Execution Record
Memory Patch Candidate
```

Select exactly one primary route before execution.

After execution, use the Post-Execution Backtest-to-Memory Gate when the task affects files, state, decisions, routes, evidence, dependency gates, radar corrections, or reusable workflow behavior.

---

## Boundary

Agent owns a complete task goal. Workflow orders steps. Skill judges. Tool operates. Loop reviews and improves.
