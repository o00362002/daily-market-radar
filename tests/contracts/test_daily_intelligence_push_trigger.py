from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "daily-intelligence.yml"


class DailyIntelligencePushTriggerTests(unittest.TestCase):
    def test_relevant_main_changes_trigger_the_production_pipeline(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("push:", text)
        self.assertIn("branches: [main]", text)
        for required_path in (
            '"src/radar/**"',
            '"config/**"',
            '"configs/**"',
            '"web/**"',
            '"schemas/**"',
            '"tools/check_production_quality.py"',
        ):
            self.assertIn(required_path, text)

    def test_push_path_uses_the_same_production_safety_gate(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Production deployment gate", text)
        self.assertIn("check_production_quality.py", text)
        self.assertIn("Persist durable state (only accepted production runs)", text)
        self.assertIn("actions/deploy-pages@v4", text)


if __name__ == "__main__":
    unittest.main()
