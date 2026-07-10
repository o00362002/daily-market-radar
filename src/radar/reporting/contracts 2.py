from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


REQUIRED_ITEM_FIELDS = {
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


def validate_report_contract(report: dict[str, Any]) -> None:
    if "items" not in report or "coverage_gaps" not in report:
        raise ValueError("report requires items and coverage_gaps")
    for item in report["items"]:
        missing = REQUIRED_ITEM_FIELDS - set(item)
        if missing:
            raise ValueError(f"report item missing fields: {sorted(missing)}")
        for score_field in ("importance_score", "potential_score", "confidence_score"):
            score = item[score_field]
            if not isinstance(score, int) or not 0 <= score <= 100:
                raise ValueError(f"{score_field} must be 0-100")
        if not item["evidence_links"]:
            raise ValueError(f"report item lacks evidence: {item['item_id']}")
        for link in item["evidence_links"]:
            _validate_evidence_link(link)
        for link in item["direct_taiwan_evidence"]:
            _validate_evidence_link(link)


def _validate_evidence_link(link: dict[str, Any]) -> None:
    for key in ("url", "source_id", "fetched_at"):
        if not link.get(key):
            raise ValueError(f"evidence link missing {key}")
    parts = urlsplit(link["url"])
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError(f"invalid evidence URL: {link['url']}")
