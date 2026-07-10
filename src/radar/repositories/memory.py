from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from radar.contracts.report import RadarReportV2, StructuralIndicatorObservationV1
from radar.domain.models import Document, Event, EventDelta


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
