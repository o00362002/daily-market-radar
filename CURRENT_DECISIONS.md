# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-07-10

---

## 2026-07-10：scheduler, durable state and Pages（PR F）

### Decision

```text
1. Six workflows automate the pipeline; the daily job's cron is UTC ('0 23 * * *' == 07:00 Asia/Taipei)
   and documented, deploying before 09:00 Taiwan. RADAR_EVALUATION_MODE defaults to auto.
2. Durable state lives on a dedicated radar-state branch (never main): compressed + checksummed SQLite,
   a state manifest, last-good backup with retention, atomic update, a concurrency lock and corruption
   rollback. An external DATABASE_URL backend is the documented alternative.
3. Pages deploys only the validated site artifact — never live data. Failed reports are not deployed,
   fixture runs are preview-only, and the site base comes from the environment (no hardcoded hostname).
4. Every secret is optional. With none configured, deterministic mode runs, the site is generated, Pages
   deploys, and unavailable integrations are disclosed. Passwords, API keys, auth headers and database
   credentials are never logged (redaction).
```

### Boundary / owner-required UI setup

```text
Workflows are pushed and parse-valid, but only the owner can enable them in the GitHub UI: Pages source =
GitHub Actions; Actions read/write permission (to push radar-state); optional Secrets (OPENAI_API_KEY,
FRESHRSS_*, DATABASE_URL) and Variables (RADAR_EVALUATION_MODE, OPENAI_MODEL, OPENAI_MAX_*). Live Actions
runs and Pages deployment execute on GitHub, not in this environment.
```

### Evidence

`reports/execution_checks/2026-07-10_pr_f_daily_scheduler_pages.md` · `docs/state-persistence.md` · `docs/secrets.md` · `docs/operations.md`

---

## 2026-07-10：projection-first Astro dashboard（PR E）

### Decision

```text
1. The web layer is a projection of validated RadarReportV2 only. Typed web read-models are strict and
   provider-neutral; schemas/web.schema.json is generated from them and web/src/generated/web-types.ts is
   generated from that schema (drift-checked in CI).
2. Web artifacts are immutable and content-addressed. Export is atomic (stage-then-replace), skips
   unchanged artifacts by content hash, rebuilds indexes incrementally, and never leaves half-written
   artifacts on failure.
3. The Astro site is static, zero-JS-first, native CSS, GitHub Pages compatible (site/base from env, never
   hardcoded), 繁體中文預設. Evidence quality and provenance are shown as text+symbol badges, never colour
   alone. The homepage never loads full history; history is paginated; structural empty windows render
   insufficient, never a fabricated trend.
```

### Boundary

```text
The Astro npm build passes locally (14 pages, zero client JS). Web CI (npm build + bundle budgets) and the
GitHub Pages deploy workflow land in PR F. Multi-adapter collection integration remains follow-up.
```

### Evidence

`reports/execution_checks/2026-07-10_pr_e_projection_first_dashboard.md` · `docs/web-architecture.md` · `web/README.md`

---

## 2026-07-10：optional AI and chat-assisted evaluation（PR D）

### Decision

```text
1. Four evaluation modes (deterministic/auto/api-assisted/chat-assisted), default auto. Deterministic
   never imports or calls AI; auto and api-assisted degrade to deterministic without a key.
2. The model is a semantic assistant, not the judge of facts. It sees only a bounded, provider-neutral
   context and may never invent URLs, event/document/source ids or numeric facts; score deltas are
   bounded. Every AI output is re-validated deterministically; invalid output retries once then keeps
   the deterministic result; provider errors never crash the run.
3. Evaluation is cached (event state, evidence hashes, material delta, model, schema version, config) and
   budget-limited; over budget stops new AI calls with degradation=ai_budget_exhausted.
4. The chat package is deterministic, content-addressed, byte-stable, secret-free, and contains no full
   articles or model-invented conclusions. Import re-validates the context hash and every allowed id /
   url / numeric fact / matrix key / indicator id / Taiwan direct-evidence rule / Major-Potential
   overlap; a failed import preserves the last valid report.
```

### Boundary

```text
No real API keys in tests; the OpenAI client path is not executed in CI (proven via a mock provider).
The full secrets contract (.env.example, docs/secrets.md, redaction tests) is planned for PR F.
```

### Evidence

`reports/execution_checks/2026-07-10_pr_d_optional_ai_chat_assisted.md` · `docs/evaluation-modes.md` · `docs/chat-assisted-workflow.md` · `docs/cost-control.md`

---

## 2026-07-10：source adapters and deterministic evaluation（PR C）

### Decision

