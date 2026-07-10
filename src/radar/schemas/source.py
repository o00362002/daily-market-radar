from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class SourceAdapterConfig:
    kind: str
    url: str
    enabled_for_opml: bool = False
    opml_category: str = ""
    route_status: str = ""


# Backward-compatible configuration DTO import. The behavior Protocol is
# intentionally namespaced as ``radar.ports.SourceAdapter``.
SourceAdapter = SourceAdapterConfig


@dataclass(frozen=True)
class Source:
    source_id: str
    name: str
    canonical_url: str
    publisher_country: str
    macro_region: str
    languages: list[str]
    source_roles: list[str]
    domains: list[str]
    ownership_profile: str
    evidence_profile: str
    priority: str
    adapters: list[SourceAdapterConfig]
    fetch_interval_minutes: int
    freshness_slo_minutes: int
    usage_policy: str
    fulltext_policy: str
    enabled: bool
    verification_status: str
    last_verified_at: str
    aliases: list[str]


class SourceRegistry:
    def __init__(self, sources: list[Source]) -> None:
        self.sources = sources

    @classmethod
    def from_file(cls, path: Path) -> "SourceRegistry":
        data = json.loads(path.read_text(encoding="utf-8"))
        sources = []
        for row in data["sources"]:
            adapters = [SourceAdapterConfig(**adapter) for adapter in row.get("adapters", [])]
            sources.append(Source(**{**row, "adapters": adapters}))
        return cls(sources)

    def get(self, source_id: str) -> Source:
        for source in self.sources:
            if source.source_id == source_id or source_id in source.aliases:
                return source
        raise KeyError(source_id)

    def validate(self) -> None:
        source_ids: set[str] = set()
        aliases: set[str] = set()
        canonical_urls: set[str] = set()
        for source in self.sources:
            required = [
                source.source_id,
                source.name,
                source.canonical_url,
                source.publisher_country,
                source.macro_region,
                source.languages,
                source.source_roles,
                source.domains,
                source.usage_policy,
                source.fulltext_policy,
                source.last_verified_at,
            ]
            if any(value in ("", [], None) for value in required):
                raise ValueError(f"source has missing required field: {source.source_id}")
            if source.source_id in source_ids:
                raise ValueError(f"duplicate source_id: {source.source_id}")
            source_ids.add(source.source_id)
            if source.canonical_url in canonical_urls:
                raise ValueError(f"duplicate canonical_url: {source.canonical_url}")
            canonical_urls.add(source.canonical_url)
            self._validate_url(source.canonical_url)
            for alias in source.aliases:
                if alias in aliases or alias in source_ids:
                    raise ValueError(f"duplicate alias: {alias}")
                aliases.add(alias)
            for adapter in source.adapters:
                self._validate_url(adapter.url)

    def to_opml(self) -> str:
        categories: dict[str, list[tuple[str, str]]] = {}
        for source in self.sources:
            if not source.enabled:
                continue
            for adapter in source.adapters:
                if adapter.kind != "rss" or not adapter.enabled_for_opml:
                    continue
                categories.setdefault(adapter.opml_category, []).append((source.name, adapter.url))

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<opml version="2.0">',
            "  <head>",
            "    <title>daily-market-radar feed stack seeds</title>",
            "  </head>",
            "  <body>",
        ]
        for category, feeds in categories.items():
            cat = html.escape(category, quote=True)
            lines.append(f'    <outline text="{cat}" title="{cat}">')
            for name, url in feeds:
                escaped_name = html.escape(name, quote=True)
                escaped_url = html.escape(url, quote=True)
                lines.append(
                    f'      <outline text="{escaped_name}" title="{escaped_name}" type="rss" xmlUrl="{escaped_url}"/>'
                )
            lines.append("    </outline>")
        lines.extend(["  </body>", "</opml>", ""])
        return "\n".join(lines)

    @staticmethod
    def _validate_url(url: str) -> None:
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError(f"invalid url: {url}")
