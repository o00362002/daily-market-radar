from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from radar.application import ApplicationDependencies, DailyRadarApplication, DailyRunRequest
from radar.contracts.report import (
    CompetitorAuditV1,
    CompetitorCheckV1,
    CompetitorSourceCheckV1,
)
from radar.contracts.runtime import RuntimeContract
from radar.pipeline.ingest import ingest_fixture_documents
from radar.ports import CompetitorMonitorResult
from tests.support import (
    FakeIntelligenceEvaluator,
    FakePublisher,
    FakeSourceAdapter,
    InMemoryDocumentRepository,
    InMemoryEventRepository,
    InMemoryIndicatorRepository,
    InMemoryReportRepository,
    InMemoryStateStore,
    InMemoryUnitOfWork,
    InMemoryWebArtifactStore,
)


ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 7, 10, 1, 30, tzinfo=timezone.utc)


class FakeCompetitorMonitor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run(self, report_date: str, checked_at: str) -> CompetitorMonitorResult:
        self.calls.append((report_date, checked_at))
        source = CompetitorSourceCheckV1(
            source_id="product",
            url="https://alpha.example/product",
            channel="official_product",
            status="checked",
            checked_at=checked_at,
            http_status=200,
            etag="",
            last_modified="",
            content_hash="abc",
            previous_content_hash="",
            material_change=False,
            similarity=None,
            title="Alpha",
            excerpt="baseline",
            error="",
        )
        check = CompetitorCheckV1(
            competitor_id="alpha",
            group="global_direct_retail_action_systems",
            name="Alpha",
            market="global",
            relationship="direct",
            priority="high",
            status="baseline",
            checked_at=checked_at,
            successful_source_count=1,
            failed_source_count=0,
            fresh_material_delta=False,
            summary="baseline established",
            source_checks=[source],
        )
        audit = CompetitorAuditV1(
            registry_version="1.1",
            source_registry_version="1.0",
            checked_at=checked_at,
            fixed_target_count=1,
            checked_target_count=1,
            updated_target_count=0,
            baseline_target_count=1,
            partial_target_count=0,
            failed_target_count=0,
            not_executed_target_count=0,
            checked_ids=["alpha"],
            updated_ids=[],
            baseline_ids=["alpha"],
            partial_ids=[],
            failed_ids=[],
            not_executed_ids=[],
            checks=[check],
        )
        return CompetitorMonitorResult(
            audit=audit,
            state_key="competitor-monitor:v1",
            state_value=b'{"version":"competitor-monitor-state/v1"}\n',
        )


class CompetitorMonitorApplicationTests(unittest.TestCase):
    def test_report_and_competitor_baseline_commit_in_one_run_transaction(self) -> None:
        document_repository = InMemoryDocumentRepository()
        event_repository = InMemoryEventRepository()
        report_repository = InMemoryReportRepository()
        indicator_repository = InMemoryIndicatorRepository()
        state_store = InMemoryStateStore()
        unit_of_work = InMemoryUnitOfWork(
            document_repository=document_repository,
            event_repository=event_repository,
            report_repository=report_repository,
            indicator_repository=indicator_repository,
            state_store=state_store,
        )
        monitor = FakeCompetitorMonitor()
        dependencies = ApplicationDependencies(
            source_adapter=FakeSourceAdapter(tuple(ingest_fixture_documents())),
            evaluator=FakeIntelligenceEvaluator(finished_at=NOW.isoformat()),
            document_repository=document_repository,
            event_repository=event_repository,
            report_repository=report_repository,
            indicator_repository=indicator_repository,
            state_store=state_store,
            web_artifact_store=InMemoryWebArtifactStore(),
            unit_of_work=unit_of_work,
            publishers=(FakePublisher(),),
            competitor_monitor=monitor,
        )
        application = DailyRadarApplication(dependencies, clock=lambda: NOW)
        contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")

        result = application.run(
            DailyRunRequest(
                date="2026-07-10",
                profile="daily_push",
                ingestion_mode="fixture",
                evaluation_mode="deterministic",
            ),
            contract,
        )

        self.assertEqual(result.report.competitor_audit.baseline_ids, ["alpha"])
        self.assertEqual(result.report.source_audit.integration_status["competitor_monitor"], "healthy")
        self.assertEqual(
            state_store.load("competitor-monitor:v1"),
            b'{"version":"competitor-monitor-state/v1"}\n',
        )
        self.assertEqual(
            state_store.load("last-valid-report:daily_push"),
            result.report.canonical_json_bytes(),
        )
        self.assertEqual(len(unit_of_work.committed_batches), 1)
        self.assertEqual(monitor.calls, [("2026-07-10", NOW.isoformat())])


if __name__ == "__main__":
    unittest.main()
