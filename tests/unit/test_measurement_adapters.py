from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from radar.adapters.measurements import StructuredMeasurementSourceAdapter
from radar.adapters.transport import HttpRequest, HttpResponse
from radar.evaluators.matrices import evaluate_crypto_matrix, evaluate_structural_indicators
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.qualification import assess_report_qualification
from radar.ports.sources import SourceFetchRequest
from radar.schemas.measurement import MeasurementRegistry, MeasurementSource


def bls_payload(series_id: str, value: float) -> bytes:
    return json.dumps(
        {
            "status": "REQUEST_SUCCEEDED",
            "message": [],
            "Results": {
                "series": [
                    {
                        "seriesID": series_id,
                        "data": [
                            {
                                "year": "2026",
                                "period": "Q02",
                                "periodName": "2nd Quarter",
                                "value": str(value),
                            },
                            {
                                "year": "2026",
                                "period": "Q01",
                                "periodName": "1st Quarter",
                                "value": "0.1",
                            },
                        ],
                    }
                ]
            },
        }
    ).encode()


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


def response(url: str, body: bytes) -> HttpResponse:
    return HttpResponse(status=200, url=url, headers={"Content-Type": "application/json"}, body=body)


def bls_source() -> MeasurementSource:
    return MeasurementSource(
        source_id="bls_productivity",
        name="BLS Productivity",
        adapter="bls_productivity",
        canonical_url="https://www.bls.gov/productivity/",
        api_base="https://api.bls.gov/publicAPI/v2/timeseries/data",
        primary_domain="global_markets_macro",
        macro_region="North America",
        language="en",
        source_roles=("official", "government", "data"),
        series=(
            ("rate_labor_productivity_yoy", "PRS85006091"),
            ("rate_labor_share_yoy", "PRS85006171"),
            ("rate_real_hourly_compensation_yoy", "PRS85006151"),
        ),
    )


def llama_source() -> MeasurementSource:
    return MeasurementSource(
        source_id="defillama_hyperliquid",
        name="DefiLlama Hyperliquid",
        adapter="defillama_protocol",
        canonical_url="https://defillama.com/protocol/hyperliquid",
        api_base="https://api.llama.fi",
        primary_domain="crypto_rwa_agent_payments",
        macro_region="Global",
        language="en",
        source_roles=("specialist", "data"),
        protocol="hyperliquid",
        endpoints=(
            ("fees", "/summary/fees/hyperliquid?dataType=dailyFees&excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"),
            ("revenue", "/summary/fees/hyperliquid?dataType=dailyRevenue&excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"),
            ("tvl", "/tvl/hyperliquid"),
        ),
    )


