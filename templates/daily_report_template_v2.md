# Full Daily Radar Report Template v2

Formal archive rendering for a validated `profile=full` runtime report.

## 0. Run Metadata

```text
report date / timezone:
run_id:
profile: full
status: complete / partial / failed
contract_version:
ingestion_mode: live / degraded / fixture
run budget:
source registry status:
source health status:
report contract validation:
degradation reasons:
```

## 1. Executive Synthesis

Summarize the main cross-domain developments, structural changes and decision relevance. Every conclusion links to event or signal IDs.

## 2. Coverage Cells and Gap Cards

| Domain | Region | Language | Source role | Channel | Window | Observed | Status | Retry / gap |
|---|---|---|---|---|---|---:|---|---|

Completeness is determined by coverage and contract validation, not fixed item counts.

## 3. Source and Ingestion Audit

```text
canonical registry checked:
source health checks:
top-down sources checked:
bottom-up sources checked:
non-English / regional sources checked:
social-first direct channels checked:
FreshRSS / RSSHub status:
external discovery providers used:
original-source resolution status:
source misses / stale / blocked:
```

## 4. Major Lane by Domain

For every canonical report domain, output all qualified major items allowed by the declared run budget.

Each item:

```text
item_id / event_id:
primary_domain:
headline:
first_seen_at:
today material delta:
importance / potential / confidence:
evidence trace:
counterevidence:
uncertainties:
Taiwan direct evidence:
Taiwan implication:
next verification:
```

## 5. Potential Lane by Domain

Each potential item:

```text
item_id / signal_id / event_id:
primary_domain:
headline:
candidate_type:
formation_level:
fresh concrete anchor:
today material delta:
importance / potential / confidence:
why early / why scalable:
what would confirm:
what would invalidate:
evidence trace:
counterevidence / uncertainty:
next check:
```

A single event cannot appear in both lanes or more than one primary domain.

## 6. Taiwan Direct-Evidence Section

```text
qualified Taiwan events:
direct source list:
official/data checks:
social/channel direct checks:
Taiwan implications excluded from direct evidence:
failed or unavailable Taiwan sources:
next retry:
```

## 7. Retail Fixed Matrix

Render every configured Retail key.

| Key | Status | Supporting IDs | Counter IDs | Taiwan evidence | Missing data | Next verification |
|---|---|---|---|---|---|---|

Include true-vs-fake segmentation evidence at product, assortment, channel, community, sell-through, repeat purchase and discount levels.

## 8. Crypto Fixed Matrix

Render every configured Crypto key.

| Key | Status | Data checked | Supporting IDs | Counter IDs | Missing data | Next verification |
|---|---|---|---|---|---|---|

## 9. Structural Trend Indicator Panel

| Indicator | Direction | Confidence | Supporting IDs | Counter IDs | Missing data | One-sentence read | Next verification |
|---|---|---|---|---|---|---|---|
| K-shaped AI productivity economy |  |  |  |  |  |  |  |
| AI bubble / overinvestment |  |  |  |  |  |  |  |
| Brand polarization + true vs fake segmentation |  |  |  |  |  |  |  |

## 10. Technology Development Audit

```text
non-AI subdomains checked:
technical milestones:
commercial maturity:
supply-chain readiness:
AI-overcapture rejections:
Taiwan technology evidence:
remaining gaps:
```

## 11. Rejection, De-duplication and Retry Audit

```text
duplicate_rejection_count:
field_overlap_rejection_count:
niche_low_novelty_rejection_count:
background-only rejection count:
candidate_retry_paths_used:
external discovery results accepted / rejected:
```

## 12. Future Direction

```text
7–30 days:
1–3 months:
3–12 months:
```

Each statement requires supporting IDs, counterevidence and invalidation conditions.

## 13. Post-run Backtest

```text
missed cases:
coverage blind spots:
source health failures:
source registry changes proposed:
contract / schema changes proposed:
model behavior adjustments:
next-run acceptance tests:
```

## Archive Gate

A formal report may be marked complete only when the runtime contract, coverage gate, evidence trace, matrices, structural indicators and post-run backtest validate. Fixture mode cannot be archived as complete real-world intelligence.
