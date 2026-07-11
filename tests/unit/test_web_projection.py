from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from radar.contracts.report import RadarReportV2
from radar.contracts.runtime import RuntimeContract
from radar.contracts.web_projection import ReportSummaryV1, WebManifestV1, web_json_schemas
from radar.runtime.runs import run_daily_fixture
from radar.web.export import export_web_artifacts
from radar.web.projection import WEB_ROOT, project_web

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-07-10T00:00:00+00:00"


def _reports() -> list[RadarReportV2]:
    a = RadarReportV2.from_payload(run_daily_fixture(ROOT, date="2026-07-09", freshrss_available=False).report)
    b = RadarReportV2.from_payload(
        run_daily_fixture(ROOT, date="2026-07-10", freshrss_available=False, external_discovery_available=False).report
    )
    return [a, b]


def _contract() -> RuntimeContract:
    return RuntimeContract.from_file(ROOT / "config/runtime_contract.json")


class ProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reports = _reports()
        self.contract = _contract()
        self.artifacts = project_web(self.reports, self.contract, generated_at=STAMP)
        self.by_path = {a.path: a for a in self.artifacts}

    def test_projection_is_deterministic(self) -> None:
        again = project_web(self.reports, self.contract, generated_at=STAMP)
        self.assertEqual([(a.path, a.content_hash) for a in self.artifacts], [(a.path, a.content_hash) for a in again])

    def test_full_report_filename_matches_content_hash(self) -> None:
        for path, artifact in self.by_path.items():
            if "/full." in path:
                embedded = path.split("full.")[1].split(".json")[0]
                self.assertEqual(embedded, hashlib.sha256(artifact.content).hexdigest())
                self.assertEqual(embedded, artifact.content_hash)

    def test_manifest_and_summary_validate(self) -> None:
        manifest = WebManifestV1.model_validate_json(self.by_path["manifest.json"].content)
        self.assertEqual(manifest.report_count, 2)
        self.assertEqual(manifest.latest_date, "2026-07-10")
        self.assertEqual(sorted(manifest.report_dates), ["2026-07-09", "2026-07-10"])
        summary = ReportSummaryV1.model_validate_json(self.by_path["reports/2026/2026-07-10/summary.json"].content)
        self.assertEqual(summary.date, "2026-07-10")
        self.assertTrue(summary.is_fixture)
        self.assertIn(summary.status, {"partial", "complete", "failed"})

    def test_indexes_present_for_domains_taiwan_and_trends(self) -> None:
        self.assertIn("indexes/reports/2026.json", self.by_path)
        self.assertIn("indexes/taiwan/2026.json", self.by_path)
        for indicator_id in self.contract.structural_indicator_ids:
            self.assertIn(f"indexes/trends/{indicator_id}.json", self.by_path)
        self.assertTrue(any(path.startswith("indexes/domains/") for path in self.by_path))

    def test_web_schema_is_stable(self) -> None:
        checked_in = json.loads((ROOT / "schemas/web.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(checked_in, web_json_schemas())


class FloorRetroValidationTests(unittest.TestCase):
    """Regression: 2026-07-11 daily run failed because export re-validated stored
    pre-floors reports against the new floor policy (taiwan 0 below floor 1
    without declared below_minimum_taiwan). Floor policy must apply at creation
    time only — never retroactively to stored history."""

    def _pre_floors_payload(self) -> dict:
        from radar.contracts.report import RadarReportV2

        report = RadarReportV2.from_payload(
            run_daily_fixture(ROOT, date="2026-07-09", freshrss_available=False).report
        )
        payload = report.model_dump(mode="json")
        # Simulate a report produced before the floor policy existed: no
        # below_minimum_* declarations, no floor coverage gaps, taiwan count 0.
        payload["degradation_reasons"] = [
            r for r in payload["degradation_reasons"] if not r.startswith("below_minimum_")
        ]
        payload["coverage_gaps"] = [
            g for g in payload["coverage_gaps"] if not g["reason"].startswith("below_minimum_")
        ]
        for item in payload["items"]:
            item["direct_taiwan_evidence"] = []
        return payload

    def test_projection_tolerates_stored_pre_floors_reports(self) -> None:
        from radar.reporting.contracts import validate_report_contract

        payload = self._pre_floors_payload()
        contract = _contract()
        # Creation-time validation still rejects the undeclared shortfall...
        with self.assertRaises(ValueError):
            validate_report_contract(payload, contract=contract)
        # ...but projection of stored history must not.
        validate_report_contract(payload, contract=contract, enforce_floors=False)

    def test_export_web_projects_a_database_containing_pre_floors_reports(self) -> None:
        import json as jsonlib
        import tempfile

        from radar.web.runtime import export_web

        payload = self._pre_floors_payload()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report_dir = out / "stored"
            report_dir.mkdir()
            (report_dir / "old.json").write_text(jsonlib.dumps(payload), encoding="utf-8")
            result = export_web(ROOT, out, reports_dir=report_dir, generated_at=STAMP)
            self.assertTrue(result.written)


class ExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reports = _reports()
        self.contract = _contract()
        self.artifacts = project_web(self.reports, self.contract, generated_at=STAMP)

    def test_export_then_incremental_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            first = export_web_artifacts(self.artifacts, out)
            self.assertTrue(first.written)
            self.assertFalse(first.skipped)
            second = export_web_artifacts(self.artifacts, out)
            self.assertFalse(second.written)  # everything unchanged -> skipped
            self.assertEqual(len(second.skipped), len(self.artifacts))
            self.assertTrue((out / WEB_ROOT / "manifest.json").exists())

    def test_incremental_only_rewrites_changed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            export_web_artifacts(self.artifacts, out)
            # Add a third report; only new + index/manifest artifacts change.
            third = RadarReportV2.from_payload(run_daily_fixture(ROOT, date="2026-07-11", freshrss_available=True, external_discovery_available=True).report)
            grown = project_web([*self.reports, third], self.contract, generated_at=STAMP)
            result = export_web_artifacts(grown, out)
            self.assertTrue(any("2026-07-11" in path for path in result.written))
            self.assertTrue(result.skipped)  # unchanged prior reports were skipped

    def test_atomic_failure_leaves_no_partial_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            calls = {"n": 0}

            def faulty(path: Path, content: bytes) -> None:
                calls["n"] += 1
                if calls["n"] == 2:
                    raise RuntimeError("disk full")
                path.write_bytes(content)

            with self.assertRaises(RuntimeError):
                export_web_artifacts(self.artifacts, out, _write=faulty)

            root = out / WEB_ROOT
            finals = [p for p in root.rglob("*") if p.is_file() and not p.name.startswith(".")]
            temps = [p for p in root.rglob("*") if p.is_file() and ".tmp" in p.name]
            self.assertEqual(finals, [])  # no final artifact was placed
            self.assertEqual(temps, [])  # staged temporaries were cleaned up


if __name__ == "__main__":
    unittest.main()
