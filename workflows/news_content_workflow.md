# News Content Workflow

Purpose: convert validated or labelled radar signals into readable news content, trend notes, social posts, or article drafts.

This workflow is owned by `news_content_agent` in `AGENT_DEFINITION_MAP.md`.

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

---

## ordered_steps

```text
1. Receive input signal / brief.
2. Identify source, date, evidence level, and uncertainty.
3. Choose content format.
4. Rewrite into readable content.
5. Preserve claim boundaries.
6. Add Taiwan / user relevance when available.
7. Add review note: what is fact, what is inference, what needs verification.
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
Evidence level:
Draft:
Claim boundary:
Next verification:
```

---

## completion rule

Can be marked complete when:

```text
input signal is identified
source / evidence label is preserved
content type is clear
uncertainty is not removed
output is ready for human review
```

If any item is missing, mark `content draft partial`.
