# 2026-07-09 Missed Case：低新奇度、重複、台灣缺口、真分眾 / 假分眾漏項

## Status

- 狀態：active missed case / next-run hard check
- 觸發來源：使用者回饋
- 影響任務：Daily Push Brief / Full Daily Radar / News Search Output

---

## User feedback

2026-07-09 的每日市場情報報告仍不滿意，主要問題：

1. 大眾訊號有些重複。
2. 領域之間有些內容重複。
3. 小眾候選與新的消息太少，這是最大落差。
4. 台灣內容幾乎沒有。
5. 長期結構指標少了「真分眾 / 假分眾」，且應與「大品牌更大、小眾品牌存活、中間品牌被排擠」合併追蹤。

---

## Confirmed diagnosis

### A. 大眾訊號重複

- 原因：7 日去重沒有完整跑。
- 結果：前日延續主題、背景題或同一事件不同角度占用 major quota。
- 修正：每則 major signal 必須有 concrete fresh delta / today_new_information，否則不計 quota。

### B. 領域重複

- 原因：AI、勞動、科技、市場之間的 cross-domain 訊號沒有建立 primary-domain rule。
- 結果：同一 AI / CapEx / labor story 重複塞入多個 domain。
- 修正：同一新聞只能有一個 primary domain；其他領域只能在 cross-domain mapping / indicator panel 引用，不可重複計 quota。

### C. 小眾候選新奇度不足

- 原因：candidate discovery 太依賴 mainstream wires / broad search，retry 不足。
- 結果：候選變成大型新聞改寫、研究背景、概念延伸或老主題。
- 修正：小眾候選必須具備 fresh concrete anchor，並標 candidate_type + formation_level。

### D. 台灣內容不足

- 原因：台灣 direct sources、social-first sources、品牌 / 百貨 / 加密固定來源沒有完整直查。
- 修正：台灣不足時不可硬寫映射；必須輸出 direct-source audit。

### E. 真分眾 / 假分眾漏項

- 修正：已併入 `configs/structural_trend_indicators.yml` 的品牌兩極化指標：
  `品牌大者更大 + 小眾存活 + 中間層萎縮 + 真分眾 / 假分眾`。

---

## Next-run hard checks

下次每日播報執行前必須先跑以下檢查，否則標 partial / failed gate：

```text
1. run_source_audit_before_drafting
2. reject_major_signal_without_fresh_delta_or_today_new_information
3. reject_niche_candidate_without_fresh_concrete_anchor
4. reject_niche_candidate_that_is_only_major_signal_rephrasing
5. reject_old_background_concept_as_today_news
6. do_not_replace_taiwan_news_with_taiwan_implication
7. output_structural_trend_indicator_panel
8. include_true_vs_fake_segmentation_check_under_brand_polarization
9. disclose_taiwan_direct_source_gap_if_not_checked
10. record_duplicate_rejection_count
11. record_niche_low_novelty_rejection_count
12. record_candidate_retry_paths_used
```

---

## Candidate discovery retry paths required

若小眾候選不足，不得直接補趨勢感想。必須依序 retry：

```text
1. startup / funding / product launch sources
2. research papers / datasets
3. developer tools / open-source / release notes
4. regional and non-English sources
5. social-first / channel-first sources
6. hiring / job posting shifts
7. on-chain and market microstructure data
8. patents / clinical trials / regulatory pilots
9. fashion / brand / merchandising / assortment sources
10. Taiwan direct sources
```

---

## Required backtest fields in next report

```text
duplicate_rejection_count:
field_overlap_rejection_count:
niche_low_novelty_rejection_count:
candidate_retry_paths_used:
Taiwan_qualified_item_count_after_audit:
Taiwan_direct_sources_checked:
structural_thesis_evidence_change:
true_vs_fake_segmentation_status:
```
