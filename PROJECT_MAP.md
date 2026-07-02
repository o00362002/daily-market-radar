# daily-market-radar｜PROJECT_MAP

本檔是專案導航圖，屬於 Projection，不是 source of truth。

Source of truth：

```text
Current mount: brain.manifest.yaml
Execution entry: AGENTS.md
Current state: CURRENT_STATE.md
Current decisions: CURRENT_DECISIONS.md
Agent map and task routing: AGENT_DEFINITION_MAP.md
Dependency and completion gates: DEPENDENCY_MAP.md
Source-library routing: configs/source_routing_rules.yml, SOURCE_LIBRARY_SPEC.md, sources/
Mother architecture: o00362002/Human-AI-Collaboration-Brain
```

---

## 1. 掛載定位

```text
Level: Level 2 Runtime-Lite Brain
Role: recurring intelligence workflow / daily report system
Mother version: v1.19-draft
Mother architecture: compact_five_layer
Mount mode: active thin mount
Layer depth: level_scaled
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
DEPENDENCY_MAP.md
brain.manifest.yaml
```

---

## 3. 核心模組

```text
configs / sources / memory / templates / reports / workflows / radar rules / source library / search retry / post-report review
```

Source-library module:

```text
SOURCE_LIBRARY_SPEC.md = source-first method and schema
configs/source_routing_rules.yml = source routing and coverage audit rules
sources/key_media_library.yml = global and Taiwan key media by radar domain
sources/official_and_data_sources.yml = official, regulator, company, market, macro, chain, and data sources
```

---

## 4. Active Workflows

```text
workflows/daily_radar_workflow.md = full research / archive daily radar
workflows/daily_push_brief_workflow.md = concise daily push brief
workflows/news_search_content_workflow.md = standalone topic news search and report
workflows/news_content_workflow.md = convert confirmed / labelled signals into readable content
```

Search workflows now use source library before generic keyword fallback.

---

## 5. Active Agents

```text
radar_report_agent = produces radar reports and concise daily push briefs
news_search_agent = searches a specified topic and outputs source-backed news
news_content_agent = converts selected news / radar signals into news briefs, trend notes, social posts, or article drafts
```

Boundary:

```text
news_search_agent handles standalone topic news search, but does not replace full daily radar.
news_content_agent does not perform broad search and does not upgrade evidence.
radar_report_agent and news_search_agent must check source library before generic keyword fallback.
```

---

## 6. Routing

```text
Task routing lives inside AGENT_DEFINITION_MAP.md.
No standalone ROUTING.md is active.
```

---

## 7. Convergence Notes

```text
Projection files create no canonical rules.
Evidence does not become Memory without approval.
Frozen history is preserved but removed from active routing.
Backtest includes keep / revise / delete / archive / add / promote / demote.
Adoption Gate belongs under Interface & Integration Layer.
Source library is local execution infrastructure, not mother Brain architecture.
```

---

## 8. Frozen History

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
```

---

## 9. 同步檢查

重大變更時檢查：

```text
CURRENT_STATE.md
CURRENT_DECISIONS.md
HIGH_LEVEL_INDEX.md
PROJECT_MAP.md
AGENTS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
SOURCE_LIBRARY_SPEC.md
configs/source_routing_rules.yml
sources/
brain.manifest.yaml
check_mount_integrity.sh
```
