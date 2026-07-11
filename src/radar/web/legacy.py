"""Legacy markdown report projection.

The repo carries pre-dashboard, human/chat-authored daily reports under
``reports/<year>/``. This module projects them onto the site as an *archive* —
byte-identical markdown artifacts plus a typed index — without ever faking
RadarReportV2 data (no synthetic statuses, counts or evaluation modes).
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict

from radar.contracts.web import WebArtifactV1
from radar.contracts.web_projection import (
    LegacyReportEntryV1,
    LegacyReportIndexV1,
    canonical_json_bytes,
)

# reports/2026/2026-07-11.md or reports/2026/2026-06-29-gemini-backtest.md
_DATED_STEM = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-(.+))?$")
# reports/2026/06/11.md  (year from the directory, month/day from the path)
_NESTED = re.compile(r"^(\d{4})/(\d{2})/(\d{2})$")
_SKIP_STEMS = {"readme", "index"}


def _title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def project_legacy(files: list[tuple[str, str]]) -> list[WebArtifactV1]:
    """Project (repo-relative path, markdown text) pairs into web artifacts.

    Emits ``legacy/<year>/<slug>.md`` (byte-identical content) per report plus
    ``indexes/legacy/<year>.json``. Duplicate-date variants are kept as separate
    honest entries; README/INDEX files are skipped.
    """

    entries_by_year: dict[str, list[LegacyReportEntryV1]] = defaultdict(list)
    artifacts: list[WebArtifactV1] = []

    for relative_path, text in sorted(files):
        normalized = relative_path.replace("\\", "/")
        stem_path = re.sub(r"^reports/", "", normalized)
        stem_path = re.sub(r"\.md$", "", stem_path)
        parts = stem_path.split("/")
        stem = parts[-1].lower()
        if stem in _SKIP_STEMS:
            continue

        date = ""
        variant = ""
        nested = _NESTED.match(stem_path)
        dated = _DATED_STEM.match(parts[-1])
        if nested:
            date = f"{nested.group(1)}-{nested.group(2)}-{nested.group(3)}"
        elif dated:
            date = dated.group(1)
            variant = dated.group(2) or ""
        else:
            continue  # not a dated report file

        year = date[:4]
        slug = f"{date}-{variant}" if variant else date
        content = text.encode("utf-8")
        markdown_path = f"legacy/{year}/{slug}.md"
        artifacts.append(
            WebArtifactV1(
                path=markdown_path,
                media_type="text/markdown; charset=utf-8",
                content_hash=hashlib.sha256(content).hexdigest(),
                content=content,
            )
        )
        entries_by_year[year].append(
            LegacyReportEntryV1(
                date=date,
                slug=slug,
                title=_title_of(text, slug),
                variant=variant,
                source_path=normalized,
                markdown_path=markdown_path,
                content_hash=hashlib.sha256(content).hexdigest(),
            )
        )

    for year, entries in sorted(entries_by_year.items()):
        index = LegacyReportIndexV1(
            year=year,
            entries=sorted(entries, key=lambda entry: (entry.date, entry.slug)),
        )
        content = canonical_json_bytes(index)
        artifacts.append(
            WebArtifactV1(
                path=f"indexes/legacy/{year}.json",
                media_type="application/json",
                content_hash=hashlib.sha256(content).hexdigest(),
                content=content,
            )
        )

    artifacts.sort(key=lambda artifact: artifact.path)
    return artifacts
