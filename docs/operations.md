# Operations

## Local validation

```bash
make validate
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli sources health
```

`Makefile` defaults to `python3`. Override with `PYTHON=/path/to/python3` when needed.

## Fixture run

```bash
PYTHONPATH=src python -m radar.cli run-daily \
  --mode fixture \
  --profile daily_push \
  --date 2026-07-10
```

Fixture mode validates deterministic contracts only. It is always partial for real-world news completeness.

## Live RSS run

```bash
PYTHONPATH=src python -m radar.cli run-daily \
  --mode live-rss \
  --profile daily_push \
  --date 2026-07-10 \
  --timeout-seconds 12 \
  --per-feed-limit 20 \
  --database <database-path>
```

`live-rss` executes enabled RSS/Atom adapters in `config/source_registry.json`. It does not execute web, API, social, FreshRSS or external-discovery adapters. Unavailable integrations are exposed through the generic `source_audit.integration_status` and `source_audit.remaining_gaps` fields and keep the run partial when material.

## Daily order

```text
source health
→ top-down ingest
→ bottom-up ingest
→ external gap discovery
→ normalize and URL safety
→ document de-duplication
→ event clustering
→ historical material-delta check
→ evidence verification
→ importance / potential / confidence scoring
→ coverage cells
→ report plan and slot caps
→ report contract validation
→ optional persistence
→ post-run backtest
```

Some stages are not yet connected in the live RSS path. Never hide an unexecuted stage.

## SQLite records

When `--database` is supplied, the runtime initializes migrations and stores:

```text
fetch_runs
documents
document_payloads
events
event_documents
event_deltas
reports
report_payloads
coverage_gaps
indicator_observations
state_entries
```

Local database files under `data/` are ignored by Git.

## RSS stack

Image references are pinned through `infra/rss-stack/.env.example`. Before changing a tag or digest:

```bash
cd infra/rss-stack
docker compose pull
docker compose up -d
docker compose ps
curl -f http://localhost:1200/healthz
curl -I http://localhost:8080
```

FreshRSS availability does not prove source or evidence coverage. Record validation under `reports/execution_checks/`.

## Failure behavior

```text
feed fetch failure → coverage gap
empty source → empty/silent gap, not no-news
invalid report contract → failed run
fixture mode → partial
unexecuted adapter family → degradation reason
```

## Daily automation (PR F)

```text
Workflows: runtime-check, web-check, daily-intelligence, prepare-chat, import-chat, pages-deploy, mount-check.
Schedule: daily-intelligence cron '0 23 * * *' UTC == 07:00 Asia/Taipei, deployed before 09:00 TW.
Mode: RADAR_EVALUATION_MODE (default auto). No secrets → deterministic, site + Pages still produced.
Durable state: radar-state branch (compressed + checksummed SQLite, last-good backup, atomic, concurrency lock,
  corruption rollback). See docs/state-persistence.md.
Pages: deploy only validated site artifact; failed report not deployed; fixture is preview-only; base from env.
Secrets: all optional; redaction scrubs credentials from logs. See docs/secrets.md.
```
