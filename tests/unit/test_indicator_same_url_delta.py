from __future__ import annotations

import unittest

from radar.domain.models import Document
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deltas import classify_event_material_delta, resolve_events


class IndicatorSameUrlDeltaTests(unittest.TestCase):
    def test_changed_bls_fact_at_same_url_is_material(self) -> None:
        prior = _measurement_document(
            facts={"rate_labor_productivity_yoy": 2.1},
            fetched_at="2026-08-17T04:00:00+00:00",
        )
        current = _measurement_document(
            facts={"rate_labor_productivity_yoy": 2.8},
            fetched_at="2026-08-18T04:00:00+00:00",
        )
        prior_event = cluster_documents([prior])[0]
        current_event = cluster_documents([current])[0]

        direct = classify_event_material_delta(prior_event, current_event)
        self.assertEqual(direct.delta_type, "new_amount_or_metric")
        self.assertEqual(direct.changed_fields, ["rate_labor_productivity_yoy"])

        outcome = resolve_events(
            [current_event],
            [prior_event],
            observed_at="2026-08-18T04:00:00+00:00",
        )
        self.assertEqual(outcome.events[0].deltas[0].delta_type, "new_amount_or_metric")
        self.assertEqual(outcome.events[0].last_material_delta_at, current_event.last_seen_at)
        self.assertEqual(outcome.material_events, 1)
        self.assertEqual(outcome.unchanged_events, 0)
        self.assertEqual(outcome.duplicate_only_events, 0)
        self.assertEqual(outcome.delta_type_counts, {"new_amount_or_metric": 1})

    def test_changed_funding_fact_uses_funding_delta_family(self) -> None:
        prior = _measurement_document(
            source_id="hyperliquid_perp",
            url="https://api.hyperliquid.xyz/info",
            facts={"funding_rate_current": 0.0001},
            fetched_at="2026-08-17T04:00:00+00:00",
        )
        current = _measurement_document(
            source_id="hyperliquid_perp",
            url="https://api.hyperliquid.xyz/info",
            facts={"funding_rate_current": 0.0003},
            fetched_at="2026-08-18T04:00:00+00:00",
        )
        delta = classify_event_material_delta(
            cluster_documents([prior])[0],
            cluster_documents([current])[0],
        )
        self.assertEqual(delta.delta_type, "funding_change")
        self.assertEqual(delta.changed_fields, ["funding_rate_current"])

    def test_unchanged_indicator_at_same_url_remains_duplicate(self) -> None:
        prior = _measurement_document(
            facts={"rate_labor_productivity_yoy": 2.8},
            fetched_at="2026-08-17T04:00:00+00:00",
        )
        current = _measurement_document(
            facts={"rate_labor_productivity_yoy": 2.8},
            fetched_at="2026-08-18T04:00:00+00:00",
        )
        outcome = resolve_events(
            cluster_documents([current]),
            cluster_documents([prior]),
            observed_at="2026-08-18T04:00:00+00:00",
        )
        self.assertEqual(outcome.events[0].deltas[0].delta_type, "duplicate_document")
        self.assertEqual(outcome.material_events, 0)
        self.assertEqual(outcome.unchanged_events, 1)
        self.assertEqual(outcome.duplicate_only_events, 1)

    def test_non_indicator_same_url_keeps_existing_news_semantics(self) -> None:
        prior = _measurement_document(
            lane="top_down",
            facts={"revenue_usd_m": 100.0},
            fetched_at="2026-08-17T04:00:00+00:00",
        )
        current = _measurement_document(
            lane="top_down",
            facts={"revenue_usd_m": 120.0},
            fetched_at="2026-08-18T04:00:00+00:00",
        )
        outcome = resolve_events(
            cluster_documents([current]),
            cluster_documents([prior]),
            observed_at="2026-08-18T04:00:00+00:00",
        )
        self.assertEqual(outcome.events[0].deltas[0].delta_type, "duplicate_document")


def _measurement_document(
    *,
    facts: dict[str, object],
    fetched_at: str,
    source_id: str = "bls_productivity",
    url: str = "https://www.bls.gov/productivity/",
    lane: str = "indicator_only",
) -> Document:
    return Document.fixture(
        source_id=source_id,
        url=url,
        title="Stable structured measurement snapshot",
        summary="A typed structured measurement snapshot.",
        entities=[source_id],
        action="measures",
        object="stable structured indicators",
        location="Global",
        primary_domain="global_markets_macro",
        lane=lane,
        facts={"source_roles": ["data"], **facts},
        published_at="2026-06-30T00:00:00+00:00",
        fetched_at=fetched_at,
    )


if __name__ == "__main__":
    unittest.main()
