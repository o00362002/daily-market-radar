# Full Daily Radar Report Template V2

Use with:

```text
workflows/daily_radar_workflow.md
configs/news_freshness_and_taiwan_news.yml
```

## 0. Basic Info

```text
報告日期時間：YYYY/MM/DD（星期X）HH:mm（台灣時間）
輸出模式：完整正式歸檔版
系統資料讀取狀態：
歷史報告去重狀態：
每日訊號硬閘門狀態：通過 / 未通過 / 搜尋未完整
新資訊密度狀態：通過 / 偏低 / 未通過
台灣新聞狀態：通過 / 不足 / 未完整
```

## 1. Coverage Matrix

| 核心領域 | 大型新聞數 | 小眾候選數 | 台灣新聞數 | New Info Check | Evidence Trace | 是否達標 | 缺口 |
|---|---:|---:|---:|---|---|---|---|
| AI 模型 / Agent / 工作流替代 | >=5 | >=3 | required | required | required |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | >=5 | >=3 | required | required | required |  |  |
| 零售 / 消費 / 社群 / 服飾 | >=5 | >=3 | required | required | required |  |  |
| 全球市場 / 資金流 / 地緣政治 | >=5 | >=3 | required | required | required |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | >=5 | >=3 | required | required | required |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | >=5 | >=3 | required | required | required |  |  |

## 2. Mandatory Indicator Tracking

| 大桶 | 指標 | 目前狀態 | 方向 | 異常訊號 | 來源 / 時間 | 下一步驗證 |
|---|---|---|---|---|---|---|

## 3. Major News by Domain

Each counted major news item must include:

```text
ID:
事件:
今日新增點:
來源 / 時間:
證據等級:
是否重複歷史主題:
受影響雷達:
台灣新聞:
台灣影響推論:
不確定點 / 下一步:
```

Rule:

```text
台灣新聞必須是台灣本地新聞 / 官方資料 / 公司動作 / 數據 / 產業事件。
台灣影響推論不得取代台灣新聞。
歷史重複主題若沒有今日新增點，不得計入 5+3。
```

## 4. Niche / Potential Signals by Domain

Each counted candidate must include:

```text
ID:
候選訊號:
今日新增點:
來源 / 時間:
為何小眾 / 早期:
證據等級:
是否重複歷史主題:
台灣新聞:
台灣影響推論:
不能下的結論:
下一步驗證:
```

## 5. Taiwan News Section

```text
今日台灣新聞：
1.
2.
3.

台灣新聞不足領域：
- 領域：
  已查來源：
  已查關鍵字：
  下一步補查：
```

## 6. New Information / History Duplicate Check

| News ID | 今日新增點 | 是否重複歷史主題 | 可否計入正式訊號 | 原因 |
|---|---|---|---|---|

## 7. Retail Focus Block

```text
百貨 / 購物中心 / 街邊店：
  新聞依據：
  台灣新聞依據：
  資料缺口：
  下一步：

品牌展店 / 撤店 / tenant mix：
  新聞依據：
  台灣新聞依據：
  資料缺口：
  下一步：

社群商務 / 內容導購：
  新聞依據：
  台灣新聞依據：
  資料缺口：
  下一步：

服飾庫存 / 折扣 / 中價品牌壓力：
  新聞依據：
  台灣新聞依據：
  資料缺口：
  下一步：
```

## 8. Data Gaps and Retry Notes

| 缺口 | 已嘗試 | 下一步 |
|---|---|---|

## 9. Final Synthesis and Backtest

```text
今日主旋律：
支撐新聞 ID：
判斷類型：模型歸納，不是單一新聞

台灣新聞總結：

推播後回測：

模型調整：
```
