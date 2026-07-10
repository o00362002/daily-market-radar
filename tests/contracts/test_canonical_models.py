from __future__ import annotations

import inspect
import json
from pathlib import Path
import unittest

from pydantic import BaseModel, ValidationError

from radar.contracts import report as report_contracts
from radar.contracts import web as web_contracts
from radar.domain.models import Document


ROOT = Path(__file__).resolve().parents[2]


PROVIDER_OR_BACKEND_TOKENS = {
    "anthropic",
    "event_registry",
    "filesystem",
    "freshrss",
    "gdelt",
    "github_pages",
    "mediacloud",
    "openai",
    "postgres",
    "sqlite",
}


def canonical_model_classes() -> tuple[type[BaseModel], ...]:
    models: dict[str, type[BaseModel]] = {}
    for module in (report_contracts, web_contracts):
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(candidate, BaseModel)
                and candidate is not BaseModel
                and candidate.__module__ == module.__name__
            ):
                models[f"{candidate.__module__}.{candidate.__name__}"] = candidate
    return tuple(models[name] for name in sorted(models))


class CanonicalModelContractTests(unittest.TestCase):
    def test_expected_canonical_models_are_pydantic_models(self) -> None:
        names = {model.__name__ for model in canonical_model_classes()}
        self.assertTrue(
            {
                "EvaluationAuditV1",
                "EvidenceLinkV2",
                "PublicationReceiptV1",
                "RadarReportV2",
                "ReportItemV2",
                "WebArtifactV1",
            }.issubset(names)
        )

    def test_all_canonical_models_are_strict_and_forbid_extra_fields(self) -> None:
        models = canonical_model_classes()
        self.assertTrue(models)

        for model in models:
            with self.subTest(model=model.__name__):
                self.assertIs(model.model_config.get("strict"), True)
                self.assertEqual(model.model_config.get("extra"), "forbid")

                with self.assertRaises(ValidationError) as raised:
                    model.model_validate({"openai_response_id": "must-not-leak"})
                error_types = {error["type"] for error in raised.exception.errors()}
                self.assertIn("extra_forbidden", error_types)

    def test_provider_and_backend_specific_field_names_do_not_enter_canonical_models(self) -> None:
        violations: list[str] = []
        for model in canonical_model_classes():
            for field_name, field in model.model_fields.items():
                exposed_names = {
                    field_name,
                    field.alias,
                    field.serialization_alias,
                    field.validation_alias if isinstance(field.validation_alias, str) else None,
                }
                for exposed_name in exposed_names - {None}:
                    normalized = str(exposed_name).lower()
                    for token in PROVIDER_OR_BACKEND_TOKENS:
                        if token in normalized:
                            violations.append(f"{model.__name__}.{exposed_name} contains {token}")

        self.assertEqual(violations, [])

        # These names are provider-neutral and are explicitly allowed at the
        # canonical audit/port boundary.
        self.assertIn("provider", report_contracts.EvaluationAuditV1.model_fields)
        self.assertIn("model", report_contracts.EvaluationAuditV1.model_fields)

    def test_provider_response_fields_are_rejected_from_canonical_document_facts(self) -> None:
        provider_payloads = [
            {"adapter": "rss"},
            {"provider": "openai"},
            {"openai": {"response_id": "provider-owned"}},
            {"anthropic_response_id": "provider-owned"},
            {"openai_response_id": 123},
            {"sqlite_rowid": 7},
            {"freshrss_item_id": 42},
        ]
        for facts in provider_payloads:
            with self.subTest(facts=facts):
                with self.assertRaisesRegex(ValueError, "non-canonical document fact|canonical metric namespace"):
                    Document.fixture(facts=facts)

        document = Document.fixture(facts={"flow_usd_m": 280, "source_roles": ["official"]})
        self.assertEqual(document.facts.get("flow_usd_m"), 280)
        self.assertEqual(document.facts.get("source_roles"), ["official"])

    def test_report_json_schema_is_generated_from_the_typed_contract(self) -> None:
        checked_in = json.loads((ROOT / "schemas/report.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(checked_in, report_contracts.radar_report_json_schema())


if __name__ == "__main__":
    unittest.main()
