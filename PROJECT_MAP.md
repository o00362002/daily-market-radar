# daily-market-radar｜PROJECT_MAP

本檔是專案導航圖，屬於 Projection，不是 source of truth。

Source of truth：

```text
Current mount: brain.manifest.yaml
Execution entry: AGENTS.md
Current state: CURRENT_STATE.md
Current decisions: CURRENT_DECISIONS.md
Mother architecture: o00362002/Human-AI-Collaboration-Brain
```

---

## 1. 掛載定位

```text
Level: Level 2 Runtime-Lite Brain
Role: recurring intelligence workflow / daily report system
Mother version: v1.18-draft
Mount mode: active thin mount
```

---

## 2. 固定入口檔

```text
README.md
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENTS.md
AGENT_DEFINITION_MAP.md
brain.manifest.yaml
```

---

## 3. 核心模組

```text
configs / memory / templates / reports / workflows / radar rules / search retry / post-report review
```

---

## 4. Active Workflows

```text
workflows/daily_radar_workflow.md = full research / archive daily radar
workflows/daily_push_brief_workflow.md = concise daily push brief
workflows/news_content_workflow.md = convert confirmed / labelled signals into readable content
```

---

## 5. Active Agents

```text
radar_report_agent = produces radar reports and concise daily push briefs
news_content_agent = converts radar signals into news briefs, trend notes, social posts, or article drafts
```

Boundary:

```text
news_content_agent does not perform full radar search and does not upgrade evidence.
```

---

## 6. Convergence Notes

```text
Projection files create no canonical rules.
Evidence does not become Memory without approval.
Frozen history is preserved but removed from active routing.
Backtest includes keep / revise / delete / archive / add / promote / demote.
```

---

## 7. Frozen History

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
```

---

## 8. 同步檢查

重大變更時檢查：

```text
CURRENT_STATE.md
CURRENT_DECISIONS.md
HIGH_LEVEL_INDEX.md
DEPENDENCY_MAP.md
AGENTS.md
AGENT_DEFINITION_MAP.md
brain.manifest.yaml
check_mount_integrity.sh
```