# AIAnalysisV1

`AIAnalysisV1` is a separate interpretation layer over validated `RadarReportV2` data.
It never replaces or mutates the source report.

## Responsibilities

```text
RadarReportV2 validated facts
→ faithful headline translation
→ cross-event daily synthesis
→ conditional future-trend scenarios
→ deterministic linked indicators
→ AI interpretation of immutable indicator values
→ AIAnalysisV1 web artifact
```

The `/analysis` page keeps the following content types visibly separate:

- verified facts
- AI relationship inference
- background context
- early hypotheses
- uncertainty and follow-up verification

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

## Linked indicators

Indicator values are calculated by deterministic code from validated report fields.
The model may explain an indicator but cannot change its score, previous score, delta,
direction, status, method, components or source event ids.

Initial indicators:

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

These scores describe signal strength and evidence conditions. They do not prove causality,
market direction or investment returns.

## Evaluation modes

- `deterministic`: no model call; produces a complete fallback analysis.
- `auto`: uses OpenAI when `OPENAI_API_KEY` is available, otherwise deterministic fallback.
- `api-assisted`: requests OpenAI enhancement and falls back safely on provider or validation failure.

OpenAI receives only a bounded JSON payload containing report items, matrices, structural
indicators, linked indicators and coverage gaps. It never receives secrets or full article bodies.
Output is constrained to a typed schema and revalidated against allowed event and indicator ids.

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
