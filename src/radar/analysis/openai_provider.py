from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from radar.contracts.analysis import (
    AIAnalysisV1,
    AnalysisFindingV1,
    AnalysisProvenanceV1,
    FutureTrendV1,
    LinkedIndicatorV1,
    TranslationV1,
)
from radar.contracts.report import RadarReportV2


class _ProposalModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TranslationProposal(_ProposalModel):
    event_id: str
    translated_text: str


class FindingProposal(_ProposalModel):
    domain: str
    label: Literal["verified_fact", "ai_inference", "background", "hypothesis", "uncertainty"]
    title: str
    summary: str
    source_event_ids: list[str]
    confidence: int = Field(ge=0, le=100)


class TrendProposal(_ProposalModel):
    title: str
    stage: Literal["emerging", "forming", "established", "uncertain"]
    horizon: Literal["days", "weeks", "months", "years", "three_to_six_months"]
    horizon_months: list[int] = Field(default_factory=lambda: [3, 6], min_length=2)
    synthesis_scope: Literal["global"] = "global"
    source_domain_ids: list[str] = Field(default_factory=list)
    direction: Literal["up", "flat", "down", "mixed", "uncertain"]
    summary: str
    source_event_ids: list[str]
    counterevidence: list[str]
    uncertainties: list[str]
    next_watch: list[str]
    confidence: int = Field(ge=0, le=100)


class IndicatorInterpretationProposal(_ProposalModel):
    indicator_id: str
    interpretation: str


class AiAnalysisProposal(_ProposalModel):
    executive_summary: list[str]
    translations: list[TranslationProposal]
    key_findings: list[FindingProposal]
    future_trends: list[TrendProposal]
    indicator_interpretations: list[IndicatorInterpretationProposal]
    limitations: list[str]


@dataclass(frozen=True)
class OpenAiAnalysisProvider:
    api_key: str
    model: str
    provider_id: str = "openai"

    def enhance(
        self,
        report: RadarReportV2,
        baseline: AIAnalysisV1,
        config: dict[str, object],
    ) -> AIAnalysisV1:
        client = self._client()
        response = client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(_bounded_payload(report, baseline, config), ensure_ascii=False),
                },
            ],
            text_format=AiAnalysisProposal,
        )
        proposal = response.output_parsed
        if proposal is None:
            raise ValueError("OpenAI analysis response did not contain parsed output")
        return _merge_proposal(report, baseline, proposal, self.provider_id, self.model, config)

    def _client(self):  # pragma: no cover - requires OpenAI SDK + network + real key
        from openai import OpenAI

        return OpenAI(api_key=self.api_key)


def _bounded_payload(
    report: RadarReportV2,
    baseline: AIAnalysisV1,
    config: dict[str, object],
) -> dict[str, object]:
    return {
        "date": report.date,
        "output_language": "zh-Hant-TW",
        "limits": {
            "max_summary_points": int(config.get("max_summary_points", 6)),
            "max_findings": int(config.get("max_findings", 8)),
            "max_trends": int(config.get("max_trends", 6)),
        },
        "canonical_domains": list(config.get("_canonical_report_domains", [])),
        "events": [
            {
                "event_id": item.event_id,
                "domain": item.primary_domain,
                "lane": item.report_lane,
                "original_headline": _original_text(baseline, item.event_id),
                "current_headline": item.headline,
                "today_delta": item.today_delta,
                "importance_score": item.importance_score,
                "potential_score": item.potential_score,
                "confidence_score": item.confidence_score,
                "counterevidence": item.counterevidence,
                "uncertainties": item.uncertainties,
                "next_watch": item.next_watch,
                "source_ids": sorted({link.source_id for link in item.evidence_links}),
            }
            for item in report.items
        ],
        "retail_matrix": {
            key: {
                "status": cell.status,
                "signal_ids": cell.signal_ids,
                "data_checked": cell.data_checked,
                "gap": cell.gap,
            }
            for key, cell in report.retail_matrix.items()
        },
        "crypto_matrix": {
            key: {
                "status": cell.status,
                "signal_ids": cell.signal_ids,
                "data_checked": cell.data_checked,
                "gap": cell.gap,
            }
            for key, cell in report.crypto_matrix.items()
        },
        "structural_indicators": [row.model_dump(mode="json") for row in baseline.structural_indicators],
        "auxiliary_signal_indicators": [row.model_dump(mode="json") for row in baseline.linked_indicators],
        "coverage_gaps": [gap.model_dump(mode="json") for gap in report.coverage_gaps],
    }


