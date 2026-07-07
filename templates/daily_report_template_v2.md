# Full Daily Radar Report Template V2

Use with:

```text
workflows/daily_radar_workflow.md
configs/news_freshness_and_taiwan_news.yml
configs/niche_candidate_policy.yml
configs/technology_development.yml
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
| AI 模型 / Agent / 工作流替代 | >=5 | >=5 | required | required | required |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | >=5 | >=5 | required | required | required |  |  |
| 零售 / 消費 / 社群 / 服飾 | >=5 | >=5 | required | required | required |  |  |
| 全球市場 / 資金流 / 地緣政治 | >=5 | >=5 | required | required | required |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | >=5 | >=5 | required | required | required |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | >=5 | >=5 | required | required | required |  |  |

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

Rule: Taiwan implication cannot replace Taiwan news. Historical replay without today-new information does not count toward 5+5.

## 4. Niche / Potential Signals by Domain

Each domain target: at least 5 qualified niche candidates when available, equal to the major-signal target.

Each counted candidate must include:

```text
ID:
候選訊號:
具體錨點:
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
候選必須有具體公司 / 產品 / 論文 / 數據 / 融資 / 招聘 / 開源採用 / 鏈上指標 / 社群事件 / pilot / patent / clinical trial / prototype / supply-chain anomaly 等錨點。
不得用空泛趨勢句補位。
不得把大型主流新聞換句話說當候選。
主流 wires 不足以完成候選搜尋，必須擴展研究、新創、產品、小眾產業、開發者、社群、招聘、鏈上與區域 / 非英語來源。
不足 5 則時先 retry / external discovery；仍不足才標示 gap，不得捏造。
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

Taiwan crypto must include fixed-source audit and legislative-trigger status.

## 6. New Information / History Duplicate Check

| ID | 今日新增點 | 是否重複歷史主題 | 可否計入正式訊號 | 原因 |
|---|---|---|---|---|

## 7. Technology Development Check

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

## 8. Retail Focus Block

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

## 9. Source Coverage / Candidate Discovery Audit

```text
source_library_checked:
priority_sources_checked:
niche_source_types_checked:
non-English/regional sources checked:
social-first sources checked when required:
keyword_fallback_used:
external_discovery_used:
official/data cross-check used:
remaining_source_gap:
```

## 10. Data Gaps and Retry Notes

| 缺口 | 已嘗試 | 下一步 |
|---|---|---|

## 11. Final Synthesis and Backtest

```text
今日主旋律：
支撐新聞 ID：
判斷類型：模型歸納，不是單一新聞

台灣新聞總結：

推播後回測：

模型調整：
```

## Completion Gate

Formal completion requires six domains, >=5 major signals and >=5 qualified niche candidates per domain when available, retry before gaps, 7-day de-duplication, evidence grading, Taiwan news checks, technology anti-overcapture checks, source audits, and post-report backtest.
