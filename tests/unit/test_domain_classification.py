from __future__ import annotations

import unittest

from radar.domain.models import Document
from radar.pipeline.domain_classification import classify_document_domain


class DomainClassificationTests(unittest.TestCase):
    def test_content_can_override_source_domain_prior(self) -> None:
        document = Document.fixture(
            title="AI agent automates enterprise customer service",
            summary="The model deployment reduces manual workflow cost.",
            primary_domain="global_markets_macro",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "ai_agents_applications")
        self.assertIn("ai", result.matched_terms)

    def test_legacy_labor_alias_maps_to_global_domain(self) -> None:
        document = Document.fixture(
            title="Labor office reports wage pressure",
            primary_domain="labor_demographics_consumption_pressure",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "global_markets_macro")

    def test_source_domain_is_fallback_when_content_is_weak(self) -> None:
        document = Document.fixture(
            title="Weekly update",
            primary_domain="retail_consumer_fashion",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "retail_consumer_fashion")
        self.assertTrue(result.source_prior_used)

    def test_software_token_does_not_turn_claude_code_into_crypto_even_from_crypto_source(self) -> None:
        document = Document.fixture(
            title="Claude Code session token budget and context token usage guide",
            summary="Developers can inspect model context windows and API token counts.",
            primary_domain="crypto_rwa_agent_payments",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "ai_agents_applications")
        self.assertIn("claude", result.matched_terms)
        self.assertNotIn("token", result.matched_terms)

    def test_named_model_anchor_can_override_wrong_source_prior(self) -> None:
        document = Document.fixture(
            title="Anthropic releases new Claude model for developers",
            summary="Claude Code gains new coding capabilities.",
            primary_domain="crypto_rwa_agent_payments",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "ai_agents_applications")
        self.assertIn("anthropic", result.matched_terms)

    def test_app_store_phishing_does_not_turn_crypto_wallet_story_into_retail(self) -> None:
        document = Document.fixture(
            title="Fake DefiLlama wallet app removed from App Store after phishing reports",
            summary="The crypto wallet impersonated a DeFi analytics service.",
            primary_domain="crypto_rwa_agent_payments",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "crypto_rwa_agent_payments")
        self.assertNotIn("store", result.matched_terms)

    def test_retail_investors_are_market_participants_not_retail_industry(self) -> None:
        document = Document.fixture(
            title="Retail investors buy technology stocks after rate cut bets rise",
            summary="Fund flows and stock market positioning changed during the session.",
            primary_domain="global_markets_macro",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "global_markets_macro")
        self.assertNotIn("retail", result.matched_terms)

    def test_department_of_commerce_does_not_become_retail_commerce(self) -> None:
        document = Document.fixture(
            title="Department of Commerce reports inflation-adjusted trade data",
            summary="The policy release moved bond yields and the dollar.",
            primary_domain="global_markets_macro",
        )
        result = classify_document_domain(document)
        self.assertEqual(result.domain, "global_markets_macro")
        self.assertNotIn("commerce", result.matched_terms)


if __name__ == "__main__":
    unittest.main()
