# 2026-08-21｜Consulting AI Operations competitor lane

Change type: competitor taxonomy, fixed official-source monitoring, query recipes, monthly discovery and web projection

Affected files:
- config/competitor_registry.json
- config/competitor_sources.json
- config/competitor_monthly_watch.json
- configs/competitor_intelligence.yml
- configs/query_recipes.yml
- web/src/lib/competitors.ts
- tests/unit/test_competitor_registry.py

Human confirmed: yes

Risk level: medium

Mother Brain activated: no; the change extends the existing local Competitor Intelligence capability and does not alter cross-repo governance contracts.

Rollback note: revert this change set to remove `global_consulting_ai_operations`, its six fixed targets, official sources, query recipes, discovery queries and web metadata; existing system-vendor groups remain intact.

## Confirmed intent

The owner confirmed that RetailOps should no longer benchmark only POS, ERP and retail SaaS vendors. Daily Radar and competitor analysis must also track consulting firms when they productize consulting knowledge into AI agents, platforms or persistent operational services that overlap with RetailOps.

## Boundary

- Fixed monitoring follows six named product lines: McKinsey Lilli / Retail Agentic AI, BCG X Frontline Ops AI, PwC Commercial Brain, EY Intelligent Operations, Deloitte Zora AI / Industry Agents, and Accenture Edge / AI Refinery.
- Bain and KPMG remain discovery candidates until a productized operational offering with a stable official source is verified.
- General consulting reports, surveys, forecasts, hiring news and one-off advisory projects do not qualify.
- Consulting firms are `adjacent` by default. Promotion toward `direct` requires evidence of repeatable deployment, ongoing runtime, client self-service or a full Action-to-Outcome loop.
- Existing report-domain quotas, Major/Potential lanes and system-vendor monitoring remain unchanged.
