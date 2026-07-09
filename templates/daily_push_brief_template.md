# Daily Push Brief Template

Daily Push Brief is a structured concise radar, not a free-form summary.
Concise means shorter wording per item, not fewer reconnaissance categories.

Required shared rules:

```text
configs/daily_execution_quality_gate.yml
configs/structural_trend_indicators.yml
configs/news_freshness_and_taiwan_news.yml
configs/source_routing_rules.yml
configs/niche_candidate_policy.yml
configs/technology_development.yml
SOURCE_LIBRARY_SPEC.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

## 0. Basic Info

```text
報告日期：YYYY/MM/DD（星期X）台灣時間
輸出模式：每日推播精簡版
精簡版狀態：complete concise brief / partial concise brief
完整正式閘門：未嘗試 / 未通過 / 另需分段研究版
系統資料讀取狀態：已讀取 / 部分無法讀取 / 無法讀取
歷史去重狀態：已檢查近期 reports / 未完整
每日執行品質閘門：通過 / partial / failed
結構閘門狀態：通過 / 未通過
新資訊密度狀態：通過 / 偏低 / 未通過
台灣新聞狀態：通過 / 不足 / 未完整
來源庫檢查狀態：通過 / partial / 未完成
Feed stack 狀態：通過 / partial / 未完成 / not_required
FreshRSS ingestion 狀態：通過 / partial / 未完成 / not_available
```

## 1. Pre-draft Gate Summary

```text
source_audit_before_drafting: done / partial / skipped
recent_reports_dedup: done / partial / skipped
primary_domain_assignment: done / partial / skipped
major_signal_rejection_gate: done / partial / skipped
niche_fresh_anchor_gate: done / partial / skipped
candidate_retry_external_discovery: done / partial / skipped / not_required
Taiwan_direct_source_audit: done / partial / skipped
Retail_fixed_matrix: done / partial / skipped
Crypto_fixed_matrix: done / partial / skipped
Structural_Trend_Indicator_Panel: done / partial / skipped
```

If this gate is skipped, mark `partial concise brief` or `failed gate`.

## 2. Rejection / Retry Counters

```text
duplicate_rejection_count:
field_overlap_rejection_count:
niche_low_novelty_rejection_count:
candidate_retry_paths_used:
Taiwan_qualified_item_count_after_audit:
Taiwan_direct_sources_checked:
retail_matrix_gaps:
crypto_matrix_gaps:
structural_thesis_evidence_change:
true_vs_fake_segmentation_status:
```

## 3. Six-domain Coverage Matrix

| 核心領域 | 掃描狀態 | 大型訊號數 | 小眾候選數 | 台灣新聞數 | Evidence Trace | New Info Check | Primary-domain 去重 | 漏抓風險 |
|---|---|---:|---:|---:|---|---|---|---|
| AI / Agent / 工作流 |  | 3 | 3 | 1–2 or insufficiency | required | required | required |  |
| 加密 / RWA / Agent payments |  | 3 | 3 | 1–2 or insufficiency | required | required | required |  |
| 零售 / 消費 / 社群 / 服飾 / 時尚 / 流行 |  | 3 | 3 | 1–2 or insufficiency | required | required | required |  |
| 全球市場 / 資金流 / 地緣 |  | 3 | 3 | 1–2 or insufficiency | required | required | required |  |
| 科技發展 / 半導體 / 能源 / 機器人 |  | 3 | 3 | 1–2 or insufficiency | required | required | required |  |
| 勞動 / 消費壓力 / 台灣 |  | 3 | 3 | 1–2 or insufficiency | required | required | required |  |

## 4. Per-domain Block

Repeat this block for all six domains.

### [DOMAIN]

**大型訊號（3）**

1. ID：[DOMAIN]-1｜primary_domain：｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜可否計入：｜不確定點 / 下一步：
2. ID：[DOMAIN]-2｜primary_domain：｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜可否計入：｜不確定點 / 下一步：
3. ID：[DOMAIN]-3｜primary_domain：｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜可否計入：｜不確定點 / 下一步：

Rules:

```text
One event can count toward only one primary domain quota.
Other affected domains may reference it in mapping / indicator / synthesis, but cannot count it again.
Duplicate or repeated themes require a fresh delta; otherwise reject from quota.
```

**小眾候選（3）**

1. ID：[DOMAIN]-C1｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜fresh concrete anchor：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：
2. ID：[DOMAIN]-C2｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜fresh concrete anchor：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：
3. ID：[DOMAIN]-C3｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜fresh concrete anchor：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：

Candidate quality gate:

```text
小眾候選不是趨勢感想。
必須有 fresh concrete anchor。
不得是大型新聞換句話說。
不得是舊背景概念或舊研究，除非今日有新資料 / 新產品 / 新公司動作 / 新政策 / 新市場反應 / 新社群訊號。
不足 3 則或低新奇度時，必須先 retry / external discovery；仍不足才標 gap，不得捏造。
```

**台灣新聞（1–2 or valid insufficiency）**

- ID：TW-[DOMAIN]-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-[DOMAIN]-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

Taiwan implication cannot replace Taiwan news. If no qualified Taiwan news is found, disclose direct sources checked, hits, misses, keyword fallback and remaining gap.

## 5. Retail Fixed Matrix

```text
cost_pressure:
  signal_ids:
  Taiwan_evidence:
  gap:
