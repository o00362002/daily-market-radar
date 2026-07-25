# 2026-07-25｜Typed competitor monitoring

## Problem

The competitors page previously projected only the general daily-news pool. A zero count meant no qualified news item matched a competitor name and operational context, but it did not mean official vendor channels had been checked. The UI therefore could not truthfully distinguish no update, not checked, and source failure.

## Implemented

- Added `config/competitor_sources.json` as the executable source authority for 21 named product competitors.
- Excluded the broad social/content group from fixed checks until named account-level sources exist.
- Added provider-neutral `CompetitorMonitor` port and `OfficialCompetitorMonitor` adapter.
- Reused the bounded SSRF-aware HTTP transport with conditional ETag and Last-Modified requests.
- Added durable visible-content baselines, hashes, multilingual shingles, similarity and length-change thresholds.
- Added strict `CompetitorAuditV1`, `CompetitorCheckV1` and `CompetitorSourceCheckV1` to RadarReportV2.
- Persisted competitor baseline state atomically with the accepted daily report.
- Added baseline, checked-no-major-update, updated, partial and failed states.
- Updated the competitors page to show official source evidence, errors, material-change excerpts, general-news projections and recent audit history separately.

## Honest boundary

- The first successful production run establishes baselines; existing vendor copy is not labeled as a new update.
- A changed official page is a material-content signal, not automatically a competitive threat conclusion.
- Social/content monitoring remains discovery-only until concrete account handles and executable adapters are configured.
- Pages that block automated access remain visible as failed or partial checks rather than being silently treated as no update.

## Required verification

- unit tests for baseline, conditional no-change, material update, partial and failed checks
- contract tests for legacy migration and typed audit invariants
- integration test for atomic report and competitor-state persistence
- report schema synchronization
- Astro type check and build
- live production baseline run after merge
