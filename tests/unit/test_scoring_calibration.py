from __future__ import annotations

import unittest

from radar.domain.models import Document
from radar.domain.scoring import explain_event_scores
from radar.pipeline.cluster import cluster_documents


def event_for(*documents: Document):
    return cluster_documents(list(documents))[0]


def document(
    *,
    source_id: str,
    roles: list[str],
    url: str,
    facts: dict[str, object] | None = None,
) -> Document:
    payload: dict[str, object] = {"source_roles": roles}
    payload.update(facts or {})
    return Document.fixture(
        source_id=source_id,
        url=url,
        title="Company reports quarterly revenue update",
        entities=["Example Company"],
        action="reports",
        object="quarterly revenue",
        location="US",
        primary_domain="global_markets_macro",
        facts=payload,
    )


class ScoringCalibrationTests(unittest.TestCase):
    def test_source_roles_metadata_is_not_numeric_support(self) -> None:
        event = event_for(
            document(
                source_id="generic_news",
                roles=["media"],
                url="https://example.com/news",
            )
        )
        score = explain_event_scores(event)

        self.assertEqual(score.confidence.components["numeric_support"], 55)

    def test_real_measurement_fact_raises_numeric_support(self) -> None:
        event = event_for(
            document(
                source_id="official_data",
                roles=["official", "data"],
                url="https://example.com/data",
                facts={"revenue_usd_m": 125.0},
            )
        )
        score = explain_event_scores(event)

        self.assertEqual(score.confidence.components["numeric_support"], 82)

    def test_primary_source_role_scores_above_untyped_secondary(self) -> None:
        primary = explain_event_scores(
            event_for(
                document(
                    source_id="company_newsroom",
                    roles=["company", "official"],
                    url="https://company.example/news",
                )
            )
        )
        secondary = explain_event_scores(
            event_for(
                document(
                    source_id="generic_news",
                    roles=["media"],
                    url="https://example.com/news",
                )
            )
        )

        self.assertEqual(primary.confidence.components["source_quality"], 88)
        self.assertEqual(secondary.confidence.components["source_quality"], 66)
        self.assertGreater(primary.confidence.score, secondary.confidence.score)

    def test_high_quality_secondary_has_distinct_role_tier(self) -> None:
        score = explain_event_scores(
            event_for(
                document(
                    source_id="wire_service",
                    roles=["news_agency"],
                    url="https://wire.example/story",
                )
            )
        )

        self.assertEqual(score.confidence.components["source_quality"], 82)

    def test_independent_confirmation_increases_evidence_depth_and_confidence(self) -> None:
        one = document(
            source_id="wire_service",
            roles=["news_agency"],
            url="https://wire.example/story",
        )
        two = document(
            source_id="national_news",
            roles=["national"],
            url="https://national.example/story",
        )
        single = explain_event_scores(event_for(one))
        corroborated = explain_event_scores(event_for(one, two))

        self.assertGreater(
            corroborated.confidence.components["evidence_depth"],
            single.confidence.components["evidence_depth"],
        )
        self.assertGreater(corroborated.confidence.score, single.confidence.score)


if __name__ == "__main__":
    unittest.main()
