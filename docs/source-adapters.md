# Source Adapters & Deterministic Evaluation

Every network adapter depends on the `HttpTransport` seam (`radar/adapters/transport.py`), never on urllib/requests directly, so adapters are unit-testable offline. The real `UrllibHttpTransport` enforces bounded response size, SSRF policy on the initial URL and every redirect hop, a redirect cap and conditional request support.

## Runtime collection modes

| Mode | Connected adapters |
|------|--------------------|
| `fixture` | deterministic fixtures only |
| `live-rss` | direct registry RSS / Atom only |
| `live` | direct registry RSS / Atom + optional FreshRSS reading-list inbox |

`live` uses `CompositeSourceAdapter` to isolate child failures and merge canonical `SourceFetchResult` values. One provider failure never stops the other configured providers.

## Adapter inventory

| Adapter | Module | Runtime status |
|---------|--------|----------------|
| RSS/Atom | `adapters/rss.py`, `adapters/rss_client.py` | Connected to `live-rss` and `live`. |
| FreshRSS | `adapters/freshrss.py`, `adapters/freshrss_source.py` | Connected to `live`; credential-gated. Items map from `origin.streamId` to canonical registry RSS URLs. Missing credentials, fetch failures and unknown streams become explicit gaps. |
| Composite | `adapters/composite.py` | Connected to `live`; fans out, isolates failures and merges documents/audit/gaps. |
| Safe Web | `adapters/safe_web.py` | Lower-level implementation complete; not generically connected because each site still needs source-specific list/detail extraction rules. |
| Generic JSON API | `adapters/json_api.py` | Lower-level implementation complete; not generically connected because current registry API entries do not yet carry executable endpoint, item path, pagination and field mappings. |
| GDELT discovery | `adapters/gdelt_discovery.py` | Discovery-only implementation complete; not connected until bounded coverage queries and original-publisher verification are defined. Never final evidence. |
| Social direct channels | `adapters/social_channels.py` | Public-channel and official-API interfaces exist; authenticated X/Meta/Threads/Instagram clients and credentials remain unconnected. Generic web results never count as direct checks. |

## FreshRSS contract

Environment:

```text
FRESHRSS_BASE_URL
FRESHRSS_USERNAME
FRESHRSS_API_PASSWORD
```

Behavior:

```text
credentials missing
→ collection_aggregator=credential_unavailable
→ direct RSS continues

known origin.streamId
→ map feed URL to source_registry source_id
→ emit canonical Document

unknown origin.streamId
→ do not invent source_id
→ emit freshrss_stream_unmapped coverage gap
```

Direct RSS and FreshRSS can observe the same article. Downstream canonical URL/content de-duplication removes the duplicate before event resolution.

## Safe Web policy

`adapters/safe_web.py` is registry-allowlist only. It blocks localhost, private/link-local/cloud-metadata IPs, unsupported schemes, excessive redirects, oversized responses and disallowed content types. It stores only bounded metadata/excerpts, never bypasses paywalls or logins, and never becomes an arbitrary crawler.

## Source health

`radar/domain/source_health.py` is a deterministic state machine over:

```text
healthy
stale
empty
silent_zero
failing
policy_blocked
credential_unavailable
rate_limited
```

It records `checked_at`, `last_success_at`, `last_item_at`, `consecutive_failures`, `response_count`, `latency_ms`, `failure_reason` and `retry_at`. `SqliteSourceHealthRepository` persists source health.

## Deterministic evaluators

`radar/evaluators/matrices.py` provides feature-traced Retail, Crypto and structural evaluation:

- Matrix cells become `observed` only when canonical measurements or defined evidence features are present.
- Otherwise they remain `insufficient` with an explicit gap.
- Structural indicators use only real supporting/counter evidence.
- Rolling current/7d/30d/90d windows aggregate stored observations only; empty windows never become fabricated trends.
