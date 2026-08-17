from __future__ import annotations

import unittest

from radar.adapters.measurements import StructuredMeasurementSourceAdapter
from radar.adapters.transport import HttpRequest, HttpResponse
from radar.evaluators.matrices import evaluate_crypto_matrix
from radar.pipeline.cluster import cluster_documents
from radar.pipeline.qualification import assess_report_qualification
from radar.ports.sources import SourceFetchRequest
from radar.schemas.measurement import MeasurementRegistry, MeasurementSource


FARSIDE_URL = "https://farside.co.uk/btc/"
FSC_URL = "https://law.fsc.gov.tw/LawContent.aspx?id=GL004301"


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


def html_response(url: str, body: str) -> HttpResponse:
    return HttpResponse(
        status=200,
        url=url,
        headers={"Content-Type": "text/html; charset=utf-8"},
        body=body.encode("utf-8"),
    )


def farside_source() -> MeasurementSource:
    return MeasurementSource(
        source_id="farside_btc_etf",
        name="Farside Bitcoin ETF Daily Flows",
        adapter="farside_etf",
        canonical_url=FARSIDE_URL,
        api_base=FARSIDE_URL,
        primary_domain="crypto_rwa_agent_payments",
        macro_region="Global",
        language="en",
        source_roles=("specialist", "data"),
    )


def fsc_source() -> MeasurementSource:
    return MeasurementSource(
        source_id="fsc_tw_vasp_law",
        name="Taiwan FSC Virtual Asset Service Act",
        adapter="fsc_vasp_law",
        canonical_url=FSC_URL,
        api_base="https://law.fsc.gov.tw/",
        primary_domain="crypto_rwa_agent_payments",
        macro_region="Taiwan",
        language="zh-Hant",
        source_roles=("official", "regulator", "government", "data"),
    )


def farside_html() -> str:
    return """
    <html><body>
      <table>
        <thead><tr><th>Date</th><th>IBIT</th><th>FBTC</th><th>Total</th></tr></thead>
        <tbody>
          <tr><td>13 Aug 2026</td><td>(80.0)</td><td>(51.1)</td><td>(131.1)</td></tr>
          <tr><td>14 Aug 2026</td><td>(40.0)</td><td>(16.2)</td><td>(56.2)</td></tr>
          <tr><td>12 Aug 2026</td><td>(61.1)</td><td>-</td><td>(61.1)</td></tr>
        </tbody>
      </table>
    </body></html>
    """


def fsc_html() -> str:
    return """
    <html><body>
      <h1>虛擬資產服務法</h1>
      <div>主管機關：金融監督管理委員會</div>
      <div>公布日期：民國 115 年 7 月 22 日</div>
      <div>發文字號：華總一經字第11500072401號</div>
      <div>法規狀態：全部或部分尚未施行</div>
    </body></html>
    """


class CryptoFixedMeasurementTests(unittest.TestCase):
    def test_farside_latest_etf_flow_fills_matrix_without_news_card(self) -> None:
        transport = FakeTransport({FARSIDE_URL: html_response(FARSIDE_URL, farside_html())})
        adapter = StructuredMeasurementSourceAdapter(
            registry=MeasurementRegistry(version="1.2", sources=(farside_source(),)),
            transport=transport,
        )

        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual(len(result.documents), 1)
        document = result.documents[0]
        self.assertEqual(document.lane, "indicator_only")
        self.assertEqual(document.facts.get("flow_usd_m_latest"), -56.2)
        self.assertIn("2026-08-14", document.summary)
        self.assertIn("outflow", document.title.lower())
        self.assertEqual(transport.requests[0].method, "GET")

        event = cluster_documents([document])[0]
        self.assertFalse(assess_report_qualification(event).qualified)
        cell = evaluate_crypto_matrix([event], ["etf_flows"])["etf_flows"]
        self.assertEqual(cell.status, "observed")
        self.assertIn(event.event_id, cell.signal_ids)
        self.assertIn("metric:flow", cell.data_checked)

    def test_fsc_vasp_law_fills_regulation_and_taiwan_fixed_cells(self) -> None:
        transport = FakeTransport({FSC_URL: html_response(FSC_URL, fsc_html())})
        adapter = StructuredMeasurementSourceAdapter(
            registry=MeasurementRegistry(version="1.2", sources=(fsc_source(),)),
            transport=transport,
        )

        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual(len(result.documents), 1)
        document = result.documents[0]
        self.assertEqual(document.lane, "indicator_only")
        self.assertEqual(document.macro_region, "Taiwan")
        self.assertEqual(document.published_at, "2026-07-22T00:00:00+00:00")
        self.assertEqual(document.facts.get("count_policy_publication_yyyymmdd"), 20260722.0)
        self.assertEqual(document.facts.get("count_policy_effective_status_code"), 0.0)
        self.assertIsInstance(document.facts.get("count_policy_revision_fingerprint"), int)
        self.assertIn("華總一經字第11500072401號", document.summary)
        self.assertIn("尚未施行", document.summary)

        event = cluster_documents([document])[0]
        self.assertFalse(assess_report_qualification(event).qualified)
        matrix = evaluate_crypto_matrix(
            [event],
            ["regulation_policy", "taiwan_crypto_fixed_sources"],
        )
        self.assertEqual(matrix["regulation_policy"].status, "observed")
        self.assertIn("keyword:vasp", matrix["regulation_policy"].data_checked)
        self.assertEqual(matrix["taiwan_crypto_fixed_sources"].status, "observed")
        self.assertIn(event.event_id, matrix["taiwan_crypto_fixed_sources"].signal_ids)
        self.assertIn("keyword:vasp", matrix["taiwan_crypto_fixed_sources"].data_checked)

    def test_one_fixed_source_failure_does_not_hide_the_other(self) -> None:
        transport = FakeTransport(
            {
                FARSIDE_URL: RuntimeError("Farside timeout"),
                FSC_URL: html_response(FSC_URL, fsc_html()),
            }
        )
        adapter = StructuredMeasurementSourceAdapter(
            registry=MeasurementRegistry(
                version="1.2",
                sources=(farside_source(), fsc_source()),
            ),
            transport=transport,
        )

        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual([document.source_id for document in result.documents], ["fsc_tw_vasp_law"])
        self.assertEqual([failure.source_id for failure in result.failures], ["farside_btc_etf"])
        self.assertEqual(dict(result.integration_status)["farside_btc_etf"], "failed")
        self.assertEqual(dict(result.integration_status)["fsc_tw_vasp_law"], "checked")
        self.assertIn("structured_measurement_source_failure", result.degradation_reasons)


if __name__ == "__main__":
    unittest.main()
