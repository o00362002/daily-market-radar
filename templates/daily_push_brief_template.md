# Daily Push Brief Template

Daily Push Brief is a structured concise radar, not a free-form summary.
Concise means shorter wording per item, not fewer reconnaissance categories.

Required shared rules:

```text
configs/news_freshness_and_taiwan_news.yml
configs/source_routing_rules.yml
configs/niche_candidate_policy.yml
configs/technology_development.yml
```

## 0. Basic Info

```text
報告日期：YYYY/MM/DD（星期X）台灣時間
輸出模式：每日推播精簡版
精簡版狀態：complete concise brief / partial concise brief
完整正式閘門：未嘗試 / 未通過 / 另需分段研究版
系統資料讀取狀態：已讀取 / 部分無法讀取 / 無法讀取
歷史去重狀態：已檢查近期 reports / 未完整
結構閘門狀態：通過 / 未通過
新資訊密度狀態：通過 / 偏低 / 未通過
台灣新聞狀態：通過 / 不足 / 未完整
```

## 1. Six-domain Coverage Matrix

| 核心領域 | 掃描狀態 | 大型訊號數 | 小眾候選數 | 台灣新聞數 | Evidence Trace | New Info Check | 漏抓風險 |
|---|---|---:|---:|---:|---|---|---|
| AI / Agent / 工作流 |  | 3 | 3 | 1–2 | required | required |  |
| 加密 / RWA / Agent payments |  | 3 | 3 | 1–2 | required | required |  |
| 零售 / 消費 / 社群 / 服飾 / 時尚 / 流行 |  | 3 | 3 | 1–2 | required | required |  |
| 全球市場 / 資金流 / 地緣 |  | 3 | 3 | 1–2 | required | required |  |
| 科技發展 / 半導體 / 能源 / 機器人 |  | 3 | 3 | 1–2 | required | required |  |
| 勞動 / 消費壓力 / 台灣 |  | 3 | 3 | 1–2 | required | required |  |

## 2. Per-domain Block

Repeat this block for all six domains.

### [DOMAIN]

**大型訊號（3）**

1. ID：[DOMAIN]-1｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
2. ID：[DOMAIN]-2｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
3. ID：[DOMAIN]-3｜事件：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

**小眾候選（3）**

1. ID：[DOMAIN]-C1｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜具體錨點：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：
2. ID：[DOMAIN]-C2｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜具體錨點：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：
3. ID：[DOMAIN]-C3｜候選訊號：｜候選類型：新領域 / 新應用 / 新概念 / 新趨勢｜形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中｜具體錨點：｜今日新增點：｜來源 / 時間：｜為何小眾 / 早期：｜為何可能放大：｜證據等級：｜是否重複歷史主題：｜不能下的結論：｜下一步驗證：

**台灣新聞（1–2）**

- ID：TW-[DOMAIN]-1｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：
- ID：TW-[DOMAIN]-2｜台灣新聞：｜今日新增點：｜來源 / 時間：｜證據等級：｜是否重複歷史主題：｜不確定點 / 下一步：

## 3. Candidate Quality Gate

```text
小眾候選不是趨勢感想。
每則至少有一個具體錨點：公司 / 產品 / 論文 / 數據 / 融資 / 招聘 / 開源採用 / 鏈上指標 / 社群事件 / pilot / patent / clinical trial / prototype / supply-chain anomaly / 時尚風格微趨勢 / 品牌商品組合變化。
每則必須標示候選類型：新領域 / 新應用 / 新概念 / 新趨勢。
每則必須標示形成程度：弱訊號 / 話題形成 / 趨勢形成 / 主流化中。
主流大型新聞換句話說不得算候選。
空泛句如「監管仍是變數」不得算候選。
候選必須說明：為何早期、為何可能放大、不能下什麼結論、下一步驗證。
```

形成程度判斷：

```text
很多報導、很多討論、詞彙或敘事開始擴散 = 話題形成。
很多品牌、公司、平台、地區開始應用、試點、投資、招聘或數據同步出現 = 趨勢形成。
已廣泛商業化且有明確數據 = 主流化中，應評估是否升級為大型訊號。
```

If fewer than 3 qualified candidates are found in a domain:

```text
run candidate retry / external discovery
check non-English and regional sources
check research / startup / product / niche industry / developer / social-first / hiring / on-chain sources
check fashion / style / brand / assortment sources when relevant
never fabricate
mark remaining candidate gap
mark partial concise brief when completion gate is not met
```

## 4. Technology Development Rule

Technology block must separate:

```text
AI-driven technology breakthrough
standalone non-AI technology breakthrough
```

AI supply chain / AI governance cannot consume Technology quota. Scan at least six non-AI technology subdomains or mark partial.

## 5. Taiwan News Rule

Taiwan news must be local news / official data / company action / market data / industry event. Generic Taiwan implications do not count.

For Taiwan crypto, report fixed-source audit. If DA 交易者聯盟 / 邦妮區塊鏈 / 加密城市 / 區塊勢 were not checked as required, do not claim Taiwan crypto news is absent.

## 6. Retail / Fashion Focus Block

```text
百貨 / 購物中心 / 街邊店：
品牌展店 / 撤店 / tenant mix：
社群商務 / 內容導購：
服飾庫存 / 折扣 / 中價品牌壓力：
時尚 / 流行 / 穿搭風格 / 顏色 / 材質 / 版型 / 品類變化：
台灣零售 / 商圈 / 百貨 / 品牌 / 時尚通路訊號：
```

Each line should reference supporting news IDs where possible.

## 7. New Information / History Duplicate Check

| ID | 今日新增點 | 是否重複歷史主題 | 可否計入 | 原因 |
|---|---|---|---|---|

## 8. Source / Feed Coverage Audit

```text
source_library_checked:
priority_sources_checked:
FreshRSS_checked:
niche_source_types_checked:
formation_level_coverage:
keyword_fallback_used:
official_or_data_crosscheck_used:
Taiwan_sources_checked:
social_channels_checked_when_required:
remaining_source_gap:
```

## 9. Data Gaps and Retry Notes

| 缺口 | 已嘗試 | 下一步 |
|---|---|---|

## 10. Final Indicator Status and News Synthesis Panel

```text
indicator domain:
today status:
direction:
supporting news IDs:
data gaps:
today main themes:
Taiwan news summary:
source-library coverage note:
feed-stack coverage note:
post-brief review:
```

This panel does not count toward 3+3.

## Completion Gate

A concise brief is complete only when all six domains have exactly 3 major signals and exactly 3 qualified niche candidates, plus candidate type / formation level, required Taiwan news or valid insufficiency disclosure, evidence traces, freshness checks, source audits, retry notes, retail / fashion block, final panel and post-brief review.

If not, write `partial concise brief` and disclose the gap.
