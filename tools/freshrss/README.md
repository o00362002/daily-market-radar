# FreshRSS API Tools

This folder contains local tools for connecting the self-hosted FreshRSS inbox to `daily-market-radar`.

## Secret handling

Do not commit FreshRSS credentials.

Use local environment variables:

```bash
export FRESHRSS_BASE_URL="http://localhost:8080"
export FRESHRSS_DEFAULT_USER="<your-freshrss-user>"
export FRESHRSS_API_PASSWORD="<your-freshrss-api-password>"
```

FreshRSS API access must be enabled in the FreshRSS user profile. FreshRSS uses a dedicated API password for mobile/API clients, not necessarily the normal login password.

## Pull candidates

```bash
python3 tools/freshrss/greader_pull_candidates.py
```

Output:

```text
data/freshrss/feed_candidates_latest.json
```

The output file is a local runtime artifact. It should be treated as an input candidate pool for Daily Push Brief and should not be treated as confirmed evidence by itself.

## Boundary

```text
FreshRSS API = candidate pull layer
Daily Push Brief = selection, dedupe, evidence trace, freshness, Taiwan-news validation
```

Do not use FreshRSS summaries as final facts. Always keep original URLs and evidence checks.
