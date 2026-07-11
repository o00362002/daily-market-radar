"""Deterministic web projection: validated RadarReportV2 -> immutable artifacts.

Pure and provider-neutral. Produces a set of typed WebArtifactV1 values with
content hashes and canonical JSON; the export step (radar/web/export.py) writes
them atomically and skips unchanged artifacts.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict

from radar.contracts.report import RadarReportV2, radar_report_json_schema
from radar.contracts.runtime import RuntimeContract
from radar.contracts.web import WebArtifactV1
from radar.contracts.web_projection import (
    WEB_SCHEMA_VERSION,
    DomainIndexV1,
    ReportIndexEntryV1,
    ReportSummaryV1,
    ReportsYearIndexV1,
    TaiwanIndexEntryV1,
    TaiwanIndexV1,
    TrendPointV1,
    TrendSeriesV1,
    WebManifestV1,
    canonical_json_bytes,
    web_json_schemas,
)

WEB_ROOT = "artifacts/web/v1"


def _artifact(path: str, content: bytes, media_type: str = "application/json") -> WebArtifactV1:
    return WebArtifactV1(
        path=path,
        media_type=media_type,
        content_hash=hashlib.sha256(content).hexdigest(),
        content=content,
    )


def _raw_json(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _summary(report: RadarReportV2, full_hash: str) -> ReportSummaryV1:
    items = report.items
    return ReportSummaryV1(
        date=report.date,
        run_id=report.run_id,
        profile=report.profile,
        status=report.status,
        evaluation_mode=report.evaluation_audit.effective_mode,
        is_fixture=report.source_audit.ingestion_mode == "fixture",
        degradation_reasons=list(report.degradation_reasons),
        major_count=sum(1 for item in items if item.report_lane == "major"),
        potential_count=sum(1 for item in items if item.report_lane == "potential"),
        taiwan_count=sum(1 for item in items if item.direct_taiwan_evidence),
        coverage_gap_count=len(report.coverage_gaps),
        retail_observed=sum(1 for cell in report.retail_matrix.values() if cell.status == "observed"),
        crypto_observed=sum(1 for cell in report.crypto_matrix.values() if cell.status == "observed"),
        structural_directional=sum(1 for row in report.structural_indicators if row.direction != "insufficient"),
        content_hash=full_hash,
    )


def _index_entry(report: RadarReportV2, summary: ReportSummaryV1, full_path: str, summary_path: str) -> ReportIndexEntryV1:
    return ReportIndexEntryV1(
        date=report.date,
        run_id=report.run_id,
        status=report.status,
        evaluation_mode=summary.evaluation_mode,
        is_fixture=summary.is_fixture,
        major_count=summary.major_count,
        potential_count=summary.potential_count,
        taiwan_count=summary.taiwan_count,
        summary_path=summary_path,
        full_path=full_path,
    )


def project_web(reports: list[RadarReportV2], contract: RuntimeContract, *, generated_at: str) -> list[WebArtifactV1]:
    if not reports:
        raise ValueError("cannot project web artifacts without at least one report")

    # Callers provide reports in durable write order. Preserve that order while
    # de-duplicating same-day re-runs: ``run_id`` is a content hash, not a clock,
    # so sorting by it can resurrect an older, smaller report on the live site.
    by_date: dict[str, RadarReportV2] = {}
    for report in reports:
        by_date[report.date] = report
    ordered = [by_date[date] for date in sorted(by_date)]

    artifacts: list[WebArtifactV1] = []
    entries_by_year: dict[str, list[ReportIndexEntryV1]] = defaultdict(list)
    domain_year: dict[tuple[str, str], list[ReportIndexEntryV1]] = defaultdict(list)
    taiwan_year: dict[str, list[TaiwanIndexEntryV1]] = defaultdict(list)
    trend_points: dict[str, list[TrendPointV1]] = defaultdict(list)

    latest_full_path = ""
    for report in ordered:
        year = report.date[:4]
        full_bytes = report.canonical_json_bytes()
        full_hash = hashlib.sha256(full_bytes).hexdigest()
        full_path = f"reports/{year}/{report.date}/full.{full_hash}.json"
        summary_path = f"reports/{year}/{report.date}/summary.json"

        summary = _summary(report, full_hash)
        artifacts.append(_artifact(full_path, full_bytes))
        artifacts.append(_artifact(summary_path, canonical_json_bytes(summary)))

        entry = _index_entry(report, summary, full_path, summary_path)
        entries_by_year[year].append(entry)

        report_domains = {item.primary_domain for item in report.items}
        for domain in report_domains:
            domain_year[(domain, year)].append(entry)
        if summary.taiwan_count:
            taiwan_year[year].append(
                TaiwanIndexEntryV1(
                    date=report.date, run_id=report.run_id, taiwan_count=summary.taiwan_count, summary_path=summary_path
                )
            )
        for row in report.structural_indicators:
            trend_points[row.indicator_id].append(
                TrendPointV1(
                    date=report.date,
                    direction=row.direction,
                    support_score=row.support_score,
                    counter_score=row.counter_score,
                    confidence=str(row.confidence),
                )
            )
        latest_full_path = full_path

    latest = ordered[-1]
    artifacts.append(_artifact("latest.json", latest.canonical_json_bytes()))

    for year, entries in sorted(entries_by_year.items()):
        index = ReportsYearIndexV1(year=year, entries=sorted(entries, key=lambda e: e.date))
        artifacts.append(_artifact(f"indexes/reports/{year}.json", canonical_json_bytes(index)))
    for (domain, year), entries in sorted(domain_year.items()):
        index = DomainIndexV1(domain=domain, year=year, entries=sorted(entries, key=lambda e: e.date))
        artifacts.append(_artifact(f"indexes/domains/{domain}/{year}.json", canonical_json_bytes(index)))
    for year, entries in sorted(taiwan_year.items()):
        index = TaiwanIndexV1(year=year, entries=sorted(entries, key=lambda e: e.date))
        artifacts.append(_artifact(f"indexes/taiwan/{year}.json", canonical_json_bytes(index)))
    for indicator_id in sorted(contract.structural_indicator_ids):
        series = TrendSeriesV1(
            indicator_id=indicator_id,
            points=sorted(trend_points.get(indicator_id, []), key=lambda p: p.date),
        )
        artifacts.append(_artifact(f"indexes/trends/{indicator_id}.json", canonical_json_bytes(series)))

    manifest = WebManifestV1(
        schema_version=WEB_SCHEMA_VERSION,
        generated_at=generated_at,
        latest_date=latest.date,
        latest_full_path=latest_full_path,
        report_count=len(ordered),
        report_dates=[report.date for report in ordered],
        domains=sorted(contract.report_domains),
        indicator_ids=sorted(contract.structural_indicator_ids),
        years=sorted(entries_by_year),
    )
    artifacts.append(_artifact("manifest.json", canonical_json_bytes(manifest)))

    artifacts.append(_artifact("meta/report-schema.json", _raw_json(radar_report_json_schema())))
    artifacts.append(_artifact("meta/web-schema.json", _raw_json(web_json_schemas())))
    artifacts.append(
        _artifact(
            "meta/runtime-contract.json",
            _raw_json(
                {
                    "report_domains": contract.report_domains,
                    "retail_matrix_keys": contract.retail_matrix_keys,
                    "crypto_matrix_keys": contract.crypto_matrix_keys,
                    "structural_indicator_ids": contract.structural_indicator_ids,
                }
            ),
        )
    )

    # Deterministic ordering of the artifact set itself.
    artifacts.sort(key=lambda artifact: artifact.path)
    return artifacts
