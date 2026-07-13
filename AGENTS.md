# daily-market-radar｜AGENTS

`AGENTS.md` is the minimal AI routing adapter for this repository. It does not own governance definitions, current counts, report quotas, or source inventories.

## Entry flow

```text
1. Read AGENTS.md.
2. Open only the owner required by the task.
3. For persistent changes, inspect brain.manifest.yaml and the relevant dependency/checker path.
4. Run bash check_mount_integrity.sh before completion.
```

## Stable routes

```text
Current facts                  → CURRENT_STATE.md
Accepted decisions             → CURRENT_DECISIONS.md
Task / report route            → AGENT_DEFINITION_MAP.md
Source selection contract      → SOURCE_LIBRARY_SPEC.md
Canonical runtime quotas       → config/runtime_contract.json
Query recipes                  → configs/query_recipes.yml
Domain-pack extension          → domains/README.md
Potential-signal pool          → memory/potential_pool.md
Machine checker mapping        → brain.manifest.yaml
Dependency / sync reminders    → schema/sync-matrix.json
```

Routine reporting and research stay local to this repository. Governance definitions are supplied by the profile named in `brain.manifest.yaml`; this file does not copy them.

## Radar boundaries

```text
Fixed source libraries and query recipes run before generic-search fallback.
Taiwan-news slots require direct Taiwan evidence; inferred Taiwan impact is labelled inference.
Every accepted signal needs a current delta; unchanged historical replay does not fill a slot.
Social-first coverage requires direct-channel checks.
Capture is broad; output selection happens after collection.
Major policy, legal and market claims require primary or authoritative verification.
Evidence does not become durable memory without promotion.
Frozen history is not current authority.
```

## Completion

```text
machine checks green
+ what changed
+ what did not change
+ affected runtime/domain paths
+ remaining uncertainty
+ user-verifiable result
```

Install local gate once: `bash tools/install_hooks.sh`

Run repository validation: `bash check_mount_integrity.sh`
