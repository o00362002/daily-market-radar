# AGENT_DEFINITION_MAP

Route map for `daily-market-radar`.

Select exactly one primary `AGENT_` route before execution.

---

## AGENT_ routes

| Route id | Use when |
|---|---|
| `AGENT_RADAR_REPORT` | full daily market radar report / formal archive report |
| `AGENT_DAILY_PUSH_BRIEF` | concise daily push brief / chat daily news push |
| `AGENT_NEWS_SEARCH` | specific topic news search |
| `AGENT_NEWS_CONTENT` | rewrite checked signals into content |
| `AGENT_COVERAGE_BACKTEST` | missed case, gap, coverage, or adjustment review |
| `AGENT_RADAR_CONFIG` | config, trigger, evidence, retry, or watchlist change |

---

## Route selection rules

If the user asks:

```text
今天播報
每日新聞
每日推播
今日市場雷達
今天市場雷達
今天新聞
先看今天重點
簡版
輕量版
concise brief
daily push
```

Default route must be:

```text
AGENT_DAILY_PUSH_BRIEF
```

Do not route to `AGENT_RADAR_REPORT` unless the user explicitly asks:

```text
完整正式版
完整研究歸檔版
Full Daily Radar
48-signal report
產出 reports/YYYY/YYYY-MM-DD.md
完整寫入 reports
```

If user wording is ambiguous between daily push and full archive, choose `AGENT_DAILY_PUSH_BRIEF` and disclose:

```text
完整 48 則正式閘門：未嘗試 / 另需分段研究版。
```

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

## Boundary

Agent owns a complete task goal. Workflow orders steps. Skill judges. Tool operates. Loop reviews and improves.
