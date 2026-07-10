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
from radar.contracts.runtime import RuntimeContract


def prepare_chat(
    repo_root: Path,
    date: str,
    *,
    profile: str = "daily_push",
    output_root: Path | None = None,
) -> ChatPackage:
    """Run a deterministic fixture evaluation and write a byte-stable chat package."""

    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    composed = compose_application(CompositionConfig(source_backend="fixture"))
    result = composed.application.run(
        DailyRunRequest(date=date, profile=profile, ingestion_mode="fixture", evaluation_mode="chat-assisted"),
        contract,
    )
    package = build_chat_package(result.report, list(result.events), contract)

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
