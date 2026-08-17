# 2026-08-17 gap-fill adapters and taxonomy repair

Change type: Runtime quality repair and structured measurement integration

Affected files: `config/competitor_sources.json`, domain classification, competitor monitor transport behavior, indicator-only measurement lane, structured measurement adapters, composition wiring, and tests.

Human confirmed: yes

Risk level: medium

Mother Brain activated: yes

Rollback note: Revert this change set if live collection quality regresses, structured measurements enter Major/Potential news slots, or competitor official checks produce false material deltas. Each adapter remains independently removable from the multi-source composition.

## Decision

The 2026-08-17 formal backtest identified taxonomy leakage, WACA HTTP 405, and missing BLS/crypto structured measurements. The owner explicitly requested to start filling the gaps. The repair must preserve the canonical five-domain model, keep structured measurements indicator-only, use official/public endpoints, and never convert missing credentials into fabricated coverage.
