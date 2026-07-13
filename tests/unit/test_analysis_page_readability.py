from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "web" / "src" / "pages" / "analysis.astro"


class AnalysisPageReadabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = PAGE.read_text(encoding="utf-8")

    def test_content_precedes_indicator_panels(self) -> None:
        headings = [
            "<h2>今日統整</h2>",
            "<h2>重點判讀</h2>",
            "<h2>未來 3–6 個月趨勢情境</h2>",
            "<h2>三個核心結構趨勢指標</h2>",
            "<h2>輔助訊號面板</h2>",
        ]
        positions = [self.text.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))

    def test_provenance_stays_after_content(self) -> None:
        self.assertGreater(self.text.index("AI 產出履歷與稽核識別"), self.text.index("<h2>輔助訊號面板</h2>"))

    def test_future_trends_show_three_and_six_month_scenarios(self) -> None:
        self.assertIn("未來 3 個月可能性", self.text)
        self.assertIn("未來 6 個月可能性", self.text)
        self.assertIn("不是統計校準後的投資機率", self.text)

    def test_structural_cards_hide_raw_signal_ids_by_default(self) -> None:
        details_index = self.text.index("<summary>完整依據</summary>")
        support_ids_index = self.text.index("<strong>支持訊號：</strong>")
        counter_ids_index = self.text.index("<strong>反向訊號：</strong>")
        self.assertGreater(support_ids_index, details_index)
        self.assertGreater(counter_ids_index, details_index)
        self.assertIn("const structuralScore", self.text)

    def test_five_domain_findings_and_component_evidence_are_rendered(self) -> None:
        self.assertIn("const canonicalDomains", self.text)
        self.assertIn("const findingsForDomain", self.text)
        self.assertIn("component.evidence", self.text)
        self.assertIn("未完整查證", (ROOT / "web" / "src" / "pages" / "competitors.astro").read_text(encoding="utf-8"))

    def test_competitor_page_renders_registry_groups_and_matches(self) -> None:
        page = (ROOT / "web" / "src" / "pages" / "competitors.astro").read_text(encoding="utf-8")
        self.assertIn("const registryGroups", page)
        self.assertIn("signalsFor(entry)", page)
        self.assertIn("entry.aliases.join", page)
        self.assertIn("entry.priority", page)


if __name__ == "__main__":
    unittest.main()
