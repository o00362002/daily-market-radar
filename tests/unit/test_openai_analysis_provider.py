from __future__ import annotations

import json
import unittest
from pathlib import Path

from radar.analysis.builder import build_deterministic_analysis, load_analysis_config
from radar.analysis.openai_provider import (
    AiAnalysisProposal,
    FindingProposal,
    IndicatorInterpretationProposal,
    TranslationProposal,
    TrendProposal,
    _merge_proposal,
)
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
    return RadarReportV2.from_payload(json.loads(json.dumps(result.report, ensure_ascii=False)))


class OpenAIAnalysisProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = _report()
        self.config = load_analysis_config(ROOT)
        self.baseline = build_deterministic_analysis(
            self.report,
            None,
            self.config,
            generated_at="2026-07-10T02:00:00+00:00",
            requested_mode="auto",
        )
        self.event_id = self.report.items[0].event_id
        self.indicator_id = self.baseline.linked_indicators[0].indicator_id

    def _proposal(self, *, event_id: str | None = None) -> AiAnalysisProposal:
        event = event_id or self.event_id
        return AiAnalysisProposal(
            executive_summary=["今日重點集中在已驗證事件與早期採用訊號。"],
            translations=[TranslationProposal(event_id=event, translated_text="忠實繁中標題")],
            key_findings=[
                FindingProposal(
                    label="ai_inference",
                    title="跨事件關聯判讀",
                    summary="多個訊號可能共同指向採用擴散，但仍需要後續證據。",
                    source_event_ids=[event],
                    confidence=70,
                )
            ],
            future_trends=[
                TrendProposal(
                    title="採用動能情境",
                    stage="emerging",
                    horizon="months",
                    direction="mixed",
                    summary="若後續出現獨立採用與使用量證據，趨勢才可能成形。",
                    source_event_ids=[event],
                    counterevidence=["目前證據仍集中於單日事件。"],
                    uncertainties=["尚缺跨區域擴散資料。"],
                    next_watch=["追蹤獨立採用與量化使用資料。"],
                    confidence=65,
                )
            ],
            indicator_interpretations=[
                IndicatorInterpretationProposal(
                    indicator_id=self.indicator_id,
                    interpretation="此分數反映目前訊號強度，不代表確定市場方向。",
                )
            ],
            limitations=["分析只使用 bounded report context。"],
        )

    def test_model_may_interpret_but_not_change_indicator_values(self) -> None:
        enhanced = _merge_proposal(
            self.report,
            self.baseline,
            self._proposal(),
            "openai",
            "test-model",
            self.config,
        )
        before = {row.indicator_id: row for row in self.baseline.linked_indicators}
        after = {row.indicator_id: row for row in enhanced.linked_indicators}
        for indicator_id, original in before.items():
            updated = after[indicator_id]
            self.assertEqual(updated.score, original.score)
            self.assertEqual(updated.previous_score, original.previous_score)
            self.assertEqual(updated.delta, original.delta)
            self.assertEqual(updated.direction, original.direction)
            self.assertEqual(updated.status, original.status)
            self.assertEqual(updated.method, original.method)
            self.assertEqual(updated.components, original.components)
            self.assertEqual(updated.source_event_ids, original.source_event_ids)
        self.assertEqual(enhanced.provenance.provider, "openai")
        self.assertEqual(enhanced.provenance.model, "test-model")
        self.assertFalse(enhanced.provenance.fallback_used)

    def test_unknown_event_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown"):
            _merge_proposal(
                self.report,
                self.baseline,
                self._proposal(event_id="evt_invented"),
                "openai",
                "test-model",
                self.config,
            )


if __name__ == "__main__":
    unittest.main()
