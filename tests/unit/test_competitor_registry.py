import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class CompetitorRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(
            (ROOT / "config/competitor_registry.json").read_text(encoding="utf-8")
        )

    def test_registry_has_required_groups_and_unique_ids(self) -> None:
        groups = self.payload["groups"]
        self.assertEqual(
            set(groups),
            {"taiwan_retailops_products", "global_platforms", "social_and_content"},
        )
        entries = [entry for group in groups.values() for entry in group]
        ids = [entry["id"] for entry in entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(entry["aliases"] for entry in entries))

    def test_competitor_watch_is_cross_domain_projection(self) -> None:
        self.assertEqual(self.payload["tracking_mode"], "cross_domain_projection")
        self.assertIn("does not create a new canonical report-domain quota", self.payload["report_domain_policy"])
        self.assertIn("fresh_material_delta", self.payload["analysis_fields"])
        self.assertIn("recommended_action", self.payload["analysis_fields"])


if __name__ == "__main__":
    unittest.main()
