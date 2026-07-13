from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CanonicalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class EvidenceLinkV2(CanonicalModel):
    url: str
    source_id: str
    fetched_at: str


class ScoreExplanationV1(CanonicalModel):
    importance: dict[str, int]
    potential: dict[str, int]
    confidence: dict[str, int]
    rationale: str


class ReportItemV2(CanonicalModel):
    item_id: str
    event_id: str
    signal_id: Optional[str]
    primary_domain: str
    report_lane: Literal["major", "potential"]
    candidate_type: Optional[str]
    formation_level: Optional[str]
    headline: str
    first_seen_at: str
    today_delta: str
    importance_score: int = Field(ge=0, le=100)
    potential_score: int = Field(ge=0, le=100)
    confidence_score: int = Field(ge=0, le=100)
    evidence_links: list[EvidenceLinkV2]
    direct_taiwan_evidence: list[EvidenceLinkV2]
    taiwan_implication: str
    counterevidence: list[str]
    uncertainties: list[str]
    next_watch: str
    score_explanation: ScoreExplanationV1


class CoverageCellV2(CanonicalModel):
    domain: str
    macro_region: str
    language: str
    source_role: str
    channel: str
    time_window: str
    status: str
    observed_count: int = Field(ge=0)


class CoverageGapV2(CanonicalModel):
    domain: str
    macro_region: str
    language: str
    source_role: str
    channel: str
    time_window: str
    reason: str
    message: str


class SourceFailureV1(CanonicalModel):
    source_id: str
    reason: str
    channel: str = ""


class SourceAuditV2(CanonicalModel):
    ingestion_mode: str
    registry_checked: bool
    sources_checked: list[str]
    failures: list[SourceFailureV1]
    sources_not_executed: list[str]
    integration_status: dict[str, str]
    candidate_retry_paths_used: list[str]
    taiwan_direct_sources_checked: list[str]
    remaining_gaps: list[str]


class RejectionCountersV2(CanonicalModel):
    duplicate_rejection_count: int = Field(ge=0)
    field_overlap_rejection_count: int = Field(ge=0)
    niche_low_novelty_rejection_count: int = Field(ge=0)
    candidate_retry_paths_used: list[str]
    taiwan_qualified_item_count_after_audit: int = Field(ge=0)
    taiwan_direct_sources_checked: list[str]


class MatrixObservationV1(CanonicalModel):
    status: str
    signal_ids: list[str]
    data_checked: list[str]
    gap: str


class StructuralIndicatorEvidenceV1(CanonicalModel):
    event_id: str
    headline: str
    summary: str
    direction: Literal["toward", "against", "mixed"]


class StructuralIndicatorComponentV1(CanonicalModel):
    component_id: str
    label: str
    direction: Literal["toward", "against", "mixed", "insufficient"]
    score: int = Field(ge=0, le=100)
    support_score: int = Field(ge=0, le=100)
    counter_score: int = Field(ge=0, le=100)
    evidence: list[StructuralIndicatorEvidenceV1]
    missing_data: list[str]


class StructuralIndicatorObservationV1(CanonicalModel):
    indicator_id: str
    observation_date: str
    direction: str
    support_score: int = Field(ge=0, le=100)
    counter_score: int = Field(ge=0, le=100)
    confidence: Union[int, Literal["insufficient"]]
    supporting_signal_ids: list[str]
    counter_signal_ids: list[str]
    missing_data: list[str]
    one_sentence_read: str
    next_verification: list[str]
    evaluation_mode: str
    components: list[StructuralIndicatorComponentV1] = Field(default_factory=list)


class SignalV1(CanonicalModel):
    signal_id: str
    event_id: str
    lifecycle: str
    what_would_confirm: str
    what_would_invalidate: str
    next_check_at: str


class BacktestV1(CanonicalModel):
    status: Literal["complete", "partial", "failed"]
    findings: list[str]
    next_adjustments: list[str]


