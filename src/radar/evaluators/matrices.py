"""Deterministic, feature-traced evaluators for fixed report matrices."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from radar.contracts.report import MatrixObservationV1, StructuralIndicatorComponentV1, StructuralIndicatorEvidenceV1, StructuralIndicatorObservationV1
from radar.domain.models import Event
from radar.evaluators.matrix_features import CRYPTO_FEATURES, RETAIL_FEATURES, STRUCTURAL_COMPONENTS, STRUCTURAL_COMPONENT_GATES
from radar.evaluators.structural_gates import (
    event_domains as _event_domains,
    event_metric_namespaces as _event_metrics,
    event_text as _event_text,
    keyword_hit as _keyword_hit,
    qualify_structural_event,
)


def _event_evidence(
    event: Event,
    *,
    direction: str,
    hits: list[str],
    measurement_hits: tuple[str, ...],
) -> StructuralIndicatorEvidenceV1:
    document = event.documents[0]
    summary = document.summary.strip() or f"{document.action or '事件'}：{document.object or document.title}。"
    trace = (
        f"候選：{'、'.join(hits)}；量測：{'、'.join(measurement_hits)}；"
        "gate：domain→proposition→measurement"
    )
    return StructuralIndicatorEvidenceV1(
        event_id=event.event_id,
        headline=document.title,
        summary=f"{summary}（{trace}）",
        direction=direction,
    )


def _component_observations(
    events: list[Event],
    indicator_id: str,
) -> list[StructuralIndicatorComponentV1]:
    rows: list[StructuralIndicatorComponentV1] = []
    indicator_gates = STRUCTURAL_COMPONENT_GATES.get(indicator_id, {})
    for component_id, label, support_keywords, counter_keywords in STRUCTURAL_COMPONENTS.get(indicator_id, ()):
        support_events: list[Event] = []
        counter_events: list[Event] = []
        evidence: list[StructuralIndicatorEvidenceV1] = []
        rejected = {"domain": 0, "entailment": 0, "measurement": 0}
        gate = indicator_gates.get(component_id, {})

        for event in events:
            text = _event_text(event)
            support_hits = _keyword_hit(text, support_keywords)
            counter_hits = _keyword_hit(text, counter_keywords)

            support_decision = qualify_structural_event(
                event,
                text=text,
                candidate_hits=support_hits,
                gate=gate,
                direction="support",
            )
            if support_decision.qualified:
                support_events.append(event)
                evidence.append(
                    _event_evidence(
                        event,
                        direction="toward",
                        hits=support_hits,
                        measurement_hits=support_decision.measurement_hits,
                    )
                )
            elif support_hits and support_decision.failed_stage in rejected:
                rejected[support_decision.failed_stage] += 1

            counter_decision = qualify_structural_event(
                event,
                text=text,
                candidate_hits=counter_hits,
                gate=gate,
                direction="counter",
            )
            if counter_decision.qualified:
                counter_events.append(event)
                evidence.append(
                    _event_evidence(
                        event,
                        direction="against",
                        hits=counter_hits,
                        measurement_hits=counter_decision.measurement_hits,
                    )
                )
            elif counter_hits and counter_decision.failed_stage in rejected:
                rejected[counter_decision.failed_stage] += 1

        support_score = min(100, 25 * len({event.event_id for event in support_events}))
        counter_score = min(100, 25 * len({event.event_id for event in counter_events}))
        if not evidence:
            direction, score = "insufficient", 0
            rejected_parts = [f"{stage}={count}" for stage, count in rejected.items() if count]
            detail = "、".join(rejected_parts) if rejected_parts else "沒有候選事件"
            missing = [f"沒有通過 domain→proposition→measurement gate 的證據（{detail}）。"]
        else:
            direction = (
                "toward"
                if support_score > counter_score
                else "against"
                if counter_score > support_score
                else "mixed"
            )
            score = max(0, min(100, round(50 + (support_score - counter_score) / 2)))
            missing = []

        rows.append(
            StructuralIndicatorComponentV1(
                component_id=component_id,
                label=label,
                direction=direction,
                score=score,
                support_score=support_score,
                counter_score=counter_score,
                evidence=evidence,
                missing_data=missing,
            )
        )
    return rows


def _evaluate_matrix(
    events: list[Event],
    keys: list[str],
    features: dict[str, tuple[set[str], set[str]]],
    domain: str,
    empty_gap: str,
) -> dict[str, MatrixObservationV1]:
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
                data_checked += [f"metric:{value}" for value in metric_hits]
                data_checked += [f"keyword:{value}" for value in keyword_hits]
        observations[key] = MatrixObservationV1(
            status="observed" if signal_ids else "insufficient",
            signal_ids=sorted(set(signal_ids)),
            data_checked=sorted(set(data_checked)),
            gap="" if signal_ids else empty_gap,
        )
    return observations


def evaluate_retail_matrix(events: list[Event], keys: list[str]) -> dict[str, MatrixObservationV1]:
    return _evaluate_matrix(
        events,
        keys,
        RETAIL_FEATURES,
        "retail_consumer_fashion",
        "no retail measurement or keyword evidence in this run",
    )


def evaluate_crypto_matrix(events: list[Event], keys: list[str]) -> dict[str, MatrixObservationV1]:
    return _evaluate_matrix(
        events,
        keys,
        CRYPTO_FEATURES,
        "crypto_rwa_agent_payments",
        "no crypto measurement or keyword evidence in this run",
    )


def _observation_date(observation: StructuralIndicatorObservationV1) -> datetime:
    parsed = datetime.fromisoformat(observation.observation_date.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def rolling_summary(
    observations: list[StructuralIndicatorObservationV1],
    *,
    as_of: str,
) -> dict[str, dict[str, float | int | str]]:
    as_of_dt = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    if as_of_dt.tzinfo is None:
        as_of_dt = as_of_dt.replace(tzinfo=timezone.utc)
    ordered = sorted(observations, key=_observation_date)

    def window(days: int | None) -> dict[str, float | int | str]:
        scoped = (
            ordered[-1:]
            if days is None
            else [
                observation
                for observation in ordered
                if as_of_dt - timedelta(days=days) <= _observation_date(observation) <= as_of_dt
            ]
        )
        rated = [observation for observation in scoped if observation.direction != "insufficient"]
        if not rated:
            return {
                "status": "insufficient",
                "observations": len(scoped),
                "avg_support": 0,
                "avg_counter": 0,
            }
        return {
            "status": "observed",
            "observations": len(rated),
            "avg_support": round(sum(observation.support_score for observation in rated) / len(rated), 2),
            "avg_counter": round(sum(observation.counter_score for observation in rated) / len(rated), 2),
        }

    return {
        "current": window(None),
        "rolling_7d": window(7),
        "rolling_30d": window(30),
        "rolling_90d": window(90),
    }


def evaluate_structural_indicators(
    events: list[Event],
    indicator_ids: list[str],
    *,
    observation_date: str,
) -> list[StructuralIndicatorObservationV1]:
    observations: list[StructuralIndicatorObservationV1] = []
    for indicator_id in indicator_ids:
        components = _component_observations(events, indicator_id)
        support_ids = sorted(
            {
                evidence.event_id
                for component in components
                for evidence in component.evidence
                if evidence.direction == "toward"
            }
        )
        counter_ids = sorted(
            {
                evidence.event_id
                for component in components
                for evidence in component.evidence
                if evidence.direction == "against"
            }
        )

        if not support_ids and not counter_ids:
            observations.append(
                StructuralIndicatorObservationV1(
                    indicator_id=indicator_id,
                    observation_date=observation_date,
                    direction="insufficient",
                    support_score=0,
                    counter_score=0,
                    confidence="insufficient",
                    supporting_signal_ids=[],
                    counter_signal_ids=[],
                    missing_data=["no measurement-qualified structural evidence observed this run"],
                    one_sentence_read="Insufficient measurement-qualified evidence for a directional update.",
                    next_verification=["add or run indicator-specific structured measurement adapters"],
                    evaluation_mode="deterministic",
                    components=components,
                )
            )
            continue

        # Component fan-out never multiplies the same event in the overall score.
        support_score = min(100, 20 * len(support_ids))
        counter_score = min(100, 20 * len(counter_ids))
        direction = (
            "supporting"
            if support_score > counter_score
            else "counter"
            if counter_score > support_score
            else "mixed"
        )
        confidence = abs(support_score - counter_score)
        read = (
            "Deterministic measurement evidence is high-conflict; no directional confidence should be inferred."
            if direction == "mixed"
            else f"Deterministic measurement-qualified evidence leans {direction} for this indicator."
        )
        verify = (
            "resolve conflicting evidence with independent structured measurements"
            if direction == "mixed"
            else "confirm with independent structured measurements and primary sources"
        )
        observations.append(
            StructuralIndicatorObservationV1(
                indicator_id=indicator_id,
                observation_date=observation_date,
                direction=direction,
                support_score=support_score,
                counter_score=counter_score,
                confidence=confidence,
                supporting_signal_ids=support_ids,
                counter_signal_ids=counter_ids,
                missing_data=[],
                one_sentence_read=read,
                next_verification=[verify],
                evaluation_mode="deterministic",
                components=components,
            )
        )
    return observations
