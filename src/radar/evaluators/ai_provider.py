"""AI evaluation provider protocol, bounded context, and output validation.

The model is a semantic assistant, never the judge of facts. It only ever sees a
bounded, provider-neutral context (structured facts, summaries, evidence
snippets, event history, deltas, deterministic scores, counterevidence
candidates) — never secrets, full HTML, full articles, duplicate content or
unrelated history. Its output is always re-validated deterministically: it may
not invent URLs, event/document/source ids or numeric facts, and score
adjustments are bounded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from radar.contracts.evaluation import EvaluationResult
from radar.domain.models import Event

MAX_SCORE_DELTA = 15
MAX_SUMMARY_CHARS = 500
MAX_EXCERPT_CHARS = 280


@dataclass(frozen=True)
class BoundedEventContext:
    event_id: str
    primary_domain: str
    summary: str
    delta_types: tuple[str, ...]
    measurement_metric_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    evidence_urls: tuple[str, ...]
    evidence_snippets: tuple[str, ...]
    deterministic_importance: int
    deterministic_potential: int
    deterministic_confidence: int
    counterevidence_candidates: tuple[str, ...]


@dataclass(frozen=True)
class AiProposalRequest:
    date: str
    profile: str
    model: str
    events: tuple[BoundedEventContext, ...]


@dataclass(frozen=True)
class AiProposalItem:
    event_id: str
    headline: str = ""
    rationale: str = ""
    taiwan_implication: str = ""
    next_watch: str = ""
    counterevidence: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    importance_delta: int = 0
    potential_delta: int = 0
    confidence_delta: int = 0
    cited_event_ids: tuple[str, ...] = ()
    cited_source_ids: tuple[str, ...] = ()
    cited_urls: tuple[str, ...] = ()
    cited_numeric_facts: tuple[str, ...] = ()


@dataclass(frozen=True)
class AiUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    retries: int = 0


@dataclass(frozen=True)
class AiProposalResult:
    items: tuple[AiProposalItem, ...]
    usage: AiUsage = field(default_factory=AiUsage)


@runtime_checkable
class AiEvaluationProvider(Protocol):
    provider_id: str
    model: str

    def propose(self, request: AiProposalRequest) -> AiProposalResult: ...


@dataclass(frozen=True)
class AllowedFacts:
    event_ids: frozenset[str]
    source_ids: frozenset[str]
    urls: frozenset[str]
    numeric_facts: frozenset[str]


def build_bounded_context(events: list[Event], deterministic: EvaluationResult) -> tuple[AiProposalRequest, AllowedFacts]:
    scores_by_event = {item.event_id: item for item in deterministic.items}
    contexts: list[BoundedEventContext] = []
    allowed_event_ids: set[str] = set()
    allowed_source_ids: set[str] = set()
    allowed_urls: set[str] = set()
    allowed_numeric: set[str] = set()

    for event in events:
        item = scores_by_event.get(event.event_id)
        if item is None:
            continue
        allowed_event_ids.add(event.event_id)
        metric_ids: set[str] = set()
        source_ids: set[str] = set()
        urls: set[str] = set()
        snippets: list[str] = []
        for document in event.documents:
            source_ids.add(document.source_id)
            urls.add(document.url)
            snippets.append((document.summary or document.title)[:MAX_EXCERPT_CHARS])
            for metric in document.facts:
                if metric != "source_roles":
                    metric_ids.add(metric)
        allowed_source_ids.update(source_ids)
        allowed_urls.update(urls)
        allowed_numeric.update(metric_ids)
        contexts.append(
            BoundedEventContext(
                event_id=event.event_id,
                primary_domain=item.primary_domain,
                summary=(event.documents[0].summary or event.documents[0].title)[:MAX_SUMMARY_CHARS],
                delta_types=tuple(sorted({delta.delta_type for delta in event.deltas})),
                measurement_metric_ids=tuple(sorted(metric_ids)),
                source_ids=tuple(sorted(source_ids)),
                evidence_urls=tuple(sorted(urls)),
                evidence_snippets=tuple(snippets[:3]),
                deterministic_importance=item.importance_score,
                deterministic_potential=item.potential_score,
                deterministic_confidence=item.confidence_score,
                counterevidence_candidates=tuple(item.counterevidence),
            )
        )
    request = AiProposalRequest(
        date=deterministic.audit.started_at[:10],
        profile="",
        model="",
        events=tuple(contexts),
    )
    allowed = AllowedFacts(
        event_ids=frozenset(allowed_event_ids),
        source_ids=frozenset(allowed_source_ids),
        urls=frozenset(allowed_urls),
        numeric_facts=frozenset(allowed_numeric),
    )
    return request, allowed


def validate_ai_proposal(proposal: AiProposalResult, allowed: AllowedFacts) -> list[str]:
    """Return a list of rejection reasons; empty means the proposal is valid."""

    reasons: list[str] = []
    for item in proposal.items:
        if item.event_id not in allowed.event_ids:
            reasons.append(f"invented_event_id:{item.event_id}")
        for event_id in item.cited_event_ids:
            if event_id not in allowed.event_ids:
                reasons.append(f"invented_event_id:{event_id}")
        for source_id in item.cited_source_ids:
            if source_id not in allowed.source_ids:
                reasons.append(f"invented_source_id:{source_id}")
        for url in item.cited_urls:
            if url not in allowed.urls:
                reasons.append(f"invented_url:{url}")
        for metric in item.cited_numeric_facts:
            if metric not in allowed.numeric_facts:
                reasons.append(f"invented_numeric_fact:{metric}")
        for name, delta in (
            ("importance", item.importance_delta),
            ("potential", item.potential_delta),
            ("confidence", item.confidence_delta),
        ):
            if abs(delta) > MAX_SCORE_DELTA:
                reasons.append(f"score_delta_out_of_bounds:{name}:{delta}")
    return reasons
