from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from radar.contracts.report import CoverageGapV2, SourceFailureV1
from radar.domain.models import Document


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff_seconds: float = 0.0


@dataclass(frozen=True)
class RateLimitPolicy:
    requests_per_minute: int | None = None


@dataclass(frozen=True)
class CredentialsStatusV1:
    available: bool
    reason: str = ""


@dataclass(frozen=True)
class SourceHealthV1:
    status: str
    message: str = ""


@dataclass(frozen=True)
class SourceFetchRequest:
    date: str
    profile: str


@dataclass(frozen=True)
class SourceFetchResult:
    documents: tuple[Document, ...]
    coverage_gaps: tuple[CoverageGapV2, ...] = ()
    degradation_reasons: tuple[str, ...] = ()
    sources_checked: tuple[str, ...] = ()
    failures: tuple[SourceFailureV1, ...] = ()
    sources_not_executed: tuple[str, ...] = ()
    registry_checked: bool = True
    integration_status: tuple[tuple[str, str], ...] = ()
    taiwan_direct_sources_checked: tuple[str, ...] = ()
    remaining_gaps: tuple[str, ...] = ()


@runtime_checkable
class SourceAdapter(Protocol):
    adapter_id: str
    source_id: str
    retry_policy: RetryPolicy
    rate_limit_policy: RateLimitPolicy

    def credentials_status(self) -> CredentialsStatusV1: ...

    def health_check(self) -> SourceHealthV1: ...

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult: ...

    def normalize(self, result: SourceFetchResult) -> list[Document]: ...
