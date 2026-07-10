from __future__ import annotations

from dataclasses import dataclass, field

from radar.domain.models import Document, Event, ReportItem


@dataclass
class InMemoryRepository:
    documents: list[Document] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    report_items: list[ReportItem] = field(default_factory=list)

    def add_documents(self, documents: list[Document]) -> None:
        self.documents.extend(documents)

    def add_events(self, events: list[Event]) -> None:
        self.events.extend(events)

    def add_report_items(self, items: list[ReportItem]) -> None:
        self.report_items.extend(items)
