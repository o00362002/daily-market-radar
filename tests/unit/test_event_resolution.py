from __future__ import annotations

import unittest

from radar.domain.event_resolution import (
    EventResolutionService,
    classify_document_delta,
    classify_event_delta,
    is_material_delta_type,
)
from radar.domain.models import Document
from radar.pipeline.cluster import cluster_documents

OBSERVED_AT = "2026-07-10T08:00:00+00:00"


def _doc(**kwargs) -> Document:
    base = dict(
        source_id="src",
        url="https://example.com/a",
        title="Title",
        entities=["Entity"],
        action="acts",
        object="thing",
        location="US",
        macro_region="North America",
        published_at="2026-07-10T08:00:00+00:00",
        fetched_at="2026-07-10T08:01:00+00:00",
    )
    base.update(kwargs)
    return Document.fixture(**base)


def _event(document: Document):
    return cluster_documents([document])[0]


class MatchCascadeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EventResolutionService()

    def _resolve_one(self, current: Document, prior: Document):
        outcome = self.service.resolve([_event(current)], [_event(prior)], observed_at=OBSERVED_AT)
        return outcome, outcome.match_records[0]

    def test_canonical_url_match(self) -> None:
        prior = _doc(url="https://example.com/story", title="First headline")
        current = _doc(url="https://example.com/story", title="Rewritten headline")
        _, record = self._resolve_one(current, prior)
        self.assertEqual(record.strategy, "canonical_url")
        self.assertEqual(record.prior_event_id, _event(prior).event_id)

    def test_content_hash_match(self) -> None:
        prior = _doc(url="https://example.com/old", title="Identical body", summary="same")
        current = _doc(url="https://example.com/new", title="Identical body", summary="same")
        _, record = self._resolve_one(current, prior)
        self.assertEqual(record.strategy, "content_hash")

    def test_exact_event_signature_match(self) -> None:
        prior = _doc(url="https://example.com/one", title="Alpha", entities=["OpenAI"], action="launches", object="runtime", location="Tokyo")
        current = _doc(url="https://example.com/two", title="Beta", summary="different", entities=["OpenAI"], action="launches", object="runtime", location="Tokyo")
        _, record = self._resolve_one(current, prior)
        self.assertEqual(record.strategy, "exact_event_signature")
        self.assertEqual(record.matched_fields, ("entity", "action", "object", "location"))

    def test_entity_action_object_location_normalized_match(self) -> None:
        prior = _doc(url="https://example.com/one", title="Alpha", entities=["OpenAI"], action="launches", object="runtime", location="Tokyo")
        current = _doc(url="https://example.com/two", title="Beta", entities=["OpenAI"], action="launches", object="runtime", location="Osaka")
        outcome, record = self._resolve_one(current, prior)
        self.assertEqual(record.strategy, "normalized_entity_action_object_location")
        self.assertEqual(outcome.matched_existing_events, 1)

    def test_unrelated_event_is_not_merged(self) -> None:
        prior = _doc(url="https://example.com/retailer-a", title="Retailer A opens small-format stores", entities=["Retailer A"], action="opens", object="stores", location="US")
        current = _doc(url="https://example.com/retailer-b", title="Retailer B cuts outlet expansion", entities=["Retailer B"], action="cuts", object="expansion", location="US")
        outcome, record = self._resolve_one(current, prior)
        self.assertIsNone(record.prior_event_id)
        self.assertEqual(outcome.new_events, 1)
        self.assertEqual(outcome.matched_existing_events, 0)

    def test_ambiguous_match_is_unresolved_and_not_forced(self) -> None:
        prior_one = _doc(url="https://example.com/p1", title="ACME widget in the US", entities=["ACME"], action="acts", object="widget", location="US")
        prior_two = _doc(url="https://example.com/p2", title="ACME widget in the EU", entities=["ACME"], action="acts", object="widget", location="EU")
        current = _doc(url="https://example.com/c", title="ACME widget in Japan", entities=["ACME"], action="acts", object="widget", location="JP")
        outcome = self.service.resolve(
            [_event(current)],
            [_event(prior_one), _event(prior_two)],
            observed_at=OBSERVED_AT,
        )
        record = outcome.match_records[0]
        self.assertEqual(record.strategy, "unresolved")
        self.assertIsNone(record.prior_event_id)
        self.assertEqual(len(outcome.unresolved_matches), 1)
        # Not forced: a new event is created rather than a wrong merge.
        self.assertEqual(outcome.new_events, 1)


