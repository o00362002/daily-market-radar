from __future__ import annotations

from radar.domain.models import ReportItem


def verify_evidence_trace(items: list[ReportItem]) -> None:
    for item in items:
        if not item.evidence_links:
            raise ValueError(f"report item lacks evidence: {item.item_id}")
        for link in item.evidence_links:
            if not link.url.startswith(("http://", "https://")) or not link.fetched_at:
                raise ValueError(f"invalid evidence link on {item.item_id}")
