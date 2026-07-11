# Daily Push Brief Workflow v2

Purpose: render a concise daily brief from the deterministic Event Intelligence Runtime.
Concise means fewer rendered items, not weaker collection or validation.

## Owner and trigger

```text
owner: AGENT_DAILY_PUSH_BRIEF
profile: daily_push
runtime contract: config/runtime_contract.json
canonical source registry: config/source_registry.json
competitor registry: config/competitor_registry.json
```

Use for ordinary daily-news, morning-brief and market-radar requests. Full/archive requests use `workflows/daily_radar_workflow.md`.

## Ordered execution

```text
1. Read AGENTS.md and select AGENT_DAILY_PUSH_BRIEF.
2. Load config/runtime_contract.json profile=daily_push.
3. Validate config/source_registry.json and source health.
4. Load config/competitor_registry.json and configs/competitor_intelligence.yml.
5. Determine live / degraded / fixture ingest mode.
6. Ingest top-down sources.
7. Ingest bottom-up and weak-signal sources.
8. Run fixed competitor product/social queries; resolve claims to official or verifiable evidence.
9. Run external discovery only for coverage gaps; resolve findings to original sources.
10. Normalize URLs and source identities.
11. De-duplicate documents and cluster them into events.
12. Compare event history and require a material today delta.
13. Verify evidence, counterevidence and Taiwan direct evidence.
14. Score importance, potential and confidence independently.
15. Assign exactly one primary report domain per event.
16. Keep major and potential lanes separate.
17. Build coverage cells and gap cards.
18. Run Retail matrix, Crypto matrix, Structural Trend Indicator Panel and indicator-only labor/consumption tracking.
19. Build Product Competitor and Social Competitor projections without duplicating events or creating a new report domain.
20. Check daily-push minimum floors from the runtime contract; disclose any shortfall.
21. Render templates/daily_push_brief_template.md.
22. Validate schemas/report.schema.json and Python report contract.
23. Run post-output backtest and expose degradation reasons.
```

## Five canonical report domains

Read from `config/runtime_contract.json`; do not hand-create extra report domains.

```text
global_markets_macro
ai_agents_applications
crypto_rwa_agent_payments
retail_consumer_fashion
science_technology_industry
```

Fine-grained radars in `configs/radars.yml` are modules and indicators, not additional report-domain slots.
Policy and geopolitics map to `global_markets_macro` unless the runtime contract changes.
The retired `labor_demographics_consumption_pressure` domain is a backward-compatible alias to `global_markets_macro`; labor and consumption pressure are normally rendered only in the fixed indicator panel.

## Rendering rule

Profiles define minimum floors, never ceilings. Homepage/per-domain selections are readability projections only.

```text
rendering selection != completeness proof
missing qualified item → coverage gap
qualified item omitted from concise projection → retain in canonical report and archive
```

Do not fabricate, repeat or downgrade quality to fill a section.

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

## Competitor intelligence rule

```text
source of truth: config/competitor_registry.json
policy: configs/competitor_intelligence.yml
output groups: product competitors / social and content competitors
```

A competitor item keeps its canonical primary domain and is projected into the competitor section. It is not counted twice. If fixed competitor checks ran and no fresh material delta exists, render `已查無重大更新`. If fixed checks did not run, render `未完整查證`.

## Labor and consumption boundary

Labor, hiring, layoffs, wages and consumption pressure do not receive a standalone news block or quota. They update `configs/indicator_tracking.yml#labor_consumption_pressure`. Only an independently material AI, macro, retail or technology event may appear once under that canonical domain.

## Taiwan rule

Direct Taiwan evidence and Taiwan implication remain separate. If Taiwan sources are unavailable or unchecked, output a coverage gap. Generic search and model inference do not count as direct checks.

## Technology rule

AI market, regulation, server or earnings stories do not consume a standalone Technology slot without a technical milestone. Scan at least six non-AI technical subdomains or expose the gap.

## Fixed panels

Always include:

```text
Product and Social Competitor Watch
Retail fixed matrix
Crypto fixed matrix
Structural Trend Indicator Panel
Labor and Consumption Pressure indicator-only row
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
