# Deploy accepted site after relevant main changes

Date: 2026-07-25

## Problem

Competitor and web changes merged to `main` passed CI but did not reach GitHub Pages. The production workflow only ran on the daily schedule or manual dispatch, while the `ai-analysis` push trigger covered only analysis-layer files. The public competitors page therefore remained on the previous deployed artifact.

## Decision

`daily-intelligence` now also runs on pushes to `main` when runtime, configuration, schemas, web code, the production gate, or the workflow itself changes.

The push path uses the same full production pipeline as the daily schedule:

- restore durable state
- run live intelligence for the Taiwan date
- apply report quality checks
- generate AI analysis
- apply the production deployment gate
- persist only accepted state
- build and deploy GitHub Pages

This is not a bypass deployment. A rejected report or fallback/missing analysis still preserves the previous public site and fails visibly.

## Scope

The trigger covers:

- `src/radar/**`
- `config/**`
- `configs/**`
- `web/**`
- `schemas/**`
- `tools/check_production_quality.py`
- `.github/workflows/daily-intelligence.yml`

Documentation-only changes remain excluded.
