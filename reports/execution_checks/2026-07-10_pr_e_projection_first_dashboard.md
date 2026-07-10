# PR E — Projection-first Astro Dashboard

Base branch: `feat/optional-ai-chat-assisted` (PR D) · Branch: `feat/projection-first-dashboard`

## 改了什麼 (What changed)

- **Typed web read-model contracts** (`contracts/web_projection.py`): `WebManifestV1`, `ReportSummaryV1`,
  `ReportIndexEntryV1`, `ReportsYearIndexV1`, `DomainIndexV1`, `TaiwanIndexV1`, `TaiwanIndexEntryV1`,
  `TrendSeriesV1`, `TrendPointV1` — strict, provider-neutral. `schemas/web.schema.json` generated from
  them (drift-tested); `web/src/generated/web-types.ts` generated from the schema (`types:check`).
- **Deterministic projection** (`web/projection.py`): validated RadarReportV2 → immutable artifacts
  (manifest, latest, per-report summary + `full.<content-hash>.json`, per-year report/domain/taiwan
  indexes, per-indicator trend series, meta schemas). Content-addressed, canonical JSON, deterministic.
- **Atomic incremental export** (`web/export.py` + `web/runtime.py` + `export-web` CLI): stage-then-replace
  atomic writes, unchanged-artifact skip, incremental per-year indexes, and rollback that leaves no
  half-written artifacts. Flags: `--database/--latest`, `--input`, `--reports-dir`, `--full-rebuild`.
- **Astro static site** (`web/`): Astro + TS strict + static + native CSS, zero-JS-first, GitHub Pages
  compatible (site/base from env). Pages `/`, `/reports/[date]`, `/domains/[domain]`, `/trends`,
  `/retail`, `/crypto`, `/taiwan`, `/history/[page]`. Fact/Inference/Counterevidence/Uncertainty/Gap and
  Deterministic/API-assisted/Chat-assisted/Fixture/Complete/Partial/Failed shown as text+symbol badges,
  never colour alone. 繁體中文預設. History paginated 30/page; SVG sparklines; empty windows = insufficient.

## 機器檢查 (Machine checks)

- `unittest discover tests`: **150 passed** (8 new `test_web_projection`: determinism, content-hash
  filename, manifest/summary validation, Taiwan split, index presence, web-schema drift, incremental
  skip, incremental rewrite, atomic-failure rollback).
- `make validate` + architecture gates green. `export-web` verified end-to-end (20 artifacts; incremental
  re-export skipped 19, wrote only the manifest).
- TS types regenerate cleanly from `schemas/web.schema.json` (`node web/scripts/generate-types.mjs`).
- Astro build: see below.

## 沒做什麼 / 邊界 (Boundary)

- The Astro `npm run build` is exercised by the Web CI workflow (PR F); the scaffold is complete and the
  export → build data contract is verified via the projection tests + a local build check.
- Bundle-budget enforcement (JS<60KB/CSS<40KB) is a CI check landing with the web workflow in PR F; the
  design is zero-JS-first with a single small CSS file to stay within budget.

## 你可以驗證 (How to verify)

```bash
PYTHONPATH=src python -m unittest tests.unit.test_web_projection
PYTHONPATH=src python -m radar.cli run-daily --date 2026-07-10 --database data/radar.db
PYTHONPATH=src python -m radar.cli export-web --out-dir . --database data/radar.db
cd web && npm ci && npm run types:check && npm run build
```
