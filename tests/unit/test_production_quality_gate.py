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
        "max_total_items": 180,
        "max_major_items": 90,
        "max_major_ratio": 0.85,
        "major_ratio_min_sample": 20,
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
        self.assertEqual(MODULE.check_analysis(analysis(), current, CONFIG), [])

    def test_736_item_report_is_rejected(self) -> None:
        reasons = MODULE.check_report(report(count=736, major=629), CONFIG, "2026-07-15")
        self.assertTrue(any(reason.startswith("item_count_exceeds_limit") for reason in reasons))
        self.assertTrue(any(reason.startswith("major_count_exceeds_limit") for reason in reasons))
        self.assertTrue(any(reason.startswith("major_ratio_exceeds_limit") for reason in reasons))

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
