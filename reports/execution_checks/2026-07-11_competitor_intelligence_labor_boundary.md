# Execution Check｜Competitor Intelligence + Labor Indicator Boundary

Date: 2026-07-11
Status: partial until repository CI / Astro build completes
Owner decision: approved in conversation

## 1. Change intent

```text
Promote product and social competitor tracking from watchlist-only behavior to a first-class,
registry-backed intelligence capability with fixed web and report rendering.

Demote labor / hiring / layoffs / wages / consumption pressure from a standalone news domain
to indicator-only tracking, without losing the ability to surface independently material AI,
macro, retail or technology events.
```

## 2. Canonical changes

```text
config/runtime_contract.json
- v2.0 → v2.1
- six → five canonical news domains
- labor_demographics_consumption_pressure retained only as compatibility alias to global_markets_macro

config/competitor_registry.json
- canonical product/social competitor identities, aliases, priorities and high-risk signals

configs/competitor_intelligence.yml
- cross-domain projection policy
- evidence, no-old-news and incomplete-check rules

configs/indicator_tracking.yml
- labor_consumption_pressure mode=indicator_only
- standalone_news_section=false
- consumes_news_slot=false
```

## 3. Execution and rendering sync

```text
configs/query_recipes.yml
- competitor product/social recipes added
- labor recipes moved to indicator_only_recipes

workflows/daily_push_brief_workflow.md
- fixed competitor checks and projection added
- labor standalone domain removed

templates/daily_push_brief_template.md
- fixed Product/Social Competitor section added
- labor row placed in final indicator panel

web/src/lib/competitors.ts
- all web competitor projections consume the canonical registry

web/src/pages/index.astro
web/src/pages/competitors.astro
- no separate hard-coded competitor lists
```

## 4. Memory and navigation sync

```text
SYSTEM_PROMPT.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
HIGH_LEVEL_INDEX.md
PROJECT_MAP.md
memory/watchlist.md (already updated in the prior change)
tools/coverage_checker.md (already updated in the prior change)
```

## 5. Test and checker coverage

```text
tests/unit/test_runtime_contract.py
- asserts five canonical domains
- asserts legacy labor alias

tests/unit/test_competitor_registry.py
- asserts required groups, unique ids and cross-domain projection policy

src/radar/pipeline/ingest.py
- labor fixture routed through global_markets_macro
```

## 6. Reality check

```text
Implemented now:
- canonical competitor registry
- fixed competitor query/policy layer
- competitor web projection using one registry
- five-domain runtime contract
- labor indicator-only configuration and rendering policy
- core memory and navigation sync

Not implemented yet:
- typed competitor payload inside RadarReportV2
- durable competitor-history database table
- fully executable official-channel adapter for every named competitor
- authenticated Threads / Instagram / LinkedIn competitor collection
- local CI / Astro validation in this connector environment
```

## 7. Validation status

```text
Repository file writes: complete
Machine-consumer paths: added
Local Python tests: not run in this environment
Local Astro type/build: not run in this environment
GitHub Actions / Pages validation: pending next workflow run
Completion status: partial
```

## 8. Memory trigger check

```text
Memory update triggered: yes
Trigger type: user boundary correction + source-of-truth changed + dependency-route changed
Memory Patch Candidate: local child
Target files: CURRENT_STATE.md, CURRENT_DECISIONS.md, HIGH_LEVEL_INDEX.md, PROJECT_MAP.md, SYSTEM_PROMPT.md
Review required: yes, owner decision already supplied
Completion status: partial pending CI
```
