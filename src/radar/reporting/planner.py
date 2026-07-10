from __future__ import annotations

from radar.domain.enums import DeltaType
from radar.domain.event_resolution import is_material_delta_type
from radar.domain.models import Event, ReportItem, stable_id
from radar.domain.scoring import explain_event_scores


def plan_daily_items(events: list[Event]) -> list[ReportItem]:
    items: list[ReportItem] = []
    for event in events:
        doc = event.documents[0]
        report_lane = "major" if doc.lane == "top_down" else "potential"
        signal_id = stable_id("sig", [event.event_id, "potential"]) if report_lane == "potential" else None
        scores = explain_event_scores(event)
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
                today_delta=_today_delta(event, doc.action, doc.object),
                importance_score=scores.importance.score,
                potential_score=scores.potential.score,
                confidence_score=scores.confidence.score,
                evidence_links=[doc.evidence_link()],
                direct_taiwan_evidence=[doc.evidence_link()] if doc.macro_region == "Taiwan" else [],
                taiwan_implication="" if doc.macro_region == "Taiwan" else "No direct Taiwan evidence.",
                counterevidence=[
                    *scores.importance.counterevidence,
                    *scores.potential.counterevidence,
                    *scores.confidence.counterevidence,
                ],
                uncertainties=_uncertainties(report_lane, scores.confidence.score),
                next_watch="Check independent follow-up, material deltas, adoption and counterevidence.",
                score_explanation=scores.to_report_payload(),
            )
        )
    return items


def _today_delta(event: Event, action: str, obj: str) -> str:
    if not event.deltas:
        return f"New {action} evidence for {obj}."
    delta = event.deltas[0]
    if delta.delta_type == DeltaType.NEW_EVENT.value:
        return f"New event: first {action} evidence for {obj} in the lookback window."
    if is_material_delta_type(delta.delta_type):
        changed = ", ".join(delta.changed_fields) if delta.changed_fields else "evidence"
        return f"Material delta in {changed} ({delta.delta_type}): new {action} evidence for {obj}."
    return f"No material delta: {delta.reason}."


def _uncertainties(report_lane: str, confidence_score: int) -> list[str]:
    uncertainties: list[str] = []
    if report_lane == "potential":
        uncertainties.append("Early signal; adoption scale is not yet verified.")
    if confidence_score < 70:
        uncertainties.append("Confidence is limited by source quality, evidence depth or numeric support.")
    return uncertainties
