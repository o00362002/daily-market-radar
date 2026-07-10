"""SourceAdapter wrapper for the FreshRSS Google Reader collection inbox."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
from urllib.parse import unquote

from radar.adapters.freshrss import FreshRssAdapter
from radar.adapters.transport import HttpTransport
from radar.contracts.report import CoverageGapV2, SourceFailureV1
from radar.domain.models import Document, canonicalize_url
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
class FreshRssRegistrySourceAdapter:
    registry: SourceRegistry
    transport: HttpTransport
    env: Callable[[str], str | None]
    adapter_id: str = "freshrss_google_reader"
    source_id: str = "freshrss_collection"
    retry_policy: RetryPolicy = RetryPolicy(max_attempts=2, backoff_seconds=0.5)
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()

    def _client(self) -> FreshRssAdapter:
        return FreshRssAdapter(self.transport, env=self.env)

    def credentials_status(self) -> CredentialsStatusV1:
        return self._client().credentials_status()

    def health_check(self) -> SourceHealthV1:
        status = self.credentials_status()
        if not status.available:
            return SourceHealthV1(status="credential_unavailable", message=status.reason)
        return SourceHealthV1(status="healthy", message="FreshRSS Google Reader API credentials are available")

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        del request
        credentials = self.credentials_status()
        if not credentials.available:
            return SourceFetchResult(
                documents=(),
                coverage_gaps=(
                    CoverageGapV2(
                        domain="all",
                        macro_region="global",
                        language="multi",
                        source_role="collection_aggregator",
                        channel=self.adapter_id,
                        time_window="24h",
                        reason="credential_unavailable",
                        message=credentials.reason,
                    ),
                ),
                degradation_reasons=("freshrss_credentials_unavailable",),
                sources_not_executed=(self.source_id,),
                integration_status=(("collection_aggregator", "credential_unavailable"),),
                remaining_gaps=(credentials.reason,),
            )

        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            items = self._client().unread_items()
        except Exception as exc:  # noqa: BLE001 - converted to an explicit source failure
            reason = f"{type(exc).__name__}: {exc}"
            return SourceFetchResult(
                documents=(),
                coverage_gaps=(
                    CoverageGapV2(
                        domain="all",
                        macro_region="global",
                        language="multi",
                        source_role="collection_aggregator",
                        channel=self.adapter_id,
                        time_window="24h",
                        reason="freshrss_fetch_failed",
                        message=reason,
                    ),
                ),
                degradation_reasons=("freshrss_fetch_failed",),
                failures=(SourceFailureV1(source_id=self.source_id, reason=reason, channel=self.adapter_id),),
                integration_status=(("collection_aggregator", "failing"),),
                remaining_gaps=("FreshRSS inbox could not be read",),
            )

        feed_map = _registry_feed_map(self.registry)
        documents: list[Document] = []
        mapped_sources: list[str] = []
        unmapped_streams: list[str] = []
        taiwan_sources: list[str] = []
        for item in items:
            feed_url = _feed_url(item.origin_stream_id)
            source = feed_map.get(canonicalize_url(feed_url)) if feed_url else None
            if source is None:
                unmapped_streams.append(item.origin_stream_id or "unknown_stream")
                continue
            if not item.title or not item.url:
                continue
            documents.append(
                Document.fixture(
                    source_id=source.source_id,
                    url=item.url,
                    title=item.title,
                    language=source.languages[0],
                    macro_region=source.macro_region,
                    published_at=item.published_at or fetched_at,
                    fetched_at=fetched_at,
                    entities=[source.name],
                    action="publishes",
                    object=item.title,
                    location=source.publisher_country,
                    primary_domain=source.domains[0],
                    lane=_lane_for_source(source),
                    facts={"source_roles": source.source_roles},
                )
            )
            mapped_sources.append(source.source_id)
            if source.macro_region == "Taiwan":
                taiwan_sources.append(source.source_id)

        gaps = tuple(
            CoverageGapV2(
                domain="unknown_until_source_mapping",
                macro_region="collection_inbox",
                language="source_defined",
                source_role="collection_aggregator",
                channel=stream,
                time_window="24h",
                reason="freshrss_stream_unmapped",
                message=f"FreshRSS origin stream is not mapped to source_registry: {stream}",
            )
            for stream in sorted(set(unmapped_streams))
        )
        degradation: list[str] = []
        remaining: list[str] = []
        if unmapped_streams:
            degradation.append("freshrss_unmapped_streams")
            remaining.append("Some FreshRSS streams are not mapped to canonical source_id values")
        if not documents:
            degradation.append("freshrss_no_documents")

        return SourceFetchResult(
            documents=tuple(documents),
            coverage_gaps=gaps,
            degradation_reasons=tuple(degradation),
            sources_checked=tuple(sorted(set(mapped_sources))),
            sources_not_executed=tuple(sorted(set(unmapped_streams))),
            registry_checked=True,
            integration_status=(("collection_aggregator", "checked"),),
            taiwan_direct_sources_checked=tuple(sorted(set(taiwan_sources))),
            remaining_gaps=tuple(remaining),
        )

    def normalize(self, result: SourceFetchResult) -> list[Document]:
        return list(result.documents)


def _feed_url(origin_stream_id: str) -> str:
    value = unquote(origin_stream_id.strip())
    if value.startswith("feed/"):
        value = value[5:]
    return value if value.startswith(("http://", "https://")) else ""


def _registry_feed_map(registry: SourceRegistry) -> dict[str, Source]:
    result: dict[str, Source] = {}
    for source in registry.sources:
        if not source.enabled:
            continue
        for adapter in source.adapters:
            if adapter.kind == "rss":
                result[canonicalize_url(adapter.url)] = source
    return result


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
