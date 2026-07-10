"""Safe web fetcher: registry allowlist only, SSRF-guarded, bounded extraction.

Never bypasses paywalls or logins, never stores full copyrighted articles, and
never becomes an arbitrary URL crawler. Only allowlisted registry URLs are
fetched; the transport re-validates every redirect hop against the SSRF policy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser

from radar.adapters.base import AdapterError, UrlPolicy
from radar.adapters.transport import HttpRequest, HttpTransport
from radar.domain.models import canonicalize_url, stable_id

ALLOWED_CONTENT_TYPES = {"text/html", "application/xhtml+xml", "application/xml", "text/xml", "text/plain"}
DEFAULT_EXCERPT_CHARS = 400


@dataclass(frozen=True)
class SafeWebDocument:
    source_id: str
    canonical_url: str
    title: str
    excerpt: str
    published_at: str
    content_hash: str


class _MetaTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.published_at = ""
        self._in_title = False
        self._text_parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style"}:
            self._skip_depth += 1
        if tag == "meta":
            attributes = {key.lower(): (value or "") for key, value in attrs}
            prop = attributes.get("property", "") or attributes.get("name", "")
            if prop.lower() in {"article:published_time", "og:published_time", "date", "pubdate"}:
                self.published_at = attributes.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif self._skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self._text_parts.append(stripped)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._text_parts)).strip()


class SafeWebFetcher:
    def __init__(
        self,
        transport: HttpTransport,
        *,
        policy: UrlPolicy | None = None,
        excerpt_chars: int = DEFAULT_EXCERPT_CHARS,
    ) -> None:
        self._transport = transport
        self._policy = policy or UrlPolicy(allow_internal_hosts=set())
        self._excerpt_chars = excerpt_chars

    def fetch(self, url: str, *, source_id: str, allowlist: set[str]) -> SafeWebDocument:
        canonical = canonicalize_url(url)
        if canonical not in allowlist and url not in allowlist:
            raise AdapterError(f"url is not in the registry allowlist: {url}")
        if not self._policy.is_allowed(url):
            raise AdapterError(f"blocked by url policy: {url}")

        response = self._transport.fetch(HttpRequest(url=url))
        if response.content_type and response.content_type not in ALLOWED_CONTENT_TYPES:
            raise AdapterError(f"disallowed content type: {response.content_type}")

        parser = _MetaTextParser()
        parser.feed(response.body.decode("utf-8", errors="replace"))
        excerpt = parser.text[: self._excerpt_chars]
        published_at = _normalize_date(parser.published_at)
        content_hash = stable_id("web", [canonical, excerpt])
        return SafeWebDocument(
            source_id=source_id,
            canonical_url=canonical,
            title=parser.title.strip() or canonical,
            excerpt=excerpt,
            published_at=published_at,
            content_hash=content_hash,
        )


def _normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except ValueError:
        return ""
