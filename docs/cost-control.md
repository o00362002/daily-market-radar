# Cost Control & Evaluation Cache (PR D)

## Evaluation cache

`radar/evaluators/cache.py` keys AI evaluations on **event state + evidence hashes + material delta +
model + schema version + evaluator configuration** (`cache_key`). A hit reuses the stored proposal and
avoids a new provider call (`cache_hits` is recorded in `evaluation_audit`).

Each entry records: provider, model, input/output tokens, estimated cost, latency, retries, validation
result, input hash and output hash.

## Cost / budget

`CostBudget` enforces `OPENAI_MAX_DAILY_COST_USD`, `OPENAI_MAX_ITEMS_PER_RUN` and
`OPENAI_MAX_INPUT_TOKENS_PER_RUN`. Before each AI call the evaluator checks affordability; when the
budget is exhausted it **stops new AI calls, the deterministic flow continues, and the run reports
`degradation=ai_budget_exhausted`**. A zero limit means "unbounded" for that dimension.
