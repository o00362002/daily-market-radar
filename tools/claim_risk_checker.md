# claim_risk_checker

## name

```text
claim_risk_checker
```

## purpose

Check candidate report claims for source risk, overstatement, missing dates, and unsupported inference.

This tool is not a news filter and should not remove ordinary news simply because it is not an official or academic source.

Its main job is to prevent unverified information from being written as confirmed fact.

---

## maintenance principle

Keep this tool easy to maintain:

```text
claim_risk_checker = tag / downgrade / rewrite risk
coverage_checker = check whether required buckets are covered
report_formatter = place the checked items into the report
human / agent judgement = decide final importance
```

Do not put radar coverage rules, search retry rules, or final formatting rules here.

---

## input

```text
candidate_signal_list
source_list
report draft claims
```

---

## operation

```text
1. Identify factual claims, numbers, company / policy statements, and trend conclusions.
2. Check whether each important claim has a source or traceable reference.
3. Check whether dates are explicit when recency matters.
4. Separate sourced facts from AI inference.
5. Tag the claim risk level.
6. Prefer keep / tag / soften / rewrite over remove.
7. Remove only high-risk unsupported claims that would mislead if kept.
```

---

## news source rule

News is an information source, not a professional audit report.

Ordinary news, industry media, local media, interviews, blogs, and social discussion may be used as radar inputs when labelled correctly.

Do not reject a news item only because it is:

```text
single-source
not official
not academic
not a financial filing
not statistically complete
```

Instead, label it honestly:

```text
single-source news
industry source
local source
social signal
unverified candidate
low-evidence weak signal
```

---

## rewrite action policy

Use the least destructive action that keeps the report honest:

| Risk condition | Preferred action |
|---|---|
| Sourced news, but not official | keep + mark evidence level |
| Single-source item | keep as candidate / single-source |
| Social discussion or leak | keep only as unverified weak signal |
| Missing date, but non-critical | keep + mark date missing |
| Missing date, recency-critical | needs date / soften |
| AI inference written as fact | rewrite as inference / possible trend |
| Big number without source | needs source / remove if not sourced |
| Legal, regulatory, financial, health, safety, or accusation claim without source | remove or hold out of fact section |
| Contradicted by better source | remove or mark conflict |
```

---

## output

```text
claim_risk_table
unsupported_claims
claims_to_rewrite
approved_claims
candidate_claims_to_keep_with_label
removed_high_risk_claims
```

---

## required_evidence

```text
claim
source
source type: official / authoritative media / industry media / local media / social / unknown
risk level: low / medium / high
rewrite action: keep / tag / soften / rewrite / needs source / remove
reason
```

---

## removal rule

Removal should be rare.

Only remove when one of the following is true:

```text
No source and high-risk if published.
Inference is written as fact and cannot be rewritten safely.
Recent fact has no date and timing is central to the claim.
The claim is contradicted by stronger available evidence.
The claim makes legal, financial, regulatory, medical, safety, fraud, accusation, or market-moving assertions without adequate sourcing.
```

Otherwise, keep the item as a candidate, weak signal, or low-evidence signal with a clear label.

---

## failure_condition

```text
Important claims have no source or traceable reference.
Inference is written as fact.
Recent facts have no date when recency is central.
High-risk claims remain in final report without warning.
Low-evidence signals are removed instead of being labelled when they could safely remain as candidates.
```