channel_offline_department_store_mall_street:
  signal_ids:
  Taiwan_evidence:
  gap:
channel_online_marketplace_social_commerce:
  signal_ids:
  Taiwan_evidence:
  gap:
product_fashion_style_assortment_material_fit_category:
  signal_ids:
  Taiwan_evidence:
  gap:
inventory_markdown_mid_price_pressure:
  signal_ids:
  Taiwan_evidence:
  gap:
membership_CRM_loyalty_retail_media:
  signal_ids:
  Taiwan_evidence:
  gap:
social_commerce_content_discovery_AI_referral:
  signal_ids:
  Taiwan_evidence:
  gap:
true_vs_fake_segmentation:
  signal_ids:
  true_segmentation_evidence:
  fake_segmentation_evidence:
  gap:
Taiwan_retail_commercial_district_department_store_brand:
  signal_ids:
  Taiwan_direct_sources_checked:
  gap:
```

Retail domain is not only channel news. It must include cost, channels, product/fashion, inventory, membership, social/AI discovery, segmentation quality, and Taiwan local retail signals. If evidence is missing, disclose the gap.

## 6. Crypto Fixed Matrix

```text
BTC_ETH_SOL_market_structure:
  data_checked:
  signal_ids:
  gap:
ETF_flows:
  data_checked:
  signal_ids:
  gap:
stablecoin_supply_and_dry_powder:
  data_checked:
  signal_ids:
  gap:
RWA_tokenized_assets:
  data_checked:
  signal_ids:
  gap:
Perp_DEX_volume_OI_funding:
  data_checked:
  signal_ids:
  gap:
TVL_fees_revenue:
  data_checked:
  signal_ids:
  gap:
regulation_policy:
  data_checked:
  signal_ids:
  gap:
Taiwan_crypto_fixed_sources:
  DA_交易者聯盟:
  邦妮區塊鏈:
  加密城市:
  區塊勢:
  official_legislative_trigger:
  gap:
```

Crypto section must not rely only on price headlines. If quantitative data is not checked, mark crypto indicator coverage partial.

## 7. Structural Trend Indicator Panel

The concise report must include all three structural theses:

| 結構指標 | 今日方向 toward / against / mixed / insufficient | 信心 | 支撐 signal IDs | 反向 signal IDs | 缺口 | 一句判斷 | 下一步驗證 |
|---|---|---|---|---|---|---|---|
| 生產力便車無法共享的 K 型經濟 |  |  |  |  |  |  |  |
| AI 泡沫 / 過度投資趨勢 |  |  |  |  |  |  |  |
| 品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾 |  |  |  |  |  |  |  |

These are cumulative direction meters, not single-day conclusions. Do not force direction when evidence is weak.

## 8. Technology Development Rule

```text
AI-driven technology breakthrough:
standalone non-AI technology breakthrough:
Non-AI subdomains checked minimum 6:
Technology maturity labels:
AI-overcapture check:
Taiwan technology mapping:
Remaining gap:
```

AI supply chain / AI governance cannot consume Technology quota.

## 9. New Information / History Duplicate Check

| ID | primary_domain | 今日新增點 | 是否重複歷史主題 | 可否計入 | 拒絕原因 / 保留原因 |
|---|---|---|---|---|---|

## 10. Source / Feed Coverage Audit

```text
source_library_checked:
priority_sources_checked:
source_hits:
source_misses:
FreshRSS_checked:
feed_stack_loaded:
niche_source_types_checked:
formation_level_coverage:
keyword_fallback_used:
external_discovery_used:
official_or_data_crosscheck_used:
Taiwan_sources_checked:
social_channels_checked_when_required:
remaining_source_gap:
```

## 11. Data Gaps and Retry Notes

| 缺口 | 已嘗試 | 下一步 |
|---|---|---|

## 12. Final Indicator Status and News Synthesis Panel

```text
indicator domain:
today status:
direction:
supporting news IDs:
data gaps:
today main themes:
Taiwan news summary:
source-library coverage note:
feed-stack coverage note:
structural trend summary:
post-brief review:
```

This panel does not count toward 3+3.

## Completion Gate

A concise brief is complete only when all six domains have exactly 3 major signals and exactly 3 qualified niche candidates, plus candidate type / formation level / fresh concrete anchor, required Taiwan news or valid insufficiency disclosure, evidence traces, freshness checks, primary-domain de-dup, source audits, retry counters, Retail fixed matrix, Crypto fixed matrix, Structural Trend Indicator Panel, data gaps, final panel and post-brief review.

If not, write `partial concise brief` and disclose the gap.
