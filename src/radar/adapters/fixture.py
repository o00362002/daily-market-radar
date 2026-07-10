from __future__ import annotations

from dataclasses import dataclass

from radar.contracts.report import CoverageGapV2
from radar.domain.models import Document
from radar.pipeline.ingest import ingest_fixture_documents
from radar.ports.sources import (
    CredentialsStatusV1,
    RateLimitPolicy,
    RetryPolicy,
    SourceFetchRequest,
    SourceFetchResult,
    SourceHealthV1,
)


@dataclass(frozen=True)
class FixtureSourceAdapter:
    collection_aggregator_available: bool = False
    external_discovery_available: bool = True
    adapter_id: str = "fixture"
    source_id: str = "fixture_registry"
    retry_policy: RetryPolicy = RetryPolicy()
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()

    def credentials_status(self) -> CredentialsStatusV1:
        return CredentialsStatusV1(available=True)

    def health_check(self) -> SourceHealthV1:
        return SourceHealthV1(status="healthy", message="deterministic fixture available")

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        del request
        degradation_reasons = ["fixture_ingestion_only"]
        integration_status = [
            ("collection_aggregator", "available" if self.collection_aggregator_available else "unavailable")
        ]
        remaining_gaps = ["fixture data is not live source coverage"]
        coverage_gaps: list[CoverageGapV2] = []
        if not self.collection_aggregator_available:
            degradation_reasons.append("freshrss_unavailable")
            coverage_gaps.append(
                CoverageGapV2(
                    domain="all",
                    macro_region="global",
                    language="multi",
                    source_role="collection",
                    channel="collection_aggregator",
                    time_window="24h",
                    reason="freshrss_unavailable",
                    message="collection aggregator unavailable; fixture run remains partial",
                )
            )
        if not self.external_discovery_available:
            degradation_reasons.append("external_discovery_unavailable")
            integration_status.append(("external_discovery", "unavailable"))
            message = "external discovery unavailable; report is partial"
            remaining_gaps.append(message)
            coverage_gaps.append(
                CoverageGapV2(
                    domain="all",
                    macro_region="global",
                    language="multi",
                    source_role="discovery",
                    channel="external",
                    time_window="24h",
                    reason="external_discovery_unavailable",
                    message=message,
                )
            )
        else:
            integration_status.append(("external_discovery", "available"))
        return SourceFetchResult(
            documents=tuple(ingest_fixture_documents()),
            coverage_gaps=tuple(coverage_gaps),
            degradation_reasons=tuple(degradation_reasons),
            sources_checked=("fixture_registry",),
            registry_checked=True,
            integration_status=tuple(integration_status),
            taiwan_direct_sources_checked=("twse",),
            remaining_gaps=tuple(remaining_gaps),
        )

    def normalize(self, result: SourceFetchResult) -> list[Document]:
        return list(result.documents)
