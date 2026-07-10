from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from radar.domain.models import Document
from radar.schemas.source import Source, SourceRegistry


@dataclass(frozen=True)
class FeedFailure:
    source_id: str
    adapter_url: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "adapter_url": self.adapter_url,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RssAdapter:
    source_id: str
    feed_url: str

    def parse(self, xml_text: str) -> list[Document]:
        root = ElementTree.fromstring(xml_text)
        documents: list[Document] = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or "Untitled"
            link = urljoin(self.feed_url, item.findtext("link") or self.feed_url)
            documents.append(Document.fixture(source_id=self.source_id, url=link, title=title))
        return documents


def fetch_registry_rss_documents(
    registry: SourceRegistry,
    *,
    timeout_seconds: int = 12,
    per_feed_limit: int = 20,
) -> tuple[list[Document], list[FeedFailure], list[str]]:
    documents: list[Document] = []
    failures: list[FeedFailure] = []
    checked_sources: list[str] = []
    fetched_at = datetime.now(timezone.utc).isoformat()

    for source in registry.sources:
        if not source.enabled:
            continue
        rss_adapters = [adapter for adapter in source.adapters if adapter.kind == "rss"]
        if not rss_adapters:
            continue
        checked_sources.append(source.source_id)
        for adapter in rss_adapters:
            try:
                payload = _download(adapter.url, timeout_seconds=timeout_seconds)
                documents.extend(
                    _parse_feed(
                        payload,
                        source=source,
                        fetched_at=fetched_at,
                        limit=per_feed_limit,
                    )
                )
            except Exception as exc:  # noqa: BLE001 - failure is converted to an explicit coverage gap
                failures.append(FeedFailure(source.source_id, adapter.url, f"{type(exc).__name__}: {exc}"))

    return documents, failures, checked_sources


def _download(url: str, *, timeout_seconds: int) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "daily-market-radar/0.2 (+https://github.com/o00362002/daily-market-radar)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.1",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310 - registry URLs are validated
        return response.read()


def _parse_feed(payload: bytes, *, source: Source, fetched_at: str, limit: int) -> list[Document]:
    root = ElementTree.fromstring(payload)
    entries = list(_rss_entries(root)) or list(_atom_entries(root))
    documents: list[Document] = []
    for entry in entries[:limit]:
        title = entry.get("title", "").strip()
        raw_link = entry.get("link", "").strip()
        link = urljoin(source.canonical_url, raw_link)
        if not title or not link:
            continue
        published_at = _normalize_date(entry.get("published", ""), fallback=fetched_at)
        summary = entry.get("summary", "").strip()
        documents.append(
            Document.fixture(
                source_id=source.source_id,
                url=link,
                title=title,
                language=source.languages[0],
                macro_region=source.macro_region,
                published_at=published_at,
                fetched_at=fetched_at,
                entities=[source.name],
                action="publishes",
                object=title,
                location=source.publisher_country,
                primary_domain=source.domains[0],
                lane=_lane_for_source(source),
                summary=summary,
                facts={"source_roles": source.source_roles, "adapter": "rss"},
            )
        )
    return documents


def _rss_entries(root: ElementTree.Element) -> Iterable[dict[str, str]]:
    channel = root.find("channel")
    if channel is None:
        return []
    rows: list[dict[str, str]] = []
    for item in channel.findall("item"):
        rows.append(
            {
                "title": _text(item.find("title")),
                "link": _text(item.find("link")),
                "published": _text(item.find("pubDate")) or _text(item.find("date")),
                "summary": _text(item.find("description")),
            }
        )
    return rows


def _atom_entries(root: ElementTree.Element) -> Iterable[dict[str, str]]:
    namespace = "{http://www.w3.org/2005/Atom}"
    rows: list[dict[str, str]] = []
    for entry in root.findall(f"{namespace}entry"):
        link = ""
        for link_node in entry.findall(f"{namespace}link"):
            rel = link_node.attrib.get("rel", "alternate")
            href = link_node.attrib.get("href", "")
            if href and rel in {"alternate", ""}:
                link = href
                break
        rows.append(
            {
                "title": _text(entry.find(f"{namespace}title")),
                "link": link,
                "published": _text(entry.find(f"{namespace}published")) or _text(entry.find(f"{namespace}updated")),
                "summary": _text(entry.find(f"{namespace}summary")) or _text(entry.find(f"{namespace}content")),
            }
        )
    return rows


def _text(node: ElementTree.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def _normalize_date(value: str, *, fallback: str) -> str:
    if not value:
        return fallback
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except ValueError:
            return fallback


def _lane_for_source(source: Source) -> str:
    top_down_roles = {
        "official",
        "company",
        "data",
        "central_bank",
        "exchange",
        "regulator",
        "international_organization",
        "news_agency",
        "national",
        "legislature",
        "executive",
    }
    return "top_down" if top_down_roles.intersection(source.source_roles) else "bottom_up"
