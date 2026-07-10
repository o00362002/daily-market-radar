# Daily Market Radar

`daily-market-radar` is an event-intelligence runtime and evidence archive, not a headline-summary repository.

## Core goal

Surface important current events and potential weak signals across global markets, AI, crypto, retail/fashion, technology, labor and Taiwan, then track whether they change structural directions.

## Active architecture

```text
AGENTS.md                     first entry
config/runtime_contract.json  canonical execution/output contract
config/source_registry.json   canonical source identity and adapters
src/radar/                    deterministic runtime
schemas/                      payload contracts
migrations/                   persistence foundation
workflows/ + templates/       human execution/rendering projections
reports/ + memory/            evidence, backtests and approved learning
```

## Runtime principles

```text
source registry before generic search
one real source = one source_id
RSS/API/web/RSSHub/social = adapters
one event = one primary report domain
major importance, future potential and evidence confidence are independent
Taiwan direct evidence != Taiwan implication
slot caps != completeness
coverage gaps must be visible
fixture replay != live-news coverage
```

## Profiles

```text
daily_push = concise slot-capped rendering
full       = all qualified items within run budget
```

Completion is validated through source health, coverage cells, evidence trace, fresh material delta, de-duplication, rejection counters, retry audit, Taiwan direct evidence, Retail/Crypto matrices, structural indicators, report contract and backtest.

## Canonical report domains

Read from `config/runtime_contract.json`.
Fine-grained radar modules live in `configs/radars.yml` and do not create additional report-domain quotas.

## Structural indicators

```text
K-shaped AI productivity economy
AI bubble / overinvestment
brand polarization + true vs fake segmentation
```

## Source architecture

`config/source_registry.json` is canonical. `FRESHRSS_SEEDS.opml` is generated from it. Legacy files under `sources/` remain compatibility inputs until regenerated.

FreshRSS/RSSHub improve collection coverage only. Discovery providers locate sources and clusters; final claims must resolve to original evidence.

## Validation and runtime

```bash
make validate
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli run-daily --mode fixture --date 2026-07-10
PYTHONPATH=src python -m radar.cli run-daily --mode live-rss --date 2026-07-10 --database data/radar.sqlite3
```

`live-rss` fetches enabled RSS/Atom adapters and can persist report payloads and coverage gaps to SQLite. It still reports partial when web/API/social/FreshRSS, external discovery or semantic evaluators are not executed.

## Current boundary

Implemented:

```text
fixture replay
live RSS/Atom ingestion
source registry and OPML validation
URL normalization and de-duplication
event clustering and major/potential separation
coverage gaps and report contract
optional SQLite report persistence
```

Not production-complete:

```text
web/API/social/FreshRSS adapters
external discovery providers
historical material-delta repository
semantic scoring and structural indicator evaluators
scheduler and production credentials
```

## Governance

```text
Parent control panel: o00362002/personal-project-brain
Core governance: o00362002/brain-core
Local source of truth: this repo
Sync edges: schema/sync-matrix.json
```

Structural changes require human review. Evidence does not become Memory without approval.
