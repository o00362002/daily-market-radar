# News Content Workflow

Purpose: convert validated or labelled radar signals into readable news content, trend notes, social posts, or article drafts.

This workflow is owned by `news_content_agent` in `AGENT_DEFINITION_MAP.md`.

Required shared rule:

```text
configs/news_freshness_and_taiwan_news.yml
```

---

## name

```text
news_content_workflow
```

## trigger

```text
selected radar signal to content
turn daily brief into article
turn daily brief into social content
manual request for news-style output
```

---

## boundary

`news_content_agent` does not perform full radar search and does not upgrade evidence.

It can only use:

```text
- radar_report_agent output
- selected source-backed signals
- labelled candidate signals
- user-provided source material
```

If the input is low evidence or insufficient, the output must preserve that uncertainty.

`news_content_agent` must not make old concepts look like new news.

It must preserve:

```text
source / date
evidence level
today_new_information
historical duplication status
Taiwan news vs Taiwan implication boundary
```

---

## ordered_steps

```text
1. Receive input signal / brief.
2. Identify source, date, evidence level, today_new_information, historical duplication status, and uncertainty.
3. Determine whether the input is news, background, synthesis, Taiwan news, or Taiwan implication.
4. Choose content format.
5. Rewrite into readable content.
6. Preserve claim boundaries.
7. Add Taiwan news only if source-backed Taiwan news exists.
8. Add Taiwan / user implication separately when useful.
9. Add review note: what is fact, what is inference, what needs verification.
```

---

## content formats

```text
news_brief = short factual digest
trend_note = interpretation-focused market note
social_post = concise social media draft
retail_angle = retail / brand / store operations angle
article_draft = longer structured article
```

---

## freshness rule

When writing content, distinguish:

```text
News = source-backed new event / data / company action / policy / market reaction.
Background = older concept or historical context.
Synthesis = model or analyst interpretation based on news.
```

Do not write background or repeated concepts as if they are today's new news.

If an item is historical or repeated, the draft must say one of:

```text
延續性主題
背景脈絡
歷史已播但今日有新增資料
歷史已播且今日無新增，不應當作新新聞
```

---

## Taiwan news rule

When adding Taiwan relevance, separate:

```text
Taiwan news = source-backed Taiwan event / data / company action / policy / market news.
Taiwan implication = model inference or relevance.
```

Do not label Taiwan implication as Taiwan news.

If no Taiwan news is available, write:

```text
台灣新聞不足，以下僅為台灣影響推論。
```

---

## claim safety rules

```text
High evidence → may be written as reported fact with source note.
Medium evidence → write as reported signal / industry interpretation.
Low evidence → write as candidate signal / unverified discussion.
Insufficient → do not present as fact; use as question or verification target.
```

---

## output requirement

Every output must include:

```text
Content type:
Input signal:
Source / date:
Today new information:
Historical duplication status:
Evidence level:
Draft:
Claim boundary:
Taiwan news:
Taiwan implication:
Next verification:
```

---

## completion rule

Can be marked complete when:

```text
input signal is identified
source / evidence label is preserved
today_new_information is preserved or marked missing
historical duplication status is preserved or marked missing
Taiwan news vs Taiwan implication is separated
content type is clear
uncertainty is not removed
output is ready for human review
```

If any item is missing, mark `content draft partial`.
