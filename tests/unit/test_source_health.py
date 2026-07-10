from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from radar.domain.source_health import (
    FetchObservation,
    SourceHealthRecord,
    SourceHealthStatus,
    evaluate_health,
    with_source_id,
)
from radar.repositories.source_health import SqliteSourceHealthRepository

ROOT = Path(__file__).resolve().parents[2]


def _obs(**kwargs) -> FetchObservation:
    base = dict(ok=True, item_count=1, latency_ms=100, checked_at="2026-07-10T08:00:00+00:00", latest_item_at="2026-07-10T07:00:00+00:00")
    base.update(kwargs)
    return FetchObservation(**base)


class SourceHealthTransitionTests(unittest.TestCase):
    def test_healthy_when_items_returned(self) -> None:
        record = evaluate_health(None, _obs(), freshness_slo_minutes=180)
        self.assertEqual(record.status, SourceHealthStatus.HEALTHY.value)
        self.assertEqual(record.consecutive_failures, 0)
        self.assertEqual(record.response_count, 1)

    def test_empty_when_never_seen_an_item(self) -> None:
        record = evaluate_health(None, _obs(item_count=0, latest_item_at=""), freshness_slo_minutes=180)
        self.assertEqual(record.status, SourceHealthStatus.EMPTY.value)

    def test_silent_zero_when_recent_prior_item_but_zero_now(self) -> None:
        prior = SourceHealthRecord(source_id="s", status="healthy", checked_at="2026-07-10T07:00:00+00:00", last_item_at="2026-07-10T07:30:00+00:00")
        record = evaluate_health(prior, _obs(item_count=0, checked_at="2026-07-10T08:00:00+00:00"), freshness_slo_minutes=180)
        self.assertEqual(record.status, SourceHealthStatus.SILENT_ZERO.value)

    def test_stale_when_zero_items_past_freshness_slo(self) -> None:
        prior = SourceHealthRecord(source_id="s", status="healthy", checked_at="2026-07-01T00:00:00+00:00", last_item_at="2026-07-01T00:00:00+00:00")
        record = evaluate_health(prior, _obs(item_count=0, checked_at="2026-07-10T00:00:00+00:00"), freshness_slo_minutes=180)
        self.assertEqual(record.status, SourceHealthStatus.STALE.value)

    def test_failing_increments_consecutive_failures_and_sets_retry(self) -> None:
        prior = SourceHealthRecord(source_id="s", status="failing", checked_at="2026-07-10T07:00:00+00:00", consecutive_failures=1)
        record = evaluate_health(prior, _obs(ok=False, item_count=0, failure_reason="timeout"), freshness_slo_minutes=180)
        self.assertEqual(record.status, SourceHealthStatus.FAILING.value)
        self.assertEqual(record.consecutive_failures, 2)
        self.assertTrue(record.retry_at)
        self.assertEqual(record.failure_reason, "timeout")

    def test_policy_credential_and_rate_limit_states(self) -> None:
        self.assertEqual(
            evaluate_health(None, _obs(ok=False, policy_blocked=True), freshness_slo_minutes=180).status,
            SourceHealthStatus.POLICY_BLOCKED.value,
        )
        self.assertEqual(
            evaluate_health(None, _obs(ok=False, credential_unavailable=True), freshness_slo_minutes=180).status,
            SourceHealthStatus.CREDENTIAL_UNAVAILABLE.value,
        )
        rate = evaluate_health(None, _obs(ok=False, rate_limited=True, retry_after_seconds=42), freshness_slo_minutes=180)
        self.assertEqual(rate.status, SourceHealthStatus.RATE_LIMITED.value)
        self.assertTrue(rate.retry_at)


class DurableSourceHealthTests(unittest.TestCase):
    def test_upsert_and_reload_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SqliteSourceHealthRepository(Path(tmp) / "radar.db", ROOT / "migrations")
            record = with_source_id(evaluate_health(None, _obs(), freshness_slo_minutes=180), "feed_source")
            repo.upsert(record)
            repo.upsert(with_source_id(evaluate_health(repo.get("feed_source"), _obs(ok=False, item_count=0, failure_reason="boom"), freshness_slo_minutes=180), "feed_source"))

            reloaded = SqliteSourceHealthRepository(Path(tmp) / "radar.db", ROOT / "migrations")
            current = reloaded.get("feed_source")
            self.assertIsNotNone(current)
            assert current is not None
            self.assertEqual(current.status, "failing")
            self.assertEqual(current.consecutive_failures, 1)
            self.assertEqual(current.response_count, 2)
            self.assertEqual([r.source_id for r in reloaded.list_all()], ["feed_source"])


if __name__ == "__main__":
    unittest.main()
