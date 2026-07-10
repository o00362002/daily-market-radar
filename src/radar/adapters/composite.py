"""Provider-neutral composition for multiple source adapters.

The application still depends on one SourceAdapter. This adapter fans out to
independent children, isolates one integration's failure, and merges their
canonical SourceFetchResult values without importing provider details into the
application layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from radar.contracts.report import CoverageGapV2, SourceFailureV1
from radar.domain.models import Document
from radar.ports.sources import (
    CredentialsStatusV1,
    RateLimitPolicy,
    RetryPolicy,
    SourceAdapter,
    SourceFetchRequest,
    SourceFetchResult,
    SourceHealthV1,
)


@dataclass(frozen=True)
class CompositeSourceAdapter:
    adapters: tuple[SourceAdapter, ...]
    adapter_id: str = "multi_source"
    source_id: str = "source_registry"
    retry_policy: RetryPolicy = RetryPolicy(max_attempts=1)
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()

    def __post_init__(self) -> None:
        if not self.adapters:
            raise ValueError("CompositeSourceAdapter requires at least one child adapter")

    def credentials_status(self) -> CredentialsStatusV1:
        statuses = [(adapter.adapter_id, adapter.credentials_status()) for adapter in self.adapters]
        if any(status.available for _, status in statuses):
            unavailable = [f"{adapter_id}: {status.reason}" for adapter_id, status in statuses if not status.available]
            return CredentialsStatusV1(available=True, reason="; ".join(unavailable))
        reasons = [f"{adapter_id}: {status.reason}" for adapter_id, status in statuses]
        return CredentialsStatusV1(available=False, reason="; ".join(reasons))

    def health_check(self) -> SourceHealthV1:
        child_statuses: list[tuple[str, str, str]] = []
        for adapter in self.adapters:
            credentials = adapter.credentials_status()
            if not credentials.available:
                child_statuses.append((adapter.adapter_id, "credential_unavailable", credentials.reason))
                continue
            health = adapter.health_check()
            child_statuses.append((adapter.adapter_id, health.status, health.message))

        healthy_count = sum(status == "healthy" for _, status, _ in child_statuses)
        if healthy_count == len(child_statuses):
            return SourceHealthV1(status="healthy", message="all configured source adapters are healthy")
        if healthy_count:
            details = "; ".join(f"{adapter_id}={status}" for adapter_id, status, _ in child_statuses)
            return SourceHealthV1(status="partial", message=details)
        details = "; ".join(f"{adapter_id}={status}" for adapter_id, status, _ in child_statuses)
        return SourceHealthV1(status="failing", message=details)

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        documents: list[Document] = []
        coverage_gaps: list[CoverageGapV2] = []
        degradation_reasons: list[str] = []
        sources_checked: list[str] = []
        failures: list[SourceFailureV1] = []
        sources_not_executed: list[str] = []
        integration_status: dict[str, str] = {}
        taiwan_sources: list[str] = []
        remaining_gaps: list[str] = []
        registry_checked = True

        for adapter in self.adapters:
            credentials = adapter.credentials_status()
            if not credentials.available:
                degradation_reasons.append(f"{adapter.adapter_id}_credential_unavailable")
                sources_not_executed.append(adapter.source_id)
                integration_status[adapter.adapter_id] = "credential_unavailable"
                remaining_gaps.append(credentials.reason or f"{adapter.adapter_id} credentials unavailable")
                coverage_gaps.append(
                    CoverageGapV2(
                        domain="all",
                        macro_region="global",
                        language="multi",
                        source_role="collection",
                        channel=adapter.adapter_id,
                        time_window="24h",
                        reason="credential_unavailable",
                        message=credentials.reason or f"{adapter.adapter_id} credentials unavailable",
                    )
                )
                continue

            try:
                result = adapter.fetch(request)
            except Exception as exc:  # noqa: BLE001 - one provider must not stop the full collection run
                reason = f"{type(exc).__name__}: {exc}"
                degradation_reasons.append(f"{adapter.adapter_id}_fetch_failed")
                failures.append(SourceFailureV1(source_id=adapter.source_id, reason=reason, channel=adapter.adapter_id))
                integration_status[adapter.adapter_id] = "failing"
                coverage_gaps.append(
                    CoverageGapV2(
                        domain="all",
                        macro_region="global",
                        language="multi",
                        source_role="collection",
                        channel=adapter.adapter_id,
                        time_window="24h",
                        reason="adapter_fetch_failed",
                        message=reason,
                    )
                )
                continue

            documents.extend(result.documents)
            coverage_gaps.extend(result.coverage_gaps)
            degradation_reasons.extend(result.degradation_reasons)
            sources_checked.extend(result.sources_checked)
            failures.extend(result.failures)
            sources_not_executed.extend(result.sources_not_executed)
            integration_status.update(dict(result.integration_status))
            integration_status.setdefault(adapter.adapter_id, adapter.health_check().status)
            taiwan_sources.extend(result.taiwan_direct_sources_checked)
            remaining_gaps.extend(result.remaining_gaps)
            registry_checked = registry_checked and result.registry_checked

        return SourceFetchResult(
            documents=tuple(documents),
            coverage_gaps=tuple(_unique(coverage_gaps)),
            degradation_reasons=tuple(_unique(degradation_reasons)),
            sources_checked=tuple(_unique(sources_checked)),
            failures=tuple(_unique(failures)),
            sources_not_executed=tuple(_unique(sources_not_executed)),
            registry_checked=registry_checked,
            integration_status=tuple(sorted(integration_status.items())),
            taiwan_direct_sources_checked=tuple(_unique(taiwan_sources)),
            remaining_gaps=tuple(_unique(remaining_gaps)),
        )

    def normalize(self, result: SourceFetchResult) -> list[Document]:
        return list(result.documents)


def _unique(values):  # type: ignore[no-untyped-def]
    return list(dict.fromkeys(values))
