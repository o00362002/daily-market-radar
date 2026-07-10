from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import replace

from radar.contracts.evaluation import EvaluationRequest, EvaluationResult
from radar.contracts.report import (
    EvaluationAuditV1,
    MatrixObservationV1,
    RadarReportV2,
    ReportItemV2,
    SignalV1,
    StructuralIndicatorObservationV1,
    TokenUsageV1,
)
from radar.contracts.web import PublicationReceiptV1, WebArtifactV1
from radar.domain.models import Document, Event, EventDelta
from radar.pipeline.classify import classify_potential_signals
from radar.ports import (
    CredentialsStatusV1,
    RateLimitPolicy,
    RetryPolicy,
    SourceFetchRequest,
    SourceFetchResult,
    SourceHealthV1,
)
from radar.reporting.planner import plan_daily_items


class FakeSourceAdapter:
    """Provider-neutral source double with observable port calls."""

    def __init__(
        self,
        documents: Sequence[Document],
        *,
        adapter_id: str = "fake-source",
        source_id: str = "fake-source",
        credentials_available: bool = True,
        health_status: str = "healthy",
        degradation_reasons: Sequence[str] = (),
    ) -> None:
        self.adapter_id = adapter_id
        self.source_id = source_id
        self.retry_policy = RetryPolicy(max_attempts=1)
        self.rate_limit_policy = RateLimitPolicy(requests_per_minute=None)
        self._documents = tuple(documents)
        self._credentials_available = credentials_available
        self._health_status = health_status
        self._degradation_reasons = tuple(degradation_reasons)
        self.fetch_requests: list[SourceFetchRequest] = []
        self.normalize_calls: list[SourceFetchResult] = []
        self.credentials_status_calls = 0
        self.health_check_calls = 0

    def credentials_status(self) -> CredentialsStatusV1:
        self.credentials_status_calls += 1
        return CredentialsStatusV1(
            available=self._credentials_available,
            reason="" if self._credentials_available else "fake credentials disabled",
        )

    def health_check(self) -> SourceHealthV1:
        self.health_check_calls += 1
        return SourceHealthV1(status=self._health_status, message="fake source health")

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        self.fetch_requests.append(request)
        taiwan_sources = tuple(
            sorted({document.source_id for document in self._documents if document.macro_region == "Taiwan"})
        )
        return SourceFetchResult(
            documents=self._documents,
            degradation_reasons=self._degradation_reasons,
            sources_checked=(self.source_id,),
            registry_checked=True,
            integration_status=((self.adapter_id, self._health_status),),
            taiwan_direct_sources_checked=taiwan_sources,
        )

    def normalize(self, result: SourceFetchResult) -> list[Document]:
        self.normalize_calls.append(result)
        return list(result.documents)


