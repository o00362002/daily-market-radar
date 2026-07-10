# web/ — Astro static dashboard (PR E)

Projection-first, zero-JS-first static site built from the immutable web artifacts under
`artifacts/web/v1/` (produced by `radar export-web`). No React SPA, no server framework, native CSS
only, 繁體中文為預設.

## Build

```bash
# 1. Produce artifacts (build input)
PYTHONPATH=../src python -m radar.cli run-daily --date $(date +%F) --database ../data/radar.db
PYTHONPATH=../src python -m radar.cli export-web --out-dir .. --database ../data/radar.db
# 2. Build the static site
cd web
npm ci
npm run types:check   # TS types must match schemas/web.schema.json
npm run build         # -> dist/
```

`RADAR_ARTIFACTS_DIR` overrides the artifact source (default `../artifacts/web/v1`). `PAGES_SITE` /
`PAGES_BASE` set the GitHub Pages origin + repository subpath (never hardcoded).

## Contracts

`src/generated/web-types.ts` is generated from `schemas/web.schema.json` via
`scripts/generate-types.mjs`; `npm run types:check` fails the build on drift.

## Design rules

- Fact / Inference / Counterevidence / Uncertainty / Gap and Deterministic / API-assisted /
  Chat-assisted / Fixture / Complete / Partial / Failed are shown as **text + symbol badges, never colour
  alone**.
- The homepage does not load all history; history is paginated (30/page). Trends use inline SVG
  sparklines. Empty structural windows render as `insufficient`, never a fabricated trend.
