# Daily Push Brief Workflow

Purpose: define a lightweight daily push version for chat / automation output when a full 48-signal formal report is too large for reliable single-pass execution.

This workflow does **not** replace the full `daily_radar_workflow.md`.
It creates a stable concise output mode.

---

## name

```text
daily_push_brief_workflow
```

## owner

```text
radar_report_agent
```

## trigger

```text
quick daily market brief
scheduled daily push
manual concise radar request
```

---

## mode boundary

```text
Daily Push Brief = concise user-facing radar output.
Full Daily Radar = full research / archive output.
```

Daily Push Brief may be marked `complete` only for the concise mode. It must not claim to satisfy the full 48-signal formal gate unless it actually does.

---

## minimum output shape

```text
0. Read status and mode
1. Hard gate status: concise mode / full gate not attempted or not passed
2. Six-domain coverage matrix
3. Each core domain: 2–3 major signals
4. Each core domain: 1 niche / potential candidate
5. Each core domain: Taiwan mapping directly under the domain
6. Retail focus block
7. Data gaps and retry notes
8. Post-brief backtest / model adjustment panel
```

---

## six core domains

```text
1. AI models / agents / workflow replacement
2. Crypto / RWA / agent payments
3. Retail / consumer / social / fashion
4. Global markets / capital flows / geopolitics
5. Technology development / robotics / biotech / energy / semiconductor
6. Labor / consumption pressure / Taiwan local signals
```

---

## required per-domain fields

Each domain must include:

```text
major_signals: 2–3
niche_candidate: 1
Taiwan mapping:
  - Taiwan signal
  - Taiwan industry relevance
  - Taiwan data gap
  - next verification
```

Do not put all Taiwan mapping only at the end.

---

## retail focus rule

The concise report must preserve a retail section even when other domains are compressed.

Minimum retail scan:

```text
- department store / mall / street retail
- brand openings / closures / tenant mix
- online retail / marketplace / social commerce
- fashion inventory / discount / mid-price pressure
- Taiwan retail / malls / department stores / brands
```

If retail data is weak, write the data gap and next sources. Do not omit retail.

---

## output status wording

If using this workflow, write:

```text
輸出模式：每日推播精簡版。
完整 48 則正式閘門：未嘗試 / 未通過 / 另需分段研究版。
```

Do not write the concise brief as a full formal report.

---

## completion rule

Concise mode can be marked complete when:

```text
entry read complete or missing files disclosed
six domains covered
each domain has Taiwan mapping
retail focus block present
data gaps disclosed
post-brief review present
```

If any item is missing, mark `partial concise brief`.
