# daily-market-radar｜HIGH_LEVEL_INDEX

This file is a navigation projection, not a source of truth.

## Source of truth

Owners and entry route live in `AGENTS.md`（讀取路由）and the machine contract `brain.manifest.yaml`. This file does not maintain a second copy of that list; it only projects the layout below.

## Runtime v2

```text
src/radar/                     deterministic event-intelligence runtime
config/runtime_contract.json   five news domains, profiles, matrices and completion contract
config/source_registry.json    canonical source identity and adapters
config/competitor_registry.json canonical product/social competitor identities and aliases
schemas/                       stable payload contracts
migrations/                    durable storage foundation
Makefile                       validation entrypoint
```

## Semantic policy and coverage modules

```text
configs/competitor_intelligence.yml competitor collection, projection and analysis policy
configs/query_recipes.yml            five news-domain recipes + competitor recipes + labor indicator-only recipes
configs/indicator_tracking.yml       fixed indicators, including labor/consumption indicator-only boundary
configs/                             other radar, evidence, freshness, retry and structural policies
sources/                             legacy / compatibility source inputs until regenerated from registry
domains/                             optional source/query packs mapped to canonical report domains
memory/                              potential pool, competitor watchlist and approved missed cases
```

## Competitor Intelligence

```text
config/competitor_registry.json  canonical names, aliases, priorities and high-risk signals
memory/watchlist.md              long-term watch intent and evaluation questions
tools/coverage_checker.md        fixed-check and missing-coverage audit
web/src/lib/competitors.ts       registry-backed web projection
web/src/pages/competitors.astro  product and social competitor analysis page
web/src/pages/index.astro        daily competitor summary
```

Competitor Intelligence is a cross-domain projection. It does not create an additional report-domain quota and does not duplicate an event.

## Human execution and rendering

```text
workflows/daily_push_brief_workflow.md
templates/daily_push_brief_template.md
workflows/daily_radar_workflow.md
templates/daily_report_template_v2.md
reports/ and reports/backtests/
```

## Active profiles

```text
Daily Push Brief = profile=daily_push, concise readability projection with minimum floors
Full Daily Radar = profile=full, all qualified items within run budget
```

Rendered selections are not completeness proof. Completion comes from source health, coverage cells, evidence trace, fresh delta, de-duplication, matrices, structural indicators, report validation and backtest.

## Canonical report domains

Read from `config/runtime_contract.json`.

```text
global_markets_macro
ai_agents_applications
crypto_rwa_agent_payments
retail_consumer_fashion
science_technology_industry
```

Fine-grained entries in `configs/radars.yml` are modules and indicators, not extra report-domain quotas. The retired labor domain remains only as a compatibility alias; labor and consumption pressure normally render in the fixed indicator panel.

## Active agents

```text
radar_report_agent
news_search_agent
news_content_agent
coverage_backtest_agent
radar_config_agent
social_channel_reader_agent
```

Routing lives in `AGENT_DEFINITION_MAP.md`.

## Important boundaries

```text
fixture replay != live news coverage
legacy sources/ files != canonical registry
Taiwan implication != Taiwan direct evidence
major importance != future potential != evidence confidence
competitor projection != canonical report domain
labor indicator != standalone news domain
number of rendered items != completeness
projection != source of truth
frozen history != current state
```
