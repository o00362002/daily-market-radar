# Social Channel Reader Tool Spec

## Role

Tool adapter spec for reading public social-channel content used by Daily Market Radar agents.

This is not a scraper implementation. It defines approved acquisition routes, fallback rules, and evidence boundaries for future MCP / API / Actor integrations.

---

## Minimum channel scope

```text
must_support:
  - Instagram
  - X / Twitter
  - Facebook
  - Threads

optional_when_relevant:
  - YouTube
  - TikTok
  - LINE OA
  - Discord
  - Telegram
  - Podcast
  - Newsletter
  - Website / Linktree / bio link
```

---

## Approved tool routes

### 1. Official API route

Use first when credentials, permissions, and terms allow.

```yaml
route_id: official_api
priority: 1
examples:
  - X API recent search / user posts
  - Meta Graph API for authorized Instagram / Facebook assets
  - Threads API where app permissions allow
  - YouTube Data API
  - RSS / Atom for podcasts and newsletters
allowed_for:
  - public data
  - owned or authorized accounts
  - policy-compliant research / monitoring
risk: low_to_medium
```

### 2. Public URL route

Use when the user or source library provides a public post URL.

```yaml
route_id: public_url
priority: 2
allowed_for:
  - public post pages
  - public profile pages
  - public web-visible Threads / X / Facebook / Instagram content
risk: medium
notes:
  - Some platforms block unauthenticated reading.
  - If inaccessible, mark inaccessible instead of claiming no hit.
```

### 3. User evidence route

Use when direct reading is unavailable.

```yaml
route_id: user_evidence
priority: 3
inputs:
  - screenshot
  - copied caption
  - copied post text
  - exported data
  - manually provided post URL
allowed_for:
  - user-provided public evidence
risk: medium_low
notes:
  - Screenshots and copied text require timestamp/source/link if possible.
```

### 4. Third-party public-data actor route

Use only after compliance and cost check.

```yaml
route_id: third_party_actor
priority: 4
examples:
  - Apify Instagram Scraper
  - Apify X / Twitter Scraper
  - Apify Facebook Pages Scraper
  - Apify Threads Scraper, if available
  - other social listening vendors
allowed_for:
  - public data only
  - no private accounts
  - no captcha bypass
  - no hidden-login scraping
risk: medium_to_high
requires:
  - usage_policy_check
  - cost_check
  - source_attribution
  - output validation
```

### 5. Generic search fallback

Generic search is fallback and never counts as direct social-channel check.

```yaml
route_id: generic_search_fallback
priority: 5
allowed_for:
  - discovery only
  - source existence check
  - finding public mirrored posts
not_allowed_for:
  - declaring social channel coverage complete
  - proving no post exists
```

---

## Platform notes

### Instagram

```text
preferred:
  - official Meta API if authorized
  - public post URL
  - user screenshot / transcript
  - third-party public-data actor after compliance check
minimum_output:
  - profile checked?
  - post/reel URL checked?
  - caption extracted?
  - image/carousel OCR needed?
```

### X / Twitter

```text
preferred:
  - X API recent search for recent posts
  - from:account keyword query
  - public post URL
notes:
  - Full archive may require paid / enterprise access.
```

### Facebook

```text
preferred:
  - official page / public post URL
  - Meta Graph API if authorized
  - page feed where accessible
notes:
  - If page is inaccessible without login, mark inaccessible.
```

### Threads

```text
preferred:
  - Threads API if authorized
  - public post URL
  - account page if web-visible
notes:
  - Generic search often misses Threads posts.
```

### Optional channels

```text
YouTube:
  - YouTube Data API / public channel / video URL
TikTok:
  - public post URL / approved third-party actor if compliant
LINE OA:
  - user-provided screenshot / public broadcast archive if available
Discord / Telegram:
  - public channels only; no private scraping
Podcast / Newsletter:
  - RSS / archive / public post page
```

---

## Required output contract

```yaml
source_id: string
source_name: string
channel: instagram | x | facebook | threads | youtube | tiktok | line | discord | telegram | podcast | newsletter | website
check_status: hit | no_hit | inaccessible | not_available | policy_blocked | user_input_required
checked_at: YYYY-MM-DDTHH:mm:ss+08:00
method: official_api | public_url | screenshot | user_transcript | third_party_actor | generic_search_fallback
query_or_url: string
post_url: string
post_time: string
author_handle: string
content_summary: string
raw_text_excerpt: string
media_ocr_needed: true | false
claim_type: policy | market | product | brand | community | rumor | opinion
claim_risk: high | medium | low
evidence_default: high | medium | medium_low | low
verification_required: true | false
verification_targets:
  - official_source
  - regulator
  - company_announcement
  - data_source
notes: string
```

---

## Evidence rules

```text
- Official platform API result from verified account: medium to high, depending on claim.
- Public social post from source account: medium_low by default.
- Screenshot / copied text: low to medium_low unless link and timestamp are verifiable.
- KOL / community posts: candidate only unless verified.
- Policy, law, financial, investment, market, or regulatory claims must be cross-checked with official / data / trusted media sources.
```

---

## Required audit fields

Daily report coverage audit must include:

```text
social_channels_checked_when_required: yes / partial / no / not_required
minimum_channels_checked: Instagram / X / Facebook / Threads = yes / partial / no
channel_gaps: none / list
social_tool_mode_used: official_api / public_url / screenshot / third_party_actor / generic_search_fallback / none
policy_or_access_blockers: none / list
```

If channels were not checked:

```text
Social/channel-first source not checked directly; generic search may miss posts or channel-native content.
```

---

## Hard boundaries

```text
- No private-account scraping.
- No hidden-login scraping.
- No captcha bypass.
- No unauthorized data collection.
- No use of social posts as high evidence for policy, financial, legal, investment, or market claims without verification.
```
