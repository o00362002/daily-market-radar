# AGENT_DEFINITION_MAP

Route map for `daily-market-radar`.

## AGENT_ routes

| Route id | Use when |
|---|---|
| `AGENT_RADAR_REPORT` | full daily market radar report |
| `AGENT_DAILY_PUSH_BRIEF` | concise daily push brief |
| `AGENT_NEWS_SEARCH` | specific topic news search |
| `AGENT_NEWS_CONTENT` | rewrite checked signals into content |
| `AGENT_COVERAGE_BACKTEST` | missed case, gap, coverage, or adjustment review |
| `AGENT_RADAR_CONFIG` | config, trigger, evidence, retry, or watchlist change |

Select exactly one primary `AGENT_` route before execution.

## Boundary

Agent owns a complete task goal. Workflow orders steps. Skill judges. Tool operates. Loop reviews and improves.
