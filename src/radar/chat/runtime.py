"""prepare-chat / import-chat runtime (file I/O around the pure package logic)."""

from __future__ import annotations

import json
from pathlib import Path

from radar.application import DailyRunRequest
from radar.chat.context_package import (
    ChatImportReceipt,
    ChatPackage,
    build_chat_package,
    load_chat_context,
    validate_chat_import,
)
from radar.composition import CompositionConfig, compose_application
from radar.contracts.report import RadarReportV2
from radar.contracts.runtime import RuntimeContract
from radar.domain.models import Event
from radar.repositories.sqlite import SqliteRunRepository


def _load_persisted_report_and_events(
    repo_root: Path,
    database_path: Path,
    *,
    date: str,
    profile: str,
) -> tuple[RadarReportV2, list[Event]]:
    """Load one validated report and its evidence-bearing events from durable state."""

    repository = SqliteRunRepository(database_path, repo_root / "migrations")
    report = repository.get_report_by_date(date, profile)
    if report is None:
        raise ValueError(f"no persisted report for date={date} profile={profile}")

    event_ids = sorted({item.event_id for item in report.items})
    events: list[Event] = []
    missing: list[str] = []
    for event_id in event_ids:
        event = repository.get_event(event_id)
        if event is None:
            missing.append(event_id)
        else:
            events.append(event)

    if missing:
        raise ValueError(
            "persisted report references events that are missing from durable state: "
            + ", ".join(missing)
        )
    return report, events


def prepare_chat(
    repo_root: Path,
    date: str,
    *,
    profile: str = "daily_push",
    output_root: Path | None = None,
    database_path: Path | None = None,
) -> ChatPackage:
    """Write a bounded, byte-stable package from durable state or fixture fallback.

    Production automation supplies ``database_path`` and packages the already
    validated report plus its persisted evidence-bearing events. Omitting the
    database preserves the deterministic fixture path used by local contract
    tests and does not claim live coverage.
    """

    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    if database_path is not None:
        report, events = _load_persisted_report_and_events(
            repo_root,
            database_path,
            date=date,
            profile=profile,
        )
    else:
        composed = compose_application(CompositionConfig(source_backend="fixture"))
        result = composed.application.run(
            DailyRunRequest(date=date, profile=profile, ingestion_mode="fixture", evaluation_mode="chat-assisted"),
            contract,
        )
        report = result.report
        events = list(result.events)

    package = build_chat_package(report, events, contract)
    root = output_root or repo_root
    target = root / package.relative_dir
    target.mkdir(parents=True, exist_ok=True)
    for name, content in package.files.items():
        (target / name).write_bytes(content)
    return package


def import_chat(
    repo_root: Path,
    package_dir: Path,
    submitted_report_path: Path,
    *,
    receipt_path: Path | None = None,
) -> ChatImportReceipt:
    """Validate a human-produced report against a written chat package.

    A failed import produces a validation receipt and does not overwrite the last
    valid report or the site.
    """

    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    files = {path.name: path.read_bytes() for path in package_dir.iterdir() if path.is_file()}
    context = load_chat_context(files)
    manifest = json.loads(files["manifest.json"].decode("utf-8"))
    submitted = json.loads(submitted_report_path.read_text(encoding="utf-8"))

    receipt = validate_chat_import(
        submitted,
        context,
        contract,
        claimed_context_hash=manifest["context_hash"],
        claimed_package_version=manifest["package_version"],
    )
    if receipt_path is not None:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return receipt
