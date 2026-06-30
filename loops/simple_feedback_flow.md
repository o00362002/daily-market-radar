# Simple Feedback Flow

Use this when the user gives feedback or correction after an AI / agent / Codex run.

Default behavior: keep feedback simple. Do not open formal backtest or rule governance unless escalation is triggered.

---

## Default Flow

```text
User feedback
→ AI classifies feedback type
→ AI decides adjustment complexity
→ AI proposes the smallest local adjustment
→ Human confirms once only when needed
→ AI updates the relevant skill / workflow / template / config
→ Next run uses the corrected version
```

---

## Default Output

```text
Issue found:
Feedback type:
Adjustment level:
Adjustment:
Files / skill affected:
Needs your confirmation: yes / no
Escalation needed: no / yes
```

---

## Feedback Type to Adjustment Level

| Feedback type | Adjustment level | Default action |
|---|---|---|
| wording / format correction | output only | adjust wording, format, labels, or final response style |
| one-step operation error | skill step | revise the exact step, selector, command, or wait condition |
| missing check in same workflow | workflow local | add a local validation or retry step |
| repeated same error | skill / workflow review | revise skill and record lightweight note |
| cross-skill inconsistency | template / workflow | align shared template or workflow behavior |
| source-of-truth conflict | rule / decision | escalate to formal backtest and sync check |
| routing or index issue | index / dependency | check HIGH_LEVEL_INDEX.md / DEPENDENCY_MAP.md impact |
| new deterministic failure pattern | checker / schema | consider checker or schema only if repeated and stable |
| strategic or risky decision | human / decision gate | require one human confirmation |

---

## Do Not Ask By Default

Do not ask by default:

```text
Should this become a rule?
Should this update HIGH_LEVEL_INDEX.md?
Should this become a Core decision?
```

Only mention these when escalation is actually required.

---

## Escalation Triggers

Escalate only when:

```text
same issue repeats 2-3 times
multiple skills / workflows / agents are affected
source-of-truth routing is affected
HIGH_LEVEL_INDEX.md is affected
CURRENT_STATE.md or CURRENT_DECISIONS.md is affected
new checker / schema / template is needed
active route is removed or archived
material operational risk exists
user explicitly asks for formal review / backtest / retrospective
```

---

## Default Rule

```text
Small feedback → small local fix.
Repeated feedback → review skill / workflow.
Cross-system feedback → formal backtest.
Source-of-truth feedback → decision / sync check.
```
