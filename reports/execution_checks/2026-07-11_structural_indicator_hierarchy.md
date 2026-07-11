# Structural indicator hierarchy restoration

日期：2026-07-11

## 問題

AIAnalysisV1 首版把六個每日動能／品質分數統稱為「連動指標」，網站也以此作為唯一指標區。專案其實早已在 runtime contract、structural config、舊報告與 CURRENT_DECISIONS 記錄三個長期結構主指標，但入口與顯示層沒有把主從關係說清楚，容易被誤判為專案沒有保存原始需求。

## 接受的層級

```text
Primary structural indicators
1. k_shaped_ai_productivity_economy
2. ai_bubble_overinvestment
3. brand_market_polarization_and_true_vs_fake_segmentation

Secondary auxiliary signal indicators
1. ai_application_momentum
2. retail_change_momentum
3. crypto_rwa_adoption_momentum
4. taiwan_exposure_intensity
5. cross_domain_convergence
6. evidence_confidence
```

## 實作

- `AIAnalysisV1` 新增 `structural_indicators`，以標籤化但不可變的形式投影 `RadarReportV2.structural_indicators`。
- `config/ai_analysis.json` 明確拆成 `core_structural_indicators` 與 `auxiliary_signal_indicators`。
- OpenAI bounded payload 同時包含兩層；三個主指標完全唯讀，六個輔助指標只允許模型產生 interpretation。
- `/analysis` 先顯示三個核心結構指標，再顯示重點判讀、趨勢與輔助訊號面板。
- 新增 `docs/structural-indicators.md`，把三個名稱、ID、支持／反向訊號、輸出契約與所有權威路徑集中成可檢索入口。
- README 與 CURRENT_STATE 增加明確索引，避免需要從舊報告考古。

## 不變式

- 三個核心指標每日都必須存在；證據不足輸出 `insufficient`，不得省略。
- AI 不得修改方向、support/counter score、confidence、signal IDs、missing data 或 next verification。
- 六個輔助訊號不能被稱為或取代三個核心結構指標。
- 同一事件不得拆成多個獨立支持訊號灌高分數。

## Repo-wide retrieval audit

完成後應以以下查詢逐項驗證：

```text
AI 泡沫
K 型經濟
真分眾
假分眾
k_shaped_ai_productivity_economy
ai_bubble_overinvestment
brand_market_polarization_and_true_vs_fake_segmentation
```

每個查詢至少應命中：

- `README.md` 或 `CURRENT_STATE.md`
- `docs/structural-indicators.md`
- `config/runtime_contract.json`
- `configs/structural_trend_indicators.yml`
- 實作或網站檔案

## 驗證關口

- runtime-check
- web-check
- mount-check
- AIAnalysisV1 schema and immutability tests
- OpenAI provider structural-preservation test
- Astro build
- repo-wide keyword retrieval audit
