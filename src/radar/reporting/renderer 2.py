from __future__ import annotations

from radar.domain.models import ReportItem


def render_markdown(items: list[ReportItem], coverage_gaps: list[dict[str, str]]) -> str:
    lines = ["# Daily Push Brief", "", "## Items"]
    for item in items:
        lines.append(f"- {item.headline} ({item.event_id})")
    lines.extend(["", "## Coverage Gaps"])
    for gap in coverage_gaps:
        lines.append(f"- {gap.get('message', gap.get('reason', 'gap'))}")
    return "\n".join(lines) + "\n"
