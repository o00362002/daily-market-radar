from __future__ import annotations

import unittest

from radar.domain.models import Document
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deltas import material_events
from radar.pipeline.freshness import document_is_in_report_window, filter_documents_by_freshness


REPORT_DATE = "2026-07-25"
OBSERVED_AT = "2026-07-25T07:00:00+08:00"


def document(*, published_at: str, suffix: str = "a") -> Document:
    return Document.fixture(
        source_id="feed",
        url=f"https://example.com/{suffix}",
        title=f"Story {suffix}",
        published_at=published_at,
        fetched_at=OBSERVED_AT,
        entities=[f"Entity {suffix}"],
        action="reports",
        object="update",
    )


class FreshnessFilterTests(unittest.TestCase):
    def test_current_taiwan_day_is_reportable(self) -> None:
        row = document(published_at="2026-07-25T01:00:00+08:00")
        self.assertTrue(document_is_in_report_window(row, REPORT_DATE))
        self.assertEqual(material_events(cluster_documents([row]), report_date=REPORT_DATE)[0].documents[0], row)

    def test_previous_taiwan_day_is_kept_for_global_sessions(self) -> None:
        row = document(published_at="2026-07-24T03:00:00-04:00")
        self.assertTrue(document_is_in_report_window(row, REPORT_DATE))
        self.assertEqual(len(material_events(cluster_documents([row]), report_date=REPORT_DATE)), 1)

    def test_archive_entry_older_than_one_prior_day_is_rejected(self) -> None:
        row = document(published_at="2026-07-22T12:00:00+00:00")
        self.assertFalse(document_is_in_report_window(row, REPORT_DATE))
        self.assertEqual(material_events(cluster_documents([row]), report_date=REPORT_DATE), [])

    def test_invalid_timestamp_is_not_treated_as_fetched_today(self) -> None:
        row = document(published_at="not-a-date")
        result = filter_documents_by_freshness([row], observed_at=OBSERVED_AT)
        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected_invalid_timestamp, [row])
        self.assertFalse(document_is_in_report_window(row, REPORT_DATE))

    def test_hour_window_rejects_old_and_future_documents(self) -> None:
        fresh = document(published_at="2026-07-24T12:00:00+08:00", suffix="fresh")
        stale = document(published_at="2026-07-22T12:00:00+08:00", suffix="stale")
        future = document(published_at="2026-07-25T12:00:00+08:00", suffix="future")
        result = filter_documents_by_freshness([fresh, stale, future], observed_at=OBSERVED_AT)
        self.assertEqual(result.accepted, [fresh])
        self.assertEqual(result.rejected_stale, [stale])
        self.assertEqual(result.rejected_future, [future])


if __name__ == "__main__":
    unittest.main()
