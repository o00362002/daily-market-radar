from __future__ import annotations

import json
import unittest

from radar.adapters.competitor_web import OfficialCompetitorMonitor
from radar.adapters.transport import HttpRequest, HttpResponse
from radar.schemas.competitor import (
    CompetitorMonitoringRegistry,
    CompetitorSourceSpec,
    CompetitorTarget,
)
from radar.stores.memory import InMemoryStateStore


CHECKED_AT = "2026-07-25T08:00:00+00:00"


def page(title: str, body: str) -> bytes:
    repeated = " ".join([body] * 18)
    return f"<html><head><title>{title}</title></head><body><main>{repeated}</main></body></html>".encode()


class FakeTransport:
    def __init__(self, responses: dict[str, HttpResponse | Exception]) -> None:
        self.responses = responses
        self.requests: list[HttpRequest] = []

    def fetch(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        response = self.responses[request.url]
        if isinstance(response, Exception):
            raise response
        return response


def registry() -> CompetitorMonitoringRegistry:
    targets = (
        CompetitorTarget(
            competitor_id="alpha",
            group="global_direct_retail_action_systems",
            name="Alpha Retail",
            market="global",
            relationship="direct",
            priority="high",
            sources=(
                CompetitorSourceSpec(
                    source_id="product",
                    channel="official_product",
                    url="https://alpha.example/product",
                    material_similarity_threshold=0.96,
                ),
            ),
        ),
        CompetitorTarget(
            competitor_id="beta",
            group="taiwan_adjacent_retail_platforms",
            name="Beta Retail",
            market="taiwan",
            relationship="adjacent",
            priority="medium",
            sources=(
                CompetitorSourceSpec(
                    source_id="homepage",
                    channel="official_product",
                    url="https://beta.example/",
                    material_similarity_threshold=0.96,
                ),
                CompetitorSourceSpec(
                    source_id="docs",
                    channel="official_docs",
                    url="https://beta.example/docs",
                    material_similarity_threshold=0.985,
                ),
            ),
        ),
    )
    result = CompetitorMonitoringRegistry(
        competitor_registry_version="1.1",
        source_registry_version="1.0",
        state_key="competitor-monitor:v1",
        timeout_seconds=3,
        max_workers=3,
        minimum_visible_characters=80,
        targets=targets,
        excluded_registry_groups=("social_and_content",),
    )
    result.validate()
    return result


def response(url: str, text: bytes, *, etag: str = "") -> HttpResponse:
    headers = {"Content-Type": "text/html; charset=utf-8"}
    if etag:
        headers["ETag"] = etag
    return HttpResponse(status=200, url=url, headers=headers, body=text)


class OfficialCompetitorMonitorTests(unittest.TestCase):
    def test_first_run_establishes_baseline_for_every_successful_target(self) -> None:
        state = InMemoryStateStore()
        transport = FakeTransport(
            {
                "https://alpha.example/product": response(
                    "https://alpha.example/product", page("Alpha", "retail task execution proof escalation")
                ),
                "https://beta.example/": response(
                    "https://beta.example/", page("Beta", "store operations inventory workflow")
                ),
                "https://beta.example/docs": response(
                    "https://beta.example/docs", page("Beta docs", "retail operations documentation")
                ),
            }
        )
        result = OfficialCompetitorMonitor(
            registry=registry(), transport=transport, state_store=state
        ).run("2026-07-25", CHECKED_AT)

        self.assertEqual(result.audit.fixed_target_count, 2)
        self.assertEqual(result.audit.checked_target_count, 2)
        self.assertEqual(result.audit.baseline_target_count, 2)
        self.assertEqual(result.audit.updated_target_count, 0)
        self.assertEqual({check.status for check in result.audit.checks}, {"baseline"})
        payload = json.loads(result.state_value)
        self.assertEqual(payload["version"], "competitor-monitor-state/v1")
        self.assertEqual(len(payload["sources"]), 3)

    def test_unchanged_second_run_is_checked_no_major_update_and_uses_conditionals(self) -> None:
        state = InMemoryStateStore()
        first_transport = FakeTransport(
            {
                "https://alpha.example/product": response(
                    "https://alpha.example/product",
                    page("Alpha", "retail task execution proof escalation"),
                    etag='"alpha-v1"',
                ),
                "https://beta.example/": response(
                    "https://beta.example/", page("Beta", "store operations inventory workflow")
                ),
                "https://beta.example/docs": response(
                    "https://beta.example/docs", page("Beta docs", "retail operations documentation")
                ),
            }
        )
        first = OfficialCompetitorMonitor(
            registry=registry(), transport=first_transport, state_store=state
        ).run("2026-07-25", CHECKED_AT)
        state.save(first.state_key, first.state_value)

        second_transport = FakeTransport(
            {
                "https://alpha.example/product": HttpResponse(
                    status=304,
                    url="https://alpha.example/product",
                    headers={"ETag": '"alpha-v1"'},
                    body=b"",
                ),
                "https://beta.example/": response(
                    "https://beta.example/", page("Beta", "store operations inventory workflow")
                ),
                "https://beta.example/docs": response(
                    "https://beta.example/docs", page("Beta docs", "retail operations documentation")
                ),
            }
        )
        second = OfficialCompetitorMonitor(
            registry=registry(), transport=second_transport, state_store=state
        ).run("2026-07-25", "2026-07-25T09:00:00+00:00")

        self.assertEqual(second.audit.updated_target_count, 0)
        self.assertEqual(
            {check.status for check in second.audit.checks}, {"checked_no_major_update"}
        )
        alpha_request = next(
            request for request in second_transport.requests if "alpha.example" in request.url
        )
        self.assertEqual(alpha_request.headers["If-None-Match"], '"alpha-v1"')

    def test_substantial_page_change_becomes_typed_update(self) -> None:
        state = InMemoryStateStore()
        base_transport = FakeTransport(
            {
                "https://alpha.example/product": response(
                    "https://alpha.example/product", page("Alpha", "retail task execution proof escalation")
                ),
                "https://beta.example/": response(
                    "https://beta.example/", page("Beta", "store operations inventory workflow")
                ),
                "https://beta.example/docs": response(
                    "https://beta.example/docs", page("Beta docs", "retail operations documentation")
                ),
            }
        )
        first = OfficialCompetitorMonitor(
            registry=registry(), transport=base_transport, state_store=state
        ).run("2026-07-25", CHECKED_AT)
        state.save(first.state_key, first.state_value)

        changed_transport = FakeTransport(
            {
                "https://alpha.example/product": response(
                    "https://alpha.example/product",
                    page("Alpha Agent", "autonomous store manager reprioritizes actions from POS outcomes"),
                ),
                "https://beta.example/": response(
                    "https://beta.example/", page("Beta", "store operations inventory workflow")
                ),
                "https://beta.example/docs": response(
                    "https://beta.example/docs", page("Beta docs", "retail operations documentation")
                ),
            }
        )
        second = OfficialCompetitorMonitor(
            registry=registry(), transport=changed_transport, state_store=state
        ).run("2026-07-26", "2026-07-26T08:00:00+00:00")

        self.assertEqual(second.audit.updated_target_count, 1)
        self.assertEqual(second.audit.updated_ids, ["alpha"])
        alpha = next(check for check in second.audit.checks if check.competitor_id == "alpha")
        self.assertEqual(alpha.status, "updated")
        self.assertTrue(alpha.fresh_material_delta)
        self.assertTrue(alpha.source_checks[0].material_change)
        self.assertIsNotNone(alpha.source_checks[0].similarity)

    def test_partial_and_failed_targets_are_disclosed_without_aborting_run(self) -> None:
        transport = FakeTransport(
            {
                "https://alpha.example/product": RuntimeError("alpha blocked"),
                "https://beta.example/": response(
                    "https://beta.example/", page("Beta", "store operations inventory workflow")
                ),
                "https://beta.example/docs": RuntimeError("docs timeout"),
            }
        )
        result = OfficialCompetitorMonitor(
            registry=registry(), transport=transport, state_store=InMemoryStateStore()
        ).run("2026-07-25", CHECKED_AT)

        by_id = {check.competitor_id: check for check in result.audit.checks}
        self.assertEqual(by_id["alpha"].status, "failed")
        self.assertEqual(by_id["beta"].status, "partial")
        self.assertEqual(result.audit.failed_target_count, 1)
        self.assertEqual(result.audit.partial_target_count, 1)
        self.assertIn("blocked", by_id["alpha"].source_checks[0].error)


if __name__ == "__main__":
    unittest.main()
