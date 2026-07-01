# Mount Check Policy

This repo follows the mother Brain version-tolerant mount check principle.

Hard failures are reserved for structural safety:

- required entry files are missing
- manifest has no mother repo
- manifest has no level
- unresolved conflict markers exist
- active legacy contradiction exists

Warnings are used for moving metadata:

- mother version drift
- projection wording freshness
- backtest note freshness
- incomplete non-blocking sync language

The local shell checker has been updated to avoid hard-coding moving version numbers.