class DeltaTaxonomyTests(unittest.TestCase):
    def _same_event(self, **current_kwargs):
        prior = _doc(url="https://example.com/prior", **{k: v for k, v in current_kwargs.items() if k == "facts" and False})
        return prior

    def test_numeric_fact_change_becomes_new_amount_or_metric(self) -> None:
        prior = _doc(url="https://example.com/a", facts={"flow_usd_m": 200})
        current = _doc(url="https://example.com/b", facts={"flow_usd_m": 280})
        delta = classify_document_delta(prior, current)
        self.assertEqual(delta.delta_type, "new_amount_or_metric")
        self.assertIn("flow_usd_m", delta.changed_fields)
        self.assertTrue(is_material_delta_type(delta.delta_type))

    def test_funding_metric_change_becomes_funding_change(self) -> None:
        prior = _doc(url="https://example.com/a", facts={"funding_usd_m": 50})
        current = _doc(url="https://example.com/b", facts={"funding_usd_m": 120})
        delta = classify_document_delta(prior, current)
        self.assertEqual(delta.delta_type, "funding_change")

    def test_title_only_rewrite_is_not_material(self) -> None:
        # Neutral action/object avoid lifecycle keywords; only the title changes.
        prior = _doc(url="https://example.com/a", title="Neutral phrasing one", action="acts", object="thing")
        current = _doc(url="https://example.com/b", title="Neutral phrasing two", action="acts", object="thing")
        delta = classify_document_delta(prior, current)
        self.assertEqual(delta.delta_type, "no_material_change")
        self.assertFalse(is_material_delta_type(delta.delta_type))
        self.assertEqual(delta.changed_fields, ["title"])

    def test_summary_only_rewrite_is_not_material(self) -> None:
        prior = _doc(url="https://example.com/a", title="Steady", summary="First summary", action="acts", object="thing")
        current = _doc(url="https://example.com/b", title="Steady", summary="Reworded summary", action="acts", object="thing")
        delta = classify_document_delta(prior, current)
        self.assertEqual(delta.delta_type, "no_material_change")
        self.assertEqual(delta.changed_fields, ["summary"])

    def test_new_region_delta(self) -> None:
        # Same entity/action/object/location keeps them one event; only macro_region differs.
        prior = _doc(url="https://example.com/a", title="Brand expands stores wave one", entities=["Brand"], action="expands", object="stores", location="Asia", macro_region="North America")
        current = _doc(url="https://example.com/b", title="Brand expands stores wave two", entities=["Brand"], action="expands", object="stores", location="Asia", macro_region="Taiwan")
        delta = classify_document_delta(prior, current)
        self.assertEqual(delta.delta_type, "new_region")

    def test_policy_stage_change(self) -> None:
        prior = _doc(url="https://example.com/a", entities=["Regulator"], action="drafts", object="rule", title="Regulator drafts rule")
        current = _doc(url="https://example.com/b", entities=["Regulator"], action="drafts", object="rule", title="Regulator approves the rule")
        delta = classify_document_delta(prior, current)
        self.assertEqual(delta.delta_type, "policy_stage_change")

    def test_cancellation_and_invalidation(self) -> None:
        prior = _doc(url="https://example.com/a", entities=["Firm"], action="plans", object="project", title="Firm plans project")
        cancelled = _doc(url="https://example.com/b", entities=["Firm"], action="plans", object="project", title="Firm cancels the project")
        invalidated = _doc(url="https://example.com/c", entities=["Firm"], action="plans", object="project", title="Report retracted as false")
        self.assertEqual(classify_document_delta(prior, cancelled).delta_type, "cancellation")
        self.assertEqual(classify_document_delta(prior, invalidated).delta_type, "invalidation")

    def test_duplicate_document(self) -> None:
        prior = _doc(url="https://example.com/same", title="Same", summary="same")
        current = _doc(url="https://example.com/same", title="Same", summary="same")
        self.assertEqual(classify_document_delta(prior, current).delta_type, "duplicate_document")
        self.assertFalse(is_material_delta_type("duplicate_document"))


class SourceConfirmationTests(unittest.TestCase):
    def test_new_independent_official_source_becomes_confirmation(self) -> None:
        prior = _doc(
            source_id="reuters",
            url="https://reuters.com/story",
            title="Event happens",
            entities=["Gov"],
            action="announces",
            object="policy",
            facts={"source_roles": ["official"]},
        )
        current = _doc(
            source_id="twse",
            url="https://twse.com.tw/story",
            title="Event happens (official filing)",
            entities=["Gov"],
            action="announces",
            object="policy",
            facts={"source_roles": ["official"]},
        )
        delta = classify_event_delta(cluster_documents([prior])[0], cluster_documents([current])[0])
        self.assertEqual(delta.delta_type, "new_source_confirmation")
        self.assertTrue(is_material_delta_type(delta.delta_type))

    def test_same_publisher_duplicate_is_not_confirmation(self) -> None:
        prior = _doc(
            source_id="reuters",
            url="https://reuters.com/story-1",
            title="Event happens",
            entities=["Gov"],
            action="announces",
            object="policy",
            facts={"source_roles": ["official"]},
        )
        current = _doc(
            source_id="reuters",
            url="https://reuters.com/story-2",
            title="Event happens reworded",
            entities=["Gov"],
            action="announces",
            object="policy",
            facts={"source_roles": ["official"]},
        )
        delta = classify_event_delta(cluster_documents([prior])[0], cluster_documents([current])[0])
        self.assertNotEqual(delta.delta_type, "new_source_confirmation")
        self.assertFalse(is_material_delta_type(delta.delta_type))


class AuditCounterTests(unittest.TestCase):
    def test_counters_are_consistent(self) -> None:
        service = EventResolutionService()
        prior = _doc(url="https://example.com/prior", facts={"flow_usd_m": 200})
        changed = _doc(url="https://example.com/changed", facts={"flow_usd_m": 280})
        replay = _doc(url="https://example.com/replay", facts={"flow_usd_m": 200})
        brand_new = _doc(entities=["Fresh"], action="debuts", object="startup", url="https://example.com/fresh")

        outcome = service.resolve(
            cluster_documents([changed, replay, brand_new]),
            cluster_documents([prior]),
            observed_at=OBSERVED_AT,
        )
        # changed + replay share the prior signature -> clustered into one current event;
        # brand_new is a separate new event.
        self.assertEqual(outcome.events_observed, outcome.new_events + outcome.matched_existing_events)
        self.assertEqual(outcome.material_events + outcome.unchanged_events, outcome.events_observed)
        self.assertGreaterEqual(outcome.new_events, 1)
        self.assertIn("new_event", outcome.delta_type_counts)
        self.assertTrue(outcome.match_strategy_counts)


if __name__ == "__main__":
    unittest.main()
