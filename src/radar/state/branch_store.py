"""Durable state store for the ephemeral GitHub runner.

The SQLite database is compressed and checksummed, described by a state manifest,
and committed to a dedicated `radar-state` branch (never `main`). A last-good
backup is retained so a corrupt update can be rolled back. This module provides
the pure pack / verify / unpack / retention logic; the git side lives in the
`daily-intelligence` workflow with a concurrency lock.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

STATE_DIR = "state"
DB_ARTIFACT = "radar.db.gz"
MANIFEST_ARTIFACT = "manifest.json"
LAST_GOOD_DIR = "last-good"
MANIFEST_VERSION = "state/v1"


class StateCorruptionError(RuntimeError):
    pass


@dataclass(frozen=True)
class StateManifest:
    version: str
    db_filename: str
    compressed_sha256: str
    uncompressed_sha256: str
    uncompressed_size: int
    created_at: str
    run_id: str

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "db_filename": self.db_filename,
            "compressed_sha256": self.compressed_sha256,
            "uncompressed_sha256": self.uncompressed_sha256,
            "uncompressed_size": self.uncompressed_size,
            "created_at": self.created_at,
            "run_id": self.run_id,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "StateManifest":
        return cls(
            version=str(payload["version"]),
            db_filename=str(payload["db_filename"]),
            compressed_sha256=str(payload["compressed_sha256"]),
            uncompressed_sha256=str(payload["uncompressed_sha256"]),
            uncompressed_size=int(payload["uncompressed_size"]),
            created_at=str(payload["created_at"]),
            run_id=str(payload["run_id"]),
        )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pack_state(db_path: Path, *, run_id: str, created_at: str) -> tuple[bytes, StateManifest]:
    """Compress and checksum a SQLite database for durable storage."""

    raw = db_path.read_bytes()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)  # mtime=0 -> byte-stable
    manifest = StateManifest(
        version=MANIFEST_VERSION,
        db_filename=db_path.name,
        compressed_sha256=_sha256(compressed),
        uncompressed_sha256=_sha256(raw),
        uncompressed_size=len(raw),
        created_at=created_at,
        run_id=run_id,
    )
    return compressed, manifest


def verify_state(compressed: bytes, manifest: StateManifest) -> None:
    """Raise StateCorruptionError if the compressed blob does not match the manifest."""

    if _sha256(compressed) != manifest.compressed_sha256:
        raise StateCorruptionError("compressed checksum mismatch")
    try:
        raw = gzip.decompress(compressed)
    except OSError as exc:  # corrupt gzip stream
        raise StateCorruptionError(f"gzip decompression failed: {exc}") from exc
    if _sha256(raw) != manifest.uncompressed_sha256:
        raise StateCorruptionError("uncompressed checksum mismatch")
    if len(raw) != manifest.uncompressed_size:
        raise StateCorruptionError("uncompressed size mismatch")


def unpack_state(compressed: bytes, manifest: StateManifest, dest_path: Path) -> None:
    """Verify then atomically write the database to ``dest_path``."""

    verify_state(compressed, manifest)
    raw = gzip.decompress(compressed)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp = dest_path.with_name(f".{dest_path.name}.tmp")
    temp.write_bytes(raw)
    temp.replace(dest_path)


def write_state_tree(state_root: Path, compressed: bytes, manifest: StateManifest, *, retain: int = 3) -> list[str]:
    """Write the current state + rotate the last-good backup on the state branch.

    Before overwriting, the existing valid state is moved into last-good/ and old
    backups beyond ``retain`` are pruned. Returns the list of written paths.
    """

    state_root.mkdir(parents=True, exist_ok=True)
    current_db = state_root / DB_ARTIFACT
    current_manifest = state_root / MANIFEST_ARTIFACT
    backups = state_root / LAST_GOOD_DIR
    written: list[str] = []

    # Rotate the currently committed state into last-good before overwriting.
    if current_db.exists() and current_manifest.exists():
        try:
            existing = StateManifest.from_dict(json.loads(current_manifest.read_text(encoding="utf-8")))
            verify_state(current_db.read_bytes(), existing)
            backups.mkdir(parents=True, exist_ok=True)
            (backups / f"{existing.run_id}.db.gz").write_bytes(current_db.read_bytes())
            (backups / f"{existing.run_id}.manifest.json").write_text(
                json.dumps(existing.to_dict(), ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8"
            )
        except (StateCorruptionError, KeyError, ValueError):
            pass  # do not back up a corrupt current state

    current_db.write_bytes(compressed)
    current_manifest.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8"
    )
    written.extend([f"{STATE_DIR}/{DB_ARTIFACT}", f"{STATE_DIR}/{MANIFEST_ARTIFACT}"])

    _prune_backups(backups, retain=retain)
    return written


def _prune_backups(backups: Path, *, retain: int) -> None:
    if not backups.exists():
        return
    manifests = sorted(backups.glob("*.manifest.json"), key=lambda path: path.read_text(encoding="utf-8"))
    # Order by created_at inside the manifest, newest last.
    manifests = sorted(
        backups.glob("*.manifest.json"),
        key=lambda path: json.loads(path.read_text(encoding="utf-8")).get("created_at", ""),
    )
    excess = manifests[:-retain] if retain > 0 else manifests
    for manifest_path in excess:
        run_id = json.loads(manifest_path.read_text(encoding="utf-8")).get("run_id", "")
        manifest_path.unlink(missing_ok=True)
        (backups / f"{run_id}.db.gz").unlink(missing_ok=True)


def restore_last_good(state_root: Path, dest_path: Path) -> StateManifest | None:
    """Restore the newest valid last-good backup (corruption rollback)."""

    backups = state_root / LAST_GOOD_DIR
    if not backups.exists():
        return None
    manifests = sorted(
        backups.glob("*.manifest.json"),
        key=lambda path: json.loads(path.read_text(encoding="utf-8")).get("created_at", ""),
        reverse=True,
    )
    for manifest_path in manifests:
        manifest = StateManifest.from_dict(json.loads(manifest_path.read_text(encoding="utf-8")))
        blob = (backups / f"{manifest.run_id}.db.gz").read_bytes()
        try:
            unpack_state(blob, manifest, dest_path)
            return manifest
        except StateCorruptionError:
            continue
    return None
