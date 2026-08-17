from __future__ import annotations

import unittest

from radar.domain.models import Document, Event, EventDelta
from radar.evaluators.matrices import evaluate_structural_indicators
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deltas import material_events
from radar.reporting.planner import plan_daily_items


class IndicatorFreshnessTests(unittest.TestCase):
    def test_old_quarter_measurement_reaches_structural_evaluator_on_material_day(self) -> None:
        document = Document.fixture(
            source_id="bls_productivity",
            title="BLS productivity gain; labor share decline; real wage decline",
            summary="Productivity increased while labor share and real wage declined.",
            published_at="2026-06-30T00:00:00+00:00",
            fetched_at="2026-08-17T04:45:36+00:00",
            primary_domain="global_markets_macro",
            lane="indicator_only",
            facts={
                "source_roles": ["official", "government", "data"],
                "rate_labor_productivity_yoy": 2.8,
                "rate_labor_share_yoy": -2.9,
                "rate_real_hourly_compensation_yoy": -0.4,
            },
        )
        event = cluster_documents([document])[0]

        selected = material_events([event], report_date="2026-08-17")
        self.assertEqual(selected, [event])
        self.assertEqual(plan_daily_items(selected), [])

        observation = evaluate_structural_indicators(
            selected,
            ["k_shaped_ai_productivity_economy"],
            observation_date="2026-08-17",
        )[0]
        self.assertGreater(observation.support_score, 0)
        self.assertIn(event.event_id, observation.supporting_signal_ids)

    def test_unchanged_old_measurement_does_not_cast_another_vote_next_day(self) -> None:
        document = Document.fixture(
            source_id="bls_productivity",
            title="BLS productivity gain; labor share decline; real wage decline",
            summary="Productivity increased while labor share and real wage declined.",
            published_at="2026-06-30T00:00:00+00:00",
            fetched_at="2026-08-17T04:45:36+00:00",
            primary_domain="global_markets_macro",
            lane="indicator_only",
            facts={
                "rate_labor_productivity_yoy": 2.8,
                "rate_labor_share_yoy": -2.9,
                "rate_real_hourly_compensation_yoy": -0.4,
            },
        )
        clustered = cluster_documents([document])[0]
        unchanged = Event(
            event_id=clustered.event_id,
            documents=clustered.documents,
            first_seen_at="2026-08-17T04:45:36+00:00",
            last_seen_at="2026-08-18T04:45:36+00:00",
            last_material_delta_at="2026-08-17T04:45:36+00:00",
            status="active",
            deltas=[
                EventDelta(
                    delta_type="same_event_same_facts",
                    changed_fields=[],
                    reason="unchanged measurement",
                )
            ],
        )

        self.assertEqual(material_events([unchanged], report_date="2026-08-18"), [])

    def test_old_news_story_still_requires_daily_news_freshness(self) -> None:
        document = Document.fixture(
            source_id="archive_feed",
            title="Old company earnings report",
            summary="Historical earnings story replayed by an RSS archive.",
            published_at="2026-06-30T00:00:00+00:00",
            fetched_at="2026-08-17T04:45:36+00:00",
            primary_domain="global_markets_macro",
            lane="top_down",
            facts={"revenue_usd_m": 100.0},
        )
        event = cluster_documents([document])[0]

        self.assertEqual(material_events([event], report_date="2026-08-17"), [])


if __name__ == "__main__":
    unittest.main()
