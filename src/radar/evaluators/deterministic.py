from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Callable

from radar.contracts.evaluation import EvaluationRequest, EvaluationResult
from radar.contracts.report import (
    EvaluationAuditV1,
    ReportItemV2,
    SignalV1,
    TokenUsageV1,
)
from radar.evaluators.matrices import (
    evaluate_crypto_matrix,
    evaluate_retail_matrix,
    evaluate_structural_indicators,
)
from radar.pipeline.classify import classify_potential_signals
from radar.reporting.planner import plan_daily_items


class DeterministicIntelligenceEvaluator:
    evaluator_id = "deterministic_rules_v1"

    def __init__(self, clock: Callable[[], datetime]) -> None:
        self._clock = clock

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        events = list(request.events)
        items = tuple(ReportItemV2.model_validate(item.to_dict()) for item in plan_daily_items(events))
        signals = tuple(SignalV1.model_validate(signal.__dict__) for signal in classify_potential_signals(events))
        context_hash = hashlib.sha256(
            "|".join(
                sorted(
                    document.content_hash
                    for event in events
                    for document in event.documents
                )
            ).encode("utf-8")
        ).hexdigest()
        degradation_reasons = []
        if request.requested_mode not in {"deterministic", "auto"}:
            degradation_reasons.append("requested_evaluator_unavailable")

        return EvaluationResult(
            items=items,
            signals=signals,
            retail_matrix=evaluate_retail_matrix(events, request.contract.retail_matrix_keys),
            crypto_matrix=evaluate_crypto_matrix(events, request.contract.crypto_matrix_keys),
            structural_indicators=tuple(
                evaluate_structural_indicators(
                    events,
                    request.contract.structural_indicator_ids,
                    observation_date=request.date,
                )
            ),
            audit=EvaluationAuditV1(
                requested_mode=request.requested_mode,
                effective_mode="deterministic",
                evaluator=self.evaluator_id,
                model=None,
                provider=None,
                started_at=request.started_at,
                finished_at=self._clock().isoformat(),
                cache_hits=0,
                evaluated_item_count=len(items),
                failed_item_count=0,
                token_usage=TokenUsageV1(),
                estimated_cost_usd=0.0,
                source_context_hash=context_hash,
                validation_status="valid",
                degradation_reasons=degradation_reasons,
            ),
        )
