from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

from radar.runtime.runs import run_daily_fixture

ROOT = Path(__file__).resolve().parents[2]


class EvaluationPipelineTests(unittest.TestCase):
    def _openai_loaded(self) -> bool:
        return any(name == "openai" or name.startswith("openai.") for name in sys.modules)

    def test_deterministic_mode_never_imports_ai(self) -> None:
        before = self._openai_loaded()
        with mock.patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("OPENAI_API_KEY", None)
            result = run_daily_fixture(ROOT, date="2026-07-10", freshrss_available=False, evaluation_mode="deterministic")
        self.assertEqual(result.report["evaluation_audit"]["effective_mode"], "deterministic")
        self.assertEqual(self._openai_loaded(), before)

    def test_auto_without_key_falls_back_without_importing_ai(self) -> None:
        before = self._openai_loaded()
        with mock.patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("OPENAI_API_KEY", None)
            result = run_daily_fixture(ROOT, date="2026-07-10", freshrss_available=False, evaluation_mode="auto")
        audit = result.report["evaluation_audit"]
        self.assertEqual(audit["requested_mode"], "auto")
        self.assertEqual(audit["effective_mode"], "deterministic")
        self.assertIn("ai_evaluation_unavailable", audit["degradation_reasons"])
        self.assertEqual(self._openai_loaded(), before)


if __name__ == "__main__":
    unittest.main()
