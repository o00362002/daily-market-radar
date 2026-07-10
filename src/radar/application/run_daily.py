from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from radar.contracts.evaluation import EvaluationRequest, EvaluationResult
from radar.contracts.report import (
    BacktestV1,
    CoverageCellV2,
    CoverageGapV2,
    RadarReportV2,
    RejectionCountersV2,
    ReportItemV2,
    SourceAuditV2,
)
from radar.contracts.runtime import RuntimeContract
from radar.contracts.web import PublicationReceiptV1, WebArtifactV1
from radar.domain.models import Document, Event, stable_id
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deduplicate import deduplicate_documents
from radar.pipeline.deltas import material_events, reconcile_cross_day_events
from radar.reporting.contracts import validate_report_contract
from radar.ports import (
    DocumentRepository,
    EventRepository,
    IndicatorRepository,
    IntelligenceEvaluator,
    ReportPublisher,
    ReportRepository,
    SourceAdapter,
    SourceFetchRequest,
    SourceFetchResult,
    StateStore,
    WebArtifactStore,
)


@dataclass(frozen=True)
class DailyRunRequest:
    date: str
    profile: str = "daily_push"
    ingestion_mode: str = "fixture"
    evaluation_mode: str = "deterministic"


@dataclass(frozen=True)
class ApplicationDependencies:
    source_adapter: SourceAdapter
    evaluator: IntelligenceEvaluator
    document_repository: DocumentRepository
    event_repository: EventRepository
    report_repository: ReportRepository
    indicator_repository: IndicatorRepository
    state_store: StateStore
    web_artifact_store: WebArtifactStore
    publishers: tuple[ReportPublisher, ...]


@dataclass(frozen=True)
class ApplicationRunResult:
    report: RadarReportV2
    artifacts: tuple[WebArtifactV1, ...]
    publications: tuple[PublicationReceiptV1, ...]
    documents: tuple[Document, ...]
    events: tuple[Event, ...]


