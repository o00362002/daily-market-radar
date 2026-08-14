"""Auditable deterministic gates for structural-trend evidence.

The scoring order is deliberately strict:
candidate -> domain relevance -> proposition entailment -> measurement evidence
-> support/counter -> score.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from radar.domain.models import Event, normalize_text


_QUANTIFIED_VALUE = re.compile(
    r"(?<![a-z0-9])(?:[$€£¥]|nt\$)?\s*\d[\d,]*(?:\.\d+)?\s*"
    r"(?:%|percent|percentage points?|bps|basis points?|million|billion|trillion|bn|mn|"
    r"employees?|workers?|stores?|customers?|users?|億|萬|兆|美元|新台幣|台幣|元|人|家|店|間|倍)",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class StructuralGateDecision:
    qualified: bool
    failed_stage: str
    measurement_hits: tuple[str, ...] = ()


def event_text(event: Event) -> str:
    return normalize_text(
        " ".join(
            part
            for document in event.documents
            for part in (
                document.title,
                document.action,
                document.object,
                document.summary,
                " ".join(document.entities),
            )
        )
    )


def event_metric_ids(event: Event) -> set[str]:
    return {
        metric
        for document in event.documents
        for metric in document.facts
        if metric != "source_roles"
    }


def event_metric_namespaces(event: Event) -> set[str]:
    return {metric.split("_", 1)[0] for metric in event_metric_ids(event)}


def event_domains(event: Event) -> set[str]:
    return {document.primary_domain for document in event.documents if document.primary_domain}


def keyword_hit(text: str, keywords: set[str]) -> list[str]:
    """Match Latin terms on token boundaries and CJK terms as phrases."""
    hits: list[str] = []
    for keyword in keywords:
        if any("\u3400" <= char <= "\u9fff" for char in keyword):
            matched = keyword.lower() in text
        else:
            matched = re.search(
                rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])",
                text,
                flags=re.IGNORECASE,
            ) is not None
        if matched:
            hits.append(keyword)
    return sorted(hits)


def _passes_entailment(text: str, groups: tuple[set[str], ...]) -> bool:
    return all(keyword_hit(text, group) for group in groups)


def _quantified_candidate_hits(
    text: str,
    candidate_hits: list[str],
    *,
    radius: int = 140,
) -> list[str]:
    """Only accept explicit quantities located near the candidate proposition."""
    quantified: list[str] = []
    lowered = text.lower()
    for keyword in candidate_hits:
        needle = keyword.lower()
        start = 0
        while True:
            index = lowered.find(needle, start)
            if index < 0:
                break
            left = max(0, index - radius)
            right = min(len(text), index + len(needle) + radius)
            if _QUANTIFIED_VALUE.search(text[left:right]):
                quantified.append(f"text:{keyword}")
                break
            start = index + max(1, len(needle))
    return sorted(set(quantified))


def _measurement_hits(
    event: Event,
    text: str,
    candidate_hits: list[str],
    namespaces: set[str],
) -> list[str]:
    metric_hits = sorted(
        metric
        for metric in event_metric_ids(event)
        if metric.split("_", 1)[0] in namespaces
    )
    if metric_hits:
        return [f"metric:{metric}" for metric in metric_hits]
    return _quantified_candidate_hits(text, candidate_hits)


def qualify_structural_event(
    event: Event,
    *,
    text: str,
    candidate_hits: list[str],
    gate: dict[str, object],
    direction: str,
) -> StructuralGateDecision:
    if not candidate_hits:
        return StructuralGateDecision(False, "candidate")

    domains = set(gate.get("domains", set()))
    if domains and not (event_domains(event) & domains):
        return StructuralGateDecision(False, "domain")

    entailment_groups = tuple(gate.get(f"{direction}_all", ()))
    if entailment_groups and not _passes_entailment(text, entailment_groups):
        return StructuralGateDecision(False, "entailment")

    namespaces = set(gate.get("measurement_namespaces", set()))
    measurements = _measurement_hits(event, text, candidate_hits, namespaces)
    if not measurements:
        return StructuralGateDecision(False, "measurement")

    return StructuralGateDecision(True, "qualified", tuple(measurements))
