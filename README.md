# Daily Market Radar

`daily-market-radar` is a deterministic-first global event-intelligence runtime, evidence archive and static dashboard. It tracks important current events, future-potential signals and material changes across global markets, AI, crypto, retail/fashion and technology. Product/social competitor intelligence is a fixed cross-domain projection; labor and consumption pressure are indicator-only by default.

## What is connected

```text
Source registry + competitor registry
→ direct RSS / Atom
→ optional FreshRSS Google Reader inbox
→ fixed product/social competitor checks
→ normalization and document de-duplication
→ cross-day event resolution
→ material-delta filtering
→ deterministic / optional AI / chat-assisted evaluation
→ strict RadarReportV2
→ competitor projection + fixed indicator panels
→ SQLite durable state
→ versioned web projection
→ Astro static dashboard
→ scheduled GitHub Actions deployment
```

The application depends on provider-neutral ports. Concrete RSS, FreshRSS, OpenAI, SQLite, filesystem and publishing implementations are selected only by the composition root.

## Runtime principles

```text
source registry before generic search
competitor registry before ad-hoc competitor keywords
one real source = one source_id
RSS/API/web/RSSHub/social = adapters
one event = one primary report domain
importance, future potential and evidence confidence are independent
Major/Potential is content-driven, not source-role routing
competitor watch = projection, not a sixth domain or duplicate event
labor / hiring / wages / consumption pressure = indicator-only by default
Taiwan direct evidence != Taiwan implication
item floors are minimums, never ceilings
coverage gaps must be visible
fixture replay != live-news coverage
```

## Canonical news domains

The current `config/runtime_contract.json` defines five canonical news domains:

```text
global_markets_macro
ai_agents_applications
crypto_rwa_agent_payments
retail_consumer_fashion
science_technology_industry
```

The retired labor-domain identifier remains only as a backward-compatible alias. Labor and consumption pressure normally render in the final indicator panel; an independently material event may appear once under AI, macro, retail or technology.

## Three canonical structural indicators

These are the project's long-term primary direction meters. They are mandatory in every `RadarReportV2` and appear first on the `/analysis` page:

```text
k_shaped_ai_productivity_economy
  生產力便車無法共享的 K 型經濟

ai_bubble_overinvestment
  AI 泡沫 / 過度投資趨勢

brand_market_polarization_and_true_vs_fake_segmentation
  品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾
```

Canonical IDs live in `config/runtime_contract.json`; detailed supporting, counter and evidence requirements live in `configs/structural_trend_indicators.yml`; the human-readable index is `docs/structural-indicators.md`.

The six AI/retail/crypto/Taiwan/convergence/evidence scores in `AIAnalysisV1.linked_indicators` are auxiliary daily signal indicators. They do not replace the three structural indicators.

## Competitor Intelligence

```text
config/competitor_registry.json       canonical product/social identities and aliases
configs/competitor_intelligence.yml   collection and projection policy
memory/watchlist.md                    owner-approved fixed watch intent
web/src/pages/competitors.astro        product/social competitor page
```

A competitor update must have a fresh material delta and verified evidence. Completed checks with no delta render `已查無重大更新`; incomplete checks render `未完整查證`. Old competitor news is never replayed to fill the section.

## Install and validate

Python 3.12+ is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make validate
radar sources validate
radar sources health
```

## Run modes

### Fixture contract check

```bash
radar run-daily \
  --mode fixture \
  --profile daily_push \
  --evaluation-mode deterministic \
  --date "$(TZ=Asia/Taipei date +%F)" \
  --database data/radar.db
```

Fixture mode is never evidence of live-news completeness.

### Direct RSS / Atom only

```bash
radar run-daily \
  --mode live-rss \
  --profile daily_push \
  --evaluation-mode deterministic \
  --date "$(TZ=Asia/Taipei date +%F)" \
  --database data/radar.db
```

### Connected live collection

```bash
radar run-daily \
  --mode live \
  --profile daily_push \
  --evaluation-mode auto \
  --date "$(TZ=Asia/Taipei date +%F)" \
  --database data/radar.db
```

`live` executes direct RSS/Atom and the optional FreshRSS collection inbox. Missing FreshRSS credentials are reported as a coverage gap and never stop direct RSS. Duplicate URLs collected through both paths are removed before event resolution.

## Evaluation modes

```text
deterministic  no AI import or API key; valid report with insufficient where evidence is absent
auto           API enhancement when OPENAI_API_KEY exists, deterministic fallback otherwise
api-assisted  explicitly request bounded OpenAI structured enhancement
chat-assisted deterministic run followed by prepare-chat / import-chat
```

Deterministic system narratives use Taiwan Traditional Chinese. Without an AI key, foreign-language source headlines remain in the original language. API/chat-assisted translation must preserve the original headline and may not alter names, products, numbers, dates, URLs or evidence ids.

## Potential candidate retention

```text
daily_push Major      homepage highlights up to 3 items per domain
daily_push Potential  all qualified candidates retained in report data
homepage Potential    top 3 per domain highlighted, complete pool remains visible
full                  all qualified items within the run budget
```

Potential is determined by content features such as pilots, prototypes, new applications, business-model changes, cross-domain combinations, adoption/diffusion and material deltas. Source role is only a supporting feature.

## Build the website

```bash
radar export-web --out-dir "$PWD" --database data/radar.db
cd web
npm ci
npm run types:check
npm run build
npm run dev
```

The local development site is normally available at `http://localhost:4321`.

## Automation

`.github/workflows/daily-intelligence.yml` runs daily at `0 23 * * *` UTC, equivalent to 07:00 Asia/Taipei. It restores the `radar-state` branch, runs `--mode live`, exports web artifacts, builds Astro, deploys validated non-fixture output and persists compressed/checksummed SQLite state.

Owner-side GitHub settings:

```text
Settings → Pages → Source = GitHub Actions
Settings → Actions → General → Workflow permissions = Read and write
```

## Optional configuration

See `.env.example` and `docs/secrets.md`.

```text
OPENAI_API_KEY / OPENAI_MODEL / OPENAI_MAX_*
FRESHRSS_BASE_URL / FRESHRSS_USERNAME / FRESHRSS_API_PASSWORD
DATABASE_URL
RADAR_EVALUATION_MODE
```

No secrets are required for deterministic RSS collection, report generation, website build or deployment.

## Honest current boundary

Connected now:

```text
RSS / Atom
FreshRSS inbox when configured
cross-day event history and material delta
Retail / Crypto / three structural deterministic evaluators
canonical competitor registry and registry-backed web projection
labor/consumption indicator-only policy
optional API and chat-assisted evaluation
SQLite state, web projection, Astro and daily automation
```

Not yet safe to execute generically from the current registry:

```text
web-page watches that require source-specific extraction rules
JSON/API sources without executable endpoint + pagination + field mappings
GDELT gap discovery queries and original-source verification workflow
authenticated X / Meta / Threads / Instagram official APIs
typed competitor payload and durable competitor-history table in RadarReportV2/runtime
```

These remain explicit coverage gaps. They are not silently treated as checked, and the current system must not claim complete global or competitor coverage.
