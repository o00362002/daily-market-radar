from __future__ import annotations

import json
import unittest
from typing import Callable

from radar.adapters.base import AdapterError, UrlPolicy
from radar.adapters.freshrss import FreshRssAdapter
from radar.adapters.gdelt_discovery import GdeltDiscoveryAdapter
from radar.adapters.json_api import GenericJsonApiAdapter, JsonApiConfig
from radar.adapters.rss_client import ConditionalRssClient, backoff_delays, fetch_with_retry
from radar.adapters.safe_web import SafeWebFetcher
from radar.adapters.social_channels import OfficialSocialApiAdapter, PublicSocialChannelAdapter
from radar.adapters.transport import HttpRequest, HttpResponse
from radar.schemas.source import Source, SourceAdapterConfig


class FakeTransport:
    """Programmable offline transport that records every request."""

    def __init__(self, handler: Callable[[HttpRequest], HttpResponse]) -> None:
        self._handler = handler
        self.requests: list[HttpRequest] = []

    def fetch(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        return self._handler(request)


def _html(body: str, content_type: str = "text/html") -> HttpResponse:
    return HttpResponse(status=200, url="https://example.com", headers={"Content-Type": content_type}, body=body.encode("utf-8"))


class SafeWebSsrfTests(unittest.TestCase):
    def _fetcher(self) -> SafeWebFetcher:
        transport = FakeTransport(lambda request: _html("<html><head><title>Ok</title></head><body>Hello world body text</body></html>"))
        return SafeWebFetcher(transport, policy=UrlPolicy(allow_internal_hosts=set()))

    def test_rejects_url_outside_allowlist(self) -> None:
        with self.assertRaises(AdapterError):
            self._fetcher().fetch("https://evil.example/x", source_id="s", allowlist={"https://good.example/x"})

    def test_blocks_ssrf_even_when_allowlisted(self) -> None:
        fetcher = self._fetcher()
        for url in [
            "http://localhost/x",
            "http://127.0.0.1/x",
            "http://10.0.0.5/x",
            "http://169.254.169.254/latest/meta-data",
            "file:///etc/passwd",
        ]:
            with self.subTest(url=url):
                with self.assertRaises(AdapterError):
                    fetcher.fetch(url, source_id="s", allowlist={url})

    def test_fetches_allowlisted_public_url_with_bounded_excerpt(self) -> None:
        fetcher = self._fetcher()
        url = "https://good.example/story"
        doc = fetcher.fetch(url, source_id="good", allowlist={url})
        self.assertEqual(doc.title, "Ok")
        self.assertIn("Hello world", doc.excerpt)
        self.assertTrue(doc.content_hash.startswith("web_"))

    def test_rejects_disallowed_content_type(self) -> None:
        transport = FakeTransport(lambda request: HttpResponse(200, request.url, {"Content-Type": "application/pdf"}, b"%PDF"))
        fetcher = SafeWebFetcher(transport, policy=UrlPolicy(allow_internal_hosts=set()))
        with self.assertRaises(AdapterError):
            fetcher.fetch("https://good.example/x", source_id="s", allowlist={"https://good.example/x"})


class JsonApiTests(unittest.TestCase):
    def test_page_pagination_stops_on_empty_page(self) -> None:
        def handler(request: HttpRequest) -> HttpResponse:
            page = "2" if "page=2" in request.url else "1"
            items = [{"headline": "A"}, {"headline": "B"}] if page == "1" else []
            return HttpResponse(200, request.url, {"Content-Type": "application/json"}, json.dumps({"items": items}).encode())

        transport = FakeTransport(handler)
        config = JsonApiConfig(source_id="s", endpoint="https://api.example/data", pagination="page", max_pages=5)
        result = GenericJsonApiAdapter(transport, config, credential_lookup=lambda _key: "").fetch()
        self.assertTrue(result.available)
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.pages_fetched, 2)

    def test_cursor_pagination_follows_next_cursor(self) -> None:
        def handler(request: HttpRequest) -> HttpResponse:
            if "cursor=c2" in request.url:
                return HttpResponse(200, request.url, {"Content-Type": "application/json"}, json.dumps({"items": [{"headline": "C"}]}).encode())
            return HttpResponse(200, request.url, {"Content-Type": "application/json"}, json.dumps({"items": [{"headline": "A"}], "next_cursor": "c2"}).encode())

        transport = FakeTransport(handler)
        config = JsonApiConfig(source_id="s", endpoint="https://api.example/data", pagination="cursor", max_pages=5)
        result = GenericJsonApiAdapter(transport, config, credential_lookup=lambda _key: "").fetch()
        self.assertEqual([item["headline"] for item in result.items], ["A", "C"])

    def test_missing_credential_degrades_without_crash(self) -> None:
        transport = FakeTransport(lambda request: _html("{}", "application/json"))
        config = JsonApiConfig(source_id="s", endpoint="https://api.example/data", auth_style="bearer", secret_env="X_API_KEY")
        result = GenericJsonApiAdapter(transport, config, credential_lookup=lambda _key: None).fetch()
        self.assertFalse(result.available)
        self.assertIn("credential_unavailable", result.degradation_reason)
        self.assertEqual(result.items, ())

    def test_bearer_token_is_sent_and_fields_are_mapped(self) -> None:
        transport = FakeTransport(lambda request: HttpResponse(200, request.url, {"Content-Type": "application/json"}, json.dumps({"data": [{"t": "hi", "u": "https://x/y"}]}).encode()))
        config = JsonApiConfig(
            source_id="s",
            endpoint="https://api.example/data",
            auth_style="bearer",
            secret_env="X_API_KEY",
            item_path="data",
            field_mapping={"title": "t", "url": "u"},
        )
        result = GenericJsonApiAdapter(transport, config, credential_lookup=lambda _key: "secret-token").fetch()
        self.assertEqual(result.items[0], {"title": "hi", "url": "https://x/y"})
        self.assertEqual(transport.requests[0].headers.get("Authorization"), "Bearer secret-token")


