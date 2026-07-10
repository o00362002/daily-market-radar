from __future__ import annotations

import copy
from collections import defaultdict
from dataclasses import replace
from typing import TYPE_CHECKING

from radar.contracts.report import RadarReportV2, StructuralIndicatorObservationV1
from radar.domain.models import Document, Event, EventDelta

if TYPE_CHECKING:
    from radar.ports.persistence import RunPersistenceBatch


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}

    def save_documents(self, documents: list[Document]) -> None:
        self.documents.update({document.document_id: document for document in documents})

    def get_document(self, document_id: str) -> Document | None:
        return self.documents.get(document_id)

    def find_by_canonical_url(self, canonical_url: str) -> Document | None:
        return next((document for document in self.documents.values() if document.url == canonical_url), None)

    def find_by_content_hash(self, content_hash: str) -> Document | None:
        return next((document for document in self.documents.values() if document.content_hash == content_hash), None)

    def list_recent_documents(self, since: str) -> list[Document]:
        return sorted(
            (document for document in self.documents.values() if document.fetched_at >= since),
            key=lambda document: (document.fetched_at, document.document_id),
        )


class InMemoryEventRepository:
    def __init__(self) -> None:
        self.events: dict[str, Event] = {}
        self.event_documents: dict[str, list[str]] = defaultdict(list)
        self.event_deltas: dict[str, list[EventDelta]] = defaultdict(list)

    def save_event(self, event: Event) -> None:
        self.events[event.event_id] = event

    def get_event(self, event_id: str) -> Event | None:
        return self.events.get(event_id)

    def find_recent_events(self, since: str) -> list[Event]:
        return sorted(
            (event for event in self.events.values() if event.last_seen_at >= since),
            key=lambda event: (event.last_seen_at, event.event_id),
        )

    def attach_documents(self, event_id: str, document_ids: list[str]) -> None:
        known = self.event_documents[event_id]
        known.extend(document_id for document_id in document_ids if document_id not in known)

    def save_event_delta(self, event_id: str, delta: EventDelta, observed_at: str) -> None:
        del observed_at
        self.event_deltas[event_id].append(delta)

    def list_event_deltas(self, event_id: str) -> list[EventDelta]:
        return list(self.event_deltas.get(event_id, []))

    def update_last_seen(self, event_id: str, last_seen_at: str) -> None:
        event = self.events[event_id]
        self.events[event_id] = replace(event, last_seen_at=last_seen_at)

    def list_active_events(self) -> list[Event]:
        return sorted(
            (event for event in self.events.values() if event.status == "active"),
            key=lambda event: event.event_id,
        )


class InMemoryReportRepository:
    def __init__(self) -> None:
        self.reports: dict[str, RadarReportV2] = {}
        self._save_order: list[str] = []

    def save_report(self, report: RadarReportV2) -> None:
        if report.report_id in self._save_order:
            self._save_order.remove(report.report_id)
        self._save_order.append(report.report_id)
        self.reports[report.report_id] = report

    def get_report(self, report_id: str) -> RadarReportV2 | None:
        return self.reports.get(report_id)

    def get_report_by_date(self, report_date: str, profile: str) -> RadarReportV2 | None:
        matches = [report for report in self.list_reports(profile) if report.date == report_date]
        return matches[-1] if matches else None

    def get_latest_report(self, profile: str | None = None) -> RadarReportV2 | None:
        reports = self.list_reports(profile)
        return reports[-1] if reports else None

    def list_reports(self, profile: str | None = None) -> list[RadarReportV2]:
        return [
            self.reports[report_id]
            for report_id in self._save_order
            if profile is None or self.reports[report_id].profile == profile
        ]


class InMemoryIndicatorRepository:
    def __init__(self) -> None:
        self.observations: dict[str, list[StructuralIndicatorObservationV1]] = defaultdict(list)

    def save_indicator_observation(self, observation: StructuralIndicatorObservationV1) -> None:
        self.observations[observation.indicator_id].append(observation)

    def list_indicator_observations(self, indicator_id: str) -> list[StructuralIndicatorObservationV1]:
        return sorted(
            self.observations.get(indicator_id, []),
            key=lambda observation: observation.observation_date,
        )

    def get_rolling_window(self, indicator_id: str, days: int) -> list[StructuralIndicatorObservationV1]:
        if days <= 0:
            raise ValueError("days must be positive")
        return self.list_indicator_observations(indicator_id)[-days:]


class InMemoryUnitOfWork:
    """Atomic run-transaction boundary for the in-memory backend.

    Delegates every write to the injected repositories and snapshots their state
    first, so a failure mid-commit restores the prior state and never leaves a
    partially written run behind.
    """

    def __init__(
        self,
        *,
        document_repository: InMemoryDocumentRepository,
        event_repository: InMemoryEventRepository,
        report_repository: InMemoryReportRepository,
        indicator_repository: InMemoryIndicatorRepository,
        state_store: object,
    ) -> None:
        self._document_repository = document_repository
        self._event_repository = event_repository
        self._report_repository = report_repository
        self._indicator_repository = indicator_repository
        self._state_store = state_store

    def commit_run(self, batch: "RunPersistenceBatch") -> None:
        snapshot = self._snapshot()
        try:
            self._document_repository.save_documents(list(batch.documents))
            for event in batch.events:
                self._event_repository.save_event(event)
                self._event_repository.attach_documents(
                    event.event_id, [document.document_id for document in event.documents]
                )
                for delta in event.deltas:
                    self._event_repository.save_event_delta(event.event_id, delta, batch.observed_at)
            self._report_repository.save_report(batch.report)
            for observation in batch.indicator_observations:
                self._indicator_repository.save_indicator_observation(observation)
            for key, value in batch.state_entries:
                self._state_store.save(key, value)
        except BaseException:
            self._restore(snapshot)
            raise

    def _snapshot(self) -> tuple:
        return copy.deepcopy(
            (
                self._document_repository.documents,
                self._event_repository.events,
                dict(self._event_repository.event_documents),
                dict(self._event_repository.event_deltas),
                self._report_repository.reports,
                list(self._report_repository._save_order),
                dict(self._indicator_repository.observations),
                getattr(self._state_store, "values", {}),
            )
        )

    def _restore(self, snapshot: tuple) -> None:
        (
            documents,
            events,
            event_documents,
            event_deltas,
            reports,
            save_order,
            observations,
            state_values,
        ) = snapshot
        self._document_repository.documents = documents
        self._event_repository.events = events
        self._event_repository.event_documents = defaultdict(list, event_documents)
        self._event_repository.event_deltas = defaultdict(list, event_deltas)
        self._report_repository.reports = reports
        self._report_repository._save_order = save_order
        self._indicator_repository.observations = defaultdict(list, observations)
        if hasattr(self._state_store, "values"):
            self._state_store.values = state_values
