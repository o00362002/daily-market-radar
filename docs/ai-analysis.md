# AIAnalysisV1

`AIAnalysisV1` is a separate interpretation layer over validated `RadarReportV2` data.
It never replaces or mutates the source report.

## Responsibilities

```text
RadarReportV2 validated facts
→ faithful headline translation
→ cross-event daily synthesis
→ three canonical structural indicators as the primary trend panel
→ conditional future-trend scenarios
→ six deterministic auxiliary signal indicators
→ AI interpretation of immutable auxiliary values
→ AIAnalysisV1 web artifact
```

The `/analysis` page keeps the following content types visibly separate:

- verified facts
- AI relationship inference
- background context
- early hypotheses
- uncertainty and follow-up verification
- canonical structural trend indicators
- auxiliary daily signal indicators

## Indicator hierarchy

The project has two distinct indicator layers. They must not be merged or described as equivalents.

### Primary: three canonical structural indicators

These are defined by `config/runtime_contract.json` and detailed in
`configs/structural_trend_indicators.yml`:

1. `k_shaped_ai_productivity_economy`
   - 生產力便車無法共享的 K 型經濟
2. `ai_bubble_overinvestment`
   - AI 泡沫 / 過度投資趨勢
3. `brand_market_polarization_and_true_vs_fake_segmentation`
   - 品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾

`AIAnalysisV1.structural_indicators` is an ordered, labelled projection of the same
`RadarReportV2.structural_indicators` observations. Direction, support score, counter score,
confidence, signal IDs, missing data, interpretation and next verification are immutable.
The AI provider may use them when synthesising the day, but cannot edit or replace them.

The authoritative human-readable index is `docs/structural-indicators.md`.

### Secondary: six auxiliary signal indicators

`AIAnalysisV1.linked_indicators` remains for backward compatibility, but the website labels it
**輔助訊號面板**. These values describe daily signal strength and evidence conditions:

- AI application momentum
- retail change momentum
- crypto and RWA adoption momentum
- Taiwan direct exposure intensity
- cross-domain convergence
- evidence confidence

Domain/Taiwan momentum uses:

```text
importance average 30%
+ potential average 30%
+ confidence average 25%
+ event breadth 15%
```

Cross-domain convergence uses domain breadth, potential-item ratio and average confidence.
Evidence confidence uses average confidence and source breadth, minus coverage-gap and
source-failure penalties.

Directions compare the latest report with the previous report of the same profile:

- delta >= 5: up
- delta <= -5: down
- otherwise: flat
- no prior baseline: new
- no qualifying data: insufficient

These scores do not prove causality, market direction or investment returns, and they must not
be presented as replacements for the three structural indicators.

## Provenance

Every analysis records:

- provider and model
- generation time
- source report date and run id
- source context hash
- prompt version
- schema version
- requested and effective mode
- validation and fallback status

## Evaluation modes

- `deterministic`: no model call; produces a complete fallback analysis.
- `auto`: uses OpenAI when `OPENAI_API_KEY` is available, otherwise deterministic fallback.
- `api-assisted`: requests OpenAI enhancement and falls back safely on provider or validation failure.

OpenAI receives only a bounded JSON payload containing report items, matrices, the three
structural indicators, auxiliary signal indicators and coverage gaps. It never receives secrets
or full article bodies. Output is constrained to a typed schema and revalidated against allowed
event and auxiliary-indicator ids.

## Automation

`.github/workflows/ai-analysis.yml` runs after successful `daily-intelligence` or `import-chat` runs:

```text
restore radar-state
→ export validated web artifacts
→ reject failed/fixture production deployment
→ generate AIAnalysisV1
→ Astro typecheck/build
→ deploy GitHub Pages
```

Optional variables:

```text
OPENAI_ANALYSIS_MODEL
RADAR_AI_ANALYSIS_MODE
```

`OPENAI_MODEL` remains the fallback model setting when `OPENAI_ANALYSIS_MODEL` is absent.
