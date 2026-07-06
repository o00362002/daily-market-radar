# FreshRSS Ingestion Dependency Gate

Purpose: add a small dependency gate for the FreshRSS ingestion layer without replacing the main `DEPENDENCY_MAP.md`.

## Active dependency chain

```text
Daily Push Brief
→ workflows/daily_push_brief_workflow.md
→ workflows/freshrss_ingestion_workflow.md
→ configs/freshrss_ingestion.yml
→ sources/channel_feed_sources.json
→ FRESHRSS_SEEDS.opml
→ templates/feed_item_candidate_schema.md
→ memory/feed_ingestion_log.json
```

## Required gate

```text
FreshRSS ingestion config read: yes / no / not_available
FreshRSS candidate inbox checked: yes / partial / not_available
Feed candidates normalized: yes / partial / not_available
Feed candidates deduped: yes / partial / not_available
Feed candidate evidence trace preserved: yes / partial / not_available
Feed gaps disclosed: yes / partial / not_available
```

## Completion rule

```text
Daily Push Brief may use FreshRSS only as a candidate pool.
FreshRSS candidates must be checked for original URL, freshness, duplication status, and evidence trace before appearing in output.
Infrastructure-only feeds may support feed-stack health notes but cannot count as market news.
```

## Status wording

```text
FreshRSS ingestion status: passed / partial / not_available
```

## Sync note

This file is a dependency addendum for the FreshRSS ingestion layer. The main `DEPENDENCY_MAP.md` should reference this file in the next low-risk documentation pass.
