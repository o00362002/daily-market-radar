# 2026-07-25｜Retail Action Layer 競品聚焦與顯示修正

## 變更目的

將競品情報從「台灣產品／全球平台／社群」的地理與公司規模混合分類，收斂為以零售營運執行關係為中心的分類，並納入 2026-07-25 聚焦研究確認的直接與相鄰廠商。

本次產品焦點：

```text
POS／ERP／SOP／訊息／照片／現場事件
→ 營運訊號或自然交代
→ 優先 Action
→ 指派、催辦、證據與覆核
→ Outcome
→ 規則、流程或最佳做法改善
```

## 問題確認

1. 舊 registry 將 SHOPLINE、91APP 等台灣平台與 Microsoft、Google Cloud、AWS、Adobe 等通用平台用地理群組分類，沒有區分直接競品、相鄰產品與基礎設施威脅。
2. 舊前端以 `headline + today_delta + taiwan_implication + uncertainties + primary_domain` 做品牌 substring matching。海外新聞只要在「台灣關聯」提到台灣平台，就可能被錯分為台灣競品。
3. `ACT` 等短別名使用任意 substring matching，可能命中一般英文單字。
4. competitors 頁只呈現「台灣產品／全球平台／社群」，因此與 RetailOps 產品關係很低的海外平台新聞也會和直接競品並列。
5. 現行 RadarReportV2 尚無 typed competitor audit。registry 與 query policy 已存在，但固定官方渠道查核結果尚未寫入報告契約，不能把沒有投影事件解讀成「已查無重大更新」。

## 新分類

1. `global_direct_retail_action_systems`
   - STOREE
   - Quorso
   - WorkJam
   - Hubler
2. `global_adjacent_execution_platforms`
   - YOOBIC
   - Zipline Retail
   - Retail Coach
   - Pipefy Retail
3. `taiwan_adjacent_retail_platforms`
   - CATCH / Claireye、FLAPS、91APP、SHOPLINE、CYBERBIZ、WACA、ACT、Omnichat、Tangent Plus、RSL
4. `global_enabling_platform_threats`
   - Microsoft Copilot Studio / Dynamics 365
   - Workato Enterprise MCP
   - Shopify Retail
5. `social_and_content`

Google Cloud、AWS、Adobe、SAP、Oracle、ServiceNow、Salesforce 的一般公司或平台新聞不再是固定 RetailOps 競品投影。未來只有出現明確零售營運 Action、前線執行或可量化替代能力時，才重新納入。

## 匹配與顯示修正

- 競品身分只從 `headline` 與 `today_delta` 等事實欄位辨識。
- `taiwan_implication`、`uncertainties`、`next_watch` 與 domain label 不再作為身分證據。
- 英文別名採 token boundary，避免短字串誤判。
- 容易混淆或產品範圍過廣的品牌加入 `requires_any` 營運語境門檻。
- 一則事件只指定一個 primary competitor group，優先採標題直接命中的最高關聯群組。
- competitors 頁依直接、相鄰、台灣在地、基礎設施與內容分層顯示。
- 沒有 typed audit 時，狀態改為「固定來源待查」，不再用模糊文案暗示已完成查核。

## 查詢配方修正

固定查詢改為分層執行：

- STOREE / Quorso
- WorkJam / Hubler
- YOOBIC / Zipline
- Retail Coach / Pipefy Retail
- 台灣平台 + 門市營運／補貨／庫存／SOP／任務／巡檢／工作流／AI Agent
- Copilot Studio / Dynamics / Workato / Shopify Retail + 零售營運執行情境

一般 CRM、行銷、電商促銷、雲端模型與消費者購物助手新聞，若沒有營運 Action 關聯，不進競品區。

## 研究與官方驗證基礎

本次以 `Retail Action Layer 聚焦競爭研究` 為研究證據，並重新核對下列官方產品頁：

- STOREE Retail Operations Platform
- Quorso Intelligent Management / Product
- WorkJam AI & Workflows / Task Connect
- Hubler Retail / Retail Operations Suite
- YOOBIC AI-powered frontline performance
- Zipline Retail Platform / AI at Zipline
- Retail Coach
- Pipefy Retail with AI
- Microsoft Copilot Studio MCP / multi-agent
- Workato Enterprise MCP

功能、ROI、導入時間與客戶數仍以廠商公開宣稱為主，未視為獨立審計結果。

## 驗證

- competitor registry JSON parse：通過
- registry unit tests：6/6 通過
- TypeScript strict compile：通過
- matching regression cases：通過
  - WorkJam 海外新聞即使 `taiwan_implication` 提到 91APP，仍歸海外直接競品
  - 91APP 一般 CRM 行銷更新不進競品投影
  - 91APP 門市工作流更新歸台灣相鄰平台
  - Zipline 無零售語境不匹配；Zipline Retail + store audit 才匹配
  - 一般 `impact` 不會誤中 ACT

## 邊界

本次沒有修改 RadarReportV2、Runtime、六責任域、資料庫或 durable competitor history。

仍未完成：

- typed `competitor_audit`
- 每個競品官方渠道的可執行 web / API / social adapter
- durable competitor history 與跨日差異表
- 自動生成「已查無重大更新」的可信 fixed-check pipeline

因此目前完成的是：聚焦 registry、查詢配方、匹配邏輯、網頁分類與誠實狀態顯示。不是宣稱已完成所有競品的每日官方渠道自動查核。
