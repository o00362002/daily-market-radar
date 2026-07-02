# daily-market-radar｜HIGH_LEVEL_INDEX

本檔是高階索引，屬於 Projection，不是 source of truth。

Source of truth：

```text
brain.manifest.yaml
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
```

---

## 1. 指定 Level

```text
Level 2 Runtime-Lite Brain
```

---

## 2. 一句話定位

```text
recurring intelligence workflow / daily report system
```

---

## 3. 核心模組

```text
configs / sources / memory / templates / reports / workflows / radar rules / source library / search retry / post-report review
```

Source-library module:

```text
SOURCE_LIBRARY_SPEC.md
configs/source_routing_rules.yml
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

---

## 4. Active Output Modes

```text
Full Daily Radar = full research / archive output, uses workflows/daily_radar_workflow.md and templates/daily_report_template.md
Daily Push Brief = concise daily user-facing output, uses workflows/daily_push_brief_workflow.md and templates/daily_push_brief_template.md
News Search Output = standalone topic news search, uses workflows/news_search_content_workflow.md and templates/news_search_content_template.md
News Content Output = converts selected news / radar signals into content, uses workflows/news_content_workflow.md and templates/news_content_template.md
```

Search outputs now use source library before generic keyword fallback.

---

## 5. Active Agents

```text
radar_report_agent
news_search_agent
news_content_agent
```

Boundary:

```text
radar_report_agent searches and grades cross-domain daily radar signals.
news_search_agent searches and grades one specified news topic.
news_content_agent writes content from already graded / labelled signals.
news_content_agent must not upgrade evidence or replace radar search.
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
Frozen history is not current state.
Backtest also checks keep / revise / delete / archive / add / promote / demote.
Schema coverage must not be overstated.
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

## 9. 回答時必須避免

```text
不要把 repo Level 與 module Level 混在一起
不要把 thin mount 寫成完整複製母架構
不要把尚未產品化的內容寫成已完成
不要把 frozen history 當成 current state
不要把 Projection 當成 source of truth
不要把 Daily Push Brief 寫成完整 48-signal formal report
不要把 news_search_agent 的指定主題新聞寫成完整每日市場雷達
不要把 news_content_agent 的內容稿寫成已驗證情報判斷
不要把來源庫檢查寫成已完成，除非實際讀取 sources/ 與 source routing rules
```
