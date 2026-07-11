# coverage_checker

## name

```text
coverage_checker
```

## purpose

Check whether the daily radar covers the required topic buckets, including the fixed RetailOps competitor radar, and marks gaps honestly.

## input

```text
candidate_signal_list
report draft
configs/
memory/watchlist.md
memory/missed_cases.md
```

## operation

```text
1. Compare candidate signals against required buckets.
2. Check whether high-priority buckets are covered.
3. Check whether missed-case watch items were searched.
4. Check the RetailOps competitor radar in memory/watchlist.md:
   - Taiwan RetailOps / retail-system competitors
   - international general platforms and retail vertical platforms
   - social-media and content competitors
5. For competitor signals, distinguish shipped product, public beta, partnership announcement,
   concept demo, customer case, pricing change, and media speculation.
6. Mark missing buckets as gap notes instead of silently omitting them.
7. Identify duplicated or low-value signals.
```

## output

```text
coverage_table
missing_bucket_notes
duplicate_signal_notes
retry_needed_notes
competitor_radar_status
```

## required_evidence

```text
bucket name
covered? yes / no
source count
gap reason
retry needed? yes / no

For RetailOps competitor radar when a material update exists:
competitor / platform
event date
update type
product status
source quality
retailops-agent-system overlap: low / medium / high
impact layer: free entry / template subscription / decision module / agent / private integration
action: observe / validate / reposition / accelerate / no action
```

## competitor_radar_minimum_check

```text
1. Search both Taiwan and international sources.
2. Check named companies in memory/watchlist.md, but do not stop at the named list.
3. Search for new entrants using capability terms such as:
   RetailOps, AI store manager, retail agent, fashion inventory AI,
   replenishment AI, merchandising AI, store operations platform,
   retail OS builder, retail copilot, agentic commerce, retail module marketplace.
4. Check whether international general platforms have released vertical retail templates,
   modules, connectors, low-code packs, or self-service offerings.
5. Check social platforms for newly emerging Taiwan accounts that combine store operations,
   retail data, fashion retail, and AI.
6. If no material update is found, mark "已查無重大更新" and retain the search status.
```

## failure_condition

```text
Required buckets are missing without gap notes.
Known missed cases are not checked.
RetailOps competitor radar was omitted or searched only through one language / one market.
A competitor announcement is described as a shipped capability without evidence.
A material competitor update lacks overlap and impact assessment.
Report claims broad coverage without evidence.
```