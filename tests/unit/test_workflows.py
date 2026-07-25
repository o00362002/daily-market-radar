from __future__ import annotations

import unittest
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"
REQUIRED = {
    "runtime-check.yml",
    "web-check.yml",
    "daily-intelligence.yml",
    "prepare-chat.yml",
    "import-chat.yml",
    "ai-analysis.yml",
    "pages-deploy.yml",
    "mount-check.yml",
}


@unittest.skipIf(yaml is None, "pyyaml not installed")
class WorkflowContractTests(unittest.TestCase):
    def _load(self, name: str) -> dict:
        with (WORKFLOWS / name).open(encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def test_all_required_workflows_exist_and_parse(self) -> None:
        present = {path.name for path in WORKFLOWS.glob("*.yml")}
        self.assertTrue(REQUIRED.issubset(present), f"missing: {REQUIRED - present}")
        for name in REQUIRED:
            self.assertIsInstance(self._load(name), dict)

    def test_daily_pipeline_has_utc_cron_concurrency_and_production_gates(self) -> None:
        doc = self._load("daily-intelligence.yml")
        on = doc.get("on", doc.get(True))
        crons = [entry["cron"] for entry in on["schedule"]]
        self.assertIn("0 23 * * *", crons)
        self.assertEqual(doc["concurrency"]["group"], "radar-daily")
        self.assertFalse(doc["concurrency"]["cancel-in-progress"])
        text = (WORKFLOWS / "daily-intelligence.yml").read_text(encoding="utf-8")
        self.assertIn("radar-state", text)
        self.assertNotIn("HEAD:main", text)
        self.assertIn("run-daily --mode live", text)
        self.assertIn("FRESHRSS_BASE_URL", text)
        self.assertIn("radar.analysis.cli", text)
        self.assertIn("check_production_quality.py", text)
        self.assertIn("Report quality pre-gate", text)
        self.assertIn("analysis_fallback", (ROOT / "tools/check_production_quality.py").read_text(encoding="utf-8"))
        self.assertIn("previous website remains live", text.lower())
        self.assertIn("Persist durable state (accepted report runs)", text)
        self.assertIn("status=report_only", text)
        self.assertIn("rm -rf artifacts/web/v1/ai-analysis", text)

    def test_runtime_check_runs_deterministic_no_secret_and_auto_fallback(self) -> None:
        text = (WORKFLOWS / "runtime-check.yml").read_text(encoding="utf-8")
        self.assertIn("make validate", text)
        self.assertIn("--evaluation-mode deterministic", text)
        self.assertIn("ai_evaluation_unavailable", text)

    def test_web_check_enforces_type_sync_and_bundle_budgets(self) -> None:
        text = (WORKFLOWS / "web-check.yml").read_text(encoding="utf-8")
        self.assertIn("types:check", text)
        self.assertIn("npm run build", text)
        self.assertIn("61440", text)

    def test_prepare_chat_reads_durable_state_without_api_call(self) -> None:
        doc = self._load("prepare-chat.yml")
        self.assertEqual(doc["concurrency"]["group"], "radar-daily")
        text = (WORKFLOWS / "prepare-chat.yml").read_text(encoding="utf-8")
        self.assertIn("radar-state", text)
        self.assertIn("state restore", text)
        self.assertIn("prepare-chat", text)
        self.assertIn("--database", text)
        self.assertIn("OPENAI_API_KEY", text)
        self.assertIn("refusing to publish a fixture package", text)

    def test_import_chat_can_persist_build_and_deploy_with_fixture_gate(self) -> None:
        doc = self._load("import-chat.yml")
        self.assertEqual(doc["concurrency"]["group"], "radar-daily")
        text = (WORKFLOWS / "import-chat.yml").read_text(encoding="utf-8")
        self.assertIn("import-chat", text)
        self.assertIn("save_report", text)
        self.assertIn("export-web", text)
        self.assertIn("deploy-pages", text)
        self.assertIn("allow_fixture_deploy", text)

    def test_ai_analysis_rejects_fallback_from_production(self) -> None:
        doc = self._load("ai-analysis.yml")
        on = doc.get("on", doc.get(True))
        self.assertEqual(on["workflow_run"]["workflows"], ["import-chat"])
        self.assertEqual(doc["concurrency"]["group"], "radar-daily")
        text = (WORKFLOWS / "ai-analysis.yml").read_text(encoding="utf-8")
        self.assertIn("radar.analysis.cli", text)
        self.assertIn("OPENAI_ANALYSIS_MODEL", text)
        self.assertIn("ai-analysis/latest.json", text)
        self.assertIn("check_production_quality.py", text)
        self.assertIn("previous website remains live", text.lower())
        self.assertIn("deploy-pages", text)

    def test_pages_deploy_uses_same_production_gate(self) -> None:
        text = (WORKFLOWS / "pages-deploy.yml").read_text(encoding="utf-8")
        self.assertIn("check_production_quality.py", text)
        self.assertIn("production-quality-gate.json", text)
        self.assertIn("deploy-pages", text)
        self.assertNotIn("deterministic\n", text)


if __name__ == "__main__":
    unittest.main()
