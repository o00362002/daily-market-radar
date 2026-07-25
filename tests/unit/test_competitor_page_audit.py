from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "web/src/pages/competitors.astro"


class CompetitorPageAuditTests(unittest.TestCase):
    def test_page_uses_typed_audit_not_absence_of_news_as_no_update(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("report?.competitor_audit", text)
        self.assertIn("checked_no_major_update", text)
        self.assertIn("已查無重大更新", text)
        self.assertIn("官方來源檢查明細", text)
        self.assertIn("當日新聞投影", text)
        self.assertIn("這不影響上方官方來源查核結果", text)

    def test_page_discloses_baseline_failures_and_discovery_only_boundary(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("已建立監測基準", text)
        self.assertIn("部分來源失敗", text)
        self.assertIn("官方來源檢查失敗", text)
        self.assertIn("discovery-only", text)
        self.assertIn("最近監測歷史", text)
        self.assertIn("首次成功取得官方頁面只建立 baseline", text)


if __name__ == "__main__":
    unittest.main()
