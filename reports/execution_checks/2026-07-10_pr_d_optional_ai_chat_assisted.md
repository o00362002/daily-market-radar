# PR D — Optional API and Chat-assisted Evaluation

Base branch: `feat/source-adapters-deterministic-evaluation` (PR C) · Branch: `feat/optional-ai-chat-assisted`

## 改了什麼 (What changed)

- **Four evaluation modes** (`evaluators/modes.py`), default `auto`, wired into `run-daily --evaluation-mode`:
  deterministic / auto / api-assisted / chat-assisted. Deterministic never imports or calls AI; auto
  and api-assisted degrade to deterministic without a key (`ai_evaluation_unavailable`, no crash).
- **AI provider port + safety model** (`evaluators/ai_provider.py`): the model sees only a bounded,
  provider-neutral context (structured facts, summaries, evidence snippets, event history, deltas,
  deterministic scores, counterevidence). Output is re-validated — it may not invent URLs / event /
  document / source ids / numeric facts; score deltas bounded to ±15.
- **AiAssistedEvaluator** (`evaluators/ai_assisted.py`): deterministic base → bounded enhancement →
  revalidate. Invalid output → retry once → keep deterministic result (`ai_output_invalid`). Provider
  error → deterministic fallback, never crashes.
- **Evaluation cache + cost/budget** (`evaluators/cache.py`): cache key over event state / evidence
  hashes / material delta / model / schema version / config; over budget →
  `ai_budget_exhausted`, deterministic continues.
- **OpenAI structured-output provider** (`adapters/openai_provider.py`), lazy-imported — never exercised
  with a real key in tests.
- **Chat-assisted** (`chat/context_package.py`, `chat/runtime.py`): `prepare-chat` writes a
  deterministic, content-addressed, byte-stable, secret-free package; `import-chat` re-validates a
  human report against it (context hash, contract, allowed ids/urls/facts, matrix keys, indicator ids,
  Taiwan direct-evidence rules, Major/Potential overlap). Failed import preserves the last valid report.

## 機器檢查 (Machine checks — all green)

- `unittest discover tests`: **142 passed** (22 new across `test_evaluation_modes`, `test_ai_assisted`,
  `test_chat_assisted`, `test_evaluation_pipeline`).
- `make validate` + architecture gates green. CLI verified end-to-end:
  `run-daily --evaluation-mode {deterministic,auto}` (auto no-key → deterministic + `ai_evaluation_unavailable`),
  `prepare-chat` (10-file package), `import-chat` (run_id guard rejects mismatched submission).
- Deterministic and auto-without-key runs never import `openai` (asserted).

## 沒做什麼 (Out of scope / honest boundary)

- No real API keys in tests; the OpenAI provider path (`_client`) is not executed in CI. API-assisted is
  proven via a mock provider.
- Full `.env.example` + `docs/secrets.md` + redaction tests land in PR F (secrets contract).

## 你可以驗證 (How to verify)

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=src OPENAI_API_KEY= python -m radar.cli run-daily --date 2026-07-10 --evaluation-mode auto | \
  python -c "import sys,json;print(json.load(sys.stdin)['evaluation_audit']['degradation_reasons'])"
PYTHONPATH=src python -m radar.cli prepare-chat --date 2026-07-10 --output-root /tmp/radar-chat
```
