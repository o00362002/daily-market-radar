# Event Resolution (PR B)

Provider-neutral, deterministic cross-day event resolution. No AI, embedding, network or
persistence dependency lives in `radar.domain.event_resolution`.

## Matching cascade

Today's clustered events are matched against prior events using an ordered cascade. The first
applicable (highest-confidence) strategy wins:

| # | Strategy | Confidence | Basis |
|---|----------|-----------|-------|
| 1 | `exact_document_id` | 1.00 | shared `document_id` |
| 2 | `canonical_url` | 0.98 | shared canonical URL |
| 3 | `content_hash` | 0.96 | shared content hash |
| 4 | `exact_event_signature` | 0.92 | identical `(entity, action, object, location)` |
| 5 | `normalized_entity_action_object_location` | 0.80 | entity + object match with action **or** location |
| 6 | `source_independent_structured_fact_overlap` | 0.60 | shared canonical measurement metric across independent publishers |
| 7 | `bounded_publication_time_window` | 0.45 | same entity within a bounded window |

High-confidence strategies (≥ 0.90) merge unambiguously. Fuzzy strategies merge only when
unambiguous; if another prior event competes within 0.15 confidence, the match is **unresolved** —
a new event is created and an `unresolved_match` record is emitted. Matches are never forced.

Every decision produces an `EventMatchRecord`: `strategy`, `confidence`, `reason`,
`prior_event_id`, `current_event_id`, `matched_fields`, `unresolved_fields`, `observed_at`, and is
persisted durably in the `event_matches` table.

## Delta taxonomy

`DeltaType` covers new_event, duplicate_document, no_material_change, new_source_confirmation,
new_entity, new_amount_or_metric, policy_stage_change, launch_or_release, pilot_to_production,
new_region, adoption_expansion, funding_change, hiring_change, supply_chain_change, counterevidence,
delay, cancellation, invalidation, background_only, unresolved (plus retained legacy members).

Rules:

- **Title/summary rewrite alone is not material** — it becomes `no_material_change` and is counted in
  `title_only_changes_rejected`. Text differences are supporting evidence only.
- **Numeric change must come from canonical structured measurement facts** — namespace decides the
  family (`funding_*` → funding_change, `hiring_*` → hiring_change, `supply_*`/`procurement_*` →
  supply_chain_change, otherwise new_amount_or_metric).
- **A new source only confirms** when the publisher is independent (different domain) and its source
  role is at least as authoritative as the prior best role. Same publisher, different URL is not
  independent confirmation.
- When a change cannot be reliably classified it is left `unresolved` rather than guessed.

## Audit

`EventResolutionAuditV1` in `RadarReportV2` reports events_observed, new_events,
matched_existing_events, material_events, unchanged_events, duplicate_only_events, unresolved_matches,
match_strategy_counts, delta_type_counts, title_only_changes_rejected and background_only_rejected.
`events_observed == new_events + matched_existing_events` and
`material_events + unchanged_events == events_observed` are validated invariants.

## Atomic persistence

`UnitOfWork.commit_run(RunPersistenceBatch)` persists documents, events, event-document relations,
deltas, report, indicator observations, state checkpoint and match provenance in a single
transaction. Any validation or persistence failure rolls the entire run back: the last valid report
is not overwritten, no half-written report remains, and event history is not corrupted. SQLite is the
first implementation; the in-memory backend snapshots and restores on failure.
