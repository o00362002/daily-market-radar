"""FreshRSS Google Reader API adapter.

Credential-gated. When FRESHRSS_BASE_URL / FRESHRSS_USERNAME / FRESHRSS_API_PASSWORD
are absent the adapter reports itself unavailable and the deterministic pipeline
continues with a coverage gap — it never raises.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from radar.adapters.base import AdapterError
from radar.adapters.transport import HttpRequest, HttpTransport
from radar.ports.sources import CredentialsStatusV1

_ENV_KEYS = ("FRESHRSS_BASE_URL", "FRESHRSS_USERNAME", "FRESHRSS_API_PASSWORD")


@dataclass(frozen=True)
class FreshRssItem:
    item_id: str
    title: str
    url: str
    published_at: str
    origin_stream_id: str


class FreshRssAdapter:
    adapter_id = "freshrss_google_reader"
    source_id = "freshrss_collection"

    def __init__(
        self,
        transport: HttpTransport,
        *,
        env: Callable[[str], str | None],
    ) -> None:
        self._transport = transport
        self._env = env
        self._auth_token: str | None = None

    def credentials_status(self) -> CredentialsStatusV1:
        missing = [key for key in _ENV_KEYS if not self._env(key)]
        if missing:
            return CredentialsStatusV1(available=False, reason=f"missing FreshRSS credentials: {', '.join(missing)}")
        return CredentialsStatusV1(available=True)

    def _base_url(self) -> str:
        return (self._env("FRESHRSS_BASE_URL") or "").rstrip("/")

    def login(self) -> str:
        status = self.credentials_status()
        if not status.available:
            raise AdapterError(status.reason)
        from urllib.parse import urlencode

        body = urlencode(
            {"Email": self._env("FRESHRSS_USERNAME") or "", "Passwd": self._env("FRESHRSS_API_PASSWORD") or ""}
        )
        response = self._transport.fetch(
            HttpRequest(
                url=f"{self._base_url()}/api/greader.php/accounts/ClientLogin?{body}",
                method="GET",
            )
        )
        token = ""
        for line in response.body.decode("utf-8", errors="replace").splitlines():
            if line.startswith("Auth="):
                token = line.split("=", 1)[1].strip()
        if not token:
            raise AdapterError("FreshRSS ClientLogin did not return an Auth token")
        self._auth_token = token
        return token

    def unread_items(self, *, max_pages: int = 5, page_size: int = 100) -> list[FreshRssItem]:
        import json

        token = self._auth_token or self.login()
        headers = {"Authorization": f"GoogleLogin auth={token}"}
        items: list[FreshRssItem] = []
        continuation: str | None = None
        for _ in range(max_pages):
            from urllib.parse import urlencode

            params = {"n": str(page_size), "xt": "user/-/state/com.google/read", "output": "json"}
            if continuation:
                params["c"] = continuation
            url = f"{self._base_url()}/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/reading-list?{urlencode(params)}"
            response = self._transport.fetch(HttpRequest(url=url, headers=headers))
            payload: dict[str, Any] = json.loads(response.body.decode("utf-8") or "{}")
            for entry in payload.get("items", []):
                items.append(_item_from_entry(entry))
            continuation = payload.get("continuation")
            if not continuation:
                break
        return items


def _item_from_entry(entry: dict[str, Any]) -> FreshRssItem:
    canonical = ""
    for link in entry.get("canonical", []) or entry.get("alternate", []):
        if isinstance(link, dict) and link.get("href"):
            canonical = link["href"]
            break
    timestamp = entry.get("published") or entry.get("crawlTimeMsec")
    published_at = ""
    if isinstance(timestamp, int):
        from datetime import datetime, timezone

        seconds = timestamp / 1000 if timestamp > 10_000_000_000 else timestamp
        published_at = datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    return FreshRssItem(
        item_id=str(entry.get("id", "")),
        title=str(entry.get("title", "")).strip(),
        url=canonical,
        published_at=published_at,
        origin_stream_id=str((entry.get("origin") or {}).get("streamId", "")),
    )
