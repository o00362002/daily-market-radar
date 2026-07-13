from __future__ import annotations

import unittest

from radar.evaluators.matrices import (
    evaluate_crypto_matrix,
    evaluate_retail_matrix,
    evaluate_structural_indicators,
    rolling_summary,
)
from radar.domain.models import Document
from radar.pipeline.cluster import cluster_documents


def _event(**kwargs):
    base = dict(
        source_id="src",
        url="https://example.com/x",
        title="Title",
        entities=["Entity"],
        action="acts",
        object="thing",
        location="US",
        macro_region="North America",
    )
    base.update(kwargs)
    return cluster_documents([Document.fixture(**base)])[0]


RETAIL_KEYS = ["cost_pressure", "inventory_markdown_mid_price_pressure", "membership_crm_loyalty_retail_media"]
CRYPTO_KEYS = ["btc_eth_sol_market_structure", "etf_flows", "tvl_fees_revenue"]
INDICATORS = ["ai_bubble_overinvestment"]


class RetailMatrixTests(unittest.TestCase):
    def test_insufficient_without_evidence(self) -> None:
        matrix = evaluate_retail_matrix([_event(title="Nothing retail here")], RETAIL_KEYS)
        self.assertTrue(all(cell.status == "insufficient" for cell in matrix.values()))
        self.assertTrue(all(cell.gap for cell in matrix.values()))

    def test_observed_with_feature_trace_when_metric_present(self) -> None:
        event = _event(
            title="Retailer inventory markdown accelerates",
            primary_domain="retail_consumer_fashion",
            facts={"inventory_units": 1000},
        )
        matrix = evaluate_retail_matrix([event], RETAIL_KEYS)
        cell = matrix["inventory_markdown_mid_price_pressure"]
        self.assertEqual(cell.status, "observed")
        self.assertTrue(cell.signal_ids)
        self.assertTrue(any(trace.startswith("metric:") or trace.startswith("keyword:") for trace in cell.data_checked))


class CryptoMatrixTests(unittest.TestCase):
    def test_insufficient_without_evidence(self) -> None:
        matrix = evaluate_crypto_matrix([_event(title="unrelated news")], CRYPTO_KEYS)
        self.assertTrue(all(cell.status == "insufficient" for cell in matrix.values()))

    def test_observed_with_etf_flow_metric(self) -> None:
        event = _event(title="ETF sees record inflow", primary_domain="crypto_rwa_agent_payments", facts={"flow_usd_m": 500})
        matrix = evaluate_crypto_matrix([event], CRYPTO_KEYS)
        self.assertEqual(matrix["etf_flows"].status, "observed")
        self.assertIn("metric:flow", matrix["etf_flows"].data_checked)


class StructuralIndicatorTests(unittest.TestCase):
    def test_insufficient_produces_no_fabricated_trend(self) -> None:
        observations = evaluate_structural_indicators([_event(title="neutral update")], INDICATORS, observation_date="2026-07-10")
        self.assertEqual(observations[0].direction, "insufficient")
        self.assertEqual(observations[0].confidence, "insufficient")
        self.assertEqual(observations[0].support_score, 0)

    def test_supporting_evidence_yields_directional_read_with_trace(self) -> None:
        event = _event(title="Massive AI capex fuels overinvestment and bubble fears")
        observations = evaluate_structural_indicators([event], INDICATORS, observation_date="2026-07-10")
        obs = observations[0]
        self.assertEqual(obs.direction, "supporting")
        self.assertGreater(obs.support_score, 0)
        self.assertTrue(obs.supporting_signal_ids)
        self.assertTrue(obs.components)
        self.assertTrue(any(component.evidence for component in obs.components))
        self.assertNotEqual(obs.confidence, "insufficient")


class RollingWindowTests(unittest.TestCase):
    def test_rolling_windows_only_use_real_observations(self) -> None:
        observations = evaluate_structural_indicators(
            [_event(title="AI capex overinvestment bubble")], INDICATORS, observation_date="2026-07-08"
        )
        observations += evaluate_structural_indicators(
            [_event(title="AI capex overinvestment valuation")], INDICATORS, observation_date="2026-07-10"
        )
        summary = rolling_summary(observations, as_of="2026-07-10")
        self.assertEqual(summary["current"]["status"], "observed")
        self.assertEqual(summary["rolling_7d"]["observations"], 2)
        self.assertGreaterEqual(summary["rolling_30d"]["avg_support"], 0)

    def test_empty_window_is_insufficient_not_fabricated(self) -> None:
        insufficient = evaluate_structural_indicators([_event(title="neutral")], INDICATORS, observation_date="2026-01-01")
        summary = rolling_summary(insufficient, as_of="2026-07-10")
        self.assertEqual(summary["rolling_7d"]["status"], "insufficient")


if __name__ == "__main__":
    unittest.main()
