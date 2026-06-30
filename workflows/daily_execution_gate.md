# daily-market-radar｜每日執行模式化閘門

本檔用來定義每日輸出的最小執行閘門。

核心原則：

```text
1. 閘門必須依照 `AGENT_DEFINITION_MAP.md` 的 route 判定。
2. 閘門必須依照 `DEPENDENCY_MAP.md` 的 active output mode 連動。
3. 不同輸出模式不得互相誤用完成標準。
4. Daily Push Brief 可標示為 concise complete，但不得宣稱通過 full 48-signal formal gate。
5. Full Daily Radar 若未達 5+3，不得稱為完整正式播報。
```

---

## 1. Mode Selection Gate

每日輸出前，必須先選擇一個 primary route：

```text
AGENT_RADAR_REPORT
AGENT_DAILY_PUSH_BRIEF
AGENT_NEWS_SEARCH
AGENT_NEWS_CONTENT
AGENT_COVERAGE_BACKTEST
AGENT_RADAR_CONFIG
```

路由來源以 `AGENT_DEFINITION_MAP.md` 為準。

若使用者要求：

```text
今天播報
每日新聞
每日推播
今日市場雷達
先看今天重點
簡版
輕量版
concise brief
daily push
```

預設 route 必須是：

```text
AGENT_DAILY_PUSH_BRIEF
```

除非使用者明確要求：

```text
完整正式版
完整研究歸檔版
Full Daily Radar
48-signal report
產出 reports/YYYY/YYYY-MM-DD.md
```

才可選擇：

```text
AGENT_RADAR_REPORT
```

---

## 2. Dependency-linked Gate

閘門必須依照 `DEPENDENCY_MAP.md` 的 active output mode 選擇對應 workflow 與 template。

```text
AGENT_RADAR_REPORT
→ workflows/daily_radar_workflow.md
→ templates/daily_report_template.md
→ Full Daily Radar Gate

AGENT_DAILY_PUSH_BRIEF
→ workflows/daily_push_brief_workflow.md
→ templates/daily_push_brief_template.md
→ Daily Push Brief Gate
```

若 route、workflow、template、gate 不一致，必須標示：

```text
依賴鏈不一致：partial / blocked
```

不得輸出為 complete。

---

## 3. Full Daily Radar Gate

適用 route：

```text
AGENT_RADAR_REPORT
```

通過條件：

```text
6 大核心領域皆達 5 則大型重要新聞 + 3 則小眾潛力候選
已完成必要 repo 檔案讀取
已完成搜尋
已完成最近 7 日 reports 去重
已完成高風險 claim 檢查
已輸出 Coverage Matrix
已輸出 Data Gaps / Retry Notes
```

只有全部通過，才可標示：

```text
完整正式播報：通過
```

若任一項未完成，必須標示：

```text
完整正式播報：未通過
不可視為完整正式播報
```

---

## 4. Daily Push Brief Gate

適用 route：

```text
AGENT_DAILY_PUSH_BRIEF
```

通過條件：

```text
已讀取必要入口檔，或明確揭露缺失
6 大核心領域皆有覆蓋
每一核心領域包含 2–3 則大型訊號
每一核心領域包含 1 則小眾 / 潛力候選
每一核心領域包含台灣映射
Retail Focus Block 存在
Data Gaps and Retry Notes 存在
Post-brief Review 存在
```

通過時只能標示：

```text
輸出模式：每日推播精簡版
精簡版狀態：complete
完整 48 則正式閘門：未嘗試 / 未通過 / 另需分段研究版
```

不得因為未達 5+3 而把 Daily Push Brief 判定為失敗。

若精簡版缺少任一必要項目，標示：

```text
精簡版狀態：partial concise brief
```

---

## 5. Coverage Matrix Rules

### Full Daily Radar

| 核心領域 | 大型新聞數 | 小眾候選數 | 是否達標 | 缺口 |
|---|---:|---:|---|---|
| AI 模型 / Agent / 工作流替代 | >=5 | >=3 |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | >=5 | >=3 |  |  |
| 零售 / 消費 / 社群 / 服飾 | >=5 | >=3 |  |  |
| 全球市場 / 資金流 / 地緣政治 | >=5 | >=3 |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | >=5 | >=3 |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | >=5 | >=3 |  |  |

### Daily Push Brief

| 核心領域 | 大型訊號數 | 小眾候選數 | 台灣映射 | 精簡版狀態 | 漏抓風險 |
|---|---:|---:|---|---|---|
| AI 模型 / Agent / 工作流替代 | 2–3 | 1 | required |  |  |
| 區塊鏈 / 加密 / RWA / Agent payments | 2–3 | 1 | required |  |  |
| 零售 / 消費 / 社群 / 服飾 | 2–3 | 1 | required |  |  |
| 全球市場 / 資金流 / 地緣政治 | 2–3 | 1 | required |  |  |
| 科技發展 / 機器人 / 生技 / 能源 / 半導體 | 2–3 | 1 | required |  |  |
| 勞動 / 消費壓力 / 台灣本地訊號 | 2–3 | 1 | required |  |  |

---

## 6. High-risk Claim Gate

所有模式都適用。

高風險 claim 包含：

```text
精確數字
重大政策
公司重大事件
新技術突破
加密資金流
台灣本地判斷
外部模型提供的陌生訊號
```

每日報告若包含高風險 claim，需輸出：

| Claim | 來源 / 可回查線索 | 來源時間 | 證據等級 | 採用狀態 | 處理方式 |
|---|---|---|---|---|---|
|  |  |  | 高 / 中 / 低 / 資料不足 | 採用 / 降級 / 不採用 |  |

判定：

```text
官方、權威媒體、多來源交叉驗證 → 可採用
可信媒體但資料不完整 → 可採用，但標中證據與不確定點
只有社群或模型敘事 → 只能列候選
查不到來源 → 不得放入事實區
來源支持方向但不支持數字 → 方向保留，數字降級或不採用
來源支持舊事件但不是今日新事件 → 標示為背景訊號或歷史已播
```

---

## 7. Failure Output

若 route、workflow、template、gate 不一致，必須輸出：

```text
本次輸出依賴鏈不一致。
不可視為 complete。

不一致原因：
1. route：
2. workflow：
3. template：
4. gate：

修正方式：
1.
2.
3.
```

若 Full Daily Radar 未通過，輸出：

```text
本次報告未通過完整正式版閘門。
不可視為完整正式播報。
未通過原因：
1.
2.
3.
下一步補查：
1.
2.
3.
```

若 Daily Push Brief 未完整，輸出：

```text
本次為 partial concise brief。
不可視為完整精簡版。
缺少項目：
1.
2.
3.
下一步補查：
1.
2.
3.
```

---

## 8. 外部模型輸出規則

外部模型輸出不得直接併入正式報告。

必須先經過：

```text
外部模型輸出 → 拆成高風險 claim → 查來源 → 證據分級 → 採用 / 降級 / 不採用 → 回補到報告或規則
```

外部模型適合當 scout，不可直接當 judge。
