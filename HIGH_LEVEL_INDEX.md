# daily-market-radar｜HIGH_LEVEL_INDEX

This file is a navigation projection, not a source of truth.

## Source of truth

```text
brain.manifest.yaml
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
config/runtime_contract.json
config/source_registry.json
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
schema/sync-matrix.json
```

## Runtime v2

```text
src/radar/                     deterministic event-intelligence runtime
config/runtime_contract.json   report domains, profiles, matrices and completion contract
config/source_registry.json    canonical source identity and adapters
schemas/                       stable payload contracts
migrations/                    durable storage foundation
Makefile                       validation entrypoint
```

## Semantic policy and coverage modules

```text
configs/       radar modules, evidence, freshness, retry and structural policies
sources/       legacy / compatibility source inputs until regenerated from registry
domains/       optional source/query packs mapped to canonical report domains
memory/        potential pool, watchlists and approved missed cases
```

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
Daily Push Brief = profile=daily_push, concise slot-capped rendering
Full Daily Radar = profile=full, all qualified items within run budget
```

Slot caps are not completeness proof. Completion comes from source health, coverage cells, evidence trace, fresh delta, de-duplication, matrices, structural indicators, report validation and backtest.

## Canonical report domains

Read from `config/runtime_contract.json`.
Fine-grained entries in `configs/radars.yml` are modules and indicators, not extra report-domain quotas.

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
number of rendered items != completeness
projection != source of truth
frozen history != current state
```
