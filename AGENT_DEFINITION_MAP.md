# AGENT_DEFINITION_MAP

Select exactly one primary route before execution.
Machine execution profiles and domain definitions come from `config/runtime_contract.json`.

## Shared boundaries

All search and radar routes use:

```text
config/runtime_contract.json
config/source_registry.json
configs/news_freshness_and_taiwan_news.yml
configs/evidence.yml
configs/technology_development.yml
configs/structural_trend_indicators.yml
src/radar/ deterministic pipeline
schemas/report.schema.json
```

Rules:

```text
source registry before generic search
one event = one primary report domain
major and potential lanes remain separate
importance, potential and confidence are independent
Taiwan direct evidence != Taiwan implication
slot caps are readability limits, not completeness proof
fixture mode cannot claim live-news completeness
```

## Routes

| Route | Use when | Runtime profile |
|---|---|---|
| `AGENT_DAILY_PUSH_BRIEF` | ordinary daily news, morning brief, concise radar | `daily_push` |
| `AGENT_RADAR_REPORT` | explicit full, formal, archive or research report | `full` |
| `AGENT_NEWS_SEARCH` | one specified topic or entity | topic scope |
| `AGENT_NEWS_CONTENT` | rewrite already validated report items | no search profile |
| `AGENT_COVERAGE_BACKTEST` | gaps, misses, duplication, source health, model adjustment | backtest |
| `AGENT_RADAR_CONFIG` | source registry, runtime contract, radar, schema, workflow or policy changes | config |
| `AGENT_SOCIAL_CHANNEL_READER` | direct checks of public social/channel-first sources | specialist sub-route |

## Route selection

Use `AGENT_DAILY_PUSH_BRIEF` for:

```text
每日播報 / 每日新聞 / 今日市場雷達 / 今天新聞
morning brief / daily news / concise brief / quick radar
```

Use `AGENT_RADAR_REPORT` only for explicit:

```text
完整版 / 正式版 / 完整研究 / 歸檔版 / full report / archival report
```

Historical fixed-count phrases do not define active completeness. Interpret them only as a request for a broader report and still apply runtime-v2 coverage gates.

## Dependency chains

### Daily Push

```text
AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ config/runtime_contract.json profile=daily_push
→ config/source_registry.json
→ src/radar pipeline
→ templates/daily_push_brief_template.md
→ schemas/report.schema.json + Python validator
→ post-run backtest
```

### Full Radar

```text
AGENT_RADAR_REPORT
→ workflows/daily_radar_workflow.md
→ config/runtime_contract.json profile=full
→ config/source_registry.json
→ src/radar pipeline
→ templates/daily_report_template_v2.md
→ report validation
→ reports/ archive + backtest
```

### Topic Search

```text
AGENT_NEWS_SEARCH
→ source registry routing
→ source health / ingest / gap discovery
→ event and evidence validation
→ topic-search template
```

### Content Rewrite

```text
AGENT_NEWS_CONTENT
→ validated items only
→ content template
```

`AGENT_NEWS_CONTENT` cannot upgrade evidence, invent a fresh delta or replace a radar/search run.

## Social-channel specialist

Invoke `AGENT_SOCIAL_CHANNEL_READER` when direct checks are required for:

```text
Instagram / Threads / X / Facebook / YouTube / TikTok
LINE OA / Newsletter / Website / Linktree
Discord / Telegram / Podcast / public community channels
```

Generic search is not a direct social check. RSSHub and FreshRSS are collection adapters, not factual verification.

## Source and discovery boundary

```text
one real-world source = one source_id
RSS / API / web / RSSHub / social = adapters
unavailable adapter = coverage gap
external discovery = source discovery only
final claim = original source or verified credible evidence
```

## Domain boundary

Canonical report domains come only from `config/runtime_contract.json`.
Fine-grained entries in `configs/radars.yml` are radar modules, triggers and indicators; they do not create extra report-domain slots.

New extensible subject packs under `domains/` can add source/query coverage, but must map to a canonical report domain unless the runtime contract is intentionally changed and validated.

## Freshness and event identity

Every report item requires a material `today_delta`. Background knowledge, historical replay or article rephrasing does not create a new event item.

The same event cannot:

```text
occupy major and potential lanes together
occupy multiple primary report domains
be repeated because several publishers covered it
```

Cross-domain consequences belong in indicator panels and synthesis.

## Taiwan boundary

Direct Taiwan evidence is counted separately from Taiwan implication. If direct sources or channels were not checked, expose the coverage gap and do not say `Taiwan has no news`.

## Multi-agent handoff

Agents hand off externalized state only:

```text
run_id / event_id / signal_id
report JSON contract
coverage gaps
reports/backtests/
CURRENT_STATE.md / CURRENT_DECISIONS.md when approved
```

Agents do not share hidden reasoning and cannot approve their own evidence or structural changes.
