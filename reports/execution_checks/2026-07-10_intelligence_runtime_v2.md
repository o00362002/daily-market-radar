# intelligence_runtime_v2 execution check

Date: 2026-07-10
Branch: `refactor-intelligence-runtime-v2`

## Baseline

Commands run before implementation:

```text
bash check_mount_integrity.sh
git status --short
git ls-files
```

Baseline findings:

```text
FAIL AGENTS.md exceeded 4500 byte budget.
FAIL workflows/daily_radar_workflow.md referenced missing path data/policy/statistics.
Tracked local-only files included infra/rss-stack/.env and .DS_Store files.
Docker Compose used latest image tags.
```

## Red / Green Evidence

Red test:

```text
PYTHONPATH=src ...python3 -m unittest discover -s tests/unit -p 'test_*.py'
FAILED with ModuleNotFoundError: No module named 'radar'
```

Green test:

```text
PYTHONPATH=src ...python3 -m unittest discover -s tests -p 'test_*.py'
Ran 21 tests OK
```

Final verification:

```text
make validate
  unit: 15 tests OK
  integration: 3 tests OK
  contracts: 3 tests OK
  source registry OPML drift: OK
  radar CLI source validation and run-daily smoke: OK
  doc-path/core/domain-pack/sync-matrix checks: OK

git diff --check
  OK

bash check_mount_integrity.sh
  Result: complete
```

## Implemented

```text
src/radar deterministic runtime foundation
config/source_registry.yaml canonical source registry
FRESHRSS_SEEDS.opml drift contract
schemas/ JSON-schema stubs
migrations/0001_runtime_foundation.sql
Makefile validate entrypoint
docs/architecture.md
docs/methodology.md
docs/operations.md
docs/source-policy.md
docs/migration-v1-to-v2.md
archive/v1-spec/README.md
```

## Safety Changes

```text
infra/rss-stack/.env removed from Git tracking; .env ignored.
tracked .DS_Store files removed.
Docker Compose image references no longer use latest.
AGENTS.md budget repaired.
workflows/daily_radar_workflow.md path wording repaired.
active fixed-count quota wording replaced by v2 slot cap + coverage gate wording.
```

## Known Limits

```text
Live network ingestion is not enabled in CI.
pytest/ruff/mypy were not installed in this local environment; repo-local dev dependency install was attempted and blocked by sandbox DNS, then by platform usage-limit review for escalated network install.
Docker image tags require owner production validation before use.
External credential rotation, if needed, must be done by the owner outside this repo.
```
