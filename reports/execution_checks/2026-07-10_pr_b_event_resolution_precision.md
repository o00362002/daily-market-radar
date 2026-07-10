# PR B — Event Resolution Precision

Base branch: `main` (`3311eeb`) · Branch: `feat/event-resolution-precision`

## 改了什麼 (What changed)

- **Provider-neutral `EventResolutionService`** (`src/radar/domain/event_resolution.py`): ordered,
  deterministic 7-strategy cross-day matching cascade — exact document id → canonical URL →
  content hash → exact event signature → normalized entity/action/object/location →
  source-independent structured fact overlap → bounded publication time window. No AI, embedding
  or external model. Every match emits an `EventMatchRecord`
  (strategy, confidence, reason, prior/current event id, matched/unresolved fields, observed_at).
  Ambiguous fuzzy matches are **not forced**: a new event is created and an `unresolved_match` recorded.
- **Expanded `DeltaType` taxonomy** (20 members) + deterministic classifier. Title/summary rewrite
  alone is `no_material_change` (non-material, supporting difference only); numeric change comes from
  canonical structured measurement facts (`new_amount_or_metric`, or `funding_change` /
  `hiring_change` / `supply_chain_change` by metric namespace); a new independent higher-role
  publisher yields `new_source_confirmation` (same-publisher duplicate does not).
- **`EventResolutionAuditV1`** added to strict `RadarReportV2` (events_observed, new/matched,
  material/unchanged, duplicate-only, unresolved_matches, match_strategy_counts, delta_type_counts,
  title_only_changes_rejected, background_only_rejected) with legacy migration + regenerated
  `schemas/report.schema.json`.
- **`UnitOfWork` run-transaction port** (`src/radar/ports/persistence.py`) + `RunPersistenceBatch`.
  SQLite implementation commits documents, events, event-document relations, deltas, report,
  indicators, state checkpoint and match provenance in **one transaction**; any failure rolls the
  whole run back and never overwrites the last-valid report. Ports extended 9 → 10.
- Migration `0004_event_resolution.sql` (durable `event_matches` provenance).

## 機器檢查 (Machine checks — all green)

- `unittest discover tests`: **87 passed** (68 prior + 17 new `test_event_resolution` + 2 atomicity).
- `make validate`: check-core / check-domain-packs / check-sync-matrix / check-doc-paths green;
  runtime-contract valid; `sources validate` + fixture `run-daily` smoke green; OPML projection stable.
- Architecture gates green: all 10 ports are runtime-checkable Protocols with stable surfaces;
  application imports no concrete infrastructure; module + package import graphs acyclic.
- Canonical-model gate green: `EventResolutionAuditV1` strict + `extra=forbid`, no provider tokens;
  `schemas/report.schema.json` regenerated from the typed contract.

## 沒做什麼 (Out of scope for PR B)

- Source adapters, source health repository and deterministic evaluators (PR C).
- AI / chat-assisted evaluation modes (PR D). Web projection / Astro (PR E). Scheduler / Pages (PR F).
- The memory backend's atomicity is validation-gated + snapshot/restore; SQLite provides true
  transactional rollback (the durable production guarantee, tested).

## 會影響誰 (Who is affected)

- `ApplicationDependencies` gains a required `unit_of_work` collaborator; the composition root and
  both integration test harnesses were updated. Downstream PRs build on this atomic write boundary.
- Cross-day delta labels are finer: numeric change now reports `new_amount_or_metric` rather than the
  legacy `same_event_new_delta`. Existing behavior tests were updated to the improved taxonomy.

## 你可以驗證 (How to verify)

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
make validate PYTHON=python
PYTHONPATH=src python -m radar.cli run-daily --mode fixture --date 2026-07-10 | python -c \
  "import sys,json;print(json.load(sys.stdin)['event_resolution_audit'])"
```
