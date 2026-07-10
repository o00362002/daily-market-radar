"""Provider-neutral source health model and deterministic transition logic."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum


class SourceHealthStatus(str, Enum):
    HEALTHY = "healthy"
    STALE = "stale"
    EMPTY = "empty"
    SILENT_ZERO = "silent_zero"
    FAILING = "failing"
    POLICY_BLOCKED = "policy_blocked"
    CREDENTIAL_UNAVAILABLE = "credential_unavailable"
    RATE_LIMITED = "rate_limited"


@dataclass(frozen=True)
class SourceHealthRecord:
    source_id: str
    status: str
    checked_at: str
    last_success_at: str = ""
    last_item_at: str = ""
    consecutive_failures: int = 0
    response_count: int = 0
    latency_ms: int = 0
    failure_reason: str = ""
    retry_at: str = ""

    def as_health_status(self) -> str:
        return self.status


@dataclass(frozen=True)
class FetchObservation:
    ok: bool
    item_count: int
    latency_ms: int
    checked_at: str
    latest_item_at: str = ""
    failure_reason: str = ""
    policy_blocked: bool = False
    credential_unavailable: bool = False
    rate_limited: bool = False
    retry_after_seconds: int = 0


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def evaluate_health(
    prior: SourceHealthRecord | None,
    observation: FetchObservation,
    *,
    freshness_slo_minutes: int,
    backoff_base_seconds: int = 60,
) -> SourceHealthRecord:
    """Deterministically derive the new health record from a fetch observation."""

    last_success_at = prior.last_success_at if prior else ""
    last_item_at = prior.last_item_at if prior else ""
    consecutive_failures = prior.consecutive_failures if prior else 0

    if observation.policy_blocked:
        status = SourceHealthStatus.POLICY_BLOCKED.value
    elif observation.credential_unavailable:
        status = SourceHealthStatus.CREDENTIAL_UNAVAILABLE.value
    elif observation.rate_limited:
        status = SourceHealthStatus.RATE_LIMITED.value
    elif not observation.ok:
        status = SourceHealthStatus.FAILING.value
    else:
        # Successful transport response.
        last_success_at = observation.checked_at
        if observation.item_count > 0:
            last_item_at = observation.latest_item_at or observation.checked_at
            status = SourceHealthStatus.HEALTHY.value
        elif not last_item_at:
            status = SourceHealthStatus.EMPTY.value
        else:
            # Responded 200 with zero items: stale if past the freshness SLO, else silent zero.
            age = _parse(observation.checked_at) - _parse(last_item_at)
            status = (
                SourceHealthStatus.STALE.value
                if age > timedelta(minutes=freshness_slo_minutes)
                else SourceHealthStatus.SILENT_ZERO.value
            )

    if observation.ok and not (
        observation.policy_blocked or observation.credential_unavailable or observation.rate_limited
    ):
        consecutive_failures = 0
    elif not observation.ok:
        consecutive_failures += 1

    retry_at = ""
    if status in {
        SourceHealthStatus.FAILING.value,
        SourceHealthStatus.RATE_LIMITED.value,
    }:
        base = observation.retry_after_seconds or backoff_base_seconds * (2 ** min(consecutive_failures, 6))
        retry_at = (_parse(observation.checked_at) + timedelta(seconds=base)).isoformat()

    return SourceHealthRecord(
        source_id=prior.source_id if prior else "",
        status=status,
        checked_at=observation.checked_at,
        last_success_at=last_success_at,
        last_item_at=last_item_at,
        consecutive_failures=consecutive_failures,
        response_count=(prior.response_count if prior else 0) + 1,
        latency_ms=observation.latency_ms,
        failure_reason=observation.failure_reason,
        retry_at=retry_at,
    )


def with_source_id(record: SourceHealthRecord, source_id: str) -> SourceHealthRecord:
    return replace(record, source_id=source_id)
