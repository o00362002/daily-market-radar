from __future__ import annotations

import unittest

from radar.domain.models import Document, Event
from radar.domain.potential import assess_event
from radar.evaluators.matrices import evaluate_crypto_matrix, evaluate_structural_indicators
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deltas import indicator_events_for_date, material_events
from radar.pipeline.qualification import assess_report_qualification
from radar.reporting.planner import plan_daily_items


class IndicatorOnlyMeasurementTests(unittest.TestCase):
    def test_indicator_measurement_does_not_become_news_or_potential_signal(self) -> None:
        document = Document.fixture(
            source_id="measurement_source",
            title="Protocol TVL and revenue measurement snapshot",
            summary="Structured protocol measurement used by the fixed crypto matrix.",
            primary_domain="crypto_rwa_agent_payments",
            lane="indicator_only",
            facts={"tvl_usd_m": 1200, "revenue_usd_m": 4.2},
        )
        event = cluster_documents([document])[0]

        self.assertEqual(assess_event(event).lane, "indicator_only")
        self.assertFalse(assess_report_qualification(event).qualified)
        self.assertEqual(plan_daily_items([event]), [])

    def test_indicator_measurement_still_fills_fixed_matrix(self) -> None:
        document = Document.fixture(
            source_id="measurement_source",
            title="Protocol TVL and revenue measurement snapshot",
            summary="Structured protocol measurement used by the fixed crypto matrix.",
            primary_domain="crypto_rwa_agent_payments",
            lane="indicator_only",
            facts={"tvl_usd_m": 1200, "revenue_usd_m": 4.2},
        )
        event = cluster_documents([document])[0]
        cell = evaluate_crypto_matrix([event], ["tvl_fees_revenue"])["tvl_fees_revenue"]

        self.assertEqual(cell.status, "observed")
        self.assertEqual(cell.signal_ids, [event.event_id])
        self.assertIn("metric:tvl", cell.data_checked)
        self.assertIn("metric:revenue", cell.data_checked)

    def test_old_observation_period_can_reach_structural_evaluator_when_material_today(self) -> None:
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

        self.assertEqual(material_events([event], report_date="2026-08-17"), [])
        indicator_events = indicator_events_for_date([event], report_date="2026-08-17")
        self.assertEqual(indicator_events, [event])
        observation = evaluate_structural_indicators(
            indicator_events,
            ["k_shaped_ai_productivity_economy"],
            observation_date="2026-08-17",
        )[0]
        self.assertGreater(observation.support_score, 0)
        self.assertIn(event.event_id, observation.supporting_signal_ids)

    def test_unchanged_old_indicator_does_not_cast_a_new_vote_next_day(self) -> None:
        document = Document.fixture(
            source_id="bls_productivity",
            title="BLS productivity gain; labor share decline; real wage decline",
            published_at="2026-06-30T00:00:00+00:00",
            fetched_at="2026-08-17T04:45:36+00:00",
            primary_domain="global_markets_macro",
            lane="indicator_only",
            facts={"rate_labor_productivity_yoy": 2.8, "rate_labor_share_yoy": -2.9},
        )
        clustered = cluster_documents([document])[0]
        unchanged = Event(
            event_id=clustered.event_id,
            documents=clustered.documents,
            first_seen_at="2026-08-17T04:45:36+00:00",
            last_seen_at="2026-08-18T04:45:36+00:00",
            last_material_delta_at="2026-08-17T04:45:36+00:00",
            status="active",
            deltas=[],
        )
        # No deltas on a manually constructed legacy event are treated as material,
        # so model the resolver's duplicate-only output with a non-material delta.
        from radar.domain.models import EventDelta
        unchanged = Event(
            event_id=unchanged.event_id,
            documents=unchanged.documents,
            first_seen_at=unchanged.first_seen_at,
            last_seen_at=unchanged.last_seen_at,
            last_material_delta_at=unchanged.last_material_delta_at,
            status="active",
            deltas=[EventDelta(delta_type="duplicate_only", changed_fields=[], reason="unchanged measurement")],
        )

        self.assertEqual(indicator_events_for_date([unchanged], report_date="2026-08-18"), [])


if __name__ == "__main__":
    unittest.main()
