"""Evaluation cache and cost/budget control for AI-assisted evaluation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from radar.domain.models import Event

SCHEMA_VERSION = "ai-eval/v1"


def cache_key(
    events: list[Event],
    *,
    model: str,
    evaluator_config: str,
) -> str:
    """Deterministic cache key over event state, evidence hashes, material delta,
    model, schema version and evaluator configuration."""

    payload = {
        "schema_version": SCHEMA_VERSION,
        "model": model,
        "evaluator_config": evaluator_config,
        "events": [
            {
                "event_id": event.event_id,
                "delta_types": sorted({delta.delta_type for delta in event.deltas}),
                "evidence_hashes": sorted(document.content_hash for document in event.documents),
            }
            for event in sorted(events, key=lambda event: event.event_id)
        ],
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "aieval:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True)
class EvaluationCacheEntry:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: int
    retries: int
    validation_status: str
    input_hash: str
    output_hash: str
    payload_json: str


class InMemoryEvaluationCache:
    def __init__(self) -> None:
        self.entries: dict[str, EvaluationCacheEntry] = {}
        self.hits = 0

    def get(self, key: str) -> EvaluationCacheEntry | None:
        entry = self.entries.get(key)
        if entry is not None:
            self.hits += 1
        return entry

    def put(self, key: str, entry: EvaluationCacheEntry) -> None:
        self.entries[key] = entry


@dataclass
class CostBudget:
    max_daily_cost_usd: float = 0.0
    max_items_per_run: int = 0
    max_input_tokens_per_run: int = 0
    spent_cost_usd: float = 0.0
    spent_items: int = 0
    spent_input_tokens: int = 0
    _exhausted: bool = field(default=False)

    @property
    def exhausted(self) -> bool:
        return self._exhausted or self._over_limit(0.0, 0, 0)

    def _over_limit(self, cost: float, items: int, tokens: int) -> bool:
        if self.max_daily_cost_usd and self.spent_cost_usd + cost > self.max_daily_cost_usd:
            return True
        if self.max_items_per_run and self.spent_items + items > self.max_items_per_run:
            return True
        if self.max_input_tokens_per_run and self.spent_input_tokens + tokens > self.max_input_tokens_per_run:
            return True
        return False

    def can_afford(self, *, cost: float, items: int, input_tokens: int) -> bool:
        return not self._over_limit(cost, items, input_tokens)

    def charge(self, *, cost: float, items: int, input_tokens: int) -> None:
        self.spent_cost_usd += cost
        self.spent_items += items
        self.spent_input_tokens += input_tokens
        if self._over_limit(0.0, 0, 0):
            self._exhausted = True
