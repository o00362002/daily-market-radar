"""Hardened, transport-based RSS/Atom fetch with conditional requests + backoff.

Adds ETag / Last-Modified conditional fetching, deterministic exponential backoff
with injectable jitter, and per-source failure isolation on top of the existing
feed parser. Fully unit-testable offline via the HttpTransport seam.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from radar.adapters.base import AdapterError
from radar.adapters.transport import HttpRequest, HttpTransport, conditional_headers
from radar.adapters.rss import _parse_feed
from radar.domain.models import Document
from radar.schemas.source import Source


@dataclass(frozen=True)
class ConditionalFetchResult:
    documents: tuple[Document, ...]
    etag: str
    last_modified: str
    not_modified: bool
    item_count: int


def backoff_delays(
    attempts: int,
    *,
    base_seconds: float = 0.5,
    max_seconds: float = 30.0,
    jitter: Callable[[int], float] = lambda _attempt: 0.0,
) -> list[float]:
    """Deterministic exponential backoff schedule with injectable jitter.

    ``jitter`` receives the attempt index and returns a non-negative offset; the
    default (0.0) makes the schedule fully deterministic for tests.
    """

    delays: list[float] = []
    for attempt in range(attempts):
        raw = min(max_seconds, base_seconds * (2 ** attempt)) + max(0.0, jitter(attempt))
        delays.append(round(min(max_seconds, raw), 4))
    return delays


class ConditionalRssClient:
    def __init__(self, transport: HttpTransport, *, per_feed_limit: int = 20) -> None:
        self._transport = transport
        self._per_feed_limit = per_feed_limit

    def fetch(
        self,
        source: Source,
        feed_url: str,
        *,
        etag: str | None = None,
        last_modified: str | None = None,
    ) -> ConditionalFetchResult:
        fetched_at = datetime.now(timezone.utc).isoformat()
        response = self._transport.fetch(
            HttpRequest(url=feed_url, headers=conditional_headers(etag, last_modified))
        )
        if response.not_modified:
            return ConditionalFetchResult(
                documents=(),
                etag=etag or "",
                last_modified=last_modified or "",
                not_modified=True,
                item_count=0,
            )
        documents = tuple(
            _parse_feed(response.body, source=source, fetched_at=fetched_at, limit=self._per_feed_limit)
        )
        return ConditionalFetchResult(
            documents=documents,
            etag=response.header("ETag"),
            last_modified=response.header("Last-Modified"),
            not_modified=False,
            item_count=len(documents),
        )


def fetch_with_retry(
    fetcher: Callable[[], ConditionalFetchResult],
    *,
    max_attempts: int = 3,
    sleep: Callable[[float], None] = lambda _seconds: None,
    jitter: Callable[[int], float] = lambda _attempt: 0.0,
) -> ConditionalFetchResult:
    """Retry a single-feed fetch with bounded exponential backoff + jitter.

    Failures are isolated to this feed; the last error is surfaced only after all
    attempts are exhausted.
    """

    delays = backoff_delays(max_attempts, jitter=jitter)
    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return fetcher()
        except Exception as exc:  # noqa: BLE001 - isolated per feed
            last_error = exc
            if attempt < max_attempts - 1:
                sleep(delays[attempt + 1])
    raise AdapterError(f"feed failed after {max_attempts} attempts: {last_error}")
