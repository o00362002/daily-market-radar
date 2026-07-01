# Backtest｜Mother Brain v1.19 mount sync

Date: 2026-07-01
Repo: daily-market-radar
Status: pending local verification

## Purpose

Sync this child repo with the mother Brain v1.19 compact five-layer architecture.

## Required direction

```text
All child repos and modules inherit the mother Brain compact five-layer architecture and vocabulary.
Each layer is implemented locally according to the repo's Level and actual complexity.
Thin mount keeps the child repo light and does not copy the full mother Brain.
```

## Files checked / updated

```text
PROJECT_OS_MOUNT.md
AGENTS.md
brain.manifest.yaml
check_mount_integrity.sh
```

## Expected semantic changes

```text
Mother version: v1.18-draft -> v1.19-draft
Mother architecture: compact_five_layer
Layer depth: level_scaled
Adoption Layer wording -> Adoption Gate under Interface & Integration Layer
Bash level parsing quote bug fixed
```

## Required local check

```bash
bash check_mount_integrity.sh
```

## Completion rule

Mark complete only after local checker passes and changed files are committed.
