# 2026-08-17 live backtest follow-up

Change type: Live taxonomy and competitor-state continuity repair

Affected files: `config/competitor_sources.json`, `src/radar/pipeline/domain_classification.py`, competitor page rendering, and regression tests.

Human confirmed: yes

Risk level: low

Mother Brain activated: yes

Rollback note: Revert this follow-up if named AI systems start overriding clearly non-AI stories or WACA state continuity renders cached material as current. Cached WACA material must remain explicitly labeled as last-known baseline when the current direct check fails.

## Decision

The first live run after PR #70 proved that explicit named-model anchors were still missing and WACA direct HTTP remained 405. The fix adds named AI systems as strong content anchors and restores the prior WACA source IDs/URLs so previously verified official baseline content remains traceable. Current WACA direct-check failure must stay visible; search-engine cache is supplemental only and is not promoted into the formal competitor audit.
