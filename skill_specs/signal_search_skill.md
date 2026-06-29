# signal_search_skill

## purpose

Convert configured radar priorities into searchable signal targets.

## input

```text
configs/
memory/watchlist.md
memory/missed_cases.md
user priority topics
```

## procedure

```text
1. Identify required radar buckets.
2. Expand each bucket into search intents.
3. Prioritize high-signal, recent, and source-verifiable items.
4. Hand off to signal_search_tool.
```

## output

```text
search_intents
priority_bucket_list
```

## quality_gate

Every priority bucket must have either signals or an explicit gap note.
