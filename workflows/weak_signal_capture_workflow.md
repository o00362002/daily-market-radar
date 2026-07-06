# Weak Signal Capture Workflow

Purpose: retain early, niche, social-first, and potential trend signals that are not yet strong enough to become confirmed news or long-term tracked sources.

This workflow prevents the radar from becoming only an official-news digest.

---

## Execution position

```text
FreshRSS candidates / query recipes / GDELT / Media Cloud / social-route candidates
→ weak signal scoring
→ memory/potential_pool.md
→ follow-up checks
→ promote, keep watching, or reject
```

---

## Required files

```text
configs/weak_signal_capture_rules.yml
templates/weak_signal_schema.md
memory/potential_pool.md
configs/source_promotion_rules.yml
workflows/source_promotion_workflow.md
```

---

## Capture loop

```text
1. Inspect rejected or low-confidence candidate items before discarding them.
2. If novelty and relevance are high, create a weak signal record.
3. Store it in memory/potential_pool.md.
4. Assign next_check_query and next_check_after.
5. During future briefs, check whether the signal gained confirmation, repetition, or action.
6. Promote to news, promote to source candidate, keep watching, or reject as noise.
```

---

## What to capture

```text
small but repeated social signals
new tool or protocol usage before mainstream coverage
early retail format changes
unusual discount or inventory pressure observations
RWA / agent payment / x402 / protocol adoption hints
AI agent workflow deployment cases
small policy pre-signals
Taiwan local retail or consumption signs
```

---

## What not to capture

```text
pure engagement bait
untraceable rumor
one-off hot take with no source
duplicate of already-covered news
content unrelated to the six core domains
unsafe or private-source material
```

---

## Daily output boundary

Weak signals may be used as:

```text
niche_candidate
trend_watch_note
potential_pool_update
post_brief_review_item
```

Weak signals must not be used as:

```text
confirmed major news
Taiwan news quota filler without qualified Taiwan source
final conclusion without evidence
```

---

## Review rhythm

```text
crypto / market structure signals: re-check within 7 days
AI agent workflow signals: re-check within 21 days
retail and consumer signals: re-check within 30 days
Taiwan policy or local signals: re-check within 30 days
```
