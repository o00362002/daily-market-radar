from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from radar.domain.models import Document


@dataclass(frozen=True)
class FreshnessFilterResult:
    accepted: list[Document]
    rejected_stale: list[Document]
    rejected_future: list[Document]
    rejected_invalid_timestamp: list[Document]

    @property
    def rejected_count(self) -> int:
        return len(self.rejected_stale) + len(self.rejected_future) + len(self.rejected_invalid_timestamp)


def filter_documents_by_freshness(
    documents: list[Document],
    *,
    observed_at: str,
    max_age_hours: int = 36,
    future_tolerance_hours: int = 2,
) -> FreshnessFilterResult:
    """Keep only documents plausibly belonging to the current live-news window.

    Feed endpoints frequently return archive entries on every poll. Without a publication-time
    boundary, an old article that does not match durable event history can be misclassified as a
    new event. The filter therefore runs before clustering and event resolution.

    ``published_at`` is authoritative. Invalid publication timestamps are rejected rather than
    silently replaced with ``fetched_at``, because doing so would turn every archive item fetched
    today into an apparently fresh document.
    """

    observed = _parse_timestamp(observed_at)
    oldest = observed - timedelta(hours=max_age_hours)
    newest = observed + timedelta(hours=future_tolerance_hours)

    accepted: list[Document] = []
    rejected_stale: list[Document] = []
    rejected_future: list[Document] = []
    rejected_invalid: list[Document] = []

    for document in documents:
        try:
            published = _parse_timestamp(document.published_at)
        except ValueError:
            rejected_invalid.append(document)
            continue
        if published < oldest:
            rejected_stale.append(document)
        elif published > newest:
            rejected_future.append(document)
        else:
            accepted.append(document)

    return FreshnessFilterResult(
        accepted=accepted,
        rejected_stale=rejected_stale,
        rejected_future=rejected_future,
        rejected_invalid_timestamp=rejected_invalid,
    )


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
