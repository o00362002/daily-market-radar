# claim_risk_check_skill

## purpose

Judge whether report claims are sufficiently supported before they enter the final report.

## input

```text
candidate_signal_list
source_list
report draft claims
```

## procedure

```text
1. Separate facts, numbers, quotes, policy claims, and AI inference.
2. Check whether each important claim has a source and date.
3. Classify claim risk.
4. Rewrite, soften, remove, or request more evidence.
5. Hand off approved claim set to coverage_check_skill.
```

## output

```text
claim_risk_table
approved_claims
claims_to_rewrite_or_remove
```

## quality_gate

High-risk unsupported claims must not enter the final report.
