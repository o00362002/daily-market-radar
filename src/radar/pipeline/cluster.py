from __future__ import annotations

from collections import defaultdict

from radar.domain.models import Document, Event, stable_id


def cluster_documents(documents: list[Document]) -> list[Event]:
    grouped: dict[tuple[str, str, str, str], list[Document]] = defaultdict(list)
    for document in documents:
        grouped[document.event_signature].append(document)

    events: list[Event] = []
    for signature, docs in grouped.items():
        ordered = sorted(docs, key=lambda doc: (doc.published_at, doc.document_id))
        event_id = stable_id("evt", list(signature))
        first_seen = ordered[0].fetched_at
        last_seen = ordered[-1].fetched_at
        events.append(
            Event(
                event_id=event_id,
                documents=ordered,
                first_seen_at=first_seen,
                last_seen_at=last_seen,
                last_material_delta_at=last_seen,
            )
        )
    return sorted(events, key=lambda event: event.event_id)
