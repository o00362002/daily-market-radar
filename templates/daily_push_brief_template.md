# Daily Push Brief Template v2

Render from a validated runtime report. Do not infer completion from item counts.

## 0. Run Status

```text
報告日期：
profile: daily_push
status: complete / partial / failed
contract_version:
ingestion_mode: live / degraded / fixture
source_registry_status:
source_health_status:
coverage_status:
competitor_registry_status:
report_contract_validation:
degradation_reasons:
```

## 1. Today Main Line

One concise synthesis paragraph linked to supporting event IDs.

## 2. Coverage Matrix

| Report domain | Major qualified | Potential qualified | Taiwan direct evidence | Coverage status | Gap card |
|---|---:|---:|---:|---|---|

Canonical report domains come from `config/runtime_contract.json`. Homepage/per-domain selections are readability projections, not completeness proof. Labor and consumption pressure do not receive a standalone report-domain row.

## 3. Domain Blocks

Repeat for each canonical report domain.

### [DOMAIN]

#### Major lane

For each rendered item:

```text
item_id:
event_id:
headline:
today_delta:
importance / potential / confidence:
evidence:
counterevidence:
uncertainties:
Taiwan direct evidence:
Taiwan implication:
next_watch:
```

#### Potential lane

For each rendered item:

```text
item_id:
signal_id:
event_id:
headline:
candidate_type:
formation_level:
fresh concrete anchor:
today_delta:
importance / potential / confidence:
what would confirm:
what would invalidate:
evidence:
uncertainties:
next_watch:
```

#### Domain gap card

```text
failed coverage cells:
source hits / misses:
retry paths used:
remaining gap:
```

Do not repeat one event across domains or lanes.

## 4. Competitor Intelligence

Competitor watch is a cross-domain projection from the same validated events. It does not create a sixth report domain and does not count an event twice.

### 4.1 Product Competitors

```text
fixed checks executed: yes / no / partial
status: major update / potential signal / checked no major update / incomplete
competitor_id:
event date:
fresh material delta:
overlap: low / medium / high
affected layer: free entry / template subscription / decision module / agent / private integration
threat: functional substitution / price compression / distribution control / ecosystem advantage
current differentiation status:
recommended action: observe / verify / reposition / accelerate / no action
evidence:
```

### 4.2 Social and Content Competitors

```text
fixed checks executed: yes / no / partial
status: major update / potential signal / checked no major update / incomplete
competitor_id or category:
fresh material delta:
overlap with store operations × data × AI positioning:
attention or product-funnel threat:
recommended action:
evidence:
```

If there is no fresh material delta after fixed checks, state `已查無重大更新`. If fixed checks were not completed, state `未完整查證`. Never fill with old competitor news.

## 5. Taiwan Direct-Evidence Audit

```text
qualified Taiwan item count:
direct sources checked:
direct source hits:
direct source misses:
social/channel checks:
Taiwan implications excluded from direct count:
remaining Taiwan gaps:
```

## 6. Retail Fixed Matrix

Render every key from `runtime_contract.retail_matrix_keys`.

| Key | Status | Supporting IDs | Taiwan evidence | Gap / next verification |
|---|---|---|---|---|

The `true_vs_fake_segmentation` row must distinguish real product/community/channel differentiation from copy-only or targeting-only personalization.

## 7. Crypto Fixed Matrix

Render every key from `runtime_contract.crypto_matrix_keys`.

| Key | Status | Data checked | Supporting IDs | Gap / next verification |
|---|---|---|---|---|

Price-only coverage is insufficient.

## 8. Structural Trend Indicator Panel

| Indicator | Direction | Confidence | Supporting IDs | Counter IDs | Missing data | Next verification |
|---|---|---|---|---|---|---|
| K-shaped AI productivity economy |  |  |  |  |  |  |
| AI bubble / overinvestment |  |  |  |  |  |  |
| Brand polarization + true vs fake segmentation |  |  |  |  |  |  |

These are cumulative direction meters, not single-day conclusions.

## 9. Final Indicator Status and News Synthesis Panel

Fixed indicators do not consume news slots.

| Indicator area | Today status | Direction | Supporting news IDs | Data gap | Next check |
|---|---|---|---|---|---|
| Crypto / blockchain |  |  |  |  |  |
| AI product / infrastructure |  |  |  |  |  |
| Retail / consumer / social / fashion |  |  |  |  |  |
| Labor and consumption pressure (indicator only) |  |  |  |  |  |
| Global markets / capital flows |  |  |  |  |  |

Labor, hiring, layoffs, wages and consumption pressure must remain in this panel unless the event independently qualifies under AI, global markets, retail or technology. Do not create a standalone labor news chapter.

## 10. Rejection and Retry Audit

```text
duplicate_rejection_count:
field_overlap_rejection_count:
niche_low_novelty_rejection_count:
candidate_retry_paths_used:
source discovery used:
competitor fixed checks used:
```

## 11. Future Outlook

```text
7–30 days:
1–3 months:
3–12 months:
```

Each outlook statement must cite supporting event or signal IDs and state what would invalidate it.

## 12. Post-run Backtest and Model Adjustment

```text
what improved:
what failed:
coverage blind spots:
competitor blind spots:
source registry additions proposed:
runtime / contract changes proposed:
next-run checks:
```

## Completion Rule

The brief is `complete` only when the runtime report contract validates and no required coverage cell or audit remains unresolved. Otherwise mark `partial` or `failed` and show the reasons. Fixture mode is always partial for real-world completeness.
