from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from radar.application import ApplicationDependencies, DailyRadarApplication, DailyRunRequest
from radar.chat.context_package import build_chat_package, validate_chat_import
from radar.chat.runtime import prepare_chat
from radar.contracts.runtime import RuntimeContract
from radar.domain.models import Document
from radar.evaluators.deterministic import DeterministicIntelligenceEvaluator
from radar.repositories.sqlite import SqliteRunRepository
from radar.stores.memory import InMemoryWebArtifactStore
from tests.support import (
    FakePublisher,
    FakeSourceAdapter,
    InMemoryDocumentRepository,
    InMemoryEventRepository,
    InMemoryIndicatorRepository,
    InMemoryReportRepository,
    InMemoryStateStore,
    InMemoryUnitOfWork,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 7, 10, 1, 30, tzinfo=timezone.utc)


def _documents():
    return (
        Document.fixture(source_id="openai_news", url="https://openai.com/a", title="Lab launches agent runtime", primary_domain="ai_agents_applications", entities=["Lab"], action="launches", object="runtime", location="US", macro_region="North America", lane="bottom_up"),
        Document.fixture(source_id="twse", url="https://twse.com.tw/b", title="TWSE reports ETF flows", primary_domain="global_markets_macro", entities=["TWSE"], action="reports", object="ETF flows", location="Taiwan", macro_region="Taiwan", lane="top_down", facts={"flow_usd_m": 200}),
    )


def _run():
    contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")
    documents = _documents()
    doc_repo = InMemoryDocumentRepository()
    event_repo = InMemoryEventRepository()
    report_repo = InMemoryReportRepository()
    indicator_repo = InMemoryIndicatorRepository()
    state = InMemoryStateStore()
    deps = ApplicationDependencies(
        source_adapter=FakeSourceAdapter(documents),
        evaluator=DeterministicIntelligenceEvaluator(lambda: NOW),
        document_repository=doc_repo,
        event_repository=event_repo,
        report_repository=report_repo,
        indicator_repository=indicator_repo,
        state_store=state,
        web_artifact_store=InMemoryWebArtifactStore(),
        unit_of_work=InMemoryUnitOfWork(
            document_repository=doc_repo,
            event_repository=event_repo,
            report_repository=report_repo,
            indicator_repository=indicator_repo,
            state_store=state,
        ),
        publishers=(FakePublisher(),),
    )
    app = DailyRadarApplication(deps, clock=lambda: NOW)
    result = app.run(DailyRunRequest(date="2026-07-10", profile="daily_push", ingestion_mode="fake", evaluation_mode="chat-assisted"), contract)
    return result, contract


class ChatPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result, self.contract = _run()
        self.package = build_chat_package(self.result.report, list(self.result.events), self.contract)

    def test_package_is_byte_stable_and_content_addressed(self) -> None:
        again = build_chat_package(self.result.report, list(self.result.events), self.contract)
        self.assertEqual(self.package.files, again.files)
        self.assertEqual(self.package.context.context_hash, again.context.context_hash)
        self.assertIn("manifest.json", self.package.files)
        self.assertIn("expected-output.schema.json", self.package.files)

    def test_instructions_mandate_traditional_chinese_output(self) -> None:
        instructions = self.package.files["INSTRUCTIONS.md"].decode("utf-8")
        self.assertIn("zh-Hant-TW", instructions)
        self.assertIn("原文標題", instructions)
        context = json.loads(self.package.files["context.json"])
        self.assertEqual(context["output_language"], "zh-Hant-TW")

    def test_package_excludes_secrets_and_full_articles(self) -> None:
        blob = b"".join(self.package.files.values()).decode("utf-8")
        self.assertNotIn("OPENAI_API_KEY", blob)
        self.assertNotIn("FRESHRSS_API_PASSWORD", blob)
        # Only bounded excerpts, never a full article body.
        events = json.loads(self.package.files["events.json"])
        for event in events:
            for document in event["documents"]:
                self.assertLessEqual(len(document["excerpt"]), 280)


class PersistedChatPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result, _ = _run()

    def _write_state(self, database: Path, *, include_events: bool = True) -> None:
        repository = SqliteRunRepository(database, ROOT / "migrations")
        if include_events:
            for event in self.result.events:
                repository.save_event(event)
        repository.save_report(self.result.report)

    def test_prepare_chat_packages_persisted_report_and_events(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "radar.db"
            output = root / "out"
            self._write_state(database)

            package = prepare_chat(
                ROOT,
                date=self.result.report.date,
                profile=self.result.report.profile,
                output_root=output,
                database_path=database,
            )

            expected_ids = frozenset(item.event_id for item in self.result.report.items)
            self.assertEqual(package.context.run_id, self.result.report.run_id)
            self.assertEqual(package.context.allowed_event_ids, expected_ids)
            self.assertTrue((output / package.relative_dir / "manifest.json").exists())
            baseline = json.loads(package.files["deterministic-evaluation.json"])
            self.assertEqual(baseline["source_audit"]["ingestion_mode"], "fake")

    def test_prepare_chat_rejects_missing_persisted_report(self) -> None:
        with TemporaryDirectory() as directory:
            database = Path(directory) / "empty.db"
            with self.assertRaisesRegex(ValueError, "no persisted report"):
                prepare_chat(
                    ROOT,
                    date="2026-07-10",
                    database_path=database,
                    output_root=Path(directory) / "out",
                )

    def test_prepare_chat_rejects_report_with_missing_events(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "radar.db"
            self._write_state(database, include_events=False)
            with self.assertRaisesRegex(ValueError, "missing from durable state"):
                prepare_chat(
                    ROOT,
                    date=self.result.report.date,
                    profile=self.result.report.profile,
                    database_path=database,
                    output_root=root / "out",
                )


class ChatImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result, self.contract = _run()
        self.package = build_chat_package(self.result.report, list(self.result.events), self.contract)
        self.context = self.package.context
        self.submitted = self.result.report.model_dump(mode="json")

    def _validate(self, submitted, *, context_hash=None):
        return validate_chat_import(
            submitted,
            self.context,
            self.contract,
            claimed_context_hash=context_hash or self.context.context_hash,
        )

    def test_valid_chat_import_is_accepted(self) -> None:
        receipt = self._validate(self.submitted)
        self.assertTrue(receipt.valid, receipt.reasons)
        self.assertEqual(receipt.effective_mode, "chat-assisted")
        self.assertEqual(receipt.evaluator, "human_initiated_chat")

    def test_context_hash_mismatch_is_rejected(self) -> None:
        receipt = self._validate(self.submitted, context_hash="deadbeef")
        self.assertFalse(receipt.valid)
        self.assertIn("context_hash_mismatch", receipt.reasons)

    def test_invented_url_is_rejected(self) -> None:
        broken = copy.deepcopy(self.submitted)
        broken["items"][0]["evidence_links"][0]["url"] = "https://evil.example/hallucination"
        receipt = self._validate(broken)
        self.assertFalse(receipt.valid)
        self.assertTrue(any(reason.startswith("invented_url") for reason in receipt.reasons))

    def test_unknown_event_is_rejected(self) -> None:
        broken = copy.deepcopy(self.submitted)
        broken["items"][0]["event_id"] = "evt_hallucinated"
        receipt = self._validate(broken)
        self.assertFalse(receipt.valid)
        self.assertTrue(any(reason.startswith("unknown_event_id") for reason in receipt.reasons))

    def test_major_potential_overlap_is_rejected(self) -> None:
        broken = copy.deepcopy(self.submitted)
        if len(broken["items"]) < 2:
            self.skipTest("need at least two items for overlap")
        broken["items"][1]["event_id"] = broken["items"][0]["event_id"]
        receipt = self._validate(broken)
        self.assertFalse(receipt.valid)


if __name__ == "__main__":
    unittest.main()