class TokenUsageV1(CanonicalModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class EvaluationAuditV1(CanonicalModel):
    requested_mode: str
    effective_mode: str
    evaluator: str
    model: Optional[str]
    provider: Optional[str]
    started_at: str
    finished_at: str
    cache_hits: int = Field(ge=0)
    evaluated_item_count: int = Field(ge=0)
    failed_item_count: int = Field(ge=0)
    token_usage: TokenUsageV1
    estimated_cost_usd: float = Field(ge=0)
    source_context_hash: str
    validation_status: str
    degradation_reasons: list[str]


class EventResolutionAuditV1(CanonicalModel):
    events_observed: int = Field(ge=0)
    new_events: int = Field(ge=0)
    matched_existing_events: int = Field(ge=0)
    material_events: int = Field(ge=0)
    unchanged_events: int = Field(ge=0)
    duplicate_only_events: int = Field(ge=0)
    unresolved_matches: int = Field(ge=0)
    match_strategy_counts: dict[str, int]
    delta_type_counts: dict[str, int]
    title_only_changes_rejected: int = Field(ge=0)
    background_only_rejected: int = Field(ge=0)


def _default_event_resolution_audit() -> dict[str, Any]:
    return {
        "events_observed": 0,
        "new_events": 0,
        "matched_existing_events": 0,
        "material_events": 0,
        "unchanged_events": 0,
        "duplicate_only_events": 0,
        "unresolved_matches": 0,
        "match_strategy_counts": {},
        "delta_type_counts": {},
        "title_only_changes_rejected": 0,
        "background_only_rejected": 0,
    }


class RadarReportV2(CanonicalModel):
    run_id: str
    date: str
    profile: str
    status: Literal["complete", "partial", "failed"]
    degradation_reasons: list[str]
    items: list[ReportItemV2]
    coverage_cells: list[CoverageCellV2]
    coverage_gaps: list[CoverageGapV2]
    signals: list[SignalV1]
    source_audit: SourceAuditV2
    rejection_counters: RejectionCountersV2
    retail_matrix: dict[str, MatrixObservationV1]
    crypto_matrix: dict[str, MatrixObservationV1]
    structural_indicators: list[StructuralIndicatorObservationV1]
    evaluation_audit: EvaluationAuditV1
    event_resolution_audit: EventResolutionAuditV1
    backtest: BacktestV1
    contract_version: Literal["2.0"]

    @property
    def report_id(self) -> str:
        return f"report:{self.run_id}"

    def canonical_json_bytes(self) -> bytes:
        payload = self.model_dump(mode="json")
        return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RadarReportV2":
        payload = _with_item_score_explanations(payload)
        payload = _with_event_resolution_audit(payload)
        source_audit = payload.get("source_audit", {})
        canonical_source_fields = {
            "ingestion_mode",
            "registry_checked",
            "sources_checked",
            "failures",
            "sources_not_executed",
            "integration_status",
            "candidate_retry_paths_used",
            "taiwan_direct_sources_checked",
            "remaining_gaps",
        }
        if isinstance(source_audit, dict) and canonical_source_fields.issubset(source_audit):
            legacy_aliases = {
                "external_discovery_checked",
                "freshrss_checked",
                "remaining_gap",
                "rss_failures",
                "rss_sources_checked",
                "web_api_social_sources_not_executed",
            }
            if set(source_audit) - canonical_source_fields <= legacy_aliases:
                normalized = copy.deepcopy(payload)
                normalized["source_audit"] = {
                    key: value
                    for key, value in source_audit.items()
                    if key in canonical_source_fields
                }
                return cls.model_validate(normalized)
            return cls.model_validate(payload)
        return cls.model_validate(_migrate_legacy_v2_payload(payload))


RadarReport = RadarReportV2


def radar_report_json_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **RadarReportV2.model_json_schema(),
    }


