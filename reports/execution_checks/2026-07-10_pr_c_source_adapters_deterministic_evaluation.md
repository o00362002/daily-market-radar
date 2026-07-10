# PR C — Source Adapters and Deterministic Evaluation

Base branch: `feat/event-resolution-precision` (PR B) · Branch: `feat/source-adapters-deterministic-evaluation`

## 改了什麼 (What changed)

- **HttpTransport seam** (`adapters/transport.py`): every network adapter depends on the transport
  protocol, not urllib directly, so all adapters are unit-testable offline. Real transport enforces
  bounded size, SSRF policy on initial URL **and every redirect hop**, redirect cap, conditional requests.
- **Adapters** (all offline-testable): hardened RSS/Atom (`rss_client.py`, ETag/Last-Modified conditional
  fetch + deterministic backoff/jitter + per-feed retry isolation); FreshRSS Google Reader API
  (`freshrss.py`, credential-gated, unavailable without creds, never crashes); Safe Web (`safe_web.py`,
  registry allowlist + SSRF blocking + bounded excerpt + content hash); Generic JSON API (`json_api.py`,
  page + cursor pagination, bearer/query token, field mapping, missing-credential degradation); GDELT
  discovery (`gdelt_discovery.py`, discovery-only, resolves to original publisher/URL + verification
  status, never final evidence); Social direct channels (`social_channels.py`, public RSS/Atom/YouTube
  direct-checked; X/Meta/Threads/Instagram official-API interface unavailable without creds).
- **Durable source health**: pure deterministic state machine over 8 statuses
  (`domain/source_health.py`) + `SqliteSourceHealthRepository` (migration `0005_source_health.sql`).
- **Deterministic evaluators wired into the live pipeline**: `evaluators/matrices.py` produces
  feature-traced Retail/Crypto matrix cells and structural-indicator observations — `observed` only when
  a canonical metric or keyword trigger fires (trace in `data_checked`), else `insufficient`. No fixed
  production scores; no fabricated trend. `rolling_summary` aggregates current/7d/30d/90d from real
  observations only. Now used by `DeterministicIntelligenceEvaluator`.

## 機器檢查 (Machine checks — all green)

- `unittest discover tests`: **120 passed** (87 prior + 33 new across
  `test_source_adapters` / `test_source_health` / `test_deterministic_evaluators`).
- `make validate` green (check-core / domain-packs / sync-matrix / doc-paths; runtime-contract; CLI smoke; OPML).
- Architecture gates green (10 ports; application imports no concrete infrastructure; acyclic graphs).
- Fixture `run-daily` now emits feature-traced matrices (`observed` + `insufficient` mix); structural
  indicators stay `insufficient` on fixture text — no fabricated trend.

## 沒做什麼 (Out of scope / honest boundary)

- The deterministic evaluator upgrade is **wired into the live run pipeline**. The new source adapters
  and source-health repository are implemented and unit-tested as composable building blocks; composing
  them into a single multi-adapter collection stage inside `run-daily` (health-recording per source,
  registry-driven adapter selection) is a follow-up integration and is not claimed as wired here.
- No real API keys are used in tests; credential-gated adapters are exercised via the missing-credential
  (unavailable) and fake-transport paths only.

## 會影響誰 (Who is affected)

- Reports now carry real, feature-traced Retail/Crypto matrices and structural observations instead of
  uniform `insufficient`. Downstream PR E web projection renders these traces.

## 你可以驗證 (How to verify)

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=src python -m unittest tests.unit.test_source_adapters tests.unit.test_source_health tests.unit.test_deterministic_evaluators
make validate PYTHON=python
```
