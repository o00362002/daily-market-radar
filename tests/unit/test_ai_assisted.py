from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from radar.contracts.evaluation import EvaluationRequest
from radar.contracts.runtime import RuntimeContract
from radar.domain.models import Document
from radar.evaluators.ai_assisted import AiAssistedEvaluator
from radar.evaluators.ai_provider import AiProposalItem, AiProposalRequest, AiProposalResult, AiUsage
from radar.evaluators.cache import CostBudget, InMemoryEvaluationCache
from radar.evaluators.deterministic import DeterministicIntelligenceEvaluator
from radar.pipeline.cluster import cluster_documents

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 7, 10, 1, 30, tzinfo=timezone.utc)


class MockProvider:
    provider_id = "mock"
    model = "mock-model"

    def __init__(self, builder, *, raises: bool = False) -> None:
        self._builder = builder
        self._raises = raises
        self.calls = 0

    def propose(self, request: AiProposalRequest) -> AiProposalResult:
        self.calls += 1
        if self._raises:
            raise RuntimeError("provider exploded")
        return self._builder(request)


def _events():
    docs = [
        Document.fixture(source_id="openai_news", url="https://openai.com/a", title="Lab launches agent runtime", entities=["Lab"], action="launches", object="runtime", location="US", lane="top_down"),
        Document.fixture(source_id="twse", url="https://twse.com.tw/b", title="TWSE reports ETF flows", entities=["TWSE"], action="reports", object="ETF flows", location="Taiwan", macro_region="Taiwan", lane="top_down", facts={"flow_usd_m": 200}),
    ]
    return cluster_documents(docs)


def _request(mode: str) -> EvaluationRequest:
    contract = RuntimeContract.from_file(ROOT / "config/runtime_contract.json")
    return EvaluationRequest(
        date="2026-07-10",
        profile="daily_push",
        requested_mode=mode,
        events=tuple(_events()),
        contract=contract,
        started_at=NOW.isoformat(),
    )


def _valid_builder(request: AiProposalRequest) -> AiProposalResult:
    # Realistic provider output: zh-Hant narrative fields (the system prompt
    # mandates Traditional Chinese, and validate_ai_proposal now guards it).
    items = tuple(
        AiProposalItem(
            event_id=event.event_id,
            headline=f"[AI] 繁中標題：{event.summary}",
            today_delta="今日新增：官方正式發布並附具體數據。",
            taiwan_implication="暫無台灣直接證據；影響屬推論。",
            next_watch="觀察獨立來源跟進與採用擴散。",
            rationale="依據 bounded context 的官方證據。",
            importance_delta=5,
        )
        for event in request.events
    )
    return AiProposalResult(items=items, usage=AiUsage(input_tokens=100, output_tokens=50, estimated_cost_usd=0.001))


class AiAssistedEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.deterministic = DeterministicIntelligenceEvaluator(lambda: NOW)

    def test_no_provider_falls_back_to_deterministic(self) -> None:
        evaluator = AiAssistedEvaluator(self.deterministic, None, clock=lambda: NOW)
        result = evaluator.evaluate(_request("auto"))
        self.assertEqual(result.audit.effective_mode, "deterministic")
        self.assertIn("ai_evaluation_unavailable", result.audit.degradation_reasons)

    def test_valid_proposal_enhances_items(self) -> None:
        provider = MockProvider(_valid_builder)
        evaluator = AiAssistedEvaluator(self.deterministic, provider, clock=lambda: NOW, effective_mode="api-assisted")
        result = evaluator.evaluate(_request("api-assisted"))
        self.assertEqual(result.audit.effective_mode, "api-assisted")
        self.assertEqual(result.audit.provider, "mock")
        self.assertTrue(any(item.headline.startswith("[AI]") for item in result.items))
        # Translated narrative fields flow through to the report items (and thus the live page).
        self.assertTrue(any(item.today_delta == "今日新增：官方正式發布並附具體數據。" for item in result.items))
        self.assertTrue(any("暫無台灣直接證據" in item.taiwan_implication for item in result.items))
        self.assertTrue(all(0 <= item.importance_score <= 100 for item in result.items))
        self.assertEqual(provider.calls, 1)

    def test_invalid_event_id_retries_once_then_falls_back(self) -> None:
        def bad(request: AiProposalRequest) -> AiProposalResult:
            return AiProposalResult(items=(AiProposalItem(event_id="evt_invented", headline="hi"),))

        provider = MockProvider(bad)
        evaluator = AiAssistedEvaluator(self.deterministic, provider, clock=lambda: NOW)
        result = evaluator.evaluate(_request("api-assisted"))
        self.assertEqual(provider.calls, 2)  # initial + one retry
        self.assertEqual(result.audit.effective_mode, "deterministic")
        self.assertIn("ai_output_invalid", result.audit.degradation_reasons)

    def test_provider_error_does_not_crash(self) -> None:
        provider = MockProvider(_valid_builder, raises=True)
        evaluator = AiAssistedEvaluator(self.deterministic, provider, clock=lambda: NOW)
        result = evaluator.evaluate(_request("auto"))
        self.assertEqual(result.audit.effective_mode, "deterministic")
        self.assertIn("ai_provider_error", result.audit.degradation_reasons)

    def test_budget_exhaustion_skips_ai(self) -> None:
        provider = MockProvider(_valid_builder)
        budget = CostBudget(max_items_per_run=1)
        budget.charge(cost=0.0, items=1, input_tokens=0)  # already at the item cap
        evaluator = AiAssistedEvaluator(self.deterministic, provider, clock=lambda: NOW, budget=budget)
        result = evaluator.evaluate(_request("auto"))
        self.assertEqual(result.audit.effective_mode, "deterministic")
        self.assertIn("ai_budget_exhausted", result.audit.degradation_reasons)
        self.assertEqual(provider.calls, 0)

    def test_cache_hit_avoids_second_provider_call(self) -> None:
        provider = MockProvider(_valid_builder)
        cache = InMemoryEvaluationCache()
        evaluator = AiAssistedEvaluator(self.deterministic, provider, clock=lambda: NOW, cache=cache)
        first = evaluator.evaluate(_request("auto"))
        second = evaluator.evaluate(_request("auto"))
        self.assertEqual(provider.calls, 1)  # second run served from cache
        self.assertEqual(second.audit.cache_hits, 1)
        self.assertEqual(first.audit.effective_mode, "auto")


if __name__ == "__main__":
    unittest.main()
