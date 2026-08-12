from __future__ import annotations

import unittest

from radar.evaluators.matrices import evaluate_crypto_matrix, evaluate_retail_matrix, evaluate_structural_indicators, rolling_summary
from radar.domain.models import Document
from radar.pipeline.cluster import cluster_documents


def _event(**kwargs):
    base = dict(source_id="src", url="https://example.com/x", title="Title", entities=["Entity"], action="acts", object="thing", location="US", macro_region="North America")
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
        event = _event(title="Retailer inventory markdown accelerates", primary_domain="retail_consumer_fashion", facts={"inventory_units": 1000})
        cell = evaluate_retail_matrix([event], RETAIL_KEYS)["inventory_markdown_mid_price_pressure"]
        self.assertEqual(cell.status, "observed")
        self.assertTrue(cell.signal_ids)
        self.assertTrue(any(x.startswith("metric:") or x.startswith("keyword:") for x in cell.data_checked))

    def test_cross_domain_keyword_does_not_fill_retail_cell(self) -> None:
        event = _event(title="AI data center store costs rise online", primary_domain="ai_agents_applications", facts={"cost_usd_m": 100})
        self.assertTrue(all(c.status == "insufficient" for c in evaluate_retail_matrix([event], RETAIL_KEYS).values()))

    def test_generic_ai_content_does_not_fill_social_commerce(self) -> None:
        event = _event(title="Retail brand publishes AI content update", primary_domain="retail_consumer_fashion")
        cell = evaluate_retail_matrix([event], ["social_commerce_content_discovery_ai_referral"])["social_commerce_content_discovery_ai_referral"]
        self.assertEqual(cell.status, "insufficient")

    def test_ai_referral_phrase_fills_social_commerce(self) -> None:
        event = _event(title="Retailer measures AI referral traffic", primary_domain="retail_consumer_fashion")
        cell = evaluate_retail_matrix([event], ["social_commerce_content_discovery_ai_referral"])["social_commerce_content_discovery_ai_referral"]
        self.assertEqual(cell.status, "observed")


class CryptoMatrixTests(unittest.TestCase):
    def test_insufficient_without_evidence(self) -> None:
        self.assertTrue(all(c.status == "insufficient" for c in evaluate_crypto_matrix([_event(title="unrelated news")], CRYPTO_KEYS).values()))

    def test_observed_with_etf_flow_metric(self) -> None:
        event = _event(title="ETF sees record inflow", primary_domain="crypto_rwa_agent_payments", facts={"flow_usd_m": 500})
        cell = evaluate_crypto_matrix([event], CRYPTO_KEYS)["etf_flows"]
        self.assertEqual(cell.status, "observed")
        self.assertIn("metric:flow", cell.data_checked)

    def test_cross_domain_market_terms_do_not_fill_crypto_cell(self) -> None:
        event = _event(title="ETF market revenue grows", primary_domain="global_markets_macro", facts={"flow_usd_m": 500, "revenue_usd_m": 10})
        self.assertTrue(all(c.status == "insufficient" for c in evaluate_crypto_matrix([event], CRYPTO_KEYS).values()))

    def test_generic_policy_does_not_fill_crypto_regulation(self) -> None:
        event = _event(title="Company updates internal policy", primary_domain="crypto_rwa_agent_payments")
        self.assertEqual(evaluate_crypto_matrix([event], ["regulation_policy"])["regulation_policy"].status, "insufficient")

    def test_vasp_fills_crypto_regulation(self) -> None:
        event = _event(title="Taiwan VASP licensing rules take effect", primary_domain="crypto_rwa_agent_payments")
        self.assertEqual(evaluate_crypto_matrix([event], ["regulation_policy"])["regulation_policy"].status, "observed")


class StructuralIndicatorTests(unittest.TestCase):
    def test_insufficient_produces_no_fabricated_trend(self) -> None:
        obs = evaluate_structural_indicators([_event(title="neutral update")], INDICATORS, observation_date="2026-07-10")[0]
        self.assertEqual(obs.direction, "insufficient")
        self.assertEqual(obs.confidence, "insufficient")
        self.assertEqual(obs.support_score, 0)

    def test_supporting_evidence_yields_directional_read_with_trace(self) -> None:
        event = _event(title="Massive AI capex fuels overinvestment and AI bubble fears")
        obs = evaluate_structural_indicators([event], INDICATORS, observation_date="2026-07-10")[0]
        self.assertEqual(obs.direction, "supporting")
        self.assertGreater(obs.support_score, 0)
        self.assertTrue(obs.supporting_signal_ids)
        self.assertTrue(any(component.evidence for component in obs.components))

    def test_layoff_does_not_match_playoff(self) -> None:
        obs = evaluate_structural_indicators([_event(title="NHL playoff race tightens")], ["k_shaped_ai_productivity_economy"], observation_date="2026-08-08")[0]
        self.assertEqual(obs.direction, "insufficient")

    def test_middle_east_does_not_count_as_brand_polarization(self) -> None:
        obs = evaluate_structural_indicators([_event(title="Middle East port traffic rises")], ["brand_market_polarization_and_true_vs_fake_segmentation"], observation_date="2026-08-12")[0]
        self.assertEqual(obs.direction, "insufficient")

    def test_total_income_does_not_count_as_wage_income(self) -> None:
        obs = evaluate_structural_indicators([_event(title="Company total income rises after asset sale")], ["k_shaped_ai_productivity_economy"], observation_date="2026-08-12")[0]
        self.assertEqual(obs.direction, "insufficient")
        wage = next(row for row in obs.components if row.component_id == "wage_income")
        self.assertEqual(wage.direction, "insufficient")

    def test_generic_platform_community_do_not_fill_brand_components(self) -> None:
        obs = evaluate_structural_indicators([_event(title="Community platform launches software update")], ["brand_market_polarization_and_true_vs_fake_segmentation"], observation_date="2026-08-12")[0]
        self.assertEqual(obs.direction, "insufficient")
        self.assertTrue(all(row.direction == "insufficient" for row in obs.components))

    def test_balanced_conflict_reduces_directional_confidence(self) -> None:
        events = [_event(title="AI capex overinvestment drives AI valuation bubble"), _event(title="Paid adoption drives AI revenue and profitable AI services")]
        obs = evaluate_structural_indicators(events, INDICATORS, observation_date="2026-08-08")[0]
        self.assertEqual(obs.direction, "mixed")
        self.assertEqual(obs.support_score, obs.counter_score)
        self.assertEqual(obs.confidence, 0)
        self.assertIn("high-conflict", obs.one_sentence_read)


class RollingWindowTests(unittest.TestCase):
    def test_rolling_windows_only_use_real_observations(self) -> None:
        observations = evaluate_structural_indicators([_event(title="AI capex overinvestment drives AI bubble")], INDICATORS, observation_date="2026-07-08")
        observations += evaluate_structural_indicators([_event(title="AI capex overinvestment lifts AI valuation")], INDICATORS, observation_date="2026-07-10")
        summary = rolling_summary(observations, as_of="2026-07-10")
        self.assertEqual(summary["current"]["status"], "observed")
        self.assertEqual(summary["rolling_7d"]["observations"], 2)

    def test_empty_window_is_insufficient_not_fabricated(self) -> None:
        insufficient = evaluate_structural_indicators([_event(title="neutral")], INDICATORS, observation_date="2026-01-01")
        self.assertEqual(rolling_summary(insufficient, as_of="2026-07-10")["rolling_7d"]["status"], "insufficient")


if __name__ == "__main__":
    unittest.main()
