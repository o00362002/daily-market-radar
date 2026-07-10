import pathlib
import unittest

from radar.runtime.contract import RuntimeContract


ROOT = pathlib.Path(__file__).resolve().parents[2]


class RuntimeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")

    def test_six_canonical_report_domains(self) -> None:
        self.assertEqual(len(self.contract.report_domains), 6)
        self.assertEqual(len(self.contract.report_domains), len(set(self.contract.report_domains)))

    def test_policy_geopolitics_maps_to_global_markets(self) -> None:
        self.assertEqual(self.contract.canonical_domain("policy_geopolitics"), "global_markets_macro")

    def test_daily_push_caps_major_but_retains_all_potential_candidates(self) -> None:
        daily = self.contract.profile("daily_push")
        self.assertEqual(daily.major_slot_cap_per_domain, 3)
        self.assertIsNone(daily.potential_slot_cap_per_domain)
        self.assertFalse(daily.slot_caps_are_completeness_proof)

    def test_required_matrices_and_indicators_exist(self) -> None:
        self.assertIn("true_vs_fake_segmentation", self.contract.retail_matrix_keys)
        self.assertIn("rwa_tokenized_assets", self.contract.crypto_matrix_keys)
        self.assertEqual(len(self.contract.structural_indicator_ids), 3)


if __name__ == "__main__":
    unittest.main()
