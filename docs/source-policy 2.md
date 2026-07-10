# Source Policy

`config/source_registry.yaml` is the canonical source registry. Legacy source
files under `sources/` remain as historical inputs and compatibility references
until they are regenerated as projections.

Rules:

- One real-world source has one `source_id`.
- RSS, API, web, RSSHub, social, and discovery routes are adapters under that
  source, not separate source identities.
- RSSHub and FreshRSS are channel adapters, not evidence stores.
- GDELT, Media Cloud, Event Registry, and NewsCatcher are discovery or benchmark
  tools. Final facts must resolve to original URLs, official data, company
  releases, regulators, or credible media.
- Full text is not committed to Git. Save URL, title, timestamps, hash, summary,
  provenance, and allowed snippets only.
- Taiwan direct evidence and Taiwan implication are separate fields.
- Unavailable feeds become coverage gaps, not "no news".
