# Full Daily Radar Report Template V2

Use with:

```text
workflows/daily_radar_workflow.md
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
報告日期時間：YYYY/MM/DD（星期X）HH:mm（台灣時間）
輸出模式：完整正式歸檔版
系統資料讀取狀態：
歷史報告去重狀態：
每日訊號硬閘門狀態：通過 / 未通過 / 搜尋未完整
每日執行品質閘門：通過 / partial / failed
新資訊密度狀態：通過 / 偏低 / 未通過
台灣新聞狀態：通過 / 不足 / 未完整
來源庫檢查狀態：通過 / partial / 未完成
Feed stack 狀態：通過 / partial / 未完成 / not_required
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

## 3. Coverage Matrix

| 核心領域 | 大型新聞數 | 小眾候選數 | 台灣新聞數 | New Info Check | Evidence Trace | Primary-domain 去重 | 是否達標 | 缺口 |
|---|---:|---:|---:|---|---|---|---|---|
| AI 模型 / Agent / 工作流替代 | >=5 | >=5 | required or insufficiency | required | required | required |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | >=5 | >=5 | required or insufficiency | required | required | required |  |  |
| 零售 / 消費 / 社群 / 服飾 / 時尚 / 流行 | >=5 | >=5 | required or insufficiency | required | required | required |  |  |
| 全球市場 / 資金流 / 地緣政治 | >=5 | >=5 | required or insufficiency | required | required | required |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | >=5 | >=5 | required or insufficiency | required | required | required |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | >=5 | >=5 | required or insufficiency | required | required | required |  |  |

## 4. Major News by Domain

Each counted major news item must include:

```text
ID:
primary_domain:
事件:
今日新增點:
來源 / 時間:
證據等級:
是否重複歷史主題:
可否計入正式訊號:
受影響雷達:
台灣新聞:
台灣影響推論:
不確定點 / 下一步:
```

Rules:

```text
Taiwan implication cannot replace Taiwan news.
Historical replay without today-new information does not count toward output slots.
One event can count toward only one primary domain slot.
Other affected domains may reference it in cross-domain mapping / indicator / synthesis, but cannot count it again.
```

## 5. Niche / Potential Signals by Domain

Each domain target: at least 5 qualified niche candidates when available, equal to the major-signal target.

Each counted candidate must include:

```text
ID:
候選訊號:
候選類型：新領域 / 新應用 / 新概念 / 新趨勢
形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中
fresh concrete anchor:
今日新增點:
來源 / 時間:
為何小眾 / 早期:
為何可能放大:
證據等級:
是否重複歷史主題:
台灣新聞:
台灣影響推論:
不確定性:
不能下的結論:
下一步驗證:
```

Candidate quality rule:

```text
候選必須有 fresh concrete anchor：公司 / 產品 / 論文 / 數據 / 融資 / 招聘 / 開源採用 / 鏈上指標 / 社群事件 / pilot / patent / clinical trial / prototype / supply-chain anomaly / 時尚風格微趨勢 / 品牌商品組合變化 等。
不得用空泛趨勢句補位。
不得把大型主流新聞換句話說當候選。
不得用舊背景概念或舊研究補今日候選，除非今日有新資料 / 新動作 / 新市場反應 / 新社群訊號。
主流 wires 不足以完成候選搜尋，必須擴展研究、新創、產品、小眾產業、開發者、社群、招聘、鏈上、時尚媒體、品牌官方、商品組合、區域 / 非英語來源。
不足 5 則或新奇度低時，先 retry / external discovery；仍不足才標示 gap，不得捏造。
```

Formation rule:

```text
很多報導、很多討論、詞彙或敘事開始擴散 = 話題形成。
很多品牌、公司、平台、地區開始應用、試點、投資、招聘或數據同步出現 = 趨勢形成。
已廣泛商業化且有明確數據 = 主流化中，應評估是否升級為大型訊號。
```

## 6. Taiwan News Section

```text
今日台灣新聞：
1.
2.
3.

台灣新聞不足領域：
- 領域：
  Taiwan_qualified_item_count_after_audit:
  Taiwan_direct_sources_checked:
  Taiwan_source_hits:
  Taiwan_source_misses:
  Taiwan_keyword_fallback_used:
  Taiwan_remaining_gap:
```

Taiwan crypto must include fixed-source audit and legislative-trigger status.

## 7. Retail Fixed Matrix

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

## 8. Crypto Fixed Matrix

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

## 9. Structural Trend Indicator Panel

| 結構指標 | 今日方向 toward / against / mixed / insufficient | 信心 | 支撐 signal IDs | 反向 signal IDs | 缺口 | 一句判斷 | 下一步驗證 |
|---|---|---|---|---|---|---|---|
| 生產力便車無法共享的 K 型經濟 |  |  |  |  |  |  |  |
| AI 泡沫 / 過度投資趨勢 |  |  |  |  |  |  |  |
| 品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾 |  |  |  |  |  |  |  |

These are cumulative direction meters, not single-day conclusions. Do not force direction when evidence is weak.

## 10. New Information / History Duplicate Check

| ID | primary_domain | 今日新增點 | 是否重複歷史主題 | 可否計入正式訊號 | 拒絕原因 / 保留原因 |
|---|---|---|---|---|---|

## 11. Technology Development Check

```text
AI-driven technology breakthrough:
Standalone non-AI technology breakthrough:
Non-AI subdomains checked (minimum 6):
Technology maturity labels:
AI-overcapture check:
Taiwan technology mapping:
Remaining gap:
```

AI supply chain / AI governance cannot consume Technology quota.

## 12. Source Coverage / Candidate Discovery Audit

```text
source_library_checked:
priority_sources_checked:
source_hits:
source_misses:
niche_source_types_checked:
formation_level_coverage:
non-English/regional sources checked:
social-first sources checked when required:
fashion/style/brand sources checked when relevant:
keyword_fallback_used:
external_discovery_used:
official/data cross-check used:
Taiwan_sources_checked:
remaining_source_gap:
```

## 13. Data Gaps and Retry Notes

| 缺口 | 已嘗試 | 下一步 |
|---|---|---|

## 14. Final Synthesis and Backtest

```text
今日主旋律：
支撐新聞 ID：
判斷類型：模型歸納，不是單一新聞

台灣新聞總結：
結構指標總結：
推播後回測：
模型調整：
```

## Completion Gate

Formal completion requires six domains, >=5 major signals and >=5 qualified niche candidates per domain when available, daily execution quality gate, candidate type / formation level / fresh concrete anchor, retry before gaps, 7-day de-duplication, primary-domain de-dup, evidence grading, Taiwan news checks, Retail fixed matrix, Crypto fixed matrix, Structural Trend Indicator Panel, technology anti-overcapture checks, source audits, and post-report backtest.

If any required gate is missing, mark `partial full report` or `搜尋未完整`.
