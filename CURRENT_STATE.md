# daily-market-radar｜CURRENT_STATE

最後更新：2026-07-05

---

## 1. 目前掛載深度

```text
Mother brain: o00362002/Human-AI-Collaboration-Brain
Mother version: v2.0-draft
Mother architecture: compact_five_layer
Mount mode: active thin mount
Legacy alias: Level 2
Capabilities: entry, state, decisions, routing
Complexity signals: generates-output
```

`Level 2` 只作 legacy alias。正式判斷以 `brain.manifest.yaml` 的 capabilities / complexity_signals / depth_note 為準。

---

## 2. 2026-07-05 mother-brain v2 sync

```text
README.md updated to Mount Depth model
AGENTS.md updated to Mother Brain v2 Mount Contract
brain.manifest.yaml updated to mother_version v2.0-draft and capabilities
CURRENT_STATE.md updated to remove v1.19 / formal Level wording
```

Inherited mother contracts:

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

---

## 3. 目前定位

```text
recurring intelligence workflow / daily report system
```

---

## 4. 入口邊界

```text
AGENTS.md = Agent-first execution entry
brain.manifest.yaml = thin mount manifest
SYSTEM_PROMPT.md = local instruction policy / daily radar quality policy
PROJECT_MAP.md = project navigation projection
HIGH_LEVEL_INDEX.md = high-level projection index
CURRENT_STATE.md = current reality
CURRENT_DECISIONS.md = accepted decisions
DEPENDENCY_MAP.md = dependency map
SOURCE_LIBRARY_SPEC.md + sources/ = local source-library execution module
```

Agent / Codex / Claude Code 執行任務時，第一入口是 `AGENTS.md`。

`SYSTEM_PROMPT.md` 定義每日雷達品質標準與報告規格，但不取代 `AGENTS.md`。

---

## 5. 目前判斷

```text
具備固定 workflow、configs、sources、memory、templates、reports 與 loop checklist。
Mount depth = entry + state + decisions + routing。
不需要升級成 multi-agent product runtime。
```

Search / radar collection is moving from keyword-first to source-library-first:

```text
fixed source library
→ source-scoped keyword and topic filtering
→ generic keyword fallback
→ external discovery
→ coverage audit
```

Backtest 也要檢查專案成長控制：

```text
keep / revise / delete / archive / add / promote / demote / observe
```

---

## 6. Frozen History

以下舊過渡檔已凍結，只保留歷史脈絡，不再作為 current routing / source of truth / active rule：

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
```
