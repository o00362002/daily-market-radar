from __future__ import annotations

import builtins
import importlib
import os
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from radar.ports import (
    DocumentRepository,
    EventRepository,
    IndicatorRepository,
    IntelligenceEvaluator,
    ReportPublisher,
    ReportRepository,
    SourceAdapter,
    StateStore,
    WebArtifactStore,
)
from radar.schemas.source import SourceRegistry


FORBIDDEN_OPTIONAL_MODULE_PREFIXES = (
    "openai",
    "radar.adapters.freshrss",
    "radar.artifacts.filesystem",
    "radar.evaluators.openai",
    "radar.publishers.filesystem",
    "radar.repositories.filesystem",
    "radar.stores.filesystem",
)
ROOT = Path(__file__).resolve().parents[2]


class CompositionRootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        attempted_optional_imports: list[str] = []
        real_import = builtins.__import__

        def guarded_import(
            name: str,
            globals: dict[str, object] | None = None,
            locals: dict[str, object] | None = None,
            fromlist: tuple[str, ...] = (),
            level: int = 0,
        ) -> object:
            if name == "openai" or name.startswith(FORBIDDEN_OPTIONAL_MODULE_PREFIXES):
                attempted_optional_imports.append(name)
                raise AssertionError(f"disabled optional integration imported concrete module: {name}")
            return real_import(name, globals, locals, fromlist, level)

        # Force the composition module itself to execute under the import guard. This
        # catches eager optional imports even when another test imported dependencies.
        sys.modules.pop("radar.composition", None)
        with patch.object(builtins, "__import__", side_effect=guarded_import):
            cls.composition = importlib.import_module("radar.composition")
        cls.attempted_optional_imports = attempted_optional_imports

    def test_disabled_optional_integrations_compose_without_credentials_or_concrete_imports(self) -> None:
        config = self.composition.CompositionConfig(
            optional_integrations={
                "ai": False,
                "collection_aggregator": False,
                "filesystem_artifacts": False,
            }
        )

        with patch.dict(os.environ, {}, clear=True):
            composed = self.composition.compose_application(config)

        self.assertEqual(self.attempted_optional_imports, [])
        self.assertIsNotNone(composed.application)

    def test_factory_dependencies_structurally_satisfy_all_nine_stable_ports(self) -> None:
        composed = self.composition.compose_application(self.composition.CompositionConfig())
        dependencies = composed.dependencies

        port_bindings = {
            "SourceAdapter": (dependencies.source_adapter, SourceAdapter),
            "IntelligenceEvaluator": (dependencies.evaluator, IntelligenceEvaluator),
            "DocumentRepository": (dependencies.document_repository, DocumentRepository),
            "EventRepository": (dependencies.event_repository, EventRepository),
            "ReportRepository": (dependencies.report_repository, ReportRepository),
            "IndicatorRepository": (dependencies.indicator_repository, IndicatorRepository),
            "StateStore": (dependencies.state_store, StateStore),
            "WebArtifactStore": (dependencies.web_artifact_store, WebArtifactStore),
            "ReportPublisher": (dependencies.publishers[0], ReportPublisher),
        }

        self.assertEqual(len(port_bindings), 9)
        for port_name, (implementation, protocol) in port_bindings.items():
            with self.subTest(port=port_name):
                self.assertIsInstance(implementation, protocol)

    def test_multi_source_composes_rss_and_optional_freshrss_without_network(self) -> None:
        registry = SourceRegistry.from_file(ROOT / "config/source_registry.json")
        composed = self.composition.compose_application(
            self.composition.CompositionConfig(
                source_backend="multi",
                optional_integrations={
                    "ai": False,
                    "collection_aggregator": True,
                    "filesystem_artifacts": False,
                },
                environment=lambda _key: None,
            ),
            source_registry=registry,
        )

        self.assertIsInstance(composed.dependencies.source_adapter, SourceAdapter)
        self.assertEqual(composed.dependencies.source_adapter.adapter_id, "multi_source")
        # Direct RSS remains available even when FreshRSS credentials are absent.
        self.assertTrue(composed.dependencies.source_adapter.credentials_status().available)

    def test_sqlite_runtime_backend_can_be_selected_for_durable_ports(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            composed = self.composition.compose_application(
                self.composition.CompositionConfig(
                    document_repository_backend="sqlite",
                    event_repository_backend="sqlite",
                    report_repository_backend="sqlite",
                    indicator_repository_backend="sqlite",
                    state_store_backend="sqlite",
                    database_path=Path(tempdir) / "radar.db",
                    migrations_dir=ROOT / "migrations",
                )
            )

        dependencies = composed.dependencies
        self.assertIsInstance(dependencies.document_repository, DocumentRepository)
        self.assertIsInstance(dependencies.event_repository, EventRepository)
        self.assertIsInstance(dependencies.report_repository, ReportRepository)
        self.assertIsInstance(dependencies.indicator_repository, IndicatorRepository)
        self.assertIsInstance(dependencies.state_store, StateStore)

    def test_unknown_backends_and_integrations_fail_closed(self) -> None:
        base = self.composition.CompositionConfig()
        invalid_configs = {
            "source": replace(base, source_backend="freshrss"),
            "evaluator": replace(base, evaluator_backend="remote-ai"),
            "document repository": replace(base, document_repository_backend="filesystem"),
            "event repository": replace(base, event_repository_backend="postgres"),
            "report repository": replace(base, report_repository_backend="postgres"),
            "indicator repository": replace(base, indicator_repository_backend="timeseries"),
            "state store": replace(base, state_store_backend="state-branch"),
            "web artifact store": replace(base, web_artifact_store_backend="filesystem"),
            "publisher": replace(base, publisher_backends=("github-pages",)),
            "optional integration": replace(
                base,
                optional_integrations={**base.optional_integrations, "mystery": False},
            ),
        }

        for backend_name, config in invalid_configs.items():
            with self.subTest(backend=backend_name):
                with self.assertRaisesRegex(ValueError, "unknown"):
                    self.composition.compose_application(config)

    def test_known_but_unavailable_backends_fail_closed(self) -> None:
        base = self.composition.CompositionConfig()
        unavailable_configs = {
            "rss without registry": replace(base, source_backend="rss"),
            "multi without registry": replace(base, source_backend="multi"),
            "sqlite without paths": replace(base, report_repository_backend="sqlite"),
            "ai implementation": replace(
                base,
                optional_integrations={**base.optional_integrations, "ai": True},
            ),
            "filesystem artifacts implementation": replace(
                base,
                optional_integrations={**base.optional_integrations, "filesystem_artifacts": True},
            ),
        }

        for backend_name, config in unavailable_configs.items():
            with self.subTest(backend=backend_name):
                with self.assertRaisesRegex(ValueError, "required|unavailable"):
                    self.composition.compose_application(config)


if __name__ == "__main__":
    unittest.main()
