import unittest

from radar.domain.models import CoverageCell, Document, ReportItem
from radar.pipeline.coverage import audit_coverage, enforce_major_potential_split
from radar.reporting.contracts import validate_report_contract


class CoverageAndReportTests(unittest.TestCase):
    def test_taiwan_implication_is_not_direct_taiwan_news(self) -> None:
        item = ReportItem.fixture(
            item_id="item_1",
            event_id="evt_global_chip",
            signal_id=None,
            direct_taiwan_evidence=[],
            taiwan_implication="May affect Taiwan semiconductor suppliers.",
        )
        validate_report_contract({"items": [item.to_dict()], "coverage_gaps": []})
        self.assertEqual(item.taiwan_direct_count, 0)

    def test_source_outage_becomes_coverage_gap(self) -> None:
        cells = [
            CoverageCell(
                domain="ai_agents_applications",
                macro_region="Taiwan",
                language="zh-Hant",
                source_role="official",
                channel="rss",
                time_window="24h",
                status="failing",
            )
        ]
        gaps = audit_coverage(cells)
        self.assertEqual(gaps[0]["reason"], "source_failing")

    def test_major_and_potential_cannot_use_same_event_slot(self) -> None:
        with self.assertRaises(ValueError):
            enforce_major_potential_split(
                major_event_ids=["evt_same"],
                potential_event_ids=["evt_same"],
            )

    def test_report_items_require_evidence_url_and_timestamp(self) -> None:
        doc = Document.fixture(
            source_id="openai_news",
            url="https://openai.com/news/rss.xml",
            title="OpenAI publishes release",
            published_at="2026-07-10T08:00:00+08:00",
        )
        item = ReportItem.fixture(evidence_links=[doc.evidence_link()])
        validate_report_contract({"items": [item.to_dict()], "coverage_gaps": []})
        broken = item.to_dict()
        broken["evidence_links"][0]["fetched_at"] = ""
        with self.assertRaises(ValueError):
            validate_report_contract({"items": [broken], "coverage_gaps": []})


if __name__ == "__main__":
    unittest.main()
