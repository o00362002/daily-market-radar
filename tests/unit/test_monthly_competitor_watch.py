from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/run_monthly_competitor_watch.py"
CONFIG = ROOT / "config/competitor_monthly_watch.json"
REGISTRY = ROOT / "config/competitor_registry.json"

spec = importlib.util.spec_from_file_location("monthly_competitor_watch", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


RSS = b"""<?xml version='1.0' encoding='UTF-8'?>
<rss version='2.0'><channel><title>test</title>
<item>
<title>New agentic retail operations platform deployed across 120 stores</title>
<link>https://example.com/new-retailops</link>
<description>A retailer rollout uses a store operations agent for task execution and outcome measurement.</description>
<pubDate>Thu, 30 Jul 2026 10:00:00 GMT</pubDate>
<source>Example Retail Tech</source>
</item>
<item>
<title>Brand launches personalized shopping assistant campaign</title>
<link>https://example.com/shopping</link>
<description>Consumer marketing and product recommendations.</description>
<pubDate>Thu, 30 Jul 2026 10:00:00 GMT</pubDate>
</item>
</channel></rss>"""


class MonthlyCompetitorWatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.config["providers"] = [{"id": "fixture", "url_template": "https://example.test/?q={query}"}]
        self.config["queries"] = [
            {"id": "agentic", "theme": "agentic_retailops", "query": "agentic retail operations"}
        ]

    def test_report_selects_operational_case_and_excludes_consumer_assistant(self) -> None:
        report = module.build_report(
            config=self.config,
            registry=self.registry,
            now=datetime(2026, 7, 31, tzinfo=timezone.utc),
            fetcher=lambda _url: RSS,
        )
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["candidate_count"], 1)
        candidate = report["candidates"][0]
        self.assertEqual(candidate["category"], "retailer_case")
        self.assertIn("agentic_retailops", candidate["matched_themes"])
        self.assertIn("closed_loop_operations", candidate["matched_themes"])

    def test_partial_provider_failure_is_visible_but_not_fatal(self) -> None:
        self.config["providers"].append(
            {"id": "broken", "url_template": "https://broken.test/?q={query}"}
        )

        def fetcher(url: str) -> bytes:
            if "broken" in url:
                raise RuntimeError("network down")
            return RSS

        report = module.build_report(
            config=self.config,
            registry=self.registry,
            now=datetime(2026, 7, 31, tzinfo=timezone.utc),
            fetcher=fetcher,
        )
        self.assertEqual(report["status"], "partial")
        self.assertEqual(report["failed_source_check_count"], 1)
        self.assertEqual(report["candidate_count"], 1)

    def test_all_provider_failures_return_diagnostic_report(self) -> None:
        report = module.build_report(
            config=self.config,
            registry=self.registry,
            now=datetime(2026, 7, 31, tzinfo=timezone.utc),
            fetcher=lambda _url: (_ for _ in ()).throw(RuntimeError("blocked")),
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["candidate_count"], 0)
        self.assertEqual(report["successful_source_check_count"], 0)


if __name__ == "__main__":
    unittest.main()
