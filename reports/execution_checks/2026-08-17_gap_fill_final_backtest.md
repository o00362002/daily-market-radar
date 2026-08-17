# 2026-08-17 gap-fill final live backtest

## Scope

This record closes the implementation, live-backtest, chat-analysis import and Pages deployment loop for the 2026-08-17 radar. The accepted work repaired taxonomy leakage, same-run/cross-day identity, confidence calibration, indicator/news freshness, stable-URL measurement deltas, competitor evidence continuity and Taiwan source traceability.

## Accepted change sequence

- PR #70 · `cd7de9b1028f5cd0a959c74ce83c730a4bf5f918` · taxonomy leakage、indicator-only lane、WACA evidence boundary
- PR #71 · `ab8bcd09f8fd86717752da7c1eb641a763f4cb46` · BLS + DefiLlama structured measurements
- PR #72 · `4a97a91b4f708e5776c953825c0d2e069a69514e` · confidence score calibration
- PR #73 · `537674be5226bd5e925d643803cf8788bbd07b88` · named AI anchors + WACA state continuity
- PR #74 · `69f9870b2f1c8b738856f882afd950c3320d5710` · official Hyperliquid perp volume/OI/funding
- PR #75 · `00c0a0aff582fa76c2fa1eb6be23aaeda3f98f9e` · same-run sibling story coalescing
- PR #77 · `d3e3fc6e4ed730edf3d738090b877f76c0c4a425` · indicator freshness separated from news freshness
- PR #78 · `b7bac0fc71e9b65b0e7483ac08dac9adc1b36c91` · stable-URL indicator measurement deltas
- PR #79 · `8b68fd20fd319b1f293216c29fa1336c47128d45` · Farside ETF flow + Taiwan FSC VASP fixed measurements
- PR #80 · `02c9710a4cacb2ae810041483fc9f8f2b48ffca5` · Taiwan direct-source audit traceability
- PR #81 · `7505a952f2bace5ae683cbecfcdd565c77078ee4` · final chat-assisted AIAnalysisV1 bound to the completed production report

PR #76 was closed without merge after review found an older full-file `run_daily.py` replacement. PR #77 restarted from current `main` and applied only the narrow freshness change. The stale implementation was never allowed into production.

## Final formal run

```text
daily-intelligence workflow_run_id: 32003893376
workflow head: 02c9710a4cacb2ae810041483fc9f8f2b48ffca5
report run_id: run_9a871b96bda9
date/profile: 2026-08-17 / daily_push
ingestion/status: live_multi / partial
deployment: accepted
durable state: success
```

Formal volume:

```text
items: 173
Major: 108
Potential: 65
Taiwan-direct items: 83
coverage gaps: 2
source failures: 0
```

Domain counts:

```json
{
  "ai_agents_applications": 97,
  "crypto_rwa_agent_payments": 8,
  "global_markets_macro": 35,
  "retail_consumer_fashion": 3,
  "science_technology_industry": 30
}
```

Profiles remain minimum floors, not ceilings. Historical replay was not used to pad counts.

## Structured measurements

All five formal sources executed:

```text
bls_productivity
defillama_hyperliquid
hyperliquid_perp
farside_btc_etf
fsc_tw_vasp_law
```

Integration status:

- `bls_productivity`: `checked`
- `competitor_monitor`: `partial`
- `defillama_hyperliquid`: `checked`
- `external_discovery`: `not_executed`
- `farside_btc_etf`: `checked`
- `freshrss_google_reader`: `credential_unavailable`
- `fsc_tw_vasp_law`: `checked`
- `hyperliquid_perp`: `checked`
- `multi_source`: `partial`
- `rss_atom`: `healthy`
- `structured_measurements`: `healthy`

Taiwan direct-source audit includes `fsc_tw_vasp_law`:

```json
[
  "dgbas_tw",
  "cna_tw",
  "economic_daily_tw",
  "vogue_taiwan",
  "blocktrend_tw",
  "technews_tw",
  "ithome_tw",
  "inside_tw",
  "pts_tw",
  "abmedia_tw",
  "blocktempo_tw",
  "digitimes_asia",
  "fsc_tw_vasp_law"
]
```

