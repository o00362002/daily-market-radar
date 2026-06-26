# Skill: Daily Broadcast GitHub Sync

## Purpose

This Skill defines how the daily market broadcast should be organized and synchronized into GitHub after each broadcast cycle.

The goal is to keep the repository as the source of truth for daily market radar outputs, missed-signal corrections, model adjustments, and post-broadcast review records.

## Source of truth

- Repository: `o00362002/daily-market-radar`
- This Skill controls the post-broadcast GitHub整理流程.
- If this Skill conflicts with older chat memory, old memory is lower priority.
- Before producing or syncing a daily broadcast, read the repo structure first, especially:
  - `SYSTEM_PROMPT.md`
  - `configs/`
  - `memory/`
  - `templates/`
  - `reports/`
  - `skills/`

## Core rule

There are two different workflows:

1. **Normal daily broadcast finished**
   - After the daily market broadcast is completed, organize the final broadcast into GitHub automatically.
   - Save it under the correct broadcast date.
   - Preserve source links, dates, evidence, checked buckets, and any stated data gaps.

2. **Post-broadcast discussion / missed-signal repair**
   - If the user discusses missed content, wrong weighting, search-model flaws, signal architecture issues, or later corrections after the broadcast, do **not** immediately sync those discussion fragments.
   - Continue discussing, testing, and revising the model in chat.
   - Only整理進 GitHub after the user explicitly says one of the following or a clear equivalent:
     - `整理進 github`
     - `整理近 github`
     - `放到 github`
     - `同步到 github`
     - `把這段整理到 repo`

## What to save after each normal broadcast

For each broadcast date, save or update a structured report containing:

- Broadcast date and weekday in Taiwan time.
- Final daily market broadcast content.
- Major events and their source links.
- Publication time or event time when available.
- Cross-day deduplication notes.
- Required radar buckets and whether each had material signals.
- Data gaps, no-update sections, and checked sources.
- Practical implications for the user's focus areas:
  - Retail / physical retail / omnichannel / shopping districts / department stores / apparel brands.
  - AI applications / agents / workflows / enterprise adoption.
  - Crypto potential markets and early signals.
  - Global markets, policy, and geopolitics.
- Follow-up watchlist and next verification points.

## What to save after user-approved missed-signal repair

When the user explicitly asks to整理進 GitHub after discussion, save a post-broadcast correction note containing:

- Original broadcast date.
- Missed signal or disputed topic.
- Whether the missed item was truly important or only user-mentioned noise.
- Evidence and source links used to verify the item.
- Root cause of the miss:
  - Missing radar bucket.
  - Wrong query layer.
  - Too narrow keywords.
  - Wrong geography / language source.
  - Overweighting finance news.
  - Underweighting industry application news.
  - Insufficient platform / social / official source checks.
  - Weak connection between event and user's strategic domains.
- Search-model adjustment, not just event addition.
- Simulation of whether the adjusted model would catch the same class of news next time.
- Loop review result:
  - What changed.
  - What remains uncertain.
  - What must be checked in the next broadcast.

## File organization recommendation

Use this structure unless the repo already defines a different one:

```text
reports/YYYY/YYYY-MM-DD.md
memory/post_broadcast_corrections/YYYY-MM-DD.md
configs/search_model_adjustments.yml
templates/daily_report_template.md
templates/post_broadcast_correction_template.md
skills/daily-broadcast-github-sync/SKILL.md
```

If a target file already exists, update it instead of creating duplicates.

## Naming conventions

- Use Taiwan date, format: `YYYY-MM-DD`.
- One final report per broadcast date.
- One correction note per broadcast date when applicable.
- If several corrections belong to the same broadcast date, append them into the same correction note under separate sections.

## Quality gates before syncing

Before committing to GitHub, check:

1. **Date integrity**
   - Correct Taiwan date and weekday.
   - Clear distinction between event date, publication date, and broadcast date.

2. **Evidence integrity**
   - Important claims have source links.
   - Claims without enough evidence are marked as unverified, weak, or pending.

3. **Architecture integrity**
   - Missed-signal repairs adjust the search/radar model, not only a keyword list.
   - Corrections identify why the model failed.

4. **User-intent integrity**
   - Normal broadcast can be saved after completion.
   - Discussion corrections must wait for explicit user approval before syncing.

5. **Loop review**
   - Check whether the saved content includes report, gaps, corrections, model update, and next verification.
   - If anything is missing, add it before commit.

## Commit message format

Use concise commit messages:

- `Add daily broadcast report YYYY-MM-DD`
- `Update daily broadcast report YYYY-MM-DD`
- `Add post-broadcast correction YYYY-MM-DD`
- `Update post-broadcast correction YYYY-MM-DD`
- `Update daily broadcast GitHub sync skill`

## Operational behavior

When the user says `每日播報後整理`, interpret it as:

- Final broadcast report should be saved automatically after the report is complete.
- Follow-up discussion should not be saved until the user says to整理進 GitHub.

When the user says `整理進 github` after a discussion, interpret it as:

- Consolidate the discussion into durable repo records.
- Do not paste raw chat logs unless explicitly requested.
- Convert the discussion into structured correction notes, model changes, and next checks.
