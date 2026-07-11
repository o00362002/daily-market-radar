"""export-web runtime: load validated reports and project immutable artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from radar.contracts.report import RadarReportV2
from radar.contracts.runtime import RuntimeContract
from radar.reporting.contracts import validate_report_contract
from radar.repositories.sqlite import SqliteRunRepository
from radar.web.export import ExportResult, export_web_artifacts
from radar.web.projection import project_web


def _load_reports(
    repo_root: Path,
    *,
    database: Path | None,
    input_report: Path | None,
    reports_dir: Path | None,
    latest: bool,
    contract: RuntimeContract,
) -> list[RadarReportV2]:
    reports: list[RadarReportV2] = []
    if database is not None:
        repository = SqliteRunRepository(database, repo_root / "migrations")
        stored = repository.list_reports()
        reports = [stored[-1]] if latest and stored else stored
    elif input_report is not None:
        reports = [RadarReportV2.from_payload(json.loads(input_report.read_text(encoding="utf-8")))]
    elif reports_dir is not None:
        for path in sorted(reports_dir.glob("*.json")):
            reports.append(RadarReportV2.from_payload(json.loads(path.read_text(encoding="utf-8"))))
    else:
        raise ValueError("export-web requires one of --database, --input or --reports-dir")

    # Only structurally valid reports may be projected. Floor policy is enforced
    # at creation/import time; stored history was valid under the policy of its
    # day and must not be retroactively invalidated by later floor changes.
    for report in reports:
        validate_report_contract(report.model_dump(mode="json"), contract=contract, enforce_floors=False)
    return reports


def export_web(
    repo_root: Path,
    out_dir: Path,
    *,
    database: Path | None = None,
    input_report: Path | None = None,
    reports_dir: Path | None = None,
    latest: bool = False,
    incremental: bool = True,
    generated_at: str | None = None,
    legacy_reports_dir: Path | None = None,
) -> ExportResult:
    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    reports = _load_reports(
        repo_root,
        database=database,
        input_report=input_report,
        reports_dir=reports_dir,
        latest=latest,
        contract=contract,
    )
    stamp = generated_at or datetime.now(timezone.utc).isoformat()
    artifacts = list(project_web(reports, contract, generated_at=stamp))
    if legacy_reports_dir is not None:
        artifacts.extend(_load_legacy_artifacts(legacy_reports_dir))
    return export_web_artifacts(artifacts, out_dir, incremental=incremental)


def _load_legacy_artifacts(legacy_reports_dir: Path):
    from radar.web.legacy import project_legacy

    files: list[tuple[str, str]] = []
    for path in sorted(legacy_reports_dir.glob("[0-9][0-9][0-9][0-9]/**/*.md")):
        relative = f"reports/{path.relative_to(legacy_reports_dir)}"
        files.append((relative, path.read_text(encoding="utf-8")))
    return project_legacy(files)