All structured observations stay `indicator_only`: they can fill matrices/structural indicators but cannot become Major/Potential cards or potential signals. One dataset failure would remain isolated and visible.

## Crypto and Retail matrices

Crypto observed: **8/8**

```json
[
  "btc_eth_sol_market_structure",
  "etf_flows",
  "perp_dex_volume_oi_funding",
  "regulation_policy",
  "rwa_tokenized_assets",
  "stablecoin_supply_and_dry_powder",
  "taiwan_crypto_fixed_sources",
  "tvl_fees_revenue"
]
```

The formal Crypto panel now separates market structure, ETF flow, stablecoins, RWA, Perp DEX volume/OI/funding, TVL/fees/revenue, regulation and Taiwan fixed sources. Farside remains specialist data; FSC is direct official regulator evidence; Hyperliquid uses only its read-only information endpoint.

Retail observed: **2/9**

```json
[
  "channel_online_marketplace_social_commerce",
  "product_fashion_style_assortment_material_fit_category"
]
```

Still insufficient:

```json
[
  "channel_offline_department_store_mall_street",
  "cost_pressure",
  "inventory_markdown_mid_price_pressure",
  "membership_crm_loyalty_retail_media",
  "social_commerce_content_discovery_ai_referral",
  "taiwan_retail_commercial_district_department_store_brand",
  "true_vs_fake_segmentation"
]
```

The seven remaining Retail cells need operating measurements such as sell-through, inventory age, markdown, member repeat and AI-referral conversion. They are not estimated from general news.

## Structural indicators

```json
[
  {
    "indicator_id": "k_shaped_ai_productivity_economy",
    "direction": "supporting",
    "support_score": 20,
    "counter_score": 0,
    "confidence": 20,
    "supporting_signal_ids": [
      "evt_df844c597646"
    ]
  },
  {
    "indicator_id": "ai_bubble_overinvestment",
    "direction": "insufficient",
    "support_score": 0,
    "counter_score": 0,
    "confidence": "insufficient",
    "supporting_signal_ids": []
  },
  {
    "indicator_id": "brand_market_polarization_and_true_vs_fake_segmentation",
    "direction": "insufficient",
    "support_score": 0,
    "counter_score": 0,
    "confidence": "insufficient",
    "supporting_signal_ids": []
  }
]
```

The K-shaped indicator uses aligned BLS productivity, labor-share and real-hourly-compensation facts from `evt_df844c597646`. Wage/income and productivity-sharing lean toward the hypothesis; labor market, firm-size gap and consumption polarization remain insufficient. The AI-bubble and brand-polarization indicators remain `insufficient`/`N/A`.

## Identity, delta and freshness checks

```text
events observed: 1549
matched existing: 1524
new events: 25
material events: 28
unchanged events: 1521
duplicate-only events: 1511
unresolved matches: 25
```

Delta counts:

```json
{
  "duplicate_document": 1511,
  "funding_change": 1,
  "launch_or_release": 1,
  "new_amount_or_metric": 1,
  "new_event": 25,
  "same_event_same_facts": 10
}
```

Accepted semantics:

```text
same-run coalescing
→ conservative high-precision families only

normal news
→ current material/same-day anchor + bounded Taiwan news window

indicator_only
→ current material/same-day anchor; observation period may be older

stable URL + changed typed facts
→ material indicator delta

stable URL + unchanged typed facts
→ duplicate / no new daily vote
```

The observed `funding_change=1` and `new_amount_or_metric=1` prove the stable-URL measurement-delta path was active.

## Competitor audit

```text
fixed targets: 21
checked targets: 20
updated targets: 0
failed targets: 1
failed ids: ["waca"]
```

WACA's verified baseline remains traceable, but the current direct automated check remains failed/incomplete. No cache, proxy or old article was promoted into the formal audit.

## Report gate, analysis gate and deployment

The canonical report quality check passed:

