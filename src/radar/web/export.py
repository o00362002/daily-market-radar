"""Atomic, incremental web artifact export.

Stage-then-replace: every changed artifact is written to a temporary file first;
only after all stages succeed are they atomically moved into place. If staging
fails, all temporaries are removed and no final artifact is touched — a failed
export never leaves half-written artifacts behind.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from radar.contracts.web import WebArtifactV1
from radar.web.projection import WEB_ROOT


@dataclass(frozen=True)
class ExportResult:
    out_dir: Path
    written: tuple[str, ...]
    skipped: tuple[str, ...]

    @property
    def manifest_path(self) -> Path:
        return self.out_dir / WEB_ROOT / "manifest.json"


def _existing_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_web_artifacts(
    artifacts: Sequence[WebArtifactV1],
    out_dir: Path,
    *,
    incremental: bool = True,
    _write: object = None,
) -> ExportResult:
    """Write artifacts atomically. ``_write`` is a test seam for fault injection."""

    write = _write or (lambda path, content: path.write_bytes(content))
    root = out_dir / WEB_ROOT

    to_write: list[tuple[Path, bytes]] = []
    skipped: list[str] = []
    for artifact in artifacts:
        target = root / artifact.path
        if incremental and _existing_hash(target) == artifact.content_hash:
            skipped.append(artifact.path)
            continue
        to_write.append((target, artifact.content))

    # Phase 1: stage every changed artifact to a temp file (rollback-safe).
    staged: list[tuple[Path, Path]] = []
    try:
        for target, content in to_write:
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(f".{target.name}.tmp")
            write(temp, content)
            staged.append((temp, target))
    except BaseException:
        for temp, _ in staged:
            temp.unlink(missing_ok=True)
        raise

    # Phase 2: atomically move each staged file into place.
    written: list[str] = []
    for temp, target in staged:
        os.replace(temp, target)
        written.append(str(target.relative_to(root)))

    return ExportResult(out_dir=out_dir, written=tuple(sorted(written)), skipped=tuple(sorted(skipped)))
