from __future__ import annotations

from typing import Protocol, runtime_checkable

from radar.contracts.evaluation import EvaluationRequest, EvaluationResult


@runtime_checkable
class IntelligenceEvaluator(Protocol):
    evaluator_id: str

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult: ...
