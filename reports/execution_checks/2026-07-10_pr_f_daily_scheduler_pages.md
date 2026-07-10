# PR F — Scheduler, Durable State and Pages

Base branch: `feat/projection-first-dashboard` (PR E) · Branch: `feat/daily-scheduler-pages`

## 改了什麼 (What changed)

- **Six GitHub Actions workflows** (+ existing mount-check): `runtime-check` (unit/integration/contract/
  architecture + make validate + deterministic no-secret run + auto fallback), `web-check` (export →
  types:check → Astro build → bundle budgets), `daily-intelligence` (scheduled pipeline), `prepare-chat`
  (no API call, uploads package), `import-chat` (validate, deploy only if valid), `pages-deploy` (manual
  redeploy of the validated site).
- **Daily schedule**: `daily-intelligence` cron `0 23 * * *` UTC == 07:00 Asia/Taipei, deploying before
  09:00 TW (mapping documented). `RADAR_EVALUATION_MODE` (default auto). Concurrency lock `radar-daily`.
- **Durable state** (`radar/state/branch_store.py` + `radar state pack/verify/restore` CLI): the SQLite DB
  is compressed (deterministic gzip), checksummed, described by a `state/v1` manifest, and committed to the
  dedicated **`radar-state` branch (never main)**. Last-good backup rotation + retention + atomic write +
  corruption rollback.
- **Pages deploy**: deploys only the validated site artifact — never live data; failed reports are not
  deployed; fixture runs are preview-only; site base comes from env (no hardcoded hostname).
- **Secrets contract**: `.env.example`, `docs/secrets.md`, and secret **redaction** (`radar/observability/
  redaction.py`) that scrubs passwords, API keys, auth headers and DB credentials from logs. All secrets
  optional; with none, deterministic mode + site + Pages still work and unavailable integrations are
  disclosed.

## 機器檢查 (Machine checks — all green)

- `unittest discover tests`: **167 passed** (17 new: `test_state_branch` 4, `test_redaction` 7,
  `test_workflows` 6).
- `make validate` + architecture gates green. All 7 workflow YAML files parse. State CLI verified
  end-to-end (pack → verify → restore round-trip).

## 沒做什麼 / 邊界 (Boundary — owner UI setup required)

Workflows are pushed and parse-valid, but the owner must configure the following in the GitHub UI (code
cannot): Pages source = GitHub Actions; Actions read/write permissions (to push `radar-state`); optional
Secrets (`OPENAI_API_KEY`, `FRESHRSS_*`, `DATABASE_URL`); optional Variables (`RADAR_EVALUATION_MODE`,
`OPENAI_MODEL`, `OPENAI_MAX_*`). Live GitHub Actions execution / Pages deployment happen on GitHub, not in
this environment; the workflows are authored to standard, and their logic is unit-covered by `test_workflows`.

## 你可以驗證 (How to verify)

```bash
PYTHONPATH=src python -m unittest tests.unit.test_state_branch tests.unit.test_redaction tests.unit.test_workflows
PYTHONPATH=src python -m radar.cli state pack --database data/radar.db --state-root .state/state --run-id x
PYTHONPATH=src python -m radar.cli state restore --state-root .state/state --database /tmp/restored.db
```
