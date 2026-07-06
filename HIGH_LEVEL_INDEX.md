# daily-market-radar｜HIGH_LEVEL_INDEX

本檔是高階索引，屬於 Projection，不是 source of truth。

Source of truth：

```text
brain.manifest.yaml（core: o00362002/brain-core）
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
```

---

## 1. 一句話定位

```text
每日市場情報雷達（recurring intelligence workflow）＋ 多領域新聞趨勢掃描
掛載 brain-core：規則是資料＋檢查器，在 commit 關口自己出現。
```

---

## 2. 核心模組

```text
configs / sources / domains / memory / templates / reports / workflows /
skill_specs / tools / agent_specs / loops / evals
```

Source-library module:

```text
SOURCE_LIBRARY_SPEC.md
configs/source_routing_rules.yml
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

Domain extension module:

```text
domains/README.md ＋ domains/_template/
configs/query_recipes.yml
memory/potential_pool.md
tools/brain/check-domain-packs.js
```

---

## 3. Active Output Modes

```text
Full Daily Radar = full research / archive output, uses workflows/daily_radar_workflow.md and templates/daily_report_template.md
Daily Push Brief = concise daily user-facing output, uses workflows/daily_push_brief_workflow.md and templates/daily_push_brief_template.md
News Search Output = standalone topic news search, uses workflows/news_search_content_workflow.md and templates/news_search_content_template.md
News Content Output = converts selected news / radar signals into content, uses workflows/news_content_workflow.md and templates/news_content_template.md
```

Search outputs use source library and fixed query recipes before generic keyword fallback.

---

## 4. Active Agents

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

## 5. Routing

```text
Task routing lives inside AGENT_DEFINITION_MAP.md.
No standalone ROUTING.md is active.
```

---

## 6. Frozen History

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
ADOPTION_LEVELS.md
```

---

## 7. 回答時必須避免

```text
不要把 thin mount 寫成完整複製核心架構
不要把尚未產品化的內容寫成已完成
不要把 frozen history 當成 current state
不要把 Projection 當成 source of truth
不要把 Daily Push Brief 寫成完整 48-signal formal report
不要把 news_search_agent 的指定主題新聞寫成完整每日市場雷達
不要把 news_content_agent 的內容稿寫成已驗證情報判斷
不要把來源庫檢查寫成已完成，除非實際讀取 sources/ 與 source routing rules
不要在蒐集階段替使用者篩掉潛力項目；篩選只發生在輸出階段且留紀錄
不要用模型自由發想的查詢取代固定查詢配方；補充查詢需在 coverage audit 揭露
```
