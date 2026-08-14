from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "web/src/pages/competitors.astro"
ANALYSIS = ROOT / "web/src/lib/competitorAnalysis.ts"


class CompetitorPageAuditTests(unittest.TestCase):
    def test_page_uses_typed_audit_not_absence_of_news_as_no_update(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("report?.competitor_audit", text)
        self.assertIn("checked_no_major_update", text)
        self.assertIn("已查無重大更新", text)
        self.assertIn("官方來源檢查明細", text)
        self.assertIn("當日新聞投影", text)
        self.assertIn("這不影響上方官方來源查核與競品分析", text)

    def test_page_discloses_baseline_failures_and_discovery_only_boundary(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("已建立監測基準", text)
        self.assertIn("部分來源失敗", text)
        self.assertIn("官方來源檢查失敗", text)
        self.assertIn("discovery-only", text)
        self.assertIn("最近監測歷史", text)
        self.assertIn("首次成功取得官方頁面只建立 baseline", text)

    def test_page_renders_analysis_even_when_there_is_no_news(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("buildCompetitorAnalysis", text)
        self.assertIn("競品分析", text)
        self.assertIn("Action Loop 重疊", text)
        self.assertIn("RetailOps 關聯", text)
        self.assertIn("閉環重疊", text)
        self.assertIn("受影響產品層", text)
        self.assertIn("威脅類型", text)
        self.assertIn("目前差異判讀", text)
        self.assertIn("建議動作", text)
        self.assertIn("目前官方內容基準", text)
        self.assertIn("一般新聞只是 fresh evidence 投影", text)

    def test_analysis_projection_uses_only_registry_and_formal_audit_fields(self) -> None:
        text = ANALYSIS.read_text(encoding="utf-8")
        self.assertIn("entry?.focus", text)
        self.assertIn("check?.source_checks", text)
        self.assertIn("check?.fresh_material_delta", text)
        self.assertNotIn("competitorSignals", text)
        self.assertNotIn("fetch(", text)
        self.assertNotIn("OpenAI", text)


if __name__ == "__main__":
    unittest.main()