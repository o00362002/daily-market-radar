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


if __name__ == "__main__":
    unittest.main()
