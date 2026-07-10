# daily-market-radar｜PROJECT_MAP

Navigation projection for Event Intelligence Runtime v2.

## 1. Canonical control layer

```text
AGENTS.md                    first entry and route selection
CURRENT_STATE.md             current facts
CURRENT_DECISIONS.md         accepted decisions
config/runtime_contract.json machine execution and output contract
config/source_registry.yaml  canonical source registry
AGENT_DEFINITION_MAP.md      route mapping
DEPENDENCY_MAP.md            dependency and degradation map
schema/sync-matrix.json      machine-consumed change edges
```

## 2. Deterministic runtime

```text
src/radar/domain/       document, event, signal, coverage and report types
src/radar/schemas/      registry/config parsing
src/radar/pipeline/     ingest, normalize, deduplicate, cluster, classify, coverage
src/radar/reporting/    planner and report-contract validation
src/radar/runtime/      run orchestration and profile contract
schemas/                JSON-schema payload contracts
migrations/             persistence foundation
```

Dependency direction:

```text
domain/types → config/schemas → repositories/adapters → pipeline/services → reporting/runtime
```

LLMs may assist semantic extraction, fuzzy matching, summaries and trend mapping. Fetching, source identity, URL safety, counts, coverage, evidence trace and contract validation remain deterministic.

## 3. Source architecture

```text
config/source_registry.yaml = canonical identity and adapter registry
FRESHRSS_SEEDS.opml         = generated projection
sources/                    = legacy / compatibility inputs pending regeneration
configs/query_recipes.yml   = fixed query recipes
```

One real source has one source_id. RSS, API, web, RSSHub and social are adapters.

## 4. Semantic radar modules

```text
configs/radars.yml
configs/triggers.yml
configs/evidence.yml
configs/technology_development.yml
configs/structural_trend_indicators.yml
configs/news_freshness_and_taiwan_news.yml
configs/search_retry_protocol.yml
```

These define what to look for and how to judge it. They do not redefine report domains or completion counts.

## 5. Report domains and profiles

Canonical report domains and profile slot caps live only in `config/runtime_contract.json`.

```text
daily_push = concise rendering with slot caps
full       = all qualified items allowed by run budget
```

Fine-grained radars map into the canonical domains.

## 6. Human workflow and rendering

```text
workflows/daily_push_brief_workflow.md
templates/daily_push_brief_template.md
workflows/daily_radar_workflow.md
templates/daily_report_template_v2.md
workflows/news_search_content_workflow.md
workflows/news_content_workflow.md
```

Workflows order execution. Templates render already validated runtime output.

## 7. Memory, evidence and evaluation

```text
memory/potential_pool.md       capture-stage weak signals without prefilter
memory/missed_cases/           approved reusable failure checks
reports/                       historical reports and execution evidence
reports/backtests/             post-run reviews
evals/ and loops/              replay and improvement controls
```

Evidence does not become Memory without approval.

## 8. Runtime boundary

Current runtime foundation supports deterministic fixture replay and contract checks.
Live network ingestion, durable database persistence, scheduler and provider integrations must be explicitly validated before the system claims production operation.

## 9. Frozen history

Historical v1 fixed-count specifications and migration files remain for context only. They are not current routing or completion authority.
