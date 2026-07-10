# Source Policy

`config/source_registry.json` is the canonical source registry.
The old `config/source_registry.yaml` path is retired because its contents were JSON and the extension misled maintainers.
Legacy source files under `sources/` remain compatibility inputs until they are regenerated as projections.

Rules:

- One real-world source has one `source_id`.
- RSS, API, web, RSSHub, social and discovery routes are adapters under that source, not separate identities.
- `FRESHRSS_SEEDS.opml` is generated from adapters with `enabled_for_opml=true`.
- RSSHub and FreshRSS are collection channels, not evidence stores.
- GDELT, Media Cloud, Event Registry and NewsCatcher are discovery or benchmark tools.
- Final facts must resolve to original URLs, official data, company releases, regulators or credible media.
- Full text is not committed. Store URL, title, timestamps, hash, summary, provenance and allowed snippets only.
- Taiwan direct evidence and Taiwan implication are separate fields.
- Unavailable, stale or blocked adapters become coverage gaps, not `no news`.
- Social-first sources require direct channel verification or an explicit inaccessible status.
- Registry entries marked `runtime_test_required` are not considered healthy until a live adapter check passes.
