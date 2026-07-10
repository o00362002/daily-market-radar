from __future__ import annotations

from radar.domain.enums import DeltaType
from radar.domain.models import Document, EventDelta


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
    return EventDelta(DeltaType.SAME_EVENT_SAME_FACTS.value, [], "same event without material delta")
