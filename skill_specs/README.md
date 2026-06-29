# Skill Specs

Skill 是每日市場情報工作流中可重複使用的判斷能力。

---

## Maintenance Principle

Keep skills easy to maintain:

```text
Skill = reusable judgement capability
Tool = operation / search / check / formatting
Config = detailed parameters
Workflow = ordered execution path
Template = output shape
```

Do not hide detailed retry rules, evidence rules, or report layout inside this README.

---

## Required Daily Radar Skills

```text
signal_search_skill
claim_risk_check_skill
coverage_check_skill
report_formatting_skill
```

These skills support the required tool chain:

```text
signal_search_tool
→ claim_risk_checker
→ coverage_checker
→ report_formatter
```

---

## Search Skills

- `signal_search_skill`：把 radar configs / watchlist / missed cases 轉成搜尋目標。
- `query_expansion.skill`：同義詞、跨語言、區域詞擴展。
- `source_triage.skill`：官方、媒體、研究、社群來源初篩。
- `edge_signal_detection.skill`：弱訊號與早期案例辨識。

### signal_search_skill boundary

`signal_search_skill` should not stop when the first search fails.

When a bucket lacks useful results, the skill should switch method before declaring a gap:

```text
change keywords
change language
change source type
change level
change time window
search negative space
search metrics instead of news
check recent reports
```

Detailed retry examples live in:

```text
configs/search_retry_protocol.yml
```

---

## Evidence Skills

- `claim_risk_check_skill`：檢查主張風險、來源、日期與推論邊界。
- `evidence_grading.skill`：高 / 中 / 低 / 資料不足分級。
- `causality_check.skill`：區分事實、推論、候選訊號。
- `cross_source_validation.skill`：交叉驗證。

### claim_risk_check_skill boundary

`claim_risk_check_skill` is not a news rejection skill.

News is an information source. The skill should prevent unsupported certainty, not delete ordinary news.

Preferred actions:

```text
keep with label
tag as single-source
mark as unverified candidate
soften wording
rewrite inference as inference
request source
remove only high-risk unsupported claims
```

Removal should be rare and reserved for high-risk unsupported claims.

---

## Coverage Skills

- `coverage_check_skill`：檢查固定雷達桶、watchlist 與漏抓案例覆蓋。

---

## Radar Skills

- `crypto_narrative_detection.skill`：RWA、tokenized stocks、Perp DEX、AI x crypto 等敘事辨識。
- `ai_application_detection.skill`：企業導入、Agent、工具層與工作流替代辨識。
- `retail_signal_mapping.skill`：百貨、商圈、品牌、服飾與消費訊號判斷。
- `technology_breakthrough_classification.skill`：AI / 非 AI 科技突破分類。
- `taiwan_relevance_mapping.skill`：台灣產業關聯、缺口與行動提醒。

---

## Report Skills

- `report_formatting_skill`：將已檢查內容轉成最終報告格式。
- `cross_day_dedup.skill`：跨日去重。
- `gap_explanation.skill`：資料缺口說明。
- `final_synthesis.skill`：整合今日趨勢與下一步觀察。
