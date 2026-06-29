# AGENTS.md

Thin-mount entry for agents.

This file is not the source of truth. It is the execution entry for `daily-market-radar`.

Level: Level 2 Runtime-Lite Brain.

Parent framework rules:

```text
Human-AI-Collaboration-Brain/rules/universal_execution_contract.md
Human-AI-Collaboration-Brain/rules/high_level_index_update_policy.md
Human-AI-Collaboration-Brain/rules/optional_adapter_applicability_check.md
```

Core rule:

```text
Level controls structure depth.
Execution Contract is universal.
```

Read first:

1. SYSTEM_PROMPT.md
2. PROJECT_MAP.md
3. HIGH_LEVEL_INDEX.md
4. CURRENT_STATE.md
5. CURRENT_DECISIONS.md
6. README.md
7. DEPENDENCY_MAP.md

Then read task-specific files in configs, memory, templates, workflows, loops, and recent reports.

Level 2 execution path:

```text
Entry Gate: read the required entry files above
Plan Gate: state intended report / config / workflow change
Execution Gate: follow the relevant workflow, checklist, template, or loop
Reality / Sync Gate: compare planned vs actual result before declaring complete
```

Completion check:

- radar coverage
- fixed indicators
- source retry status
- missed-case check
- backtest or adjustment note
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
Reality check:
Sync check:
HIGH_LEVEL_INDEX.md update needed? yes / no
Optional adapters checked? yes / no
Auto Sync / Auto PR active or requested? yes / no
Status: complete / partial change / No downstream sync required
Next required action:
```

If required source checks, workflow steps, sync, index check, optional adapter check, or reality check are incomplete, mark the work as `partial change`.
