# FreshRSS seed import list

Use the enabled entries in `sources/channel_feed_sources.json` as the first manual import seeds.

Current enabled entries:

```text
openai_news_rss
rsshub_project_github_releases_atom
```

Runtime test result:

```text
rsshub_youtube_route_smoke_seed returned an empty route during local RSSHub runtime testing and is disabled.
```

Current seed roles:

```text
openai_news_rss = first real market-radar official AI source.
rsshub_project_github_releases_atom = feed-stack infrastructure monitoring source.
```

Next replacement rule:

```text
1. Pick a concrete official feed or public account.
2. Verify the feed or RSSHub route output locally.
3. Set route_status = verified.
4. Set enabled_for_opml = true only after verification.
5. Add it to FRESHRSS_SEEDS.opml.
6. Remove smoke-test or infrastructure-only entries after at least one real source per target domain is validated.
```

Templates remain disabled until a concrete public account or official feed is selected and route output is tested.
