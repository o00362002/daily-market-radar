# Daily Radar Workflow

Purpose: define the full formal daily market radar execution path.

Owner: `AGENT_RADAR_REPORT` in `AGENT_DEFINITION_MAP.md`.

General daily news requests should use `workflows/daily_push_brief_workflow.md` unless the user explicitly asks for a full, formal, or archive report.

Required shared rules:

```text
configs/news_freshness_and_taiwan_news.yml
configs/source_routing_rules.yml
configs/niche_candidate_policy.yml
configs/technology_development.yml
SOURCE_LIBRARY_SPEC.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

Full reports must enforce:

```text
台灣段必須優先放台灣新聞，不得只用台灣影響或台灣推論補位。
每則大型訊號與小眾候選都必須標示今日新增點。
歷史重複主題只有在有新數據、新公司動作、新政策、新市場反應、新鏈上數據或新台灣新聞時，才能計入正式 5+5。
只有背景概念或歷史重播，不得計入 5+5。
固定來源庫必須先於 generic keyword search 檢查。
小眾候選必須是具體早期弱訊號，不得用空泛趨勢句補位。
```

## name

```text
daily_radar_workflow
```

## trigger

```text
explicit full daily radar report request
scheduled full daily radar run
manual full market radar generation
formal archive report request
5+5 hard-gate report request
60-signal report request
archive output request
```

## non_trigger

```text
每日播報
每日新聞
今天的每日新聞
播報今天的每日新聞
今日市場雷達
今天市場雷達
今天新聞
每日推播
morning brief
daily news
daily push
quick daily market brief
```

Non-trigger phrases route to `AGENT_DAILY_PUSH_BRIEF` unless the user explicitly asks for formal, complete, or archival output.

## ordered_steps

```text
1. Entry read.
2. Load full radar context.
3. Read configs/news_freshness_and_taiwan_news.yml.
4. Read configs/source_routing_rules.yml.
5. Read configs/niche_candidate_policy.yml.
6. Read configs/technology_development.yml.
7. Read SOURCE_LIBRARY_SPEC.md.
8. Read sources/key_media_library.yml and sources/official_and_data_sources.yml.
9. Build six-domain source plan from source library.
10. Build separate major-signal and niche-candidate search plans.
11. Collect priority source candidates by domain, region, and language.
12. Expand niche search into research, startup, product, niche industry, developer, social-first, hiring, on-chain, patent and clinical sources.
13. Filter items with topic keywords and radar rules.
14. Cross-check high-risk claims with official / data sources.
15. Use generic keyword search only as fallback / enrichment / discovery.
16. If 5 major + 5 niche candidates is not met, run retry and external discovery.
17. Check source, date, claim risk, and 今日新增點.
18. Check candidate concrete anchor, why early, scale path, cannot-conclude and next verification.
19. Check Taiwan news validity by domain.
20. Check coverage and historical duplicates.
21. Remove background-only / historical-replay items from 5+5 count.
22. Enforce Technology anti-AI-overcapture rule and non-AI scan.
23. Format with the full daily report template.
24. Output source-library coverage matrix and retry notes.
25. Run missed-case backtest loop when needed.
26. Complete final status check.
```

## required_checks

```text
source library check
priority source coverage check
source / date check
search retry check before gap
claim risk check
new information check
historical duplicate check
Taiwan news validity check
coverage check
niche candidate concrete-anchor check
candidate equality check
gap note check
technology anti-AI-overcapture check
missed-case backtest check
```

## source-first rule

Full Daily Radar must not start from generic keyword search. Generic search is allowed only after priority-source checks or when coverage expansion / Taiwan retry / external discovery is required.

## niche candidate rule

```text
Full target = at least 5 major signals + at least 5 niche candidates per domain when available.
Candidate target equals major target.
Mainstream wires alone are insufficient for niche-candidate completion.
Every candidate needs a concrete anchor and must explain why early, why it could scale, what cannot be concluded, and next verification.
If candidate quota is not met, run retry / external discovery before declaring a gap.
Never fabricate candidates to satisfy quota.
```

## Taiwan news rule

Allowed Taiwan news includes Taiwan official data/policy/statistics, Taiwan company actions, local industry events, retail/channel news, market/labor/consumption data, or international news explicitly involving Taiwan entities.

Generic implications are not Taiwan news. If Taiwan news is not found, disclose checked sources, keywords and next retry. Taiwan crypto must obey the fixed-source and legislative-trigger audit in `configs/source_routing_rules.yml`.

## freshness rule

Every counted major signal / niche candidate must include:

```text
ID
事件或候選訊號
今日新增點
來源 / 時間
證據等級
是否重複歷史主題
不確定點 / 下一步
```

Candidates additionally require:

```text
concrete_anchor
why_niche_or_early
why_it_could_scale
cannot_conclude
next_verification
```

Items without new information must not count toward 5+5.

## technology rule

Technology domain must obey `configs/technology_development.yml`. AI domain cannot consume Technology quota. At least six non-AI technology subdomains must be scanned; otherwise mark Technology coverage partial.

## source coverage matrix requirement

Full reports must include:

```text
核心領域
priority sources checked
source hits
source misses
keyword fallback used
external discovery used
official / data cross-check used
Taiwan sources checked
niche source types checked
remaining source gap
```

If this audit is missing, mark `partial full report`.

## output_path

```text
reports/YYYY/YYYY-MM-DD.md
reports/backtests/ when needed
```

## completion_rule

The report can be marked `complete` only when required source-library checks, 5+5 equality target, candidate quality checks, technology checks, freshness, Taiwan news and backtest checks are complete. If any required check is skipped, mark `partial full report`.
