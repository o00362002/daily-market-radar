from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "daily-intelligence.yml"


class DailyIntelligencePushTriggerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_relevant_main_changes_trigger_the_production_pipeline(self) -> None:
        self.assertIn("push:", self.text)
        self.assertIn("branches: [main]", self.text)
        for required_path in (
            '"src/radar/**"',
            '"config/**"',
            '"configs/**"',
            '"web/**"',
            '"schemas/**"',
            '"tools/check_production_quality.py"',
        ):
            self.assertIn(required_path, self.text)

    def test_report_quality_remains_the_hard_deployment_gate(self) -> None:
        self.assertIn("Report quality pre-gate", self.text)
        self.assertIn("--report-only", self.text)
        self.assertIn("deployable=false", self.text)
        self.assertIn("Fail visibly when the report is rejected", self.text)

    def test_valid_report_can_deploy_without_invalid_ai_analysis(self) -> None:
        self.assertIn("continue-on-error: true", self.text)
        self.assertIn("status=report_only", self.text)
        self.assertIn("analysis_status=unavailable", self.text)
        self.assertIn("rm -rf artifacts/web/v1/ai-analysis", self.text)
        self.assertIn("analysis-status.json", self.text)
        self.assertIn("Persist durable state (accepted report runs)", self.text)
        self.assertIn("actions/deploy-pages@v4", self.text)

    def test_report_only_deploy_never_publishes_stale_analysis(self) -> None:
        remove_index = self.text.index("rm -rf artifacts/web/v1/ai-analysis")
        build_index = self.text.index("Build static site")
        self.assertLess(remove_index, build_index)
        self.assertIn("尚無 AIAnalysisV1", (ROOT / "web" / "src" / "pages" / "analysis.astro").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