def _migrate_legacy_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("contract_version") != "2.0":
        raise ValueError("only legacy contract_version 2.0 payloads can be migrated")
    migrated = copy.deepcopy(payload)
    migrated = _with_item_score_explanations(migrated)
    migrated = _with_event_resolution_audit(migrated)
    migrated.setdefault("signals", [])

    old_audit = migrated.get("source_audit", {})
    if not isinstance(old_audit, dict):
        raise ValueError("legacy source_audit must be an object")
    legacy_failures = old_audit.get("failures", old_audit.get("rss_failures", []))
    failures = [
        {
            "source_id": str(failure.get("source_id", "unknown")),
            "reason": str(failure.get("reason", "legacy source failure")),
            "channel": str(failure.get("channel", failure.get("adapter_url", ""))),
        }
        for failure in legacy_failures
        if isinstance(failure, dict)
    ]
    integration_status = dict(old_audit.get("integration_status", {}))
    if "freshrss_checked" in old_audit:
        integration_status["collection_aggregator"] = (
            "checked" if old_audit.get("freshrss_checked") else "unavailable"
        )
    if "external_discovery_checked" in old_audit:
        integration_status["external_discovery"] = (
            "checked" if old_audit.get("external_discovery_checked") else "not_executed"
        )
    if old_audit.get("web_api_social_sources_not_executed"):
        integration_status["other_source_adapters"] = "not_executed"
    migrated["source_audit"] = {
        "ingestion_mode": str(old_audit.get("ingestion_mode", "legacy_runtime_v2")),
        "registry_checked": bool(old_audit.get("registry_checked", False)),
        "sources_checked": list(old_audit.get("sources_checked", old_audit.get("rss_sources_checked", []))),
        "failures": failures,
        "sources_not_executed": list(
            old_audit.get("sources_not_executed", old_audit.get("web_api_social_sources_not_executed", []))
        ),
        "integration_status": integration_status,
        "candidate_retry_paths_used": list(old_audit.get("candidate_retry_paths_used", [])),
        "taiwan_direct_sources_checked": list(old_audit.get("taiwan_direct_sources_checked", [])),
        "remaining_gaps": list(old_audit.get("remaining_gaps", old_audit.get("remaining_gap", []))),
    }

    for observation in migrated.get("structural_indicators", []):
        if not isinstance(observation, dict):
            continue
        observation.setdefault("observation_date", str(migrated.get("date", "")))
        observation.setdefault("support_score", 0)
        observation.setdefault("counter_score", 0)
        observation.setdefault("evaluation_mode", "not_evaluated")

    if "evaluation_audit" not in migrated:
        report_date = str(migrated.get("date", "1970-01-01"))
        context = json.dumps(migrated.get("items", []), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        migrated["evaluation_audit"] = {
            "requested_mode": "not_recorded",
            "effective_mode": "not_evaluated",
            "evaluator": "legacy_runtime_v2",
            "model": None,
            "provider": None,
            "started_at": f"{report_date}T00:00:00+00:00",
            "finished_at": f"{report_date}T00:00:00+00:00",
            "cache_hits": 0,
            "evaluated_item_count": 0,
            "failed_item_count": 0,
            "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "estimated_cost_usd": 0.0,
            "source_context_hash": hashlib.sha256(context.encode("utf-8")).hexdigest(),
            "validation_status": "migrated_legacy",
            "degradation_reasons": ["legacy_evaluation_audit_unavailable"],
        }
    return migrated


def _with_event_resolution_audit(payload: dict[str, Any]) -> dict[str, Any]:
    if "event_resolution_audit" in payload:
        return payload
    migrated = copy.deepcopy(payload)
    migrated["event_resolution_audit"] = _default_event_resolution_audit()
    return migrated


def _with_item_score_explanations(payload: dict[str, Any]) -> dict[str, Any]:
    items = payload.get("items")
    if not isinstance(items, list):
        return payload
    if all(isinstance(item, dict) and "score_explanation" in item for item in items):
        return payload
    migrated = copy.deepcopy(payload)
    migrated["items"] = [
        _with_item_score_explanation(item) if isinstance(item, dict) else item
        for item in items
    ]
    return migrated


def _with_item_score_explanation(item: dict[str, Any]) -> dict[str, Any]:
    if "score_explanation" in item:
        return item
    return {
        **item,
        "score_explanation": {
            "importance": {"legacy_score": int(item.get("importance_score", 0))},
            "potential": {"legacy_score": int(item.get("potential_score", 0))},
            "confidence": {"legacy_score": int(item.get("confidence_score", 0))},
            "rationale": "Legacy item migrated without deterministic component details.",
        },
    }
