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
        canonical_domains = set(self.config["_canonical_report_domains"])
        self.assertEqual(
            canonical_domains,
            {
                "global_markets_macro",
                "ai_agents_applications",
                "crypto_rwa_agent_payments",
                "retail_consumer_fashion",
                "science_technology_industry",
            },
        )
        self.assertTrue(set(row.domain for row in typed.key_findings) <= canonical_domains)
        self.assertTrue(canonical_domains.issubset({row.domain for row in typed.key_findings}))
        self.assertTrue(all(row.horizon == "three_to_six_months" for row in typed.future_trends))
        self.assertTrue(all(sorted(row.horizon_months) == [3, 6] for row in typed.future_trends))
        self.assertTrue(all(row.synthesis_scope == "global" for row in typed.future_trends))
        self.assertTrue(all(len(row.source_domain_ids) >= 2 for row in typed.future_trends))
        self.assertTrue(all(len(row.source_event_ids) >= 2 for row in typed.future_trends))
        self.assertTrue(all(0 <= row.score <= 100 for row in typed.linked_indicators))
        for row in typed.key_findings:
            self.assertTrue(set(row.source_event_ids).issubset(allowed_events))
        for row in typed.future_trends:
            self.assertTrue(set(row.source_event_ids).issubset(allowed_events))
        for row in typed.linked_indicators:
            self.assertTrue(set(row.source_event_ids).issubset(allowed_events))

    def test_three_canonical_structural_indicators_are_primary_and_unchanged(self) -> None:
        analysis = build_deterministic_analysis(
            self.report,
            None,
            self.config,
            generated_at="2026-07-10T02:00:00+00:00",
        )
        expected_ids = [row["indicator_id"] for row in self.config["core_structural_indicators"]]
        actual_ids = [row.indicator_id for row in analysis.structural_indicators]
        self.assertEqual(actual_ids, expected_ids)
        self.assertEqual(len(actual_ids), 3)
        self.assertEqual(len(analysis.linked_indicators), 6)

        source = {row.indicator_id: row for row in self.report.structural_indicators}
        for row in analysis.structural_indicators:
            original = source[row.indicator_id]
            expected_direction = {
                "supporting": "toward",
                "support": "toward",
                "counter": "against",
            }.get(original.direction, original.direction)
            self.assertEqual(row.direction, expected_direction)
            self.assertEqual(row.support_score, original.support_score)
            self.assertEqual(row.counter_score, original.counter_score)
            self.assertEqual(row.confidence, original.confidence)
            self.assertEqual(row.supporting_signal_ids, original.supporting_signal_ids)
            self.assertEqual(row.counter_signal_ids, original.counter_signal_ids)
            self.assertEqual(row.missing_data, original.missing_data)
            self.assertEqual(row.one_sentence_read, original.one_sentence_read)
            self.assertEqual(row.next_verification, original.next_verification)
            self.assertEqual(row.components, original.components)
        self.assertTrue(all(component.evidence or component.missing_data for component in row.components))

    def test_structural_direction_aliases_are_normalized_at_analysis_boundary(self) -> None:
        payload = self.report.model_dump(mode="json")
        payload["structural_indicators"][0]["direction"] = "counter"
        payload["structural_indicators"][1]["direction"] = "supporting"
        report = RadarReportV2.from_payload(payload)

        analysis = build_deterministic_analysis(
            report,
            None,
            self.config,
            generated_at="2026-07-10T02:00:00+00:00",
        )

        self.assertEqual(analysis.structural_indicators[0].direction, "against")
        self.assertEqual(analysis.structural_indicators[1].direction, "toward")

    def test_same_report_as_previous_produces_flat_auxiliary_indicator_deltas(self) -> None:
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
        self.assertEqual(
            schema["properties"]["structural_indicators"]["items"]["$ref"],
            "#/$defs/StructuralIndicatorAnalysisV1",
        )


if __name__ == "__main__":
    unittest.main()
