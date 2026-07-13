# 三個核心結構趨勢指標

本檔是三個長期主指標的人類可讀入口。這三項不是一般新聞分類，也不是每日動能分數；它們是跨日累積、必須同時考慮支持證據、反向證據、資料缺口與下一次驗證的結構方向計。

## 權威位置

```text
config/runtime_contract.json               canonical IDs and required presence
configs/structural_trend_indicators.yml    thesis, support/counter indicators and evidence to seek
src/radar/contracts/report.py              RadarReportV2 structural observation contract
src/radar/evaluators/matrices.py           deterministic evaluation implementation
config/ai_analysis.json                    labels and primary display order in AIAnalysisV1
src/radar/contracts/analysis.py            AIAnalysisV1 labelled projection contract
web/src/pages/analysis.astro               primary website panel
```

每個指標都先拆成可觀察的細分指標。網站先顯示細分指標的新聞 evidence、摘要、支持／反向方向與 component score，最後才顯示整體指標分數。

搜尋下列任一名稱或 ID，都應能找到本檔、runtime contract、詳細規格與網站輸出：

```text
AI 泡沫
過度投資
K 型經濟
生產力便車無法共享
品牌兩極化
真分眾
假分眾
k_shaped_ai_productivity_economy
ai_bubble_overinvestment
brand_market_polarization_and_true_vs_fake_segmentation
```

## 1. 生產力便車無法共享的 K 型經濟

ID：`k_shaped_ai_productivity_economy`

核心問題：AI 與自動化帶來的生產力利益，是否主要流向資本、平台、大企業與高技能人才，而沒有廣泛傳到實質薪資、初階職缺、中小企業與中等收入消費。

主要支持訊號：

- 生產力上升但實質薪資停滯
- 企業利潤擴大但薪資未同步
- AI CapEx 上升，同時裁員或凍結招聘
- 初階／中階職缺下降
- AI 生產力效益集中在大型企業
- 資產價格漲幅高於勞動所得
- 高價與低價消費優於中間價位

反向訊號：

- 廣泛實質薪資成長
- 中小企業導入 AI 後利潤或存活改善
- 生產力成果轉成價格下降
- 初階與 AI 協作職缺擴張
- 工具價格下降並廣泛普及

## 2. AI 泡沫／過度投資趨勢

ID：`ai_bubble_overinvestment`

核心問題：AI 估值、資料中心、GPU／HBM、電力、CapEx 與融資，是否跑在可持續收入、現金流、利用率、毛利與企業 ROI 之前。

主要支持訊號：

- AI CapEx 增速高於 AI 收入
- 資料中心債務或專案融資增加
- GPU／HBM／電力訂單提前拉貨
- 估值擴張但現金流能見度不足
- 折舊、電力、冷卻與推理成本壓力增加
- 模型價格競爭壓縮毛利
- 企業試點疲勞、續約與 ROI 不清楚
- AI winner trade 過度擁擠

反向訊號：

- AI 收入追上或超過 CapEx
- 付費採用、續約與 ROI 清楚
- AI 產品擴大利潤率
- 資料中心維持高利用率
- CapEx 由營運現金流支應且無槓桿壓力

## 3. 品牌兩極化＋真分眾／假分眾

ID：`brand_market_polarization_and_true_vs_fake_segmentation`

核心問題：市場是否走向大品牌與平台更強、真正差異化小眾品牌仍能存活、缺乏差異的中間品牌萎縮；同時檢查 AI 個人化究竟改變了商品與營運，還是只改文案與廣告表面。

市場兩極化支持訊號：

- 頭部品牌／平台市占與利潤率增加
- 中價品牌折扣、撤櫃或關店增加
- 百貨 tenant mix 轉向精品、低價、體驗與目的型業態
- 小眾品牌售出率、原價率或回購具有韌性
- AI 搜尋、平台與社群演算法使注意力更集中
- 高價與低價優於中價

真分眾：

- 商品設計、材質、版型、品類真的不同
- 使用情境、場合或社群身份不同
- 商品組合、陳列、通路與定價邏輯不同
- 原價售出率、回購、會員行為真的分化

假分眾：

- 同一商品只換 AI 文案、persona 或 landing page
- 只有廣告、prompt、推薦標籤不同
- 點擊提升但回購、毛利與原價率未改善
- 客群名稱很多，商品和營運沒有差異
- 宣稱小眾，但 assortment 高度通用

## 每日輸出契約

每個指標固定輸出：

```text
indicator_id
direction: toward | against | mixed | insufficient
support_score
counter_score
confidence
supporting_signal_ids
counter_signal_ids
missing_data
one_sentence_read
next_verification
evaluation_mode
```

規則：

1. 三項全部都必須出現，不能因資料不足而省略。
2. 資料不足時輸出 `insufficient`，不得硬推方向。
3. 同一事件不得拆成多個獨立支持訊號灌高分數。
4. AI 可以統整與解讀，但不得修改 deterministic 方向、分數、證據 ID 或缺口。
5. `AIAnalysisV1.linked_indicators` 的六個每日動能／品質分數只是輔助訊號，不能取代本頁三項。