```text
1. Every network source adapter depends on a shared HttpTransport seam, never on urllib/requests
   directly, so adapters are fully unit-testable offline and SSRF/redirect/size policy is enforced in
   one place.
2. Safe Web fetches registry-allowlisted URLs only, blocks localhost/private/link-local/metadata IPs,
   disallowed schemes/content-types, excessive redirects and oversized responses; it never bypasses
   paywalls or logins, never stores full copyrighted articles, and never becomes an arbitrary crawler.
3. GDELT is discovery-only and must resolve to an original publisher/URL with a verification status;
   it is never final evidence. Generic web results are never marked as social direct-channel checks.
4. Credential-gated adapters (FreshRSS, JSON API auth, official social APIs) degrade to unavailable
   without credentials and never crash the deterministic pipeline.
5. Deterministic matrix and structural-indicator scores are feature-traced and never fixed; absent
   evidence yields insufficient and no fabricated trend. Rolling windows use only real observations.
6. Source health is a deterministic state machine over eight statuses, persisted durably.
```

### Boundary

```text
The deterministic evaluator upgrade is wired into the live pipeline. The new adapters and source-health
repository are tested building blocks; composing them into a single multi-adapter collection stage inside
run-daily is follow-up integration. No real API keys are used in tests.
```

### Evidence

`reports/execution_checks/2026-07-10_pr_c_source_adapters_deterministic_evaluation.md` · `docs/source-adapters.md`

---

## 2026-07-10：event resolution precision（PR B）

### Decision

```text
1. Cross-day event matching is a provider-neutral deterministic cascade (exact document id →
   canonical URL → content hash → exact event signature → normalized entity/action/object/location →
   source-independent structured fact overlap → bounded publication time window). No AI/embedding.
2. Ambiguous fuzzy matches are never forced: a new event is created and an unresolved_match recorded.
3. Material-delta taxonomy: title/summary rewrite alone is not material; numeric change must come from
   canonical structured measurement facts; a new source confirms only when independent and of equal-or-
   higher role; unclassifiable changes are left unresolved.
4. EventResolutionAuditV1 is a required RadarReportV2 section with legacy migration.
5. A UnitOfWork run-transaction port commits documents, events, relations, deltas, report, indicators,
   state checkpoint and match provenance atomically; any failure rolls the run back and never overwrites
   the last valid report. SQLite is the first implementation. The port set grows nine → ten; every port
   remains a runtime-checkable Protocol and the application depends only on ports.
```

### Boundary

```text
This decision improves cross-day precision and durability only. It does not add source adapters,
source health, AI/chat evaluation, web projection, Astro or the scheduler; those remain PR C–F.
```

### Evidence

`reports/execution_checks/2026-07-10_pr_b_event_resolution_precision.md` · `docs/event-resolution.md`

---

## 2026-07-10：modularity and replaceability acceptance gate

### Decision

```text
1. Every replaceable/external application collaborator is injected through SourceAdapter, IntelligenceEvaluator,
   DocumentRepository, EventRepository, ReportRepository, IndicatorRepository,
   StateStore, WebArtifactStore and ReportPublisher Protocols. Provider-neutral contracts/domain and
   pure deterministic pipeline/validation functions remain direct code dependencies.
2. src/radar/composition.py is the only selection point for concrete source,
   evaluator, storage and publisher implementations.
3. RadarReportV2 is validated before report persistence, indicator persistence,
   web artifact commit, state checkpoint or publication.
4. Provider-specific payload fields stay inside adapters/evaluators; canonical models
   are strict and reject unknown fields.
5. runtime/runs.py remains a backward-compatible façade, not an application service.
6. AST import and cycle tests plus a no-network/no-SQLite/no-filesystem fake flow are
   mandatory acceptance gates.
```

### Boundary

```text
This decision proves replaceability for the currently implemented deterministic flow.
It does not claim that FreshRSS, API-assisted evaluation, filesystem web export,
production publishers, durable cross-day events, the Astro dashboard or scheduler exist.
Those remain explicit later implementation work.
```

### Evidence

`reports/execution_checks/2026-07-10_modularity_replaceability_gate.md`

---

## 2026-07-10：runtime v2 contract sync repair

### Decision

```text
1. config/runtime_contract.json is the canonical machine execution/output contract.
2. config/source_registry.json is the canonical source identity and adapter registry.
3. Daily Push slot caps are readability limits; Full profile outputs qualified items within run budget.
4. Historical fixed-count completion rules are frozen v1 behavior.
5. Completeness is determined by source health, coverage cells, evidence trace, fresh material delta,
   de-duplication, rejection/retry audit, Taiwan direct evidence, fixed matrices, structural indicators,
   report-contract validation and backtest.
6. Canonical report domains are six. policy_geopolitics maps to global_markets_macro.
7. Major and potential are separate lanes; one event cannot occupy both lanes or multiple primary domains.
8. Importance, future potential and evidence confidence are independent scores.
9. Retail matrix, Crypto matrix and Structural Trend Indicator Panel are executable report requirements.
10. Taiwan direct evidence and Taiwan implication remain separate fields.
```

