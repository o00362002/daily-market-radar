# Daily Push Brief Template

Daily Push Brief is a structured concise radar, not a free-form summary.

```text
Daily Push Brief 不代表可刪減結構。
Brief 只代表單則內容字數較短。
所有章節、欄位、證據追溯、台灣新聞、指標狀態仍必須完整保留。
```

Required shared rule:

```text
configs/news_freshness_and_taiwan_news.yml
```

Important correction:

```text
「台灣映射」在 Daily Push Brief 中改為「台灣新聞」。
使用者要的是台灣新聞內容，不是模型把國際新聞套到台灣的策略推論。
每個領域的台灣段必須優先放台灣本地新聞 / 官方資料 / 公司動作 / 數據 / 產業事件。
若當日查無合格台灣新聞，必須寫「台灣新聞不足」與已查來源，不得用泛泛台灣影響補位。
```

New information rule:

```text
每日情報必須優先提供今日新增資訊。
不得用昨日或歷史已播概念重複填滿 3+1。
若重複歷史主題，必須有新數據 / 新公司動作 / 新政策 / 新市場反應 / 新鏈上數據 / 新台灣新聞，否則不得列入大型訊號。
```

---

## 0. Basic Info

```text
報告日期：YYYY/MM/DD（星期X）台灣時間
輸出模式：每日推播精簡版
精簡版狀態：complete concise brief / partial concise brief
完整 48 則正式閘門：未嘗試 / 未通過 / 另需分段研究版
系統資料讀取狀態：已讀取 / 部分無法讀取 / 無法讀取
歷史去重狀態：已檢查近期 reports / 未完整
結構閘門狀態：通過 / 未通過
新資訊密度狀態：通過 / 偏低 / 未通過
台灣新聞狀態：通過 / 不足 / 未完整
```

---

## 1. Six-domain Coverage Matrix

| 核心領域 | 掃描狀態 | 大型訊號數 | 小眾候選數 | 台灣新聞數 | Evidence Trace | New Info Check | 今日狀態 | 漏抓風險 |
|---|---|---:|---:|---:|---|---|---|---|
| AI / Agent / 工作流 |  | 3 | 1 | 1–2 | required | required |  |  |
| 加密 / RWA / Agent payments |  | 3 | 1 | 1–2 | required | required |  |  |
| 零售 / 消費 / 社群 / 服飾 |  | 3 | 1 | 1–2 | required | required |  |  |
| 全球市場 / 資金流 / 地緣 |  | 3 | 1 | 1–2 | required | required |  |  |
| 科技發展 / 半導體 / 能源 / 機器人 |  | 3 | 1 | 1–2 | required | required |  |  |
| 勞動 / 消費壓力 / 台灣 |  | 3 | 1 | 1–2 | required | required |  |  |

---

## 2. Domain Blocks

Each domain must include exactly:

```text
大型訊號：3 則
小眾候選：1 則
台灣新聞：1–2 則
```

News / signals must be real events, data changes, company actions, policy changes, product releases, market moves, or source-backed observations.

Indicators, synthesis, themes, Taiwan implications, and model conclusions must not be counted as news.

Each news item must keep concise evidence trace:

```text
ID：
事件：
今日新增點：
來源 / 時間：
證據等級：high / medium / low / insufficient_data
是否重複歷史主題：new_today / repeated_theme_with_new_data / repeated_theme_with_new_company_action / repeated_theme_with_new_policy / repeated_theme_with_new_market_reaction / repeated_theme_with_new_taiwan_news / background_only_do_not_count / historical_replay_do_not_count
不確定點 / 下一步：
```

Each Taiwan news item must keep the same trace:

```text
ID：TW-[DOMAIN]-1
台灣新聞：
今日新增點：
來源 / 時間：
證據等級：
是否重複歷史主題：
不確定點 / 下一步：
```

---

### 2.1 AI / Agent / 工作流

**大型訊號（3）**
1. ID：AI-1｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
2. ID：AI-2｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
3. ID：AI-3｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**小眾候選（1）**
- ID：AI-C1｜候選訊號：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**台灣新聞（1–2）**
- ID：TW-AI-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-AI-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

