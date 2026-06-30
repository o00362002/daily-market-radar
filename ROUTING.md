# Daily Market Radar｜ROUTING

This file defines lightweight request routing for `daily-market-radar`.

It is a routing guide, not a new Agent and not a replacement for `AGENTS.md`.

---

## 1. Entry

All repo-working execution still starts from:

```text
AGENTS.md
```

Then route by request type.

---

## 2. Agent Router

| User request type | Agent | Workflow | Template |
|---|---|---|---|
| Daily market intelligence / daily radar / market radar report | `radar_report_agent` | `workflows/daily_radar_workflow.md` | `templates/daily_report_template.md` |
| Concise daily push / quick daily radar / automation-friendly brief | `radar_report_agent` | `workflows/daily_push_brief_workflow.md` | `templates/daily_push_brief_template.md` |
| Search latest news on a specific topic, e.g. technology news, AI news, retail news, crypto news, Taiwan business news | `news_search_agent` | `workflows/news_search_content_workflow.md` | `templates/news_search_content_template.md` |
| Rewrite / expand / explain / turn selected news into article, trend note, social post, retail angle | `news_content_agent` | `workflows/news_content_workflow.md` | `templates/news_content_template.md` |

---

## 3. Model Capability Routing

Use concise mode when:

```text
- model is fast / weak / limited-context
- user wants daily push, not full archive
- automation output must be stable
- full 48-signal search is too large for one pass
```

Use full radar mode when:

```text
- user explicitly asks for full formal report
- user asks for archive-grade research
- task can be split into parts
- claim checking and coverage checking can be completed
```

Use news search mode when:

```text
- user asks for one topic only
- examples: 今天科技新聞, AI 新聞, 零售新聞, 加密新聞, 台灣百貨新聞
```

Use news content mode when:

```text
- source news / radar signal is already selected
- user asks to make it more detailed, readable, social, article-style, or retail-angle
```

---

## 4. Boundary Rules

```text
news_search_agent can search and produce topic-specific news.
news_content_agent does not search broadly and does not upgrade evidence.
radar_report_agent owns daily market radar and full cross-domain coverage.
Daily Push Brief is not a full 48-signal formal report.
```

---

## 5. Example Routing

```text
「產出每日市場情報」
→ radar_report_agent + daily_radar_workflow or daily_push_brief_workflow depending on requested depth

「用精簡版產出每日推播」
→ radar_report_agent + daily_push_brief_workflow

「今天科技新聞」
→ news_search_agent + news_search_content_workflow

「把這則新聞寫詳細」
→ news_content_agent + news_content_workflow

「把今天雷達裡的零售訊號變成社群貼文」
→ news_content_agent + news_content_workflow
```
