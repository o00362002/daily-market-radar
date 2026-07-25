from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_report(report: dict[str, Any], config: dict[str, Any], expected_date: str | None) -> list[str]:
    rules = config["report"]
    reasons: list[str] = []
    items = report.get("items", [])
    total = len(items)
    major = sum(item.get("report_lane") == "major" for item in items)
    major_ratio = major / total if total else 0.0

    if report.get("status") not in set(rules["allowed_statuses"]):
        reasons.append(f"report_status_not_deployable:{report.get('status')}")
    if expected_date and report.get("date") != expected_date:
        reasons.append(f"report_date_mismatch:{report.get('date')}!={expected_date}")
    if rules.get("require_live_ingestion", True):
        mode = report.get("source_audit", {}).get("ingestion_mode")
        if mode == "fixture" or not mode:
            reasons.append(f"ingestion_mode_not_live:{mode}")
    if total > int(rules["max_total_items"]):
        reasons.append(f"item_count_exceeds_limit:{total}>{rules['max_total_items']}")
    if major > int(rules["max_major_items"]):
        reasons.append(f"major_count_exceeds_limit:{major}>{rules['max_major_items']}")
    if total >= int(rules["major_ratio_min_sample"]) and major_ratio > float(rules["max_major_ratio"]):
        reasons.append(f"major_ratio_exceeds_limit:{major_ratio:.3f}>{rules['max_major_ratio']}")
    if rules.get("require_unique_event_ids", True):
        event_ids = [str(item.get("event_id", "")) for item in items]
        if len(event_ids) != len(set(event_ids)):
            reasons.append("duplicate_event_ids")
        if any(not event_id for event_id in event_ids):
            reasons.append("missing_event_id")
    return reasons


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
    if not args.report_only:
        reasons.extend(check_analysis(analysis, report, config))

    items = report.get("items", [])
    major = sum(item.get("report_lane") == "major" for item in items)
    result = {
        "valid": not reasons,
        "reasons": reasons,
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