```text
production-quality-report.valid: True
warnings: ["major_count_above_review_threshold:108>90"]
```

At the daily-run stage, the combined report+AI gate was correctly false because only stale deterministic analysis existed:

```text
production-quality-gate.valid: False
reasons: ["analysis_effective_mode_not_allowed:deterministic", "analysis_provider_missing", "analysis_model_missing", "analysis_fallback_forbidden", "analysis_source_report_mismatch"]
```

The workflow therefore deployed the valid report in report-only mode instead of presenting stale AI output.

A matching chat-assisted analysis was then merged and validated:

```text
PR #81 merge: 7505a952f2bace5ae683cbecfcdd565c77078ee4
materialized main commit: d310644d51421df33642460d4247892784d8d3ff
import-chat-analysis workflow_run_id: 32005837749
analysis_id: analysis_c1c697253b46da98
source_run_id: run_9a871b96bda9
context_hash: 5fae7ea3c94089d2f9912dda781f325fd6871b7aae9728d869411fd82bd12858
mode: chat-assisted
provider/model: OpenAI ChatGPT / GPT-5.6 Pro
valid: True
materialized_input: True
hydrated_fields: ["translations", "structural_indicators", "linked_indicators"]
```

Every import check passed:

```json
{
  "date_matches": true,
  "source_report_matches": true,
  "source_date_matches": true,
  "source_run_matches": true,
  "context_hash_matches": true,
  "schema_matches": true,
  "chat_mode": true,
  "provider_present": true,
  "not_fallback": true,
  "validation_status": true,
  "structural_indicators_preserved": true,
  "linked_indicators_preserved": true
}
```

The import workflow build and Pages deploy both completed successfully. The deployed Pages artifact was inspected directly:

```text
executive summary: 6
key findings: 7
future trends: 3
translations: 173
structural indicators: 3
linked indicators: 6
supplemental evidence: 0
```

Deployed provenance:

```json
{
  "effective_mode": "chat-assisted",
  "fallback_used": false,
  "generated_at": "2026-08-17T07:18:00+00:00",
  "model": "GPT-5.6 Pro",
  "prompt_version": "daily-analysis-v1.2",
  "provider": "OpenAI ChatGPT",
  "requested_mode": "chat-assisted",
  "schema_version": "ai-analysis/v1",
  "source_context_hash": "5fae7ea3c94089d2f9912dda781f325fd6871b7aae9728d869411fd82bd12858",
  "source_report_date": "2026-08-17",
  "source_run_id": "run_9a871b96bda9",
  "validation_status": "valid"
}
```

The generated `/analysis` HTML contains the expected `GPT-5.6 Pro` / `OpenAI ChatGPT` byline and final analysis text. Translations, structural indicators and linked indicators were hydrated from the immutable deterministic baseline.

## Remaining honest gaps

- `credential_unavailable` · `freshrss_google_reader` · missing FreshRSS credentials: FRESHRSS_BASE_URL, FRESHRSS_USERNAME, FRESHRSS_API_PASSWORD
- `competitor_monitor_incomplete` · `fixed_official_channels` · official competitor monitor incomplete: failed=1, partial=0, not_executed=0

These are explicit boundaries, not silent successes:

```text
FreshRSS credentials remain owner-provided.
WACA direct automation remains incomplete.
Generic web/API/social/GDELT extraction remains not_executed until source-specific rules exist.
Authenticated X / Meta / Threads / Instagram APIs remain unconnected.
Typed competitor history in RadarReportV2/runtime remains follow-up.
Seven Retail matrix cells remain insufficient.
Two canonical structural indicators remain insufficient.
```

## Final judgment

The runtime now has a safe indicator-only measurement lane, stable-URL material-delta protection, conservative same-run coalescing, differentiated confidence scoring, direct Taiwan source traceability, a formal 8/8 Crypto matrix and a validated chat-assisted analysis bound to the exact deployed report.

The report correctly remains `partial` because FreshRSS, WACA and generic unimplemented channels are incomplete. That status is evidence honesty, not a deployment failure.
