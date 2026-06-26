# Daily Market Radar

這個專案是「全球每日市場情報雷達系統」的版本控管中心，不是單純存放新聞摘要。

每日播報在執行前，應先讀取本 repo 的規格、雷達清單、漏抓案例、歷史報告與回測規則，再進行多語言搜尋與交叉驗證。

## 核心定位

- 不是新聞摘要器。
- 不是只挑幾則主觀重要新聞的編輯。
- 是一套「雷達覆蓋與證據分級型」每日市場情報系統。
- 目標是同時捕捉：
  - 全球大趨勢
  - 資金與政策變化
  - 產業結構變化
  - AI 工作流替代
  - 加密與鏈上資金流
  - 零售、消費、社群、流行與服飾訊號
  - 早期弱訊號與候選訊號
  - 台灣產業映射

## 每日執行順序

1. 讀取 `SYSTEM_PROMPT.md`
2. 讀取 `configs/radars.yml`
3. 讀取 `configs/triggers.yml`
4. 讀取 `configs/evidence.yml`
5. 讀取 `configs/source_strategy.md`
6. 讀取 `memory/missed_cases.md`
7. 讀取 `memory/watchlist.md`
8. 讀取近期 `reports/` 內的歷史報告，避免跨日重複與漏抓
9. 使用 `templates/daily_report_template.md` 產出每日報告
10. 報告最後更新 `推播後回測與模型調整面板`

## 重要規則

- 若資料不足，必須寫「資料不足」。
- 若因果未確認，只能寫「產業訊號」或「待驗證推論」。
- 候選訊號不得因證據不足被刪除。
- 使用者指出的漏抓事件，必須進入 `memory/missed_cases.md` 的硬檢查清單。
- 跨領域事件必須標示受影響的所有雷達。

## 報告索引

| 日期 | 檔案 | 本次整理內容 |
|---|---|---|
| 2026-06-07 | `reports/2026/2026-06-07.md` | 含原始推播、V2.1 重做版、AI Agent／生產力便車／潛力鏈生態修正、零售品牌／商圈／百貨補洞 |
| 2026-06-08 | `reports/2026/2026-06-08.md` | 含當日推播、Strategy／STRC 漏抓反思、結構性漏抓檢查、最終推播規則整合 |

## 建議檔案命名

每日報告建議放在：

```text
reports/YYYY/YYYY-MM-DD.md
```

例如：

```text
reports/2026/2026-06-26.md
```

## 使用方式

每日產出前，對 AI 說：

```text
請先讀取 GitHub repo `o00362002/daily-market-radar` 的 SYSTEM_PROMPT、configs、memory、templates 與近期 reports，再依照規格搜尋最新資訊，產出今日每日市場情報報告。
```
