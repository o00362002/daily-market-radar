from __future__ import annotations

from dataclasses import dataclass

from radar.domain.enums import DeltaType
from radar.domain.event_resolution import is_material_delta_type
from radar.domain.models import Event
from radar.pipeline.classify import assess_event


@dataclass(frozen=True)
class ScoreBreakdown:
    score: int
    components: dict[str, int]
    rationale: str
    counterevidence: list[str]

    def validate(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError(f"score out of range: {self.score}")
        for name, value in self.components.items():
            if not 0 <= value <= 100:
                raise ValueError(f"component {name} out of range: {value}")


def weighted_score(components: dict[str, int], weights: dict[str, float]) -> int:
    if not components:
        return 0
    total_weight = sum(weights.get(name, 1.0) for name in components)
    if total_weight <= 0:
        raise ValueError("total weight must be positive")
    total = sum(value * weights.get(name, 1.0) for name, value in components.items())
    return round(total / total_weight)


@dataclass(frozen=True)
class EventScoreExplanation:
    importance: ScoreBreakdown
    potential: ScoreBreakdown
    confidence: ScoreBreakdown

    def to_report_payload(self) -> dict[str, object]:
        return {
            "importance": dict(self.importance.components),
            "potential": dict(self.potential.components),
            "confidence": dict(self.confidence.components),
            "rationale": " ".join(
                rationale
                for rationale in (
                    self.importance.rationale,
                    self.potential.rationale,
                    self.confidence.rationale,
                )
                if rationale
            ),
        }


OFFICIAL_OR_PRIMARY_SOURCES = {
    "bls",
    "federal_reserve",
    "openai_news",
    "twse",
}


def event_has_material_delta(event: Event) -> bool:
    if not event.deltas:
        return True
    return any(is_material_delta_type(delta.delta_type) for delta in event.deltas)


def explain_event_scores(event: Event) -> EventScoreExplanation:
    if not event.documents:
        empty = ScoreBreakdown(0, {"evidence": 0}, "事件沒有附加文件。", [])
        return EventScoreExplanation(empty, empty, empty)

    primary_document = event.documents[0]
    source_ids = {document.source_id for document in event.documents}
    regions = {document.macro_region for document in event.documents}
    material_delta = event_has_material_delta(event)
    is_new_event = any(delta.delta_type == DeltaType.NEW_EVENT.value for delta in event.deltas) or not event.deltas
    has_numeric_facts = any(tuple(document.facts) for document in event.documents)
    assessment = assess_event(event)

    source_quality = 88 if source_ids & OFFICIAL_OR_PRIMARY_SOURCES else 66
    evidence_depth = min(100, 45 + 15 * len(event.documents) + 10 * len(source_ids))
    novelty = 90 if is_new_event else 82 if material_delta else 30
    numeric_support = 82 if has_numeric_facts else 55
    taiwan_relevance = 90 if "Taiwan" in regions else 45
    lane_fit = 80 if assessment.lane == "major" else 72
    content_signal_fit = max(35, assessment.feature_score) if assessment.lane == "potential" else 42

    importance_components = {
        "source_quality": source_quality,
        "evidence_depth": evidence_depth,
        "novelty": novelty,
        "numeric_support": numeric_support,
        "lane_fit": lane_fit,
        "taiwan_relevance": taiwan_relevance,
    }
    potential_components = {
        "novelty": novelty,
        "content_signal_fit": min(100, content_signal_fit),
        "evidence_depth": evidence_depth,
        "numeric_support": numeric_support,
    }
    confidence_components = {
        "source_quality": source_quality,
        "evidence_depth": evidence_depth,
        "numeric_support": numeric_support,
    }

    importance = ScoreBreakdown(
        weighted_score(
            importance_components,
            {
                "source_quality": 1.4,
                "evidence_depth": 1.0,
                "novelty": 1.2,
                "numeric_support": 0.8,
                "lane_fit": 1.1,
                "taiwan_relevance": 0.5,
            },
        ),
        importance_components,
        "重要性依來源品質、證據深度、今日新增與重大事件適配度計算。",
        [] if material_delta else ["回看期間沒有偵測到實質新增。"],
    )
    potential = ScoreBreakdown(
        weighted_score(
            potential_components,
            {
                "novelty": 1.5,
                "content_signal_fit": 1.5,
                "evidence_depth": 0.8,
                "numeric_support": 0.6,
            },
        ),
        potential_components,
        f"潛力分數由內容型弱訊號、今日新增與證據深度計算；判斷依據：{assessment.rationale}",
        [] if material_delta else ["事件看似重播，因此潛力不應因來源角色被放大。"],
    )
    confidence = ScoreBreakdown(
        weighted_score(
            confidence_components,
            {
                "source_quality": 1.5,
                "evidence_depth": 1.0,
                "numeric_support": 0.8,
            },
        ),
        confidence_components,
        "信心反映來源品質、獨立證據深度與量化支持。",
        [],
    )
    for breakdown in (importance, potential, confidence):
        breakdown.validate()
    return EventScoreExplanation(importance, potential, confidence)
