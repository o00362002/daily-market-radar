from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from radar.adapters.rss import FeedFailure, fetch_registry_rss_documents
from radar.domain.models import CoverageCell, Document, ReportItem, RunResult, stable_id
from radar.pipeline.classify import classify_potential_signals
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.coverage import audit_coverage, enforce_major_potential_split
from radar.pipeline.deduplicate import deduplicate_documents
from radar.pipeline.ingest import ingest_fixture_documents
from radar.reporting.contracts import validate_report_contract
from radar.reporting.planner import plan_daily_items
from radar.repositories.sqlite import SqliteRunRepository
from radar.runtime.contract import RuntimeContract
from radar.schemas.source import SourceRegistry


def _empty_matrix(keys: list[str], reason: str) -> dict[str, dict[str, Any]]:
    return {
        key: {
            "status": "insufficient",
            "signal_ids": [],
            "data_checked": [],
            "gap": reason,
        }
        for key in keys
    }


def _empty_structural_indicators(indicator_ids: list[str], reason: str) -> list[dict[str, Any]]:
    return [
        {
            "indicator_id": indicator_id,
            "direction": "insufficient",
            "confidence": "insufficient",
            "supporting_signal_ids": [],
            "counter_signal_ids": [],
            "missing_data": [reason],
            "one_sentence_read": "Insufficient verified evidence for a directional update.",
            "next_verification": ["run indicator-specific data checks and semantic mapping"],
        }
        for indicator_id in indicator_ids
    ]


def _apply_slot_caps(
    items: list[ReportItem],
    contract: RuntimeContract,
    profile_name: str,
) -> list[ReportItem]:
    profile = contract.profile(profile_name)
    grouped: dict[tuple[str, str], list[ReportItem]] = defaultdict(list)
    for item in items:
        grouped[(item.primary_domain, item.report_lane)].append(item)

    selected: list[ReportItem] = []
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


