from __future__ import annotations

import builtins
import os
import pathlib
import socket
import sqlite3
import sys
import unittest
import urllib.request
from collections.abc import Sequence
from contextlib import ExitStack, contextmanager
from dataclasses import replace
from datetime import datetime, timezone
from unittest import mock

from radar.application import ApplicationDependencies, DailyRadarApplication, DailyRunRequest
from radar.contracts.evaluation import EvaluationRequest, EvaluationResult
from radar.contracts.report import RadarReportV2
from radar.contracts.runtime import ProfileContract, RuntimeContract
from radar.contracts.web import PublicationReceiptV1, WebArtifactV1
from radar.domain.models import Document
from radar.ports import (
    IntelligenceEvaluator,
    ReportPublisher,
    ReportRepository,
    SourceAdapter,
    StateStore,
    WebArtifactStore,
)
from radar.reporting.contracts import validate_report_contract
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


FIXED_NOW = datetime(2026, 7, 10, 1, 30, tzinfo=timezone.utc)
REPORT_DATE = "2026-07-10"


def _contract() -> RuntimeContract:
    return RuntimeContract(
        report_domains=[
            "global_markets_macro",
            "ai_agents_applications",
            "crypto_rwa_agent_payments",
            "retail_consumer_fashion",
            "science_technology_industry",
            "labor_demographics_consumption_pressure",
        ],
        domain_aliases={"policy_geopolitics": "global_markets_macro"},
        profiles={
            # Test-contract floors sized to what the fake documents yield so the
            # baseline status stays "complete"; floor-shortfall behavior has its
            # own dedicated assertions.
            "daily_push": ProfileContract(
                min_major_items=3,
                min_potential_items=2,
                min_taiwan_items=1,
            ),
            "full": ProfileContract(
                min_major_items=4,
                min_potential_items=2,
                min_taiwan_items=1,
            ),
        },
        completion_requires=[],
        structural_indicator_ids=[
            "k_shaped_ai_productivity_economy",
            "ai_bubble_overinvestment",
            "brand_market_polarization_and_true_vs_fake_segmentation",
        ],
        retail_matrix_keys=["retail_channel", "retail_segmentation"],
        crypto_matrix_keys=["crypto_market_structure", "crypto_regulation"],
        required_backtest_counters=[
            "duplicate_rejection_count",
            "field_overlap_rejection_count",
            "niche_low_novelty_rejection_count",
            "candidate_retry_paths_used",
            "taiwan_qualified_item_count_after_audit",
            "taiwan_direct_sources_checked",
        ],
    )


def _documents() -> tuple[Document, ...]:
    rows = [
        (
            "macro-official",
            "https://example.com/macro",
            "Policy authority publishes a market update",
            "global_markets_macro",
            "Authority",
            "publishes",
            "market update",
            "Global",
            "North America",
            "top_down",
        ),
        (
            "ai-lab",
            "https://example.com/ai",
            "Lab launches an agent runtime",
            "ai_agents_applications",
            "Lab",
            "launches",
            "agent runtime",
            "US",
            "North America",
            "top_down",
        ),
        (
            "crypto-builder",
            "https://example.com/crypto",
            "Builder pilots tokenized settlement",
            "crypto_rwa_agent_payments",
            "Builder",
            "pilots",
            "tokenized settlement",
            "Singapore",
            "Southeast Asia",
            "bottom_up",
        ),
        (
            "taiwan-retail",
            "https://example.com/taiwan-retail",
            "Taiwan retailer tests a neighborhood format",
            "retail_consumer_fashion",
            "Taiwan Retailer",
            "tests",
            "neighborhood format",
            "Taiwan",
            "Taiwan",
            "bottom_up",
        ),
        (
            "science-journal",
            "https://example.com/science",
            "Researchers release a robotics result",
            "science_technology_industry",
            "Researchers",
            "release",
            "robotics result",
            "Japan",
            "East Asia",
            "top_down",
        ),
        (
            "labor-office",
            "https://example.com/labor",
            "Labor office reports wage changes",
            "labor_demographics_consumption_pressure",
            "Labor Office",
            "reports",
            "wage changes",
            "Europe",
            "Europe",
            "top_down",
        ),
    ]
    return tuple(
        Document.fixture(
            source_id=source_id,
            url=url,
            title=title,
            primary_domain=domain,
            entities=[entity],
            action=action,
            object=obj,
            location=location,
            macro_region=region,
            lane=lane,
            published_at="2026-07-10T08:00:00+00:00",
            fetched_at="2026-07-10T08:01:00+00:00",
        )
        for source_id, url, title, domain, entity, action, obj, location, region, lane in rows
    )


