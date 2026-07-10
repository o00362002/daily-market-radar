import copy
import json
import pathlib
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import jsonschema

from radar.contracts.report import RadarReportV2
from radar.repositories.memory import InMemoryReportRepository
from radar.repositories.sqlite import SqliteRunRepository
from radar.runtime.contract import RuntimeContract
from radar.runtime.runs import run_daily_fixture


ROOT = pathlib.Path(__file__).resolve().parents[2]


class RuntimeV2IntegrationTests(unittest.TestCase):
    def test_fixture_run_emits_full_v2_contract(self) -> None:
        result = run_daily_fixture(
            ROOT,
            date="2026-07-10",
            freshrss_available=False,
            external_discovery_available=True,
        )
        contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")
        self.assertEqual(result.status, "partial")
        self.assertEqual(result.domains_seen, contract.report_domains)
        self.assertEqual(set(result.report["retail_matrix"]), set(contract.retail_matrix_keys))
        self.assertEqual(set(result.report["crypto_matrix"]), set(contract.crypto_matrix_keys))
        self.assertEqual(
            {row["indicator_id"] for row in result.report["structural_indicators"]},
            set(contract.structural_indicator_ids),
        )
        self.assertIn("fixture_ingestion_only", result.degradation_reasons)
        self.assertIn("freshrss_checked", result.report["source_audit"])
        self.assertIn("external_discovery_checked", result.report["source_audit"])
        canonical = RadarReportV2.from_payload(result.report)
        self.assertNotIn("freshrss_checked", canonical.source_audit.model_dump())
        serialized = json.loads(json.dumps(result.report))
        self.assertNotIn("freshrss_checked", serialized["source_audit"])
        RadarReportV2.model_validate(serialized)
        schema = json.loads((ROOT / "schemas/report.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(serialized, schema)

    def test_sqlite_persistence_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = pathlib.Path(temp_dir) / "radar.sqlite3"
            result = run_daily_fixture(
                ROOT,
                date="2026-07-10",
                freshrss_available=False,
                database_path=database,
            )
            repository = SqliteRunRepository(database, ROOT / "migrations")
            stored = repository.load_report(result.run_id)
            self.assertIsNotNone(stored)
            assert stored is not None
            self.assertEqual(stored["run_id"], result.run_id)
            self.assertEqual(stored["contract_version"], "2.0")

    def test_distinct_degradation_states_have_distinct_run_ids_and_history_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = pathlib.Path(temp_dir) / "radar.sqlite3"
            degraded = run_daily_fixture(
                ROOT,
                date="2026-07-10",
                freshrss_available=False,
                external_discovery_available=False,
                database_path=database,
            )
            available = run_daily_fixture(
                ROOT,
                date="2026-07-10",
                freshrss_available=True,
                external_discovery_available=True,
                database_path=database,
            )

            self.assertNotEqual(degraded.run_id, available.run_id)
            repository = SqliteRunRepository(database, ROOT / "migrations")
            self.assertEqual(len(repository.list_reports("daily_push")), 2)

    def test_sqlite_migrates_legacy_v2_payload_for_typed_reads(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = pathlib.Path(temp_dir) / "radar.sqlite3"
            current = run_daily_fixture(
                ROOT,
                date="2026-07-10",
                freshrss_available=False,
            ).report
            legacy = copy.deepcopy(current)
            legacy.pop("evaluation_audit")
            legacy["source_audit"] = {
                "ingestion_mode": "fixture",
                "registry_checked": True,
                "freshrss_checked": False,
                "external_discovery_checked": True,
                "candidate_retry_paths_used": [],
                "taiwan_direct_sources_checked": ["twse"],
                "remaining_gap": ["fixture data is not live source coverage"],
            }
            for observation in legacy["structural_indicators"]:
                for key in ("observation_date", "support_score", "counter_score", "evaluation_mode"):
                    observation.pop(key)

            repository = SqliteRunRepository(database, ROOT / "migrations")
            repository.save_report(legacy)

            raw = repository.load_report(legacy["run_id"])
            self.assertNotIn("evaluation_audit", raw)
            migrated = repository.get_report(f"report:{legacy['run_id']}")
            self.assertIsNotNone(migrated)
            assert migrated is not None
            self.assertEqual(migrated.evaluation_audit.validation_status, "migrated_legacy")
            self.assertEqual(migrated.source_audit.integration_status["collection_aggregator"], "unavailable")

    def test_sqlite_latest_report_uses_write_order_not_run_id_hash_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = pathlib.Path(temp_dir) / "radar.sqlite3"
            result = run_daily_fixture(
                ROOT,
                date="2026-07-10",
                freshrss_available=False,
            )
            base = RadarReportV2.from_payload(result.report)
            first = base.model_copy(update={"run_id": "run_zzzz"})
            second = base.model_copy(update={"run_id": "run_aaaa"})
            repository = SqliteRunRepository(database, ROOT / "migrations")

            class FrozenDateTime:
                @classmethod
                def now(cls, tz: object = None) -> datetime:
                    del cls, tz
                    return datetime(2026, 7, 10, 8, 0, tzinfo=timezone.utc)

                fromisoformat = staticmethod(datetime.fromisoformat)

            with patch("radar.repositories.sqlite.datetime", FrozenDateTime):
                repository.save_report(first)
                repository.save_report(second)
                repository.save_report(first)

            latest = repository.get_latest_report("daily_push")
            self.assertIsNotNone(latest)
            assert latest is not None
            self.assertEqual(latest.run_id, "run_zzzz")

    def test_memory_latest_report_uses_write_order_not_run_id_hash_order(self) -> None:
        result = run_daily_fixture(
            ROOT,
            date="2026-07-10",
            freshrss_available=False,
        )
        base = RadarReportV2.from_payload(result.report)
        repository = InMemoryReportRepository()
        repository.save_report(base.model_copy(update={"run_id": "run_zzzz"}))
        repository.save_report(base.model_copy(update={"run_id": "run_aaaa"}))

        latest = repository.get_latest_report("daily_push")
        self.assertIsNotNone(latest)
        assert latest is not None
        self.assertEqual(latest.run_id, "run_aaaa")


if __name__ == "__main__":
    unittest.main()
