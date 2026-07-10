from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from radar.adapters.fixture import FixtureSourceAdapter
from radar.adapters.openai_provider import OpenAiEvaluationProvider
from radar.adapters.rss import RegistryRssSourceAdapter
from radar.application import ApplicationDependencies, DailyRadarApplication
from radar.evaluators.ai_assisted import AiAssistedEvaluator
from radar.evaluators.cache import CostBudget
from radar.evaluators.deterministic import DeterministicIntelligenceEvaluator
from radar.publishers.noop import NoOpReportPublisher
from radar.repositories.memory import (
    InMemoryDocumentRepository,
    InMemoryEventRepository,
    InMemoryIndicatorRepository,
    InMemoryReportRepository,
    InMemoryUnitOfWork,
)
from radar.repositories.sqlite import SqliteRunRepository
from radar.schemas.source import SourceRegistry
from radar.stores.memory import InMemoryStateStore, InMemoryWebArtifactStore


@dataclass(frozen=True)
class CompositionConfig:
    source_backend: str = "fixture"
    evaluator_backend: str = "deterministic"
    document_repository_backend: str = "memory"
    event_repository_backend: str = "memory"
    report_repository_backend: str = "memory"
    indicator_repository_backend: str = "memory"
    state_store_backend: str = "memory"
    web_artifact_store_backend: str = "memory"
    publisher_backends: tuple[str, ...] = ("disabled",)
    optional_integrations: dict[str, bool] = field(
        default_factory=lambda: {
            "ai": False,
            "collection_aggregator": False,
            "filesystem_artifacts": False,
        }
    )
    database_path: Path | None = None
    migrations_dir: Path | None = None
    timeout_seconds: int = 12
    per_feed_limit: int = 20
    external_discovery_available: bool = True
    fixture_collection_aggregator_available: bool = False
    ai_api_key: str = ""
    ai_model: str = "gpt-4.1-mini"
    ai_effective_mode: str = "auto"
    ai_max_daily_cost_usd: float = 0.0
    ai_max_items_per_run: int = 0
    ai_max_input_tokens_per_run: int = 0


@dataclass(frozen=True)
class ComposedApplication:
    application: DailyRadarApplication
    dependencies: ApplicationDependencies


