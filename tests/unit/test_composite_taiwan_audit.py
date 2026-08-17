from __future__ import annotations

import unittest
from dataclasses import dataclass

from radar.adapters.composite import CompositeSourceAdapter
from radar.domain.models import Document
from radar.ports.sources import (
    CredentialsStatusV1,
    RateLimitPolicy,
    RetryPolicy,
    SourceFetchRequest,
    SourceFetchResult,
    SourceHealthV1,
)


@dataclass(frozen=True)
class FakeAdapter:
    documents: tuple[Document, ...]
    explicit_taiwan_sources: tuple[str, ...] = ()
    adapter_id: str = "fake"
    source_id: str = "fake_registry"
    retry_policy: RetryPolicy = RetryPolicy()
    rate_limit_policy: RateLimitPolicy = RateLimitPolicy()

    def credentials_status(self) -> CredentialsStatusV1:
        return CredentialsStatusV1(True)

    def health_check(self) -> SourceHealthV1:
        return SourceHealthV1("healthy", "fake adapter healthy")

    def fetch(self, request: SourceFetchRequest) -> SourceFetchResult:
        del request
        return SourceFetchResult(
            documents=self.documents,
            sources_checked=tuple(document.source_id for document in self.documents),
            integration_status=((self.adapter_id, "checked"),),
            taiwan_direct_sources_checked=self.explicit_taiwan_sources,
        )

    @staticmethod
    def normalize(result: SourceFetchResult) -> list[Document]:
        return list(result.documents)


class CompositeTaiwanAuditTests(unittest.TestCase):
    def test_taiwan_document_adds_direct_source_even_when_child_omits_audit_field(self) -> None:
        taiwan = Document.fixture(
            source_id="fsc_tw_vasp_law",
            url="https://law.fsc.gov.tw/LawContent.aspx?id=GL004301",
            title="金管會虛擬資產服務法",
            language="zh-Hant",
            macro_region="Taiwan",
            primary_domain="crypto_rwa_agent_payments",
            lane="indicator_only",
        )
        global_doc = Document.fixture(
            source_id="farside_btc_etf",
            url="https://farside.co.uk/btc/",
            title="Bitcoin ETF flows",
            macro_region="Global",
            primary_domain="crypto_rwa_agent_payments",
            lane="indicator_only",
        )
        adapter = CompositeSourceAdapter((FakeAdapter((taiwan, global_doc)),))

        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual(result.taiwan_direct_sources_checked, ("fsc_tw_vasp_law",))

    def test_explicit_and_derived_taiwan_sources_are_deduplicated(self) -> None:
        document = Document.fixture(
            source_id="twse",
            url="https://example.tw/market",
            title="TWSE market update",
            macro_region="Taiwan",
            primary_domain="global_markets_macro",
        )
        adapter = CompositeSourceAdapter(
            (FakeAdapter((document,), explicit_taiwan_sources=("twse",)),)
        )

        result = adapter.fetch(SourceFetchRequest(date="2026-08-17", profile="daily_push"))

        self.assertEqual(result.taiwan_direct_sources_checked, ("twse",))


if __name__ == "__main__":
    unittest.main()
