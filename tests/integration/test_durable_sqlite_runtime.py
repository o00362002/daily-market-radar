from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from radar.application import ApplicationDependencies, DailyRadarApplication, DailyRunRequest
from radar.contracts.runtime import RuntimeContract
from radar.domain.models import Document
from radar.evaluators.deterministic import DeterministicIntelligenceEvaluator
from radar.repositories.sqlite import SqliteRunRepository
from radar.stores.memory import InMemoryWebArtifactStore
from tests.support import FakePublisher, FakeSourceAdapter


ROOT = Path(__file__).resolve().parents[2]


def _document(url: str, title: str, flow: int, fetched_at: str) -> Document:
    return Document.fixture(
        source_id="twse",
        url=url,
        title=title,
        language="zh-Hant",
        macro_region="Taiwan",
        primary_domain="global_markets_macro",
        entities=["TWSE"],
        action="reports",
        object="ETF flows",
        location="Taiwan",
        lane="top_down",
        facts={"flow_usd_m": flow},
        published_at=fetched_at,
        fetched_at=fetched_at,
    )


class DurableSqliteRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.repository = SqliteRunRepository(
            Path(self.tempdir.name) / "radar.db",
            ROOT / "migrations",
        )
        self.contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")

    def _run(self, date: str, documents: tuple[Document, ...]):
        run_now = datetime.fromisoformat(date).replace(hour=1, minute=30, second=0, microsecond=0, tzinfo=timezone.utc)
        publisher = FakePublisher()
        artifacts = InMemoryWebArtifactStore()
        dependencies = ApplicationDependencies(
            source_adapter=FakeSourceAdapter(documents, adapter_id="test-source", source_id="test-source"),
            evaluator=DeterministicIntelligenceEvaluator(lambda: run_now),
            document_repository=self.repository,
            event_repository=self.repository,
            report_repository=self.repository,
            indicator_repository=self.repository,
            state_store=self.repository,
            web_artifact_store=artifacts,
            unit_of_work=self.repository,
            publishers=(publisher,),
        )
        application = DailyRadarApplication(dependencies, clock=lambda: run_now)
        return application.run(
            DailyRunRequest(
                date=date,
                profile="daily_push",
                ingestion_mode="fake",
                evaluation_mode="deterministic",
            ),
            self.contract,
        )

    def test_sqlite_persists_documents_events_indicators_reports_and_state(self) -> None:
        document = _document(
            "https://example.tw/day-1",
            "TWSE reports ETF flows",
            200,
            "2026-07-09T08:01:00+00:00",
        )

        result = self._run("2026-07-09", (document,))
        reloaded = SqliteRunRepository(Path(self.tempdir.name) / "radar.db", ROOT / "migrations")

        self.assertEqual(reloaded.get_document(document.document_id), document)
        self.assertEqual(reloaded.find_by_canonical_url(document.url), document)
        self.assertEqual(reloaded.find_by_content_hash(document.content_hash), document)
        self.assertEqual([doc.document_id for doc in reloaded.list_recent_documents("2026-07-01")], [document.document_id])
        self.assertEqual(reloaded.get_report(result.report.report_id), result.report)
        self.assertEqual(reloaded.get_latest_report("daily_push"), result.report)
        self.assertEqual(
            len(reloaded.list_indicator_observations(self.contract.structural_indicator_ids[0])),
            1,
        )
        self.assertEqual(
            reloaded.load("last-valid-report:daily_push"),
            result.report.canonical_json_bytes(),
        )

    def test_same_day_rerun_keeps_the_days_union_reportable(self) -> None:
        """Re-running the pipeline on the same date must not shrink the day's report."""

        document = _document(
            "https://example.tw/day-1",
            "TWSE reports ETF flows",
            200,
            "2026-07-09T08:01:00+00:00",
        )
        first = self._run("2026-07-09", (document,))
        self.assertEqual(len(first.report.items), 1)

        rerun = self._run("2026-07-09", (document,))
        # The event was first seen today, so it stays in today's report even though
        # this run classified it as a duplicate observation.
        self.assertEqual(len(rerun.report.items), 1)
        self.assertEqual(rerun.report.items[0].event_id, first.report.items[0].event_id)
        self.assertEqual(rerun.events[0].first_seen_at, first.events[0].first_seen_at)

        # A true cross-day replay (no material delta on the later date) stays suppressed.
        replay = _document(
            "https://example.tw/replay",
            "TWSE reports ETF flows",
            200,
            "2026-07-10T08:01:00+00:00",
        )
        next_day = self._run("2026-07-10", (replay,))
        self.assertEqual(next_day.report.items, [])

    def test_cross_run_material_delta_uses_latest_prior_event_state(self) -> None:
        day_1 = _document(
            "https://example.tw/day-1",
            "TWSE reports ETF flows",
            200,
            "2026-07-09T08:01:00+00:00",
        )
        day_2 = _document(
            "https://example.tw/day-2",
            "TWSE updates ETF flows to 280m",
            280,
            "2026-07-10T08:01:00+00:00",
        )
        day_3_replay = _document(
            "https://example.tw/day-3",
            "TWSE updates ETF flows to 280m",
            280,
            "2026-07-11T08:01:00+00:00",
        )

        first = self._run("2026-07-09", (day_1,))
        second = self._run("2026-07-10", (day_2,))
        third = self._run("2026-07-11", (day_3_replay,))
        event_id = first.events[0].event_id
        reloaded_event = self.repository.get_event(event_id)
        assert reloaded_event is not None

        self.assertEqual(second.events[0].first_seen_at, first.events[0].first_seen_at)
        self.assertEqual(second.events[0].deltas[0].delta_type, "new_amount_or_metric")
        self.assertIn("flow_usd_m", second.events[0].deltas[0].changed_fields)
        self.assertIn("今日實質新增", second.report.items[0].today_delta)
        self.assertIn("new_amount_or_metric", second.report.items[0].today_delta)
        self.assertIn("score_explanation", second.report.items[0].model_dump(mode="json"))
        self.assertEqual(third.report.items, [])
        self.assertGreaterEqual(len(reloaded_event.documents), 3)
        self.assertEqual(
            [delta.delta_type for delta in self.repository.list_event_deltas(event_id)],
            ["new_event", "new_amount_or_metric", "duplicate_document"],
        )

    def test_failed_persistence_rolls_back_and_preserves_last_valid_report(self) -> None:
        from unittest import mock

        day_1 = _document(
            "https://example.tw/day-1",
            "TWSE reports ETF flows",
            200,
            "2026-07-09T08:01:00+00:00",
        )
        day_2 = _document(
            "https://example.tw/day-2",
            "TWSE updates ETF flows to 280m",
            280,
            "2026-07-10T08:01:00+00:00",
        )
        first = self._run("2026-07-09", (day_1,))
        first_report = self.repository.get_report(first.report.report_id)
        last_valid_before = self.repository.load("last-valid-report:daily_push")

        # Force a failure after the report row is written inside the same transaction.
        with mock.patch.object(
            SqliteRunRepository,
            "_save_state_within",
            side_effect=RuntimeError("simulated mid-transaction persistence failure"),
        ):
            with self.assertRaises(RuntimeError):
                self._run("2026-07-10", (day_2,))

        # The failed run is fully rolled back: no new report, last-valid preserved, history intact.
        self.assertEqual(len(self.repository.list_reports("daily_push")), 1)
        self.assertEqual(self.repository.get_latest_report("daily_push"), first_report)
        self.assertEqual(self.repository.load("last-valid-report:daily_push"), last_valid_before)
        event_id = first.events[0].event_id
        self.assertEqual(
            [delta.delta_type for delta in self.repository.list_event_deltas(event_id)],
            ["new_event"],
        )

    def test_commit_run_is_all_or_nothing_for_documents_and_state(self) -> None:
        document = _document(
            "https://example.tw/only",
            "TWSE reports ETF flows",
            200,
            "2026-07-09T08:01:00+00:00",
        )
        result = self._run("2026-07-09", (document,))
        # The atomic batch persisted the document, report, indicators and state together.
        self.assertIsNotNone(self.repository.get_document(document.document_id))
        self.assertEqual(
            self.repository.load("last-valid-report:daily_push"),
            result.report.canonical_json_bytes(),
        )
        self.assertTrue(
            self.repository.list_match_records(result.events[0].event_id),
            "match provenance should be persisted with the run",
        )
