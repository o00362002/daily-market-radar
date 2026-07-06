# Weak Signal Schema

Purpose: preserve early signals that are not yet strong enough to be treated as confirmed news or long-term source promotions.

Weak signals are trend candidates, not final facts.

---

## Weak signal object

```yaml
signal_id: "weak::<domain>::<date>::<slug_or_hash>"
captured_at: ""
signal_type: "emerging_trend | niche_project | social_first_signal | repeated_keyword_cluster | local_retail_observation | crypto_protocol_signal | ai_agent_workflow_case"

title: ""
summary: ""
source_url: ""
source_name: ""
source_confidence: "low | medium_low | medium | high"
evidence_status: "unverified | partially_supported | source_backed | confirmed_later"

domain_ids:
  - ai_agents_workflow
region: "global | taiwan | multi"
languages:
  - en

novelty_score: 0
relevance_score: 0
repetition_score: 0
potential_score: 0

novelty_reason: ""
why_it_might_matter: ""
what_would_confirm_it: ""
what_would_invalidate_it: ""
next_check_query: ""
next_check_after: ""

status: "watching | promoted_to_news | promoted_to_source_candidate | rejected_noise | expired"
used_in_output: false
output_role: "none | niche_candidate | trend_watch_note | potential_pool_section"

notes: ""
```

---

## Boundary

```text
Weak signal ≠ confirmed news.
Weak signal ≠ long-term source.
Weak signal = early item worth watching because it may become a future trend.
```

---

## Promotion conditions

A weak signal can be promoted when:

```text
1. Repeated by independent sources.
2. Confirmed by official source, data source, or primary actor.
3. Produces visible market, policy, social, retail, or technology action.
4. Becomes relevant to at least one core domain and passes freshness checks.
```

---

## Rejection conditions

```text
pure hype
no original source
no follow-up within watch window
not relevant to core domains
contradicted by stronger evidence
spam or engagement bait
```
