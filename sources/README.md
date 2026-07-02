# sources/

This directory stores the source library used by `daily-market-radar`.

The active method is source-first:

```text
fixed source library
→ source-scoped search / filtering
→ keyword fallback
→ external discovery
→ coverage audit
```

Files:

```text
key_media_library.yml
= global and Taiwan media sources by radar domain.

official_and_data_sources.yml
= official, regulator, company, market, macro, chain, and research/data sources.
```

Rules:

```text
1. Do not treat this directory as a dead static list.
2. Source health must be reviewed through usage evidence and backtests.
3. Keyword search can expand coverage, but it must not replace priority source checks.
4. Taiwan news must come from source-backed Taiwan event / data / company action / policy / market news.
5. Any source with unclear usage terms should be marked `usage_policy: check_required`.
```
