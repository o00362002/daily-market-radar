# Evaluation Modes (PR D)

Four modes, resolved deterministically (`radar/evaluators/modes.py`). Default: **auto**.

```bash
radar run-daily --evaluation-mode deterministic
radar run-daily --evaluation-mode auto           # default
radar run-daily --evaluation-mode api-assisted
radar run-daily --evaluation-mode chat-assisted
```

| Mode | Behaviour |
|------|-----------|
| **deterministic** | Never imports or calls an AI provider. No `OPENAI_API_KEY` needed. Produces a valid report, web export and deploy. Insufficient where data is absent. |
| **auto** | With `OPENAI_API_KEY`: deterministic base → bounded API enhancement → deterministic revalidation. Without a key: deterministic fallback, `degradation=ai_evaluation_unavailable`, no crash. |
| **api-assisted** | Requires a key; uses OpenAI structured output. Without a key it degrades to deterministic. |
| **chat-assisted** | The run stays deterministic; a human runs `prepare-chat` → ChatGPT → `import-chat`. |

## API-assisted safety model

The model is a semantic assistant, never the judge of facts.

- It only ever receives a **bounded, provider-neutral context**: structured facts, summaries, evidence
  snippets, event history, deltas, deterministic scores and counterevidence candidates.
- It never receives secrets, full HTML, full articles, duplicate content or unrelated history.
- It may not invent URLs, event ids, document ids, source ids or numeric facts; score adjustments are
  bounded to ±15.
- **Every output is re-validated deterministically.** Invalid output → retry once → keep the
  deterministic result (`partial`, `degradation=ai_output_invalid`). Provider errors never crash the run.

Environment: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_MAX_DAILY_COST_USD`, `OPENAI_MAX_ITEMS_PER_RUN`,
`OPENAI_MAX_INPUT_TOKENS_PER_RUN`. See [cost-control.md](cost-control.md) and
[chat-assisted-workflow.md](chat-assisted-workflow.md).
