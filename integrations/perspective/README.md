---
tier: consumer-entry
status: draft
execution: false
promotion: false
updated: 2026-08-09
---

# Perspective Capability｜Quick Entry

This is the local entry for using the central Perspective Capability in daily-market-radar.

Current access is a contract plus manual / AI-assisted bounded review. It is not a runtime API, autonomous Agent, or automatic implementation path.

## Read order

1. Read this entry and `consumer-adapter.yaml`.
2. Read the [canonical architecture](https://github.com/o00362002/personal-project-brain/blob/main/notes/adversarial-perspective-board/ARCHITECTURE.md}) and [Objective Layer](https://github.com/o00362002/personal-project-brain/blob/main/notes/adversarial-perspective-board/OBJECTIVE_LAYER.md}).
3. Read the [selected Objective Profile](https://github.com/o00362002/personal-project-brain/blob/main/notes/adversarial-perspective-board/objectives/daily-market-radar.signal-selection.yaml).
4. Select one [Purpose Mode contract](https://github.com/o00362002/personal-project-brain/tree/main/notes/adversarial-perspective-board/purpose_modes/) before asking for opinions.
5. Freeze the artifact, local context, objective and panel budget before the review.

## Project route

Primary objective: [daily-market-radar.signal-selection](https://github.com/o00362002/personal-project-brain/blob/main/notes/adversarial-perspective-board/objectives/daily-market-radar.signal-selection.yaml)
Task classes: signal_selection_review, content_review, architecture_review
Local criteria: `AGENTS.md`, `CURRENT_DECISIONS.md`, `SOURCE_LIBRARY_SPEC.md`
Local output route: `reports/`

## Quick use

Use this instruction at the start of an implementation or design task:

```text
Read integrations/perspective/README.md and consumer-adapter.yaml first.
Use the declared objective and choose one Purpose Mode.
Return isolated Review Opinions with claim, evidence, assumption, missing information, impact, confidence and minimum correction.
Do not edit the product or treat the review as a pass/fail decision.
Save the Review Packet in the local output route and wait for the project / human decision gate.
```

## Decision boundary

Perspective supplies additional viewpoints. This project remains the owner of its criteria, implementation, tests, operations, outcome and final decision. A review may suggest a change; it does not authorize the change.

Do not promote a Persona, activate a runtime, or convert an opinion into durable project truth from this entry alone.