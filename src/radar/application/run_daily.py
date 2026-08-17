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
    CompetitorAuditV1,
    CoverageCellV2,
    CoverageGapV2,
    EventResolutionAuditV1,
    RadarReportV2,
    RejectionCountersV2,
    ReportItemV2,
    SourceAuditV2,
)
from radar.contracts.runtime import RuntimeContract
from radar.contracts.web import PublicationReceiptV1, WebArtifactV1
from radar.domain.event_resolution import EventResolutionOutcome
from radar.domain.models import Document, Event, stable_id
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deduplicate import deduplicate_documents
from radar.pipeline.deltas import indicator_events_for_date, material_events, resolve_events
from radar.pipeline.enrich import enrich_documents
from radar.reporting.contracts import validate_report_contract
from radar.ports import (
    CompetitorMonitor,
    DocumentRepository,
    EventRepository,
    IndicatorRepository,
    IntelligenceEvaluator,
    ReportPublisher,
    ReportRepository,
    RunPersistenceBatch,
    SourceAdapter,
    SourceFetchRequest,
    SourceFetchResult,
    StateStore,
    UnitOfWork,
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
    unit_of_work: UnitOfWork
    publishers: tuple[ReportPublisher, ...]
    competitor_monitor: CompetitorMonitor | None = None


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

        competitor_result = (
            self._dependencies.competitor_monitor.run(request.date, started_at)
            if self._dependencies.competitor_monitor is not None
            else None
        )
        competitor_audit = (
            competitor_result.audit if competitor_result is not None else self._empty_competitor_audit()
        )

        source_result = self._collect(request)
        normalized = self._dependencies.source_adapter.normalize(source_result)
        classified = enrich_documents(
            normalized,
            canonical_domains=contract.report_domains,
            domain_aliases=contract.domain_aliases,
        )
        documents = deduplicate_documents(classified)
        duplicate_rejection_count = len(normalized) - len(documents)

        prior_events = self._dependencies.event_repository.find_recent_events(self._event_history_since(request.date))
        resolution = resolve_events(cluster_documents(documents), prior_events, observed_at=started_at)
        events = resolution.events

        reportable_events = material_events(events, report_date=request.date)
        indicator_events = indicator_events_for_date(events, report_date=request.date)
        # The evaluator receives the union. News planning rejects indicator-only
        # events by contract, while matrices/structural indicators can use a
        # quarterly/monthly measurement whose observation period is outside the
        # daily-news freshness window. Dedup by event_id also keeps same-day live
        # measurements from appearing twice when their fetched/published timestamp
        # already falls inside today's news window.
        evaluation_events_by_id = {event.event_id: event for event in reportable_events}
        evaluation_events_by_id.update({event.event_id: event for event in indicator_events})
        evaluation_events = sorted(evaluation_events_by_id.values(), key=lambda event: event.event_id)

        evaluation = self._dependencies.evaluator.evaluate(
            EvaluationRequest(
                date=request.date,
                profile=request.profile,
                requested_mode=request.evaluation_mode,
                events=tuple(evaluation_events),
                contract=contract,
                started_at=started_at,
            )
        )
        items = self._select_items(list(evaluation.items), contract)
        floor_gaps, floor_reasons = self._floor_shortfalls(items, contract, request.profile)
        coverage_cells = self._coverage_cells(documents, contract, request.ingestion_mode)
        competitor_gaps = self._competitor_gaps(competitor_audit)
        coverage_gaps = [
            *source_result.coverage_gaps,
            *self._coverage_gaps(coverage_cells),
            *floor_gaps,
            *competitor_gaps,
        ]
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
            [
                *evaluation.audit.degradation_reasons,
                *floor_reasons,
                *self._competitor_degradation_reasons(competitor_audit),
            ],
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
            competitor_audit,
        )

        integration_status = dict(source_result.integration_status)
        integration_status[self._dependencies.source_adapter.adapter_id] = source_health.status
        integration_status["competitor_monitor"] = self._competitor_integration_status(competitor_audit)
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
            competitor_audit=competitor_audit,
            retail_matrix=evaluation.retail_matrix,
            crypto_matrix=evaluation.crypto_matrix,
            structural_indicators=list(evaluation.structural_indicators),
            evaluation_audit=evaluation.audit,
            event_resolution_audit=self._event_resolution_audit(resolution),
            backtest=BacktestV1(
                status="complete" if report_status == "complete" else "partial",
                findings=["provider-neutral application flow and report contract validated"],
                next_adjustments=list(source_result.remaining_gaps),
            ),
            contract_version="2.0",
        )
        validate_report_contract(report.model_dump(mode="json"), contract=contract)

        artifacts = self._project_web(report)
        state_entries: list[tuple[str, bytes]] = [
            (f"last-valid-report:{request.profile}", report.canonical_json_bytes())
        ]
        if competitor_result is not None:
            state_entries.append((competitor_result.state_key, competitor_result.state_value))
        batch = RunPersistenceBatch(
            report=report,
            documents=tuple(documents),
            events=tuple(events),
            indicator_observations=tuple(evaluation.structural_indicators),
            state_entries=tuple(state_entries),
            match_records=tuple(resolution.match_records),
            observed_at=started_at,
        )
        self._dependencies.unit_of_work.commit_run(batch)

        self._dependencies.web_artifact_store.commit(artifacts)
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
    def _select_items(
        items: list[ReportItemV2],
        contract: RuntimeContract,
    ) -> list[ReportItemV2]:
        grouped: dict[tuple[str, str], list[ReportItemV2]] = defaultdict(list)
        for item in items:
            grouped[(item.primary_domain, item.report_lane)].append(item)

        selected: list[ReportItemV2] = []
        for domain in contract.report_domains:
            for lane in ("major", "potential"):
                selected.extend(
                    sorted(
                        grouped.get((domain, lane), []),
                        key=lambda item: (
                            item.importance_score if lane == "major" else item.potential_score,
                            item.confidence_score,
                            item.item_id,
                        ),
                        reverse=True,
                    )
                )
        return selected

    @staticmethod
    def _floor_shortfalls(
        items: list[ReportItemV2],
        contract: RuntimeContract,
        profile_name: str,
    ) -> tuple[list[CoverageGapV2], list[str]]:
        profile = contract.profile(profile_name)
        major = sum(1 for item in items if item.report_lane == "major")
        potential = sum(1 for item in items if item.report_lane == "potential")
        taiwan = sum(1 for item in items if item.direct_taiwan_evidence)

        gaps: list[CoverageGapV2] = []
        reasons: list[str] = []
        for lane, count, floor in (
            ("major", major, profile.min_major_items),
            ("potential", potential, profile.min_potential_items),
            ("taiwan", taiwan, profile.min_taiwan_items),
        ):
            if count < floor:
                message = f"{lane} floor unmet: {count} < {floor}"
                gaps.append(
                    CoverageGapV2(
                        domain="all",
                        macro_region="global" if lane != "taiwan" else "Taiwan",
                        language="multi",
                        source_role="coverage_floor",
                        channel="report",
                        time_window="same_day",
                        reason=f"{lane}_floor_unmet",
                        message=message,
                    )
                )
                reasons.append(message)
        return gaps, reasons

    @staticmethod
    def _coverage_cells(
        documents: list[Document],
        contract: RuntimeContract,
        ingestion_mode: str,
    ) -> list[CoverageCellV2]:
        source_roles_by_domain: dict[str, set[str]] = defaultdict(set)
        for document in documents:
            source_roles = document.facts.get("source_roles") or []
            for role in source_roles:
                source_roles_by_domain[document.primary_domain].add(str(role))
        cells = []
        for domain in contract.report_domains:
            observed_count = sum(1 for document in documents if document.primary_domain == domain)
            role_count = len(source_roles_by_domain.get(domain, set()))
            status = "observed" if observed_count and role_count else "insufficient"
            cells.append(
                CoverageCellV2(
                    domain=domain,
                    macro_region="multi",
                    language="multi",
                    source_role="multi",
                    channel=ingestion_mode,
                    time_window="24h",
                    status=status,
                    observed_count=observed_count,
                )
            )
        return cells

    @staticmethod
    def _coverage_gaps(cells: list[CoverageCellV2]) -> list[CoverageGapV2]:
        return [
            CoverageGapV2(
                domain=cell.domain,
                macro_region=cell.macro_region,
                language=cell.language,
                source_role=cell.source_role,
                channel=cell.channel,
                time_window=cell.time_window,
                reason="coverage_cell_insufficient",
                message=f"coverage insufficient for {cell.domain}",
            )
            for cell in cells
            if cell.status != "observed"
        ]

    @staticmethod
    def _degradation_reasons(
        source_result: SourceFetchResult,
        evaluator_reasons: list[str],
        source_health_status: str,
        credentials_available: bool,
    ) -> list[str]:
        reasons = list(dict.fromkeys([*source_result.degradation_reasons, *evaluator_reasons]))
        if source_health_status not in {"healthy", "available"}:
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
        competitor_audit: CompetitorAuditV1,
    ) -> str:
        payload = {
            "date": request.date,
            "profile": request.profile,
            "ingestion_mode": request.ingestion_mode,
            "evaluation_mode": request.evaluation_mode,
            "document_hashes": sorted(document.content_hash for document in documents),
            "event_ids": sorted(event.event_id for event in events),
            "source_result": {
                "sources_checked": list(source_result.sources_checked),
                "failures": [failure.model_dump(mode="json") for failure in source_result.failures],
                "remaining_gaps": list(source_result.remaining_gaps),
            },
            "evaluation": {
                "source_context_hash": evaluation.audit.source_context_hash,
                "items": [item.model_dump(mode="json") for item in evaluation.items],
                "signals": [signal.model_dump(mode="json") for signal in evaluation.signals],
                "structural_indicators": [
                    row.model_dump(mode="json") for row in evaluation.structural_indicators
                ],
            },
            "selected_items": [item.item_id for item in items],
            "coverage_cells": [cell.model_dump(mode="json") for cell in coverage_cells],
            "coverage_gaps": [gap.model_dump(mode="json") for gap in coverage_gaps],
            "degradation_reasons": degradation_reasons,
            "competitor_audit": competitor_audit.model_dump(mode="json"),
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return stable_id("run", [hashlib.sha256(encoded).hexdigest()])

    @staticmethod
    def _event_history_since(report_date: str) -> str:
        try:
            parsed = datetime.fromisoformat(report_date).replace(tzinfo=timezone.utc)
        except ValueError:
            parsed = datetime.now(timezone.utc)
        return (parsed - timedelta(days=120)).isoformat()

    @staticmethod
    def _event_resolution_audit(resolution: EventResolutionOutcome) -> EventResolutionAuditV1:
        strategy_counts = Counter(record.match_strategy for record in resolution.match_records)
        delta_counts = Counter(
            delta.delta_type
            for event in resolution.events
            for delta in event.deltas
        )
        return EventResolutionAuditV1(
            events_observed=resolution.events_observed,
            new_events=resolution.new_events,
            matched_existing_events=resolution.matched_existing_events,
            material_events=resolution.material_events,
            unchanged_events=resolution.unchanged_events,
            duplicate_only_events=resolution.duplicate_only_events,
            unresolved_matches=resolution.unresolved_matches,
            match_strategy_counts=dict(strategy_counts),
            delta_type_counts=dict(delta_counts),
            title_only_changes_rejected=resolution.title_only_changes_rejected,
            background_only_rejected=resolution.background_only_rejected,
        )

    @staticmethod
    def _empty_competitor_audit() -> CompetitorAuditV1:
        return CompetitorAuditV1(
            registry_version="unavailable",
            source_registry_version="unavailable",
            checked_at="",
            fixed_target_count=0,
            checked_target_count=0,
            updated_target_count=0,
            baseline_target_count=0,
            partial_target_count=0,
            failed_target_count=0,
            not_executed_target_count=0,
            checked_ids=[],
            updated_ids=[],
            baseline_ids=[],
            partial_ids=[],
            failed_ids=[],
            not_executed_ids=[],
            checks=[],
        )

    @staticmethod
    def _competitor_gaps(audit: CompetitorAuditV1) -> list[CoverageGapV2]:
        gaps = []
        if audit.fixed_target_count == 0:
            return gaps
        for check in audit.checks:
            if check.status not in {"failed", "partial", "not_executed"}:
                continue
            reason = f"competitor_{check.status}"
            gaps.append(
                CoverageGapV2(
                    domain="retail_consumer_fashion",
                    macro_region=check.market,
                    language="multi",
                    source_role="official_competitor",
                    channel="official_web",
                    time_window="daily",
                    reason=reason,
                    message=check.summary,
                )
            )
        return gaps

    @staticmethod
    def _competitor_degradation_reasons(audit: CompetitorAuditV1) -> list[str]:
        reasons = []
        if audit.failed_target_count:
            reasons.append("competitor_monitor_failed_targets")
        if audit.partial_target_count:
            reasons.append("competitor_monitor_partial_targets")
        if audit.not_executed_target_count:
            reasons.append("competitor_monitor_not_executed_targets")
        return reasons

    @staticmethod
    def _competitor_integration_status(audit: CompetitorAuditV1) -> str:
        if audit.fixed_target_count == 0:
            return "not_executed"
        if audit.failed_target_count == audit.fixed_target_count:
            return "failed"
        if audit.failed_target_count or audit.partial_target_count:
            return "partial"
        return "checked"

    def _project_web(self, report: RadarReportV2) -> tuple[WebArtifactV1, ...]:
        summary = {
            "run_id": report.run_id,
            "date": report.date,
            "status": report.status,
            "domains": list(dict.fromkeys(item.primary_domain for item in report.items)),
            "item_count": len(report.items),
            "degradation_reasons": list(report.degradation_reasons),
            "backtest_status": report.backtest.status,
            "contract_version": report.contract_version,
        }
        full = report.model_dump(mode="json")
        return (
            WebArtifactV1(path="artifacts/web/v1/latest.json", content=json.dumps(full, ensure_ascii=False, indent=2) + "\n"),
            WebArtifactV1(path=f"artifacts/web/v1/history/{report.date}.json", content=json.dumps(full, ensure_ascii=False, indent=2) + "\n"),
            WebArtifactV1(path="artifacts/web/v1/summary.json", content=json.dumps(summary, ensure_ascii=False, indent=2) + "\n"),
        )