def _coverage_cells(
    documents: list[Document],
    contract: RuntimeContract,
    *,
    channel: str,
    taiwan_channel_status: str,
) -> list[CoverageCell]:
    observed_by_domain = Counter(doc.primary_domain for doc in documents)
    cells = [
        CoverageCell(
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
    cells.append(
        CoverageCell(
            domain="all",
            macro_region="Taiwan",
            language="zh-Hant",
            source_role="direct",
            channel=channel,
            time_window="24h",
            status=taiwan_channel_status,
            observed_count=sum(1 for doc in documents if doc.macro_region == "Taiwan"),
        )
    )
    return cells


def _feed_failure_gaps(failures: list[FeedFailure]) -> list[dict[str, str]]:
    return [
        {
            "domain": "unknown_until_source_mapping",
            "macro_region": "source_registry",
            "language": "source_defined",
            "source_role": "rss",
            "channel": failure.adapter_url,
            "time_window": "24h",
            "reason": "feed_fetch_failed",
            "message": f"{failure.source_id}: {failure.reason}",
        }
        for failure in failures
    ]


def _run_from_documents(
    *,
    repo_root: Path,
    date: str,
    profile_name: str,
    contract: RuntimeContract,
    documents: list[Document],
    ingestion_mode: str,
    source_audit: dict[str, Any],
    degradation_reasons: list[str],
    extra_gaps: list[dict[str, str]],
    taiwan_channel_status: str,
    database_path: Path | None = None,
) -> RunResult:
    original_count = len(documents)
    documents = deduplicate_documents(documents)
    duplicate_rejection_count = original_count - len(documents)
    events = cluster_documents(documents)
    signals = classify_potential_signals(events)
    planned_items = plan_daily_items(events)
    items = _apply_slot_caps(planned_items, contract, profile_name)

    major_event_ids = [item.event_id for item in items if item.report_lane == "major"]
    potential_event_ids = [item.event_id for item in items if item.report_lane == "potential"]
    enforce_major_potential_split(major_event_ids, potential_event_ids)

    coverage_cells = _coverage_cells(
        documents,
        contract,
        channel=ingestion_mode,
        taiwan_channel_status=taiwan_channel_status,
    )
    gaps = [*extra_gaps, *audit_coverage(coverage_cells)]
    selected_item_ids = [item.item_id for item in items]
    run_id = stable_id("run", [str(repo_root), date, profile_name, ingestion_mode, ",".join(degradation_reasons)])
    report_status = "partial" if degradation_reasons or gaps else "complete"
    direct_taiwan_count = sum(item.taiwan_direct_count for item in items)

    report: dict[str, Any] = {
        "run_id": run_id,
        "date": date,
        "profile": profile_name,
        "status": report_status,
        "degradation_reasons": degradation_reasons,
        "items": [item.to_dict() for item in items],
        "coverage_cells": [cell.__dict__ for cell in coverage_cells],
        "coverage_gaps": gaps,
        "signals": [signal.__dict__ for signal in signals],
        "source_audit": {"ingestion_mode": ingestion_mode, **source_audit},
        "rejection_counters": {
            "duplicate_rejection_count": duplicate_rejection_count,
            "field_overlap_rejection_count": 0,
            "niche_low_novelty_rejection_count": 0,
            "candidate_retry_paths_used": source_audit.get("candidate_retry_paths_used", []),
            "taiwan_qualified_item_count_after_audit": direct_taiwan_count,
            "taiwan_direct_sources_checked": source_audit.get("taiwan_direct_sources_checked", []),
        },
        "retail_matrix": _empty_matrix(contract.retail_matrix_keys, f"{ingestion_mode}: semantic matrix evaluation pending"),
        "crypto_matrix": _empty_matrix(contract.crypto_matrix_keys, f"{ingestion_mode}: quantitative matrix evaluation pending"),
        "structural_indicators": _empty_structural_indicators(
            contract.structural_indicator_ids,
            f"{ingestion_mode}: structural indicator evaluator not yet connected",
        ),
        "backtest": {
            "status": "partial" if report_status != "complete" else "complete",
            "findings": [
                "runtime structure validated",
                "semantic matrices and structural indicators still require dedicated evaluators",
            ],
            "next_adjustments": [
                "add web/API/social adapters",
                "add historical event repository for material-delta comparison",
                "connect indicator-specific data evaluators",
            ],
        },
        "contract_version": "2.0",
    }
    validate_report_contract(report, contract=contract)

    if database_path is not None:
        repository = SqliteRunRepository(database_path, repo_root / "migrations")
        repository.save_report(report)

    domains_seen = sorted(
        {doc.primary_domain for doc in documents},
        key=lambda domain: contract.report_domains.index(domain),
    )
    return RunResult(
        run_id=run_id,
        status=report_status,
        degradation_reasons=degradation_reasons,
        languages_seen=sorted({doc.language for doc in documents}),
        regions_seen=sorted({doc.macro_region for doc in documents}),
        domains_seen=domains_seen,
        event_ids=[event.event_id for event in events],
        selected_item_ids=selected_item_ids,
        report=report,
    )


def run_daily_fixture(
    repo_root: Path,
    date: str,
    freshrss_available: bool,
    external_discovery_available: bool = True,
    profile_name: str = "daily_push",
    database_path: Path | None = None,
) -> RunResult:
    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    degradation_reasons = ["fixture_ingestion_only"]
    if not freshrss_available:
        degradation_reasons.append("freshrss_unavailable")
    if not external_discovery_available:
        degradation_reasons.append("external_discovery_unavailable")

    extra_gaps: list[dict[str, str]] = []
    if not external_discovery_available:
        extra_gaps.append(
            {
                "domain": "all",
                "macro_region": "global",
                "language": "multi",
                "source_role": "discovery",
                "channel": "external",
                "time_window": "24h",
                "reason": "external_discovery_unavailable",
                "message": "external discovery unavailable; report is partial",
            }
        )

    return _run_from_documents(
        repo_root=repo_root,
        date=date,
        profile_name=profile_name,
        contract=contract,
        documents=ingest_fixture_documents(),
        ingestion_mode="fixture",
        source_audit={
            "registry_checked": True,
            "freshrss_checked": freshrss_available,
            "external_discovery_checked": external_discovery_available,
            "candidate_retry_paths_used": [],
            "taiwan_direct_sources_checked": ["twse"],
            "remaining_gap": ["fixture data is not live source coverage"],
        },
        degradation_reasons=degradation_reasons,
        extra_gaps=extra_gaps,
        taiwan_channel_status="healthy" if freshrss_available else "failing",
        database_path=database_path,
    )


def run_daily_live_rss(
    repo_root: Path,
    date: str,
    *,
    profile_name: str = "daily_push",
    timeout_seconds: int = 12,
    per_feed_limit: int = 20,
    database_path: Path | None = None,
) -> RunResult:
    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    registry = SourceRegistry.from_file(repo_root / "config/source_registry.json")
    registry.validate()
    documents, failures, checked_sources = fetch_registry_rss_documents(
        registry,
        timeout_seconds=timeout_seconds,
        per_feed_limit=per_feed_limit,
    )

    non_rss_enabled = [
        source.source_id
        for source in registry.sources
        if source.enabled and not any(adapter.kind == "rss" for adapter in source.adapters)
    ]
    degradation_reasons: list[str] = []
    if failures:
        degradation_reasons.append("rss_fetch_failures")
    if non_rss_enabled:
        degradation_reasons.append("web_api_social_adapters_not_executed")
    if not documents:
        degradation_reasons.append("no_live_documents_ingested")

    taiwan_rss_sources = [
        source.source_id
        for source in registry.sources
        if source.macro_region == "Taiwan" and any(adapter.kind == "rss" for adapter in source.adapters)
    ]
    taiwan_status = "healthy" if any(doc.macro_region == "Taiwan" for doc in documents) else "empty"

    return _run_from_documents(
        repo_root=repo_root,
        date=date,
        profile_name=profile_name,
        contract=contract,
        documents=documents,
        ingestion_mode="live_rss",
        source_audit={
            "registry_checked": True,
            "rss_sources_checked": checked_sources,
            "rss_failures": [failure.to_dict() for failure in failures],
            "web_api_social_sources_not_executed": non_rss_enabled,
            "external_discovery_checked": False,
            "candidate_retry_paths_used": [],
            "taiwan_direct_sources_checked": taiwan_rss_sources,
            "remaining_gap": [
                "web/API/social adapters are not yet executed by run_daily_live_rss",
                "external discovery and FreshRSS inbox are not connected",
            ],
        },
        degradation_reasons=degradation_reasons,
        extra_gaps=_feed_failure_gaps(failures),
        taiwan_channel_status=taiwan_status,
        database_path=database_path,
    )
