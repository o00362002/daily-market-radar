from __future__ import annotations

from radar.domain.models import Event, ReportItem, stable_id


def plan_daily_items(events: list[Event]) -> list[ReportItem]:
    items: list[ReportItem] = []
    for event in events:
        doc = event.documents[0]
        report_lane = "major" if doc.lane == "top_down" else "potential"
        signal_id = stable_id("sig", [event.event_id, "potential"]) if report_lane == "potential" else None
        items.append(
            ReportItem.fixture(
                item_id=stable_id("item", [event.event_id, doc.primary_domain, report_lane]),
                event_id=event.event_id,
                signal_id=signal_id,
                primary_domain=doc.primary_domain,
                report_lane=report_lane,
                candidate_type="新應用" if report_lane == "potential" else None,
                formation_level="弱訊號" if report_lane == "potential" else None,
                headline=doc.title,
                first_seen_at=event.first_seen_at,
                today_delta=f"New {doc.action} evidence for {doc.object}.",
                importance_score=70 if report_lane == "major" else 45,
                potential_score=55 if report_lane == "major" else 75,
                confidence_score=80 if doc.source_id in {"openai_news", "twse", "bls"} else 65,
                evidence_links=[doc.evidence_link()],
                direct_taiwan_evidence=[doc.evidence_link()] if doc.macro_region == "Taiwan" else [],
                taiwan_implication="" if doc.macro_region == "Taiwan" else "No direct Taiwan evidence.",
                uncertainties=[] if report_lane == "major" else ["Early signal; adoption scale is not yet verified."],
                next_watch="Check independent follow-up, material deltas, adoption and counterevidence.",
            )
        )
    return items
