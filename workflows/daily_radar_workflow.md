# Full Daily Radar Workflow v2

Purpose: produce the formal full research and archive output from Event Intelligence Runtime v2.

```text
owner: AGENT_RADAR_REPORT
profile: full
runtime contract: config/runtime_contract.json
canonical source registry: config/source_registry.yaml
archive path: reports/YYYY/YYYY-MM-DD.md
```

## Trigger

Use only for explicit full, formal, complete, archive or research requests.
Ordinary daily pushes use `workflows/daily_push_brief_workflow.md`.

## Ordered execution

```text
1. Select AGENT_RADAR_REPORT.
2. Load config/runtime_contract.json profile=full.
3. Validate source registry, source health and run budget.
4. Declare live / degraded / fixture ingest mode.
5. Run top-down and bottom-up ingestion.
6. Run gap discovery for failed coverage cells.
7. Resolve discovery results to original evidence.
8. Normalize, de-duplicate and event-cluster all documents.
9. Compare prior events and retain only material deltas as current items.
10. Verify claims, counterevidence, timestamps and direct Taiwan evidence.
11. Score importance, potential and confidence independently.
12. Assign one primary report domain per event.
13. Keep major and potential lanes independent.
14. Compute coverage cells across domain, region, language, source role, channel and time window.
15. Produce gap cards for silent, stale, blocked, empty or failing cells.
16. Run Retail fixed matrix, Crypto fixed matrix and Structural Trend Indicator Panel.
17. Select all qualified items allowed by the full run budget; do not use fixed-count completion rules.
18. Render templates/daily_report_template_v2.md.
19. Validate JSON schema and Python report contract.
20. Archive the report, run backtest and write reusable missed cases when approved.
```

## Completeness rule

The full report is complete only when every requirement from `config/runtime_contract.json` passes.

```text
number of items != proof of completeness
coverage and evidence contract = proof of completeness
```

Do not require or claim historical `5+5`, `48-signal` or `60-signal` counts.
If a domain lacks qualified signals, show the coverage and retry gap. If many qualified signals exist, include all within the declared run budget.

## Canonical report domains

Use the six domains from the runtime contract. Fine-grained radars, triggers and structural indicators are subordinate modules, not extra report-domain quotas.

## Major / potential separation

```text
major = high current decision relevance
potential = early signal with future option value
confidence = evidence strength
```

One event cannot fill both lanes or multiple primary domains. Cross-domain consequences are represented through mappings and synthesis.

## Taiwan boundary

Taiwan direct evidence must be source-backed. Taiwan implication is inference and cannot satisfy Taiwan coverage. Channel-first sources require direct checks; unavailable channels become gap cards.

## Required report sections

```text
run metadata and degradation status
source-health and ingestion audit
coverage cells and gap cards
major lane by domain
potential lane by domain
Retail fixed matrix
Crypto fixed matrix
Structural Trend Indicator Panel
Taiwan direct-evidence audit
rejection and retry counters
future outlook linked to signal IDs
post-run backtest and model adjustments
```

Every synthesis statement links back to event or signal IDs.

## Fixture boundary

Fixture replay validates deterministic behavior only. A fixture run cannot be archived as a complete real-world daily report.
