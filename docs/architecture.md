# Event Intelligence Runtime v2 Architecture

`daily-market-radar` v2 is a modular monolith whose behavior boundaries are enforced by code and tests.

```text
contracts/domain → ports → application → composition root → concrete infrastructure
```

## Stable ports

`src/radar/ports/` owns the replaceable behavior contracts:

```text
SourceAdapter
IntelligenceEvaluator
DocumentRepository
EventRepository
ReportRepository
IndicatorRepository
StateStore
WebArtifactStore
ReportPublisher
```

Every replaceable or external collaborator enters application modules through these Protocols. The application
also imports provider-neutral contracts/domain values and pure deterministic pipeline/validation functions; it
does not import RSS, SQLite, provider SDKs, network clients, filesystem stores or publisher implementations.

## Composition and compatibility

```text
src/radar/application/run_daily.py = provider-neutral orchestration
src/radar/composition.py           = concrete implementation selection
src/radar/runtime/runs.py          = backward-compatible CLI façade
```

Adding or replacing a source, evaluator, repository, state store, artifact store or publisher changes the
composition root, not event resolution, report assembly or web projection.

## Canonical contracts

```text
config/runtime_contract.json        report domains, profiles, matrices and completion contract
config/source_registry.json         source identity and adapter configuration
src/radar/contracts/report.py       strict RadarReportV2 boundary
src/radar/contracts/evaluation.py   provider-neutral evaluator request/result
src/radar/contracts/web.py          immutable web artifact and publication receipts
src/radar/reporting/contracts.py    executable cross-field report invariants
schema/sync-matrix.json             change-impact edges
```

Provider response fields remain inside concrete adapters and evaluators. Canonical Pydantic models use
`extra="forbid"`; generic audit fields such as `provider` and `model` are allowed, while backend response
payloads are not. Canonical document facts accept only source roles and numeric `MeasurementFact` values whose
metric IDs use approved semantic namespaces; adapter/provider response IDs are not document facts.

## Deterministic flow

```text
SourceAdapter
→ normalize to Document
→ DocumentRepository
→ deterministic dedup / event resolution
→ EventRepository
→ IntelligenceEvaluator
→ RadarReportV2 validation
→ ReportRepository + IndicatorRepository
→ WebArtifactStore + StateStore
→ ReportPublisher
```

The fake-only acceptance test executes this whole flow with every external side effect blocked. This proves
that network access, SQLite, OpenAI and filesystem writes are not application-layer dependencies.

## Current concrete implementations

```text
sources: fixture, public RSS/Atom registry
evaluation: deterministic rules
reports: memory, optional SQLite
documents/events/indicators: memory foundation
state/web artifacts: memory foundation
publisher: disabled no-op
```

SQLite migrations remain the local report/run foundation. A later backend can implement the repository
Protocols without changing application services.

## Current limits

Historical material-delta persistence, web/API/social/FreshRSS adapters, external discovery, production-grade
semantic scoring, API-assisted evaluation, filesystem projection, production publishers, the Astro dashboard
and scheduling are not connected. Their absence remains a degradation or later implementation boundary, not
a simulated capability.
