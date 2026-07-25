from __future__ import annotations

import unittest

from radar.domain.models import Document
from radar.domain.text_matching import contains_term
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.qualification import assess_report_qualification
from radar.reporting.planner import plan_daily_items, qualified_report_events


def event_for(
    title: str,
    *,
    domain: str = "global_markets_macro",
    action: str = "reports",
    obj: str = "update",
    source_id: str = "source",
):
    document = Document.fixture(
        source_id=source_id,
        url=f"https://example.com/{source_id}/{abs(hash(title))}",
        title=title,
        action=action,
        object=obj,
        primary_domain=domain,
    )
    return cluster_documents([document])[0]


class BoundaryAwareTextMatchingTests(unittest.TestCase):
    def test_short_ascii_terms_do_not_match_inside_unrelated_words(self) -> None:
        self.assertFalse(contains_term("Company raises capital", "ai"))
        self.assertFalse(contains_term("Capital spending grows", "api"))
        self.assertTrue(contains_term("AI agent launches API", "ai"))
        self.assertTrue(contains_term("AI agent launches API", "api"))


class ReportQualificationTests(unittest.TestCase):
    def test_generic_fresh_feed_story_is_rejected_instead_of_defaulting_to_major(self) -> None:
        event = event_for("幼年穿山甲疑遭遊蕩犬攻擊死亡 台南動保處加強巡查")

        assessment = assess_report_qualification(event)

        self.assertFalse(assessment.qualified)
        self.assertEqual(assessment.reason, "generic_or_low_materiality_feed_story")
        self.assertEqual(plan_daily_items([event]), [])

    def test_explicit_economic_change_is_qualified_as_major(self) -> None:
        event = event_for("美國新關稅衝擊出口產業 成本與價格同步上升")

        assessment = assess_report_qualification(event)
        items = plan_daily_items([event])

        self.assertTrue(assessment.qualified)
        self.assertEqual(assessment.reason, "major_has_explicit_subject_and_change")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].report_lane, "major")

    def test_content_qualified_potential_is_preserved(self) -> None:
        event = event_for(
            "Startup pilots agent payment API",
            domain="ai_agents_applications",
            action="pilots",
            obj="agent payment API",
        )

        assessment = assess_report_qualification(event)
        items = plan_daily_items([event])

        self.assertTrue(assessment.qualified)
        self.assertEqual(assessment.reason, "content_qualified_potential")
        self.assertEqual(items[0].report_lane, "potential")

    def test_generic_market_update_is_not_major_without_a_concrete_change(self) -> None:
        event = event_for("Local outlet reports quarterly market update")

        self.assertFalse(assess_report_qualification(event).qualified)
        self.assertEqual(qualified_report_events([event]), [])

    def test_qualification_is_not_a_count_cap(self) -> None:
        events = [
            event_for(f"晶片產能擴張帶動供應鏈投資增加 {index}", source_id=f"source-{index}")
            for index in range(25)
        ]

        self.assertEqual(len(qualified_report_events(events)), 25)
        self.assertEqual(len(plan_daily_items(events)), 25)


if __name__ == "__main__":
    unittest.main()
