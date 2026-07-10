from __future__ import annotations

from dataclasses import dataclass

from radar.contracts.report import (
    EvaluationAuditV1,
    MatrixObservationV1,
    ReportItemV2,
    SignalV1,
    StructuralIndicatorObservationV1,
)
from radar.contracts.runtime import RuntimeContract
from radar.domain.models import Event


@dataclass(frozen=True)
class EvaluationRequest:
    date: str
    profile: str
    requested_mode: str
    events: tuple[Event, ...]
    contract: RuntimeContract
    started_at: str


@dataclass(frozen=True)
class EvaluationResult:
    items: tuple[ReportItemV2, ...]
    signals: tuple[SignalV1, ...]
    retail_matrix: dict[str, MatrixObservationV1]
    crypto_matrix: dict[str, MatrixObservationV1]
    structural_indicators: tuple[StructuralIndicatorObservationV1, ...]
    audit: EvaluationAuditV1
