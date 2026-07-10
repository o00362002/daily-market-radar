"""GDELT discovery adapter — discovery only, never final evidence.

GDELT is used to discover coverage gaps, regions, languages and related events.
Every entry must resolve back to the original publisher and URL and carry a
verification status; it is never emitted as final evidence on its own.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode, urlsplit

from radar.adapters.base import AdapterError
from radar.adapters.transport import HttpRequest, HttpTransport

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


@dataclass(frozen=True)
class DiscoveryEntry:
    original_publisher: str
    original_url: str
    registry_source_id: str
    verification_status: str
    language: str
    macro_region: str
    title: str

    @property
    def is_final_evidence(self) -> bool:
        return False


class GdeltDiscoveryAdapter:
    adapter_id = "gdelt_discovery"

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def discover(self, query: str, *, max_records: int = 25, known_domains: dict[str, str] | None = None) -> list[DiscoveryEntry]:
        known = known_domains or {}
        params = {"query": query, "mode": "artlist", "format": "json", "maxrecords": str(max_records)}
        url = f"{GDELT_DOC_API}?{urlencode(params)}"
        response = self._transport.fetch(HttpRequest(url=url))
        if response.content_type and "json" not in response.content_type:
            raise AdapterError(f"gdelt returned non-json: {response.content_type}")
        payload = json.loads(response.body.decode("utf-8") or "{}")
        entries: list[DiscoveryEntry] = []
        for article in payload.get("articles", []):
            original_url = str(article.get("url", "")).strip()
            if not original_url:
                continue
            domain = str(article.get("domain") or urlsplit(original_url).netloc).lower()
            registry_source_id = known.get(domain, "")
            entries.append(
                DiscoveryEntry(
                    original_publisher=domain,
                    original_url=original_url,
                    registry_source_id=registry_source_id or f"temporary:{domain}",
                    verification_status="registry_mapped" if registry_source_id else "unverified_discovery",
                    language=str(article.get("language", "")),
                    macro_region=str(article.get("sourcecountry", "")),
                    title=str(article.get("title", "")).strip(),
                )
            )
        return entries