def _original_text(baseline: AIAnalysisV1, event_id: str) -> str:
    for row in baseline.translations:
        if row.event_id == event_id:
            return row.original_text
    return ""


def _merge_proposal(
    report: RadarReportV2,
    baseline: AIAnalysisV1,
    proposal: AiAnalysisProposal,
    provider: str,
    model: str,
    config: dict[str, object],
) -> AIAnalysisV1:
    allowed_events = {item.event_id for item in report.items}
    allowed_indicators = {row.indicator_id for row in baseline.linked_indicators}
    allowed_domains = {str(domain) for domain in config.get("_canonical_report_domains", [])}
    max_summary = int(config.get("max_summary_points", 6))
    max_findings = int(config.get("max_findings", 8))
    max_trends = int(config.get("max_trends", 6))

    _validate_text_language(proposal)
    _validate_references(proposal, allowed_events, allowed_indicators, allowed_domains)

    translation_map = {row.event_id: row.translated_text.strip() for row in proposal.translations}
    translations = [
        TranslationV1(
            event_id=row.event_id,
            original_text=row.original_text,
            translated_text=translation_map.get(row.event_id, row.translated_text),
            original_language=row.original_language,
        )
        for row in baseline.translations
    ]

    findings: list[AnalysisFindingV1] = []
    for row in proposal.key_findings[:max_findings]:
        source_ids = sorted(set(row.source_event_ids))
        raw = f"{row.label}|{row.title}|{'|'.join(source_ids)}"
        findings.append(
            AnalysisFindingV1(
                finding_id="finding_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12],
                domain=row.domain,
                label=row.label,
                title=row.title.strip(),
                summary=row.summary.strip(),
                source_event_ids=source_ids,
                confidence=row.confidence,
            )
        )

    trends: list[FutureTrendV1] = []
    for row in proposal.future_trends[:max_trends]:
        source_ids = sorted(set(row.source_event_ids))
        raw = f"{row.title}|{'|'.join(source_ids)}"
        trends.append(
            FutureTrendV1(
                trend_id="trend_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12],
                title=row.title.strip(),
                stage=row.stage,
                horizon=row.horizon,
                horizon_months=list(row.horizon_months),
                synthesis_scope=row.synthesis_scope,
                source_domain_ids=sorted(set(row.source_domain_ids)),
                direction=row.direction,
                summary=row.summary.strip(),
                source_event_ids=source_ids,
                counterevidence=[text.strip() for text in row.counterevidence if text.strip()],
                uncertainties=[text.strip() for text in row.uncertainties if text.strip()],
                next_watch=[text.strip() for text in row.next_watch if text.strip()],
                confidence=row.confidence,
            )
        )

    interpretation_map = {row.indicator_id: row.interpretation.strip() for row in proposal.indicator_interpretations}
    indicators = [
        LinkedIndicatorV1(
            **{
                **row.model_dump(mode="python"),
                "interpretation": interpretation_map.get(row.indicator_id, row.interpretation),
            }
        )
        for row in baseline.linked_indicators
    ]

    provenance = AnalysisProvenanceV1(
        provider=provider,
        model=model,
        generated_at=baseline.provenance.generated_at,
        source_report_date=baseline.provenance.source_report_date,
        source_run_id=baseline.provenance.source_run_id,
        source_context_hash=baseline.provenance.source_context_hash,
        prompt_version=baseline.provenance.prompt_version,
        schema_version="ai-analysis/v1",
        requested_mode=baseline.provenance.requested_mode,
        effective_mode="api-assisted",
        validation_status="valid",
        fallback_used=False,
    )
    return AIAnalysisV1(
        analysis_id=AIAnalysisV1.analysis_id_for(
            source_context_hash=baseline.provenance.source_context_hash,
            effective_mode="api-assisted",
            model=model,
        ),
        date=baseline.date,
        source_report_id=baseline.source_report_id,
        executive_summary=[text.strip() for text in proposal.executive_summary[:max_summary] if text.strip()],
        translations=translations,
        key_findings=findings or baseline.key_findings,
        future_trends=trends or baseline.future_trends,
        structural_indicators=baseline.structural_indicators,
        linked_indicators=indicators,
        limitations=_deduplicate([*baseline.limitations, *proposal.limitations]),
        provenance=provenance,
    )


