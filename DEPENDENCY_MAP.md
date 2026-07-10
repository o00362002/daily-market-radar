# Daily Market Radar｜DEPENDENCY_MAP

Human-readable dependency and degradation map for Event Intelligence Runtime v2.
Machine-derivable contract values live in `config/runtime_contract.json` and must not be hand-copied here.

## 1. Sources of truth

```text
Execution entry: AGENTS.md
Current facts: CURRENT_STATE.md
Accepted decisions: CURRENT_DECISIONS.md
Runtime contract: config/runtime_contract.json
Canonical source registry: config/source_registry.json
Deterministic runtime: src/radar/
Report schema: schemas/report.schema.json
Database foundation: migrations/0001_runtime_foundation.sql + migrations/0002_report_payloads.sql + migrations/0003_durable_runtime_repositories.sql
Sync edges: schema/sync-matrix.json
```

Semantic policies remain in `configs/`; human rendering remains in `workflows/` and `templates/`.
If prose conflicts with the runtime contract, mark dependency drift and follow the machine contract.

## 2. Active execution chains

### Daily Push Brief

```text
AGENT_DAILY_PUSH_BRIEF
→ config/runtime_contract.json profile=daily_push
→ config/source_registry.json
→ source health / ingest adapters
→ normalize / deduplicate / event clustering / cross-day material delta
→ evidence verification / independent scores
→ coverage cells and gap discovery
→ report planner with slot caps
→ templates/daily_push_brief_template.md
→ schemas/report.schema.json + Python contract validation
→ post-run backtest
```

### Full Daily Radar

```text
AGENT_RADAR_REPORT
→ config/runtime_contract.json profile=full
→ same deterministic pipeline
→ all qualified items within run budget
→ templates/daily_report_template_v2.md
→ report contract validation
→ archive + backtest
```

### Topic Search

```text
AGENT_NEWS_SEARCH
→ source registry route for the topic
→ source health / ingest / fallback discovery
→ event and evidence contracts
→ topic-search template
```

### Content Rewrite

```text
AGENT_NEWS_CONTENT
→ already validated report items
→ content template
```

Content rewrite cannot search broadly, upgrade evidence or alter event identity.

## 3. Slot-cap rule

Daily Push slot caps and Full profile behavior are read from `config/runtime_contract.json`.

```text
slot cap = readability limit
coverage gate = completeness check
```

A domain with fewer qualified items receives a gap card. Do not fabricate or repeat items.
A run with many qualified items may keep overflow in machine output or archive while the brief renders only the cap.
Historical fixed-count completion rules are frozen v1 behavior and are not active.

## 4. Completion gate

A run can be `complete` only when all requirements in `completion_requires` from the runtime contract pass.
At minimum this includes:

```text
source health and run budget
coverage cells by domain / region / language / source role / channel / time window
evidence trace and original-source verification
fresh material delta and historical de-duplication
one primary domain per event
major and potential lane separation
rejection counters and retry audit
Taiwan direct-evidence audit
Retail fixed matrix
Crypto fixed matrix
Structural Trend Indicator Panel
report schema and Python contract validation
post-run backtest
```

Otherwise status is `partial` or `failed`, with explicit degradation reasons.

## 5. Source and feed gate

Canonical source identity lives in `config/source_registry.json`.

```text
one real source = one source_id
RSS / API / web / RSSHub / social = adapters
FRESHRSS_SEEDS.opml = generated projection
FreshRSS / RSSHub = collection channels, not evidence stores
GDELT / Media Cloud / Event Registry / NewsCatcher = discovery only
```

Original evidence must be verified before a claim is accepted. Unavailable sources become coverage gaps, not `no news`.
Legacy files under `sources/` remain compatibility inputs until regenerated from the registry.

## 6. Taiwan gate

```text
direct_taiwan_evidence != taiwan_implication
```

Taiwan direct evidence must resolve to a Taiwan source or an event explicitly involving a Taiwan entity.
Generic implications do not satisfy Taiwan coverage. Social-first sources require direct checks.
Taiwan crypto fixed-source failures must be disclosed as source gaps.

## 7. Major and potential lanes

```text
importance_score = importance now
potential_score = future option value
confidence_score = evidence strength
```

These scores are independent. A single event cannot fill both major and potential lanes or multiple primary-domain slots.
Potential items require candidate metadata and a fresh concrete anchor.

## 8. Retail, Crypto and structural panels

Keys are canonical in `config/runtime_contract.json`.
The report contract must include every configured key, even when status is `insufficient`.

Structural indicators:

```text
K-shaped AI productivity economy
AI bubble / overinvestment
brand polarization + true vs fake segmentation
```

They are cumulative direction meters and must include counterevidence and missing data.

## 9. Live / fixture boundary

Fixture replay proves deterministic structure only.

```text
fixture ingestion != live source coverage
CLI accepted != provider integrated
schema exists != database persistence active
```

The report must expose ingestion mode and cannot claim live completeness from fixture data.
`live-rss` executes verified RSS/Atom adapters and can persist optional SQLite document, event, delta,
report, indicator and state records, but remains partial until web/API/social, FreshRSS and external
discovery adapters are connected.

## 10. Replaceability boundary

```text
src/radar/contracts/     canonical provider-neutral values
src/radar/ports/         stable behavior Protocols
src/radar/application/   Protocol-injected external collaborators + pure deterministic orchestration
src/radar/composition.py concrete implementation selection
src/radar/runtime/       compatibility façade
```

Architecture tests reject direct application imports of concrete adapters, repositories,
network/provider modules and filesystem APIs. A fake-only integration test blocks all external
I/O while exercising report persistence, web artifact projection, state and publishing.

## 11. Runtime commands

```bash
make validate
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli run-daily --mode fixture --date YYYY-MM-DD
PYTHONPATH=src python -m radar.cli run-daily --mode live-rss --date YYYY-MM-DD --database <database-path>
```

## 12. Sync expectations

`schema/sync-matrix.json` must link:

```text
runtime contract ↔ workflows / templates / report schema / runtime
source registry ↔ OPML / source policy / source tests
report model ↔ planner / contract validator / schema / tests
CURRENT_DECISIONS ↔ reports execution record
```

A caught drift should add or upgrade a machine-consumed sync edge.
