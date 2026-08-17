"""Indicator-only delta promotion for stable measurement endpoints.

Many structured datasets expose the newest observation at one canonical URL. The
core news resolver intentionally treats an identical URL as duplicate evidence,
but that ordering would hide a changed BLS/DefiLlama/Hyperliquid fact. This module
adds a narrow pipeline-level exception: only indicator-only events, only matching
stable URLs and event signatures, and only typed fact changes are promoted.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from radar.domain.enums import DeltaType
from radar.domain.event_resolution import EventResolutionOutcome, is_material_delta_type
from radar.domain.models import Document, Event, EventDelta


_METRIC_NAMESPACE_DELTA = {
    "funding": DeltaType.FUNDING_CHANGE.value,
    "hiring": DeltaType.HIRING_CHANGE.value,
    "supply": DeltaType.SUPPLY_CHAIN_CHANGE.value,
    "procurement": DeltaType.SUPPLY_CHAIN_CHANGE.value,
}


def indicator_measurement_delta(prior: Event, current: Event) -> EventDelta | None:
    """Return a material delta for changed indicator facts at one stable URL.

    The exception is deliberately narrower than generic event resolution. It does
    not promote news rewrites, URL changes, source-role metadata changes, or event
    signature drift.
    """

    if not prior.documents or not current.documents:
        return None
    if not all(document.lane == "indicator_only" for document in current.documents):
        return None
    if not all(document.lane == "indicator_only" for document in prior.documents):
        return None

    changed_fields: set[str] = set()
    for current_document in current.documents:
        for prior_document in prior.documents:
            if not _same_stable_measurement(prior_document, current_document):
                continue
            changed_fields.update(_changed_facts(prior_document, current_document))

    if not changed_fields:
        return None
    ordered = sorted(changed_fields)
    return EventDelta(
        delta_type=_metric_delta_type(ordered),
        changed_fields=ordered,
        reason="indicator-only structured facts changed at a stable canonical URL",
    )


def promote_indicator_measurement_deltas(
    outcome: EventResolutionOutcome,
    *,
    current_events: list[Event],
    prior_events: list[Event],
) -> EventResolutionOutcome:
    """Repair non-material resolver results when stable-url indicator facts changed."""

    current_by_id = {event.event_id: event for event in current_events}
    prior_by_id = {event.event_id: event for event in prior_events}
    record_by_current = {record.current_event_id: record for record in outcome.match_records}

    events = list(outcome.events)
    delta_counts = Counter(outcome.delta_type_counts)
    material_events = outcome.material_events
    unchanged_events = outcome.unchanged_events
    duplicate_only_events = outcome.duplicate_only_events
    title_only_changes_rejected = outcome.title_only_changes_rejected
    background_only_rejected = outcome.background_only_rejected
    changed = False

    for index, resolved in enumerate(events):
        record = record_by_current.get(resolved.event_id)
        if record is None or record.prior_event_id is None:
            continue
        current = current_by_id.get(record.current_event_id)
        prior = prior_by_id.get(record.prior_event_id)
        if current is None or prior is None:
            continue
        if resolved.deltas and any(is_material_delta_type(delta.delta_type) for delta in resolved.deltas):
            continue

        promoted = indicator_measurement_delta(prior, current)
        if promoted is None:
            continue

        original_type = resolved.deltas[0].delta_type if resolved.deltas else ""
        if original_type:
            delta_counts[original_type] -= 1
            if delta_counts[original_type] <= 0:
                del delta_counts[original_type]
        delta_counts[promoted.delta_type] += 1

        material_events += 1
        unchanged_events = max(0, unchanged_events - 1)
        if original_type == DeltaType.DUPLICATE_DOCUMENT.value:
            duplicate_only_events = max(0, duplicate_only_events - 1)
        elif original_type == DeltaType.NO_MATERIAL_CHANGE.value:
            title_only_changes_rejected = max(0, title_only_changes_rejected - 1)
        elif original_type == DeltaType.BACKGROUND_ONLY.value:
            background_only_rejected = max(0, background_only_rejected - 1)

        events[index] = replace(
            resolved,
            last_material_delta_at=current.last_seen_at,
            deltas=[promoted],
        )
        changed = True

    if not changed:
        return outcome
    return replace(
        outcome,
        events=events,
        delta_type_counts=dict(sorted(delta_counts.items())),
        material_events=material_events,
        unchanged_events=unchanged_events,
        duplicate_only_events=duplicate_only_events,
        title_only_changes_rejected=title_only_changes_rejected,
        background_only_rejected=background_only_rejected,
    )


def _same_stable_measurement(prior: Document, current: Document) -> bool:
    return bool(
        prior.url
        and prior.url == current.url
        and prior.source_id == current.source_id
        and prior.event_signature == current.event_signature
    )


def _changed_facts(prior: Document, current: Document) -> set[str]:
    keys = {key for key in prior.facts if key != "source_roles"}
    keys.update(key for key in current.facts if key != "source_roles")
    return {key for key in keys if prior.facts.get(key) != current.facts.get(key)}


def _metric_delta_type(changed_fields: list[str]) -> str:
    for field in changed_fields:
        namespace = field.split("_", 1)[0]
        if namespace in _METRIC_NAMESPACE_DELTA:
            return _METRIC_NAMESPACE_DELTA[namespace]
    return DeltaType.NEW_AMOUNT_OR_METRIC.value
