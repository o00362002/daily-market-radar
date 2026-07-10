"""Backward-compatible runtime façade over the provider-neutral application."""

from __future__ import annotations

from pathlib import Path

from radar.application import ApplicationRunResult, DailyRunRequest
from radar.composition import CompositionConfig, compose_application
from radar.contracts.runtime import RuntimeContract
from radar.domain.models import RunResult
from radar.schemas.source import SourceRegistry


class _LegacySourceAuditView(dict[str, object]):
    """Canonical JSON mapping with legacy Python key lookups.

    Legacy aliases are deliberately not stored as mapping fields, so JSON output
    remains valid against the strict canonical report schema.
    """

    def __init__(self, canonical: dict[str, object], aliases: dict[str, object]) -> None:
        super().__init__(canonical)
        self._legacy_aliases = aliases

    def __contains__(self, key: object) -> bool:
        return super().__contains__(key) or key in self._legacy_aliases

    def __getitem__(self, key: str) -> object:
        if super().__contains__(key):
            return super().__getitem__(key)
        return self._legacy_aliases[key]

    def get(self, key: str, default: object = None) -> object:
        if key in self:
            return self[key]
        return default


def _legacy_result(application_result: ApplicationRunResult) -> RunResult:
    report = application_result.report.model_dump(mode="json")
    source_audit = report["source_audit"]
    integration_status = source_audit["integration_status"]
    legacy_aliases = {
        "freshrss_checked": integration_status.get("collection_aggregator") in {"available", "checked"},
        "external_discovery_checked": integration_status.get("external_discovery") in {"available", "checked"},
        "rss_sources_checked": list(source_audit["sources_checked"]),
        "rss_failures": [
            {
                "source_id": failure["source_id"],
                "adapter_url": failure["channel"],
                "reason": failure["reason"],
            }
            for failure in source_audit["failures"]
        ],
        "web_api_social_sources_not_executed": list(source_audit["sources_not_executed"]),
        "remaining_gap": list(source_audit["remaining_gaps"]),
    }
    report["source_audit"] = _LegacySourceAuditView(source_audit, legacy_aliases)
    contract_domains = [item.primary_domain for item in application_result.report.items]
    domains_seen = list(dict.fromkeys(contract_domains))
    return RunResult(
        run_id=application_result.report.run_id,
        status=application_result.report.status,
        degradation_reasons=list(application_result.report.degradation_reasons),
        languages_seen=sorted({document.language for document in application_result.documents}),
        regions_seen=sorted({document.macro_region for document in application_result.documents}),
        domains_seen=domains_seen,
        event_ids=[event.event_id for event in application_result.events],
        selected_item_ids=[item.item_id for item in application_result.report.items],
        report=report,
    )


def run_daily_fixture(
    repo_root: Path,
    date: str,
    freshrss_available: bool,
    external_discovery_available: bool = True,
    profile_name: str = "daily_push",
    database_path: Path | None = None,
) -> RunResult:
    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    composed = compose_application(
        CompositionConfig(
            source_backend="fixture",
            report_repository_backend="sqlite" if database_path is not None else "memory",
            database_path=database_path,
            migrations_dir=repo_root / "migrations" if database_path is not None else None,
            optional_integrations={
                "ai": False,
                "collection_aggregator": False,
                "filesystem_artifacts": False,
            },
            external_discovery_available=external_discovery_available,
            fixture_collection_aggregator_available=freshrss_available,
        )
    )
    result = composed.application.run(
        DailyRunRequest(
            date=date,
            profile=profile_name,
            ingestion_mode="fixture",
            evaluation_mode="deterministic",
        ),
        contract,
    )
    return _legacy_result(result)


def run_daily_live_rss(
    repo_root: Path,
    date: str,
    *,
    profile_name: str = "daily_push",
    timeout_seconds: int = 12,
    per_feed_limit: int = 20,
    database_path: Path | None = None,
) -> RunResult:
    contract = RuntimeContract.from_file(repo_root / "config/runtime_contract.json")
    registry = SourceRegistry.from_file(repo_root / "config/source_registry.json")
    registry.validate()
    composed = compose_application(
        CompositionConfig(
            source_backend="rss",
            report_repository_backend="sqlite" if database_path is not None else "memory",
            database_path=database_path,
            migrations_dir=repo_root / "migrations" if database_path is not None else None,
            timeout_seconds=timeout_seconds,
            per_feed_limit=per_feed_limit,
        ),
        source_registry=registry,
    )
    result = composed.application.run(
        DailyRunRequest(
            date=date,
            profile=profile_name,
            ingestion_mode="live_rss",
            evaluation_mode="deterministic",
        ),
        contract,
    )
    return _legacy_result(result)
