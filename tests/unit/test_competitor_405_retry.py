from __future__ import annotations

import unittest

from radar.adapters.competitor_web import OfficialCompetitorMonitor
from radar.adapters.transport import HttpRequest, HttpResponse
from radar.schemas.competitor import CompetitorMonitoringRegistry, CompetitorSourceSpec, CompetitorTarget
from radar.stores.memory import InMemoryStateStore


class SequenceTransport:
    def __init__(self) -> None:
        self.requests: list[HttpRequest] = []

    def fetch(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        if len(self.requests) == 1:
            raise RuntimeError("http error 405: https://vendor.example/pos")
        body = (
            "<html><head><title>Vendor POS</title></head><body><main>"
            + "retail pos inventory member workflow evidence " * 20
            + "</main></body></html>"
        ).encode()
        return HttpResponse(
            status=200,
            url=request.url,
            headers={"Content-Type": "text/html"},
            body=body,
        )


def registry() -> CompetitorMonitoringRegistry:
    return CompetitorMonitoringRegistry(
        competitor_registry_version="1.1",
        source_registry_version="1.1",
        state_key="competitor-monitor:v1",
        timeout_seconds=3,
        max_workers=1,
        minimum_visible_characters=80,
        targets=(
            CompetitorTarget(
                competitor_id="vendor",
                group="taiwan_adjacent_retail_platforms",
                name="Vendor",
                market="taiwan",
                relationship="adjacent",
                priority="medium",
                sources=(
                    CompetitorSourceSpec(
                        source_id="pos",
                        channel="official_product",
                        url="https://vendor.example/pos",
                        material_similarity_threshold=0.96,
                    ),
                ),
            ),
        ),
        excluded_registry_groups=("social_and_content",),
    )


class Competitor405RetryTests(unittest.TestCase):
    def test_browser_compatible_retry_is_bounded_and_preserves_official_url(self) -> None:
        transport = SequenceTransport()
        result = OfficialCompetitorMonitor(
            registry=registry(),
            transport=transport,
            state_store=InMemoryStateStore(),
        ).run("2026-08-17", "2026-08-17T01:00:00+00:00")

        self.assertEqual(result.audit.failed_target_count, 0)
        self.assertEqual(result.audit.baseline_target_count, 1)
        self.assertEqual(len(transport.requests), 2)
        self.assertNotIn("User-Agent", transport.requests[0].headers)
        self.assertIn("Mozilla/5.0", transport.requests[1].headers["User-Agent"])
        self.assertEqual(transport.requests[0].url, transport.requests[1].url)


if __name__ == "__main__":
    unittest.main()
