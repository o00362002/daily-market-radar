from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from radar.contracts.report import RadarReportV2, StructuralIndicatorObservationV1
from radar.domain.event_resolution import EventMatchRecord
from radar.domain.models import Document, Event


@dataclass(frozen=True)
class RunPersistenceBatch:
    """Everything a single run must persist atomically.

    The application assembles this batch only after typed validation succeeds.
    A ``UnitOfWork`` implementation commits every element in one transaction and
    rolls the whole run back on any failure, so a partially written run can never
    overwrite the last valid report or corrupt event history.
    """

    report: RadarReportV2
    documents: tuple[Document, ...] = ()
    events: tuple[Event, ...] = ()
    indicator_observations: tuple[StructuralIndicatorObservationV1, ...] = ()
    state_entries: tuple[tuple[str, bytes], ...] = ()
    match_records: tuple[EventMatchRecord, ...] = ()
    observed_at: str = ""


@runtime_checkable
class UnitOfWork(Protocol):
    """Atomic run-transaction boundary (SQLite is the first implementation)."""

    def commit_run(self, batch: RunPersistenceBatch) -> None: ...
