# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-07-10

---

## 2026-07-10：runtime v2 contract sync repair

### Decision

```text
1. config/runtime_contract.json is the canonical machine execution/output contract.
2. config/source_registry.json is the canonical source identity and adapter registry.
3. Daily Push slot caps are readability limits; Full profile outputs qualified items within run budget.
4. Fixed-count completion rules (3+3 / 5+5 / 48-signal / 60-signal) are frozen v1 behavior.
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
