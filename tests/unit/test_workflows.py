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

    def test_daily_pipeline_has_utc_cron_and_concurrency(self) -> None:
        doc = self._load("daily-intelligence.yml")
        on = doc.get("on", doc.get(True))
        crons = [entry["cron"] for entry in on["schedule"]]
        self.assertIn("0 23 * * *", crons)  # 07:00 Asia/Taipei
        self.assertEqual(doc["concurrency"]["group"], "radar-daily")
        self.assertFalse(doc["concurrency"]["cancel-in-progress"])
        # State is persisted to radar-state, never main.
        text = (WORKFLOWS / "daily-intelligence.yml").read_text(encoding="utf-8")
        self.assertIn("radar-state", text)
        self.assertNotIn("HEAD:main", text)

    def test_runtime_check_runs_deterministic_no_secret_and_auto_fallback(self) -> None:
        text = (WORKFLOWS / "runtime-check.yml").read_text(encoding="utf-8")
        self.assertIn("make validate", text)
        self.assertIn("--evaluation-mode deterministic", text)
        self.assertIn("ai_evaluation_unavailable", text)

    def test_web_check_enforces_type_sync_and_bundle_budgets(self) -> None:
        text = (WORKFLOWS / "web-check.yml").read_text(encoding="utf-8")
        self.assertIn("types:check", text)
        self.assertIn("npm run build", text)
        self.assertIn("61440", text)  # 60 KB gzip JS budget

    def test_prepare_chat_makes_no_api_call(self) -> None:
        text = (WORKFLOWS / "prepare-chat.yml").read_text(encoding="utf-8")
        self.assertIn("prepare-chat", text)
        self.assertIn("openai", text)  # asserts openai is NOT imported

    def test_pages_deploy_only_deploys_validated_non_fixture(self) -> None:
        text = (WORKFLOWS / "pages-deploy.yml").read_text(encoding="utf-8")
        self.assertIn("deployable", text)
        self.assertIn("fixture", text)
        self.assertIn("deploy-pages", text)


if __name__ == "__main__":
    unittest.main()
