# Secrets Contract (PR F)

Every secret is **optional**. With no secrets configured:

- deterministic mode runs normally,
- the website is still generated,
- GitHub Pages still deploys,
- AIAnalysisV1 uses deterministic fallback,
- unavailable integrations are disclosed (coverage gaps + evaluation/analysis fallback metadata).

See [.env.example](../.env.example) for the full list.

## Optional secrets and variables

| Name | Purpose | Absent → |
|------|---------|----------|
| `OPENAI_API_KEY` | auto / api-assisted evaluation and AIAnalysisV1 enhancement | deterministic fallback |
| `OPENAI_MODEL` | default OpenAI model id | repository default model (only used when a key is present) |
| `OPENAI_ANALYSIS_MODEL` | optional model override for translation, synthesis, trend scenarios and indicator interpretation | falls back to `OPENAI_MODEL`, then repository default |
| `RADAR_AI_ANALYSIS_MODE` | `deterministic`, `auto`, or `api-assisted` for the separate analysis layer | `auto` |
| `OPENAI_MAX_DAILY_COST_USD` / `OPENAI_MAX_ITEMS_PER_RUN` / `OPENAI_MAX_INPUT_TOKENS_PER_RUN` | evaluation budget caps | unbounded per dimension |
| `FRESHRSS_BASE_URL` / `FRESHRSS_USERNAME` / `FRESHRSS_API_PASSWORD` | FreshRSS collection | adapter unavailable, coverage gap |
| `DATABASE_URL` | external state backend | durable state uses the `radar-state` branch |

The first AIAnalysisV1 release does not silently copy model output into the fact layer. It records provider,
model, source run, context hash, prompt/schema versions and fallback status. Linked-indicator values are
calculated deterministically; the model can only explain them.

## Redaction

`radar/observability/redaction.py` scrubs secrets from any string before it is logged or written into a
receipt. It removes both the actual env values and secret-shaped patterns: `Authorization:` headers,
`Bearer`/`GoogleLogin` tokens, `sk-…`/`ghp_…` keys, `scheme://user:password@host` connection strings, and
`apikey=`/`token=`/`password=` pairs. **Passwords, API keys, auth headers and database credentials are
never logged.** Tests live in `tests/unit/test_redaction.py`.

## Owner-required GitHub UI setup (one-time)

The code cannot configure these; the repository owner must set them in the GitHub UI:

1. **Settings → Secrets and variables → Actions → Secrets**: optionally add `OPENAI_API_KEY`,
   `FRESHRSS_BASE_URL`, `FRESHRSS_USERNAME`, `FRESHRSS_API_PASSWORD`, `DATABASE_URL`.
2. **Settings → Secrets and variables → Actions → Variables**: optionally add `RADAR_EVALUATION_MODE`,
   `RADAR_AI_ANALYSIS_MODE` (both default `auto`), `OPENAI_MODEL`, `OPENAI_ANALYSIS_MODEL`, and the
   `OPENAI_MAX_*` budget caps.
3. **Settings → Pages → Build and deployment → Source = GitHub Actions**.
4. Ensure Actions has **Read and write permissions** (Settings → Actions → General) so the daily job can
   push the `radar-state` branch.
5. (Optional) Enable OpenAI billing/API access if you want model-assisted evaluation and AI interpretation.
