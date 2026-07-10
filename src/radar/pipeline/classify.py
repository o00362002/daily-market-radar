from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from radar.domain.models import Event, Signal, normalize_text, stable_id


@dataclass(frozen=True)
class PotentialAssessment:
    lane: str
    candidate_type: str | None
    formation_level: str | None
    lifecycle: str | None
    feature_score: int
    rationale: str


_EARLY_STAGE_TERMS = {
    "pilot",
    "prototype",
    "beta",
    "sandbox",
    "trial",
    "experiment",
    "research preview",
    "proof of concept",
    "poc",
    "tests",
    "testing",
    "試點",
    "原型",
    "測試",
    "實驗",
    "沙盒",
    "概念驗證",
}

_APPLICATION_TERMS = {
    "agent",
    "agentic",
    "api",
    "runtime",
    "developer tool",
    "automation",
    "robotics",
    "digital twin",
    "copilot",
    "assistant",
    "integration",
    "新應用",
    "代理",
    "自動化",
    "機器人",
    "開發者工具",
    "整合",
}

_BUSINESS_MODEL_TERMS = {
    "business model",
    "subscription",
    "marketplace",
    "retail media",
    "usage based",
    "pay per use",
    "revenue share",
    "agent payment",
    "商業模式",
    "訂閱",
    "平台抽成",
    "零售媒體",
    "按量付費",
    "代理支付",
}

_COMBINATION_TERMS = {
    "cross-domain",
    "cross domain",
    "combined with",
    "powered by",
    "integrated with",
    "x ai",
    "ai x",
    "新組合",
    "跨領域",
    "結合",
    "融合",
}

_TREND_TERMS = {
    "adoption",
    "rollout",
    "expansion",
    "scaling",
    "diffusion",
    "growing demand",
    "new region",
    "procurement",
    "採用",
    "擴張",
    "擴散",
    "規模化",
    "新市場",
    "採購",
}

_POTENTIAL_DELTA_TYPES = {
    "new_source_confirmation",
    "new_entity",
    "launch_or_release",
    "pilot_to_production",
    "new_region",
    "adoption_expansion",
    "funding_change",
    "hiring_change",
    "supply_chain_change",
    "trend_evidence_only",
}


def assess_event(event: Event) -> PotentialAssessment:
    """Classify Major/Potential from event content, not publisher role alone.

    Source lane is only a small supporting feature. An official/company source can
    still be Potential when it describes an early application, pilot, new model or
    diffusion signal; a bottom-up source is not Potential without content evidence.
    """

    if not event.documents:
        return PotentialAssessment("major", None, None, None, 0, "事件沒有可判讀文件。")

    text = normalize_text(
        " ".join(
            part
            for document in event.documents
            for part in (document.title, document.summary, document.action, document.object)
            if part
        )
    )
    delta_types = {delta.delta_type for delta in event.deltas}
    source_ids = {document.source_id for document in event.documents}
    domains = {document.primary_domain for document in event.documents}

    score = 0
    reasons: list[str] = []
    candidate_type: str | None = None

    if _contains_any(text, _BUSINESS_MODEL_TERMS):
        candidate_type = "新商業模式"
        score += 42
        reasons.append("出現新商業模式特徵")
    elif _contains_any(text, _COMBINATION_TERMS) or len(domains) > 1:
        candidate_type = "新組合"
        score += 40
        reasons.append("出現跨領域或技術組合特徵")
    elif _contains_any(text, _APPLICATION_TERMS):
        candidate_type = "新應用"
        score += 36
        reasons.append("出現新應用或工具特徵")
    elif _contains_any(text, _TREND_TERMS):
        candidate_type = "新趨勢"
        score += 34
        reasons.append("出現採用、擴散或需求變化特徵")

    if _contains_any(text, _EARLY_STAGE_TERMS):
        candidate_type = candidate_type or "新應用"
        score += 22
        reasons.append("仍處於試點、原型或實驗階段")

    if delta_types & _POTENTIAL_DELTA_TYPES:
        candidate_type = candidate_type or "新趨勢"
        score += 20
        reasons.append("事件有新的採用、擴散或驗證增量")

    if len(source_ids) > 1:
        score += 8
        reasons.append("已有多個獨立來源")

    # Publisher/source lane may support the assessment, but can never decide it.
    if any(document.lane == "bottom_up" for document in event.documents):
        score += 6
        reasons.append("包含 bottom-up 弱訊號來源")

    is_potential = candidate_type is not None and score >= 30
    if not is_potential:
        return PotentialAssessment(
            lane="major",
            candidate_type=None,
            formation_level=None,
            lifecycle=None,
            feature_score=score,
            rationale="；".join(reasons) if reasons else "未出現足以判定潛力訊號的內容特徵。",
        )

    formation_level, lifecycle = _formation(delta_types, len(source_ids), event)
    return PotentialAssessment(
        lane="potential",
        candidate_type=candidate_type,
        formation_level=formation_level,
        lifecycle=lifecycle,
        feature_score=min(100, score),
        rationale="；".join(reasons),
    )


def classify_potential_signals(events: list[Event]) -> list[Signal]:
    signals: list[Signal] = []
    for event in events:
        assessment = assess_event(event)
        if assessment.lane != "potential":
            continue
        signals.append(
            Signal(
                signal_id=stable_id("sig", [event.event_id]),
                event_id=event.event_id,
                lifecycle=assessment.lifecycle or "seed",
                what_would_confirm="後續獨立採用、採購、使用量、資金、招聘、跨區域擴散或監管進展。",
                what_would_invalidate="後續沒有重複證據、試點終止，或出現可信反證。",
                next_check_at=_next_check_at(event),
            )
        )
    return signals


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _formation(delta_types: set[str], source_count: int, event: Event) -> tuple[str, str]:
    metric_count = sum(
        1
        for document in event.documents
        for metric in document.facts
        if metric != "source_roles"
    )
    if delta_types & {"pilot_to_production", "adoption_expansion", "new_region"}:
        return "擴散中", "diffusing"
    if source_count >= 2 or "new_source_confirmation" in delta_types:
        return "重複出現", "repeated"
    if metric_count > 0 and delta_types & {"launch_or_release", "new_amount_or_metric"}:
        return "已驗證", "validated"
    return "萌芽", "seed"


def _next_check_at(event: Event) -> str:
    raw = event.last_seen_at or event.first_seen_at
    try:
        observed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        observed = datetime.now(timezone.utc)
    return (observed + timedelta(days=7)).isoformat(timespec="seconds")
