from __future__ import annotations

from radar.domain.enums import DeltaType
from radar.domain.event_resolution import is_material_delta_type
from radar.domain.models import Event, ReportItem, stable_id
from radar.domain.scoring import explain_event_scores
from radar.pipeline.classify import assess_event


def plan_daily_items(events: list[Event]) -> list[ReportItem]:
    items: list[ReportItem] = []
    for event in events:
        doc = event.documents[0]
        assessment = assess_event(event)
        report_lane = assessment.lane
        signal_id = stable_id("sig", [event.event_id, "potential"]) if report_lane == "potential" else None
        scores = explain_event_scores(event)
        items.append(
            ReportItem.fixture(
                item_id=stable_id("item", [event.event_id, doc.primary_domain, report_lane]),
                event_id=event.event_id,
                signal_id=signal_id,
                primary_domain=doc.primary_domain,
                report_lane=report_lane,
                candidate_type=assessment.candidate_type,
                formation_level=assessment.formation_level,
                headline=doc.title,
                first_seen_at=event.first_seen_at,
                today_delta=_today_delta(event, doc.action, doc.object),
                importance_score=scores.importance.score,
                potential_score=scores.potential.score,
                confidence_score=scores.confidence.score,
                evidence_links=[document.evidence_link() for document in event.documents],
                direct_taiwan_evidence=[
                    document.evidence_link()
                    for document in event.documents
                    if document.macro_region == "Taiwan"
                ],
                taiwan_implication="" if doc.macro_region == "Taiwan" else "目前沒有台灣直接證據；台灣影響屬後續推論。",
                counterevidence=[
                    *scores.importance.counterevidence,
                    *scores.potential.counterevidence,
                    *scores.confidence.counterevidence,
                ],
                uncertainties=_uncertainties(report_lane, scores.confidence.score),
                next_watch=(
                    "追蹤獨立採用、採購、使用量、資金、跨區域擴散與可信反證。"
                    if report_lane == "potential"
                    else "追蹤後續官方更新、數值變化與可信反證。"
                ),
                score_explanation=scores.to_report_payload(),
            )
        )
    return items


def _today_delta(event: Event, action: str, obj: str) -> str:
    action_text = action or "事件"
    object_text = obj or "相關主題"
    if not event.deltas:
        return f"今日首次觀察到「{action_text}／{object_text}」的新證據。"
    delta = event.deltas[0]
    if delta.delta_type == DeltaType.NEW_EVENT.value:
        return f"今日新事件：在回看期間首次出現「{action_text}／{object_text}」證據。"
    if is_material_delta_type(delta.delta_type):
        changed = "、".join(delta.changed_fields) if delta.changed_fields else "證據"
        return f"今日實質新增：{changed} 發生變化（{delta.delta_type}）。"
    return f"今日沒有實質新增：{delta.reason}。"


def _uncertainties(report_lane: str, confidence_score: int) -> list[str]:
    uncertainties: list[str] = []
    if report_lane == "potential":
        uncertainties.append("仍是早期訊號，實際採用規模尚未確認。")
    if confidence_score < 70:
        uncertainties.append("信心受來源品質、獨立證據深度或量化資料不足限制。")
    return uncertainties