@contextmanager
def _external_io_forbidden():
    def blocked(operation: str):
        def fail(*args: object, **kwargs: object) -> None:
            del args, kwargs
            raise AssertionError(f"fake-only flow attempted {operation}")

        return fail

    real_import = builtins.__import__

    def guarded_import(name: str, *args: object, **kwargs: object):
        if name == "openai" or name.startswith("openai."):
            raise AssertionError("fake-only flow attempted to import OpenAI")
        return real_import(name, *args, **kwargs)

    patches = [
        mock.patch("builtins.open", side_effect=blocked("builtins.open")),
        mock.patch("builtins.__import__", side_effect=guarded_import),
        mock.patch.object(pathlib.Path, "open", side_effect=blocked("Path.open")),
        mock.patch.object(pathlib.Path, "read_text", side_effect=blocked("Path.read_text")),
        mock.patch.object(pathlib.Path, "write_text", side_effect=blocked("Path.write_text")),
        mock.patch.object(pathlib.Path, "mkdir", side_effect=blocked("Path.mkdir")),
        mock.patch.object(pathlib.Path, "replace", side_effect=blocked("Path.replace")),
        mock.patch.object(pathlib.Path, "unlink", side_effect=blocked("Path.unlink")),
        mock.patch.object(os, "open", side_effect=blocked("os.open")),
        mock.patch.object(os, "replace", side_effect=blocked("os.replace")),
        mock.patch.object(sqlite3, "connect", side_effect=blocked("sqlite3.connect")),
        mock.patch.object(socket.socket, "connect", side_effect=blocked("socket.connect")),
        mock.patch.object(socket, "create_connection", side_effect=blocked("socket.create_connection")),
        mock.patch.object(socket, "getaddrinfo", side_effect=blocked("socket.getaddrinfo")),
        mock.patch.object(urllib.request, "urlopen", side_effect=blocked("urllib.request.urlopen")),
    ]
    with ExitStack() as stack:
        for patcher in patches:
            stack.enter_context(patcher)
        yield


class ListBackedReportRepository:
    """Second report storage shape used to prove structural replacement."""

    def __init__(self) -> None:
        self.saved: list[RadarReportV2] = []

    def save_report(self, report: RadarReportV2) -> None:
        self.saved.append(report)

    def get_report(self, report_id: str) -> RadarReportV2 | None:
        return next((report for report in self.saved if report.report_id == report_id), None)

    def get_report_by_date(self, report_date: str, profile: str) -> RadarReportV2 | None:
        matches = [report for report in self.saved if report.date == report_date and report.profile == profile]
        return matches[-1] if matches else None

    def get_latest_report(self, profile: str | None = None) -> RadarReportV2 | None:
        matches = self.list_reports(profile)
        return matches[-1] if matches else None

    def list_reports(self, profile: str | None = None) -> list[RadarReportV2]:
        return sorted(
            (report for report in self.saved if profile is None or report.profile == profile),
            key=lambda report: (report.date, report.run_id),
        )


class JournalStateStore:
    def __init__(self) -> None:
        self.entries: list[tuple[str, bytes]] = []

    def load(self, key: str) -> bytes | None:
        return next((value for entry_key, value in reversed(self.entries) if entry_key == key), None)

    def save(self, key: str, value: bytes) -> None:
        self.entries.append((key, bytes(value)))


class BatchWebArtifactStore:
    def __init__(self) -> None:
        self.batches: list[tuple[WebArtifactV1, ...]] = []

    def read(self, path: str) -> WebArtifactV1 | None:
        return next(
            (
                artifact
                for batch in reversed(self.batches)
                for artifact in batch
                if artifact.path == path
            ),
            None,
        )

    def commit(self, artifacts: Sequence[WebArtifactV1]) -> None:
        self.batches.append(tuple(artifacts))


