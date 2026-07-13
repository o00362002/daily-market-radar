from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from radar.contracts.analysis import (
    AIAnalysisV1,
    AnalysisFindingV1,
    AnalysisProvenanceV1,
    FutureTrendV1,
    LinkedIndicatorV1,
    StructuralIndicatorAnalysisV1,
    TranslationV1,
)
from radar.contracts.report import RadarReportV2, ReportItemV2


DEFAULT_CONFIG_PATH = Path("config/ai_analysis.json")

DOMAIN_LABELS = {
    "global_markets_macro": "全球市場與宏觀",
    "ai_agents_applications": "AI 代理與應用",
    "crypto_rwa_agent_payments": "加密、RWA 與代理支付",
    "retail_consumer_fashion": "零售、消費與時尚",
    "science_technology_industry": "科學、科技與產業",
}


def load_analysis_config(repo_root: Path) -> dict[str, Any]:
    path = repo_root / DEFAULT_CONFIG_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "ai-analysis/v1":
        raise ValueError("unsupported ai analysis schema version")
    core = payload.get("core_structural_indicators")
    auxiliary = payload.get("auxiliary_signal_indicators")
    if not isinstance(core, list) or not core:
        raise ValueError("ai analysis config requires core_structural_indicators")
    if not isinstance(auxiliary, list) or not auxiliary:
        raise ValueError("ai analysis config requires auxiliary_signal_indicators")
    core_ids = [str(row.get("indicator_id", "")) for row in core if isinstance(row, dict)]
    if len(core_ids) != len(set(core_ids)) or any(not value for value in core_ids):
        raise ValueError("core structural indicator ids must be unique and non-empty")
    runtime = json.loads((repo_root / "config/runtime_contract.json").read_text(encoding="utf-8"))
    domains = runtime.get("report_domains")
    if not isinstance(domains, list) or len(domains) != 5 or len(set(domains)) != 5:
        raise ValueError("AI analysis requires the five canonical report domains")
    payload["_canonical_report_domains"] = [str(domain) for domain in domains]
    return payload


def build_deterministic_analysis(
    report: RadarReportV2,
    previous_report: RadarReportV2 | None,
    config: dict[str, Any],
    *,
    generated_at: str | None = None,
    requested_mode: str = "deterministic",
    fallback_reason: str | None = None,
) -> AIAnalysisV1:
    stamp = generated_at or datetime.now(timezone.utc).isoformat()
    source_hash = _source_context_hash(report, config)
    structural = _build_structural_indicators(report, config)
    linked = _build_linked_indicators(report, previous_report, config)
    translations = [_translation(item) for item in report.items]
    findings = _build_findings(
        report,
        int(config.get("max_findings", 8)),
        [str(domain) for domain in config.get("_canonical_report_domains", [])],
    )
    trends = _build_trends(report, int(config.get("max_trends", 6)))
    summary = _build_summary(report, structural, linked, int(config.get("max_summary_points", 6)))
    fallback_used = requested_mode != "deterministic"
    limitations = _limitations(report, previous_report, fallback_reason)

    provenance = AnalysisProvenanceV1(
        provider=None,
        model=None,
        generated_at=stamp,
        source_report_date=report.date,
        source_run_id=report.run_id,
        source_context_hash=source_hash,
        prompt_version=str(config.get("prompt_version", "daily-analysis-v1")),
        schema_version="ai-analysis/v1",
        requested_mode=requested_mode,
        effective_mode="deterministic",
        validation_status="fallback" if fallback_used else "valid",
        fallback_used=fallback_used,
    )
    return AIAnalysisV1(
        analysis_id=AIAnalysisV1.analysis_id_for(
            source_context_hash=source_hash,
            effective_mode="deterministic",
            model=None,
        ),
        date=report.date,
        source_report_id=report.report_id,
        executive_summary=summary,
        translations=translations,
        key_findings=findings,
        future_trends=trends,
        structural_indicators=structural,
        linked_indicators=linked,
        limitations=limitations,
        provenance=provenance,
    )


