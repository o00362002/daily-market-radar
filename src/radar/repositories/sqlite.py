from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from radar.contracts.report import RadarReportV2


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