def compose_application(
    config: CompositionConfig,
    *,
    source_registry: SourceRegistry | None = None,
    clock: Callable[[], datetime] | None = None,
) -> ComposedApplication:
    active_clock = clock or (lambda: datetime.now(timezone.utc))
    _validate_optional_integrations(config)

    if config.source_backend == "fixture":
        source_adapter = FixtureSourceAdapter(
            collection_aggregator_available=config.fixture_collection_aggregator_available,
            external_discovery_available=config.external_discovery_available,
        )
    elif config.source_backend == "rss":
        if source_registry is None:
            raise ValueError("source_registry is required for the rss source backend")
        source_adapter = RegistryRssSourceAdapter(
            registry=source_registry,
            timeout_seconds=config.timeout_seconds,
            per_feed_limit=config.per_feed_limit,
        )
    else:
        raise ValueError(f"unknown source backend: {config.source_backend}")

    if config.evaluator_backend == "deterministic":
        evaluator = DeterministicIntelligenceEvaluator(active_clock)
    elif config.evaluator_backend == "ai_assisted":
        deterministic_evaluator = DeterministicIntelligenceEvaluator(active_clock)
        provider = (
            OpenAiEvaluationProvider(model=config.ai_model, api_key=config.ai_api_key)
            if config.ai_api_key
            else None
        )
        evaluator = AiAssistedEvaluator(
            deterministic_evaluator,
            provider,
            clock=active_clock,
            budget=CostBudget(
                max_daily_cost_usd=config.ai_max_daily_cost_usd,
                max_items_per_run=config.ai_max_items_per_run,
                max_input_tokens_per_run=config.ai_max_input_tokens_per_run,
            ),
            effective_mode=config.ai_effective_mode,
        )
    else:
        raise ValueError(f"unknown evaluator backend: {config.evaluator_backend}")

    sqlite_repository: SqliteRunRepository | None = None
    if "sqlite" in {
        config.document_repository_backend,
        config.event_repository_backend,
        config.report_repository_backend,
        config.indicator_repository_backend,
        config.state_store_backend,
    }:
        if config.database_path is None or config.migrations_dir is None:
            raise ValueError("database_path and migrations_dir are required for sqlite")
        sqlite_repository = SqliteRunRepository(config.database_path, config.migrations_dir)

    if config.document_repository_backend == "memory":
        document_repository = InMemoryDocumentRepository()
    elif config.document_repository_backend == "sqlite":
        assert sqlite_repository is not None
        document_repository = sqlite_repository
    else:
        raise ValueError(f"unknown document repository backend: {config.document_repository_backend}")

    if config.event_repository_backend == "memory":
        event_repository = InMemoryEventRepository()
    elif config.event_repository_backend == "sqlite":
        assert sqlite_repository is not None
        event_repository = sqlite_repository
    else:
        raise ValueError(f"unknown event repository backend: {config.event_repository_backend}")

    if config.report_repository_backend == "memory":
        report_repository = InMemoryReportRepository()
    elif config.report_repository_backend == "sqlite":
        assert sqlite_repository is not None
        report_repository = sqlite_repository
    else:
        raise ValueError(f"unknown report repository backend: {config.report_repository_backend}")

    if config.indicator_repository_backend == "memory":
        indicator_repository = InMemoryIndicatorRepository()
    elif config.indicator_repository_backend == "sqlite":
        assert sqlite_repository is not None
        indicator_repository = sqlite_repository
    else:
        raise ValueError(f"unknown indicator repository backend: {config.indicator_repository_backend}")

    if config.state_store_backend == "memory":
        state_store = InMemoryStateStore()
    elif config.state_store_backend == "sqlite":
        assert sqlite_repository is not None
        state_store = sqlite_repository
    else:
        raise ValueError(f"unknown state store backend: {config.state_store_backend}")

    if config.web_artifact_store_backend != "memory":
        raise ValueError(f"unknown web artifact store backend: {config.web_artifact_store_backend}")

    core_repositories = (
        document_repository,
        event_repository,
        report_repository,
        indicator_repository,
        state_store,
    )
    if sqlite_repository is not None and all(repo is sqlite_repository for repo in core_repositories):
        unit_of_work = sqlite_repository
    elif all(
        isinstance(repo, expected)
        for repo, expected in (
            (document_repository, InMemoryDocumentRepository),
            (event_repository, InMemoryEventRepository),
            (report_repository, InMemoryReportRepository),
            (indicator_repository, InMemoryIndicatorRepository),
        )
    ):
        unit_of_work = InMemoryUnitOfWork(
            document_repository=document_repository,
            event_repository=event_repository,
            report_repository=report_repository,
            indicator_repository=indicator_repository,
            state_store=state_store,
        )
    else:
        raise ValueError(
            "atomic unit of work requires a uniform sqlite or in-memory persistence backend"
        )

    publishers = []
    for publisher_backend in config.publisher_backends:
        if publisher_backend == "disabled":
            publishers.append(NoOpReportPublisher())
        else:
            raise ValueError(f"unknown publisher backend: {publisher_backend}")

    dependencies = ApplicationDependencies(
        source_adapter=source_adapter,
        evaluator=evaluator,
        document_repository=document_repository,
        event_repository=event_repository,
        report_repository=report_repository,
        indicator_repository=indicator_repository,
        state_store=state_store,
        web_artifact_store=InMemoryWebArtifactStore(),
        unit_of_work=unit_of_work,
        publishers=tuple(publishers),
    )
    return ComposedApplication(
        application=DailyRadarApplication(dependencies, clock=active_clock),
        dependencies=dependencies,
    )


def _validate_optional_integrations(config: CompositionConfig) -> None:
    supported = {"ai", "collection_aggregator", "filesystem_artifacts"}
    unknown = set(config.optional_integrations) - supported
    if unknown:
        raise ValueError(f"unknown optional integrations: {sorted(unknown)}")
    unavailable_enabled = [
        name
        for name in ("ai", "collection_aggregator", "filesystem_artifacts")
        if config.optional_integrations.get(name, False)
    ]
    if unavailable_enabled:
        raise ValueError(
            "optional integration implementation is unavailable: "
            + ", ".join(sorted(unavailable_enabled))
        )
