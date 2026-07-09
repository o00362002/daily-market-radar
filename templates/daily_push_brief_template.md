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
configs/feed_discovery_stack.yml
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
```

## 1. Pre-draft Gate and Counters

```text
source_audit_before_drafting: yes / partial / no
recent_reports_dedup: yes / partial / no
primary_domain_assignment: yes / partial / no
major_signal_rejection_gate: yes / partial / no
niche_candidate_fresh_anchor_gate: yes / partial / no
candidate_retry_or_external_discovery: yes / partial / no / not_required
Taiwan_direct_source_audit: yes / partial / no
retail_fixed_matrix: yes / partial / no
crypto_fixed_matrix: yes / partial / no
structural_trend_indicator_panel: yes / partial / no
```

Required counters:

```text
duplicate_rejection_count:
field_overlap_rejection_count:
niche_low_novelty_rejection_count:
candidate_retry_paths_used:
Taiwan_qualified_item_count_after_audit:
Taiwan_direct_sources_checked:
```

## 2. Six-domain Coverage Matrix

| 核心領域 | 掃描狀態 | 大型訊號數 | 小眾候選數 | 台灣新聞數 | Evidence Trace | New Info Check | Primary-domain 去重 | 漏抓風險 |
|---|---|---:|---:|---:|---|---|---|---|
| AI / Agent / 工作流 |  | 3 | 3 | 1–2 or gap | required | required | required |  |
| 加密 / RWA / Agent payments |  | 3 | 3 | 1–2 or gap | required | required | required |  |
| 零售 / 消費 / 社群 / 服飾 / 時尚 / 流行 |  | 3 | 3 | 1–2 or gap | required | required | required |  |
| 全球市場 / 資金流 / 地緣 |  | 3 | 3 | 1–2 or gap | required | required | required |  |
| 科技發展 / 半導體 / 能源 / 機器人 |  | 3 | 3 | 1–2 or gap | required | required | required |  |
| 勞動 / 消費壓力 / 台灣 |  | 3 | 3 | 1–2 or gap | required | required | required |  |

## 3. Per-domain Block

Repeat this block for all six domains.

### [DOMAIN]

**大型訊號（3）**

1. ID：[DOMAIN]-1｜primary_domain：｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜counted_or_rejected_reason：｜不確定點 / 下一步：
2. ID：[DOMAIN]-2｜primary_domain：｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜counted_or_rejected_reason：｜不確定點 / 下一步：
3. ID：[DOMAIN]-3｜primary_domain：｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜counted_or_rejected_reason：｜不確定點 / 下一步：

**小眾候選（3）**

1. ID：[DOMAIN]-C1｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜fresh concrete anchor：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：
2. ID：[DOMAIN]-C2｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜fresh concrete anchor：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：
3. ID：[DOMAIN]-C3｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜fresh concrete anchor：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：

**台灣新聞（1–2 or valid gap）**

- ID：TW-[DOMAIN]-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-[DOMAIN]-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

## 4. Candidate Quality Gate

```text
小眾候選不是趨勢感想。
每則至少有一個 fresh concrete anchor：公司 / 產品 / 論文 / 數據 / 融資 / 招聘 / 開源採用 / 鏈上指標 / 社群事件 / pilot / patent / clinical trial / prototype / supply-chain anomaly / 時尚風格微趨勢 / 品牌商品組合變化。
每則必須標示候選類型：新領域 / 新應用 / 新概念 / 新趨勢。
每則必須標示形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中。
主流大型新聞換句話說不得算候選。
舊背景概念不得冒充今日新聞。
空泛句如「監管仍是變數」不得算候選。
候選必須說明：為何早期、為何可能放大、不能下什麼結論、下一步驗證。
```

If fewer than 3 qualified candidates are found in a domain, or candidates are low-novelty:

```text
run candidate retry / external discovery
check startup / funding / product launch sources
check research / datasets
check developer / open-source / release notes
check non-English and regional sources
check social-first / channel-first sources
check hiring / job posting shifts
check on-chain and market microstructure data
check patents / clinical trials / regulatory pilots
check fashion / style / brand / assortment sources when relevant
check Taiwan direct sources
never fabricate
mark remaining candidate gap
mark partial concise brief when completion gate is not met
```

## 5. Duplicate and Primary-domain Rule

```text
One event = one primary domain quota.
Other domains may reference the event in mapping / indicator / synthesis, but cannot count it again.
Duplicate or repeated themes require a fresh delta; otherwise reject from quota.
```

## 6. Technology Development Rule

```text
AI-driven technology breakthrough:
standalone non-AI technology breakthrough:
non-AI subdomains checked minimum 6:
AI-overcapture check:
```

AI supply chain / AI governance cannot consume Technology quota.

## 7. Taiwan News Rule

Taiwan news must be local news / official data / company action / market data / industry event. Generic Taiwan implications do not count.

For Taiwan crypto, report fixed-source audit. If DA 交易者聯盟 / 邦妮區塊鏈 / 加密城市 / 區塊勢 were not checked as required, do not claim Taiwan crypto news is absent.

Required Taiwan audit:

```text
Taiwan_qualified_item_count_after_audit:
Taiwan_direct_sources_checked:
Taiwan_source_hits:
Taiwan_source_misses:
Taiwan_keyword_fallback_used:
Taiwan_remaining_gap:
```

## 8. Retail Fixed Matrix

```text
cost_pressure:
channel_offline_department_store_mall_street:
channel_online_marketplace_social_commerce:
product_fashion_style_assortment_material_fit_category:
inventory_markdown_mid_price_pressure:
membership_CRM_loyalty_retail_media:
social_commerce_content_discovery_AI_referral:
true_vs_fake_segmentation:
Taiwan_retail_commercial_district_department_store_brand:
retail_matrix_gaps:
```

Each line should reference supporting IDs or disclose direct evidence gap.

## 9. Crypto Fixed Matrix

```text
BTC_ETH_SOL_market_structure:
ETF_flows:
stablecoin_supply_and_dry_powder:
RWA_tokenized_assets:
Perp_DEX_volume_OI_funding:
TVL_fees_revenue:
regulation_policy:
Taiwan_crypto_fixed_sources:
crypto_matrix_gaps:
```

Crypto section must not rely only on price headlines. If quantitative data is not checked, mark crypto indicator coverage partial.

## 10. Structural Trend Indicator Panel

```text
1. 生產力便車無法共享的 K 型經濟
2. AI 泡沫 / 過度投資趨勢
3. 品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾
```

Each thesis must include:

```text
current_direction:
confidence:
supporting_signal_ids:
counter_signal_ids_or_none:
missing_data:
one_sentence_read:
next_verification:
```

These are cumulative direction meters, not single-day conclusions.

## 11. New Information / History Duplicate Check

| ID | 今日新增點 | 是否重複歷史主題 | primary_domain | 可否計入 | 原因 |
|---|---|---|---|---|---|

## 12. Source / Feed Coverage Audit

```text
source_library_checked:
priority_sources_checked:
FreshRSS_checked:
niche_source_types_checked:
formation_level_coverage:
keyword_fallback_used:
official_or_data_crosscheck_used:
Taiwan_sources_checked:
social_channels_checked_when_required:
remaining_source_gap:
```

## 13. Data Gaps and Retry Notes

| 缺口 | 已嘗試 | 下一步 |
|---|---|---|

## 14. Final Indicator Status and News Synthesis Panel

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
post-brief review:
```

This panel does not count toward 3+3.

## 15. Post-brief Backtest / Model Adjustment

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
next_model_adjustment:
```

## Completion Gate

A concise brief is complete only when all six domains have exactly 3 major signals and exactly 3 qualified niche candidates, plus candidate type / formation level / fresh concrete anchor, primary-domain de-dup, required Taiwan news or valid insufficiency disclosure, evidence traces, freshness checks, source audits, retry notes, Retail fixed matrix, Crypto fixed matrix, Structural Trend Indicator Panel, final panel and post-brief review.

If not, write `partial concise brief` and disclose the gap.
