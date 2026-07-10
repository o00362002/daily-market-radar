from __future__ import annotations

from radar.domain.enums import FeedHealth


def classify_feed_health(success: bool, item_count: int, expected_nonzero: bool) -> str:
    if not success:
        return FeedHealth.FAILING.value
    if item_count == 0 and expected_nonzero:
        return FeedHealth.SILENT_ZERO.value
    if item_count == 0:
        return FeedHealth.EMPTY.value
    return FeedHealth.HEALTHY.value
