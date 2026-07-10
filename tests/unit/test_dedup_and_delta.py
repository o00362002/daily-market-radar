import unittest

from radar.domain.models import Document
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.deltas import classify_event_delta, material_events, reconcile_cross_day_events


class DedupAndDeltaTests(unittest.TestCase):
    def test_multilingual_same_event_clusters_together(self) -> None:
        docs = [
            Document.fixture(
                source_id="openai_news",
                url="https://openai.com/news/agent-runtime",
                title="OpenAI launches agent runtime in Tokyo",
                language="en",
                macro_region="East Asia",
                entities=["OpenAI"],
                action="launches",
                object="agent runtime",
                location="Tokyo",
                published_at="2026-07-10T01:00:00+08:00",
            ),
            Document.fixture(
                source_id="nikkei",
                url="https://example.jp/openai-agent",
                title="OpenAI、東京でエージェント基盤を発表",
                language="ja",
                macro_region="East Asia",
                entities=["OpenAI"],
                action="launches",
                object="agent runtime",
                location="Tokyo",
                published_at="2026-07-10T02:00:00+08:00",
            ),
        ]
        events = cluster_documents(docs)
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0].event_id.startswith("evt_"))
        self.assertEqual(events[0].event_id, cluster_documents(docs)[0].event_id)

    def test_same_topic_different_event_does_not_merge(self) -> None:
        docs = [
            Document.fixture(
                source_id="retail_dive",
                url="https://example.com/a",
                title="Retailer A opens new small-format stores",
                entities=["Retailer A"],
                action="opens",
                object="small-format stores",
                location="US",
            ),
            Document.fixture(
                source_id="retail_dive",
                url="https://example.com/b",
                title="Retailer B cuts outlet expansion plan",
                entities=["Retailer B"],
                action="cuts",
                object="outlet expansion",
                location="US",
            ),
        ]
        self.assertEqual(len(cluster_documents(docs)), 2)

    def test_new_material_number_is_delta_not_replay(self) -> None:
        prior = Document.fixture(
            source_id="twse",
            url="https://example.tw/old",
            title="TWSE reports ETF flows",
            entities=["TWSE"],
            action="reports",
            object="ETF flows",
            location="Taiwan",
            facts={"flow_usd_m": 200},
        )
        current = Document.fixture(
            source_id="twse",
            url="https://example.tw/new",
            title="TWSE updates ETF flows to 280m",
            entities=["TWSE"],
            action="reports",
            object="ETF flows",
            location="Taiwan",
            facts={"flow_usd_m": 280},
        )
        delta = classify_event_delta(prior, current)
        self.assertEqual(delta.delta_type, "same_event_new_delta")
        self.assertIn("flow_usd_m", delta.changed_fields)

    def test_cross_day_same_signature_preserves_first_seen_and_records_material_delta(self) -> None:
        prior = Document.fixture(
            source_id="twse",
            url="https://example.tw/old",
            title="TWSE reports ETF flows",
            entities=["TWSE"],
            action="reports",
            object="ETF flows",
            location="Taiwan",
            facts={"flow_usd_m": 200},
            fetched_at="2026-07-09T08:01:00+00:00",
        )
        current = Document.fixture(
            source_id="twse",
            url="https://example.tw/new",
            title="TWSE updates ETF flows to 280m",
            entities=["TWSE"],
            action="reports",
            object="ETF flows",
            location="Taiwan",
            facts={"flow_usd_m": 280},
            fetched_at="2026-07-10T08:01:00+00:00",
        )
        prior_event = cluster_documents([prior])[0]
        current_event = cluster_documents([current])[0]

        reconciled = reconcile_cross_day_events([current_event], [prior_event])

        self.assertEqual(len(reconciled), 1)
        self.assertEqual(reconciled[0].event_id, prior_event.event_id)
        self.assertEqual(reconciled[0].first_seen_at, prior_event.first_seen_at)
        self.assertEqual(reconciled[0].last_material_delta_at, current_event.last_seen_at)
        self.assertEqual(reconciled[0].deltas[0].delta_type, "same_event_new_delta")
        self.assertIn("flow_usd_m", reconciled[0].deltas[0].changed_fields)
        self.assertEqual(material_events(reconciled), reconciled)

    def test_cross_day_replay_is_not_reportable_material_event(self) -> None:
        prior = Document.fixture(
            source_id="twse",
            url="https://example.tw/old",
            title="TWSE reports ETF flows",
            entities=["TWSE"],
            action="reports",
            object="ETF flows",
            location="Taiwan",
            facts={"flow_usd_m": 200},
            fetched_at="2026-07-09T08:01:00+00:00",
        )
        replay = Document.fixture(
            source_id="twse",
            url="https://example.tw/replay",
            title="TWSE reports ETF flows",
            entities=["TWSE"],
            action="reports",
            object="ETF flows",
            location="Taiwan",
            facts={"flow_usd_m": 200},
            fetched_at="2026-07-10T08:01:00+00:00",
        )

        reconciled = reconcile_cross_day_events(cluster_documents([replay]), cluster_documents([prior]))

        self.assertEqual(reconciled[0].deltas[0].delta_type, "duplicate_document")
        self.assertEqual(material_events(reconciled), [])


if __name__ == "__main__":
    unittest.main()
