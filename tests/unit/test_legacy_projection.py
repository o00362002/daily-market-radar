from __future__ import annotations

import json
import unittest

from radar.web.legacy import project_legacy


FILES = [
    ("reports/2026/2026-07-11.md", "# 2026-07-11 每日市場情報雷達\n\n內容一"),
    ("reports/2026/2026-06-29.md", "# 六月廿九\n\n內容"),
    ("reports/2026/2026-06-29-gemini-backtest.md", "# 回測變體\n\n內容"),
    ("reports/2026/06/11.md", "# 六月十一週報\n\n內容"),
    ("reports/2026/README.md", "# 不該出現"),
    ("reports/2026/INDEX.md", "# 也不該出現"),
]


class LegacyProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.artifacts = project_legacy(FILES)
        self.by_path = {a.path: a for a in self.artifacts}

    def test_dated_files_project_and_index_files_are_skipped(self) -> None:
        md_paths = [p for p in self.by_path if p.endswith(".md")]
        self.assertEqual(
            sorted(md_paths),
            [
                "legacy/2026/2026-06-11.md",
                "legacy/2026/2026-06-29-gemini-backtest.md",
                "legacy/2026/2026-06-29.md",
                "legacy/2026/2026-07-11.md",
            ],
        )

    def test_nested_month_day_form_parses_date_from_path(self) -> None:
        index = json.loads(self.by_path["indexes/legacy/2026.json"].content)
        dates = [e["date"] for e in index["entries"]]
        self.assertIn("2026-06-11", dates)

    def test_duplicate_date_variants_stay_separate_entries(self) -> None:
        index = json.loads(self.by_path["indexes/legacy/2026.json"].content)
        june29 = [e for e in index["entries"] if e["date"] == "2026-06-29"]
        self.assertEqual(len(june29), 2)
        self.assertEqual({e["variant"] for e in june29}, {"", "gemini-backtest"})

    def test_content_is_byte_identical_and_titled_from_heading(self) -> None:
        artifact = self.by_path["legacy/2026/2026-07-11.md"]
        self.assertEqual(artifact.content.decode("utf-8"), FILES[0][1])
        index = json.loads(self.by_path["indexes/legacy/2026.json"].content)
        entry = next(e for e in index["entries"] if e["slug"] == "2026-07-11")
        self.assertEqual(entry["title"], "2026-07-11 每日市場情報雷達")

    def test_never_emits_v2_report_paths(self) -> None:
        self.assertFalse(any(p.startswith(("reports/", "indexes/reports/")) for p in self.by_path))

    def test_deterministic(self) -> None:
        again = project_legacy(FILES)
        self.assertEqual(
            [(a.path, a.content_hash) for a in self.artifacts],
            [(a.path, a.content_hash) for a in again],
        )


if __name__ == "__main__":
    unittest.main()
