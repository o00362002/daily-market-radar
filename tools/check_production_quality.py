from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_report(report: dict[str, Any], config: dict[str, Any], expected_date: str | None) -> list[str]:
    """Return only conditions that make a report unsafe to deploy.

    Report volume is deliberately not a blocker. The runtime keeps every qualified
    item and the web layer performs its own readable curation, so a broad live-news
    day must not be mistaken for a corrupt production artifact.
    """

    rules = config["report"]
    reasons: list[str] = []
    items = report.get("items", [])

    if report.get("status") not in set(rules["allowed_statuses"]):
        reasons.append(f"report_status_not_deployable:{report.get('status')}")
    if expected_date and report.get("date") != expected_date:
        reasons.append(f"report_date_mismatch:{report.get('date')}!={expected_date}")
    if rules.get("require_live_ingestion", True):
        mode = report.get("source_audit", {}).get("ingestion_mode")
        if mode == "fixture" or not mode:
            reasons.append(f"ingestion_mode_not_live:{mode}")
    minimum_total = int(rules.get("minimum_total_items", 0) or 0)
    if len(items) < minimum_total:
        reasons.append(f"item_count_below_minimum:{len(items)}<{minimum_total}")
    if rules.get("require_unique_event_ids", True):
        event_ids = [str(item.get("event_id", "")) for item in items]
        if len(event_ids) != len(set(event_ids)):
            reasons.append("duplicate_event_ids")
        if any(not event_id for event_id in event_ids):
            reasons.append("missing_event_id")
    return reasons


def check_report_warnings(report: dict[str, Any], config: dict[str, Any]) -> list[str]:
    """Return review observations that should be visible but must not block Pages."""

    items = report.get("items", [])
    total = len(items)
    major = sum(item.get("report_lane") == "major" for item in items)
    major_ratio = major / total if total else 0.0
    thresholds = config["report"].get("review_thresholds", {})
    warnings: list[str] = []

    total_threshold = int(thresholds.get("total_items", 0) or 0)
    if total_threshold and total > total_threshold:
        warnings.append(f"item_count_above_review_threshold:{total}>{total_threshold}")

    major_threshold = int(thresholds.get("major_items", 0) or 0)
    if major_threshold and major > major_threshold:
        warnings.append(f"major_count_above_review_threshold:{major}>{major_threshold}")

    ratio_threshold = float(thresholds.get("major_ratio", 0) or 0)
    ratio_minimum_sample = int(thresholds.get("major_ratio_min_sample", 0) or 0)
    if (
        ratio_threshold
        and total >= ratio_minimum_sample
        and major_ratio > ratio_threshold
    ):
        warnings.append(
            f"major_ratio_above_review_threshold:{major_ratio:.3f}>{ratio_threshold}"
        )
    return warnings


def check_analysis(
    analysis: dict[str, Any] | None,
    report: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    rules = config["analysis"]
    if not rules.get("required_for_production", True):
        return []
    if analysis is None:
        return ["analysis_missing"]

    reasons: list[str] = []
    provenance = analysis.get("provenance", {})
    effective_mode = provenance.get("effective_mode")
    if effective_mode not in set(rules["allowed_effective_modes"]):
        reasons.append(f"analysis_effective_mode_not_allowed:{effective_mode}")
    if rules.get("require_provider", True) and not provenance.get("provider"):
        reasons.append("analysis_provider_missing")
    if rules.get("require_model", True) and not provenance.get("model"):
        reasons.append("analysis_model_missing")
    if rules.get("forbid_fallback", True) and provenance.get("fallback_used"):
        reasons.append("analysis_fallback_forbidden")
    if rules.get("require_same_report", True):
        if analysis.get("source_report_id") != report.get("report_id"):
            reasons.append("analysis_source_report_mismatch")
        if provenance.get("source_report_date") != report.get("date"):
            reasons.append("analysis_source_date_mismatch")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--analysis", type=Path)
    parser.add_argument("--config", type=Path, default=Path("config/production_quality_gate.json"))
    parser.add_argument("--expected-date")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    config = load_json(args.config)
    report = load_json(args.report)
    analysis = load_json(args.analysis) if args.analysis and args.analysis.exists() else None

    reasons = check_report(report, config, args.expected_date)
    warnings = check_report_warnings(report, config)
    if not args.report_only:
        reasons.extend(check_analysis(analysis, report, config))

    items = report.get("items", [])
    major = sum(item.get("report_lane") == "major" for item in items)
    result = {
        "valid": not reasons,
        "reasons": reasons,
        "warnings": warnings,
        "report": {
            "date": report.get("date"),
            "report_id": report.get("report_id"),
            "status": report.get("status"),
            "ingestion_mode": report.get("source_audit", {}).get("ingestion_mode"),
            "item_count": len(items),
            "major_count": major,
            "potential_count": len(items) - major,
        },
        "analysis": None if analysis is None else {
            "analysis_id": analysis.get("analysis_id"),
            "source_report_id": analysis.get("source_report_id"),
            "effective_mode": analysis.get("provenance", {}).get("effective_mode"),
            "provider": analysis.get("provenance", {}).get("provider"),
            "model": analysis.get("provenance", {}).get("model"),
            "fallback_used": analysis.get("provenance", {}).get("fallback_used"),
        },
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(text, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
