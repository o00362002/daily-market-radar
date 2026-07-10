from __future__ import annotations

import json
import unittest
from dataclasses import dataclass
from typing import Callable

from radar.adapters.composite import CompositeSourceAdapter
from radar.adapters.freshrss_source import FreshRssRegistrySourceAdapter
from radar.adapters.transport import HttpRequest, HttpResponse
from radar.domain.models import Document
from radar.ports.sources import (
    CredentialsStatusV1,
    RateLimitPolicy,
    RetryPolicy,
    SourceFetchRequest,
    SourceFetchResult,
    SourceHealthV1,
)
from radar.schemas.source import Source, SourceAdapterConfig, SourceRegistry


class FakeTransport:
    def __init__(self, handler: Callable[[HttpRequest], HttpResponse]) -> None:
        self.handler = handler
        self.requests: list[HttpRequest] = []

    def fetch(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        return self.handler(request)


def _source() -> Source:
    return Source(
        source_id="feed_source",
        name="Feed Source",
        canonical_url="https://feed.example/",
        publisher_country="US",
        macro_region="North America",
        languages=["en"],
        source_roles=["official"],
        domains=["ai_agents_applications"],
        ownership_profile="official",
        evidence_profile="primary",
        priority="high",
        adapters=[SourceAdapterConfig(kind="rss", url="https://feed.example/rss")],
        fetch_interval_minutes=60,
        freshness_slo_minutes=180,
        usage_policy="public",
        fulltext_policy="metadata_summary_only",
        enabled=True,
        verification_status="verified",
        last_verified_at="2026-07-01",
        aliases=[],
    )


@dataclass(frozen=True)
class StaticSourceAdapter:
    adapter_id: str
    source_id: str
    result: SourceFetchResult
    available: bool = True
    retry_policy: RetryPolicy = RetryPolicy()
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()

    def credentials_status(self) -> CredentialsStatusV1:
        return CredentialsStatusV1(self.available, "missing test credential" if not self.available else "")

    def health_check(self) -> SourceHealthV1:
        return SourceHealthV1("healthy")

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        del request
        return self.result

    def normalize(self, result: SourceFetchResult) -> list[Document]:
        return list(result.documents)


class CompositeSourceAdapterTests(unittest.TestCase):
    def test_missing_optional_credentials_do_not_stop_healthy_child(self) -> None:
        document = Document.fixture(source_id="direct", url="https://example.com/a", title="A")
        direct = StaticSourceAdapter(
            adapter_id="rss_atom",
            source_id="registry",
            result=SourceFetchResult(documents=(document,), sources_checked=("direct",)),
        )
        optional = StaticSourceAdapter(
            adapter_id="optional_reader",
            source_id="reader",
            result=SourceFetchResult(documents=()),
            available=False,
        )

        adapter = CompositeSourceAdapter((direct, optional))
        result = adapter.fetch(SourceFetchRequest(date="2026-07-11", profile="daily_push"))

        self.assertEqual(result.documents, (document,))
        self.assertIn("direct", result.sources_checked)
        self.assertIn("reader", result.sources_not_executed)
        self.assertIn("optional_reader_credential_unavailable", result.degradation_reasons)
        self.assertEqual(dict(result.integration_status)["optional_reader"], "credential_unavailable")
        self.assertEqual(adapter.health_check().status, "partial")


class FreshRssRegistrySourceAdapterTests(unittest.TestCase):
    def test_missing_credentials_returns_explicit_gap_without_network(self) -> None:
        transport = FakeTransport(lambda request: HttpResponse(500, request.url, {}, b""))
        adapter = FreshRssRegistrySourceAdapter(
            SourceRegistry([_source()]),
            transport,
            env=lambda _key: None,
        )

        result = adapter.fetch(SourceFetchRequest(date="2026-07-11", profile="daily_push"))

        self.assertEqual(result.documents, ())
        self.assertIn("freshrss_credentials_unavailable", result.degradation_reasons)
        self.assertEqual(dict(result.integration_status)["collection_aggregator"], "credential_unavailable")
        self.assertEqual(transport.requests, [])

    def test_reader_items_map_back_to_canonical_registry_source(self) -> None:
        payload = {
            "items": [
                {
                    "id": "item-1",
                    "title": "Official agent pilot",
                    "published": 1783737600,
                    "canonical": [{"href": "https://feed.example/story"}],
                    "origin": {"streamId": "feed/https://feed.example/rss"},
                }
            ]
        }

        def handler(request: HttpRequest) -> HttpResponse:
            if "ClientLogin" in request.url:
                return HttpResponse(200, request.url, {}, b"Auth=token-123\n")
            return HttpResponse(
                200,
                request.url,
                {"Content-Type": "application/json"},
                json.dumps(payload).encode("utf-8"),
            )

        env = {
            "FRESHRSS_BASE_URL": "https://reader.example",
            "FRESHRSS_USERNAME": "user",
            "FRESHRSS_API_PASSWORD": "password",
        }
        adapter = FreshRssRegistrySourceAdapter(
            SourceRegistry([_source()]),
            FakeTransport(handler),
            env=env.get,
        )

        result = adapter.fetch(SourceFetchRequest(date="2026-07-11", profile="daily_push"))

        self.assertEqual(len(result.documents), 1)
        self.assertEqual(result.documents[0].source_id, "feed_source")
        self.assertEqual(result.documents[0].url, "https://feed.example/story")
        self.assertEqual(dict(result.integration_status)["collection_aggregator"], "checked")
        self.assertEqual(result.sources_checked, ("feed_source",))


if __name__ == "__main__":
    unittest.main()
