from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from radar.contracts.report import CompetitorAuditV1


@dataclass(frozen=True)
class CompetitorMonitorResult:
    audit: CompetitorAuditV1
    state_key: str
    state_value: bytes


@runtime_checkable
class CompetitorMonitor(Protocol):
    def run(self, report_date: str, checked_at: str) -> CompetitorMonitorResult: ...
