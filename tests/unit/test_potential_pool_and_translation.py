from __future__ import annotations

import unittest

from radar.contracts.report import ReportItemV2
from radar.domain.models import Document
from radar.domain.potential import assess_event
from radar.evaluators.ai_assisted import _apply_proposal
from radar.evaluators.ai_provider import AiProposalItem, AiProposalResult, AllowedFacts
from radar.pipeline.classify import classify_potential_signals
from radar.pipeline.cluster import cluster_documents
from radar.reporting.planner import plan_daily_items


def _event(
    *,
    title: str,
    action: str,
    obj: str,
    lane: str,
    source_id: str = "source",
    language: str = "en",
):
    document = Document.fixture(
        source_id=source_id,
        url=f"https://example.com/{source_id}",
        title=title,
        language=language,
        entities=["Example"],
        action=action,
        object=obj,
        location="Global",
        lane=lane,
        primary_domain="ai_agents_applications",
    )
    return cluster_documents([document])[0]


class PotentialPoolAndTranslationTests(unittest.TestCase):
    def test_official_pilot_can_be_potential(self) -> None:
        event = _event(
            title="Regulator opens AI agent sandbox pilot",
            action="opens",
            obj="AI agent sandbox",
            lane="top_down",
            source_id="regulator",
        )

        assessment = assess_event(event)

        self.assertEqual(assessment.lane, "potential")
        self.assertEqual(assessment.candidate_type, "新應用")
        self.assertIn(assessment.formation_level, {"萌芽", "重複出現", "擴散中", "已驗證"})

    def test_bottom_up_generic_story_is_not_automatically_potential(self) -> None:
        event = _event(
            title="Local outlet reports quarterly market update",
            action="reports",
            obj="quarterly market update",
            lane="bottom_up",
            source_id="local-outlet",
        )

        assessment = assess_event(event)

        self.assertEqual(assessment.lane, "major")
        self.assertIsNone(assessment.candidate_type)

    def test_all_content_qualified_potential_events_emit_signals(self) -> None:
        events = [
            _event(
                title="Startup pilots agent payment API",
                action="pilots",
                obj="agent payment API",
                lane="bottom_up",
                source_id=f"startup-{index}",
            )
            for index in range(5)
        ]

        signals = classify_potential_signals(events)

        self.assertEqual(len(signals), 5)
        self.assertTrue(all(signal.next_check_at for signal in signals))

    def test_deterministic_narrative_is_traditional_chinese(self) -> None:
        event = _event(
            title="Company pilots retail agent",
            action="pilots",
            obj="retail agent",
            lane="top_down",
        )

        item = plan_daily_items([event])[0]

        self.assertEqual(item.report_lane, "potential")
        self.assertIn("今日", item.today_delta)
        self.assertIn("追蹤", item.next_watch)
        self.assertTrue(any("早期訊號" in text for text in item.uncertainties))

    def test_ai_translation_preserves_original_headline(self) -> None:
        event = _event(
            title="Company pilots retail agent",
            action="pilots",
            obj="retail agent",
            lane="top_down",
        )
        base = ReportItemV2.model_validate(plan_daily_items([event])[0].to_dict())
        proposal = AiProposalResult(
            items=(
                AiProposalItem(
                    event_id=event.event_id,
                    headline="公司試行零售 AI 代理",
                    today_delta="今日新增：公司開始試行零售 AI 代理。",
                ),
            )
        )
        allowed = AllowedFacts(
            event_ids=frozenset({event.event_id}),
            source_ids=frozenset(),
            urls=frozenset(),
            numeric_facts=frozenset(),
        )

        translated = _apply_proposal((base,), proposal, allowed)[0]

        self.assertEqual(translated.headline, "公司試行零售 AI 代理")
        self.assertIn("今日新增", translated.today_delta)
        self.assertIn("原文標題：Company pilots retail agent", translated.uncertainties)


if __name__ == "__main__":
    unittest.main()
