# Daily Push Brief Workflow

Purpose: define the default structured concise daily push version for chat / automation output when a full 48-signal formal report is not explicitly requested.

This workflow does **not** replace the full `daily_radar_workflow.md`.
It creates the default concise output mode, but concise means shorter wording per item, not reduced structure.

```text
Daily Push Brief 不代表可刪減結構。
Brief 只代表單則內容字數較短。
所有章節、欄位、證據追溯、台灣新聞、指標狀態仍必須完整保留。
```

Required shared rule:

```text
configs/news_freshness_and_taiwan_news.yml
```

---

## name

```text
daily_push_brief_workflow
```

## owner

```text
AGENT_DAILY_PUSH_BRIEF
```

## trigger

```text
每日播報
每日新聞
今天的每日新聞
播報今天的每日新聞
每日推播
今日市場雷達
今天市場雷達
今天新聞
先看今天重點
讀 repo 播報今天
不靠記憶讀 repo 播報今天
quick daily market brief
scheduled daily push
manual concise radar request
morning brief
daily news
daily push
concise brief
簡版
輕量版
```

---

## mode boundary

```text
Daily Push Brief = default structured concise user-facing radar output.
Full Daily Radar = opt-in full research / archive output.
```

Daily Push Brief may be marked `complete` only for the concise mode. It must not claim to satisfy the full 48-signal formal gate unless it actually does.

Brief means:

```text
- shorter wording per item
- fewer items than Full Daily Radar
- full template structure preserved
```

Brief does not mean:

```text
- removing required sections
- reducing domain structure
- merging Taiwan news into generic Taiwan implications
- replacing news with synthesis
- treating indicator status or conclusions as news
- replaying old concepts without today's new information
```

---

## minimum output shape

```text
0. Read status and mode
1. Hard gate status: concise mode / full gate not attempted or not passed
2. Six-domain coverage matrix
3. Each core domain: exactly 3 major signals
4. Each core domain: exactly 1 niche / potential candidate
5. Each core domain: 1–2 Taiwan news items directly under the domain
6. Retail focus block with five fixed checks
7. New Information / History Duplicate Check
8. Data gaps and retry notes
9. Final indicator status and news synthesis panel
10. Post-brief review inside the final panel
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
major_signals: exactly 3
niche_candidate: exactly 1
Taiwan news: 1–2 items
Evidence trace: required for every news / signal item
New information check: required for every news / signal item
Historical duplication status: required for every news / signal item
```

Taiwan section must be Taiwan news, not generic Taiwan mapping:

```text
Allowed Taiwan news:
- Taiwan official data / policy / statistics
- Taiwan company announcement / earnings / major action
- Taiwan media-reported local industry event
- Taiwan retail / mall / department store / brand / channel / store opening / closure / commercial district news
- Taiwan market data / FX / labor / consumption / credit data
- International news that explicitly includes Taiwan companies, Taiwan supply chain, Taiwan market, or Taiwan policy

Not Taiwan news:
- international news may affect Taiwan
- Taiwan companies should pay attention
- Taiwan brands can learn from this
- generic model inference about Taiwan relevance
```

If no qualified Taiwan news is found, write:

```text
台灣新聞不足
已查來源：
已查關鍵字：
下一步補查：
```

Do not use generic Taiwan implications to fill the Taiwan news quota.

---

## news freshness rule

News / signals must be source-backed events, data changes, company actions, policy changes, market moves, product releases, or verifiable observations.

Each item must identify:

```text
今日新增點
是否重複歷史主題
```

Do not count an item as a major signal if it is only:

```text
- background concept
- old research without new relevance
- old company news without new update
- model synthesis
- generic Taiwan implication
- historical replay without new data / action / policy / market reaction / Taiwan news
```

Repeated themes can count only if they contain:

```text
- new data
- new company action
- new policy
- new market reaction
- new chain / market metric
- new Taiwan news
```

---

## news vs synthesis rule

The following must not be counted as news:

```text
- indicator status
- theme statements
- market conclusions
- Taiwan implications
- model inference
- cross-domain summary
```

Every synthesis statement must point back to supporting news IDs.
If it cannot point back to news IDs, mark it as a data gap or candidate inference.

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

Retail Focus Block should reference the above news IDs and Taiwan news IDs when possible.
It should not convert a broad conclusion into a news item.
If retail data is weak, write the data gap and next sources. Do not omit retail.

---

## final indicator and synthesis panel rule

Fixed indicator tracking is required, but in Daily Push Brief it belongs at the end.

```text
Final Indicator Status and News Synthesis Panel must include:
- indicator domain
- today status
- direction
- supporting news IDs
- data gaps
- today’s main themes
- Taiwan news summary
- post-brief review
```

This panel is required but must not be counted toward the per-domain 3+1 news quota.

---

## output status wording

If using this workflow, write:

```text
輸出模式：每日推播精簡版。
精簡版狀態：complete concise brief / partial concise brief。
完整 48 則正式閘門：未嘗試 / 未通過 / 另需分段研究版。
結構閘門狀態：通過 / 未通過。
新資訊密度狀態：通過 / 偏低 / 未通過。
台灣新聞狀態：通過 / 不足 / 未完整。
```

Do not write the concise brief as a full formal report.

---

## completion rule

Concise mode can be marked `complete concise brief` only when:

```text
entry read complete or missing files disclosed
six domains covered
all domains contain exactly 3 major signals
all domains contain exactly 1 niche candidate
all domains contain 1–2 Taiwan news items or explicit Taiwan news insufficiency disclosure
all news / signals contain evidence trace
all news / signals contain today_new_information and historical_duplication_status
retail focus block with five fixed checks is present
data gaps are disclosed
final indicator status and news synthesis panel is present
indicator status and conclusions point back to news IDs
post-brief review is present
```

If any item is missing, mark `partial concise brief`.
