# Migration v1 to v2

## Preserved

- `brain-core` child-mount governance remains active.
- Historical reports, backtests, missed cases and frozen history remain evidence.
- Legacy source files under `sources/` remain compatibility inputs until regenerated.

## Frozen v1 behavior

- Fixed-count completion rules such as `3+3`, `5+5`, `48-signal` and `60-signal` are historical only.
- Markdown templates no longer define machine completeness.
- Split source identity across media, official/data and channel files is no longer canonical.

See `archive/v1-spec/README.md`.

## Replaced by v2

- `config/runtime_contract.json` defines canonical report domains, profiles, slot caps, matrices and completion requirements.
- `config/source_registry.json` defines source identity and adapters.
- `FRESHRSS_SEEDS.opml` is a generated projection.
- `src/radar/` provides deterministic source validation, URL normalization, de-duplication, event clustering, lane separation, coverage gaps, report planning and contract validation.
- `schemas/report.schema.json` and the Python validator enforce report structure.
- `make validate` is the local validation entrypoint.

## Added in contract-sync repair

- Six canonical report domains with policy/geopolitics mapped into global markets/macro.
- Major and potential lanes with independent importance, potential and confidence scores.
- Retail, Crypto and Structural Trend panels in the executable report contract.
- Expanded Taiwan, official, research and niche source registry.
- Standard-library live RSS/Atom ingestion.
- Optional SQLite persistence for run records, report payloads and coverage gaps.
- Runtime-v2 sync-matrix edges.

## Added in durable runtime repair

- Optional SQLite persistence for canonical document payloads, event-document links, event delta history,
  structural-indicator observations and state checkpoints.
- Cross-day event matching by stable event identity over a 30-day lookback.
- Deterministic material-delta filtering so replayed events do not fill report slots.
- Deterministic score explanations for importance, potential and confidence components.

## Still incomplete

- Web, API, social and FreshRSS adapters.
- External discovery providers.
- AI-assisted semantic scoring, counterevidence extraction and structural-indicator evaluators.
- Production scheduler, PostgreSQL/pgvector and credential management.
- Regeneration of every legacy source projection from the canonical registry.

A `live-rss` run is real network collection for RSS/Atom adapters, but it remains partial whenever other required adapter families or coverage cells are unexecuted.

## External credential action

`infra/rss-stack/.env` remains outside Git (historical path; path-ok). Any credential that was previously used externally must be rotated by the owner; this migration does not read or operate external credentials.
