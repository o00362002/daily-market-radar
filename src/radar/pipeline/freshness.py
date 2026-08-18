from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from radar.domain.models import Document


_TAIWAN_TZ = timezone(timedelta(hours=8))


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

    ``published_at`` is authoritative. Invalid publication timestamps are rejected rather than
    silently replaced with ``fetched_at``, because doing so would turn archive items fetched today
    into apparently fresh documents.
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


def document_is_in_report_window(document: Document, report_date: str, *, lookback_days: int = 1) -> bool:
    """Accept the Taiwan report date and a bounded number of prior calendar days.

    The default keeps the daily run's current and prior Taiwan calendar day to
    cover US and European sessions. Callers with a seven-day inclusive report
    window pass ``lookback_days=6``. Archive entries older than the requested
    window must not become ``new_event`` merely because a feed returns them
    again. Invalid publication timestamps are rejected.
    """

    try:
        published_date = _parse_timestamp(document.published_at).astimezone(_TAIWAN_TZ).date()
        anchor = date.fromisoformat(report_date)
    except ValueError:
        return False
    return anchor - timedelta(days=lookback_days) <= published_date <= anchor


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
