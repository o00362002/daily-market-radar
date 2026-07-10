# Runtime v2 contract sync and live RSS foundation

Date: 2026-07-10
Branch: `fix/runtime-v2-contract-sync`
Status: implementation complete on branch; automated validation pending

## Why

The repository had a valid runtime-v2 direction but active Markdown policies still contained v1 fixed-count completion rules. The runtime also used seven domain identifiers while user-facing reports used six, the report contract did not enforce Retail/Crypto/structural panels, the source registry had a misleading `.yaml` extension despite JSON content, and only fixture ingestion was connected.

## Changed

```text
1. Added config/runtime_contract.json as canonical report-domain/profile/completion contract.
2. Standardized six canonical report domains; policy_geopolitics maps to global_markets_macro.
3. Replaced fixed-count completeness language with slot caps + coverage gates.
4. Separated major and potential lanes; importance, potential and confidence remain independent.
5. Expanded executable report validation to require coverage, source audit, rejection counters,
   Retail matrix, Crypto matrix, structural indicators and backtest.
6. Added candidate_type and formation_level to potential report items.
7. Added config/source_registry.json and expanded global, official, Taiwan, retail/fashion,
   labor and crypto source coverage.
8. Added standard-library live RSS/Atom ingestion with explicit feed-failure gaps.
9. Added optional SQLite persistence for run records, report payloads and coverage gaps.
10. Updated SYSTEM_PROMPT, DEPENDENCY_MAP, route map, workflows, templates, source policy,
    current state, README, navigation docs and migration docs.
11. Expanded schema/sync-matrix.json with runtime-contract, registry, adapter and repository edges.
12. Made Makefile portable with PYTHON ?= python3.
13. Added runtime-contract, RSS/Atom, report-contract and SQLite persistence tests.
```

## Canonical files after repair

```text
config/runtime_contract.json
config/source_registry.json
src/radar/
schemas/report.schema.json
schema/sync-matrix.json
```

## Deliberately not claimed complete

```text
web/API/social/FreshRSS adapters
external discovery providers
historical event persistence and cross-run material-delta comparison
semantic evidence scoring and counterevidence extraction
Retail/Crypto matrix evaluators
structural-trend indicator evaluators
scheduler and production credentials
```

`live-rss` is a real network adapter for RSS/Atom sources, but a run remains partial when other required adapter families or coverage cells are unexecuted.

## Validation plan

```text
make validate
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli run-daily --mode fixture --date 2026-07-10 --database /tmp/radar.sqlite3
optional network smoke:
PYTHONPATH=src python -m radar.cli run-daily --mode live-rss --date 2026-07-10 --per-feed-limit 1 --timeout-seconds 5
```

At record creation time these commands had not yet been executed in a checked-out branch environment. Do not describe them as passing until CI or a local checkout confirms them.

## Affected users

- Daily report agents now use runtime-v2 coverage semantics instead of filling fixed quotas.
- Maintainers edit one runtime contract and one source registry rather than duplicating values in prose.
- Taiwan and niche gaps become explicit coverage failures.
- Operators can run fixture or live-RSS mode and optionally persist report payloads locally.

## Verification receipt target

```text
changed: runtime contract, source registry, runtime, schemas, policies, workflows, templates, tests and docs
machine checks: pending
not done: production web/API/social/FreshRSS/discovery integrations
impact: all daily-push, full-radar, source-health and backtest runs
owner verification: review PR diff and run make validate
```
