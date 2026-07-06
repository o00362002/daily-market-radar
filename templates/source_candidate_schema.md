# Source Candidate Schema

Purpose: normalize discovered sources before they are promoted into long-term tracked sources.

A source candidate is not automatically a trusted source. It must be scored, checked, and either promoted, reviewed, or rejected.

---

## Candidate object

```yaml
source_candidate_id: "candidate::<domain>::<name_slug>"
name: ""
source_type: "official_newsroom | official_rss | government_source | data_provider | media_source | rsshub_public_channel | social_public_account | company_ir | retail_brand_source"
source_url: ""
potential_feed_url: null
rsshub_path_candidate: null

candidate_status: "discovered | scored | review_queue | promoted | rejected"
promotion_status: "not_promoted | auto_promoted | manual_promoted | blocked"
review_required: true

region: "global | taiwan | multi"
languages:
  - en
domain_ids:
  - ai_agents_workflow

score: 0
score_reasons:
  - ""

checks:
  source_identity_verified: false
  feed_or_api_verified: false
  route_runtime_verified: false
  original_information_density_checked: false
  duplicate_source_checked: false
  domain_mapping_checked: false
  legal_or_access_risk_checked: false

promotion_decision:
  action: "keep_candidate | promote_to_registry | enable_opml | reject"
  reason: ""
  decided_at: null
  decided_by: "system | user | agent"

observed_from:
  - "manual_seed"
  - "query_recipe"
  - "fresh_rss_candidate"
  - "gdelt"
  - "media_cloud"

notes: ""
```

---

## Promotion boundary

```text
Auto-discovery can be broad.
Auto-promotion must be narrow.
Official RSS, official government feeds, and verified data feeds may auto-promote after checks.
Social accounts, RSSHub routes, unknown media, and unstable pages require review before enabling OPML.
```

---

## Required rejection reasons

```text
unknown_identity
login_required
no_original_information
duplicate_source
unstable_route
low_signal_density
not_relevant_to_current_domains
unsafe_or_disallowed_access
```
