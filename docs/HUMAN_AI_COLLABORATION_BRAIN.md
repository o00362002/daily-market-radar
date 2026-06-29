# Human-AI 協作大腦掛載｜daily-market-radar

> 目的：把 Human-AI 協作大腦從文字規則升級為可版本控管、可案例測試、可回測改善的實際工作流。

## 1. 專案角色

`daily-market-radar` 是 Human-AI 協作大腦的「資訊雷達與趨勢判斷測試場」。

本 repo 不只產出每日摘要，而是用來測試：

- 多來源資訊蒐集是否完整
- 來源引用與發布時間是否清楚
- 趨勢判斷是否早於市場共識
- 缺口檢查是否能降低漏抓
- 回測是否能改善下一次報告

## 2. 掛載到實際案例

每一份市場報告都應被視為一次案例測試。

建議案例類型：

| 類型 | 測試重點 | 輸出位置 |
|---|---|---|
| AI 實際應用 | Agent、企業導入、工作流、權限治理 | `reports/` |
| 零售／百貨／服飾趨勢 | 商圈、展店、撤櫃、tenant mix、品牌動向 | `reports/` |
| 加密與鏈上生態 | RWA、AI x Crypto、Perp DEX、ETF、TVL、Fees | `reports/` |
| 國際市場與地緣政治 | 市場反應、政策、風險事件 | `reports/` |

## 3. 必讀檔案

執行前優先讀取：

1. `SYSTEM_PROMPT.md`
2. `configs/`
3. `memory/`
4. `templates/`
5. `reports/`
6. 本檔案

若聊天記憶與 repo 衝突，以 repo 為準。

## 4. Loops 檢查

每次輸出後要做四段回圈：

1. **Source Loop**：重要事件是否有來源、時間、發布者。
2. **Coverage Loop**：AI、零售、加密、國際市場是否有缺口標示。
3. **Signal Loop**：是否只整理新聞，還是有判斷早期趨勢。
4. **Backtest Loop**：前次漏抓、誤判、低價值訊號是否有修正。

## 5. 成功標準

不是「每天有報告」而已，而是：

- 可追蹤每次判斷依據
- 可回看哪一類訊號被漏掉
- 可比較本週與上週判斷品質
- 可把失敗案例變成下一版規則

## 6. 與其他 repo 的關係

- `retail-not-magic-social-lab`：把市場訊號轉成社群內容題材。
- `retailops-agent-system`：把雷達流程抽象成可委派 Agent / Skill。
- `c2c-store-ops`：把零售與百貨訊號回灌到真實門市營運判斷。
