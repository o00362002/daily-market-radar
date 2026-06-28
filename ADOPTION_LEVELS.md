# daily-market-radar｜ADOPTION_LEVELS

This file defines how `daily-market-radar` adopts the Human-AI Collaboration Brain architecture.

---

## 1. Repo Level

Current level:

```text
Level 2 runtime-lite
```

Reason:

```text
具備固定 workflow、configs、memory、templates、reports 與 loop checklist，但不需要升級成 Agent Product System。
```

---

## 2. Architecture Relationship

```text
Adopted architecture: Human-AI Collaboration Brain
Architecture repo: o00362002/Human-AI-Collaboration-Brain
Runtime dependency: none
Parent repo: none
Content source of truth: daily-market-radar
```

This repo is independent. The architecture repo provides method and structure, not project content.

---

## 3. Task Levels

Task levels are maintained in `CONTEXT_ROUTING.md`.

```text
T0 quick understanding
T1 status check
T2 module work
T3 architecture / tool / rule change
T4 execution / runtime / artifact
```

---

## 4. Module Level Rule

Modules should inherit root rules and record local tasks, state, decisions, and dependencies.

Suggested module / area:

```text
每日報告：SYSTEM_PROMPT.md, configs/, memory/, templates/, reports/
雷達設定：configs/
漏抓與 watchlist：memory/
歷史報告：reports/
輸出格式：templates/
```
