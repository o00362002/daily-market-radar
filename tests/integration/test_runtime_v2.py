import pathlib
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
