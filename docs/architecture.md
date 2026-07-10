# Event Intelligence Runtime v2 Architecture

`daily-market-radar` v2 is a modular monolith.

```text
domain/types → config/schemas → repositories/adapters → pipeline/services → reporting/runtime
```

## Canonical contracts

```text
config/runtime_contract.json = report domains, profiles, matrices and completion contract
config/source_registry.json  = source identity and adapters
schemas/report.schema.json   = external report payload shape
src/radar/reporting/contracts.py = executable report invariants
schema/sync-matrix.json      = change-impact edges
```

## Runtime modules

```text
src/radar/domain/        Document, Event, Signal, CoverageCell, ReportItem, RunResult
src/radar/schemas/       canonical registry parsing and validation
src/radar/adapters/      fixture and live RSS/Atom adapters
src/radar/repositories/  SQLite run/report/gap persistence
src/radar/pipeline/      normalization, dedup, clustering, classification and coverage
src/radar/reporting/     planning and contract validation
src/radar/runtime/       profile contract and run orchestration
```

## Source model

One real-world source has one `source_id`. RSS, API, web, RSSHub and social routes are adapters. `FRESHRSS_SEEDS.opml` is a generated projection from enabled RSS adapters.

The live RSS path currently executes RSS/Atom adapters only. Web, API, social, FreshRSS and external-discovery adapters remain explicit coverage gaps until connected.

## Event and report model

```text
Document → Event → optional Potential Signal → ReportItem
```

A report item has one primary report domain and one lane:

```text
major = importance now
potential = future option value
confidence = evidence strength
```

The same event cannot occupy both lanes or multiple primary domains. Daily Push slot caps are rendering limits, not completeness proof.

## Persistence

```text
migrations/0001_runtime_foundation.sql = source, run, document, event, signal and report foundation
migrations/0002_report_payloads.sql     = report JSON payloads and coverage gaps
```

`SqliteRunRepository` is the local durable foundation. A later production repository can implement the same boundary for PostgreSQL without changing the event/report contract.

## LLM boundary

LLMs may perform semantic extraction, fuzzy event matching, summaries and trend mapping. Fetching, URL safety, source identity, deterministic de-duplication, slot counting, coverage gates, evidence-link validation and report-contract validation stay in code.

## Current limits

Historical material-delta comparison, web/API/social/FreshRSS adapters, external discovery, semantic scoring, indicator evaluators and scheduling are not production connected. These missing stages must appear as degradation reasons rather than being simulated by prose.
