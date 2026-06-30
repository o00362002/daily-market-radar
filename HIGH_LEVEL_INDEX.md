# daily-market-radar｜HIGH_LEVEL_INDEX

本檔是高階索引，屬於 Projection，不是 source of truth。

Source of truth：

```text
brain.manifest.yaml
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENT_DEFINITION_MAP.md
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
configs / memory / templates / reports / workflows / radar rules / search retry / post-report review
```

---

## 4. Active Output Modes

```text
Full Daily Radar = full research / archive output, uses workflows/daily_radar_workflow.md and templates/daily_report_template.md
Daily Push Brief = concise daily user-facing output, uses workflows/daily_push_brief_workflow.md and templates/daily_push_brief_template.md
News Content Output = converts selected radar signals into content, uses workflows/news_content_workflow.md and templates/news_content_template.md
```

---

## 5. Active Agents

```text
radar_report_agent
news_content_agent
```

Boundary:

```text
radar_report_agent searches and grades signals.
news_content_agent writes content from already graded / labelled signals.
news_content_agent must not upgrade evidence or replace radar search.
```

---

## 6. Convergence Notes

```text
Projection files create no canonical rules.
Frozen history is not current state.
Backtest also checks keep / revise / delete / archive / add / promote / demote.
Schema coverage must not be overstated.
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

## 8. 回答時必須避免

```text
不要把 repo Level 與 module Level 混在一起
不要把 thin mount 寫成完整複製母架構
不要把尚未產品化的內容寫成已完成
不要把 frozen history 當成 current state
不要把 Projection 當成 source of truth
不要把 Daily Push Brief 寫成完整 48-signal formal report
不要把 news_content_agent 的內容稿寫成已驗證情報判斷
```