# Source Adapters & Deterministic Evaluation

Every network adapter depends on the `HttpTransport` seam (`radar/adapters/transport.py`), never on urllib/requests directly, so adapters are unit-testable offline. The real `UrllibHttpTransport` enforces bounded response size, SSRF policy on the initial URL and every redirect hop, a redirect cap, conditional request support and a method allowlist. The request body seam exists only for bounded read-only public APIs such as Hyperliquid's information endpoint.

## Runtime collection modes

| Mode | Connected adapters |
|------|--------------------|
| `fixture` | deterministic fixtures only |
| `live-rss` | direct registry RSS 2.0 / RSS 1.0 RDF / Atom only |
| `live` | direct registry RSS / Atom + optional FreshRSS inbox + fixed public structured measurements |

`live` uses `CompositeSourceAdapter` to isolate child failures and merge canonical `SourceFetchResult` values. One provider failure never stops the other configured providers.

## Adapter inventory

| Adapter | Module | Runtime status |
|---------|--------|----------------|
| RSS 2.0 / RSS 1.0 RDF / Atom | `adapters/rss.py`, `adapters/rss_client.py` | Connected to `live-rss` and `live`; namespaced RDF fields and Taiwan naïve timestamps are normalized. |
| FreshRSS | `adapters/freshrss.py`, `adapters/freshrss_source.py` | Connected to `live`; credential-gated. Items map from `origin.streamId` to canonical registry RSS URLs. Missing credentials, fetch failures and unknown streams become explicit gaps. |
| Structured measurements | `adapters/measurements.py`, `src/radar/schemas/measurement.py` | Connected to `live` through `config/measurement_sources.json`; every source emits `indicator_only` typed facts and is isolated from sibling failures. |
| BLS productivity/distribution | `adapters/measurements.py` | Official public API. Aligns nonfarm-business productivity, real hourly compensation and labor-share series to one latest quarter and one event. |
| DefiLlama protocol economics | `adapters/measurements.py` | Specialist public API. Collects fixed Hyperliquid TVL, 24h fees and 24h revenue. |
| Hyperliquid perpetuals | `adapters/measurements.py`, `adapters/transport.py` | Official read-only `POST /info` `metaAndAssetCtxs`. Produces 24h notional volume, notional OI and OI-weighted current funding; no trading endpoint is used. |
| Farside Bitcoin ETF flows | `adapters/fixed_crypto_measurements.py` | Fixed specialist HTML table. Parses only the latest dated aggregate U.S. spot Bitcoin ETF flow; Farside is never promoted to official evidence. |
| Taiwan FSC VASP law | `adapters/fixed_crypto_measurements.py` | Fixed official law record. Parses publication date, implementation status and a bounded numeric revision fingerprint for direct Taiwan regulation evidence. |
| Composite | `adapters/composite.py` | Connected to `live`; fans out, isolates failures and merges documents/audit/gaps. |
| Safe Web | `adapters/safe_web.py` | Lower-level implementation complete; not generically connected because each site still needs source-specific list/detail extraction rules. |
| Generic JSON API | `adapters/json_api.py` | Lower-level implementation complete; not generically connected because current registry API entries do not yet carry executable endpoint, item path, pagination and field mappings. |
| GDELT discovery | `adapters/gdelt_discovery.py` | Discovery-only implementation complete; not connected until bounded coverage queries and original-publisher verification are defined. Never final evidence. |
| Social direct channels | `adapters/social_channels.py` | Public-channel and official-API interfaces exist; authenticated X/Meta/Threads/Instagram clients and credentials remain unconnected. Generic web results never count as direct checks. |

## Structured-measurement contract

The registry is separate from the news source registry:

```text
config/measurement_sources.json
→ typed MeasurementRegistry validation
→ fixed adapter and allowlisted endpoint
→ canonical numeric facts + source_roles
→ lane=indicator_only
→ Crypto matrix / structural indicators
```

Rules:

```text
measurement period may predate today's news window
but the event must be new, materially changed or anchored to today's Taiwan date

stable canonical URL + changed typed facts
→ material indicator delta

stable canonical URL + unchanged typed facts
→ duplicate / no new daily vote

indicator_only
→ may fill matrices and structural indicators
→ never becomes Major/Potential news or a potential signal
```

HTML measurement adapters persist only typed facts and a bounded summary. They do not retain the full Farside or FSC page. Provider-specific JSON is normalized before entering `Document.facts`; non-numeric provider fields are rejected.

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
→ direct RSS and public structured measurements continue

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
- Structural indicators use only real supporting/counter evidence that passes domain, proposition and measurement gates.
- Rolling current/7d/30d/90d windows aggregate stored observations only; empty windows never become fabricated trends.
- Indicator-only measurements can support these evaluators without increasing Major/Potential item counts.
