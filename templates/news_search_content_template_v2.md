# News Search Content Template V2

Use this template with:

```text
configs/news_freshness_and_taiwan_news.yml
```

## 0. Metadata

```text
Request topic:
Search mode:
Date / timezone:
System read status:
Search status:
Evidence policy:
Freshness policy:
New information density:
Taiwan news status:
```

## 1. Search Scope

```text
Topic:
Included regions:
Included languages:
Source types searched:
Taiwan sources searched:
Excluded / not searched:
```

## 2. Major News

Each item must include:

```text
ID:
Event:
Today new information:
Source / date:
Source type:
Evidence level:
History status:
Why it matters:
Taiwan news:
Taiwan implication:
Cannot conclude:
Next verification:
```

## 3. Potential / Niche Signals

Each item must include:

```text
ID:
Candidate:
Today new information:
Source / date:
Why niche:
Evidence level:
History status:
Taiwan news:
Taiwan implication:
Cannot conclude:
Next verification:
```

## 4. Taiwan News / Taiwan Implication Split

```text
Taiwan news:
- 

Taiwan implication:
- 

Taiwan news insufficiency:
- 已查來源：
- 已查關鍵字：
- 下一步補查：
```

## 5. New Information Check

```text
News ID:
Today new information:
History status:
Count as current news: yes / no
Reason:
```

## 6. Data Gaps

```text
Gap:
Why it matters:
Tried:
Next source / keyword:
```

## 7. Handoff Suggestion

```text
Should hand off to news_content_agent: yes / no
Recommended content type:
Reason:
Must preserve today_new_information and Taiwan news boundary: yes / no
```

## 8. Final One-line Judgment

```text

```
