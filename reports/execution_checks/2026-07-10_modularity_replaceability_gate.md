# Modularity and Replaceability Acceptance Gate

Date: 2026-07-10
Branch: `codex/modularity-replaceability-gate`
Base: `main` at task start
Status: implementation complete; local automated validation passed

## Baseline

The runtime orchestration directly imported the RSS adapter and SQLite repository, constructed SQLite inside
`runtime/runs.py`, exposed reports as untyped dictionaries, and had no behavior Protocols, composition root,
publisher boundary, state/artifact ports, architecture tests or fake-only end-to-end proof.

Baseline tests passed, but the repository-wide validation also exposed nine stale documentation path references.
Those references were repaired without adding placeholder files.

## Implemented architecture

Stable runtime-checkable Protocols now live under `src/radar/ports/`:

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

The provider-neutral flow lives in `src/radar/application/run_daily.py`. Concrete implementations are selected
only in `src/radar/composition.py`; `src/radar/runtime/runs.py` is a compatibility façade for the existing CLI
and Python entrypoints.

Strict Pydantic models now protect `RadarReportV2`, `WebArtifactV1` and publication receipts; evaluation/runtime
DTOs are typed and frozen. Unknown/provider response fields are rejected. The RSS adapter no longer places its
transport name in canonical document facts, and `Document` accepts only typed source roles and numeric
measurement facts in canonical semantic namespaces rather than arbitrary provider mappings.
`schemas/report.schema.json` is generated from the typed report model and guarded by a drift test; executable
validation rejects missing `signals` or `evaluation_audit` on current canonical payloads.

## Concrete implementations wired for the current runtime

```text
Source: fixture or registry-backed public RSS/Atom
Evaluator: deterministic rules
Documents/events/indicators: in-memory repositories
Reports: in-memory or optional SQLite repository
State: in-memory store
Web artifacts: in-memory store
Publisher: disabled no-op publisher
```

Optional AI, collection-aggregator and filesystem-artifact integrations fail closed when enabled because their
concrete implementations do not yet exist. When disabled, the composition root does not import or require them.
The legacy fixture-only availability flag is isolated from production integration selection.

## Replaceability proof

`tests/integration/test_fake_only_application.py` executes:

```text
FakeSourceAdapter
→ document/event repositories
→ FakeIntelligenceEvaluator
→ strict and cross-field RadarReportV2 validation
→ InMemoryReportRepository + indicator repository
→ InMemoryStateStore + in-memory WebArtifactStore
→ FakePublisher
```

During that run, built-in/Path/os filesystem operations, SQLite connection creation, socket/DNS access,
`urllib.request.urlopen`, and OpenAI imports are patched to fail. The flow still passes. Additional cases replace
the source adapter, evaluator, report/state/artifact storage, and publisher independently; deterministic replay
is byte-identical; an invalid cross-field report reaches none of the report/indicator/state/artifact/publisher
output ports.

## Architecture gates

The architecture suite fails when:

- any of the nine stable ports stops being a runtime-checkable Protocol or changes its locked behavior surface;
- application modules import concrete adapters, repositories, evaluators, stores, publishers, network/provider,
  SQLite or filesystem modules;
- the runtime compatibility façade imports adapters or concrete repositories directly;
- a canonical importable module cycle or top-level package cycle appears.

The existing GitHub workflow now installs the declared Python 3.12 project/dev dependencies and runs all four
test suites directly; architecture failures are blocking and are no longer hidden behind `continue-on-error`.

Tracked files whose stems are not valid Python identifiers, such as the pre-existing `models 2.py` copies, are
not importable modules and are excluded from the import graph. They were not deleted or normalized in this task.

## Migration and compatibility

No database schema migration is required for this boundary refactor. Existing migration files are unchanged.
`SqliteRunRepository.load_report()` remains available for raw legacy reads; typed repository reads migrate the
previous Runtime-v2 source-audit/indicator shape and mark its unavailable evaluation audit explicitly. New writes
are validated before persistence, and latest-report selection uses high-resolution write order rather than run-id
hash order, including repeated upserts. The runtime façade projects the prior source-audit aliases for legacy
callers while canonical parsing strips those aliases before typed use. Existing CLI commands, runtime helper
signatures, and the legacy source adapter configuration import remain available.

## Automated validation

```text
make validate
  unit: 28 passed
  integration: 16 passed
  contracts: 15 passed
  architecture: 4 passed
  runtime contract: passed
  source registry / OPML drift: passed
  CLI fixture smoke: passed
  doc-path/core/domain-pack/sync-matrix gates: passed

PYTHONPYCACHEPREFIX=/tmp/daily-market-radar-pyc PYTHONPATH=src python3 -m compileall -q src/radar
  passed

git diff --check
  passed

bash check_mount_integrity.sh
  passed
```

## Deliberately not claimed complete

This acceptance gate does not implement the remaining end-to-end attachment scope: FreshRSS/Safe Web/JSON/GDELT
production adapters, durable cross-day event/delta storage, API-assisted or chat-assisted evaluation, evaluation
cache/cost controls, filesystem web projection, Astro dashboard, production publishers, scheduler, durable state
backend, Pages deployment or the four requested stacked PRs. Current fixture/live-RSS completeness boundaries
remain partial and explicit.
No remote GitHub Actions run or pull request was created in this local implementation turn.

## Five-line receipt

```text
改了什麼：新增九個 stable ports、Protocol-injected application flow、composition root、strict report/web contracts、concrete memory/SQLite/no-op bindings與 replacement gates。
機器檢查：make validate 全綠，63 tests passed；compileall、git diff --check 與 mount integrity passed。
沒做什麼：未把尚不存在的 AI/chat/web dashboard/scheduler/Pages/production integrations宣稱完成，也未清理既有 * 2.* 重複檔。
影響誰：CLI/runtime 呼叫者維持相容；新 source/evaluator/storage/publisher 只需實作 port 並在 composition root 註冊。
Owner 如何驗證：執行 make validate，並檢視 tests/integration/test_fake_only_application.py 與 tests/architecture/test_ports_and_dependencies.py。
```
