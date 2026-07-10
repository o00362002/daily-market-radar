from __future__ import annotations

from pathlib import Path

from radar.domain.models import CoverageCell, RunResult, stable_id
from radar.pipeline.classify import classify_potential_signals
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.coverage import audit_coverage
from radar.pipeline.deduplicate import deduplicate_documents
from radar.pipeline.ingest import ingest_fixture_documents
from radar.reporting.contracts import validate_report_contract
from radar.reporting.planner import plan_daily_items


DOMAINS = [
    "global_markets_macro",
    "policy_geopolitics",
    "ai_agents_applications",
    "science_technology_industry",
    "crypto_rwa_agent_payments",
    "retail_consumer_fashion",
    "labor_demographics_consumption_pressure",
]


def run_daily_fixture(
    repo_root: Path,
    date: str,
    freshrss_available: bool,
    external_discovery_available: bool = True,
) -> RunResult:
    documents = deduplicate_documents(ingest_fixture_documents())
    events = cluster_documents(documents)
    signals = classify_potential_signals(events)
    items = plan_daily_items(events)
    coverage_cells = [
        CoverageCell(
            domain="ai_agents_applications",
            macro_region="Taiwan",
            language="zh-Hant",
            source_role="official",
            channel="rss",
            time_window="24h",
            status="failing" if not freshrss_available else "healthy",
        )
    ]
    gaps = audit_coverage(coverage_cells)
    degradation_reasons: list[str] = []
    if not freshrss_available:
        degradation_reasons.append("freshrss_unavailable")
    if not external_discovery_available:
        degradation_reasons.append("external_discovery_unavailable")
        gaps.insert(
            0,
            {
                "domain": "all",
                "macro_region": "global",
                "language": "multi",
                "source_role": "discovery",
                "channel": "external",
                "time_window": "24h",
                "reason": "external_discovery_unavailable",
                "message": "external discovery unavailable; report is partial",
            },
        )
    report = {
        "run_id": stable_id("run", [str(repo_root), date, ",".join(degradation_reasons)]),
        "profile": "daily_push",
        "items": [item.to_dict() for item in items],
        "coverage_gaps": gaps,
        "signals": [signal.__dict__ for signal in signals],
    }
    validate_report_contract(report)
    return RunResult(
        run_id=report["run_id"],
        status="partial" if degradation_reasons or gaps else "complete",
        degradation_reasons=degradation_reasons,
        languages_seen=sorted({doc.language for doc in documents}),
        regions_seen=sorted({doc.macro_region for doc in documents}),
        domains_seen=sorted({doc.primary_domain for doc in documents}, key=DOMAINS.index),
        event_ids=[event.event_id for event in events],
        selected_item_ids=[item.item_id for item in items],
        report=report,
    )
