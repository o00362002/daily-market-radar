from __future__ import annotations

import unittest

from radar.domain.models import Document
from radar.domain.potential import assess_event
from radar.evaluators.matrices import evaluate_crypto_matrix
from radar.pipeline.cluster import cluster_documents
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


if __name__ == "__main__":
    unittest.main()