### Runtime foundation accepted

```text
fixture ingestion and replay
live RSS/Atom adapter
source registry and OPML validation
URL normalization and de-duplication
event clustering and lane separation
coverage gap generation
report schema and executable contract validation
optional SQLite report/gap persistence
```

### Production boundary

```text
Web/API/social/FreshRSS adapters are not complete.
External discovery providers are not connected.
Historical cross-run material-delta comparison is not complete.
Semantic scoring, Retail/Crypto evaluators and structural-indicator evaluators are not complete.
Scheduler and production credentials are not complete.
Therefore fixture and current live-rss runs must remain partial for global completeness.
```

### Result

```text
新增：config/runtime_contract.json
新增：config/source_registry.json
更新：src/radar runtime / adapter / repository / report contract
更新：schemas/report.schema.json
更新：SYSTEM_PROMPT.md / DEPENDENCY_MAP.md / AGENT_DEFINITION_MAP.md
更新：workflows / templates / CURRENT_STATE / README / navigation docs
更新：schema/sync-matrix.json
新增：runtime/RSS/SQLite/report-contract tests
紀錄：reports/execution_checks/2026-07-10_runtime_v2_contract_sync_and_live_rss_foundation.md
```

---

## 2026-07-10：intelligence runtime v2 成為 active contract（superseded in details by sync repair）

### Preserved decision

```text
1. Runtime and canonical config, not prose, define execution.
2. Slot caps are not completeness proof.
3. Major, potential and confidence are separate.
4. Taiwan direct evidence and implication are separate.
5. LLM handles semantic assistance; deterministic runtime handles source identity, fetching boundaries,
   de-duplication, counting, coverage, evidence trace and report validation.
```

The original `config/source_registry.yaml` wording is superseded by `config/source_registry.json`.

---

## 2026-07-09：quality gates and structural indicators（v1 implementation, semantics preserved）

```text
source audit before drafting
recent-event de-duplication
one primary domain per event
fresh material delta required
potential signals need fresh concrete anchors
Taiwan implication cannot replace Taiwan news
Retail and Crypto matrices required
Structural Trend Indicator Panel required
```

Active structural indicators:

```text
1. 生產力便車無法共享的 K 型經濟
2. AI 泡沫 / 過度投資趨勢
3. 品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾
```

The fixed-count parts of the v1 implementation are retired; runtime-v2 lane and coverage semantics apply.

---

## 2026-07-07：Retail / fashion and potential-signal taxonomy

```text
Retail domain includes consumer, social, apparel, fashion, trend, style, material, fit,
category, assortment and merchandising changes, not only channel news.
Potential signal candidate_type: 新領域 / 新應用 / 新概念 / 新趨勢.
Formation levels: 弱訊號 / 話題形成 / 趨勢形成 / 主流化中.
Many articles indicate topic formation; repeated real applications and commitments indicate trend formation.
```

---

## 2026-07-07：Technology anti-AI-overcapture and Taiwan crypto audit

```text
AI stories cannot consume Technology coverage without a technical milestone.
Technology scans at least six non-AI technical subdomains or exposes a gap.
Taiwan crypto cannot be marked no-news when fixed sources or legislative triggers were not checked.
DA 交易者聯盟 and 邦妮區塊鏈 require verified direct-channel checks when relevant.
加密城市 and 區塊勢 are canonical Taiwan crypto registry sources.
```

---

## 2026-07-07：feed and discovery stack

```text
RSSHub and FreshRSS are collection adapters, not evidence stores.
GDELT / Media Cloud / Event Registry / NewsCatcher are discovery providers, not final evidence.
Discovery findings must resolve to original sources.
New weak signals may enter memory/potential_pool.md before output-stage selection.
```

---

## 2026-07-06：brain-core mount and extensible domain packs

```text
Governance mount: o00362002/brain-core.
New subject packs live under domains/ and must map to canonical report domains unless the runtime contract changes.
Capture stage does not prefilter potential signals.
```

---

## 2026-07-02：source-first search

```text
canonical source registry
→ source health and adapters
→ fixed query recipes
→ generic fallback for gaps
→ external discovery
→ coverage audit
```

## Older history

Older decisions remain in Git history and archive files. Frozen v1 fixed-count specifications are not current execution authority.