class ArtifactAuditPublisher:
    publisher_id = "artifact-audit"

    def __init__(self) -> None:
        self.calls: list[tuple[RadarReportV2, tuple[WebArtifactV1, ...]]] = []

    def publish(
        self,
        report: RadarReportV2,
        artifacts: Sequence[WebArtifactV1],
    ) -> PublicationReceiptV1:
        if not isinstance(report, RadarReportV2):
            raise TypeError("expected a validated RadarReportV2")
        typed_artifacts = tuple(artifacts)
        if not all(isinstance(artifact, WebArtifactV1) for artifact in typed_artifacts):
            raise TypeError("expected typed web artifacts")
        self.calls.append((report, typed_artifacts))
        return PublicationReceiptV1(
            publisher_id=self.publisher_id,
            status="audited",
            artifact_paths=[artifact.path for artifact in typed_artifacts],
        )


class InvalidOverlapEvaluator(FakeIntelligenceEvaluator):
    """Produces typed items that fail the report's cross-field lane invariant."""

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        result = super().evaluate(request)
        major = next(item for item in result.items if item.report_lane == "major")
        items = list(result.items)
        potential_index = next(index for index, item in enumerate(items) if item.report_lane == "potential")
        items[potential_index] = items[potential_index].model_copy(update={"event_id": major.event_id})
        return replace(result, items=tuple(items))


class FakeOnlyApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = _contract()
        self.documents = _documents()
        self.request = DailyRunRequest(
            date=REPORT_DATE,
            profile="daily_push",
            ingestion_mode="fake",
            evaluation_mode="deterministic",
        )

    def _build_application(
        self,
        *,
        source_adapter: SourceAdapter | None = None,
        evaluator: IntelligenceEvaluator | None = None,
        report_repository: ReportRepository | None = None,
        state_store: StateStore | None = None,
        web_artifact_store: WebArtifactStore | None = None,
        publishers: tuple[ReportPublisher, ...] | None = None,
    ) -> tuple[DailyRadarApplication, ApplicationDependencies]:
        document_repository = InMemoryDocumentRepository()
        event_repository = InMemoryEventRepository()
        resolved_report_repository = report_repository if report_repository is not None else InMemoryReportRepository()
        indicator_repository = InMemoryIndicatorRepository()
        resolved_state_store = state_store if state_store is not None else InMemoryStateStore()
        dependencies = ApplicationDependencies(
            source_adapter=source_adapter if source_adapter is not None else FakeSourceAdapter(self.documents),
            evaluator=(
                evaluator
                if evaluator is not None
                else FakeIntelligenceEvaluator(finished_at=FIXED_NOW.isoformat())
            ),
            document_repository=document_repository,
            event_repository=event_repository,
            report_repository=resolved_report_repository,
            indicator_repository=indicator_repository,
            state_store=resolved_state_store,
            web_artifact_store=(
                web_artifact_store if web_artifact_store is not None else InMemoryWebArtifactStore()
            ),
            unit_of_work=InMemoryUnitOfWork(
                document_repository=document_repository,
                event_repository=event_repository,
                report_repository=resolved_report_repository,
                indicator_repository=indicator_repository,
                state_store=resolved_state_store,
            ),
            publishers=publishers if publishers is not None else (FakePublisher(),),
        )
        return DailyRadarApplication(dependencies, clock=lambda: FIXED_NOW), dependencies

    def test_unmet_floor_degrades_to_partial_with_declared_reason(self) -> None:
        """Floors are disclosure targets: below the floor -> partial + below_minimum_*."""

        from dataclasses import replace as dc_replace

        from radar.contracts.runtime import ProfileContract

        demanding = dc_replace(
            self.contract,
            profiles={
                **self.contract.profiles,
                "daily_push": ProfileContract(
                    min_major_items=50,  # unreachable for the fake documents
                    min_potential_items=2,
                    min_taiwan_items=1,
                ),
            },
        )
        application, _ = self._build_application()
        result = application.run(self.request, demanding)

        self.assertEqual(result.report.status, "partial")
        self.assertIn("below_minimum_major", result.report.degradation_reasons)
        self.assertTrue(
            any(gap.reason == "below_minimum_major" for gap in result.report.coverage_gaps)
        )
        # Still a valid report — an unmet floor never fails the run.
        validate_report_contract(result.report.model_dump(mode="json"), contract=demanding)
        # No ceiling: every qualified item is retained despite the huge floor.
        self.assertEqual(len(result.report.items), len(self.documents))

    def test_full_flow_runs_with_fakes_and_external_io_disabled(self) -> None:
        application, dependencies = self._build_application()
        openai_modules_before = {
            name for name in sys.modules if name == "openai" or name.startswith("openai.")
        }

        with _external_io_forbidden():
            result = application.run(self.request, self.contract)

        openai_modules_after = {
            name for name in sys.modules if name == "openai" or name.startswith("openai.")
        }
        self.assertEqual(openai_modules_after, openai_modules_before)
        self.assertIsInstance(result.report, RadarReportV2)
        validate_report_contract(result.report.model_dump(mode="json"), contract=self.contract)
        self.assertEqual(result.report.status, "complete")
        self.assertEqual(len(result.documents), len(self.documents))
        self.assertEqual(len(result.events), len(self.documents))

        source = dependencies.source_adapter
        self.assertEqual(len(source.fetch_requests), 1)
        self.assertEqual(len(source.normalize_calls), 1)
        self.assertGreaterEqual(source.credentials_status_calls, 2)
        self.assertEqual(source.health_check_calls, 1)

        document_repository = dependencies.document_repository
        self.assertEqual(set(document_repository.documents), {document.document_id for document in self.documents})
        event_repository = dependencies.event_repository
        self.assertEqual(event_repository.recent_queries, ["2026-06-10T00:00:00+00:00"])
        self.assertEqual(set(event_repository.events), {event.event_id for event in result.events})
        self.assertTrue(all(event_repository.event_documents[event.event_id] for event in result.events))

        evaluator = dependencies.evaluator
        self.assertEqual(len(evaluator.requests), 1)
        self.assertEqual(
            {event.event_id for event in evaluator.requests[0].events},
            {event.event_id for event in result.events},
        )
        report_repository = dependencies.report_repository
        self.assertIs(report_repository.get_latest_report("daily_push"), result.report)
        indicator_repository = dependencies.indicator_repository
        self.assertEqual(len(indicator_repository.save_calls), len(self.contract.structural_indicator_ids))

        expected_state = result.report.canonical_json_bytes()
        self.assertEqual(dependencies.state_store.load("last-valid-report:daily_push"), expected_state)
        self.assertEqual(dependencies.web_artifact_store.read("latest.json").content, expected_state)
        self.assertEqual(len(result.artifacts), 2)
        self.assertEqual(len(result.publications), 1)
        publisher = dependencies.publishers[0]
        self.assertEqual(publisher.calls, [(result.report, result.artifacts)])

    def test_fake_only_replay_is_byte_deterministic(self) -> None:
        first_application, _ = self._build_application()
        second_application, _ = self._build_application()

        with _external_io_forbidden():
            first = first_application.run(self.request, self.contract)
            second = second_application.run(self.request, self.contract)

        self.assertEqual(first.report.canonical_json_bytes(), second.report.canonical_json_bytes())
        self.assertEqual(first.artifacts, second.artifacts)
        self.assertEqual(first.publications, second.publications)
        self.assertEqual(
            [event.event_id for event in first.events],
            [event.event_id for event in second.events],
        )

    def test_unfamiliar_source_adapter_needs_no_downstream_special_case(self) -> None:
        class FutureSourceAdapter(FakeSourceAdapter):
            pass

        source = FutureSourceAdapter(
            tuple(reversed(self.documents)),
            adapter_id="future-source-v99",
            source_id="future-source",
        )
        application, dependencies = self._build_application(source_adapter=source)

        result = application.run(self.request, self.contract)

        self.assertEqual(len(result.events), len(self.documents))
        self.assertEqual(result.report.source_audit.integration_status["future-source-v99"], "healthy")
        self.assertEqual(len(dependencies.report_repository.list_reports()), 1)
        self.assertIsNotNone(dependencies.web_artifact_store.read("latest.json"))
        self.assertEqual(len(dependencies.publishers[0].calls), 1)

    def test_evaluator_can_be_replaced_without_changing_ingestion_events_or_projection(self) -> None:
        baseline_application, _ = self._build_application(
            evaluator=FakeIntelligenceEvaluator(
                evaluator_id="evaluator-a",
                finished_at=FIXED_NOW.isoformat(),
            )
        )
        replacement_application, replacement_dependencies = self._build_application(
            evaluator=FakeIntelligenceEvaluator(
                evaluator_id="evaluator-b",
                headline_prefix="[alternate] ",
                score_delta=1,
                finished_at=FIXED_NOW.isoformat(),
            )
        )

        baseline = baseline_application.run(self.request, self.contract)
        replacement = replacement_application.run(self.request, self.contract)

        self.assertEqual(
            [document.document_id for document in baseline.documents],
            [document.document_id for document in replacement.documents],
        )
        self.assertEqual(
            [event.event_id for event in baseline.events],
            [event.event_id for event in replacement.events],
        )
        self.assertTrue(all(item.headline.startswith("[alternate] ") for item in replacement.report.items))
        self.assertEqual(replacement.report.evaluation_audit.evaluator, "evaluator-b")
        latest = replacement_dependencies.web_artifact_store.read("latest.json")
        self.assertEqual(latest.content, replacement.report.canonical_json_bytes())

    def test_report_state_and_web_storage_backends_are_replaceable(self) -> None:
        report_repository = ListBackedReportRepository()
        state_store = JournalStateStore()
        web_artifact_store = BatchWebArtifactStore()
        self.assertIsInstance(report_repository, ReportRepository)
        self.assertIsInstance(state_store, StateStore)
        self.assertIsInstance(web_artifact_store, WebArtifactStore)
        application, _ = self._build_application(
            report_repository=report_repository,
            state_store=state_store,
            web_artifact_store=web_artifact_store,
        )

        result = application.run(self.request, self.contract)

        self.assertEqual(report_repository.saved, [result.report])
        self.assertEqual(state_store.load("last-valid-report:daily_push"), result.report.canonical_json_bytes())
        self.assertEqual(web_artifact_store.read("latest.json").content, result.report.canonical_json_bytes())

    def test_publisher_can_be_replaced_and_receives_only_validated_artifacts(self) -> None:
        publisher = ArtifactAuditPublisher()
        self.assertIsInstance(publisher, ReportPublisher)
        application, _ = self._build_application(publishers=(publisher,))

        result = application.run(self.request, self.contract)

        self.assertEqual(publisher.calls, [(result.report, result.artifacts)])
        self.assertEqual(result.publications[0].publisher_id, "artifact-audit")
        self.assertEqual(result.publications[0].artifact_paths, [artifact.path for artifact in result.artifacts])

    def test_cross_field_invalid_report_never_reaches_output_ports(self) -> None:
        report_repository = InMemoryReportRepository()
        state_store = InMemoryStateStore()
        web_artifact_store = InMemoryWebArtifactStore()
        publisher = FakePublisher()
        application, dependencies = self._build_application(
            evaluator=InvalidOverlapEvaluator(finished_at=FIXED_NOW.isoformat()),
            report_repository=report_repository,
            state_store=state_store,
            web_artifact_store=web_artifact_store,
            publishers=(publisher,),
        )

        with self.assertRaisesRegex(ValueError, "same event cannot fill major and potential lanes"):
            application.run(self.request, self.contract)

        self.assertEqual(report_repository.reports, {})
        self.assertEqual(dependencies.indicator_repository.save_calls, [])
        self.assertEqual(state_store.values, {})
        self.assertEqual(web_artifact_store.artifacts, {})
        self.assertEqual(publisher.calls, [])


if __name__ == "__main__":
    unittest.main()
