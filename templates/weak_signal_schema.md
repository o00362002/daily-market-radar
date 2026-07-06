# Weak Signal Schema

Purpose: preserve early signals that are not yet strong enough to be treated as confirmed news or long-term source promotions.

Weak signals are trend candidates, not final facts.

A weak signal can have low truth confidence but high narrative or market influence. The system should annotate this instead of deleting it automatically.

---

## Weak signal object

```yaml
signal_id: "weak::<domain>::<date>::<slug_or_hash>"
captured_at: ""
signal_type: "emerging_trend | niche_project | social_first_signal | repeated_keyword_cluster | local_retail_observation | crypto_protocol_signal | ai_agent_workflow_case | false_but_influential_narrative | unverified_new_concept | unverified_new_application"

title: ""
summary: ""
source_url: ""
source_name: ""
source_confidence: "low | medium_low | medium | high"
truth_status: "confirmed | partially_supported | unverified | disputed | likely_false | false_but_influential"
influence_status: "low_spread | repeated_mentions | narrative_forming | market_or_policy_attention | mainstreamed"
evidence_status: "unverified | partially_supported | source_backed | confirmed_later | contradicted_later"

domain_ids:
  - ai_agents_workflow
region: "global | taiwan | multi"
languages:
  - en

novelty_score: 0
relevance_score: 0
repetition_score: 0
influence_score: 0
truth_score: 0
potential_score: 0

novelty_reason: ""
why_it_might_matter: ""
why_retained_despite_low_truth: ""
what_would_confirm_it: ""
what_would_invalidate_it: ""
next_check_query: ""
next_check_after: ""

status: "watching | promoted_to_news | promoted_to_source_candidate | retained_as_influential_false_signal | rejected_noise | expired"
used_in_output: false
output_role: "none | niche_candidate | trend_watch_note | potential_pool_section | narrative_risk_note"

notes: ""
```

---

## Boundary

```text
Weak signal ≠ confirmed news.
Weak signal ≠ long-term source.
Weak signal = early item worth watching because it may become a future trend, narrative, behavior change, policy response, or market move.
```

---

## Truth vs influence rule

```text
truth_score measures whether the claim is reliable.
influence_score measures whether the claim or concept is spreading or changing behavior.
Low truth_score does not automatically remove a signal when influence_score is high.
False or disputed signals can still matter if they move markets, social behavior, policy debates, brand decisions, or future search demand.
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

## Retention conditions for low-truth signals

Keep the signal, with warning labels, when:

```text
new concept appears repeatedly
new application is being discussed by builders, users, brands, or investors
false or disputed claim is spreading enough to influence behavior
market, social, policy, or retail actors respond to it
it reveals demand, fear, expectation, or narrative direction
```

---

## Rejection conditions

```text
pure hype with no spread
no source and no repeated mentions
no relevance to core domains
spam or engagement bait
cannot define what would confirm or invalidate it
```