class DailyRadarApplication:
    """Provider-neutral orchestration for the deterministic radar flow."""

    def __init__(
        self,
        dependencies: ApplicationDependencies,
        *,
        clock: Callable[[], datetime],
    ) -> None:
        self._dependencies = dependencies
        self._clock = clock

    def run(self, request: DailyRunRequest, contract: RuntimeContract) -> ApplicationRunResult:
        contract.validate()
        contract.profile(request.profile)
        started_at = self._clock().isoformat()

        source_result = self._collect(request)
        normalized = self._dependencies.source_adapter.normalize(source_result)
        documents = deduplicate_documents(normalized)
        duplicate_rejection_count = len(normalized) - len(documents)
        self._dependencies.document_repository.save_documents(documents)

        prior_events = self._dependencies.event_repository.find_recent_events(self._event_history_since(request.date))
        events = reconcile_cross_day_events(cluster_documents(documents), prior_events)
        for event in events:
            self._dependencies.event_repository.save_event(event)
            self._dependencies.event_repository.attach_documents(
                event.event_id,
                [document.document_id for document in event.documents],
            )
            for delta in event.deltas:
                self._dependencies.event_repository.save_event_delta(event.event_id, delta, started_at)

        reportable_events = material_events(events)
        evaluation = self._dependencies.evaluator.evaluate(
            EvaluationRequest(
                date=request.date,
                profile=request.profile,
                requested_mode=request.evaluation_mode,
                events=tuple(reportable_events),
                contract=contract,
                started_at=started_at,
            )
        )
        items = self._apply_slot_caps(list(evaluation.items), contract, request.profile)
        coverage_cells = self._coverage_cells(documents, contract, request.ingestion_mode)
        coverage_gaps = [*source_result.coverage_gaps, *self._coverage_gaps(coverage_cells)]
        source_health = self._dependencies.source_adapter.health_check()
        credentials = self._dependencies.source_adapter.credentials_status()
        if source_health.status in {"failing", "silent_zero", "empty", "stale", "policy_blocked"}:
            coverage_gaps.append(
                CoverageGapV2(
                    domain="all",
                    macro_region="global",
                    language="multi",
                    source_role="collection",
                    channel=self._dependencies.source_adapter.adapter_id,
                    time_window="24h",
                    reason=f"source_{source_health.status}",
                    message=source_health.message or f"source adapter health is {source_health.status}",
                )
            )
        degradation_reasons = self._degradation_reasons(
            source_result,
            evaluation.audit.degradation_reasons,
            source_health.status,
            credentials.available,
        )
        report_status = "partial" if degradation_reasons or coverage_gaps else "complete"
        direct_taiwan_count = sum(len(item.direct_taiwan_evidence) for item in items)
        run_id = self._run_id(
            request,
            documents,
            events,
            source_result,
            evaluation,
            items,
            coverage_cells,
            coverage_gaps,
            degradation_reasons,
        )

        integration_status = dict(source_result.integration_status)
        integration_status[self._dependencies.source_adapter.adapter_id] = source_health.status
        if not credentials.available:
            integration_status["credentials"] = "unavailable"

        report = RadarReportV2(
            run_id=run_id,
            date=request.date,
            profile=request.profile,
            status=report_status,
            degradation_reasons=degradation_reasons,
            items=items,
            coverage_cells=coverage_cells,
            coverage_gaps=coverage_gaps,
            signals=list(evaluation.signals),
            source_audit=SourceAuditV2(
                ingestion_mode=request.ingestion_mode,
                registry_checked=source_result.registry_checked,
                sources_checked=list(source_result.sources_checked),
                failures=list(source_result.failures),
                sources_not_executed=list(source_result.sources_not_executed),
                integration_status=integration_status,
                candidate_retry_paths_used=[],
                taiwan_direct_sources_checked=list(source_result.taiwan_direct_sources_checked),
                remaining_gaps=list(source_result.remaining_gaps),
            ),
            rejection_counters=RejectionCountersV2(
                duplicate_rejection_count=duplicate_rejection_count,
                field_overlap_rejection_count=0,
                niche_low_novelty_rejection_count=0,
                candidate_retry_paths_used=[],
                taiwan_qualified_item_count_after_audit=direct_taiwan_count,
                taiwan_direct_sources_checked=list(source_result.taiwan_direct_sources_checked),
            ),
            retail_matrix=evaluation.retail_matrix,
            crypto_matrix=evaluation.crypto_matrix,
            structural_indicators=list(evaluation.structural_indicators),
            evaluation_audit=evaluation.audit,
            backtest=BacktestV1(
                status="complete" if report_status == "complete" else "partial",
                findings=["provider-neutral application flow and report contract validated"],
                next_adjustments=list(source_result.remaining_gaps),
            ),
            contract_version="2.0",
        )
        validate_report_contract(report.model_dump(mode="json"), contract=contract)

        # Mutating output ports happens only after typed and cross-field validation.
        self._dependencies.report_repository.save_report(report)
        for observation in evaluation.structural_indicators:
            self._dependencies.indicator_repository.save_indicator_observation(observation)

        artifacts = self._project_web(report)
        self._dependencies.web_artifact_store.commit(artifacts)
        self._dependencies.state_store.save(f"last-valid-report:{request.profile}", report.canonical_json_bytes())
        publications = tuple(
            publisher.publish(report, artifacts)
            for publisher in self._dependencies.publishers
        )
        return ApplicationRunResult(
            report=report,
            artifacts=artifacts,
            publications=publications,
            documents=tuple(documents),
            events=tuple(events),
        )

    def _collect(self, request: DailyRunRequest) -> SourceFetchResult:
        credentials = self._dependencies.source_adapter.credentials_status()
        if not credentials.available:
            gap = CoverageGapV2(
                domain="all",
                macro_region="global",
                language="multi",
                source_role="collection",
                channel=self._dependencies.source_adapter.adapter_id,
                time_window="24h",
                reason="credentials_unavailable",
                message=credentials.reason or "optional source credentials unavailable",
            )
            return SourceFetchResult(
                documents=(),
                coverage_gaps=(gap,),
                degradation_reasons=("source_credentials_unavailable",),
                registry_checked=False,
                integration_status=((self._dependencies.source_adapter.adapter_id, "unavailable"),),
                remaining_gaps=(gap.message,),
            )
        return self._dependencies.source_adapter.fetch(SourceFetchRequest(date=request.date, profile=request.profile))

    @staticmethod
    def _apply_slot_caps(
        items: list[ReportItemV2],
        contract: RuntimeContract,
        profile_name: str,
    ) -> list[ReportItemV2]:
        profile = contract.profile(profile_name)
        grouped: dict[tuple[str, str], list[ReportItemV2]] = defaultdict(list)
        for item in items:
            grouped[(item.primary_domain, item.report_lane)].append(item)

        selected: list[ReportItemV2] = []
        for domain in contract.report_domains:
            for lane, cap in (
                ("major", profile.major_slot_cap_per_domain),
                ("potential", profile.potential_slot_cap_per_domain),
            ):
                lane_items = sorted(
                    grouped.get((domain, lane), []),
                    key=lambda item: (
                        item.importance_score if lane == "major" else item.potential_score,
                        item.confidence_score,
                        item.item_id,
                    ),
                    reverse=True,
                )
                selected.extend(lane_items if cap is None else lane_items[:cap])
        return selected

    @staticmethod
    def _coverage_cells(
        documents: list[Document],
        contract: RuntimeContract,
        channel: str,
    ) -> list[CoverageCellV2]:
        observed_by_domain = Counter(document.primary_domain for document in documents)
        cells = [
            CoverageCellV2(
                domain=domain,
                macro_region="Global",
                language="multi",
                source_role="mixed",
                channel=channel,
                time_window="24h",
                status="healthy" if observed_by_domain.get(domain, 0) else "empty",
                observed_count=observed_by_domain.get(domain, 0),
            )
            for domain in contract.report_domains
        ]
        taiwan_count = sum(1 for document in documents if document.macro_region == "Taiwan")
        cells.append(
            CoverageCellV2(
                domain="all",
                macro_region="Taiwan",
                language="zh-Hant",
                source_role="direct",
                channel=channel,
                time_window="24h",
                status="healthy" if taiwan_count else "empty",
                observed_count=taiwan_count,
            )
        )
        return cells

    @staticmethod
    def _coverage_gaps(cells: list[CoverageCellV2]) -> list[CoverageGapV2]:
        gap_statuses = {"failing", "silent_zero", "empty", "stale", "policy_blocked"}
        return [
            CoverageGapV2(
                domain=cell.domain,
                macro_region=cell.macro_region,
                language=cell.language,
                source_role=cell.source_role,
                channel=cell.channel,
                time_window=cell.time_window,
                reason=f"source_{cell.status}",
                message=f"{cell.domain}/{cell.macro_region}/{cell.language} coverage gap: {cell.status}",
            )
            for cell in cells
            if cell.status in gap_statuses
        ]

    @staticmethod
    def _degradation_reasons(
        source_result: SourceFetchResult,
        evaluator_reasons: list[str],
        source_health_status: str,
        credentials_available: bool,
    ) -> list[str]:
        reasons = [*source_result.degradation_reasons, *evaluator_reasons]
        if source_health_status != "healthy":
            reasons.append(f"source_health_{source_health_status}")
        if not credentials_available:
            reasons.append("source_credentials_unavailable")
        return list(dict.fromkeys(reasons))

    @staticmethod
    def _run_id(
        request: DailyRunRequest,
        documents: list[Document],
        events: list[Event],
        source_result: SourceFetchResult,
        evaluation: EvaluationResult,
        items: list[ReportItemV2],
        coverage_cells: list[CoverageCellV2],
        coverage_gaps: list[CoverageGapV2],
        degradation_reasons: list[str],
    ) -> str:
        audit = evaluation.audit.model_dump(mode="json", exclude={"started_at", "finished_at"})
        fingerprint = {
            "request": {
                "date": request.date,
                "profile": request.profile,
                "ingestion_mode": request.ingestion_mode,
                "evaluation_mode": request.evaluation_mode,
            },
            "documents": sorted(document.content_hash for document in documents),
            "events": [
                {
                    "event_id": event.event_id,
                    "first_seen_at": event.first_seen_at,
                    "last_seen_at": event.last_seen_at,
                    "last_material_delta_at": event.last_material_delta_at,
                    "deltas": [delta.__dict__ for delta in event.deltas],
                }
                for event in sorted(events, key=lambda event: event.event_id)
            ],
            "source": {
                "coverage_gaps": [gap.model_dump(mode="json") for gap in source_result.coverage_gaps],
                "degradation_reasons": list(source_result.degradation_reasons),
                "sources_checked": list(source_result.sources_checked),
                "failures": [failure.model_dump(mode="json") for failure in source_result.failures],
                "sources_not_executed": list(source_result.sources_not_executed),
                "registry_checked": source_result.registry_checked,
                "integration_status": list(source_result.integration_status),
                "taiwan_direct_sources_checked": list(source_result.taiwan_direct_sources_checked),
                "remaining_gaps": list(source_result.remaining_gaps),
            },
            "evaluation": {
                "items": [item.model_dump(mode="json") for item in items],
                "signals": [signal.model_dump(mode="json") for signal in evaluation.signals],
                "retail_matrix": {
                    key: value.model_dump(mode="json")
                    for key, value in sorted(evaluation.retail_matrix.items())
                },
                "crypto_matrix": {
                    key: value.model_dump(mode="json")
                    for key, value in sorted(evaluation.crypto_matrix.items())
                },
                "structural_indicators": [
                    observation.model_dump(mode="json")
                    for observation in evaluation.structural_indicators
                ],
                "audit": audit,
            },
            "coverage_cells": [cell.model_dump(mode="json") for cell in coverage_cells],
            "coverage_gaps": [gap.model_dump(mode="json") for gap in coverage_gaps],
            "degradation_reasons": degradation_reasons,
        }
        serialized = json.dumps(fingerprint, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return stable_id("run", [serialized])

    @staticmethod
    def _event_history_since(report_date: str, lookback_days: int = 30) -> str:
        start = datetime.fromisoformat(report_date).replace(tzinfo=timezone.utc) - timedelta(days=lookback_days)
        return start.isoformat(timespec="seconds")

    @staticmethod
    def _project_web(report: RadarReportV2) -> tuple[WebArtifactV1, ...]:
        content = report.canonical_json_bytes()
        content_hash = hashlib.sha256(content).hexdigest()
        full_path = f"reports/{report.date[:4]}/{report.date}/full.{content_hash}.json"
        return (
            WebArtifactV1(
                path=full_path,
                media_type="application/json",
                content_hash=content_hash,
                content=content,
            ),
            WebArtifactV1(
                path="latest.json",
                media_type="application/json",
                content_hash=content_hash,
                content=content,
            ),
        )
