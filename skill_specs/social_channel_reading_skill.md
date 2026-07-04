# Social Channel Reading Skill

## Purpose

Read public social-channel signals for Daily Market Radar when a source is social-first or channel-first.

This skill exists because generic web search often misses Instagram, X, Facebook, Threads, LINE, YouTube, TikTok, Discord, Telegram, podcast, and newsletter-native content.

## Minimum required channels

The minimum social-channel coverage for channel-aware checks is:

```text
- Instagram
- X / Twitter
- Facebook
- Threads
```

Optional channels should be added when the source uses them materially:

```text
- YouTube
- TikTok
- LINE OA
- Discord
- Telegram
- Podcast
- Newsletter
- Website / Linktree / bio link
```

## When to trigger

Trigger this skill when any of the following is true:

```text
- source has social_first: true
- source has channel_check_required: true
- source has publishing_channels including Instagram / X / Facebook / Threads
- user names a social platform or social account directly
- Taiwan crypto, Taiwan retail, brand, mall, AI community, or KOL source has a coverage gap
- generic web search returns insufficient results for a known social-first source
```

## Supported acquisition modes

### Level 1 — Official / approved APIs

Preferred where available and authorized.

```text
- X API: recent search, user timeline, keyword / from: queries
- Meta / Instagram / Facebook / Threads APIs: only when app permissions and policy allow
- YouTube Data API
- Podcast RSS / public feed
- Newsletter RSS / archive page when available
```

### Level 2 — User-provided public evidence

Use when API or direct channel access is unavailable.

```text
- public post URL
- screenshot
- copied caption / text transcript
- exported CSV / JSON from a social listening tool
```

### Level 3 — Third-party public-data tools

Allowed only for public content and compliance-reviewed use.

```text
- Apify Actors / Apify MCP
- Bright Data / social listening tools
- browser automation / scraping tools only after policy and usage check
```

Never use hidden-login scraping, private-account scraping, captcha bypass, or unauthorized collection.

## Tool selection order

```text
1. Official API / RSS / public feed
2. Public post URL / web-visible post
3. User screenshot or pasted text
4. Third-party public-data actor / MCP
5. Generic web search fallback
```

Generic search does not count as a direct channel check.

## Output schema

Each checked channel should return this shape:

```yaml
source_id: example_source
source_name: Example Source
channel: instagram | x | facebook | threads | youtube | tiktok | line | discord | telegram | podcast | newsletter | website
check_status: hit | no_hit | inaccessible | not_available | policy_blocked | user_input_required
checked_at: YYYY-MM-DDTHH:mm:ss+08:00
method: official_api | public_url | screenshot | user_transcript | third_party_actor | generic_search_fallback
query_or_url: ...
post_url: ...
post_time: ...
author_handle: ...
content_summary: ...
raw_text_excerpt: ...
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
notes: ...
```

## Evidence rules

```text
- Official platform API result from verified account: medium to high, depending on claim.
- Public social post from source account: medium_low by default.
- Screenshot / copied text: low to medium_low unless link and timestamp are verifiable.
- KOL / community posts: candidate only unless verified.
- Policy, law, financial, investment, market, or regulatory claims must be cross-checked with official / data / trusted media sources.
```

## Taiwan crypto special rule

For Taiwan crypto policy or law signals:

```text
1. Run taiwan_crypto_legislative_trigger first.
2. Then run Taiwan crypto fixed sources.
3. Then run social-channel checks for DA 交易者聯盟, 邦妮區塊鏈, 加密城市, 區塊勢 when relevant.
4. If a social post says a law passed third reading, verify with 立法院 / 議案系統 / 金管會 / 中央社 / 全國法規資料庫.
```

## Retail / brand special rule

For Taiwan retail, brand, mall, and department store signals:

```text
- Brand IG / FB / Threads / TikTok / LINE OA may be first-source signals for launches, collaborations, pop-ups, discounts, closures, and new stores.
- Mall / department store Facebook, Instagram, Threads, LINE OA should be checked when tenant mix, event, pop-up, or footfall signals are required.
- Business media such as 商業周刊 / HBR are framework or analysis sources unless they cite original data or interviews.
```

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

## Known limitations

```text
- Instagram, Facebook, Threads, and LINE content may be inaccessible without login, permissions, or user-provided links/screenshots.
- X API access level affects search depth and cost.
- Third-party tools may have cost, rate, ToS, privacy, and reliability issues.
- OCR may be needed for image-only posts or carousel screenshots.
```
