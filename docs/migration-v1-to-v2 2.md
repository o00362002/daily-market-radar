# Migration v1 to v2

## Preserved

- `brain-core` child-mount files and checks remain active.
- Historical reports, backtests, missed cases, and frozen history remain in place.
- Existing source-library seed files remain as compatibility references.

## Archived / Frozen

- Fixed-count completion language is frozen as v1 behavior.
- v1 source registry fragments are no longer canonical.
- v1 Markdown templates remain available but now point to slot caps and coverage
  gates rather than fixed-count completeness.

See `archive/v1-spec/README.md`.

## Replaced

- `config/source_registry.yaml` replaces split source identity across media,
  official/data, and channel feed files.
- `FRESHRSS_SEEDS.opml` is treated as a generated projection.
- `src/radar/` provides deterministic source validation, OPML drift checking,
  URL safety, dedup/event clustering, coverage gaps, report contracts, and fixture
  replay.
- `make validate` is the local validation entrypoint.

## Not Complete Yet

- Live RSS/http ingestion, SQLAlchemy/Alembic, PostgreSQL/pgvector, APScheduler,
  and provider integrations are scaffolded but not production connected.
- `pytest`, `ruff`, and `mypy` are declared in `pyproject.toml`; this local run
  used standard-library `unittest` because those tools were not installed in the
  provided environment.
- Docker image tags in `.env.example` must be validated by the owner before
  production use.
- Existing legacy source files have not all been regenerated from the canonical
  registry.

## External Credential Action

`infra/rss-stack/.env` was removed from Git tracking (historical path; path-ok) and `.gitignore` now blocks
future local env files. If any value from that file was ever used outside local
testing, the owner must rotate it in the external service. This migration does not
read or operate external credentials.
