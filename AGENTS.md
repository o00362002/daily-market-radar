# AGENTS.md

Agent-first entry for AI agents, Codex, Claude Code, and other repo-working executors.

This file is a Projection adapter and Execution Edge entry point for `daily-market-radar`.

It is not the source of truth.

Level: Level 2 Runtime-Lite Brain.

---

## 1. Entry Boundary

```text
AGENTS.md = Agent-first execution entry
SYSTEM_PROMPT.md = local instruction policy / daily radar quality policy
PROJECT_MAP.md = project navigation projection
HIGH_LEVEL_INDEX.md = high-level projection index
CURRENT_STATE.md = current reality
CURRENT_DECISIONS.md = accepted decisions
DEPENDENCY_MAP.md = dependency map
AGENT_DEFINITION_MAP.md = agent definition + task routing + workflow/template selection
brain.manifest.yaml = thin mount manifest
```

Agent / Codex / Claude Code execution must start here.

`SYSTEM_PROMPT.md` may define daily radar quality standards and report rules, but it is not the Agent-first entry and does not replace this file.

---

## 2. BRAIN_ARCHITECTURE

This repo is mounted under:

```text
o00362002/Human-AI-Collaboration-Brain
```

Before local execution, use the mother Brain architecture to identify:

```text
mother repo
child repo
child Level
mount mode
inherited contracts
```

Do not read the entire mother Brain by default.

Use the task type to decide read depth:

| Task type | Required read depth |
|---|---|
| Daily report / normal local work | Local project understanding layer + task-specific files. |
| Workflow / skill / tool / loop change | Also check mother execution and role-boundary contracts when needed. |
| Schema / checker / sync / completion-status change | Also check mother schema and programmable-control contracts when needed. |
| Architecture / Level / mount change | Read mother Core + child Core and require human review. |

If mother contract files are required but cannot be read, mark the work as `partial change`.

---

## 3. v1.18 Mount Contract

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

Core rule:

```text
Level controls structure depth.
Execution Contract is universal.
Role Boundary Contract is universal.
Adoption Layer is not Execution Edge.
```

---

## 4. Read First

Agent execution must read in this order:

```text
1. AGENTS.md

2. Project understanding layer
   - PROJECT_MAP.md
   - HIGH_LEVEL_INDEX.md
   - CURRENT_STATE.md
   - CURRENT_DECISIONS.md
   - README.md
   - DEPENDENCY_MAP.md
   - brain.manifest.yaml

3. Agent / task selection layer
   - AGENT_DEFINITION_MAP.md

4. Local policy layer
   - SYSTEM_PROMPT.md
```

Then choose the task route from `AGENT_DEFINITION_MAP.md`.

Then read task-specific files only as needed:

```text
workflows/
templates/
configs/
memory/
reports/
loops/
evals/
```

If required files cannot be read, mark the work as `partial change`; do not pretend the read happened.

---

## 5. Execution Flow

```text
AGENTS.md
→ Project understanding layer
→ AGENT_DEFINITION_MAP.md
→ choose Agent / Workflow / Template
→ read task-specific configs / memory / reports / templates
→ execute
→ completion check
```

Do not select a workflow only from the user sentence before understanding the current project state and decisions.

Memory is task-specific execution context. It should be read after the task route is selected, unless the task itself is to inspect or modify memory.

---

## 6. Convergence Mount Rules

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

## 7. Role Boundary Gate

Before execution, classify whether the task is Agent / Workflow / Skill / Tool / Loop / Human / Decision Gate / Memory.

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

## 8. Level 2 Execution Path

```text
Entry Gate: read AGENTS.md and project understanding layer
Agent Selection Gate: read AGENT_DEFINITION_MAP.md and choose Agent / Workflow / Template
Dependency Gate: check impacted configs, memory, templates, workflows, loops, and reports
Role Boundary Gate: classify the task boundary
Plan Gate: state intended report / config / workflow change
Execution Gate: follow the relevant workflow, checklist, template, or loop
Post-Action Check / Backtest Gate: check radar coverage, missed cases, evidence, and growth control when applicable
Reality / Sync Gate: compare planned vs actual result before declaring complete
```

---

## 9. Completion Check

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
HIGH_LEVEL_INDEX.md update needed? yes / no
Optional adapters checked? yes / no
Auto Sync / Auto PR active or requested? yes / no
Status: complete / partial change / No downstream sync required
Next required action:
```

If required source checks, workflow steps, role boundary check, frozen history check, sync, index check, optional adapter check, or reality check are incomplete, mark the work as `partial change`.
