# Web Architecture (PR E)

```
Validated RadarReportV2 → Web Read Models → Immutable Artifacts → Astro Static Site
```

## Projection (`radar/web/projection.py`)

Pure and deterministic. `project_web(reports, contract, generated_at)` produces typed `WebArtifactV1`
values (path, media_type, content_hash, content). Only validated reports are projected.

Artifact layout under `artifacts/web/v1/`:

```
manifest.json
latest.json
reports/YYYY/YYYY-MM-DD/summary.json
reports/YYYY/YYYY-MM-DD/full.<content-hash>.json
indexes/reports/YYYY.json
indexes/domains/<domain>/YYYY.json
indexes/taiwan/YYYY.json
indexes/trends/<indicator_id>.json
meta/{runtime-contract,report-schema,web-schema}.json
```

## Typed web contracts (`radar/contracts/web_projection.py`)

`WebManifestV1`, `ReportSummaryV1`, `ReportIndexEntryV1`, `ReportsYearIndexV1`, `DomainIndexV1`,
`TaiwanIndexV1`, `TaiwanIndexEntryV1`, `TrendSeriesV1`, `TrendPointV1` — all strict, provider-neutral
pydantic models. `schemas/web.schema.json` is generated from them (drift-tested), and
`web/src/generated/web-types.ts` is generated from that schema (`npm run types:check`).

## Export (`radar/web/export.py`)

`radar export-web --database <db> [--latest] | --input <report.json> | --reports-dir <dir> [--full-rebuild]`.

- Atomic: stage-then-replace. Every changed artifact is written to a temp file first; only after all
  stages succeed are they moved into place. A failed export leaves no half-written artifacts and cleans
  up temporaries.
- Content-addressed + deterministic JSON.
- Incremental: unchanged artifacts (by content hash) are skipped; indexes are rebuilt per year.

## Astro site (`web/`)

Astro, TypeScript strict, static output, native CSS, zero-JS-first, GitHub Pages compatible (site/base
from env, never hardcoded). Pages: `/`, `/reports/[date]`, `/domains/[domain]`, `/trends`, `/retail`,
`/crypto`, `/taiwan`, `/history/[page]`.

Fact / Inference / Counterevidence / Uncertainty / Gap and Deterministic / API-assisted / Chat-assisted /
Fixture / Complete / Partial / Failed are shown as text + symbol badges, never colour alone. The homepage
never loads full history; history is paginated (30/page); trends use inline SVG sparklines; empty
structural windows render `insufficient`, never a fabricated trend.

## Performance budget

Initial JS < 60 KB gzip (zero-JS-first — no client framework), CSS < 40 KB, homepage JSON < 100 KB,
first page does not load all history, static content is not hydrated, 1,000 reports do not incur O(n²)
work (per-year indexes + paginated history).
