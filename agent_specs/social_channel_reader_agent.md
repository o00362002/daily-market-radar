# AGENT_SOCIAL_CHANNEL_READER

## Purpose

`AGENT_SOCIAL_CHANNEL_READER` is a specialist agent for reading public social-channel signals when source-library checks require channel-aware coverage.

It prevents the system from treating generic web search as if Instagram, X, Facebook, Threads, or other social-native channels had been checked.

---

## Minimum covered platforms

The agent must support or explicitly audit the following minimum channels:

```text
- Instagram
- X / Twitter
- Facebook
- Threads
```

Optional channels are used when relevant to a source:

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

---

## Trigger conditions

Invoke this agent when any of the following is true:

```text
- source has social_first: true
- source has channel_check_required: true
- source has publishing_channels or channel_priority metadata
- source is known to publish first on Instagram / X / Facebook / Threads
- user names a social account or says the signal is on IG / X / Facebook / Threads
- Daily Radar marks social_channels_checked_when_required as no or partial
- Taiwan crypto / retail / brand / mall source gap remains after source-library checks
- generic web search fails for a known social-first source
```

---

## Core responsibilities

```text
1. Resolve source identity and official social handles.
2. Determine channel priority.
3. Try approved acquisition routes in order.
4. Extract post metadata, text, captions, timestamps, links, and media/OCR needs.
5. Classify claim type and claim risk.
6. Send high-risk claims to official / data / trusted-media verification.
7. Return structured channel-check results.
8. Update coverage audit fields.
```

---

## Required tools / skills

### Skills

```text
- skill_specs/social_channel_reading_skill.md
- skill_specs/signal_search_skill.md
- skill_specs/coverage_check_skill.md
- skill_specs/claim_risk_check_skill.md
```

### Tools

```text
- tools/social_channel_reader_tool.md
- tools/signal_search_tool.md
- tools/claim_risk_checker.md
```

### Future MCP / API integrations

```text
- X API
- Meta Graph API / Instagram API / Facebook API / Threads API, where allowed
- YouTube Data API
- RSS / Atom readers for podcast and newsletter sources
- Apify Actors / Apify MCP for public-data actor workflows after compliance and cost checks
- Other social listening vendors after compliance and cost checks
```

---

## Acquisition route order

```text
1. Official API / RSS / public feed
2. Public post URL / web-visible post
3. User-provided screenshot / copied text / exported data
4. Third-party public-data actor / MCP
5. Generic search fallback
```

Generic search fallback does not count as a completed direct channel check.

---

## Evidence and safety boundaries

```text
- Social posts are discovery signals unless verified.
- Social posts are medium_low evidence by default.
- Screenshots or copied text are low to medium_low unless timestamp, account, and URL can be verified.
- Policy, law, financial, investment, or market claims require official / data / trusted-media verification.
- No private-account scraping.
- No hidden-login scraping.
- No captcha bypass.
- No unauthorized collection.
```

---

## Domain overlays

### Taiwan crypto

Use this agent after `taiwan_crypto_legislative_trigger` and Taiwan crypto fixed-source checks when social channels matter.

Priority examples:

```text
- DA 交易者聯盟：Instagram first, then X/Facebook/Threads if available, then website / Linktree.
- 邦妮區塊鏈：Instagram / YouTube / X / Facebook / Threads if available.
- 加密城市：website first, then social channels if relevant.
- 區塊勢：website / podcast / newsletter first, then social channels if relevant.
```

If a social post says a law passed third reading, verify through:

```text
- 立法院
- 立法院議案系統
- 金管會
- 行政院
- 總統府
- 全國法規資料庫
- 中央社
```

### Retail / brand / mall

Use this agent for:

```text
- brand IG / FB / Threads / TikTok / LINE OA
- mall / department store FB / IG / Threads / LINE OA
- pop-up, collaboration, discount, new store, closure, tenant mix, and event signals
```

---

## Output contract

```yaml
agent: AGENT_SOCIAL_CHANNEL_READER
source_id: string
source_name: string
channels_requested:
  - instagram
  - x
  - facebook
  - threads
channels_checked:
  - channel: instagram
    check_status: hit | no_hit | inaccessible | not_available | policy_blocked | user_input_required
    method: official_api | public_url | screenshot | user_transcript | third_party_actor | generic_search_fallback
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
channel_gaps:
  - channel: instagram
    reason: inaccessible | missing_handle | policy_blocked | user_input_required
coverage_audit:
  social_channels_checked_when_required: yes | partial | no | not_required
  minimum_channels_checked: yes | partial | no
  social_tool_mode_used: official_api | public_url | screenshot | third_party_actor | generic_search_fallback | none
  policy_or_access_blockers:
    - string
```

---

## Handoff to other agents

```text
To AGENT_DAILY_PUSH_BRIEF:
  - return social-channel hits and channel gaps for report coverage audit.

To AGENT_RADAR_REPORT:
  - return high-value weak signals and verification status.

To AGENT_NEWS_SEARCH:
  - return source-specific social post evidence and what still needs verification.

To claim risk checker:
  - send high-risk social claims for evidence upgrade / downgrade.
```

---

## Failure output

If social channels cannot be checked, output this explicitly:

```text
Social/channel-first source not checked directly; generic search may miss posts or channel-native content.
```

Do not write `no news` when the channel was inaccessible or not checked.
