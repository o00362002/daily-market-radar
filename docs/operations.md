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
  --evaluation-mode deterministic \
  --date 2026-07-10
```

Fixture mode validates deterministic contracts only. It is always partial for real-world news completeness.

## Direct RSS / Atom compatibility run

```bash
PYTHONPATH=src python -m radar.cli run-daily \
  --mode live-rss \
  --profile daily_push \
  --evaluation-mode deterministic \
  --date 2026-07-10 \
  --timeout-seconds 12 \
  --per-feed-limit 20 \
  --database data/radar.db
```

`live-rss` executes enabled RSS/Atom adapters in `config/source_registry.json` only.

## Connected live collection

```bash
PYTHONPATH=src python -m radar.cli run-daily \
  --mode live \
  --profile daily_push \
  --evaluation-mode auto \
  --date 2026-07-10 \
  --timeout-seconds 12 \
  --per-feed-limit 20 \
  --database data/radar.db
```

`live` executes:

```text
direct registry RSS / Atom
+ FreshRSS Google Reader reading-list inbox when credentials exist
→ canonical source-id mapping
→ merged SourceFetchResult
→ document de-duplication
→ event resolution and material delta
```

FreshRSS environment variables:

```text
FRESHRSS_BASE_URL
FRESHRSS_USERNAME
FRESHRSS_API_PASSWORD
```

Missing credentials are not fatal. Direct RSS still runs, while `source_audit.integration_status`, coverage gaps and degradation reasons record `credential_unavailable`. A FreshRSS item is accepted only when its `origin.streamId` maps to an enabled RSS adapter URL in `config/source_registry.json`; unknown streams remain explicit gaps instead of receiving invented source identities.

## Current adapter boundary

Connected to `run-daily --mode live`:

```text
RSS / Atom
FreshRSS reading-list inbox
```

Implemented as lower-level libraries but not generically executable from the current registry:

```text
Safe Web
Generic JSON API
GDELT discovery
public / official social channels
```

Reasons:

```text
web pages need source-specific list/detail extraction rules
API registry entries need real executable endpoint, item path, pagination and field mappings
GDELT requires bounded coverage queries plus original-publisher verification before evidence use
authenticated social platforms require owner credentials and platform-specific official API clients
```

Do not mark these families checked until their source-specific routes execute.

## Daily order

```text
source health
→ direct RSS / Atom collection
→ optional FreshRSS inbox collection
→ normalize and URL safety
→ document de-duplication
→ event clustering
→ historical material-delta check
→ evidence verification
→ importance / potential / confidence scoring
→ coverage cells
→ report planning
→ report contract validation
→ atomic persistence
→ web projection and deployment
```

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
one child adapter fails → other adapters continue
feed fetch failure → coverage gap
FreshRSS credentials missing → direct RSS continues, aggregator marked unavailable
FreshRSS unknown stream → item not assigned an invented source_id; mapping gap recorded
empty source → empty/silent gap, not no-news
invalid report contract → failed run
fixture mode → partial
unexecuted adapter family → degradation reason
```

## Daily automation

```text
Workflow: daily-intelligence
Schedule: cron '0 23 * * *' UTC == 07:00 Asia/Taipei
Mode: run-daily --mode live
Evaluation: RADAR_EVALUATION_MODE, default auto
Durable state: radar-state branch
Deployment: validated non-fixture Astro artifact only
```

Owner settings:

```text
Settings → Pages → Source = GitHub Actions
Settings → Actions → General → Workflow permissions = Read and write
```

Secrets are optional; see `docs/secrets.md`. Without any secret, direct RSS, deterministic evaluation, state, site build and deployment still run. FreshRSS and AI appear as unavailable rather than crashing the pipeline.
