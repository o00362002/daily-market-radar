import json
import pathlib
import unittest
from urllib.parse import urlsplit

from radar.schemas.competitor import CompetitorMonitoringRegistry


ROOT = pathlib.Path(__file__).resolve().parents[2]


class CompetitorRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(
            (ROOT / "config/competitor_registry.json").read_text(encoding="utf-8")
        )
        self.source_payload = json.loads(
            (ROOT / "config/competitor_sources.json").read_text(encoding="utf-8")
        )

    def test_registry_has_focused_groups_in_explicit_order(self) -> None:
        expected = [
            "global_direct_retail_action_systems",
            "global_adjacent_execution_platforms",
            "taiwan_adjacent_retail_platforms",
            "global_enabling_platform_threats",
            "social_and_content",
        ]
        self.assertEqual(self.payload["group_order"], expected)
        self.assertEqual(set(self.payload["groups"]), set(expected))

    def test_registry_has_unique_ids_and_relationship_metadata(self) -> None:
        groups = self.payload["groups"]
        entries = [entry for group in groups.values() for entry in group]
        ids = [entry["id"] for entry in entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(entry["aliases"] for entry in entries))
        self.assertTrue(all(entry["market"] in {"global", "taiwan", "mixed"} for entry in entries))
        self.assertTrue(all(entry["relationship"] in {"direct", "adjacent", "enabling", "content"} for entry in entries))

    def test_research_direct_and_adjacent_vendors_are_tracked(self) -> None:
        groups = self.payload["groups"]
        direct_ids = {entry["id"] for entry in groups["global_direct_retail_action_systems"]}
        adjacent_ids = {entry["id"] for entry in groups["global_adjacent_execution_platforms"]}
        self.assertEqual(direct_ids, {"storee", "quorso", "workjam", "hubler"})
        self.assertTrue({"yoobic", "zipline_retail", "retail_coach_io", "pipefy_retail"}.issubset(adjacent_ids))

    def test_broad_platforms_are_not_fixed_competitor_projection(self) -> None:
        entries = [entry for group in self.payload["groups"].values() for entry in group]
        ids = {entry["id"] for entry in entries}
        self.assertTrue({"microsoft_copilot_dynamics", "workato", "shopify_retail"}.issubset(ids))
        self.assertTrue({"google_cloud", "aws", "adobe", "sap", "oracle", "servicenow", "salesforce"}.isdisjoint(ids))

    def test_ambiguous_aliases_require_operational_context(self) -> None:
        entries = [entry for group in self.payload["groups"].values() for entry in group]
        by_id = {entry["id"]: entry for entry in entries}
        for competitor_id in ("zipline_retail", "retail_coach_io", "pipefy_retail", "shopify_retail"):
            self.assertTrue(by_id[competitor_id].get("requires_any"), competitor_id)
        self.assertNotIn("ACT", by_id["act_retail"]["aliases"])

    def test_competitor_watch_is_cross_domain_projection(self) -> None:
        self.assertEqual(self.payload["tracking_mode"], "cross_domain_projection")
        self.assertEqual(self.payload["focus"], "retail_action_layer")
        self.assertIn("does not create a new canonical report-domain quota", self.payload["report_domain_policy"])
        self.assertIn("headline and today_delta", self.payload["matching_policy"])
        self.assertIn("competitor_group", self.payload["analysis_fields"])
        self.assertIn("recommended_action", self.payload["analysis_fields"])

    def test_every_fixed_product_competitor_has_executable_official_sources(self) -> None:
        excluded = set(self.source_payload["excluded_registry_groups"])
        expected_ids = {
            entry["id"]
            for group, entries in self.payload["groups"].items()
            if group not in excluded
            for entry in entries
        }
        self.assertEqual(set(self.source_payload["sources"]), expected_ids)
        for competitor_id, sources in self.source_payload["sources"].items():
            self.assertTrue(sources, competitor_id)
            source_ids = [source["id"] for source in sources]
            self.assertEqual(len(source_ids), len(set(source_ids)), competitor_id)
            for source in sources:
                parts = urlsplit(source["url"])
                self.assertEqual(parts.scheme, "https", source["url"])
                self.assertTrue(parts.netloc, source["url"])

    def test_typed_monitoring_registry_loads_and_validates(self) -> None:
        registry = CompetitorMonitoringRegistry.from_files(
            ROOT / "config/competitor_registry.json",
            ROOT / "config/competitor_sources.json",
        )
        self.assertEqual(len(registry.targets), 21)
        self.assertEqual(registry.state_key, "competitor-monitor:v1")
        self.assertTrue(all(target.sources for target in registry.targets))


if __name__ == "__main__":
    unittest.main()
