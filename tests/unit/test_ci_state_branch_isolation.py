from __future__ import annotations

import unittest
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"
CODE_CHECK_WORKFLOWS = (
    "runtime-check.yml",
    "mount-check.yml",
    "single-owner-check.yml",
)


@unittest.skipIf(yaml is None, "pyyaml not installed")
class DurableStateBranchIsolationTests(unittest.TestCase):
    def test_code_checks_exclude_data_only_radar_state_branch(self) -> None:
        for name in CODE_CHECK_WORKFLOWS:
            with (WORKFLOWS / name).open(encoding="utf-8") as handle:
                document = yaml.safe_load(handle)
            triggers = document.get("on", document.get(True))
            push = triggers.get("push")
            if push is None:
                self.assertIn(
                    "workflow_dispatch",
                    triggers,
                    f"{name} must remain an explicit manual diagnostic when it is not a push gate",
                )
                continue
            self.assertIn(
                "main",
                push.get("branches", []),
                f"{name} must run only from main and never from the orphan data-only radar-state branch",
            )


if __name__ == "__main__":
    unittest.main()
