# RSSHub + FreshRSS feed stack

This folder adds the local collection layer for `daily-market-radar`.

```text
RSSHub = channel / non-RSS adapter
FreshRSS = self-hosted feed inbox and aggregator
GDELT / Media Cloud = external discovery providers
```

The stack is intentionally small. It does not replace the existing source library, query recipes, evidence rules, or daily output gates. It feeds them.

---

## 1. Start locally

```bash
cd infra/rss-stack
cp .env.example .env
# Edit passwords in .env before using outside localhost.
docker compose up -d
```

Default local URLs:

```text
RSSHub:   http://localhost:1200
FreshRSS: http://localhost:8080
```

FreshRSS is configured with:

```text
TZ=Asia/Taipei
CRON_MIN=2,32
INTERNAL_HOST_ALLOWLIST=rsshub:1200
```

`INTERNAL_HOST_ALLOWLIST` allows FreshRSS to request RSSHub through the internal Docker hostname `rsshub:1200`. Without this, internal-host requests can be blocked by FreshRSS security defaults.

---

## 2. How this plugs into daily-market-radar

Active config files:

```text
configs/feed_discovery_stack.yml
sources/channel_feed_sources.json
sources/discovery_providers.yml
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

Important boundary:

```text
RSSHub / FreshRSS improve coverage, not evidence strength.
GDELT / Media Cloud discover events and sources, but original sources still need verification.
```

---

## 3. Export OPML for FreshRSS

The helper script reads `sources/channel_feed_sources.json` and exports only enabled, verified feed items.

```bash
node ../../tools/feed-stack/export-freshrss-opml.js \
  --input ../../sources/channel_feed_sources.json \
  --output ./freshrss-daily-market-radar.opml
```

Then import the OPML in FreshRSS:

```text
FreshRSS → Subscription management → Import / Export → Import OPML
```

By default, route templates and unverified RSSHub route candidates are not exported. This prevents a fake sense of coverage.

---

## 4. Route verification rule

For every RSSHub route candidate:

```text
1. Confirm the route exists in current RSSHub docs or by direct local probe.
2. Confirm it returns public, allowed content.
3. Set route_status = verified.
4. Set enabled_for_opml = true.
5. Re-run export-freshrss-opml.js.
```

Unverified route templates must remain visible as TODOs but cannot count as checked channels.

---

## 5. Local smoke checks

```bash
docker compose ps
curl -f http://localhost:1200/healthz
curl -I http://localhost:8080
node ../../tools/feed-stack/check-feed-stack-config.js
```

The checker is intentionally deterministic and shallow. It only verifies required files, obvious JSON shape, and route-status discipline. Evidence judgement still belongs to the normal daily-market-radar rules.

---

## 6. Security and access boundaries

Do not use this stack to bypass:

```text
private accounts
hidden login walls
captcha-protected content
restricted app-only content
paywall usage policies
rate limits
```

If a route is blocked, login-required, or unavailable, mark it as a channel gap. Do not silently replace it with generic search.