def _validate_references(
    proposal: AiAnalysisProposal,
    allowed_events: set[str],
    allowed_indicators: set[str],
    allowed_domains: set[str],
) -> None:
    for row in proposal.translations:
        if row.event_id not in allowed_events:
            raise ValueError(f"unknown translation event_id: {row.event_id}")
    for row in proposal.key_findings:
        if row.domain not in allowed_domains:
            raise ValueError(f"unknown finding domain: {row.domain}")
        if not row.source_event_ids:
            raise ValueError("analysis rows require at least one source_event_id")
        unknown = set(row.source_event_ids) - allowed_events
        if unknown:
            raise ValueError(f"unknown analysis event ids: {sorted(unknown)}")
    for row in proposal.future_trends:
        if not row.source_event_ids:
            raise ValueError("analysis rows require at least one source_event_id")
        unknown = set(row.source_event_ids) - allowed_events
        if unknown:
            raise ValueError(f"unknown analysis event ids: {sorted(unknown)}")
        if row.horizon != "three_to_six_months" or sorted(set(row.horizon_months)) != [3, 6]:
            raise ValueError("future trends must use the 3-to-6-month horizon")
        if row.synthesis_scope != "global":
            raise ValueError("future trends must be global syntheses")
        unknown_domains = set(row.source_domain_ids) - allowed_domains
        if unknown_domains:
            raise ValueError(f"unknown future trend domains: {sorted(unknown_domains)}")
        if len(allowed_events) > 1 and len(set(row.source_event_ids)) < 2:
            raise ValueError("future trends must synthesize multiple source events")
        if len(allowed_events) > 1 and len(set(row.source_domain_ids)) < 2:
            raise ValueError("future trends must synthesize multiple source domains")
    unknown_indicators = {row.indicator_id for row in proposal.indicator_interpretations} - allowed_indicators
    if unknown_indicators:
        raise ValueError(f"unknown indicator ids: {sorted(unknown_indicators)}")


def _validate_text_language(proposal: AiAnalysisProposal) -> None:
    texts: list[str] = [*proposal.executive_summary, *proposal.limitations]
    texts.extend(row.translated_text for row in proposal.translations)
    texts.extend(row.title for row in proposal.key_findings)
    texts.extend(row.summary for row in proposal.key_findings)
    texts.extend(row.title for row in proposal.future_trends)
    texts.extend(row.summary for row in proposal.future_trends)
    texts.extend(row.interpretation for row in proposal.indicator_interpretations)
    for text in texts:
        if len(text.strip()) >= 8 and not re.search(r"[\u3400-\u9fff]", text):
            raise ValueError("AI analysis natural-language output must use Traditional Chinese")


def _deduplicate(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = value.strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


_SYSTEM_PROMPT = """
你是全球情報雷達的受約束分析與翻譯層，不是事實判官。只可使用輸入 JSON 內已驗證的事件、矩陣、
三個核心結構指標與輔助訊號指標。所有自然語言輸出使用台灣繁體中文。公司名、產品名、日期、數字與專有名詞
必須忠實保留，不得新增輸入中不存在的數字、URL、event_id、source_id 或因果關係。

任務：
1. 忠實翻譯非中文標題，保留原意，不進行新聞改寫。
2. 今日統整要回答「今天世界的大方向是什麼」，要跨事件整合，不要只複述最高分新聞。
3. key_findings 必須使用輸入中的五個 canonical_domains；每筆只能有一個 domain，並只保留符合本專案目標的判讀。
4. 未來趨勢必須是跨事件、跨領域的全球情境統整，固定使用 horizon=three_to_six_months、horizon_months=[3,6]、synthesis_scope=global；
   不得把每則新聞各自改寫成一個趨勢。每個趨勢在有多個事件時至少引用兩個 source_event_ids，並包含反證、不確定性與下一個驗證點。
5. structural_indicators 是 RadarReportV2 的三個核心長期結構方向，全部欄位唯讀，不得改寫、刪除或自創；
   每個核心指標要依 components 的細分指標與 evidence 先解讀，再保留 deterministic 的總分。
6. auxiliary_signal_indicators 的 score、previous_score、delta、direction、status、method 與 components 皆唯讀；
   只能為既有 indicator_id 產生 interpretation，不得改分數或自創指標。
7. verified_fact 只能重述 today_delta 或輸入中的直接事實；跨事件關聯使用 ai_inference；
   尚待驗證的走向使用 hypothesis 或 uncertainty。
8. 資料不足就明確列入 limitations，不得用常識或外部知識補洞。
""".strip()
