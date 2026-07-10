"""OpenAI structured-output evaluation provider.

Imports the OpenAI SDK lazily so deterministic mode never touches it. Sends only
the bounded, provider-neutral context and requests a strict JSON object; the
caller re-validates every field. This module is intentionally never exercised
with a real API key in tests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from radar.evaluators.ai_provider import (
    AiProposalItem,
    AiProposalRequest,
    AiProposalResult,
    AiUsage,
    MAX_SCORE_DELTA,
)

# Rough public pricing (USD per 1K tokens); only used for cost estimation/budgeting.
_PRICE_PER_1K = {"input": 0.005, "output": 0.015}


@dataclass
class OpenAiEvaluationProvider:
    provider_id: str = "openai"
    model: str = "gpt-4.1-mini"
    api_key: str = ""

    def propose(self, request: AiProposalRequest) -> AiProposalResult:
        client = self._client()
        response = client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(_request_payload(request), ensure_ascii=False)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", 0) or 0
        output_tokens = getattr(usage, "completion_tokens", 0) or 0
        return AiProposalResult(
            items=_parse_items(content),
            usage=AiUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost_usd=round(
                    input_tokens / 1000 * _PRICE_PER_1K["input"] + output_tokens / 1000 * _PRICE_PER_1K["output"], 6
                ),
            ),
        )

    def _client(self):  # pragma: no cover - requires the SDK + a real key
        from openai import OpenAI

        return OpenAI(api_key=self.api_key)


def _request_payload(request: AiProposalRequest) -> dict[str, object]:
    return {
        "date": request.date,
        "profile": request.profile,
        "events": [
            {
                "event_id": event.event_id,
                "primary_domain": event.primary_domain,
                "summary": event.summary,
                "delta_types": list(event.delta_types),
                "metric_ids": list(event.measurement_metric_ids),
                "evidence_snippets": list(event.evidence_snippets),
                "deterministic_scores": {
                    "importance": event.deterministic_importance,
                    "potential": event.deterministic_potential,
                    "confidence": event.deterministic_confidence,
                },
            }
            for event in request.events
        ],
    }


def _parse_items(content: str) -> tuple[AiProposalItem, ...]:
    payload = json.loads(content)
    rows = payload.get("items", []) if isinstance(payload, dict) else []
    items: list[AiProposalItem] = []
    for row in rows:
        items.append(
            AiProposalItem(
                event_id=str(row.get("event_id", "")),
                headline=str(row.get("headline", "")),
                rationale=str(row.get("rationale", "")),
                taiwan_implication=str(row.get("taiwan_implication", "")),
                next_watch=str(row.get("next_watch", "")),
                counterevidence=tuple(row.get("counterevidence", []) or ()),
                uncertainties=tuple(row.get("uncertainties", []) or ()),
                importance_delta=_clamp_delta(row.get("importance_delta", 0)),
                potential_delta=_clamp_delta(row.get("potential_delta", 0)),
                confidence_delta=_clamp_delta(row.get("confidence_delta", 0)),
            )
        )
    return tuple(items)


def _clamp_delta(value: object) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 0
    return max(-MAX_SCORE_DELTA, min(MAX_SCORE_DELTA, number))


_SYSTEM_PROMPT = (
    "You are a semantic assistant for an intelligence radar. Enhance headlines, rationale, "
    "counterevidence, uncertainties, Taiwan implication and next-watch text only. Never invent URLs, "
    "event ids, document ids, source ids or numeric facts. Score adjustments must be within +/-"
    f"{MAX_SCORE_DELTA}. Return a JSON object: {{\"items\": [{{\"event_id\": ..., ...}}]}}."
)
