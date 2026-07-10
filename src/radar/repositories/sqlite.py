from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


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

    def save_report(self, report: dict[str, Any]) -> None:
        self.initialize()
        run_id = report["run_id"]
        status = report["status"]
        with sqlite3.connect(self.database_path) as connection:
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
                values(?, ?, ?, datetime('now'))
                on conflict(report_id) do update set
                  run_id=excluded.run_id,
                  profile=excluded.profile,
                  rendered_at=excluded.rendered_at
                """,
                (f"report:{run_id}", run_id, report["profile"]),
            )
            connection.execute(
                """
                insert into report_payloads(report_id, run_id, payload_json)
                values(?, ?, ?)
                on conflict(report_id) do update set
                  run_id=excluded.run_id,
                  payload_json=excluded.payload_json
                """,
                (f"report:{run_id}", run_id, json.dumps(report, ensure_ascii=False, sort_keys=True)),
            )
            connection.execute("delete from coverage_gaps where run_id = ?", (run_id,))
            for index, gap in enumerate(report.get("coverage_gaps", [])):
                connection.execute(
                    """
                    insert into coverage_gaps(gap_id, run_id, gap_json)
                    values(?, ?, ?)
                    """,
                    (f"{run_id}:{index}", run_id, json.dumps(gap, ensure_ascii=False, sort_keys=True)),
                )
            connection.commit()

    def load_report(self, run_id: str) -> dict[str, Any] | None:
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "select payload_json from report_payloads where run_id = ? order by report_id limit 1",
                (run_id,),
            ).fetchone()
        return None if row is None else json.loads(row[0])
