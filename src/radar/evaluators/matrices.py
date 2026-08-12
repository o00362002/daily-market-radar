"""Deterministic, feature-traced evaluators for fixed report matrices."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from radar.contracts.report import MatrixObservationV1, StructuralIndicatorComponentV1, StructuralIndicatorEvidenceV1, StructuralIndicatorObservationV1
from radar.domain.models import Event, normalize_text
from radar.evaluators.matrix_features import CRYPTO_FEATURES, RETAIL_FEATURES, STRUCTURAL_COMPONENTS, STRUCTURAL_FEATURES


def _event_text(event: Event) -> str:
    return normalize_text(" ".join(part for d in event.documents for part in (d.title, d.action, d.object, d.summary, " ".join(d.entities))))


def _event_metrics(event: Event) -> set[str]:
    return {metric.split("_", 1)[0] for d in event.documents for metric in d.facts if metric != "source_roles"}


def _event_domains(event: Event) -> set[str]:
    return {d.primary_domain for d in event.documents if d.primary_domain}


def _keyword_hit(text: str, keywords: set[str]) -> list[str]:
    """Match Latin terms on token boundaries and CJK terms as phrases."""
    hits: list[str] = []
    for keyword in keywords:
        if any("\u3400" <= char <= "\u9fff" for char in keyword):
            matched = keyword in text
        else:
            matched = re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", text, flags=re.IGNORECASE) is not None
        if matched:
            hits.append(keyword)
    return sorted(hits)


def _event_evidence(event: Event, *, direction: str, hits: list[str]) -> StructuralIndicatorEvidenceV1:
    d = event.documents[0]
    summary = d.summary.strip() or f"{d.action or '事件'}：{d.object or d.title}。"
    return StructuralIndicatorEvidenceV1(event_id=event.event_id, headline=d.title, summary=f"{summary}（命中：{'、'.join(hits)}）", direction=direction)


def _component_observations(events: list[Event], indicator_id: str) -> list[StructuralIndicatorComponentV1]:
    rows: list[StructuralIndicatorComponentV1] = []
    for component_id, label, support_keywords, counter_keywords in STRUCTURAL_COMPONENTS.get(indicator_id, ()):
        support_events: list[Event] = []
        counter_events: list[Event] = []
        evidence: list[StructuralIndicatorEvidenceV1] = []
        for event in events:
            text = _event_text(event)
            support_hits = _keyword_hit(text, support_keywords)
            counter_hits = _keyword_hit(text, counter_keywords)
            if support_hits:
                support_events.append(event)
                evidence.append(_event_evidence(event, direction="toward", hits=support_hits))
            if counter_hits:
                counter_events.append(event)
                evidence.append(_event_evidence(event, direction="against", hits=counter_hits))
        support_score = min(100, 25 * len({e.event_id for e in support_events}))
        counter_score = min(100, 25 * len({e.event_id for e in counter_events}))
        if not evidence:
            direction, score, missing = "insufficient", 0, ["本次沒有足夠新聞或量化資料支撐此細分指標。"]
        else:
            direction = "toward" if support_score > counter_score else "against" if counter_score > support_score else "mixed"
            score, missing = max(0, min(100, round(50 + (support_score - counter_score) / 2))), []
        rows.append(StructuralIndicatorComponentV1(component_id=component_id, label=label, direction=direction, score=score, support_score=support_score, counter_score=counter_score, evidence=evidence, missing_data=missing))
    return rows


def _evaluate_matrix(events: list[Event], keys: list[str], features: dict[str, tuple[set[str], set[str]]], domain: str, empty_gap: str) -> dict[str, MatrixObservationV1]:
    observations: dict[str, MatrixObservationV1] = {}
    for key in keys:
        namespaces, keywords = features.get(key, (set(), set()))
        signal_ids: list[str] = []
        data_checked: list[str] = []
        for event in events:
            if domain not in _event_domains(event):
                continue
            metric_hits = sorted(_event_metrics(event) & namespaces)
            keyword_hits = _keyword_hit(_event_text(event), keywords)
            if metric_hits or keyword_hits:
                signal_ids.append(event.event_id)
                data_checked += [f"metric:{x}" for x in metric_hits] + [f"keyword:{x}" for x in keyword_hits]
        observations[key] = MatrixObservationV1(
            status="observed" if signal_ids else "insufficient",
            signal_ids=sorted(set(signal_ids)),
            data_checked=sorted(set(data_checked)),
            gap="" if signal_ids else empty_gap,
        )
    return observations


def evaluate_retail_matrix(events: list[Event], keys: list[str]) -> dict[str, MatrixObservationV1]:
    return _evaluate_matrix(events, keys, RETAIL_FEATURES, "retail_consumer_fashion", "no retail measurement or keyword evidence in this run")


def evaluate_crypto_matrix(events: list[Event], keys: list[str]) -> dict[str, MatrixObservationV1]:
    return _evaluate_matrix(events, keys, CRYPTO_FEATURES, "crypto_rwa_agent_payments", "no crypto measurement or keyword evidence in this run")


def _observation_date(observation: StructuralIndicatorObservationV1) -> datetime:
    parsed = datetime.fromisoformat(observation.observation_date.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def rolling_summary(observations: list[StructuralIndicatorObservationV1], *, as_of: str) -> dict[str, dict[str, float | int | str]]:
    as_of_dt = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    if as_of_dt.tzinfo is None:
        as_of_dt = as_of_dt.replace(tzinfo=timezone.utc)
    ordered = sorted(observations, key=_observation_date)

    def window(days: int | None) -> dict[str, float | int | str]:
        scoped = ordered[-1:] if days is None else [o for o in ordered if as_of_dt - timedelta(days=days) <= _observation_date(o) <= as_of_dt]
        rated = [o for o in scoped if o.direction != "insufficient"]
        if not rated:
            return {"status": "insufficient", "observations": len(scoped), "avg_support": 0, "avg_counter": 0}
        return {"status": "observed", "observations": len(rated), "avg_support": round(sum(o.support_score for o in rated) / len(rated), 2), "avg_counter": round(sum(o.counter_score for o in rated) / len(rated), 2)}

    return {"current": window(None), "rolling_7d": window(7), "rolling_30d": window(30), "rolling_90d": window(90)}


def evaluate_structural_indicators(events: list[Event], indicator_ids: list[str], *, observation_date: str) -> list[StructuralIndicatorObservationV1]:
    observations: list[StructuralIndicatorObservationV1] = []
    for indicator_id in indicator_ids:
        features = STRUCTURAL_FEATURES.get(indicator_id, {"support": set(), "counter": set()})
        support_ids: list[str] = []
        counter_ids: list[str] = []
        for event in events:
            text = _event_text(event)
            if _keyword_hit(text, features["support"]):
                support_ids.append(event.event_id)
            if _keyword_hit(text, features["counter"]):
                counter_ids.append(event.event_id)
        components = _component_observations(events, indicator_id)
        if not support_ids and not counter_ids:
            observations.append(StructuralIndicatorObservationV1(indicator_id=indicator_id, observation_date=observation_date, direction="insufficient", support_score=0, counter_score=0, confidence="insufficient", supporting_signal_ids=[], counter_signal_ids=[], missing_data=["no supporting or counter evidence observed this run"], one_sentence_read="Insufficient verified evidence for a directional update.", next_verification=["run indicator-specific evidence checks"], evaluation_mode="deterministic", components=components))
            continue
        support_score = min(100, 20 * len(set(support_ids)))
        counter_score = min(100, 20 * len(set(counter_ids)))
        direction = "supporting" if support_score > counter_score else "counter" if counter_score > support_score else "mixed"
        confidence = abs(support_score - counter_score)
        read = "Deterministic evidence is high-conflict; no directional confidence should be inferred." if direction == "mixed" else f"Deterministic typed evidence leans {direction} for this indicator."
        verify = "resolve conflicting evidence with structured measurements and independent sources" if direction == "mixed" else "confirm with structured measurement facts and independent sources"
        observations.append(StructuralIndicatorObservationV1(indicator_id=indicator_id, observation_date=observation_date, direction=direction, support_score=support_score, counter_score=counter_score, confidence=confidence, supporting_signal_ids=sorted(set(support_ids)), counter_signal_ids=sorted(set(counter_ids)), missing_data=[], one_sentence_read=read, next_verification=[verify], evaluation_mode="deterministic", components=components))
    return observations
