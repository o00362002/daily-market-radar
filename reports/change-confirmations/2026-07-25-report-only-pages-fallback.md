# Healthy report deployment no longer blocked by unavailable AI

Date: 2026-07-25

## Problem

The public site remained stale after competitor and runtime fixes because production deployment treated RadarReportV2 and AIAnalysisV1 as one indivisible gate. A healthy current report could not deploy when the AI provider was unavailable or returned fallback output. This also prevented pure UI and competitor-page changes from reaching GitHub Pages.

## Decision

The daily production workflow now has two gates:

1. **Report gate, mandatory**
   - live ingestion
   - expected Taiwan date
   - unique event ids
   - bounded total items, Major count and Major ratio

2. **AI analysis gate, optional enhancement**
   - api-assisted or chat-assisted
   - provider and model present
   - fallback false
   - matching report id and date

A failed report still blocks deployment and preserves the previous site. If only AI analysis fails, the workflow:

- deploys the healthy report and current web code
- persists accepted report state
- removes the entire invalid/mismatched AI artifact directory before build
- writes `analysis-status.json` with the reason
- renders the existing honest `尚無 AIAnalysisV1` state on `/analysis`
- uploads diagnostics as a report-only production run

No deterministic or stale AI analysis is published as a successful update.

## Operational effect

A missing OpenAI API key can no longer freeze the entire public dashboard. The fact layer, competitor page, coverage gaps and validated report continue updating independently; the AI interpretation layer appears only when it passes its own stricter gate.
