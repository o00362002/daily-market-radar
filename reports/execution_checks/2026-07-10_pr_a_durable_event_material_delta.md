# PR A durable event material delta

Date: 2026-07-10
Branch: `feat/durable-event-material-delta`
Base: `main` at `9c1c19d` (`Merge pull request #7 from o00362002/codex/modularity-replaceability-gate`)

## Scope completed

- Added SQLite durable runtime storage for documents, event-document links, event deltas, reports,
  structural-indicator observations and state checkpoints.
- Added migration `migrations/0003_durable_runtime_repositories.sql`.
- Added 30-day cross-day event reconciliation and deterministic material-delta filtering.
- Added deterministic score explanations for importance, potential and confidence in `RadarReportV2`.
- Kept the PR #7 architecture boundary: application code depends on ports/contracts/domain/pure pipeline,
  while SQLite remains selected only by the composition root.

## Verification

```text
make validate
unit: 31
integration: 18
contracts: 15
architecture: 4
runtime contract: pass
source registry and OPML projection: pass
CLI fixture smoke: pass
doc paths: FAIL=0
core: FAIL=0 WARN=0
domain packs: FAIL=0
sync matrix: complete

bash check_mount_integrity.sh: complete
PYTHONPYCACHEPREFIX=/tmp/daily-market-radar-pyc PYTHONPATH=src python3 -m compileall -q src/radar tests: pass
git diff --check: pass
PYTHONPYCACHEPREFIX=/tmp/daily-market-radar-pyc PYTHONPATH=src python3 -m radar.cli run-daily --mode fixture --date 2026-07-10 --database /tmp/daily-market-radar-pr-a.sqlite: pass
```

## Not done in this PR

- FreshRSS, safe web, generic JSON API and GDELT adapters.
- OpenAI structured evaluator, chat-assisted import/export and mode routing.
- Filesystem web artifacts, versioned projection, Astro dashboard, scheduler and GitHub Pages.

## Impact

- `--database` now persists the deterministic runtime state needed by later PRs instead of only report
  payloads and coverage gaps.
- Replayed events without a fresh material delta are not passed to the evaluator as reportable items.
- Report items now carry provider-neutral score component explanations.

## Manual verification path

Run:

```bash
PYTHONPYCACHEPREFIX=/tmp/daily-market-radar-pyc make validate
PYTHONPYCACHEPREFIX=/tmp/daily-market-radar-pyc PYTHONPATH=src python3 -m radar.cli run-daily --mode fixture --date 2026-07-10 --database /tmp/daily-market-radar-pr-a.sqlite
```