class FakeIntelligenceEvaluator:
    """Deterministic evaluator double that emits canonical evaluation DTOs."""

    def __init__(
        self,
        *,
        evaluator_id: str = "fake-intelligence",
        headline_prefix: str = "",
        score_delta: int = 0,
        finished_at: str | None = None,
        degradation_reasons: Sequence[str] = (),
    ) -> None:
        self.evaluator_id = evaluator_id
        self.headline_prefix = headline_prefix
        self.score_delta = score_delta
        self.finished_at = finished_at
        self.degradation_reasons = list(degradation_reasons)
        self.requests: list[EvaluationRequest] = []

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        self.requests.append(request)
        planned_items = []
        for item in plan_daily_items(list(request.events)):
            payload = item.to_dict()
            payload["headline"] = f"{self.headline_prefix}{payload['headline']}"
            for score_name in ("importance_score", "potential_score", "confidence_score"):
                payload[score_name] = max(0, min(100, payload[score_name] + self.score_delta))
            planned_items.append(ReportItemV2.model_validate(payload))

        signals = tuple(
            SignalV1.model_validate(signal.__dict__)
            for signal in classify_potential_signals(list(request.events))
        )
        source_context_hash = hashlib.sha256(
            "|".join(
                sorted(
                    document.content_hash
                    for event in request.events
                    for document in event.documents
                )
            ).encode("utf-8")
        ).hexdigest()
        structural_indicators = tuple(
            StructuralIndicatorObservationV1(
                indicator_id=indicator_id,
                observation_date=request.date,
                direction="insufficient",
                support_score=0,
                counter_score=0,
                confidence="insufficient",
                supporting_signal_ids=[],
                counter_signal_ids=[],
                missing_data=["fake evaluator has no external indicator data"],
                one_sentence_read="Insufficient verified evidence for a directional update.",
                next_verification=["supply another canonical evaluator"],
                evaluation_mode="deterministic",
            )
            for indicator_id in request.contract.structural_indicator_ids
        )
        return EvaluationResult(
            items=tuple(planned_items),
            signals=signals,
            retail_matrix={
                key: MatrixObservationV1(
                    status="insufficient",
                    signal_ids=[],
                    data_checked=[],
                    gap="fake evaluator has no retail series",
                )
                for key in request.contract.retail_matrix_keys
            },
            crypto_matrix={
                key: MatrixObservationV1(
                    status="insufficient",
                    signal_ids=[],
                    data_checked=[],
                    gap="fake evaluator has no crypto series",
                )
                for key in request.contract.crypto_matrix_keys
            },
            structural_indicators=structural_indicators,
            audit=EvaluationAuditV1(
                requested_mode=request.requested_mode,
                effective_mode="deterministic",
                evaluator=self.evaluator_id,
                model=None,
                provider=None,
                started_at=request.started_at,
                finished_at=self.finished_at or request.started_at,
                cache_hits=0,
                evaluated_item_count=len(planned_items),
                failed_item_count=0,
                token_usage=TokenUsageV1(),
                estimated_cost_usd=0.0,
                source_context_hash=source_context_hash,
                validation_status="valid",
                degradation_reasons=list(self.degradation_reasons),
            ),
        )


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self.saved_batches: list[tuple[str, ...]] = []

    def save_documents(self, documents: list[Document]) -> None:
        self.saved_batches.append(tuple(document.document_id for document in documents))
        self.documents.update({document.document_id: document for document in documents})

    def get_document(self, document_id: str) -> Document | None:
        return self.documents.get(document_id)

    def find_by_canonical_url(self, canonical_url: str) -> Document | None:
        return next((document for document in self.documents.values() if document.url == canonical_url), None)

    def find_by_content_hash(self, content_hash: str) -> Document | None:
        return next((document for document in self.documents.values() if document.content_hash == content_hash), None)

    def list_recent_documents(self, since: str) -> list[Document]:
        return sorted(
            (document for document in self.documents.values() if document.fetched_at >= since),
            key=lambda document: (document.fetched_at, document.document_id),
        )


class InMemoryEventRepository:
    def __init__(self) -> None:
        self.events: dict[str, Event] = {}
        self.event_documents: dict[str, list[str]] = defaultdict(list)
        self.event_deltas: dict[str, list[EventDelta]] = defaultdict(list)
        self.recent_queries: list[str] = []

    def save_event(self, event: Event) -> None:
        self.events[event.event_id] = event

    def get_event(self, event_id: str) -> Event | None:
        return self.events.get(event_id)

    def find_recent_events(self, since: str) -> list[Event]:
        self.recent_queries.append(since)
        return sorted(
            (event for event in self.events.values() if event.last_seen_at >= since),
            key=lambda event: (event.last_seen_at, event.event_id),
        )

    def attach_documents(self, event_id: str, document_ids: list[str]) -> None:
        attached = self.event_documents[event_id]
        attached.extend(document_id for document_id in document_ids if document_id not in attached)

    def save_event_delta(self, event_id: str, delta: EventDelta, observed_at: str) -> None:
        del observed_at
        self.event_deltas[event_id].append(delta)

    def list_event_deltas(self, event_id: str) -> list[EventDelta]:
        return list(self.event_deltas.get(event_id, []))

    def update_last_seen(self, event_id: str, last_seen_at: str) -> None:
        self.events[event_id] = replace(self.events[event_id], last_seen_at=last_seen_at)

    def list_active_events(self) -> list[Event]:
        return sorted(
            (event for event in self.events.values() if event.status == "active"),
            key=lambda event: event.event_id,
        )


