# claim_risk_checker

## name

```text
claim_risk_checker
```

## purpose

Check candidate report claims for source risk, overstatement, missing dates, and unsupported inference.

## input

```text
candidate_signal_list
source_list
report draft claims
```

## operation

```text
1. Identify factual claims, numbers, company / policy statements, and trend conclusions.
2. Check whether each important claim has a source.
3. Check whether dates are explicit when recency matters.
4. Separate sourced facts from AI inference.
5. Downgrade or remove claims that are not supported.
```

## output

```text
claim_risk_table
unsupported_claims
claims_to_rewrite
approved_claims
```

## required_evidence

```text
claim
source
risk level: low / medium / high
rewrite action: keep / soften / remove / needs source
```

## failure_condition

```text
Important claims have no source.
Inference is written as fact.
Recent facts have no date.
High-risk claims remain in final report without warning.
```
