# News Search Content Workflow

Purpose: search a user-specified news topic and produce a source-backed news output without running the full daily market radar.

This workflow is owned by `news_search_agent` in `AGENT_DEFINITION_MAP.md`.

---

## name

```text
news_search_content_workflow
```

## trigger

```text
user asks for today / latest news on a specific topic
user asks for technology news, retail news, AI news, crypto news, fashion news, Taiwan business news
manual request for a standalone news report
```

---

## boundary

`news_search_agent` can search and produce topic-specific news.

It is not a replacement for:

```text
radar_report_agent = full daily market radar
news_content_agent = rewriting / expanding already selected news or radar signals
```

---

## ordered_steps

```text
1. Identify requested topic and scope.
2. Read minimal repo context: AGENTS.md, AGENT_DEFINITION_MAP.md, configs/source_strategy.md, configs/evidence.yml, memory/watchlist.md when relevant.
3. Search current sources in relevant languages.
4. Cross-check important claims with source type and source time.
5. Classify items into:
   - major news
   - potential / niche signal
   - background context
   - insufficient data
6. Rank by relevance to the user's topic.
7. Add Taiwan / user relevance when meaningful.
8. Output using templates/news_search_content_template.md.
9. Suggest whether to hand off to news_content_agent for deeper article / social post / retail angle.
```

---

## search depth modes

```text
quick = 3–5 major items + 1–2 candidates
standard = 5–8 major items + 2–3 candidates
deep = 8–12 major items + 3–5 candidates + source comparison
```

Default mode: `standard`.

---

## required fields per item

```text
title / event
source / date
source type
evidence level
why it matters
Taiwan / user relevance
cannot conclude
next verification
```

---

## claim safety

```text
High evidence: official / authority / data / trusted media / multiple sources.
Medium evidence: credible media / industry source / research summary, but incomplete data.
Low evidence: social / single-source / early discussion; candidate only.
Insufficient: do not present as fact.
```

---

## handoff rule

If the user asks to turn the search result into readable content, article, social post, or retail commentary, hand off to:

```text
news_content_agent
workflows/news_content_workflow.md
templates/news_content_template.md
```

---

## completion rule

Can be marked complete when:

```text
topic identified
sources searched
claims labelled
major news and candidates separated
Taiwan / user relevance included when meaningful
data gaps disclosed
handoff suggestion included
```

If any required step is missing, mark `news search partial`.
