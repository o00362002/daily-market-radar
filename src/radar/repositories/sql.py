from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_SQL = """
create table if not exists documents (
  document_id text primary key,
  source_id text not null,
  url text not null,
  title text not null,
  published_at text not null,
  fetched_at text not null
);
create table if not exists events (
  event_id text primary key,
  first_seen_at text not null,
  last_seen_at text not null,
  status text not null
);
create table if not exists reports (
  report_id text primary key,
  run_id text not null,
  profile text not null,
  rendered_at text not null
);
"""


def connect_sqlite(path: Path | str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA_SQL)
    return connection
