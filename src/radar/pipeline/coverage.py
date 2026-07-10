from __future__ import annotations

from radar.domain.models import CoverageCell


def audit_coverage(cells: list[CoverageCell]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for cell in cells:
        if cell.status in {"failing", "silent_zero", "empty", "stale", "policy_blocked"}:
            gaps.append(
                {
                    "domain": cell.domain,
                    "macro_region": cell.macro_region,
                    "language": cell.language,
                    "source_role": cell.source_role,
                    "channel": cell.channel,
                    "time_window": cell.time_window,
                    "reason": f"source_{cell.status}",
                    "message": f"{cell.domain}/{cell.macro_region}/{cell.language} coverage gap: {cell.status}",
                }
            )
    return gaps


def enforce_major_potential_split(major_event_ids: list[str], potential_event_ids: list[str]) -> None:
    overlap = set(major_event_ids) & set(potential_event_ids)
    if overlap:
        raise ValueError(f"same event cannot fill major and potential slots: {sorted(overlap)}")
