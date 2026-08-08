from __future__ import annotations

import json
from pathlib import Path

import pytest

from radar.analysis.builder import build_deterministic_analysis, load_analysis_config
from radar.analysis.import_chat import _find_previous_report, hydrate_immutable_baseline_fields, validate_chat_analysis
from radar.contracts.analysis import AIAnalysisV1
from radar.contracts.report import RadarReportV2
from radar.runtime.runs import run_daily_fixture


ROOT = Path(__file__).resolve().parents[2]


def _report_for(date: str) -> RadarReportV2:
    result = run_daily_fixture(
        ROOT,
        date=date,
        freshrss_available=True,
        external_discovery_available=True,
        evaluation_mode="deterministic",
    )
    return RadarReportV2.from_payload(json.loads(json.dumps(result.report, ensure_ascii=False)))


def _report() -> RadarReportV2:
    return _report_for("2026-07-10")


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


def test_empty_immutable_arrays_hydrate_from_formal_baseline() -> None:
    report = _report()
    complete = _chat_analysis(report).model_dump(mode="json")
    compact = dict(complete)
    compact["translations"] = []
    compact["structural_indicators"] = []
    compact["linked_indicators"] = []

    hydrated, fields = hydrate_immutable_baseline_fields(
        report=report,
        payload=compact,
        repo_root=ROOT,
    )
    analysis = AIAnalysisV1.model_validate(hydrated)
    result = validate_chat_analysis(report=report, analysis=analysis, repo_root=ROOT)

    assert fields == ["translations", "structural_indicators", "linked_indicators"]
    assert hydrated["translations"] == complete["translations"]
    assert hydrated["structural_indicators"] == complete["structural_indicators"]
    assert hydrated["linked_indicators"] == complete["linked_indicators"]
    assert all(result["checks"].values())


def test_find_previous_report_uses_latest_prior_durable_projection(tmp_path: Path) -> None:
    previous = _report_for("2026-07-09")
    current = _report_for("2026-07-10")
    older = _report_for("2026-07-08")

    for report in (older, previous):
        path = tmp_path / "artifacts" / "web" / "v1" / "reports" / "2026" / report.date
        path.mkdir(parents=True, exist_ok=True)
        (path / f"full.{report.run_id}.json").write_bytes(report.canonical_json_bytes())

    found = _find_previous_report(report=current, repo_root=tmp_path)

    assert found is not None
    assert found.date == "2026-07-09"
    assert found.profile == current.profile


def test_non_empty_immutable_rewrite_is_not_hydrated_away() -> None:
    report = _report()
    payload = _chat_analysis(report).model_dump(mode="json")
    payload["structural_indicators"][0]["support_score"] = 99

    hydrated, fields = hydrate_immutable_baseline_fields(
        report=report,
        payload=payload,
        repo_root=ROOT,
    )
    analysis = AIAnalysisV1.model_validate(hydrated)

    assert fields == []
    with pytest.raises(ValueError, match="structural_indicators_preserved"):
        validate_chat_analysis(report=report, analysis=analysis, repo_root=ROOT)


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
