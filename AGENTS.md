# AGENTS.md

Thin-mount entry for agents.

This file is not the source of truth. It is the execution entry for `daily-market-radar`.

Level: Level 2 Runtime-Lite Brain.

---

## v1.18 Mount Contract

Mother brain:

```text
o00362002/Human-AI-Collaboration-Brain
```

Inherited contracts:

```text
BRAIN_ARCHITECTURE.md
ADOPTION_LEVELS.md
schema/INDEX.md
rules/universal_execution_contract.md
rules/role_boundary_contract.md
specs/execution_edge_module_model.md
specs/programmable_control_layer.md
```

Execution path:

```text
Entry
→ Dependency
→ Role Boundary
→ Plan
→ Execution
→ Post-Action Check / Backtest
→ Reality / Sync
```

Role boundary:

```text
Brain never executes.
Agent executes but cannot approve itself.
Workflow orders forward execution only.
Skill judges.
Tool operates without judgement.
Loop rejects, retries, backtests, and proposes improvement.
Programmable Control enforces only what code can check.
Human final review is required for non-mechanizable decisions.
Decision Gate promotes evidence into system change.
Memory stores only confirmed state and decisions.
```

---

## Convergence Mount Rules

This child repo inherits the mother Brain convergence rules.

```text
Core = files that define current state and active rules.
Projection = files that point to Core, but create no canonical rule.
Evidence = reports, checks, and backtests; not Memory until approved.
Archive / Frozen History = preserved context, not current state.
```

Backtest is also growth control. When the project grows, review:

```text
keep / revise / delete / archive / add / promote / demote
```

Before adding new rules, workflows, skills, loops, schemas, or prose files, first check whether the issue can be solved by:

```text
freezing history
lowering projection authority
pointing back to Core
removing duplicate prose
archiving outdated content
```

Schema coverage must be described honestly:

```text
Class A = schema-backed enforcement
Class B = deterministic presence / reference check
Class C = prose-guided judgement only
```

Do not describe this repo as fully code-enforced unless the specific invariant has schema + validator / shell / CI coverage.

---

## Parent framework rules

```text
Human-AI-Collaboration-Brain/rules/universal_execution_contract.md
Human-AI-Collaboration-Brain/rules/role_boundary_contract.md
Human-AI-Collaboration-Brain/specs/programmable_control_layer.md
Human-AI-Collaboration-Brain/rules/high_level_index_update_policy.md
Human-AI-Collaboration-Brain/rules/optional_adapter_applicability_check.md
```

Core rule:

```text
Level controls structure depth.
Execution Contract is universal.
Role Boundary Contract is universal.
Adoption Layer is not Execution Edge.
```

Read first:

1. SYSTEM_PROMPT.md
2. PROJECT_MAP.md
3. HIGH_LEVEL_INDEX.md
4. CURRENT_STATE.md
5. CURRENT_DECISIONS.md
6. README.md
7. DEPENDENCY_MAP.md
8. brain.manifest.yaml

Then read task-specific files in configs, memory, templates, workflows, loops, and recent reports.

Level 2 execution path:

```text
Entry Gate: read the required entry files above
Dependency Gate: check impacted configs, memory, templates, workflows, loops, and reports
Role Boundary Gate: classify whether the task is Agent / Workflow / Skill / Tool / Loop / Human / Decision Gate / Memory
Plan Gate: state intended report / config / workflow change
Execution Gate: follow the relevant workflow, checklist, template, or loop
Post-Action Check / Backtest Gate: check radar coverage, missed cases, evidence, and growth control when applicable
Reality / Sync Gate: compare planned vs actual result before declaring complete
```

Completion check:

- radar coverage
- fixed indicators
- source retry status
- missed-case check
- backtest or adjustment note
- growth control check when project scope expands
- frozen history check when old adoption / plan files are touched
- role boundary check
- plan vs actual action check
- sync status
- HIGH_LEVEL_INDEX.md update need
- optional adapter need

Required completion report:

```text
Read set:
Planned action:
Actual action:
Files changed:
Role boundary check:
Frozen history / growth control check:
Reality check:
Sync check:
HIGH_LEVEL_INDEX.md update needed? yes / no
Optional adapters checked? yes / no
Auto Sync / Auto PR active or requested? yes / no
Status: complete / partial change / No downstream sync required
Next required action:
```

If required source checks, workflow steps, role boundary check, frozen history check, sync, index check, optional adapter check, or reality check are incomplete, mark the work as `partial change`.
