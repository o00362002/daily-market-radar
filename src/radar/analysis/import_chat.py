from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from radar.analysis.builder import build_deterministic_analysis, load_analysis_config
from radar.contracts.analysis import AIAnalysisV1, ai_analysis_json_schema
from radar.contracts.report import RadarReportV2


_IMMUTABLE_BASELINE_FIELDS = (
    "translations",
    "structural_indicators",
    "linked_indicators",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m radar.analysis.import_chat")
    parser.add_argument("--report", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default="artifacts/web/v1/ai-analysis")
    parser.add_argument("--receipt", default="chat-analysis-import-receipt.json")
    parser.add_argument(
        "--materialize-analysis",
        action="store_true",
        help=(
            "Fill empty immutable baseline arrays from the validated deterministic baseline and "
            "rewrite the input as a complete canonical AIAnalysisV1 after validation."
        ),
    )
    return parser


def _parse_timestamp(value: str, *, field: str, allow_unknown: bool = False) -> None:
    if allow_unknown and value == "unknown":
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601 or 'unknown', got {value!r}") from exc


def _validate_https_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"supplemental evidence URL must be absolute HTTPS: {value!r}")


def _validate_source_ids(analysis: AIAnalysisV1, report: RadarReportV2) -> None:
    allowed = {item.event_id for item in report.items}
    referenced: set[str] = set()
    for finding in analysis.key_findings:
        referenced.update(finding.source_event_ids)
    for trend in analysis.future_trends:
        referenced.update(trend.source_event_ids)
    for row in analysis.linked_indicators:
        referenced.update(row.source_event_ids)
    unknown = sorted(referenced - allowed)
    if unknown:
        raise ValueError(f"analysis references event ids outside source report: {unknown}")


def _validate_supplemental_evidence(analysis: AIAnalysisV1) -> None:
    ids: set[str] = set()
    fingerprints: set[tuple[str, str]] = set()
    for row in analysis.supplemental_evidence:
        if row.evidence_id in ids:
            raise ValueError(f"duplicate supplemental evidence id: {row.evidence_id}")
        ids.add(row.evidence_id)
        if not row.gap_ref.strip():
            raise ValueError(f"supplemental evidence {row.evidence_id} is missing gap_ref")
        if not row.title.strip() or not row.summary.strip():
            raise ValueError(f"supplemental evidence {row.evidence_id} needs title and summary")
        _validate_https_url(row.url)
        _parse_timestamp(row.published_at, field="published_at", allow_unknown=True)
        _parse_timestamp(row.fetched_at, field="fetched_at")
        fingerprint = (row.url, row.title.casefold().strip())
        if fingerprint in fingerprints:
            raise ValueError(f"duplicate supplemental evidence event: {row.url}")
        fingerprints.add(fingerprint)


