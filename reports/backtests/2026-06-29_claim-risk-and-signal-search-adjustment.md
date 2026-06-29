# Backtest / Decision Note｜Claim Risk and Signal Search Adjustment

Date: 2026-06-29

## 1. Decision

Adjusted daily radar execution rules:

```text
claim_risk_checker should tag / downgrade / rewrite first, not over-filter news.
signal_search_tool should switch search method before marking a gap.
```

## 2. Reason

Daily market radar is an intelligence workflow, not a professional audit report.

News is an information source. Ordinary news, local media, industry media, single-source reports, and social discussion may still be useful as candidate signals when labelled honestly.

The previous wording created two risks:

```text
claim_risk_checker removed too many news items instead of labelling them.
signal_search_tool could mark a gap too early when the first search failed.
```

## 3. Updated files

```text
tools/claim_risk_checker.md
tools/signal_search_tool.md
workflows/daily_radar_workflow.md
skill_specs/README.md
```

## 4. New operating rule

```text
Low evidence does not automatically mean remove.
It usually means label, downgrade, soften, or rewrite.
```

Remove only when a claim is high-risk and unsupported.

High-risk includes:

```text
legal
financial
regulatory
medical
safety
fraud
accusation
market-moving assertion
```

## 5. Search retry rule

```text
No signal found -> change method -> record retry trace -> only then mark gap.
```

Retry method details remain in:

```text
configs/search_retry_protocol.yml
```

## 6. Maintenance boundary

```text
claim_risk_checker = risk tag / downgrade / rewrite
signal_search_tool = candidate discovery + retry trace
coverage_checker = bucket coverage check
report_formatter = final layout
workflow = process skeleton
configs = detailed parameters
```

Do not move all detailed retry or claim rules into SYSTEM_PROMPT.md.

## 7. Backtest watch item

Next daily report should be checked for:

```text
whether ordinary news is preserved as labelled candidate evidence
whether weak signals are downgraded instead of removed
whether no-data claims include retry trace
whether high-risk unsupported claims are still blocked or softened
```
