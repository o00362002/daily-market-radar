"""Typed web read-model contracts (strict, provider-neutral).

These are the immutable projection artifacts the Astro dashboard consumes.
TypeScript types are generated from these models' JSON schema, so drift between
the Python contract and the TS types is caught in CI.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

WEB_SCHEMA_VERSION = "web/v1"


class WebModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ReportIndexEntryV1(WebModel):
    date: str
    run_id: str
    status: str
    evaluation_mode: str
    is_fixture: bool
    major_count: int = Field(ge=0)
    potential_count: int = Field(ge=0)
    taiwan_count: int = Field(ge=0)
    summary_path: str
    full_path: str


class ReportSummaryV1(WebModel):
    date: str
    run_id: str
    profile: str
    status: str
    evaluation_mode: str
    is_fixture: bool
    degradation_reasons: list[str]
    major_count: int = Field(ge=0)
    potential_count: int = Field(ge=0)
    taiwan_count: int = Field(ge=0)
    coverage_gap_count: int = Field(ge=0)
    retail_observed: int = Field(ge=0)
    crypto_observed: int = Field(ge=0)
    structural_directional: int = Field(ge=0)
    content_hash: str


class WebManifestV1(WebModel):
    schema_version: str
    generated_at: str
    latest_date: str
    latest_full_path: str
    report_count: int = Field(ge=0)
    report_dates: list[str]
    domains: list[str]
    indicator_ids: list[str]
    years: list[str]


class DomainIndexV1(WebModel):
    domain: str
    year: str
    entries: list[ReportIndexEntryV1]


class TaiwanIndexEntryV1(WebModel):
    date: str
    run_id: str
    taiwan_count: int = Field(ge=0)
    summary_path: str


class TaiwanIndexV1(WebModel):
    year: str
    entries: list[TaiwanIndexEntryV1]


class TrendPointV1(WebModel):
    date: str
    direction: str
    support_score: int = Field(ge=0, le=100)
    counter_score: int = Field(ge=0, le=100)
    confidence: str


class TrendSeriesV1(WebModel):
    indicator_id: str
    points: list[TrendPointV1]


class ReportsYearIndexV1(WebModel):
    year: str
    entries: list[ReportIndexEntryV1]


class LegacyReportEntryV1(WebModel):
    """A pre-dashboard human/chat-authored markdown report — never RadarReportV2 data."""

    date: str
    slug: str
    title: str
    variant: str
    source_path: str
    markdown_path: str
    content_hash: str


class LegacyReportIndexV1(WebModel):
    year: str
    entries: list[LegacyReportEntryV1]


def canonical_json_bytes(model: WebModel) -> bytes:
    payload = model.model_dump(mode="json")
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def web_json_schemas() -> dict[str, dict[str, Any]]:
    """All web read-model JSON schemas, keyed by model name (for TS generation)."""

    models: list[type[WebModel]] = [
        WebManifestV1,
        ReportSummaryV1,
        ReportIndexEntryV1,
        ReportsYearIndexV1,
        DomainIndexV1,
        TaiwanIndexEntryV1,
        TaiwanIndexV1,
        TrendPointV1,
        TrendSeriesV1,
        LegacyReportEntryV1,
        LegacyReportIndexV1,
    ]
    return {model.__name__: model.model_json_schema() for model in models}
