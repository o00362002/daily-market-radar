"""AI-assisted evaluator: deterministic base + bounded AI enhancement + revalidation.

Deterministic evaluation always runs first and is the fallback. AI output is
revalidated deterministically; on invalid output it retries once and then keeps
the deterministic result (partial). Over budget, AI is skipped and the run stays
deterministic. The evaluator never crashes on provider failure.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime
from typing import Callable

from radar.contracts.evaluation import EvaluationRequest, EvaluationResult
from radar.contracts.report import EvaluationAuditV1, ReportItemV2, TokenUsageV1
from radar.evaluators.ai_provider import (
    AiEvaluationProvider,
    AiProposalResult,
    AiUsage,
    AllowedFacts,
    MAX_SCORE_DELTA,
    build_bounded_context,
    validate_ai_proposal,
)
from radar.evaluators.cache import CostBudget, EvaluationCacheEntry, InMemoryEvaluationCache, cache_key
from radar.ports.evaluation import IntelligenceEvaluator


def _clamp(value: int) -> int:
    return max(0, min(100, value))


class AiAssistedEvaluator:
    evaluator_id = "ai_assisted_v1"

    def __init__(
        self,
        deterministic: IntelligenceEvaluator,
        provider: AiEvaluationProvider | None,
        *,
        clock: Callable[[], datetime],
        cache: InMemoryEvaluationCache | None = None,
        budget: CostBudget | None = None,
        effective_mode: str = "auto",
    ) -> None:
        self._deterministic = deterministic
        self._provider = provider
        self._clock = clock
        self._cache = cache or InMemoryEvaluationCache()
        self._budget = budget
        self._effective_mode = effective_mode

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        base = self._deterministic.evaluate(request)
        events = list(request.events)

        if self._provider is None:
            return self._fallback(base, request, ["ai_evaluation_unavailable"])
        if self._budget is not None and self._budget.exhausted:
            return self._fallback(base, request, ["ai_budget_exhausted"])

        context, allowed = build_bounded_context(events, base)
        key = cache_key(events, model=self._provider.model, evaluator_config=self.evaluator_id)
        input_hash = _hash_context(context)

        cached = self._cache.get(key)
        cache_hits = 1 if cached is not None else 0
        estimated_input_tokens = _estimate_tokens(context)
        if self._budget is not None and not self._budget.can_afford(
            cost=0.0, items=len(context.events), input_tokens=estimated_input_tokens
        ):
            return self._fallback(base, request, ["ai_budget_exhausted"])

        proposal: AiProposalResult | None = None
        retries = 0
        if cached is not None:
            proposal = _decode_proposal(cached.payload_json)
        else:
            call_context = replace(context, profile=request.profile, model=self._provider.model)
            for attempt in range(2):  # initial attempt + one retry
                try:
                    candidate = self._provider.propose(call_context)
                except Exception:  # noqa: BLE001 - provider failure must not crash the run
                    return self._fallback(base, request, ["ai_provider_error"])
                reasons = validate_ai_proposal(candidate, allowed)
                if not reasons:
                    proposal = candidate
                    break
                retries = attempt + 1
            if self._budget is not None and proposal is not None:
                usage = proposal.usage
                self._budget.charge(
                    cost=usage.estimated_cost_usd, items=len(context.events), input_tokens=usage.input_tokens
                )

        if proposal is None:
            return self._fallback(base, request, ["ai_output_invalid"], validation_status="ai_output_rejected")

        enhanced_items = _apply_proposal(base.items, proposal, allowed)
        usage = proposal.usage
        output_hash = _hash_proposal(proposal)
        if cached is None:
            self._cache.put(
                key,
                EvaluationCacheEntry(
                    provider=self._provider.provider_id,
                    model=self._provider.model,
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                    estimated_cost_usd=usage.estimated_cost_usd,
                    latency_ms=0,
                    retries=retries,
                    validation_status="valid",
                    input_hash=input_hash,
                    output_hash=output_hash,
                    payload_json=_encode_proposal(proposal),
                ),
            )

        audit = EvaluationAuditV1(
            requested_mode=request.requested_mode,
            effective_mode=self._effective_mode,
            evaluator=self.evaluator_id,
            model=self._provider.model,
            provider=self._provider.provider_id,
            started_at=request.started_at,
            finished_at=self._clock().isoformat(),
            cache_hits=cache_hits,
            evaluated_item_count=len(enhanced_items),
            failed_item_count=0,
            token_usage=TokenUsageV1(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.input_tokens + usage.output_tokens,
            ),
            estimated_cost_usd=usage.estimated_cost_usd,
            source_context_hash=base.audit.source_context_hash,
            validation_status="valid",
            degradation_reasons=[],
        )
        return replace(base, items=enhanced_items, audit=audit)

    def _fallback(
        self,
        base: EvaluationResult,
        request: EvaluationRequest,
        degradation_reasons: list[str],
        *,
        validation_status: str = "deterministic_fallback",
    ) -> EvaluationResult:
        audit = base.audit.model_copy(
            update={
                "requested_mode": request.requested_mode,
                "effective_mode": "deterministic",
                "validation_status": validation_status,
                "degradation_reasons": list(
                    dict.fromkeys([*base.audit.degradation_reasons, *degradation_reasons])
                ),
            }
        )
        return replace(base, audit=audit)


def _apply_proposal(
    items: tuple[ReportItemV2, ...],
    proposal: AiProposalResult,
    allowed: AllowedFacts,
) -> tuple[ReportItemV2, ...]:
    by_event = {item.event_id: item for item in proposal.items}
    enhanced: list[ReportItemV2] = []
    for item in items:
        change = by_event.get(item.event_id)
        if change is None:
            enhanced.append(item)
            continue
        update: dict[str, object] = {}
        if change.headline:
            update["headline"] = change.headline
        if change.taiwan_implication:
            update["taiwan_implication"] = change.taiwan_implication
        if change.next_watch:
            update["next_watch"] = change.next_watch
        if change.counterevidence:
            update["counterevidence"] = [*item.counterevidence, *change.counterevidence]
        if change.uncertainties:
            update["uncertainties"] = [*item.uncertainties, *change.uncertainties]
        update["importance_score"] = _clamp(item.importance_score + _bounded(change.importance_delta))
        update["potential_score"] = _clamp(item.potential_score + _bounded(change.potential_delta))
        update["confidence_score"] = _clamp(item.confidence_score + _bounded(change.confidence_delta))
        if change.rationale:
            explanation = dict(item.score_explanation.model_dump())
            explanation["rationale"] = f"{explanation['rationale']} AI note: {change.rationale}".strip()
            update["score_explanation"] = explanation
        enhanced.append(item.model_copy(update=update))
    return tuple(enhanced)


def _bounded(delta: int) -> int:
    return max(-MAX_SCORE_DELTA, min(MAX_SCORE_DELTA, delta))


def _estimate_tokens(context: object) -> int:
    return max(1, len(_encode_context(context)) // 4)


def _encode_context(context: object) -> str:
    return json.dumps(_context_payload(context), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _context_payload(context: object) -> dict[str, object]:
    return {
        "date": context.date,
        "events": [
            {
                "event_id": event.event_id,
                "summary": event.summary,
                "delta_types": list(event.delta_types),
                "metrics": list(event.measurement_metric_ids),
                "scores": [event.deterministic_importance, event.deterministic_potential, event.deterministic_confidence],
            }
            for event in context.events
        ],
    }


def _hash_context(context: object) -> str:
    return hashlib.sha256(_encode_context(context).encode("utf-8")).hexdigest()


def _encode_proposal(proposal: AiProposalResult) -> str:
    return json.dumps(
        {
            "items": [
                {
                    "event_id": item.event_id,
                    "headline": item.headline,
                    "rationale": item.rationale,
                    "taiwan_implication": item.taiwan_implication,
                    "next_watch": item.next_watch,
                    "counterevidence": list(item.counterevidence),
                    "uncertainties": list(item.uncertainties),
                    "importance_delta": item.importance_delta,
                    "potential_delta": item.potential_delta,
                    "confidence_delta": item.confidence_delta,
                }
                for item in proposal.items
            ]
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _decode_proposal(payload_json: str) -> AiProposalResult:
    from radar.evaluators.ai_provider import AiProposalItem

    payload = json.loads(payload_json)
    items = tuple(
        AiProposalItem(
            event_id=item["event_id"],
            headline=item.get("headline", ""),
            rationale=item.get("rationale", ""),
            taiwan_implication=item.get("taiwan_implication", ""),
            next_watch=item.get("next_watch", ""),
            counterevidence=tuple(item.get("counterevidence", [])),
            uncertainties=tuple(item.get("uncertainties", [])),
            importance_delta=item.get("importance_delta", 0),
            potential_delta=item.get("potential_delta", 0),
            confidence_delta=item.get("confidence_delta", 0),
        )
        for item in payload.get("items", [])
    )
    return AiProposalResult(items=items, usage=AiUsage())


def _hash_proposal(proposal: AiProposalResult) -> str:
    return hashlib.sha256(_encode_proposal(proposal).encode("utf-8")).hexdigest()
