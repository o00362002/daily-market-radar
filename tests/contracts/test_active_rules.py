import pathlib
import re
import unittest

from radar.reporting.contracts import validate_report_contract
from radar.schemas.source import SourceRegistry


ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFLICTING_QUOTA_RE = re.compile(r"\b(?:3\+1|5\+3|3\+3|5\+5)\b")
ACTIVE_GLOBS = [
    "AGENTS.md",
    "CURRENT_STATE.md",
    "CURRENT_DECISIONS.md",
    "DEPENDENCY_MAP.md",
    "AGENT_DEFINITION_MAP.md",
    "configs/*.yml",
    "templates/*.md",
    "workflows/*.md",
]


class ActiveRulesContractTests(unittest.TestCase):
    def test_active_rules_do_not_use_legacy_quota_completion_terms(self) -> None:
        offenders = []
        for pattern in ACTIVE_GLOBS:
            for path in ROOT.glob(pattern):
                text = path.read_text(encoding="utf-8")
                if CONFLICTING_QUOTA_RE.search(text):
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_source_registry_opml_projection_is_current(self) -> None:
        registry = SourceRegistry.from_file(ROOT / "config/source_registry.yaml")
        registry.validate()
        self.assertEqual(registry.to_opml(), (ROOT / "FRESHRSS_SEEDS.opml").read_text(encoding="utf-8"))

    def test_daily_push_fixture_contract_shape(self) -> None:
        fixture = {
            "items": [
                {
                    "item_id": "item_fixture",
                    "event_id": "evt_fixture",
                    "signal_id": None,
                    "primary_domain": "ai_agents_applications",
                    "headline": "Fixture headline",
                    "first_seen_at": "2026-07-10T08:00:00+08:00",
                    "today_delta": "New product release.",
                    "importance_score": 70,
                    "potential_score": 55,
                    "confidence_score": 80,
                    "evidence_links": [
                        {
                            "url": "https://openai.com/news/rss.xml",
                            "source_id": "openai_news",
                            "fetched_at": "2026-07-10T08:01:00+08:00",
                        }
                    ],
                    "direct_taiwan_evidence": [],
                    "taiwan_implication": "No direct Taiwan evidence.",
                    "counterevidence": [],
                    "uncertainties": ["fixture"],
                    "next_watch": "Watch follow-up releases.",
                }
            ],
            "coverage_gaps": [],
        }
        validate_report_contract(fixture)


if __name__ == "__main__":
    unittest.main()
