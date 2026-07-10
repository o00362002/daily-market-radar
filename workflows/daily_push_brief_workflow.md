# Daily Push Brief Workflow v2

Purpose: render a concise daily brief from the deterministic Event Intelligence Runtime.
Concise means fewer rendered items, not weaker collection or validation.

## Owner and trigger

```text
owner: AGENT_DAILY_PUSH_BRIEF
profile: daily_push
runtime contract: config/runtime_contract.json
canonical source registry: config/source_registry.yaml
```

Use for ordinary daily-news, morning-brief and market-radar requests. Full/archive requests use `workflows/daily_radar_workflow.md`.

## Ordered execution

```text
1. Read AGENTS.md and select AGENT_DAILY_PUSH_BRIEF.
2. Load config/runtime_contract.json profile=daily_push.
3. Validate config/source_registry.yaml and source health.
4. Determine live / degraded / fixture ingest mode.
5. Ingest top-down sources.
6. Ingest bottom-up and weak-signal sources.
7. Run external discovery only for coverage gaps; resolve findings to original sources.
8. Normalize URLs and source identities.
9. De-duplicate documents and cluster them into events.
10. Compare event history and require a material today delta.
11. Verify evidence, counterevidence and Taiwan direct evidence.
12. Score importance, potential and confidence independently.
13. Assign exactly one primary report domain per event.
14. Keep major and potential lanes separate.
15. Build coverage cells and gap cards.
16. Run Retail matrix, Crypto matrix and Structural Trend Indicator Panel.
17. Apply daily-push slot caps from the runtime contract.
18. Render templates/daily_push_brief_template.md.
19. Validate schemas/report.schema.json and Python report contract.
20. Run post-output backtest and expose degradation reasons.
```

## Six canonical report domains

Read from `config/runtime_contract.json`; do not hand-create extra report domains.

```text
global_markets_macro
ai_agents_applications
crypto_rwa_agent_payments
retail_consumer_fashion
science_technology_industry
labor_demographics_consumption_pressure
```

Fine-grained radars in `configs/radars.yml` are modules and indicators, not additional report-domain slots.
Policy and geopolitics map to `global_markets_macro` unless the runtime contract changes.

## Slot-cap rule

Daily Push renders up to the configured major and potential caps per domain.

```text
slot cap != completeness proof
missing qualified item → gap card
extra qualified item → retain in machine/archive output, omit from concise rendering if over cap
```

Do not fabricate, repeat or downgrade quality to fill a slot.

## Item requirements

Every item requires:

```text
event_id
primary_domain
report_lane: major / potential
headline
first_seen_at
today_delta
importance_score
potential_score
confidence_score
evidence_links
direct_taiwan_evidence
taiwan_implication
counterevidence
uncertainties
next_watch
```

Potential items additionally require:

```text
candidate_type
formation_level
fresh concrete anchor
what would confirm
what would invalidate
next check
```

One event cannot occupy both lanes or more than one primary-domain slot.

## Taiwan rule

Direct Taiwan evidence and Taiwan implication remain separate. If Taiwan sources are unavailable or unchecked, output a coverage gap. Generic search and model inference do not count as direct checks.

## Technology rule

AI market, regulation, server or earnings stories do not consume a standalone Technology slot without a technical milestone. Scan at least six non-AI technical subdomains or expose the gap.

## Fixed panels

Always include every key from the runtime contract:

```text
Retail fixed matrix
Crypto fixed matrix
Structural Trend Indicator Panel
rejection / retry counters
source and coverage audit
post-run backtest
```

Empty evidence is represented as `insufficient`, not omitted.

## Status wording

```text
profile: daily_push
status: complete / partial / failed
ingestion_mode: live / degraded / fixture
contract_version:
degradation_reasons:
```

Fixture mode is always partial for real-world news completeness.
