from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from radar.contracts.report import RadarReportV2, StructuralIndicatorObservationV1
from radar.domain.models import CanonicalFacts, Document, Event, EventDelta


class SqliteRunRepository:
    def __init__(self, database_path: Path, migrations_dir: Path) -> None:
        self.database_path = database_path
        self.migrations_dir = migrations_dir

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            for migration in sorted(self.migrations_dir.glob("*.sql")):
                connection.executescript(migration.read_text(encoding="utf-8"))
            connection.commit()

    def save_documents(self, documents: list[Document]) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            for document in documents:
                self._upsert_document(connection, document)
            connection.commit()

    def get_document(self, document_id: str) -> Document | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            return self._get_document(connection, document_id)

    def find_by_canonical_url(self, canonical_url: str) -> Document | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                select document_id
                from document_payloads
                where canonical_url = ?
                order by fetched_at desc, document_id desc
                limit 1
                """,
                (canonical_url,),
            ).fetchone()
            if row is not None:
                return self._get_document(connection, row[0])
            row = connection.execute(
                """
                select document_id
                from documents
                where url = ?
                order by fetched_at desc, document_id desc
                limit 1
                """,
                (canonical_url,),
            ).fetchone()
            return None if row is None else self._get_document(connection, row[0])

    def find_by_content_hash(self, content_hash: str) -> Document | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                select document_id
                from document_payloads
                where content_hash = ?
                order by fetched_at desc, document_id desc
                limit 1
                """,
                (content_hash,),
            ).fetchone()
            return None if row is None else self._get_document(connection, row[0])

    def list_recent_documents(self, since: str) -> list[Document]:
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                select document_id
                from document_payloads
                where fetched_at >= ?
                order by fetched_at asc, document_id asc
                """,
                (since,),
            ).fetchall()
            return [document for row in rows if (document := self._get_document(connection, row[0])) is not None]

    def save_event(self, event: Event) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            self._upsert_event(connection, event)
            for document in event.documents:
                self._upsert_document(connection, document)
                self._attach_document(connection, event.event_id, document.document_id)
            connection.commit()

    def get_event(self, event_id: str) -> Event | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            return self._get_event(connection, event_id)

    def find_recent_events(self, since: str) -> list[Event]:
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                select event_id
                from events
                where last_seen_at >= ?
                order by last_seen_at asc, event_id asc
                """,
                (since,),
            ).fetchall()
            return [event for row in rows if (event := self._get_event(connection, row[0])) is not None]

    def attach_documents(self, event_id: str, document_ids: list[str]) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            for document_id in document_ids:
                self._attach_document(connection, event_id, document_id)
            connection.commit()

    def save_event_delta(self, event_id: str, delta: EventDelta, observed_at: str) -> None:
        self.initialize()
        payload = _event_delta_to_payload(delta)
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        delta_id = "delta:" + hashlib.sha256(f"{event_id}|{observed_at}|{serialized}".encode("utf-8")).hexdigest()[:16]
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                insert into event_deltas(delta_id, event_id, observed_at, delta_json)
                values(?, ?, ?, ?)
                on conflict(delta_id) do update set
                  observed_at=excluded.observed_at,
                  delta_json=excluded.delta_json
                """,
                (delta_id, event_id, observed_at, serialized),
            )
            connection.commit()

    def list_event_deltas(self, event_id: str) -> list[EventDelta]:
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            return self._list_event_deltas(connection, event_id)

    def update_last_seen(self, event_id: str, last_seen_at: str) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                update events
                set last_seen_at = ?
                where event_id = ?
                """,
                (last_seen_at, event_id),
            )
            connection.commit()

    def list_active_events(self) -> list[Event]:
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                select event_id
                from events
                where status = 'active'
                order by event_id asc
                """
            ).fetchall()
            return [event for row in rows if (event := self._get_event(connection, row[0])) is not None]

    def save_report(self, report: RadarReportV2 | dict[str, Any]) -> None:
        typed_report = report if isinstance(report, RadarReportV2) else RadarReportV2.from_payload(report)
        payload = typed_report.model_dump(mode="json") if isinstance(report, RadarReportV2) else report
        self.initialize()
        run_id = typed_report.run_id
        status = typed_report.status
        with sqlite3.connect(self.database_path) as connection:
            rendered_at = self._next_rendered_at(connection)
            connection.execute(
                """
                insert into fetch_runs(run_id, started_at, finished_at, status)
                values(?, datetime('now'), datetime('now'), ?)
                on conflict(run_id) do update set
                  finished_at=excluded.finished_at,
                  status=excluded.status
                """,
                (run_id, status),
            )
            connection.execute(
                """
                insert into reports(report_id, run_id, profile, rendered_at)
                values(?, ?, ?, ?)
                on conflict(report_id) do update set
                  run_id=excluded.run_id,
                  profile=excluded.profile,
                  rendered_at=excluded.rendered_at
                """,
                (f"report:{run_id}", run_id, typed_report.profile, rendered_at),
            )
            connection.execute(
                """
                insert into report_payloads(report_id, run_id, payload_json)
                values(?, ?, ?)
                on conflict(report_id) do update set
                  run_id=excluded.run_id,
                  payload_json=excluded.payload_json
                """,
                (f"report:{run_id}", run_id, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
            )
            connection.execute("delete from coverage_gaps where run_id = ?", (run_id,))
            for index, gap in enumerate(payload.get("coverage_gaps", [])):
                connection.execute(
                    """
                    insert into coverage_gaps(gap_id, run_id, gap_json)
                    values(?, ?, ?)
                    """,
                    (f"{run_id}:{index}", run_id, json.dumps(gap, ensure_ascii=False, sort_keys=True)),
                )
            connection.commit()

    @staticmethod
    def _next_rendered_at(connection: sqlite3.Connection) -> str:
        candidate = datetime.now(timezone.utc)
        row = connection.execute("select max(rendered_at) from reports").fetchone()
        if row and row[0]:
            previous = datetime.fromisoformat(str(row[0]).replace(" ", "T").replace("Z", "+00:00"))
            if previous.tzinfo is None:
                previous = previous.replace(tzinfo=timezone.utc)
            if candidate <= previous:
                candidate = previous + timedelta(microseconds=1)
        return candidate.isoformat(timespec="microseconds")

    def load_report(self, run_id: str) -> dict[str, Any] | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "select payload_json from report_payloads where run_id = ? order by report_id limit 1",
                (run_id,),
            ).fetchone()
        return None if row is None else json.loads(row[0])

    def get_report(self, report_id: str) -> RadarReportV2 | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "select payload_json from report_payloads where report_id = ? limit 1",
                (report_id,),
            ).fetchone()
        return None if row is None else RadarReportV2.from_payload(json.loads(row[0]))

    def get_report_by_date(self, report_date: str, profile: str) -> RadarReportV2 | None:
        matches = [
            report
            for report in self.list_reports(profile)
            if report.date == report_date
        ]
        return matches[-1] if matches else None

    def get_latest_report(self, profile: str | None = None) -> RadarReportV2 | None:
        reports = self.list_reports(profile)
        return reports[-1] if reports else None

    def list_reports(self, profile: str | None = None) -> list[RadarReportV2]:
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                select rp.payload_json
                from report_payloads rp
                join reports r on r.report_id = rp.report_id
                order by r.rendered_at asc, r.rowid asc
                """
            ).fetchall()
        reports = [RadarReportV2.from_payload(json.loads(row[0])) for row in rows]
        return [report for report in reports if profile is None or report.profile == profile]

    def save_indicator_observation(self, observation: StructuralIndicatorObservationV1) -> None:
        self.initialize()
        payload = observation.model_dump(mode="json")
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                insert into indicator_observations(indicator_id, observation_date, payload_json)
                values(?, ?, ?)
                on conflict(indicator_id, observation_date) do update set
                  payload_json=excluded.payload_json
                """,
                (
                    observation.indicator_id,
                    observation.observation_date,
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                ),
            )
            connection.commit()

    def list_indicator_observations(self, indicator_id: str) -> list[StructuralIndicatorObservationV1]:
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                select payload_json
                from indicator_observations
                where indicator_id = ?
                order by observation_date asc
                """,
                (indicator_id,),
            ).fetchall()
        return [StructuralIndicatorObservationV1.model_validate(json.loads(row[0])) for row in rows]

    def get_rolling_window(self, indicator_id: str, days: int) -> list[StructuralIndicatorObservationV1]:
        if days <= 0:
            raise ValueError("days must be positive")
        return self.list_indicator_observations(indicator_id)[-days:]

    def load(self, key: str) -> bytes | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "select value_blob from state_entries where state_key = ? limit 1",
                (key,),
            ).fetchone()
        return None if row is None else bytes(row[0])

    def save(self, key: str, value: bytes) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                insert into state_entries(state_key, value_blob, updated_at)
                values(?, ?, ?)
                on conflict(state_key) do update set
                  value_blob=excluded.value_blob,
                  updated_at=excluded.updated_at
                """,
                (key, sqlite3.Binary(bytes(value)), datetime.now(timezone.utc).isoformat(timespec="microseconds")),
            )
            connection.commit()

    def _upsert_document(self, connection: sqlite3.Connection, document: Document) -> None:
        payload = _document_to_payload(document)
        connection.execute(
            """
            insert into documents(document_id, source_id, url, title, published_at, fetched_at)
            values(?, ?, ?, ?, ?, ?)
            on conflict(document_id) do update set
              source_id=excluded.source_id,
              url=excluded.url,
              title=excluded.title,
              published_at=excluded.published_at,
              fetched_at=excluded.fetched_at
            """,
            (
                document.document_id,
                document.source_id,
                document.url,
                document.title,
                document.published_at,
                document.fetched_at,
            ),
        )
        connection.execute(
            """
            insert into document_payloads(document_id, canonical_url, content_hash, fetched_at, payload_json)
            values(?, ?, ?, ?, ?)
            on conflict(document_id) do update set
              canonical_url=excluded.canonical_url,
              content_hash=excluded.content_hash,
              fetched_at=excluded.fetched_at,
              payload_json=excluded.payload_json
            """,
            (
                document.document_id,
                document.url,
                document.content_hash,
                document.fetched_at,
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
            ),
        )

    def _get_document(self, connection: sqlite3.Connection, document_id: str) -> Document | None:
        payload_row = connection.execute(
            "select payload_json from document_payloads where document_id = ? limit 1",
            (document_id,),
        ).fetchone()
        if payload_row is not None:
            return _document_from_payload(json.loads(payload_row[0]))
        row = connection.execute(
            """
            select document_id, source_id, url, title, published_at, fetched_at
            from documents
            where document_id = ?
            limit 1
            """,
            (document_id,),
        ).fetchone()
        if row is None:
            return None
        return Document(
            document_id=row[0],
            source_id=row[1],
            url=row[2],
            title=row[3],
            language="unknown",
            macro_region="Global",
            published_at=row[4],
            fetched_at=row[5],
        )

    def _upsert_event(self, connection: sqlite3.Connection, event: Event) -> None:
        connection.execute(
            """
            insert into events(event_id, first_seen_at, last_seen_at, last_material_delta_at, status)
            values(?, ?, ?, ?, ?)
            on conflict(event_id) do update set
              first_seen_at=excluded.first_seen_at,
              last_seen_at=excluded.last_seen_at,
              last_material_delta_at=excluded.last_material_delta_at,
              status=excluded.status
            """,
            (
                event.event_id,
                event.first_seen_at,
                event.last_seen_at,
                event.last_material_delta_at,
                event.status,
            ),
        )

    def _get_event(self, connection: sqlite3.Connection, event_id: str) -> Event | None:
        row = connection.execute(
            """
            select event_id, first_seen_at, last_seen_at, last_material_delta_at, status
            from events
            where event_id = ?
            limit 1
            """,
            (event_id,),
        ).fetchone()
        if row is None:
            return None
        doc_rows = connection.execute(
            """
            select document_id
            from event_documents
            where event_id = ?
            order by document_id asc
            """,
            (event_id,),
        ).fetchall()
        documents = [document for doc_row in doc_rows if (document := self._get_document(connection, doc_row[0]))]
        documents.sort(key=lambda document: (document.published_at, document.document_id))
        return Event(
            event_id=row[0],
            documents=documents,
            first_seen_at=row[1],
            last_seen_at=row[2],
            last_material_delta_at=row[3],
            status=row[4],
            deltas=self._list_event_deltas(connection, event_id),
        )

    def _attach_document(self, connection: sqlite3.Connection, event_id: str, document_id: str) -> None:
        connection.execute(
            """
            insert or ignore into event_documents(event_id, document_id)
            values(?, ?)
            """,
            (event_id, document_id),
        )

    def _list_event_deltas(self, connection: sqlite3.Connection, event_id: str) -> list[EventDelta]:
        rows = connection.execute(
            """
            select delta_json
            from event_deltas
            where event_id = ?
            order by observed_at asc, delta_id asc
            """,
            (event_id,),
        ).fetchall()
        return [_event_delta_from_payload(json.loads(row[0])) for row in rows]


def _facts_to_payload(facts: CanonicalFacts) -> dict[str, object]:
    payload: dict[str, object] = {}
    if facts.source_roles:
        payload["source_roles"] = list(facts.source_roles)
    for measurement in facts.measurements:
        payload[measurement.metric_id] = measurement.value
    return payload


def _document_to_payload(document: Document) -> dict[str, object]:
    return {
        "document_id": document.document_id,
        "source_id": document.source_id,
        "url": document.url,
        "title": document.title,
        "language": document.language,
        "macro_region": document.macro_region,
        "published_at": document.published_at,
        "fetched_at": document.fetched_at,
        "entities": list(document.entities),
        "action": document.action,
        "object": document.object,
        "location": document.location,
        "primary_domain": document.primary_domain,
        "lane": document.lane,
        "facts": _facts_to_payload(document.facts),
        "summary": document.summary,
    }


def _document_from_payload(payload: dict[str, Any]) -> Document:
    return Document(
        document_id=str(payload["document_id"]),
        source_id=str(payload["source_id"]),
        url=str(payload["url"]),
        title=str(payload["title"]),
        language=str(payload.get("language", "unknown")),
        macro_region=str(payload.get("macro_region", "Global")),
        published_at=str(payload["published_at"]),
        fetched_at=str(payload["fetched_at"]),
        entities=list(payload.get("entities", [])),
        action=str(payload.get("action", "")),
        object=str(payload.get("object", "")),
        location=str(payload.get("location", "")),
        primary_domain=str(payload.get("primary_domain", "ai_agents_applications")),
        lane=str(payload.get("lane", "top_down")),
        facts=dict(payload.get("facts", {})),
        summary=str(payload.get("summary", "")),
    )


def _event_delta_to_payload(delta: EventDelta) -> dict[str, object]:
    return {
        "delta_type": delta.delta_type,
        "changed_fields": list(delta.changed_fields),
        "reason": delta.reason,
    }


def _event_delta_from_payload(payload: dict[str, Any]) -> EventDelta:
    return EventDelta(
        delta_type=str(payload["delta_type"]),
        changed_fields=list(payload.get("changed_fields", [])),
        reason=str(payload.get("reason", "")),
    )
