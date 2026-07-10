from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from radar.runtime.contract import RuntimeContract


REQUIRED_REPORT_FIELDS = {
    "run_id",
    "date",
    "profile",
    "status",
    "degradation_reasons",
    "items",
    "coverage_cells",
    "coverage_gaps",
    "source_audit",
    "rejection_counters",
    "retail_matrix",
    "crypto_matrix",
    "structural_indicators",
    "backtest",
    "contract_version",
}

REQUIRED_ITEM_FIELDS = {
    "item_id",
    "event_id",
    "signal_id",
    "primary_domain",
    "report_lane",
    "candidate_type",
    "formation_level",
    "headline",
    "first_seen_at",
    "today_delta",
    "importance_score",
    "potential_score",
    "confidence_score",
    "evidence_links",
    "direct_taiwan_evidence",
    "taiwan_implication",
    "counterevidence",
    "uncertainties",
    "next_watch",
}

LEGACY_REQUIRED_ITEM_FIELDS = {
    "item_id",
    "event_id",
    "signal_id",
    "primary_domain",
    "headline",
    "first_seen_at",
    "today_delta",
    "importance_score",
    "potential_score",
    "confidence_score",
    "evidence_links",
    "direct_taiwan_evidence",
    "taiwan_implication",
    "counterevidence",
    "uncertainties",
    "next_watch",
}


def validate_report_contract(report: dict[str, Any], contract: RuntimeContract | None = None) -> None:
    if contract is None:
        if "items" not in report or "coverage_gaps" not in report:
            raise ValueError("report requires items and coverage_gaps")
        for item in report["items"]:
            _validate_legacy_item(item)
        return

    missing_report_fields = REQUIRED_REPORT_FIELDS - set(report)
    if missing_report_fields:
        raise ValueError(f"report missing fields: {sorted(missing_report_fields)}")
    if report["status"] not in {"complete", "partial", "failed"}:
        raise ValueError("report status must be complete, partial or failed")
    if not isinstance(report["coverage_gaps"], list):
        raise ValueError("coverage_gaps must be a list")

    for item in report["items"]:
        _validate_item(item, contract=contract)
    _validate_contract_sections(report, contract)


def _validate_legacy_item(item: dict[str, Any]) -> None:
    missing = LEGACY_REQUIRED_ITEM_FIELDS - set(item)
    if missing:
        raise ValueError(f"report item missing fields: {sorted(missing)}")
    _validate_common_item_fields(item)


def _validate_item(item: dict[str, Any], contract: RuntimeContract) -> None:
    missing = REQUIRED_ITEM_FIELDS - set(item)
    if missing:
        raise ValueError(f"report item missing fields: {sorted(missing)}")
    if item["report_lane"] not in {"major", "potential"}:
        raise ValueError("report_lane must be major or potential")
    if item["primary_domain"] not in contract.report_domains:
        raise ValueError(f"unknown primary_domain: {item['primary_domain']}")
    if item["report_lane"] == "potential":
        if not item["candidate_type"] or not item["formation_level"]:
            raise ValueError(f"potential item lacks candidate metadata: {item['item_id']}")
    elif item["candidate_type"] is not None or item["formation_level"] is not None:
        raise ValueError(f"major item must not carry candidate metadata: {item['item_id']}")
    _validate_common_item_fields(item)


def _validate_common_item_fields(item: dict[str, Any]) -> None:
    for score_field in ("importance_score", "potential_score", "confidence_score"):
        score = item[score_field]
        if not isinstance(score, int) or not 0 <= score <= 100:
            raise ValueError(f"{score_field} must be 0-100")
    if not item["today_delta"]:
        raise ValueError(f"report item lacks today_delta: {item['item_id']}")
    if not item["evidence_links"]:
        raise ValueError(f"report item lacks evidence: {item['item_id']}")
    for link in item["evidence_links"]:
        _validate_evidence_link(link)
    for link in item["direct_taiwan_evidence"]:
        _validate_evidence_link(link)


def _validate_contract_sections(report: dict[str, Any], contract: RuntimeContract) -> None:
    if set(report["retail_matrix"]) != set(contract.retail_matrix_keys):
        raise ValueError("retail_matrix keys do not match runtime contract")
    if set(report["crypto_matrix"]) != set(contract.crypto_matrix_keys):
        raise ValueError("crypto_matrix keys do not match runtime contract")

    indicator_ids = {row.get("indicator_id") for row in report["structural_indicators"]}
    if indicator_ids != set(contract.structural_indicator_ids):
        raise ValueError("structural indicator ids do not match runtime contract")

    missing_counters = set(contract.required_backtest_counters) - set(report["rejection_counters"])
    if missing_counters:
        raise ValueError(f"rejection counters missing: {sorted(missing_counters)}")

    major_event_ids = {item["event_id"] for item in report["items"] if item["report_lane"] == "major"}
    potential_event_ids = {item["event_id"] for item in report["items"] if item["report_lane"] == "potential"}
    overlap = major_event_ids & potential_event_ids
    if overlap:
        raise ValueError(f"same event cannot fill major and potential lanes: {sorted(overlap)}")

    profile = contract.profile(report["profile"])
    if profile.major_slot_cap_per_domain is not None:
        _validate_slot_cap(report["items"], "major", profile.major_slot_cap_per_domain)
    if profile.potential_slot_cap_per_domain is not None:
        _validate_slot_cap(report["items"], "potential", profile.potential_slot_cap_per_domain)


def _validate_slot_cap(items: list[dict[str, Any]], lane: str, cap: int) -> None:
    counts: dict[str, int] = {}
    for item in items:
        if item["report_lane"] != lane:
            continue
        domain = item["primary_domain"]
        counts[domain] = counts.get(domain, 0) + 1
    exceeded = {domain: count for domain, count in counts.items() if count > cap}
    if exceeded:
        raise ValueError(f"{lane} slot cap exceeded: {exceeded}")


def _validate_evidence_link(link: dict[str, Any]) -> None:
    for key in ("url", "source_id", "fetched_at"):
        if not link.get(key):
            raise ValueError(f"evidence link missing {key}")
    parts = urlsplit(link["url"])
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError(f"invalid evidence URL: {link['url']}")