def _find_previous_report(*, report: RadarReportV2, repo_root: Path) -> RadarReportV2 | None:
    """Find the latest prior same-profile report from the formal web export.

    ``export-web`` runs before ChatGPT import and projects the durable report
    history under ``artifacts/web/v1/reports``. Reusing that projection avoids a
    parallel history store while restoring real day-over-day linked-indicator
    deltas during immutable baseline hydration.
    """

    reports_root = repo_root / "artifacts" / "web" / "v1" / "reports"
    if not reports_root.exists():
        return None

    candidates: list[RadarReportV2] = []
    for path in reports_root.glob("*/*/full.*.json"):
        try:
            candidate = RadarReportV2.from_payload(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if candidate.date >= report.date or candidate.profile != report.profile:
            continue
        candidates.append(candidate)
    if not candidates:
        return None
    return max(candidates, key=lambda candidate: candidate.date)


def _deterministic_baseline(
    *,
    report: RadarReportV2,
    repo_root: Path,
    generated_at: str,
) -> tuple[AIAnalysisV1, RadarReportV2 | None]:
    config = load_analysis_config(repo_root)
    previous_report = _find_previous_report(report=report, repo_root=repo_root)
    baseline = build_deterministic_analysis(
        report,
        previous_report,
        config,
        generated_at=generated_at,
        requested_mode="deterministic",
    )
    return baseline, previous_report


def hydrate_immutable_baseline_fields(
    *,
    report: RadarReportV2,
    payload: dict[str, Any],
    repo_root: Path,
) -> tuple[dict[str, Any], list[str]]:
    """Hydrate only explicitly empty immutable arrays from the formal baseline.

    This keeps the ChatGPT-authored file small enough for bounded connector writes while preserving
    the exact deterministic translations, structural indicators and linked indicators. Non-empty
    values are never overwritten: any attempted rewrite still reaches the normal equality checks and
    is rejected.
    """

    provenance = payload.get("provenance")
    generated_at = provenance.get("generated_at") if isinstance(provenance, dict) else None
    if not isinstance(generated_at, str) or not generated_at:
        raise ValueError("analysis provenance.generated_at is required before baseline hydration")

    empty_fields = [field for field in _IMMUTABLE_BASELINE_FIELDS if payload.get(field) == []]
    if not empty_fields:
        return payload, []

    baseline, _ = _deterministic_baseline(
        report=report,
        repo_root=repo_root,
        generated_at=generated_at,
    )
    baseline_payload = baseline.model_dump(mode="json")
    hydrated = dict(payload)
    for field in empty_fields:
        hydrated[field] = baseline_payload[field]
    return hydrated, empty_fields


def validate_chat_analysis(
    *,
    report: RadarReportV2,
    analysis: AIAnalysisV1,
    repo_root: Path,
) -> dict[str, object]:
    baseline, previous_report = _deterministic_baseline(
        report=report,
        repo_root=repo_root,
        generated_at=analysis.provenance.generated_at,
    )

    checks = {
        "date_matches": analysis.date == report.date,
        "source_report_matches": analysis.source_report_id == report.report_id,
        "source_date_matches": analysis.provenance.source_report_date == report.date,
        "source_run_matches": analysis.provenance.source_run_id == report.run_id,
        "context_hash_matches": analysis.provenance.source_context_hash == baseline.provenance.source_context_hash,
        "schema_matches": analysis.provenance.schema_version == "ai-analysis/v1",
        "chat_mode": analysis.provenance.effective_mode == "chat-assisted",
        "provider_present": bool(analysis.provenance.provider),
        "not_fallback": not analysis.provenance.fallback_used,
        "validation_status": analysis.provenance.validation_status == "valid",
        "structural_indicators_preserved": analysis.structural_indicators == baseline.structural_indicators,
        "linked_indicators_preserved": analysis.linked_indicators == baseline.linked_indicators,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ValueError(f"chat analysis validation failed: {failed}")

    _validate_source_ids(analysis, report)
    _validate_supplemental_evidence(analysis)

    return {
        "checks": checks,
        "previous_report_date": previous_report.date if previous_report is not None else None,
        "supplemental_evidence_count": len(analysis.supplemental_evidence),
        "finding_count": len(analysis.key_findings),
        "trend_count": len(analysis.future_trends),
    }


def _write_analysis(output_dir: Path, analysis: AIAnalysisV1) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_path = output_dir / f"{analysis.date}.json"
    latest_path = output_dir / "latest.json"
    schema_path = output_dir / "schema.json"
    payload = analysis.canonical_json_bytes()
    date_path.write_bytes(payload)
    latest_path.write_bytes(payload)
    schema_path.write_text(
        json.dumps(ai_analysis_json_schema(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return [str(path) for path in (date_path, latest_path, schema_path)]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    receipt_path = Path(args.receipt).resolve()
    analysis_path = Path(args.analysis).resolve()
    receipt: dict[str, object]

    try:
        report = RadarReportV2.from_payload(json.loads(Path(args.report).read_text(encoding="utf-8")))
        raw_payload = json.loads(analysis_path.read_text(encoding="utf-8"))
        hydrated_payload, hydrated_fields = hydrate_immutable_baseline_fields(
            report=report,
            payload=raw_payload,
            repo_root=repo_root,
        )
        analysis = AIAnalysisV1.model_validate(hydrated_payload)
        result = validate_chat_analysis(report=report, analysis=analysis, repo_root=repo_root)
        if args.materialize_analysis and hydrated_fields:
            analysis_path.write_bytes(analysis.canonical_json_bytes())
        written = _write_analysis(Path(args.output_dir).resolve(), analysis)
        receipt = {
            "valid": True,
            "date": analysis.date,
            "analysis_id": analysis.analysis_id,
            "source_run_id": analysis.provenance.source_run_id,
            "source_context_hash": analysis.provenance.source_context_hash,
            "effective_mode": analysis.provenance.effective_mode,
            "provider": analysis.provenance.provider,
            "model": analysis.provenance.model,
            "hydrated_fields": hydrated_fields,
            "materialized_input": bool(args.materialize_analysis and hydrated_fields),
            "written": written,
            **result,
        }
        code = 0
    except Exception as exc:  # noqa: BLE001 - receipt must explain every rejection
        receipt = {
            "valid": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        code = 1

    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
