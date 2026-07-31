from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "production_quality_gate",
    ROOT / "tools" / "check_production_quality.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


CONFIG = {
    "report": {
        "minimum_total_items": 1,
        "review_thresholds": {
            "total_items": 180,
            "major_items": 90,
            "major_ratio": 0.85,
            "major_ratio_min_sample": 20,
        },
        "require_unique_event_ids": True,
        "require_live_ingestion": True,
        "allowed_statuses": ["complete", "partial"],
    },
    "analysis": {
        "required_for_production": True,
        "allowed_effective_modes": ["api-assisted", "chat-assisted"],
        "require_provider": True,
        "require_model": True,
        "forbid_fallback": True,
        "require_same_report": True,
    },
}


def report(count: int = 10, major: int = 5) -> dict:
    return {
        "date": "2026-07-15",
        "report_id": "report_1",
        "status": "partial",
        "source_audit": {"ingestion_mode": "live_multi"},
        "items": [
            {
                "event_id": f"evt_{index}",
                "report_lane": "major" if index < major else "potential",
            }
            for index in range(count)
        ],
    }


def analysis(*, fallback: bool = False, source_report_id: str = "report_1") -> dict:
    return {
        "analysis_id": "analysis_1",
        "source_report_id": source_report_id,
        "provenance": {
            "source_report_date": "2026-07-15",
            "effective_mode": "deterministic" if fallback else "api-assisted",
            "provider": None if fallback else "openai",
            "model": None if fallback else "gpt-test",
            "fallback_used": fallback,
        },
    }


class ProductionQualityGateTests(unittest.TestCase):
    def test_healthy_report_and_real_ai_pass(self) -> None:
        current = report()
        self.assertEqual(MODULE.check_report(current, CONFIG, "2026-07-15"), [])
        self.assertEqual(MODULE.check_report_warnings(current, CONFIG), [])
        self.assertEqual(MODULE.check_analysis(analysis(), current, CONFIG), [])

    def test_976_item_report_warns_but_does_not_block(self) -> None:
        current = report(count=976, major=745)
        self.assertEqual(MODULE.check_report(current, CONFIG, "2026-07-15"), [])
        warnings = MODULE.check_report_warnings(current, CONFIG)
        self.assertIn("item_count_above_review_threshold:976>180", warnings)
        self.assertIn("major_count_above_review_threshold:745>90", warnings)

    def test_duplicate_empty_fixture_and_wrong_date_still_block(self) -> None:
        current = report(count=2, major=1)
        current["items"][1]["event_id"] = current["items"][0]["event_id"]
        self.assertIn(
            "duplicate_event_ids",
            MODULE.check_report(current, CONFIG, "2026-07-15"),
        )

        empty = report(count=0, major=0)
        empty["source_audit"]["ingestion_mode"] = "fixture"
        reasons = MODULE.check_report(empty, CONFIG, "2026-07-16")
        self.assertIn("report_date_mismatch:2026-07-15!=2026-07-16", reasons)
        self.assertIn("ingestion_mode_not_live:fixture", reasons)
        self.assertIn("item_count_below_minimum:0<1", reasons)

    def test_deterministic_fallback_is_not_production_ai(self) -> None:
        reasons = MODULE.check_analysis(analysis(fallback=True), report(), CONFIG)
        self.assertIn("analysis_effective_mode_not_allowed:deterministic", reasons)
        self.assertIn("analysis_provider_missing", reasons)
        self.assertIn("analysis_model_missing", reasons)
        self.assertIn("analysis_fallback_forbidden", reasons)

    def test_mismatched_analysis_is_rejected(self) -> None:
        reasons = MODULE.check_analysis(analysis(source_report_id="report_other"), report(), CONFIG)
        self.assertIn("analysis_source_report_mismatch", reasons)


if __name__ == "__main__":
    unittest.main()
