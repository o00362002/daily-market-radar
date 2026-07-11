from __future__ import annotations

import json
import unittest

from radar.adapters.openai_provider import _SYSTEM_PROMPT, _parse_items, _request_payload
from radar.evaluators.ai_provider import (
    AiProposalItem,
    AiProposalRequest,
    AiProposalResult,
    AllowedFacts,
    BoundedEventContext,
    MAX_SCORE_DELTA,
    validate_ai_proposal,
)


def _context(event_id: str = "evt_1") -> BoundedEventContext:
    return BoundedEventContext(
        event_id=event_id,
        primary_domain="ai_agents_applications",
        summary="Lab launches agent runtime",
        delta_types=("new_event",),
        measurement_metric_ids=(),
        source_ids=("openai_news",),
        evidence_urls=("https://openai.com/a",),
        evidence_snippets=("Lab launches agent runtime",),
        deterministic_importance=60,
        deterministic_potential=50,
        deterministic_confidence=70,
        counterevidence_candidates=(),
        original_language="en",
        original_headline="Lab launches agent runtime",
    )


class SystemPromptContractTests(unittest.TestCase):
    """Lock the translation contract so prompt edits cannot silently drop it."""

    def test_prompt_mandates_zh_hant_and_today_delta(self) -> None:
        self.assertIn("zh-Hant-TW", _SYSTEM_PROMPT)
        self.assertIn("today_delta", _SYSTEM_PROMPT)
        self.assertIn("繁體中文", _SYSTEM_PROMPT)

    def test_prompt_restates_no_invention_and_score_bounds(self) -> None:
        self.assertIn("不得捏造", _SYSTEM_PROMPT)
        self.assertIn(str(MAX_SCORE_DELTA), _SYSTEM_PROMPT)

    def test_request_payload_carries_language_context(self) -> None:
        request = AiProposalRequest(date="2026-07-11", profile="daily_push", model="m", events=(_context(),))
        payload = _request_payload(request)
        self.assertEqual(payload["output_language"], "zh-Hant-TW")
        event = payload["events"][0]
        self.assertEqual(event["original_language"], "en")
        self.assertEqual(event["original_headline"], "Lab launches agent runtime")


class ParseItemsTests(unittest.TestCase):
    def test_parse_maps_all_fields_including_today_delta(self) -> None:
        content = json.dumps(
            {
                "items": [
                    {
                        "event_id": "evt_1",
                        "headline": "實驗室推出代理執行環境",
                        "today_delta": "今日新增：正式發布。",
                        "rationale": "官方來源",
                        "taiwan_implication": "暫無直接台灣證據",
                        "next_watch": "觀察採用",
                        "counterevidence": ["尚無獨立驗證"],
                        "uncertainties": ["規模未知"],
                        "importance_delta": 5,
                    }
                ]
            },
            ensure_ascii=False,
        )
        items = _parse_items(content)
        self.assertEqual(items[0].headline, "實驗室推出代理執行環境")
        self.assertEqual(items[0].today_delta, "今日新增：正式發布。")
        self.assertEqual(items[0].counterevidence, ("尚無獨立驗證",))
        self.assertEqual(items[0].importance_delta, 5)

    def test_parse_clamps_out_of_range_and_junk_deltas(self) -> None:
        content = json.dumps(
            {"items": [{"event_id": "e", "importance_delta": 99, "potential_delta": -99, "confidence_delta": "junk"}]}
        )
        item = _parse_items(content)[0]
        self.assertEqual(item.importance_delta, MAX_SCORE_DELTA)
        self.assertEqual(item.potential_delta, -MAX_SCORE_DELTA)
        self.assertEqual(item.confidence_delta, 0)


class LanguageGuardTests(unittest.TestCase):
    def _allowed(self) -> AllowedFacts:
        return AllowedFacts(
            event_ids=frozenset({"evt_1"}),
            source_ids=frozenset({"openai_news"}),
            urls=frozenset({"https://openai.com/a"}),
            numeric_facts=frozenset(),
        )

    def test_untranslated_prose_is_rejected(self) -> None:
        proposal = AiProposalResult(
            items=(AiProposalItem(event_id="evt_1", headline="Lab launches a brand new agent runtime today"),)
        )
        reasons = validate_ai_proposal(proposal, self._allowed())
        self.assertIn("non_zh_hant_output:headline", reasons)

    def test_translated_and_short_or_empty_fields_pass(self) -> None:
        proposal = AiProposalResult(
            items=(
                AiProposalItem(
                    event_id="evt_1",
                    headline="實驗室推出全新代理執行環境（agent runtime）",
                    today_delta="",  # no change proposed -> passes
                ),
            )
        )
        self.assertEqual(validate_ai_proposal(proposal, self._allowed()), [])


if __name__ == "__main__":
    unittest.main()
