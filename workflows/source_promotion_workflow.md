# Source Promotion Workflow

Purpose: automatically discover, score, and propose long-term sources based on user needs, search results, FreshRSS candidates, GDELT, Media Cloud, and repeated useful items.

This workflow prevents the source library from becoming manual-only while still protecting quality.

---

## Execution position

```text
Daily Push Brief / News Search / Full Daily Radar
→ candidate news discovery
→ source extraction
→ source candidate scoring
→ source promotion decision
→ registry / OPML update if allowed
```

---

## Required files

```text
configs/source_promotion_rules.yml
templates/source_candidate_schema.md
memory/source_candidate_registry.json
sources/channel_feed_sources.json
FRESHRSS_SEEDS.opml
configs/freshrss_ingestion.yml
```

---

## Input signals

```text
1. Repeated useful search results from query recipes.
2. Sources appearing repeatedly in GDELT or Media Cloud discovery.
3. Sources behind accepted FreshRSS candidates.
4. Official pages found while verifying claims.
5. User-requested source themes or named source targets.
```

---

## Minimum loop

```text
1. Extract source domain and source identity from accepted or repeated candidate items.
2. Check whether the source already exists in source library or channel_feed_sources.json.
3. If new, create a source_candidate using templates/source_candidate_schema.md.
4. Score source candidate with configs/source_promotion_rules.yml.
5. If high-confidence official feed passes checks, promote to registry and OPML.
6. If social, unstable, unknown, or RSSHub route source, put into review_queue.
7. If low quality or duplicate, reject with reason.
8. Record all decisions in memory/source_candidate_registry.json.
```

---

## Auto-promotion rule

Auto-promote only when all are true:

```text
source identity is official or trusted data source
feed or API URL is verified
source maps to at least one core domain
source is not duplicate
score >= auto_promote threshold
access does not require login or private content
```

---

## Review-required rule

Keep in review queue when any are true:

```text
source is a social account
source depends on RSSHub route runtime validation
source has no verified feed yet
source is useful but not official
source has unclear identity
source overlaps with existing media source
```

---

## Output actions

```text
keep_candidate = keep watching but do not promote
promote_to_registry = add to sources/channel_feed_sources.json or official source library
enable_opml = add verified feed to FRESHRSS_SEEDS.opml
reject = do not track long-term
```

---

## Audit output

Daily runs should internally track:

```text
source_candidates_checked
source_candidates_created
source_candidates_promoted
source_candidates_rejected
auto_promotions
review_required_candidates
promotion_gaps
```

---

## Safety boundary

```text
Do not auto-add login-required, private, unstable, unknown-identity, spam, or no-original-information sources.
Do not let discovery tools become final evidence.
GDELT and Media Cloud discover sources and events; original sources still need verification.
```
