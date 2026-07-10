import copy
import pathlib
import unittest

from radar.reporting.contracts import validate_report_contract
from radar.runtime.contract import RuntimeContract
from radar.runtime.runs import run_daily_fixture


ROOT = pathlib.Path(__file__).resolve().parents[2]


class RuntimeV2ReportContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")
        self.report = run_daily_fixture(
            ROOT,
            date="2026-07-10",
            freshrss_available=False,
        ).report

    def test_valid_fixture_report_passes(self) -> None:
        validate_report_contract(self.report, contract=self.contract)

    def test_missing_structural_indicator_fails(self) -> None:
        broken = copy.deepcopy(self.report)
        broken["structural_indicators"] = broken["structural_indicators"][:-1]
        with self.assertRaises(ValueError):
            validate_report_contract(broken, contract=self.contract)

    def test_missing_signals_fails(self) -> None:
        broken = copy.deepcopy(self.report)
        broken.pop("signals")
        with self.assertRaises(ValueError):
            validate_report_contract(broken, contract=self.contract)

    def test_missing_evaluation_audit_fails(self) -> None:
        broken = copy.deepcopy(self.report)
        broken.pop("evaluation_audit")
        with self.assertRaises(ValueError):
            validate_report_contract(broken, contract=self.contract)

    def test_missing_contract_version_fails(self) -> None:
        broken = copy.deepcopy(self.report)
        broken.pop("contract_version")
        with self.assertRaises(ValueError):
            validate_report_contract(broken, contract=self.contract)

    def test_same_event_in_major_and_potential_fails(self) -> None:
        broken = copy.deepcopy(self.report)
        major = next(item for item in broken["items"] if item["report_lane"] == "major")
        potential = next(item for item in broken["items"] if item["report_lane"] == "potential")
        potential["event_id"] = major["event_id"]
        with self.assertRaises(ValueError):
            validate_report_contract(broken, contract=self.contract)

    def test_potential_without_candidate_metadata_fails(self) -> None:
        broken = copy.deepcopy(self.report)
        potential = next(item for item in broken["items"] if item["report_lane"] == "potential")
        potential["candidate_type"] = None
        with self.assertRaises(ValueError):
            validate_report_contract(broken, contract=self.contract)


if __name__ == "__main__":
    unittest.main()
