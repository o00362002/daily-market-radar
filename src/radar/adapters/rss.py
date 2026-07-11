from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from radar.domain.models import Document
from radar.contracts.report import CoverageGapV2, SourceFailureV1
from radar.ports.sources import (
    CredentialsStatusV1,
    RateLimitPolicy,
    RetryPolicy,
    SourceFetchRequest,
    SourceFetchResult,
    SourceHealthV1,
)
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
        published_at = _normalize_date(
            entry.get("published", ""),
            fallback=fetched_at,
            default_timezone=_default_timezone(source),
        )
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
                facts={"source_roles": source.source_roles},
            )
        )
    return documents


def _rss_entries(root: ElementTree.Element) -> Iterable[dict[str, str]]:
    rows: list[dict[str, str]] = []
    # RSS 2.0 uses unqualified ``channel/item`` nodes, while RSS 1.0 uses
    # namespaced RDF ``item`` nodes at the document root. Match by local name
    # so both standards follow the same provider-neutral normalization path.
    for item in (node for node in root.iter() if _local_name(node.tag) == "item"):
        rows.append(
            {
                "title": _child_text(item, "title"),
                "link": _child_text(item, "link") or _rdf_about(item),
                "published": _child_text(item, "pubDate", "date", "published", "updated"),
                "summary": _child_text(item, "description", "summary", "encoded"),
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


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(node: ElementTree.Element, *names: str) -> str:
    # Respect caller priority (for example prefer a short description over a
    # full content:encoded body) while remaining namespace agnostic.
    for name in names:
        for child in node:
            if _local_name(child.tag) == name:
                value = _text(child)
                if value:
                    return value
    return ""


def _rdf_about(node: ElementTree.Element) -> str:
    return node.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "").strip()


def _default_timezone(source: Source) -> timezone:
    return timezone(timedelta(hours=8)) if source.macro_region == "Taiwan" else timezone.utc


def _normalize_date(
    value: str,
    *,
    fallback: str,
    default_timezone: timezone = timezone.utc,
) -> str:
    if not value:
        return fallback
    # Some otherwise valid feeds emit two spaces between date and time. Both
    # RFC and ISO parsers reject that spelling, so normalize whitespace first.
    value = " ".join(value.split())
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=default_timezone)
        return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=default_timezone)
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


@dataclass(frozen=True)
class RegistryRssSourceAdapter:
    registry: SourceRegistry
    timeout_seconds: int = 12
    per_feed_limit: int = 20
    adapter_id: str = "rss_atom"
    source_id: str = "source_registry"
    retry_policy: RetryPolicy = RetryPolicy(max_attempts=2, backoff_seconds=0.5)
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()

    def credentials_status(self) -> CredentialsStatusV1:
        return CredentialsStatusV1(available=True)

    def health_check(self) -> SourceHealthV1:
        return SourceHealthV1(status="healthy", message="public RSS/Atom adapter enabled")

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        del request
        documents, failures, checked_sources = fetch_registry_rss_documents(
            self.registry,
            timeout_seconds=self.timeout_seconds,
            per_feed_limit=self.per_feed_limit,
        )
        non_rss_enabled = [
            source.source_id
            for source in self.registry.sources
            if source.enabled and not any(adapter.kind == "rss" for adapter in source.adapters)
        ]
        degradation_reasons: list[str] = []
        if failures:
            degradation_reasons.append("rss_fetch_failures")
        if non_rss_enabled:
            degradation_reasons.append("web_api_social_adapters_not_executed")
        if not documents:
            degradation_reasons.append("no_live_documents_ingested")

        gaps = tuple(
            CoverageGapV2(
                domain="unknown_until_source_mapping",
                macro_region="source_registry",
                language="source_defined",
                source_role="rss",
                channel=failure.adapter_url,
                time_window="24h",
                reason="feed_fetch_failed",
                message=f"{failure.source_id}: {failure.reason}",
            )
            for failure in failures
        )
        taiwan_sources = tuple(
            source.source_id
            for source in self.registry.sources
            if source.macro_region == "Taiwan" and any(adapter.kind == "rss" for adapter in source.adapters)
        )
        return SourceFetchResult(
            documents=tuple(documents),
            coverage_gaps=gaps,
            degradation_reasons=tuple(degradation_reasons),
            sources_checked=tuple(checked_sources),
            failures=tuple(
                SourceFailureV1(
                    source_id=failure.source_id,
                    reason=failure.reason,
                    channel=failure.adapter_url,
                )
                for failure in failures
            ),
            sources_not_executed=tuple(non_rss_enabled),
            registry_checked=True,
            integration_status=(("external_discovery", "not_executed"),),
            taiwan_direct_sources_checked=taiwan_sources,
            remaining_gaps=(
                "web/API/social adapters are not executed by the RSS composition",
                "external discovery and collection inbox are not connected",
            ),
        )

    def normalize(self, result: SourceFetchResult) -> list[Document]:
        return list(result.documents)
