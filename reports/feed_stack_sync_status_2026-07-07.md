# Feed Stack Sync Status｜2026-07-07

## Completed

```text
CURRENT_DECISIONS.md
DEPENDENCY_MAP.md
SOURCE_LIBRARY_SPEC.md
AGENT_DEFINITION_MAP.md
sources/channel_feed_sources.json
infra/rss-stack/README.md
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

## Runtime result

```text
FreshRSS service is reachable and can display feed items.
RSSHub service is reachable because it returned a structured route error page.
rsshub_youtube_route_smoke_seed failed runtime validation with route is empty.
The failed YouTube smoke seed is now disabled and removed from FRESHRSS_SEEDS.opml.
```

## OPML status

```text
FRESHRSS_SEEDS.opml exists.
It includes only currently enabled seed entries.
Enabled OPML seed entries are aligned with sources/channel_feed_sources.json:
- rsshub_project_github_releases_atom
```

## Source-of-truth sync

```text
CURRENT_DECISIONS.md records the 2026-07-07 feed stack decision.
DEPENDENCY_MAP.md includes Shared Feed Stack Gate and Feed stack status fields.
SOURCE_LIBRARY_SPEC.md includes feed stack layer, provider roles, fetch priority, and coverage audit fields.
AGENT_DEFINITION_MAP.md includes feed stack dependencies and route/audit boundaries.
```

## Documentation sync

```text
infra/rss-stack/README.md now points to the existing FRESHRSS_SEEDS.opml workflow.
The README no longer depends on tools/feed-stack/*.js helper scripts, because those helper scripts were not added.
```

## Remaining runtime checks

```text
1. Pull latest main locally.
2. Re-import FRESHRSS_SEEDS.opml into FreshRSS.
3. Confirm the GitHub releases Atom seed refreshes successfully.
4. Pick concrete market-radar accounts or official feeds.
5. Enable each real feed only after route output or direct RSS output is tested.
```

## Completion boundary

```text
Repo-side wiring is complete.
Docker and FreshRSS service startup is practically validated by the user screenshot.
One RSSHub route smoke seed failed and was removed.
Final market-radar feed replacement remains pending until concrete sources are selected and tested.
```
