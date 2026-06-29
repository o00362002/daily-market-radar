# FROZEN HISTORY｜Daily Market Radar｜Agent Model Adoption Plan

Frozen status: historical reference only.

This file preserves the old Agent Model adoption planning context. It is no longer a current routing entry, source of truth, or active architecture rule.

Current mount architecture:

```text
Mother brain: o00362002/Human-AI-Collaboration-Brain
Current child entry: brain.manifest.yaml + AGENTS.md
Current rules: v1.18 convergence mount contract
```

Do not use this file to override:

```text
brain.manifest.yaml
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
```

---

# Historical Content

# Daily Market Radar｜Agent Model Adoption Plan

本檔說明 `daily-market-radar` 如何套用 Agent / Workflow / Skill / Tool / Loop 模型。

---

## 1. 新增檔案

```text
AGENT_DEFINITION_MAP.md
workflows/README.md
skill_specs/README.md
tools/README.md
loops/README.md
```

---

## 2. 目的

將每日市場情報流程從單一報告生成，拆成可檢查的情報作業系統：

```text
Radar Agents
→ Workflows
→ Skills
→ Tools
→ Loops
```

---

## 3. 不改變的原則

- 本 repo 仍以 `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` 為入口層。
- Agent model 只補充責任分層，不取代既有 configs / memory / templates / reports。
- Web search 是 Tool，不是 Agent。
- 每日報告仍需證據分級、來源、跨日去重與漏抓回測。

---
