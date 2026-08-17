# 2026-08-17 fixed Crypto measurement integration

Change type: Add formal indicator-only ETF-flow and Taiwan VASP sources

Affected files: `config/measurement_sources.json`, measurement registry validation, fixed HTML measurement adapters, composite structured-measurement dispatch, and unit tests.

Human confirmed: yes

Risk level: medium

Mother Brain activated: yes

Rollback note: Revert this change if the fixed pages change structure and typed facts cannot be parsed safely, if either source is mistaken for an official tier it does not hold, or if indicator-only observations enter Major/Potential news. Each source fails independently and can be removed from `config/measurement_sources.json` without disabling other live collection.

## Decision

The owner requested continued formal gap filling. Farside is retained as specialist market data for the latest U.S. spot Bitcoin ETF aggregate flow; it is not promoted to issuer or regulator evidence. Taiwan FSC's fixed official law record supplies direct Taiwan VASP regulation evidence. Both sources remain `indicator_only`, use fixed allowlisted URLs, store only typed facts plus bounded summaries, and may fill Crypto matrix cells without consuming daily-news slots.
