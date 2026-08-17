from __future__ import annotations

import unittest

from radar.domain.models import Document
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deltas import resolve_events


def doc(*, source_id: str, title: str, published_at: str, domain: str = "crypto_rwa_agent_payments") -> Document:
    return Document.fixture(
        source_id=source_id,
        url=f"https://{source_id}.example/story",
        title=title,
        published_at=published_at,
        fetched_at=published_at,
        entities=[source_id],
        action="publishes",
        object=title,
        location="Global",
        primary_domain=domain,
    )


class SameRunCoalesceTests(unittest.TestCase):
    def test_cross_language_safepal_breach_siblings_merge_before_resolution(self) -> None:
        documents = [
            doc(
                source_id="source_a",
                title="SafePal reveals a data breach exposing customer order information",
                published_at="2026-08-17T01:00:00+00:00",
            ),
            doc(
                source_id="source_b",
                title="加密錢包商 SafePal 主動揭露資料外洩，近四萬名客戶訂單地址曝光",
                published_at="2026-08-17T02:00:00+00:00",
            ),
            doc(
                source_id="source_c",
                title="SafePal 驚傳資料外洩：近 4 萬客戶訂單個資曝光",
                published_at="2026-08-17T03:00:00+00:00",
            ),
        ]
        clustered = cluster_documents(documents)
        self.assertEqual(len(clustered), 3)

        outcome = resolve_events(clustered, [], observed_at="2026-08-17T04:00:00+00:00")

        self.assertEqual(len(outcome.events), 1)
        self.assertEqual(len(outcome.events[0].documents), 3)
        self.assertEqual(outcome.new_events, 1)

    def test_same_named_company_generic_launches_are_not_coalesced(self) -> None:
        documents = [
            doc(
                source_id="source_a",
                title="Microsoft launches new retail AI assistant",
                published_at="2026-08-17T01:00:00+00:00",
                domain="ai_agents_applications",
            ),
            doc(
                source_id="source_b",
                title="Microsoft launches new cloud developer database service",
                published_at="2026-08-17T02:00:00+00:00",
                domain="ai_agents_applications",
            ),
        ]
        outcome = resolve_events(cluster_documents(documents), [], observed_at="2026-08-17T03:00:00+00:00")
        self.assertEqual(len(outcome.events), 2)

    def test_same_entity_and_family_outside_window_are_not_coalesced(self) -> None:
        documents = [
            doc(
                source_id="source_a",
                title="SafePal reveals a data breach exposing customers",
                published_at="2026-08-15T01:00:00+00:00",
            ),
            doc(
                source_id="source_b",
                title="SafePal reports another data breach affecting customers",
                published_at="2026-08-17T02:00:00+00:00",
            ),
        ]
        outcome = resolve_events(cluster_documents(documents), [], observed_at="2026-08-17T03:00:00+00:00")
        self.assertEqual(len(outcome.events), 2)

    def test_same_entity_family_across_different_domains_are_not_coalesced(self) -> None:
        documents = [
            doc(
                source_id="source_a",
                title="SafePal reveals a data breach exposing customers",
                published_at="2026-08-17T01:00:00+00:00",
                domain="crypto_rwa_agent_payments",
            ),
            doc(
                source_id="source_b",
                title="SafePal reveals a data breach in retail customer system",
                published_at="2026-08-17T02:00:00+00:00",
                domain="retail_consumer_fashion",
            ),
        ]
        outcome = resolve_events(cluster_documents(documents), [], observed_at="2026-08-17T03:00:00+00:00")
        self.assertEqual(len(outcome.events), 2)


if __name__ == "__main__":
    unittest.main()
