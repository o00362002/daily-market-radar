from __future__ import annotations

from radar.domain.models import Event, ReportItem, stable_id


def plan_daily_items(events: list[Event]) -> list[ReportItem]:
    items: list[ReportItem] = []
    for event in events:
        doc = event.documents[0]
        items.append(
            ReportItem.fixture(
                item_id=stable_id("item", [event.event_id, doc.primary_domain]),
                event_id=event.event_id,
                primary_domain=doc.primary_domain,
                headline=doc.title,
                first_seen_at=event.first_seen_at,
                today_delta=f"New {doc.action} evidence for {doc.object}.",
                importance_score=70 if doc.lane == "top_down" else 45,
                potential_score=55 if doc.lane == "top_down" else 75,
                confidence_score=80 if doc.source_id in {"openai_news", "twse", "bls"} else 65,
                evidence_links=[doc.evidence_link()],
                direct_taiwan_evidence=[doc.evidence_link()] if doc.macro_region == "Taiwan" else [],
                taiwan_implication="" if doc.macro_region == "Taiwan" else "No direct Taiwan evidence.",
                uncertainties=[],
                next_watch="Check independent follow-up and material deltas.",
            )
        )
    return items
