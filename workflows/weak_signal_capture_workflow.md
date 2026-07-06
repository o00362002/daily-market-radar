# Weak Signal Capture Workflow

Purpose: retain early, niche, social-first, and potential trend signals that are not yet strong enough to become confirmed news or long-term tracked sources.

This workflow prevents the radar from becoming only an official-news digest.

It also prevents the system from deleting influential but unverified or disputed narratives too early.

---

## Execution position

```text
FreshRSS candidates / query recipes / GDELT / Media Cloud / social-route candidates
→ weak signal scoring
→ truth_score and influence_score split
→ memory/potential_pool.md
→ follow-up checks
→ promote, keep watching, mark influential false signal, or reject
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
2. Score truth and influence separately.
3. If novelty, relevance, or influence is high, create a weak signal record.
4. Store it in memory/potential_pool.md.
5. Assign next_check_query and next_check_after.
6. During future briefs, check whether the signal gained confirmation, repetition, contradiction, or visible action.
7. Promote to news, promote to source candidate, retain as influential false/disputed signal, keep watching, or reject as noise.
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
new concepts before official confirmation
new applications mentioned repeatedly by builders, users, investors, brands, or policy actors
false or disputed claims that are spreading enough to affect behavior, prices, policy debate, search demand, or brand decisions
```

---

## What not to capture

```text
pure engagement bait with no spread
one-off hot take with no source and no repetition
duplicate of already-covered news
content unrelated to the six core domains
unsafe or private-source material
claims where no confirmation or invalidation path can be defined
```

Do not reject solely because a signal is unverified, disputed, or likely false. If it has high spread or narrative impact, retain it with warning labels.

---

## Daily output boundary

Weak signals may be used as:

```text
niche_candidate
trend_watch_note
potential_pool_update
post_brief_review_item
narrative_risk_note
```

Weak signals must not be used as:

```text
confirmed major news
Taiwan news quota filler without qualified Taiwan source
final conclusion without evidence
verified fact when truth_status is unverified, disputed, likely_false, or false_but_influential
```

---

## Required annotation for low-truth high-influence signals

```text
truth_status: unverified / disputed / likely_false / false_but_influential
influence_status: repeated_mentions / narrative_forming / market_or_policy_attention / mainstreamed
why_retained_despite_low_truth
what_would_confirm_it
what_would_invalidate_it
next_check_query
```

---

## Review rhythm

```text
crypto / market structure signals: re-check within 7 days
AI agent workflow signals: re-check within 21 days
retail and consumer signals: re-check within 30 days
Taiwan policy or local signals: re-check within 30 days
false but influential narratives: re-check within 14 days
```
