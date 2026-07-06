# RSSHub + FreshRSS feed stack

This folder adds the local feed collection layer for `daily-market-radar`.

```text
RSSHub = channel / non-RSS adapter
FreshRSS = self-hosted feed inbox and aggregator
GDELT / Media Cloud = discovery providers
```

The stack does not replace the existing source library, query recipes, evidence rules, or daily output gates. It feeds them.

---

## 1. Start locally

```bash
cd infra/rss-stack
cp .env.example .env
docker compose up -d
```

Default local URLs:

```text
RSSHub:   http://localhost:1200
FreshRSS: http://localhost:8080
```

---

## 2. Active config files

```text
configs/feed_discovery_stack.yml
sources/channel_feed_sources.json
sources/discovery_providers.yml
FRESHRSS_SEEDS.opml
```

Execution flow:

```text
source library + query recipes
→ RSSHub route / direct RSS feed collection
→ FreshRSS category inbox
→ GDELT / Media Cloud discovery when gaps remain
→ no-prefilter capture into memory/potential_pool.md
→ output-stage selection and evidence grading
```

Boundary:

```text
RSSHub / FreshRSS improve coverage, not evidence strength.
GDELT / Media Cloud discover events and sources, but original sources still need verification.
```

---

## 3. Import OPML into FreshRSS

The current seed OPML is maintained at repo root:

```text
FRESHRSS_SEEDS.opml
```

Import it in FreshRSS:

```text
FreshRSS → Subscription management → Import / Export → Import OPML
```

Only entries marked as both `route_status = verified` and `enabled_for_opml = true` in `sources/channel_feed_sources.json` should appear in the OPML seed file.

Route templates and unverified candidates must not be imported.

---

## 4. Route verification rule

For every route candidate:

```text
1. Confirm the route exists in current RSSHub docs or by direct local probe.
2. Confirm it returns expected feed output.
3. Set route_status = verified.
4. Set enabled_for_opml = true only for concrete, non-template feeds.
5. Update FRESHRSS_SEEDS.opml if the feed should enter FreshRSS.
```

---

## 5. Local runtime validation

```bash
cd infra/rss-stack
docker compose ps
curl -f http://localhost:1200/healthz
curl -I http://localhost:8080
```

After importing `FRESHRSS_SEEDS.opml`, confirm in FreshRSS:

```text
1. Seed feeds are listed.
2. Manual refresh completes.
3. RSSHub route seed returns items or a clear empty-state.
4. Any failed feed is recorded in reports/feed_stack_sync_status_2026-07-07.md or future source health logs.
```