def _source_context_hash(report: RadarReportV2, config: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(report.canonical_json_bytes())
    digest.update(json.dumps(config, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return digest.hexdigest()


def _original_title(item: ReportItemV2) -> str:
    prefix = "原文標題："
    for text in item.uncertainties:
        if text.startswith(prefix):
            return text[len(prefix) :].strip()
    return item.headline


def _translation(item: ReportItemV2) -> TranslationV1:
    original = _original_title(item)
    return TranslationV1(
        event_id=item.event_id,
        original_text=original,
        translated_text=item.headline,
        original_language="zh-Hant" if original == item.headline else "unknown",
    )


def _build_summary(
    report: RadarReportV2,
    structural_indicators: list[StructuralIndicatorAnalysisV1],
    auxiliary_indicators: list[LinkedIndicatorV1],
    limit: int,
) -> list[str]:
    major = sorted(
        (item for item in report.items if item.report_lane == "major"),
        key=lambda item: (-item.importance_score, -item.confidence_score, item.item_id),
    )
    potential = sorted(
        (item for item in report.items if item.report_lane == "potential"),
        key=lambda item: (-item.potential_score, -item.confidence_score, item.item_id),
    )
    taiwan_count = sum(1 for item in report.items if item.direct_taiwan_evidence)
    rows: list[str] = []
    dominant_domains = list(dict.fromkeys(item.primary_domain for item in [*major, *potential]))
    if dominant_domains:
        rows.append(
            f"今日大方向：訊號集中在{'、'.join(DOMAIN_LABELS.get(domain, domain) for domain in dominant_domains[:3])}，"
            f"同時出現 {len(major)} 件已具當期決策意義與 {len(potential)} 件仍待驗證的早期訊號；"
            "應觀察它們是否跨域匯流，而非只看單一新聞。"
        )
    elif not report.items:
        rows.append("今日大方向：目前沒有足夠的新增事件形成世界級主軸，請以覆蓋缺口與下一步補查為主。")
    rows.append(
        f"今日共有 {len(major)} 件重大項目、{len(potential)} 件潛力項目、"
        f"{taiwan_count} 件台灣直接證據項目。"
    )
    structural_state = "；".join(f"{row.label}={row.direction}" for row in structural_indicators)
    rows.append(f"三個核心結構指標：{structural_state}。")
    strongest = max(
        (row for row in auxiliary_indicators if row.status != "insufficient"),
        key=lambda row: row.score,
        default=None,
    )
    if strongest is not None:
        rows.append(f"輔助訊號最高為「{strongest.label}」{strongest.score} 分，方向為 {strongest.direction}。")
    if report.coverage_gaps:
        rows.append(f"本次仍有 {len(report.coverage_gaps)} 個覆蓋缺口，結論不得視為完整全球樣本。")
    return rows[: max(1, limit)]


def _build_findings(report: RadarReportV2, limit: int, canonical_domains: list[str]) -> list[AnalysisFindingV1]:
    ranked = sorted(
        report.items,
        key=lambda item: (
            0 if item.report_lane == "major" else 1,
            -max(item.importance_score, item.potential_score),
            -item.confidence_score,
            item.item_id,
        ),
    )
    # Keep one finding per canonical domain before filling remaining slots by
    # global relevance, so the AI layer cannot collapse the five-domain view.
    selected = [next((item for item in ranked if item.primary_domain == domain), None) for domain in canonical_domains]
    selected = [item for item in selected if item is not None]
    selected.extend(item for item in ranked if item not in selected)
    findings: list[AnalysisFindingV1] = []
    for item in selected[:limit]:
        label = "verified_fact" if item.report_lane == "major" else "hypothesis"
        summary = item.today_delta
        if item.report_lane == "potential" and item.next_watch:
            summary = f"{summary} 後續驗證：{item.next_watch}"
        finding_id = "finding_" + hashlib.sha256(f"{item.event_id}|{label}".encode("utf-8")).hexdigest()[:12]
        findings.append(
            AnalysisFindingV1(
                finding_id=finding_id,
                domain=item.primary_domain,
                label=label,
                title=item.headline,
                summary=summary,
                source_event_ids=[item.event_id],
                confidence=item.confidence_score,
            )
        )
    return findings


def _build_trends(report: RadarReportV2, limit: int) -> list[FutureTrendV1]:
    relevant = sorted(
        report.items,
        key=lambda item: (
            0 if item.report_lane == "potential" else 1,
            -max(item.potential_score, item.importance_score),
            -item.confidence_score,
            item.item_id,
        ),
    )
    themes: dict[str, tuple[str, set[str]]] = {
        "ai_productivity_and_work": (
            "AI 生產力、工作重組與採用擴散",
            {"ai_agents_applications", "science_technology_industry", "global_markets_macro"},
        ),
        "capital_and_infrastructure": (
            "資本、基礎設施與新金融管線",
            {"global_markets_macro", "crypto_rwa_agent_payments", "science_technology_industry"},
        ),
        "retail_brand_and_consumption": (
            "零售、品牌分化與消費結構重排",
            {"retail_consumer_fashion", "global_markets_macro", "ai_agents_applications"},
        ),
    }
    trends: list[FutureTrendV1] = []
    for theme_id, (title, domains) in list(themes.items())[:limit]:
        items = [item for item in relevant if item.primary_domain in domains]
        if not items:
            continue
        source_ids = sorted({item.event_id for item in items})
        potential_items = [item for item in items if item.report_lane == "potential"]
        stage = "emerging" if potential_items else "forming"
        direction = "up" if sum(item.potential_score for item in items) >= sum(item.importance_score for item in items) else "mixed"
        confidence = round(sum(item.confidence_score for item in items) / len(items))
        trend_id = "trend_" + hashlib.sha256(f"{theme_id}|{'|'.join(source_ids)}".encode("utf-8")).hexdigest()[:12]
        counterevidence = list(dict.fromkeys(text for item in items for text in item.counterevidence))[:6]
        uncertainties = list(dict.fromkeys(text for item in items for text in item.uncertainties))[:6]
        next_watch = list(dict.fromkeys(item.next_watch for item in items if item.next_watch))[:6]
        trends.append(
            FutureTrendV1(
                trend_id=trend_id,
                title=title,
                stage=stage,
                horizon="three_to_six_months",
                horizon_months=[3, 6],
                synthesis_scope="global",
                source_domain_ids=sorted({item.primary_domain for item in items}),
                direction=direction,
                summary=f"若上述 {len(source_ids)} 個跨域訊號持續出現，未來 3–6 個月可能形成此方向；這是條件式情境，不是確定預測。",
                source_event_ids=source_ids,
                counterevidence=counterevidence,
                uncertainties=uncertainties,
                next_watch=next_watch,
                confidence=confidence,
            )
        )
    return trends


def _trend_stage(value: str | None) -> str:
    mapping = {
        "萌芽": "emerging",
        "成形": "forming",
        "形成": "forming",
        "成熟": "established",
        "emerging": "emerging",
        "forming": "forming",
        "established": "established",
    }
    return mapping.get(value or "", "uncertain")


def _structural_direction(value: str) -> str:
    mapping = {
        "toward": "toward",
        "supporting": "toward",
        "support": "toward",
        "against": "against",
        "counter": "against",
        "mixed": "mixed",
        "insufficient": "insufficient",
    }
    try:
        return mapping[value]
    except KeyError as exc:
        raise ValueError(f"unsupported structural indicator direction: {value}") from exc


def _build_structural_indicators(
    report: RadarReportV2,
    config: dict[str, Any],
) -> list[StructuralIndicatorAnalysisV1]:
    observations = {row.indicator_id: row for row in report.structural_indicators}
    rows: list[StructuralIndicatorAnalysisV1] = []
    for definition in config["core_structural_indicators"]:
        indicator_id = str(definition["indicator_id"])
        observation = observations.get(indicator_id)
        if observation is None:
            raise ValueError(f"missing core structural indicator: {indicator_id}")
        rows.append(
            StructuralIndicatorAnalysisV1(
                indicator_id=indicator_id,
                label=str(definition["label"]),
                observation_date=observation.observation_date,
                direction=_structural_direction(observation.direction),
                support_score=observation.support_score,
                counter_score=observation.counter_score,
                confidence=observation.confidence,
                supporting_signal_ids=list(observation.supporting_signal_ids),
                counter_signal_ids=list(observation.counter_signal_ids),
                missing_data=list(observation.missing_data),
                one_sentence_read=observation.one_sentence_read,
                next_verification=list(observation.next_verification),
                evaluation_mode=observation.evaluation_mode,
                components=list(observation.components),
            )
        )
    return rows


def _build_linked_indicators(
    report: RadarReportV2,
    previous_report: RadarReportV2 | None,
    config: dict[str, Any],
) -> list[LinkedIndicatorV1]:
    rows: list[LinkedIndicatorV1] = []
    for definition in config["auxiliary_signal_indicators"]:
        current = _indicator_snapshot(report, definition)
        previous = _indicator_snapshot(previous_report, definition) if previous_report is not None else None
        previous_score = previous["score"] if previous and previous["status"] != "insufficient" else None
        delta = current["score"] - previous_score if previous_score is not None else None
        direction = _indicator_direction(current["status"], delta)
        rows.append(
            LinkedIndicatorV1(
                indicator_id=str(definition["indicator_id"]),
                label=str(definition["label"]),
                score=current["score"],
                previous_score=previous_score,
                delta=delta,
                direction=direction,
                status=current["status"],
                method=current["method"],
                source_event_ids=current["source_event_ids"],
                components=current["components"],
                interpretation=_indicator_interpretation(str(definition["label"]), current["score"], delta),
                confidence=current["confidence"],
            )
        )
    return rows


def _indicator_snapshot(report: RadarReportV2 | None, definition: dict[str, Any]) -> dict[str, Any]:
    if report is None:
        return _empty_indicator()
    selector = str(definition.get("selector", "domain"))
    values = {str(value) for value in definition.get("values", [])}
    if selector == "domain":
        items = [item for item in report.items if item.primary_domain in values]
        return _item_indicator(report, items)
    if selector == "taiwan_direct":
        items = [item for item in report.items if item.direct_taiwan_evidence]
        return _item_indicator(report, items)
    if selector == "cross_domain":
        return _cross_domain_indicator(report)
    if selector == "evidence_quality":
        return _evidence_quality_indicator(report)
    raise ValueError(f"unknown indicator selector: {selector}")


def _empty_indicator() -> dict[str, Any]:
    return {
        "score": 0,
        "status": "insufficient",
        "source_event_ids": [],
        "components": {},
        "method": "沒有可比較資料。",
        "confidence": 0,
    }


def _item_indicator(report: RadarReportV2, items: list[ReportItemV2]) -> dict[str, Any]:
    if not items:
        return _empty_indicator()
    count = len(items)
    importance = round(sum(item.importance_score for item in items) / count)
    potential = round(sum(item.potential_score for item in items) / count)
    confidence = round(sum(item.confidence_score for item in items) / count)
    breadth = min(100, count * 12)
    score = round(importance * 0.30 + potential * 0.30 + confidence * 0.25 + breadth * 0.15)
    status = "partial" if report.coverage_gaps or confidence < 60 else "observed"
    ranked = sorted(items, key=lambda item: (-max(item.importance_score, item.potential_score), item.item_id))
    return {
        "score": score,
        "status": status,
        "source_event_ids": [item.event_id for item in ranked[:20]],
        "components": {
            "importance_avg": importance,
            "potential_avg": potential,
            "confidence_avg": confidence,
            "breadth": breadth,
            "item_count": count,
        },
        "method": "重要性 30%＋潛力 30%＋信心 25%＋事件廣度 15%；AI 不得修改分數。",
        "confidence": confidence,
    }


def _cross_domain_indicator(report: RadarReportV2) -> dict[str, Any]:
    if not report.items:
        return _empty_indicator()
    domains = {item.primary_domain for item in report.items}
    domain_breadth = min(100, round(len(domains) / 5 * 100))
    potential_ratio = round(sum(item.report_lane == "potential" for item in report.items) / len(report.items) * 100)
    confidence = round(sum(item.confidence_score for item in report.items) / len(report.items))
    score = round(domain_breadth * 0.40 + potential_ratio * 0.35 + confidence * 0.25)
    status = "partial" if report.coverage_gaps else "observed"
    ranked = sorted(report.items, key=lambda item: (-item.potential_score, -item.confidence_score, item.item_id))
    return {
        "score": score,
        "status": status,
        "source_event_ids": [item.event_id for item in ranked[:20]],
        "components": {
            "domain_breadth": domain_breadth,
            "potential_ratio": potential_ratio,
            "confidence_avg": confidence,
            "domain_count": len(domains),
        },
        "method": "領域廣度 40%＋潛力事件比率 35%＋平均信心 25%；僅衡量匯流強度，不代表因果。",
        "confidence": confidence,
    }


def _evidence_quality_indicator(report: RadarReportV2) -> dict[str, Any]:
    if not report.items:
        return _empty_indicator()
    confidence = round(sum(item.confidence_score for item in report.items) / len(report.items))
    source_breadth = min(100, len(set(report.source_audit.sources_checked)) * 3)
    gap_penalty = min(40, len(report.coverage_gaps) * 4)
    failure_penalty = min(30, len(report.source_audit.failures) * 6)
    score = max(0, min(100, round(confidence * 0.75 + source_breadth * 0.25 - gap_penalty - failure_penalty)))
    status = "partial" if gap_penalty or failure_penalty else "observed"
    ranked = sorted(report.items, key=lambda item: (-item.confidence_score, item.item_id))
    return {
        "score": score,
        "status": status,
        "source_event_ids": [item.event_id for item in ranked[:20]],
        "components": {
            "confidence_avg": confidence,
            "source_breadth": source_breadth,
            "gap_penalty": gap_penalty,
            "failure_penalty": failure_penalty,
        },
        "method": "平均信心 75%＋來源廣度 25%，再扣除覆蓋缺口與來源失敗；AI 不得修改分數。",
        "confidence": confidence,
    }


def _indicator_direction(status: str, delta: int | None) -> str:
    if status == "insufficient":
        return "insufficient"
    if delta is None:
        return "new"
    if delta >= 5:
        return "up"
    if delta <= -5:
        return "down"
    return "flat"


def _indicator_interpretation(label: str, score: int, delta: int | None) -> str:
    strength = "偏強" if score >= 70 else "中等" if score >= 45 else "偏弱"
    if delta is None:
        return f"{label}目前為{strength}，尚無前期可比較基準。"
    if delta >= 5:
        return f"{label}目前為{strength}，較前期上升 {delta} 分。"
    if delta <= -5:
        return f"{label}目前為{strength}，較前期下降 {abs(delta)} 分。"
    return f"{label}目前為{strength}，較前期變化不大。"


def _limitations(
    report: RadarReportV2,
    previous_report: RadarReportV2 | None,
    fallback_reason: str | None,
) -> list[str]:
    rows = [
        "AI 解讀層不改寫 RadarReportV2；事實仍以原報告與來源證據為準。",
        "三個核心結構指標直接沿用 RadarReportV2 的 deterministic 評估；AI 不得修改方向、分數或證據。",
    ]
    if previous_report is None:
        rows.append("缺少前一期同 profile 報告，輔助訊號指標方向只能標記為 new。")
    if report.coverage_gaps:
        rows.append(f"存在 {len(report.coverage_gaps)} 個覆蓋缺口，趨勢推演可能受樣本偏差影響。")
    if fallback_reason:
        rows.append(f"AI 語意增強未使用或失敗：{fallback_reason}；目前顯示 deterministic fallback。")
    return rows
