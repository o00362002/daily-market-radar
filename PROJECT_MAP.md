# daily-market-radar｜PROJECT_MAP

本檔是專案導航圖，屬於 Projection，不是 source of truth。

Source of truth：

```text
Current mount: brain.manifest.yaml（core: o00362002/brain-core）
Execution entry: AGENTS.md
Current state: CURRENT_STATE.md
Current decisions: CURRENT_DECISIONS.md
Agent map and task routing: AGENT_DEFINITION_MAP.md
Dependency and completion gates: DEPENDENCY_MAP.md
Source-library routing: configs/source_routing_rules.yml, SOURCE_LIBRARY_SPEC.md, sources/
```

---

## 1. 掛載定位

```text
Core repo: o00362002/brain-core（蒸餾核，2026-07-06 起）
原則: P1–P5（規則必有機器消費者／入口極薄／資料驅動／模型無關層最厚／記憶輪替）
Role: recurring intelligence workflow ＋ 多領域新聞趨勢掃描
舊母腦: Human-AI-Collaboration-Brain 已退役
```

---

## 2. 入口檔

```text
AGENTS.md（第一入口，按需路由）
CLAUDE.md（薄適配器）
brain.manifest.yaml
README.md
CURRENT_STATE.md / CURRENT_DECISIONS.md
AGENT_DEFINITION_MAP.md / DEPENDENCY_MAP.md
```

---

## 3. 核心模組

```text
configs/          雷達規則、來源路由、查詢配方、freshness、retry、edge case
sources/          固定來源庫（六大核心領域媒體＋官方/數據來源）
domains/          領域包擴充機制（新領域可插拔;_template 為起點）
memory/           漏抓案例、來源實驗、watchlist、潛力池
templates/        日報/推播/搜尋/內容模板
workflows/        每日雷達、推播、主題搜尋、內容轉寫流程
skill_specs/ tools/ agent_specs/  訊號搜尋、claim risk、coverage、社群渠道讀取
reports/          日報、回測、execution checks（證據層）
loops/ evals/     回測補漏迴圈、冷讀評測
```

Source-library module:

```text
SOURCE_LIBRARY_SPEC.md = source-first method and schema
configs/source_routing_rules.yml = source routing and coverage audit rules
sources/key_media_library.yml = global and Taiwan key media by radar domain
sources/official_and_data_sources.yml = official, regulator, company, market, macro, chain, and data sources
```

---

## 4. 多領域新聞趨勢掃描

```text
六大核心領域: configs/radars.yml（canonical，不動）
新領域: domains/<domain_id>/domain_pack.json ＋ sources.json（spec: domains/README.md）
固定查詢配方: configs/query_recipes.yml ＋ 領域包內 query_recipes（弱模型照抄執行）
潛力池: memory/potential_pool.md（蒐集階段不預篩，configs/edge_case_discovery.yml capture_no_prefilter）
完整性檢查: tools/brain/check-domain-packs.js（commit 關口自動驗）
研究依據: research/global_news_trend_projects_2026-07-06.md
```

---

## 5. Active Workflows

```text
workflows/daily_radar_workflow.md = full research / archive daily radar
workflows/daily_push_brief_workflow.md = concise daily push brief
workflows/news_search_content_workflow.md = standalone topic news search and report
workflows/news_content_workflow.md = convert confirmed / labelled signals into readable content
```

Search workflows use source library and fixed query recipes before generic keyword fallback.

---

## 6. Active Agents

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

## 7. Routing

```text
Task routing lives inside AGENT_DEFINITION_MAP.md.
No standalone ROUTING.md is active.
```

---

## 8. Frozen History

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
ADOPTION_LEVELS.md
```

These files are retained for historical context only. They are not active routing or active source of truth.

---

## 9. 連動

連動關係唯一住在 `schema/sync-matrix.json`；commit 時 check-sync-matrix 自動提醒。
