# Event Intelligence Runtime v2 Architecture

`daily-market-radar` v2 is a modular monolith. The dependency direction is:

```text
domain/types -> config/schemas -> repositories -> adapters -> pipeline/services -> reporting/runtime
```

The runtime keeps the `brain-core` child-mount governance files in place, but the
active intelligence contract now lives in executable code and canonical config:

- `config/source_registry.yaml` is the source registry.
- `FRESHRSS_SEEDS.opml` is a generated projection from the registry.
- `src/radar/` owns ingestion, deduplication, event clustering, coverage, report
  contracts, run records, and fixture replay.
- `schemas/` exposes stable JSON-schema contracts for source, document, event,
  signal, coverage, and report payloads.
- `migrations/0001_runtime_foundation.sql` defines the initial durable tables.

LLM usage is intentionally outside the deterministic core. LLMs may perform
semantic extraction, fuzzy event matching at threshold boundaries, summaries, and
trend mapping. Fetching, URL safety, source identity, item counting, coverage
gates, evidence trace checks, and report contract validation stay in code.