class FreshRssTests(unittest.TestCase):
    def test_missing_credentials_make_adapter_unavailable(self) -> None:
        transport = FakeTransport(lambda request: _html(""))
        adapter = FreshRssAdapter(transport, env=lambda _key: None)
        status = adapter.credentials_status()
        self.assertFalse(status.available)
        self.assertIn("missing FreshRSS credentials", status.reason)
        # Does not crash; login raises a typed AdapterError rather than a network error.
        with self.assertRaises(AdapterError):
            adapter.login()
        self.assertEqual(len(transport.requests), 0)

    def test_login_returns_auth_token_when_credentials_present(self) -> None:
        def handler(request: HttpRequest) -> HttpResponse:
            return HttpResponse(200, request.url, {}, b"SID=x\nAuth=token-123\n")

        transport = FakeTransport(handler)
        env = {"FRESHRSS_BASE_URL": "https://reader.example", "FRESHRSS_USERNAME": "u", "FRESHRSS_API_PASSWORD": "p"}
        adapter = FreshRssAdapter(transport, env=env.get)
        self.assertTrue(adapter.credentials_status().available)
        self.assertEqual(adapter.login(), "token-123")


class GdeltDiscoveryTests(unittest.TestCase):
    def test_resolves_to_original_publisher_and_marks_verification(self) -> None:
        articles = {"articles": [
            {"url": "https://known.example/a", "domain": "known.example", "title": "T1", "language": "English", "sourcecountry": "US"},
            {"url": "https://unknown.example/b", "domain": "unknown.example", "title": "T2", "language": "English", "sourcecountry": "US"},
        ]}
        transport = FakeTransport(lambda request: HttpResponse(200, request.url, {"Content-Type": "application/json"}, json.dumps(articles).encode()))
        entries = GdeltDiscoveryAdapter(transport).discover("ai", known_domains={"known.example": "known_source"})
        self.assertEqual(entries[0].registry_source_id, "known_source")
        self.assertEqual(entries[0].verification_status, "registry_mapped")
        self.assertEqual(entries[1].registry_source_id, "temporary:unknown.example")
        self.assertEqual(entries[1].verification_status, "unverified_discovery")
        self.assertFalse(entries[0].is_final_evidence)
        self.assertTrue(all(entry.original_url for entry in entries))


