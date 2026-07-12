from __future__ import annotations

import json
from pathlib import Path

import pytest

from radar.analysis.builder import build_deterministic_analysis, load_analysis_config
from radar.analysis.import_chat import validate_chat_analysis
from radar.contracts.analysis import AIAnalysisV1
from radar.contracts.report import RadarReportV2
from radar.runtime.runs import run_daily_fixture


ROOT = Path(__file__).resolve().parents[2]


def _report() -> RadarReportV2:
    result = run_daily_fixture(
        ROOT,
        date="2026-07-10",
        freshrss_available=True,
        external_discovery_available=True,
        evaluation_mode="deterministic",
    )
    return RadarReportV2.from_payload(json.loads(json.dumps(result.report, ensure_ascii=False)))


def _chat_analysis(report: RadarReportV2) -> AIAnalysisV1:
    config = load_analysis_config(ROOT)
    baseline = build_deterministic_analysis(
        report,
        None,
        config,
        generated_at="2026-07-10T02:00:00+00:00",
    )
    payload = baseline.model_dump(mode="json")
    payload["analysis_id"] = "analysis_chat_20260710"
    payload["supplemental_evidence"] = [
        {
            "evidence_id": "supplemental_001",
            "gap_ref": "crypto:etf_flows",
            "title": "Official ETF flow update",
            "url": "https://example.com/official-flow",
            "published_at": "2026-07-10T01:00:00+00:00",
            "fetched_at": "2026-07-10T02:00:00+00:00",
            "source_role": "official_dataset",
            "evidence_grade": "primary",
            "direct_taiwan_evidence": False,
            "freshness": "same_day",
            "summary": "Fills the ETF-flow gap with an official same-day observation.",
        }
    ]
    payload["provenance"].update(
        {
            "provider": "chatgpt",
            "model": "GPT-5.6 Thinking",
            "requested_mode": "chat-assisted",
            "effective_mode": "chat-assisted",
            "validation_status": "valid",
            "fallback_used": False,
            "prompt_version": "chatgpt-gap-fill-v1",
        }
    )
    return AIAnalysisV1.model_validate(payload)


def test_valid_chat_analysis_preserves_deterministic_indicators() -> None:
    report = _report()
    analysis = _chat_analysis(report)

    result = validate_chat_analysis(report=report, analysis=analysis, repo_root=ROOT)

    assert result["supplemental_evidence_count"] == 1
    assert all(result["checks"].values())


def test_chat_analysis_rejects_structural_indicator_rewrite() -> None:
    report = _report()
    payload = _chat_analysis(report).model_dump(mode="json")
    payload["structural_indicators"][0]["support_score"] = 99
    analysis = AIAnalysisV1.model_validate(payload)

    with pytest.raises(ValueError, match="structural_indicators_preserved"):
        validate_chat_analysis(report=report, analysis=analysis, repo_root=ROOT)


def test_chat_analysis_rejects_non_https_supplemental_source() -> None:
    report = _report()
    payload = _chat_analysis(report).model_dump(mode="json")
    payload["supplemental_evidence"][0]["url"] = "http://example.com/insecure"
    analysis = AIAnalysisV1.model_validate(payload)

    with pytest.raises(ValueError, match="absolute HTTPS"):
        validate_chat_analysis(report=report, analysis=analysis, repo_root=ROOT)
