# 2026-07-09 Missed Case：Low Novelty + Missing Structural Trend Indicators

## Status

- 日期：2026-07-09
- 狀態：active missed case / model adjustment required
- 影響任務：Daily Push Brief / Full Daily Radar / Indicator Panel / Future Outlook

---

## Problem

今日每日市場情報報告整體新聞內容新訊息不足，小眾候選內容也不如預期。

使用者指出：每日報告除了新聞和短期指標，還需要固定追蹤幾條長期結構方向，特別是：

1. 生產力便車無法共享的 K 型經濟
2. AI 泡沫趨勢
3. 品牌大者更大 + 小眾存活，中間層越來越少

---

## Diagnosis

### A. 小眾候選不夠新奇

可能原因：

- 太依賴主流新聞與前一日延續訊號。
- 未完整跑非主流來源、社群 first source、論文、招聘、鏈上、品牌官方與時尚 / 零售專業來源。
- 部分小眾候選只是大型新聞的再分類，不是獨立早期訊號。
- 今日新增點標準仍需更嚴格，背景延續不能冒充新訊息。

### B. 指標分析還不夠結構化

原本 Indicator Panel 偏短期：AI CapEx、油價、RWA、robotics、labor 等。

缺少長期 thesis tracking，也就是要回答：

```text
今天的新訊號是否讓我們更接近某個結構未來？
還是反向？
還是資料不足？
```

---

## New Required Structural Trend Indicators

已新增 `configs/structural_trend_indicators.yml`，之後每日報告必須固定評估：

### 1. 生產力便車無法共享的 K 型經濟

判斷方向：toward / against / mixed / insufficient

要看：

- 生產力上升但實質薪資不動
- 公司毛利率提升但薪資未同步
- AI CapEx 上升同時裁員 / 凍聘
- 初階 / 中階職缺下降
- 大公司先拿到 AI 工具與資料優勢
- 低收入消費弱，高收入消費強
- 自動化降本沒有轉成消費者價格下降

### 2. AI 泡沫趨勢

判斷方向：toward / against / mixed / insufficient

要看：

- AI CapEx 成長快於 AI revenue
- data center 債務與 project finance 上升
- GPU / HBM / memory orders 被提前拉貨
- AI 類股估值與現金流脫鉤
- model price competition 壓縮毛利
- 企業 ROI 不明、pilot fatigue
- 央行 / 監管提 AI 金融穩定風險

### 3. 品牌大者更大 + 小眾存活，中間層萎縮

判斷方向：toward / against / mixed / insufficient

要看：

- 大平台 / 大品牌市佔上升
- 中價品牌折扣增加、關店、庫存老化
- 百貨 tenant mix 轉向精品、低價、體驗或高流量 tenant
- 小眾品牌靠社群、身份認同、稀缺性存活
- AI search / marketplace 對結構化大 catalog 有利
- 低價平台與 private label 壓縮中間層

---

## Output Rule

之後 Daily Push Brief 與 Full Daily Radar 必須在 Final Panel 前加入：

```text
## Structural Trend Indicator Panel

| 長期結構假說 | 今日方向 | 信心 | 支撐訊號 | 反向訊號 | 缺口 | 一句話判斷 | 下一步驗證 |
```

三個 thesis 必填：

```text
1. 生產力便車無法共享的 K 型經濟
2. AI 泡沫趨勢
3. 品牌大者更大 + 小眾存活，中間層萎縮
```

若資料不足，必須寫 insufficient，不得硬判斷。

---

## Model Adjustment

1. 每日新聞不只問「發生什麼」，也問「這讓哪個長期 thesis 更成立或更不成立？」
2. 小眾候選不足時，不能用主流新聞換句話說補位。
3. 每次小眾候選要優先搜尋：
   - 論文 / 研究
   - 新創 / 融資
   - 招聘 / 職缺
   - 鏈上 / 用量數據
   - 品牌官方 / 商品組合
   - 時尚 / 零售專業來源
   - 社群 first source
4. Long-term thesis tracking 必須獨立於短期 market / news 指標。

---

## Backtest Tag

```text
missed_case_type: low_novelty_candidate_gap + missing_structural_thesis_tracking
severity: medium_high
must_check_next_run: true
```
