# Frozen SYSTEM_PROMPT｜2026-06-29

This file freezes the previous long `SYSTEM_PROMPT.md` as historical reference.

The active root `SYSTEM_PROMPT.md` has been slimmed down to avoid context compression and execution drift.

---

## 1. Frozen source

Previous long prompt blob SHA:

```text
8ba8eb2cdbcb0dff7f401801582aa6cc98c71d8d
```

Temporary manual patch blob SHA found before cleanup:

```text
8f0bead30f6ee25849faab94e6fed33e7f9aaf42
```

---

## 2. Status

```text
status: frozen history
active_routing: false
source_of_truth: false
restorable: true
```

---

## 3. Restore rule

If the long prompt must be restored, recover it from Git history / blob SHA, then review it before promoting it back into active routing.

Do not directly treat this frozen history as current policy.

---

## 4. Why frozen

The old prompt carried too many roles:

```text
identity
read order
daily report specification
search strategy
hard gate
output format
backtest panel
user feedback handling
```

This created risk of:

```text
context compression
rule dilution
execution drift
SYSTEM_PROMPT acting like a workflow or runtime
```

The active system now uses:

```text
AGENTS.md = Agent-first execution entry
SYSTEM_PROMPT.md = thin local quality policy
workflows/ = execution flow
configs/ = radar parameters and search rules
templates/ = output structure
memory/ = watchlist and missed cases
reports/ = historical evidence
```
