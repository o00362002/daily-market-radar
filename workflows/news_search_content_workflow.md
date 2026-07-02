# News Search Content Workflow

Purpose: search a user-specified news topic and produce a source-backed news output without running the full daily market radar.

This workflow is owned by `news_search_agent` in `AGENT_DEFINITION_MAP.md`.

Required shared rule:

```text
configs/news_freshness_and_taiwan_news.yml
```

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
2. Read minimal repo context: AGENTS.md, AGENT_DEFINITION_MAP.md, configs/source_strategy.md, configs/evidence.yml, configs/news_freshness_and_taiwan_news.yml, memory/watchlist.md when relevant.
3. Search current sources in relevant languages.
4. Prioritize today / latest new information before background context.
5. Cross-check important claims with source type and source time.
6. Classify historical duplication status.
7. Search Taiwan news when Taiwan, retail, market, consumer, business, AI adoption, labor, or user relevance is requested.
8. Classify items into:
   - major news
   - potential / niche signal
   - background context, not counted as news
   - insufficient data
9. Rank by relevance to the user's topic and freshness.
10. Add Taiwan news when available; add Taiwan implications only as synthesis, not as Taiwan news.
11. Output using templates/news_search_content_template.md.
12. Suggest whether to hand off to news_content_agent for deeper article / social post / retail angle.
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
today_new_information
source / date
source type
evidence level
historical duplication status
why it matters
Taiwan news if available
Taiwan / user implication if relevant
cannot conclude
next verification
```

---

## Taiwan news rule

When the user asks for Taiwan, retail, market, consumer, business, AI adoption, labor, or user-relevant news, do not only provide Taiwan implications.

You must attempt Taiwan news search and distinguish:

```text
Taiwan news = source-backed Taiwan event / data / company action / policy / market news.
Taiwan implication = model inference or relevance; not counted as Taiwan news.
```

If no Taiwan news is found, write:

```text
台灣新聞不足
已查來源：
已查關鍵字：
下一步補查：
```

---

## freshness rule

Topic-specific news search must avoid repackaging old concepts.

A repeated theme can be included only if it has:

```text
new data
new company action
new policy
new market reaction
new chain / market metric
new Taiwan news
```

Otherwise it belongs in background context and must not be counted as major news.

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

Handoff must preserve:

```text
source / date
evidence level
today_new_information
historical duplication status
Taiwan news vs Taiwan implication boundary
```

---

## completion rule

Can be marked complete when:

```text
topic identified
sources searched
claims labelled
major news and candidates separated
today_new_information included for each news item
historical duplication status included
Taiwan news searched or Taiwan news insufficiency disclosed when relevant
data gaps disclosed
handoff suggestion included
```

If any required step is missing, mark `news search partial`.
