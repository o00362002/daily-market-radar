# AGENTS.md

Agent-first entry for AI agents, Codex, Claude Code, and other repo-working executors.

This file is a Projection adapter and Execution Edge entry point for `daily-market-radar`. It is not the source of truth.

```text
Mother repo: o00362002/Human-AI-Collaboration-Brain
Mother version: v2.0-draft
Mount mode: active thin mount
Legacy alias: Level 2
Capabilities: entry, state, decisions, routing
```

---

## 1. Entry Boundary

```text
AGENTS.md = Agent-first execution entry
brain.manifest.yaml = thin mount manifest
SYSTEM_PROMPT.md = local instruction policy / daily radar quality policy
PROJECT_MAP.md = project navigation projection
HIGH_LEVEL_INDEX.md = high-level projection index
CURRENT_STATE.md = current reality
CURRENT_DECISIONS.md = accepted decisions
DEPENDENCY_MAP.md = dependency map
AGENT_DEFINITION_MAP.md = agent definition + task routing + workflow/template selection
loops/simple_feedback_flow.md = simple feedback flow for user corrections
```

Agent / Codex / Claude Code execution must start here.

`SYSTEM_PROMPT.md` may define daily radar quality standards and report rules, but it is not the Agent-first entry and does not replace this file.

---

## 2. Mother Brain v2 Mount Contract

This child repo inherits the mother Brain compact five-layer architecture and vocabulary.

```text
1. Brain Core / Charter
2. Interface & Integration Layer
3. Memory Layer
4. Context Routing Layer
5. Execution Edge
```

Inherited contracts:

```text
BRAIN_ARCHITECTURE.md
MOUNT_DEPTH.md
schema/INDEX.md
rules/universal_execution_contract.md
rules/role_boundary_contract.md
specs/execution_edge_module_model.md
specs/programmable_control_layer.md
specs/flow_selection_and_enforcement.md
```

Core rule:

```text
Mount Depth controls local structure depth.
Level names are legacy capability aliases only.
Execution Contract is universal.
Role Boundary Contract is universal.
Interface exposes access, not authority.
Adoption Gate belongs under Interface & Integration Layer.
Flow Profile may reduce flow load but cannot disable enforcement floor.
```

Do not read the entire mother Brain by default. Use task type to decide read depth.

| Task type | Required read depth |
|---|---|
| Daily report / normal local work | Local project understanding layer + task-specific files. |
| User feedback / correction | Use `loops/simple_feedback_flow.md` first. |
| Workflow / skill / tool / loop change | Also check mother execution and role-boundary contracts when needed. |
| Schema / checker / sync / completion-status change | Also check mother schema and programmable-control contracts when needed. |
| Architecture / mount-depth / mount change | Read mother Core + child Core and require human review. |

If mother contract files are required but cannot be read, mark the work as `partial change`.

---

## 3. Read First

Agent execution must read in this order:

```text
1. AGENTS.md

2. Project understanding layer
   - brain.manifest.yaml
   - PROJECT_MAP.md
   - HIGH_LEVEL_INDEX.md
   - CURRENT_STATE.md
   - CURRENT_DECISIONS.md
   - README.md
   - DEPENDENCY_MAP.md

3. Agent / task selection layer
   - AGENT_DEFINITION_MAP.md

4. Local policy layer
   - SYSTEM_PROMPT.md
```

Then choose the task route from `AGENT_DEFINITION_MAP.md`.

For user feedback, correction, or post-run adjustment, read:

```text
loops/simple_feedback_flow.md
```

Then read task-specific files only as needed:

```text
workflows/
templates/
configs/
memory/
reports/
loops/
evals/
sources/
```

If required files cannot be read, mark the work as `partial change`; do not pretend the read happened.

---

## 4. Execution Flow

```text
AGENTS.md
→ Project understanding layer
→ AGENT_DEFINITION_MAP.md
→ choose Agent / Workflow / Template
→ read task-specific configs / memory / reports / templates / sources
→ execute
→ completion check
```

Do not select a workflow only from the user sentence before understanding the current project state and decisions.

Memory is task-specific execution context. It should be read after the task route is selected, unless the task itself is to inspect or modify memory.

---

## 5. Role Boundary

```text
Agent owns outcome but cannot approve itself.
Workflow orders forward execution only.
Skill judges search / coverage quality when defined.
Tool performs concrete action or check without semantic judgement.
Loop reviews, rejects, retries, backtests, and proposes improvement.
Human / Decision Gate approves non-mechanizable semantic changes.
Evidence does not become Memory without approval.
```

---

## 6. Simple Feedback Flow

For user feedback after an AI / agent / Codex run, use:

```text
loops/simple_feedback_flow.md
```

Default behavior:

```text
Classify feedback type → decide adjustment complexity → propose the smallest local fix → ask one confirmation only when needed.
```

Do not ask by default whether the feedback should become a rule, update `HIGH_LEVEL_INDEX.md`, or become a Core decision.

Only escalate when the simple feedback flow says escalation is required.

---

## 7. Post-Execution Rule

After any task that changes files, routes, tools, state, decisions, workflows, reports, sources, or evidence, perform a lightweight post-execution check.

Required check:

```text
1. What changed?
2. Which route / agent / workflow was used?
3. Which files were read or changed?
4. Did checker / validation pass?
5. Is there evidence?
6. Is there a failure attribution?
7. Is dependency / sync impact local only, child repo level, or mother Brain level?
8. Is a Memory Patch Candidate needed?
```

If the change affects local project memory, dependency gates, route selection, source library, or reusable workflow behavior, record it through the local backtest / decision process before treating it as durable.

Do not promote evidence into memory automatically. Do not push child repo implementation details into the mother Brain unless they affect cross-repo governance.
