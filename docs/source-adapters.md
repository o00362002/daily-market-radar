# Source Adapters & Deterministic Evaluation (PR C)

Every network adapter depends on the `HttpTransport` seam (`radar/adapters/transport.py`),
never on urllib/requests directly, so all adapters are fully unit-testable offline with a fake
transport. The real `UrllibHttpTransport` enforces a bounded response size, an SSRF allow/deny policy
on the initial URL and on every redirect hop, a hard redirect cap, and conditional requests.

## Adapters

| Adapter | Module | Notes |
|---------|--------|-------|
| RSS/Atom (hardened) | `adapters/rss_client.py` | ETag / Last-Modified conditional fetch, deterministic exponential backoff + injectable jitter, per-feed retry isolation. Legacy `adapters/rss.py` remains for the live-rss composition. |
| FreshRSS | `adapters/freshrss.py` | Google Reader API (ClientLogin, reading-list pagination). Credential-gated via `FRESHRSS_BASE_URL` / `FRESHRSS_USERNAME` / `FRESHRSS_API_PASSWORD`; **missing creds → unavailable, never crashes**. |
| Safe Web | `adapters/safe_web.py` | Registry allowlist only; blocks localhost / private / link-local / cloud-metadata IPs / disallowed schemes / excessive redirects / oversized responses / disallowed content types. Bounded excerpt + canonical URL + content hash. Never bypasses paywalls/logins, never stores full articles, never becomes an arbitrary crawler. |
| Generic JSON API | `adapters/json_api.py` | Registry-driven: endpoint, GET, query params, secret env, page + cursor pagination, item path, field mapping, bearer/query token. Missing credential → graceful degradation. |
| GDELT discovery | `adapters/gdelt_discovery.py` | **Discovery only.** Every entry resolves to original publisher + URL + a registry/temporary identity + a verification status. Never final evidence (`is_final_evidence` is always `False`). |
| Social direct channels | `adapters/social_channels.py` | Public RSS/Atom/YouTube are direct-checked. X / Meta / Threads / Instagram get an official-API adapter **interface** only; without credentials they are unavailable. A generic web result is never marked `direct_checked`. |

## Source health

`radar/domain/source_health.py` is a pure, deterministic state machine over the eight statuses
(`healthy`, `stale`, `empty`, `silent_zero`, `failing`, `policy_blocked`, `credential_unavailable`,
`rate_limited`). It records `checked_at`, `last_success_at`, `last_item_at`, `consecutive_failures`,
`response_count`, `latency_ms`, `failure_reason` and `retry_at` (exponential backoff on failure/rate
limit). `SqliteSourceHealthRepository` persists one row per source (migration `0005_source_health.sql`).

## Deterministic evaluators (wired into the live pipeline)

`radar/evaluators/matrices.py` replaces the previous always-`insufficient` matrices with
**feature-traced** evaluation, wired into `DeterministicIntelligenceEvaluator`:

- Retail and Crypto matrix cells are `observed` only when a canonical measurement metric or a keyword
  trigger is found in the run's events; the `data_checked` trace records exactly which features fired.
  Otherwise the cell is `insufficient` with an explanatory gap. **No cell ever gets a fixed score.**
- Structural indicators score support/counter from keyword evidence with a feature trace; with no
  evidence they are `insufficient` — **no fabricated trend**.
- `rolling_summary(...)` aggregates stored observations into current / 7d / 30d / 90d windows using only
  real observations; an empty window is `insufficient`, not invented.
