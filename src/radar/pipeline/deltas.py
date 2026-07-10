from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from radar.domain.enums import DeltaType
from radar.domain.models import Document, Event, EventDelta
from radar.domain.scoring import event_has_material_delta


def classify_event_delta(prior: Document, current: Document) -> EventDelta:
    if prior.url == current.url or prior.content_hash == current.content_hash:
        return EventDelta(DeltaType.DUPLICATE_DOCUMENT.value, [], "same url or content hash")
    if prior.event_signature != current.event_signature:
        return EventDelta(DeltaType.SAME_TOPIC_DIFFERENT_EVENT.value, [], "different event signature")
    changed = sorted(
        key for key in set(prior.facts) | set(current.facts) if prior.facts.get(key) != current.facts.get(key)
    )
    if changed:
        return EventDelta(DeltaType.SAME_EVENT_NEW_DELTA.value, changed, "material fact changed")
    text_changed = []
    if prior.title_hash != current.title_hash:
        text_changed.append("title")
    if prior.summary != current.summary:
        text_changed.append("summary")
    if text_changed:
        return EventDelta(
            DeltaType.SAME_EVENT_NEW_DELTA.value,
            sorted(text_changed),
            "material narrative evidence changed",
        )
    return EventDelta(DeltaType.SAME_EVENT_SAME_FACTS.value, [], "same event without material delta")


def classify_event_material_delta(prior: Event, current: Event) -> EventDelta:
    if not prior.documents:
        return EventDelta(DeltaType.NEW_EVENT.value, ["event"], "no prior documents were attached")
    baseline_documents = _latest_documents(prior.documents)
    deltas: list[EventDelta] = []
    for current_document in current.documents:
        for prior_document in baseline_documents:
            deltas.append(classify_event_delta(prior_document, current_document))
    material = [delta for delta in deltas if delta.delta_type == DeltaType.SAME_EVENT_NEW_DELTA.value]
    if material:
        changed_fields = sorted({field for delta in material for field in delta.changed_fields})
        reasons = sorted({delta.reason for delta in material})
        return EventDelta(
            DeltaType.SAME_EVENT_NEW_DELTA.value,
            changed_fields,
            "; ".join(reasons),
        )
    if deltas and all(delta.delta_type == DeltaType.DUPLICATE_DOCUMENT.value for delta in deltas):
        return EventDelta(DeltaType.DUPLICATE_DOCUMENT.value, [], "all current evidence is duplicate")
    return EventDelta(DeltaType.SAME_EVENT_SAME_FACTS.value, [], "same event without material delta")


def reconcile_cross_day_events(current_events: list[Event], prior_events: list[Event]) -> list[Event]:
    prior_by_id = {event.event_id: event for event in prior_events}
    reconciled: list[Event] = []
    for current in current_events:
        prior = prior_by_id.get(current.event_id)
        if prior is None:
            delta = EventDelta(DeltaType.NEW_EVENT.value, ["event"], "first observation in lookback window")
            reconciled.append(replace(current, deltas=[delta]))
            continue

        delta = classify_event_material_delta(prior, current)
        material = event_has_material_delta(replace(current, deltas=[delta]))
        reconciled.append(
            Event(
                event_id=current.event_id,
                documents=current.documents,
                first_seen_at=prior.first_seen_at,
                last_seen_at=_max_timestamp(prior.last_seen_at, current.last_seen_at),
                last_material_delta_at=current.last_seen_at if material else prior.last_material_delta_at,
                status="active",
                deltas=[delta],
            )
        )
    return sorted(reconciled, key=lambda event: event.event_id)


def material_events(events: list[Event]) -> list[Event]:
    return [event for event in events if event_has_material_delta(event)]


def _max_timestamp(left: str, right: str) -> str:
    left_dt = _parse_timestamp(left)
    right_dt = _parse_timestamp(right)
    return left if left_dt >= right_dt else right


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _latest_documents(documents: list[Document]) -> list[Document]:
    if not documents:
        return []
    latest = max(_parse_timestamp(document.fetched_at) for document in documents)
    return [document for document in documents if _parse_timestamp(document.fetched_at) == latest]