def _source() -> Source:
    return Source(
        source_id="feed_source",
        name="Feed Source",
        canonical_url="https://feed.example/",
        publisher_country="US",
        macro_region="North America",
        languages=["en"],
        source_roles=["news_agency"],
        domains=["ai_agents_applications"],
        ownership_profile="independent",
        evidence_profile="secondary",
        priority="normal",
        adapters=[SourceAdapterConfig(kind="rss", url="https://feed.example/rss")],
        fetch_interval_minutes=60,
        freshness_slo_minutes=180,
        usage_policy="public",
        fulltext_policy="excerpt",
        enabled=True,
        verification_status="verified",
        last_verified_at="2026-07-01",
        aliases=[],
    )


_RSS = """<?xml version='1.0'?><rss><channel>
<item><title>Headline one</title><link>https://feed.example/a</link><description>body</description></item>
</channel></rss>"""


class RssConditionalTests(unittest.TestCase):
    def test_not_modified_returns_no_documents(self) -> None:
        transport = FakeTransport(lambda request: HttpResponse(304, request.url, {"ETag": "abc"}, b""))
        client = ConditionalRssClient(transport)
        result = client.fetch(_source(), "https://feed.example/rss", etag="abc")
        self.assertTrue(result.not_modified)
        self.assertEqual(result.documents, ())
        # The conditional headers were actually sent.
        self.assertEqual(transport.requests[0].headers.get("If-None-Match"), "abc")

    def test_fresh_feed_parses_documents_and_captures_cache_headers(self) -> None:
        transport = FakeTransport(lambda request: HttpResponse(200, request.url, {"ETag": "v2", "Last-Modified": "Wed, 01 Jul 2026 00:00:00 GMT", "Content-Type": "application/rss+xml"}, _RSS.encode()))
        result = ConditionalRssClient(transport).fetch(_source(), "https://feed.example/rss")
        self.assertEqual(result.item_count, 1)
        self.assertEqual(result.etag, "v2")
        self.assertFalse(result.not_modified)

    def test_backoff_schedule_is_deterministic_and_bounded(self) -> None:
        self.assertEqual(backoff_delays(4, base_seconds=0.5, max_seconds=30), [0.5, 1.0, 2.0, 4.0])
        self.assertEqual(backoff_delays(3, base_seconds=0.5, jitter=lambda attempt: 0.1 * attempt), [0.5, 1.1, 2.2])

    def test_retry_isolates_failure_and_eventually_raises(self) -> None:
        calls = {"n": 0}

        def flaky() -> object:
            calls["n"] += 1
            raise RuntimeError("boom")

        slept: list[float] = []
        with self.assertRaises(AdapterError):
            fetch_with_retry(flaky, max_attempts=3, sleep=slept.append)
        self.assertEqual(calls["n"], 3)
        self.assertEqual(len(slept), 2)


class SocialChannelTests(unittest.TestCase):
    def test_public_channel_is_direct_checked(self) -> None:
        transport = FakeTransport(lambda request: _html(_RSS, "application/rss+xml"))
        adapter = PublicSocialChannelAdapter(transport)
        check = adapter.check("chan-1", adapter.youtube_feed_url("UC123"), kind="youtube_public")
        self.assertTrue(check.direct_checked)
        self.assertIn("channel_id=UC123", check.url)

    def test_official_api_unavailable_without_credentials(self) -> None:
        adapter = OfficialSocialApiAdapter(platform="x", secret_env="X_BEARER_TOKEN", env=lambda _key: None)
        self.assertFalse(adapter.credentials_status().available)
        # A generic web result never counts as a direct channel check.
        self.assertFalse(adapter.direct_checked())

    def test_official_api_available_with_credentials(self) -> None:
        adapter = OfficialSocialApiAdapter(platform="x", secret_env="X_BEARER_TOKEN", env={"X_BEARER_TOKEN": "t"}.get)
        self.assertTrue(adapter.credentials_status().available)


if __name__ == "__main__":
    unittest.main()
