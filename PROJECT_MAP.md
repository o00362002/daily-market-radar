# daily-market-radar｜PROJECT_MAP

Navigation projection for Event Intelligence Runtime v2.

## 1. Canonical control layer

Entry and per-concept owners live in `AGENTS.md`（讀取路由）plus the machine contract `brain.manifest.yaml`. This map does not re-list them; sections 2–11 below project the runtime layout only.

## 2. Deterministic runtime

```text
src/radar/contracts/    strict report/web models plus typed frozen evaluation/runtime DTOs
src/radar/domain/       provider-neutral document, event and signal values
src/radar/ports/        ten stable behavior Protocols
src/radar/application/  provider-neutral daily orchestration
src/radar/pipeline/     pure deduplicate, cluster, classify and coverage functions
src/radar/reporting/    planner and report-contract validation
src/radar/adapters/     concrete fixture and live RSS/Atom adapters
src/radar/evaluators/   concrete deterministic evaluator
src/radar/repositories/ concrete memory and SQLite repositories
src/radar/stores/       concrete state and web-artifact stores
src/radar/publishers/   concrete report publishers
src/radar/composition.py concrete selection / factory
src/radar/runtime/      backward-compatible façade
schemas/                JSON-schema payload contracts
migrations/             persistence foundation
```

Dependency direction:

```text
contracts/domain → ports → application → composition root → concrete infrastructure
```

LLMs may assist semantic extraction, fuzzy matching, summaries and trend mapping. Fetching, source identity, URL safety, counts, coverage, evidence trace and contract validation remain deterministic.

## 3. Source architecture

```text
config/source_registry.json = canonical identity and adapter registry
FRESHRSS_SEEDS.opml         = generated projection
sources/                    = legacy / compatibility inputs pending regeneration
configs/query_recipes.yml   = fixed news, competitor and indicator-only query recipes
```

One real source has one source_id. RSS, API, web, RSSHub and social are adapters.

## 4. Competitor Intelligence architecture

```text
config/competitor_registry.json       canonical product/social competitor identities, aliases and priorities
configs/competitor_intelligence.yml   collection, projection, evidence and analysis policy
memory/watchlist.md                    owner-approved long-term watch intent
tools/coverage_checker.md              fixed-check and gap audit
web/src/lib/competitors.ts             registry-backed projection helper
web/src/pages/competitors.astro        complete competitor page
web/src/pages/index.astro              daily competitor summary
```

Competitor Intelligence is a first-class cross-domain capability, not a sixth news domain. Each event keeps exactly one canonical primary domain and may additionally appear in the competitor projection without being counted twice.

## 5. Semantic radar modules

```text
configs/radars.yml
configs/triggers.yml
configs/evidence.yml
configs/technology_development.yml
configs/structural_trend_indicators.yml
configs/indicator_tracking.yml
configs/news_freshness_and_taiwan_news.yml
configs/search_retry_protocol.yml
configs/competitor_intelligence.yml
```

These define what to look for and how to judge it. They do not redefine report domains or completion counts.

Labor and consumption pressure are maintained under `configs/indicator_tracking.yml` as indicator-only. The retired labor domain identifier remains only as a compatibility alias in the runtime contract.

## 6. Report domains and profiles

Canonical report domains and profile minimum floors live only in `config/runtime_contract.json`.

```text
global_markets_macro
ai_agents_applications
crypto_rwa_agent_payments
retail_consumer_fashion
science_technology_industry
```

```text
daily_push = concise rendering with minimum floors and no ceiling
full       = all qualified items allowed by run budget
```

Fine-grained radars and competitor projections map into the canonical domains without creating extra quotas.

## 7. Human workflow and rendering

```text
workflows/daily_push_brief_workflow.md
templates/daily_push_brief_template.md
workflows/daily_radar_workflow.md
templates/daily_report_template_v2.md
workflows/news_search_content_workflow.md
workflows/news_content_workflow.md
```

Workflows order execution. Templates render already validated runtime output. Product/Social Competitor Watch is a fixed rendered section; labor and consumption pressure appear in the final indicator panel rather than a standalone news chapter.

## 8. Memory, evidence and evaluation

```text
memory/potential_pool.md       capture-stage weak signals without prefilter
memory/watchlist.md            owner-approved persistent watch areas and competitor list
memory/missed_cases/           approved reusable failure checks
reports/                       historical reports and execution evidence
reports/backtests/             post-run reviews
evals/ and loops/              replay and improvement controls
```

Evidence does not become Memory without approval.

## 9. Web projection

```text
validated RadarReportV2
→ typed WebArtifactV1 projection
→ artifacts/web/v1
→ Astro static dashboard
```

The left sidebar exposes Today, History, Legacy, Trends, Retail, Crypto, Taiwan and Competitors. The competitor web layer consumes the canonical competitor registry instead of maintaining separate hard-coded lists.

## 10. Runtime boundary

Implemented:

```text
fixture replay
live RSS/Atom ingestion
source registry validation
competitor identity registry and registry-backed web projection
OPML drift validation
URL normalization and de-duplication
event clustering and lane separation
coverage gaps
report contract validation
optional SQLite report and gap persistence
```

Still incomplete for production completeness:

```text
web, API and authenticated social source-specific adapters
external discovery providers
typed competitor payload and durable competitor-history table inside RadarReportV2/runtime
complete fixed competitor official-channel execution audit
historical event repository and material-delta comparison for every source route
production credentials and end-to-end live validation
```

## 11. Frozen history

Historical v1 fixed-count specifications, six-domain wording and labor standalone-news behavior remain for context only. They are not current routing or completion authority.
