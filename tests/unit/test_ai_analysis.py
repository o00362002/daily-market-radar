from __future__ import annotations

import json
import unittest
from pathlib import Path

from radar.analysis.builder import build_deterministic_analysis, load_analysis_config
from radar.contracts.analysis import AIAnalysisV1, ai_analysis_json_schema
from radar.contracts.report import RadarReportV2
from radar.runtime.runs import run_daily_fixture


ROOT = Path(__file__).resolve().parents[2]


def _report() -> RadarReportV2:
    result = run_daily_fixture(
        ROOT,
        date="2026-07-10",
        freshrss_available=True,
        external_discovery_available=True,
        evaluation_mode="deterministic",
    )
    payload = json.loads(json.dumps(result.report, ensure_ascii=False))
    return RadarReportV2.from_payload(payload)


class AIAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = _report()
        self.config = load_analysis_config(ROOT)

    def test_deterministic_analysis_is_typed_traceable_and_bounded(self) -> None:
        analysis = build_deterministic_analysis(
            self.report,
            None,
            self.config,
            generated_at="2026-07-10T02:00:00+00:00",
            requested_mode="deterministic",
        )
        typed = AIAnalysisV1.model_validate(analysis.model_dump(mode="json"))
        allowed_events = {item.event_id for item in self.report.items}

        self.assertEqual(typed.date, self.report.date)
        self.assertEqual(typed.source_report_id, self.report.report_id)
        self.assertEqual(typed.provenance.schema_version, "ai-analysis/v1")
        self.assertEqual(typed.provenance.effective_mode, "deterministic")
        self.assertFalse(typed.provenance.fallback_used)
        self.assertTrue(typed.executive_summary)
        self.assertTrue(typed.linked_indicators)
        self.assertTrue(all(0 <= row.score <= 100 for row in typed.linked_indicators))
        for row in typed.key_findings:
            self.assertTrue(set(row.source_event_ids).issubset(allowed_events))
        for row in typed.future_trends:
            self.assertTrue(set(row.source_event_ids).issubset(allowed_events))
        for row in typed.linked_indicators:
            self.assertTrue(set(row.source_event_ids).issubset(allowed_events))

    def test_same_report_as_previous_produces_flat_indicator_deltas(self) -> None:
        analysis = build_deterministic_analysis(
            self.report,
            self.report,
            self.config,
            generated_at="2026-07-10T02:00:00+00:00",
        )
        observed = [row for row in analysis.linked_indicators if row.status != "insufficient"]
        self.assertTrue(observed)
        self.assertTrue(all(row.delta == 0 for row in observed))
        self.assertTrue(all(row.direction == "flat" for row in observed))

    def test_auto_without_provider_is_explicit_fallback(self) -> None:
        analysis = build_deterministic_analysis(
            self.report,
            None,
            self.config,
            generated_at="2026-07-10T02:00:00+00:00",
            requested_mode="auto",
            fallback_reason="OPENAI_API_KEY unavailable",
        )
        self.assertTrue(analysis.provenance.fallback_used)
        self.assertEqual(analysis.provenance.validation_status, "fallback")
        self.assertTrue(any("OPENAI_API_KEY" in row for row in analysis.limitations))

    def test_schema_is_strict_ai_analysis_v1(self) -> None:
        schema = ai_analysis_json_schema()
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["provenance"]["$ref"], "#/$defs/AnalysisProvenanceV1")


if __name__ == "__main__":
    unittest.main()
