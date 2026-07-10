import pathlib
import unittest

from radar.runtime.contract import RuntimeContract
from radar.runtime.runs import run_daily_fixture


ROOT = pathlib.Path(__file__).resolve().parents[2]


class FixturePipelineTests(unittest.TestCase):
    def test_fixture_pipeline_covers_three_languages_regions_and_all_domains(self) -> None:
        result = run_daily_fixture(ROOT, date="2026-07-10", freshrss_available=False)
        contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")
        self.assertEqual(result.status, "partial")
        self.assertIn("freshrss_unavailable", result.degradation_reasons)
        self.assertGreaterEqual(len(result.languages_seen), 3)
        self.assertGreaterEqual(len(result.regions_seen), 3)
        self.assertEqual(result.domains_seen, contract.report_domains)
        self.assertTrue(result.report["coverage_gaps"])

    def test_replay_is_deterministic(self) -> None:
        first = run_daily_fixture(ROOT, date="2026-07-10", freshrss_available=False)
        second = run_daily_fixture(ROOT, date="2026-07-10", freshrss_available=False)
        self.assertEqual(first.event_ids, second.event_ids)
        self.assertEqual(first.selected_item_ids, second.selected_item_ids)

    def test_external_provider_failure_is_disclosed(self) -> None:
        result = run_daily_fixture(
            ROOT,
            date="2026-07-10",
            freshrss_available=True,
            external_discovery_available=False,
        )
        self.assertEqual(result.status, "partial")
        self.assertIn("external_discovery_unavailable", result.degradation_reasons)
        self.assertIn("external discovery unavailable", result.report["coverage_gaps"][0]["message"])


if __name__ == "__main__":
    unittest.main()