---

### 2.2 加密 / RWA / Agent payments

**大型訊號（3）**
1. ID：CRYPTO-1｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
2. ID：CRYPTO-2｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
3. ID：CRYPTO-3｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**小眾候選（1）**
- ID：CRYPTO-C1｜候選訊號：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**台灣新聞（1–2）**
- ID：TW-CRYPTO-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-CRYPTO-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

---

### 2.3 零售 / 消費 / 社群 / 服飾

**大型訊號（3）**
1. ID：RETAIL-1｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
2. ID：RETAIL-2｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
3. ID：RETAIL-3｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**小眾候選（1）**
- ID：RETAIL-C1｜候選訊號：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**台灣新聞（1–2）**
- ID：TW-RETAIL-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-RETAIL-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

---

### 2.4 全球市場 / 資金流 / 地緣

**大型訊號（3）**
1. ID：MARKET-1｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
2. ID：MARKET-2｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
3. ID：MARKET-3｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**小眾候選（1）**
- ID：MARKET-C1｜候選訊號：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**台灣新聞（1–2）**
- ID：TW-MARKET-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-MARKET-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

---

### 2.5 科技發展 / 半導體 / 能源 / 機器人

**大型訊號（3）**
1. ID：TECH-1｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
2. ID：TECH-2｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
3. ID：TECH-3｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**小眾候選（1）**
- ID：TECH-C1｜候選訊號：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**台灣新聞（1–2）**
- ID：TW-TECH-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-TECH-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

---

### 2.6 勞動 / 消費壓力 / 台灣

**大型訊號（3）**
1. ID：LABOR-1｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
2. ID：LABOR-2｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
3. ID：LABOR-3｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**小眾候選（1）**
- ID：LABOR-C1｜候選訊號：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**台灣新聞（1–2）**
- ID：TW-LABOR-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-LABOR-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

---

## 3. Retail Focus Block

Retail Focus Block must preserve the five fixed checks. It should reference news IDs above and must prioritize Taiwan retail news when discussing Taiwan.

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

台灣零售 / 商圈 / 百貨 / 品牌訊號：
  台灣新聞依據：
  資料缺口：
  下一步：
```

---

## 4. New Information / History Duplicate Check

| 新聞 ID | 今日新增點 | 是否重複歷史主題 | 可否計入 3+1 | 原因 |
|---|---|---|---|---|
|  |  |  | yes / no |  |

---

## 5. Data Gaps and Retry Notes

| 缺口 | 已嘗試 | 下一步 |
|---|---|---|
| 台灣新聞不足 |  |  |
| 新資訊不足 |  |  |
| 歷史去重未完整 |  |  |

---

## 6. Final Indicator Status and News Synthesis Panel

This panel is required but must stay at the end of the brief.

Indicators and conclusions are not news. They must not be counted toward the 3+1 domain quota.

### 6.1 Indicator Status Summary

| 指標領域 | 今日狀態 | 方向 | 支撐新聞 ID | 資料缺口 |
|---|---|---|---|---|

### 6.2 Today’s Main Themes

```text
主旋律 1：
支撐新聞：
判斷類型：模型歸納 / 資料判斷，不是單一新聞
```

### 6.3 Taiwan News Summary

```text
今日台灣新聞重點：
1.
2.
3.

台灣新聞不足領域：
- 
```

### 6.4 Post-brief Review

```text
今日漏抓風險：
新資訊密度：通過 / 偏低 / 未通過
台灣新聞完整度：通過 / 不足 / 未完整
是否需啟動完整研究版：yes / no
是否需交給 news_content_agent 產內容：yes / no
模型調整：
今日最終一句話：
```

### 6.5 Misread Guard

```text
上述指標狀態與今日主旋律為報告歸納，不是新聞本體。
台灣段落若無台灣新聞，不得用台灣推論補位。
所有指標與結論必須回指上方新聞 ID。
若無法回指新聞 ID，必須標示為資料缺口或候選推論。
```