class MeasurementRegistryTests(unittest.TestCase):
    def test_repository_measurement_registry_validates(self) -> None:
        registry = MeasurementRegistry.from_file(Path("config/measurement_sources.json"))
        self.assertEqual(registry.version, "1.0")
        self.assertEqual({source.source_id for source in registry.sources}, {"bls_productivity", "defillama_hyperliquid"})

    def test_unknown_adapter_is_rejected(self) -> None:
        payload = {
            "version": "1.0",
            "sources": [
                {
                    "source_id": "bad",
                    "name": "Bad",
                    "adapter": "unknown",
                    "canonical_url": "https://example.com/",
                    "api_base": "https://api.example.com/",
                    "primary_domain": "global_markets_macro",
                    "macro_region": "Global",
                    "language": "en",
                    "source_roles": ["data"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "measurements.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown measurement adapter"):
                MeasurementRegistry.from_file(path)


class StructuredMeasurementAdapterTests(unittest.TestCase):
    def test_bls_series_become_one_indicator_only_event_and_can_support_k_shape(self) -> None:
        base = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        transport = FakeTransport(
            {
                f"{base}/PRS85006091": response(f"{base}/PRS85006091", bls_payload("PRS85006091", 2.8)),
                f"{base}/PRS85006171": response(f"{base}/PRS85006171", bls_payload("PRS85006171", -2.9)),
                f"{base}/PRS85006151": response(f"{base}/PRS85006151", bls_payload("PRS85006151", -0.4)),
            }
        )
        adapter = StructuredMeasurementSourceAdapter(
            registry=MeasurementRegistry(version="1.0", sources=(bls_source(),)),
            transport=transport,
        )
        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual(len(result.documents), 1)
        document = result.documents[0]
        self.assertEqual(document.lane, "indicator_only")
        self.assertEqual(document.facts.get("rate_labor_productivity_yoy"), 2.8)
        self.assertEqual(document.facts.get("rate_labor_share_yoy"), -2.9)
        self.assertEqual(document.facts.get("rate_real_hourly_compensation_yoy"), -0.4)
        self.assertIn("productivity gain", document.title.lower())
        self.assertIn("labor share decline", document.title.lower())
        self.assertIn("real wage decline", document.title.lower())

        event = cluster_documents([document])[0]
        self.assertFalse(assess_report_qualification(event).qualified)
        observation = evaluate_structural_indicators(
            [event],
            ["k_shaped_ai_productivity_economy"],
            observation_date="2026-08-17",
        )[0]
        self.assertGreater(observation.support_score, 0)
        self.assertIn(event.event_id, observation.supporting_signal_ids)

    def test_defillama_snapshot_fills_tvl_fees_revenue_without_becoming_news(self) -> None:
        base = "https://api.llama.fi"
        fees_path = "/summary/fees/hyperliquid?dataType=dailyFees&excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
        revenue_path = "/summary/fees/hyperliquid?dataType=dailyRevenue&excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
        transport = FakeTransport(
            {
                f"{base}/tvl/hyperliquid": response(f"{base}/tvl/hyperliquid", b"2500000000"),
                f"{base}{fees_path}": response(f"{base}{fees_path}", b'{"total24h":3000000}'),
                f"{base}{revenue_path}": response(f"{base}{revenue_path}", b'{"total24h":2500000}'),
            }
        )
        adapter = StructuredMeasurementSourceAdapter(
            registry=MeasurementRegistry(version="1.0", sources=(llama_source(),)),
            transport=transport,
        )
        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual(len(result.documents), 1)
        document = result.documents[0]
        self.assertEqual(document.lane, "indicator_only")
        self.assertEqual(document.facts.get("tvl_usd"), 2_500_000_000.0)
        self.assertEqual(document.facts.get("fees_usd_24h"), 3_000_000.0)
        self.assertEqual(document.facts.get("revenue_usd_24h"), 2_500_000.0)

        event = cluster_documents([document])[0]
        self.assertFalse(assess_report_qualification(event).qualified)
        cell = evaluate_crypto_matrix([event], ["tvl_fees_revenue"])["tvl_fees_revenue"]
        self.assertEqual(cell.status, "observed")
        self.assertIn("metric:tvl", cell.data_checked)
        self.assertIn("metric:fees", cell.data_checked)
        self.assertIn("metric:revenue", cell.data_checked)

    def test_one_measurement_source_failure_does_not_hide_other_source(self) -> None:
        base_bls = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        base_llama = "https://api.llama.fi"
        fees_path = "/summary/fees/hyperliquid?dataType=dailyFees&excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
        revenue_path = "/summary/fees/hyperliquid?dataType=dailyRevenue&excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
        transport = FakeTransport(
            {
                f"{base_bls}/PRS85006091": RuntimeError("BLS timeout"),
                f"{base_llama}/tvl/hyperliquid": response(f"{base_llama}/tvl/hyperliquid", b"2500000000"),
                f"{base_llama}{fees_path}": response(f"{base_llama}{fees_path}", b'{"total24h":3000000}'),
                f"{base_llama}{revenue_path}": response(f"{base_llama}{revenue_path}", b'{"total24h":2500000}'),
            }
        )
        adapter = StructuredMeasurementSourceAdapter(
            registry=MeasurementRegistry(version="1.0", sources=(bls_source(), llama_source())),
            transport=transport,
        )
        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual([document.source_id for document in result.documents], ["defillama_hyperliquid"])
        self.assertEqual([failure.source_id for failure in result.failures], ["bls_productivity"])
        self.assertEqual(dict(result.integration_status)["bls_productivity"], "failed")
        self.assertEqual(dict(result.integration_status)["defillama_hyperliquid"], "checked")


if __name__ == "__main__":
    unittest.main()
