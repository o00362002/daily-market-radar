from __future__ import annotations

import copy
import unittest
from pathlib import Path

from radar.contracts.report import RadarReportV2
from radar.contracts.runtime import RuntimeContract
from radar.reporting.contracts import validate_report_contract
from radar.runtime.runs import run_daily_fixture


ROOT = Path(__file__).resolve().parents[2]


class CompetitorAuditContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")
        cls.payload = copy.deepcopy(
            run_daily_fixture(
                ROOT,
                "2026-07-10",
                freshrss_available=False,
                evaluation_mode="deterministic",
            ).report
        )

    def test_old_v2_payload_without_competitor_audit_migrates_to_empty_typed_audit(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload.pop("competitor_audit", None)

        report = RadarReportV2.from_payload(payload)

        self.assertEqual(report.competitor_audit.fixed_target_count, 0)
        self.assertEqual(report.competitor_audit.checks, [])
        self.assertEqual(report.competitor_audit.registry_version, "unavailable")

    def test_competitor_audit_counts_and_id_lists_must_match_checks(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["competitor_audit"] = {
            "registry_version": "1.1",
            "source_registry_version": "1.0",
            "checked_at": "2026-07-10T08:00:00+00:00",
            "fixed_target_count": 2,
            "checked_target_count": 1,
            "updated_target_count": 0,
            "baseline_target_count": 1,
            "partial_target_count": 0,
            "failed_target_count": 0,
            "not_executed_target_count": 0,
            "checked_ids": ["alpha"],
            "updated_ids": [],
            "baseline_ids": ["alpha"],
            "partial_ids": [],
            "failed_ids": [],
            "not_executed_ids": [],
            "checks": [
                {
                    "competitor_id": "alpha",
                    "group": "global_direct_retail_action_systems",
                    "name": "Alpha",
                    "market": "global",
                    "relationship": "direct",
                    "priority": "high",
                    "status": "baseline",
                    "checked_at": "2026-07-10T08:00:00+00:00",
                    "successful_source_count": 1,
                    "failed_source_count": 0,
                    "fresh_material_delta": False,
                    "summary": "baseline",
                    "source_checks": [
                        {
                            "source_id": "product",
                            "url": "https://alpha.example/product",
                            "channel": "official_product",
                            "status": "checked",
                            "checked_at": "2026-07-10T08:00:00+00:00",
                            "http_status": 200,
                            "etag": "",
                            "last_modified": "",
                            "content_hash": "abc",
                            "previous_content_hash": "",
                            "material_change": False,
                            "similarity": None,
                            "title": "Alpha",
                            "excerpt": "baseline",
                            "error": "",
                        }
                    ],
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "fixed_target_count"):
            validate_report_contract(payload, contract=self.contract, enforce_floors=False)

    def test_valid_typed_competitor_audit_survives_report_roundtrip(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["competitor_audit"] = {
            "registry_version": "1.1",
            "source_registry_version": "1.0",
            "checked_at": "2026-07-10T08:00:00+00:00",
            "fixed_target_count": 1,
            "checked_target_count": 1,
            "updated_target_count": 0,
            "baseline_target_count": 0,
            "partial_target_count": 0,
            "failed_target_count": 0,
            "not_executed_target_count": 0,
            "checked_ids": ["alpha"],
            "updated_ids": [],
            "baseline_ids": [],
            "partial_ids": [],
            "failed_ids": [],
            "not_executed_ids": [],
            "checks": [
                {
                    "competitor_id": "alpha",
                    "group": "global_direct_retail_action_systems",
                    "name": "Alpha",
                    "market": "global",
                    "relationship": "direct",
                    "priority": "high",
                    "status": "checked_no_major_update",
                    "checked_at": "2026-07-10T08:00:00+00:00",
                    "successful_source_count": 1,
                    "failed_source_count": 0,
                    "fresh_material_delta": False,
                    "summary": "checked",
                    "source_checks": [
                        {
                            "source_id": "product",
                            "url": "https://alpha.example/product",
                            "channel": "official_product",
                            "status": "not_modified",
                            "checked_at": "2026-07-10T08:00:00+00:00",
                            "http_status": 304,
                            "etag": "v1",
                            "last_modified": "",
                            "content_hash": "abc",
                            "previous_content_hash": "abc",
                            "material_change": False,
                            "similarity": 1.0,
                            "title": "Alpha",
                            "excerpt": "checked",
                            "error": "",
                        }
                    ],
                }
            ],
        }

        validate_report_contract(payload, contract=self.contract, enforce_floors=False)
        report = RadarReportV2.from_payload(payload)
        self.assertEqual(report.competitor_audit.checked_ids, ["alpha"])
        self.assertEqual(report.competitor_audit.checks[0].status, "checked_no_major_update")


if __name__ == "__main__":
    unittest.main()
