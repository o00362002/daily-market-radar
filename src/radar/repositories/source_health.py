"""Durable source health repositories (SQLite + in-memory)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from radar.domain.source_health import SourceHealthRecord


class InMemorySourceHealthRepository:
    def __init__(self) -> None:
        self.records: dict[str, SourceHealthRecord] = {}

    def get(self, source_id: str) -> SourceHealthRecord | None:
        return self.records.get(source_id)

    def upsert(self, record: SourceHealthRecord) -> None:
        self.records[record.source_id] = record

    def list_all(self) -> list[SourceHealthRecord]:
        return sorted(self.records.values(), key=lambda record: record.source_id)


class SqliteSourceHealthRepository:
    def __init__(self, database_path: Path, migrations_dir: Path) -> None:
        self.database_path = database_path
        self.migrations_dir = migrations_dir

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            for migration in sorted(self.migrations_dir.glob("*.sql")):
                connection.executescript(migration.read_text(encoding="utf-8"))
            connection.commit()

    def get(self, source_id: str) -> SourceHealthRecord | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                select source_id, status, checked_at, last_success_at, last_item_at,
                       consecutive_failures, response_count, latency_ms, failure_reason, retry_at
                from source_health
                where source_id = ?
                limit 1
                """,
                (source_id,),
            ).fetchone()
        return None if row is None else _row_to_record(row)

    def upsert(self, record: SourceHealthRecord) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                insert into source_health(
                    source_id, status, checked_at, last_success_at, last_item_at,
                    consecutive_failures, response_count, latency_ms, failure_reason, retry_at)
                values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(source_id) do update set
                    status=excluded.status,
                    checked_at=excluded.checked_at,
                    last_success_at=excluded.last_success_at,
                    last_item_at=excluded.last_item_at,
                    consecutive_failures=excluded.consecutive_failures,
                    response_count=excluded.response_count,
                    latency_ms=excluded.latency_ms,
                    failure_reason=excluded.failure_reason,
                    retry_at=excluded.retry_at
                """,
                (
                    record.source_id,
                    record.status,
                    record.checked_at,
                    record.last_success_at,
                    record.last_item_at,
                    record.consecutive_failures,
                    record.response_count,
                    record.latency_ms,
                    record.failure_reason,
                    record.retry_at,
                ),
            )
            connection.commit()

    def list_all(self) -> list[SourceHealthRecord]:
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                select source_id, status, checked_at, last_success_at, last_item_at,
                       consecutive_failures, response_count, latency_ms, failure_reason, retry_at
                from source_health
                order by source_id asc
                """
            ).fetchall()
        return [_row_to_record(row) for row in rows]


def _row_to_record(row: tuple) -> SourceHealthRecord:
    return SourceHealthRecord(
        source_id=str(row[0]),
        status=str(row[1]),
        checked_at=str(row[2]),
        last_success_at=str(row[3]),
        last_item_at=str(row[4]),
        consecutive_failures=int(row[5]),
        response_count=int(row[6]),
        latency_ms=int(row[7]),
        failure_reason=str(row[8]),
        retry_at=str(row[9]),
    )
