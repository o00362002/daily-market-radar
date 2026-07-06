# Feed Stack Sync Status｜2026-07-07

## Completed

```text
CURRENT_DECISIONS.md
DEPENDENCY_MAP.md
SOURCE_LIBRARY_SPEC.md
AGENT_DEFINITION_MAP.md
sources/channel_feed_sources.json
FRESHRSS_SEEDS.md
FRESHRSS_SEEDS.opml
```

## Route verification result

```text
YouTube route template: verified in upstream RSSHub route code as /youtube/channel/:id.
Telegram route template: verified in upstream RSSHub route code as /telegram/channel/:username.
Threads route template: verified in upstream RSSHub route code as /threads/:user.
Picnob route template for Instagram-like public profiles: verified in upstream route code as /picnob.info/user/:id, but kept disabled because runtime support and concrete account testing are required.
GitHub releases candidate: previous /github/repos/DIYgod/RSSHub/releases was not verified as a valid RSSHub route, so GitHub official releases.atom is used instead.
```

## OPML status

```text
FRESHRSS_SEEDS.opml exists.
It includes only verified seed entries.
Enabled OPML seed entries are aligned with sources/channel_feed_sources.json:
- rsshub_project_github_releases_atom
- rsshub_youtube_route_smoke_seed
```

## Source-of-truth sync

```text
CURRENT_DECISIONS.md records the 2026-07-07 feed stack decision.
DEPENDENCY_MAP.md includes Shared Feed Stack Gate and Feed stack status fields.
SOURCE_LIBRARY_SPEC.md includes feed stack layer, provider roles, fetch priority, and coverage audit fields.
AGENT_DEFINITION_MAP.md includes feed stack dependencies and route/audit boundaries.
```

## Remaining manual checks

```text
1. Run RSSHub + FreshRSS locally.
2. Import FRESHRSS_SEEDS.opml into FreshRSS.
3. Confirm FreshRSS can refresh both enabled feeds.
4. Replace smoke-test route entries with real market-radar sources only after concrete accounts are chosen and route output is tested.
5. Keep route templates disabled until verified concrete source entries exist.
```
