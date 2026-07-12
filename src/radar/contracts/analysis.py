from __future__ import annotations

import hashlib
import json
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CanonicalAnalysisModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class AnalysisProvenanceV1(CanonicalAnalysisModel):
    provider: Optional[str]
    model: Optional[str]
    generated_at: str
    source_report_date: str
    source_run_id: str
    source_context_hash: str
    prompt_version: str
    schema_version: Literal["ai-analysis/v1"]
    requested_mode: str
    effective_mode: str
    validation_status: Literal["valid", "fallback"]
    fallback_used: bool


class TranslationV1(CanonicalAnalysisModel):
    event_id: str
    original_text: str
    translated_text: str
    original_language: str


class AnalysisFindingV1(CanonicalAnalysisModel):
    finding_id: str
    label: Literal["verified_fact", "ai_inference", "background", "hypothesis", "uncertainty"]
    title: str
    summary: str
    source_event_ids: list[str]
    confidence: int = Field(ge=0, le=100)


class FutureTrendV1(CanonicalAnalysisModel):
    trend_id: str
    title: str
    stage: Literal["emerging", "forming", "established", "uncertain"]
    horizon: Literal["days", "weeks", "months", "years"]
    direction: Literal["up", "flat", "down", "mixed", "uncertain"]
    summary: str
    source_event_ids: list[str]
    counterevidence: list[str]
    uncertainties: list[str]
    next_watch: list[str]
    confidence: int = Field(ge=0, le=100)


class StructuralIndicatorAnalysisV1(CanonicalAnalysisModel):
    indicator_id: str
    label: str
    observation_date: str
    direction: Literal["toward", "against", "mixed", "insufficient"]
    support_score: int = Field(ge=0, le=100)
    counter_score: int = Field(ge=0, le=100)
    confidence: Union[int, Literal["insufficient"]]
    supporting_signal_ids: list[str]
    counter_signal_ids: list[str]
    missing_data: list[str]
    one_sentence_read: str
    next_verification: list[str]
    evaluation_mode: str


class LinkedIndicatorV1(CanonicalAnalysisModel):
    indicator_id: str
    label: str
    score: int = Field(ge=0, le=100)
    previous_score: Optional[int] = Field(default=None, ge=0, le=100)
    delta: Optional[int]
    direction: Literal["up", "flat", "down", "new", "insufficient"]
    status: Literal["observed", "partial", "insufficient"]
    method: str
    source_event_ids: list[str]
    components: dict[str, int]
    interpretation: str
    confidence: int = Field(ge=0, le=100)


class SupplementalEvidenceV1(CanonicalAnalysisModel):
    evidence_id: str
    gap_ref: str
    title: str
    url: str
    published_at: str
    fetched_at: str
    source_role: str
    evidence_grade: Literal["primary", "high_quality_secondary", "specialist", "secondary"]
    direct_taiwan_evidence: bool
    freshness: Literal["same_day", "weekend_72h", "candidate", "background"]
    summary: str


class AIAnalysisV1(CanonicalAnalysisModel):
    analysis_id: str
    date: str
    source_report_id: str
    executive_summary: list[str]
    translations: list[TranslationV1]
    key_findings: list[AnalysisFindingV1]
    future_trends: list[FutureTrendV1]
    structural_indicators: list[StructuralIndicatorAnalysisV1]
    linked_indicators: list[LinkedIndicatorV1]
    supplemental_evidence: list[SupplementalEvidenceV1] = Field(default_factory=list)
    limitations: list[str]
    provenance: AnalysisProvenanceV1

    def canonical_json_bytes(self) -> bytes:
        payload = self.model_dump(mode="json")
        return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )

    @classmethod
    def analysis_id_for(cls, *, source_context_hash: str, effective_mode: str, model: str | None) -> str:
        raw = f"{source_context_hash}|{effective_mode}|{model or 'none'}|ai-analysis/v1"
        return "analysis_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def ai_analysis_json_schema() -> dict[str, object]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **AIAnalysisV1.model_json_schema(),
    }