class InMemoryReportRepository:
    def __init__(self) -> None:
        self.reports: dict[str, RadarReportV2] = {}
        self.save_calls: list[RadarReportV2] = []

    def save_report(self, report: RadarReportV2) -> None:
        self.save_calls.append(report)
        self.reports[report.report_id] = report

    def get_report(self, report_id: str) -> RadarReportV2 | None:
        return self.reports.get(report_id)

    def get_report_by_date(self, report_date: str, profile: str) -> RadarReportV2 | None:
        matches = [
            report
            for report in self.reports.values()
            if report.date == report_date and report.profile == profile
        ]
        return max(matches, key=lambda report: report.run_id, default=None)

    def get_latest_report(self, profile: str | None = None) -> RadarReportV2 | None:
        reports = self.list_reports(profile)
        return reports[-1] if reports else None

    def list_reports(self, profile: str | None = None) -> list[RadarReportV2]:
        return sorted(
            (report for report in self.reports.values() if profile is None or report.profile == profile),
            key=lambda report: (report.date, report.run_id),
        )


class InMemoryIndicatorRepository:
    def __init__(self) -> None:
        self.observations: dict[str, list[StructuralIndicatorObservationV1]] = defaultdict(list)
        self.save_calls: list[StructuralIndicatorObservationV1] = []

    def save_indicator_observation(self, observation: StructuralIndicatorObservationV1) -> None:
        self.save_calls.append(observation)
        self.observations[observation.indicator_id].append(observation)

    def list_indicator_observations(self, indicator_id: str) -> list[StructuralIndicatorObservationV1]:
        return sorted(
            self.observations.get(indicator_id, []),
            key=lambda observation: observation.observation_date,
        )

    def get_rolling_window(self, indicator_id: str, days: int) -> list[StructuralIndicatorObservationV1]:
        if days <= 0:
            raise ValueError("days must be positive")
        return self.list_indicator_observations(indicator_id)[-days:]


class InMemoryStateStore:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}
        self.save_calls: list[tuple[str, bytes]] = []

    def load(self, key: str) -> bytes | None:
        return self.values.get(key)

    def save(self, key: str, value: bytes) -> None:
        copied = bytes(value)
        self.save_calls.append((key, copied))
        self.values[key] = copied


class InMemoryWebArtifactStore:
    def __init__(self) -> None:
        self.artifacts: dict[str, WebArtifactV1] = {}
        self.commits: list[tuple[WebArtifactV1, ...]] = []

    def read(self, path: str) -> WebArtifactV1 | None:
        return self.artifacts.get(path)

    def commit(self, artifacts: Sequence[WebArtifactV1]) -> None:
        committed = tuple(artifacts)
        self.commits.append(committed)
        self.artifacts.update({artifact.path: artifact for artifact in committed})


class FakePublisher:
    def __init__(self, *, publisher_id: str = "fake-publisher") -> None:
        self.publisher_id = publisher_id
        self.calls: list[tuple[RadarReportV2, tuple[WebArtifactV1, ...]]] = []

    def publish(
        self,
        report: RadarReportV2,
        artifacts: Sequence[WebArtifactV1],
    ) -> PublicationReceiptV1:
        if not isinstance(report, RadarReportV2):
            raise TypeError("publisher accepts only validated RadarReportV2 values")
        committed = tuple(artifacts)
        if not all(isinstance(artifact, WebArtifactV1) for artifact in committed):
            raise TypeError("publisher accepts only typed web artifacts")
        self.calls.append((report, committed))
        return PublicationReceiptV1(
            publisher_id=self.publisher_id,
            status="published",
            artifact_paths=[artifact.path for artifact in committed],
        )


__all__ = [
    "FakeIntelligenceEvaluator",
    "FakePublisher",
    "FakeSourceAdapter",
    "InMemoryDocumentRepository",
    "InMemoryEventRepository",
    "InMemoryIndicatorRepository",
    "InMemoryReportRepository",
    "InMemoryStateStore",
    "InMemoryWebArtifactStore",
]
