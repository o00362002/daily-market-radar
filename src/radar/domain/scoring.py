from __future__ import annotations

from dataclasses import dataclass

from radar.domain.enums import DeltaType
from radar.domain.models import Event


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


MATERIAL_DELTA_TYPES = {
    DeltaType.NEW_EVENT.value,
    DeltaType.SAME_EVENT_NEW_DELTA.value,
    DeltaType.RELATED_STORYLINE_NEW_EVENT.value,
    DeltaType.TREND_EVIDENCE_ONLY.value,
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
    return any(delta.delta_type in MATERIAL_DELTA_TYPES for delta in event.deltas)


def explain_event_scores(event: Event) -> EventScoreExplanation:
    if not event.documents:
        empty = ScoreBreakdown(0, {"evidence": 0}, "No documents were attached to the event.", [])
        return EventScoreExplanation(empty, empty, empty)

    primary_document = event.documents[0]
    source_ids = {document.source_id for document in event.documents}
    regions = {document.macro_region for document in event.documents}
    material_delta = event_has_material_delta(event)
    is_new_event = any(delta.delta_type == DeltaType.NEW_EVENT.value for delta in event.deltas) or not event.deltas
    has_numeric_facts = any(tuple(document.facts) for document in event.documents)
    source_quality = 88 if source_ids & OFFICIAL_OR_PRIMARY_SOURCES else 66
    evidence_depth = min(100, 45 + 15 * len(event.documents) + 10 * len(source_ids))
    novelty = 90 if is_new_event else 82 if material_delta else 30
    numeric_support = 82 if has_numeric_facts else 55
    taiwan_relevance = 90 if "Taiwan" in regions else 45
    lane_fit = 78 if primary_document.lane == "top_down" else 68
    weak_signal_fit = 82 if primary_document.lane != "top_down" else 55

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
        "weak_signal_fit": weak_signal_fit,
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
        "Importance is derived from source quality, evidence depth, material novelty and lane fit.",
        [] if material_delta else ["No material delta was detected in the lookback window."],
    )
    potential = ScoreBreakdown(
        weighted_score(
            potential_components,
            {
                "novelty": 1.5,
                "weak_signal_fit": 1.3,
                "evidence_depth": 0.8,
                "numeric_support": 0.6,
            },
        ),
        potential_components,
        "Potential emphasizes novelty and weak-signal fit before evidence becomes mature.",
        [] if material_delta else ["Potential is capped because the event appears to be a replay."],
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
        "Confidence reflects source quality, independent evidence depth and numeric support.",
        [],
    )
    for breakdown in (importance, potential, confidence):
        breakdown.validate()
    return EventScoreExplanation(importance, potential, confidence)
