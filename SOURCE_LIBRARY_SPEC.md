# SOURCE_LIBRARY_SPEC v2

This file explains the source-first method. Machine source identity lives in `config/source_registry.json`.

## 1. Canonical model

```text
one real-world source = one source_id
RSS / Atom / API / web / RSSHub / social = adapters under the source
FRESHRSS_SEEDS.opml = generated projection
legacy sources/ files = compatibility inputs, not canonical identity
```

Do not maintain the same source independently in several registries.

## 2. Collection order

```text
1. Load route and canonical report domain.
2. Load config/runtime_contract.json.
3. Validate config/source_registry.json.
4. Check source and adapter health.
5. Ingest top-down official/data/company/national sources.
6. Ingest bottom-up research, local, startup, developer, social and niche sources.
7. Use fixed query recipes to filter or expand collected items.
8. Use external discovery only for failed coverage cells.
9. Resolve discovery results to original evidence.
10. Normalize, de-duplicate and event-cluster.
11. Emit coverage audit and explicit gaps.
```

Generic web search is fallback and discovery. It does not prove source-library or direct-channel coverage.

## 3. Source record fields

Canonical source fields:

```text
source_id
name
canonical_url
publisher_country
macro_region
languages
source_roles
domains
ownership_profile
evidence_profile
priority
adapters
fetch_interval_minutes
freshness_slo_minutes
usage_policy
fulltext_policy
enabled
verification_status
last_verified_at
aliases
```

Adapter fields:

```text
kind: rss / api / web / rsshub / social
url
route_status
enabled_for_opml
opml_category
```

The actual schema is enforced by `src/radar/schemas/source.py` and tests.

## 4. Evidence boundary

```text
adapter success != factual verification
FreshRSS item != evidence store
RSSHub route != source identity
GDELT / Media Cloud / Event Registry / NewsCatcher result != final claim
social post != high evidence by default
```

Important claims should resolve to official/data sources, company releases, regulators, exchanges, research methods or credible original reporting.

## 5. Taiwan boundary

Taiwan coverage must distinguish:

```text
direct_taiwan_evidence
taiwan_implication
```

Generic implications do not satisfy Taiwan coverage. Social-first Taiwan sources require a direct channel check or an explicit inaccessible/unverified status.

Taiwan crypto fixed-source probes and legislative triggers remain semantic policy under `configs/source_routing_rules.yml`; their real source identities should be promoted into the canonical registry only when exact canonical URLs or public channel URLs are verified.

## 6. Coverage dimensions

Coverage is audited by cells, not by a single source count:

```text
report domain
macro region
language
source role
channel / adapter kind
time window
health status
observed count
```

Statuses such as `empty`, `stale`, `failing`, `silent_zero` or `policy_blocked` create gap cards. They do not mean there was no news.

## 7. Report-domain coverage

Canonical report domains are read from `config/runtime_contract.json`.
Fine-grained entries in `configs/radars.yml` and `domains/` packs expand search coverage but must map to a canonical report domain unless the runtime contract itself changes.

## 8. OPML projection

Only enabled RSS/Atom adapters with `enabled_for_opml=true` are projected to `FRESHRSS_SEEDS.opml`.

Validation:

```bash
make source-opml
```

Changing the canonical registry without regenerating OPML is contract drift.

## 9. Source health

Track at adapter and source level:

```text
last success
last failure
last empty
failure count
freshness age
hit rate by domain
duplicate rate
policy/access status
content originality / false-positive notes
```

Sources may be promoted, demoted, disabled or moved to discovery-only based on repeated evidence.

## 10. Current runtime support

Implemented:

```text
registry validation
RSS 2.0 / RSS 1.0 RDF / Atom live adapter
RSS + optional FreshRSS composite live collection
OPML projection validation
fixture ingestion
coverage gaps for failed feeds
```

Not yet connected:

```text
web/API/social adapters
external discovery providers
fixed query recipes and coverage retry routing
full per-source health persistence
```

These unexecuted routes must be disclosed as degradation reasons.
