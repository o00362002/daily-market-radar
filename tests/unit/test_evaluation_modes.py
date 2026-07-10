from __future__ import annotations

import unittest

from radar.evaluators.modes import resolve_evaluation_mode


class EvaluationModeTests(unittest.TestCase):
    def test_deterministic_never_uses_ai(self) -> None:
        resolved = resolve_evaluation_mode("deterministic", api_key_available=True)
        self.assertEqual(resolved.effective_mode, "deterministic")
        self.assertFalse(resolved.use_ai)

    def test_auto_uses_ai_when_key_present(self) -> None:
        resolved = resolve_evaluation_mode("auto", api_key_available=True)
        self.assertTrue(resolved.use_ai)
        self.assertEqual(resolved.degradation_reasons, ())

    def test_auto_falls_back_without_key(self) -> None:
        resolved = resolve_evaluation_mode("auto", api_key_available=False)
        self.assertFalse(resolved.use_ai)
        self.assertEqual(resolved.effective_mode, "deterministic")
        self.assertIn("ai_evaluation_unavailable", resolved.degradation_reasons)

    def test_api_assisted_requires_key(self) -> None:
        with_key = resolve_evaluation_mode("api-assisted", api_key_available=True)
        self.assertTrue(with_key.use_ai)
        self.assertEqual(with_key.effective_mode, "api-assisted")
        without = resolve_evaluation_mode("api-assisted", api_key_available=False)
        self.assertFalse(without.use_ai)
        self.assertIn("ai_evaluation_unavailable", without.degradation_reasons)

    def test_budget_exhausted_forces_deterministic(self) -> None:
        resolved = resolve_evaluation_mode("auto", api_key_available=True, budget_exhausted=True)
        self.assertFalse(resolved.use_ai)
        self.assertIn("ai_budget_exhausted", resolved.degradation_reasons)

    def test_chat_assisted_run_is_deterministic_pending_import(self) -> None:
        resolved = resolve_evaluation_mode("chat-assisted", api_key_available=False)
        self.assertFalse(resolved.use_ai)
        self.assertIn("chat_assisted_pending_import", resolved.degradation_reasons)

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_evaluation_mode("magic", api_key_available=True)


if __name__ == "__main__":
    unittest.main()
