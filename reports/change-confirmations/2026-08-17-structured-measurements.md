# 2026-08-17 structured measurement integration

Change type: Add formal indicator-only structured data sources

Affected files: `config/measurement_sources.json`, structured measurement schema/adapters, runtime composition, tests, and adapter documentation.

Human confirmed: yes

Risk level: medium

Mother Brain activated: yes

Rollback note: Revert this change if structured datasets appear as Major/Potential news, source failures make the live pipeline unusably brittle, or parsed metrics diverge from the official APIs. The measurement registry and adapters are independently removable from composition.

## Decision

The owner requested to start filling the formal gaps identified on 2026-08-17. BLS productivity/distribution data and DefiLlama protocol TVL/fees/revenue are structured measurement sources, not daily news. They must therefore enter through `indicator_only`, remain visible in source audit, feed fixed matrices/structural indicators, and never occupy daily news slots.
