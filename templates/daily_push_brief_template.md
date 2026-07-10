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
report_contract_validation:
degradation_reasons:
```

## 1. Today Main Line

One concise synthesis paragraph linked to supporting event IDs.

## 2. Coverage Matrix

| Report domain | Major rendered / cap | Potential rendered / cap | Taiwan direct evidence | Coverage status | Gap card |
|---|---:|---:|---:|---|---|

Caps come from `config/runtime_contract.json`. A lower count is valid when no qualified item exists and a gap card is present.

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

## 4. Taiwan Direct-Evidence Audit

```text
qualified Taiwan item count:
direct sources checked:
direct source hits:
direct source misses:
social/channel checks:
Taiwan implications excluded from direct count:
remaining Taiwan gaps:
```

## 5. Retail Fixed Matrix

Render every key from `runtime_contract.retail_matrix_keys`.

| Key | Status | Supporting IDs | Taiwan evidence | Gap / next verification |
|---|---|---|---|---|

The `true_vs_fake_segmentation` row must distinguish real product/community/channel differentiation from copy-only or targeting-only personalization.

## 6. Crypto Fixed Matrix

Render every key from `runtime_contract.crypto_matrix_keys`.

| Key | Status | Data checked | Supporting IDs | Gap / next verification |
|---|---|---|---|---|

Price-only coverage is insufficient.

## 7. Structural Trend Indicator Panel

| Indicator | Direction | Confidence | Supporting IDs | Counter IDs | Missing data | Next verification |
|---|---|---|---|---|---|---|
| K-shaped AI productivity economy |  |  |  |  |  |  |
| AI bubble / overinvestment |  |  |  |  |  |  |
| Brand polarization + true vs fake segmentation |  |  |  |  |  |  |

These are cumulative direction meters, not single-day conclusions.

## 8. Rejection and Retry Audit

```text
duplicate_rejection_count:
field_overlap_rejection_count:
niche_low_novelty_rejection_count:
candidate_retry_paths_used:
source discovery used:
```

## 9. Future Outlook

```text
7–30 days:
1–3 months:
3–12 months:
```

Each outlook statement must cite supporting event or signal IDs and state what would invalidate it.

## 10. Post-run Backtest and Model Adjustment

```text
what improved:
what failed:
coverage blind spots:
source registry additions proposed:
runtime / contract changes proposed:
next-run checks:
```

## Completion Rule

The brief is `complete` only when the runtime report contract validates and no required coverage cell or audit remains unresolved. Otherwise mark `partial` or `failed` and show the reasons. Fixture mode is always partial for real-world completeness.
