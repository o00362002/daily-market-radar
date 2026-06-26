# 漏抓案例與硬檢查清單

本檔用來保存使用者指出過的漏抓事件。每日播報前必須讀取，並將下列案例轉成搜尋硬檢查。

---

## 0. 每日播報記憶瘦身規則

### 單一規格來源

每日市場播報的完整規格，以 GitHub repo 為準：

```text
repo: o00362002/daily-market-radar
```

每日執行前必讀：

```text
SYSTEM_PROMPT.md
configs/
memory/
templates/
reports/
```

### 對話記憶只保留入口，不承載細節

未來不應再依賴對話記憶保存每日播報的完整雷達、搜尋清單、輸出格式與漏抓案例。

對話記憶只需保留：

```text
每日市場播報規格在 GitHub repo：o00362002/daily-market-radar。
執行前要讀：SYSTEM_PROMPT.md、configs/、memory/、templates/、reports/。
```

其餘細節以 repo 文件為準。

### 舊記憶處理原則

若對話記憶、舊規則、舊 prompt 與本 repo 內容衝突：

1. 優先使用 repo 內容。
2. 不要憑記憶補齊已移到 repo 的細節。
3. 若 repo 無相關規則，才使用對話上下文或詢問使用者。
4. 若使用者提出新漏抓事件，優先更新本檔，而不是只記在聊天中。

### 更新入口

之後若使用者說：

```text
幫我更新每日播報規格
```

應先判斷要更新哪個檔案：

- 雷達範圍：`configs/radars.yml`
- 跨領域觸發器：`configs/triggers.yml`
- 證據分級：`configs/evidence.yml`
- 多語言搜尋策略：`configs/source_strategy.md`
- 漏抓案例：`memory/missed_cases.md`
- 長期追蹤：`memory/watchlist.md`
- 報告格式：`templates/daily_report_template.md`
- 執行流程：`workflows/execution_checklist.md`

---

## 硬檢查案例 001：Seedance 2.0 / AI 影片工具 / 中國短劇與影視產業替代

- 狀態：硬檢查中
- 使用者指出時間：2026-06
- 漏抓事件：大陸 Seedance 2.0 或同類 AI 影片工具可能影響短劇、影視製作與相關職能。
- 使用者認為重要原因：這不是單純模型發布，而可能是「技術突破 + 產業流程替代 + 平台/內容產業 + 就業衝擊」的跨領域事件。
- 應屬雷達：
  - AI 工作流替代
  - AI 模型、Agent 與企業應用
  - 勞動與消費結構壓力
  - 零售、消費、社群媒體、流行與服飾（內容平台與社群流量側）
  - 台灣關聯與產業映射（內容產業、個人工具化）
- 可能漏抓原因：
  - 只搜尋英文或主流科技媒體，未掃描簡體中文產業討論。
  - 把模型發布當成一般 AI 新聞，未啟動「工作流替代」觸發器。
  - 沒有查就業、接案、招聘、短劇製作成本與平台政策。
- 每日硬搜尋關鍵字：
  - Seedance 2.0 短剧 影视 失业
  - Seedance 2.0 AI 视频 短剧 产业链
  - AI 视频 影视 后期 裁员 招聘下降
  - AI 生成视频 短剧 成本 降低
  - 即梦 可灵 Seedance 短剧 工作流 替代
  - AI video short drama production jobs China
- 必須檢查：
  - 是否有官方發布或產品能力更新？
  - 是否有短劇平台、MCN、製作公司導入案例？
  - 是否有裁員、減少外包、招聘下降、薪資下降證據？
  - 是否有成本壓縮 50% 以上的可信案例？
  - 是否有平台分發、商業化、廣告、付費閉環？
  - 是否有版權、肖像、勞動、監管反彈？
- 證據標準：
  - 單一社群討論：低證據，列候選訊號。
  - 產業訪談或媒體報導：中證據。
  - 官方資料 + 多來源就業/成本/導入證據：高證據。
- 下次驗證指標：
  - 影視/短劇相關職缺數
  - 後期/剪輯/分鏡/美術/演員相關外包價格
  - 短劇製作週期與成本
  - 平台 AI 內容政策
  - 內容產量變化

---

## 硬檢查案例 002：2026-06-25 每日播報內容偏少與雷達展開不足

- 狀態：硬檢查中
- 使用者指出時間：2026-06-25
- 漏抓事件：2026/06/25 原始播報看起來內容偏少，後續確認不是「今天沒內容」，而是 AI Commerce、加密潛力生態、社群需求上游、RWA 即時數據、台灣本地商圈等雷達沒有完整展開。
- 使用者認為重要原因：每日市場情報不是新聞摘要，而是領域雷達系統。若只抓到幾則顯眼新聞，會錯過早期弱訊號、平台入口變化與結構轉移。
- 應屬雷達：
  - AI 模型、Agent 與企業應用
  - AI 工作流替代
  - 零售、消費、社群媒體、流行與服飾
  - 區塊鏈 / 加密貨幣
  - 全球資金流
  - 台灣關聯與產業映射
- 可能漏抓原因：
  - 直接進入報告生成，未先跑覆蓋矩陣。
  - 只用固定主流來源，未做新來源探索與升降權。
  - 加密只寫 BTC / ETH / SOL、RWA、隱私幣，未掃描完整潛力生態。
  - 零售社群只當附屬段落，未升級為需求上游雷達。
  - AI Commerce 只寫成 AI referral 小訊號，未串成「AI 對話入口 + 商品資料 + marketplace 控制權 + conversion API」。
- 每日硬搜尋關鍵字：
  - ChatGPT ads Amazon product feed conversion API
  - AI referral retail conversion Adobe
  - AI commerce product feed agentic checkout
  - RWA.xyz tokenized stocks stablecoin holders turnover
  - Perp DEX volume RWA perps tokenized equities
  - prediction markets Kalshi Polymarket volume
  - social media drives store visits retail Gen Z
  - AI generated influencer disclosure retail ads EU AI Act
  - 台灣 百貨 商圈 展店 撤櫃 來客
  - Threads Instagram TikTok 小紅書 社群 導購 門市
- 必須檢查：
  - 是否先輸出今日覆蓋矩陣？
  - 是否標示「已掃描」「未完整」「已查無重大更新」「有內容但展開不足」？
  - AI Commerce 是否包含 Ads / Product Feed / Conversion API / AI referral / Marketplace 控制權？
  - 加密是否固定輸出 12 類潛力生態熱力圖？
  - 零售段是否從「消費 → 通路 → 商圈 → 品牌 → 商品 → 門市 → 社群 → 會員」大到小拆解？
  - 每個主領域是否分國際與台灣？
  - 後段是否集中整理生產力便車、AI 泡沫、AI Commerce、加密潛力、社群需求上游、來源探索、Loops 修正等雷達總表？
- 證據標準：
  - 單一社群討論：低證據，列候選訊號。
  - 官方公告 / 原始數據 / 權威媒體：高證據。
  - 產業媒體或研究機構資料：中證據，需標示不確定點。
- 下次驗證指標：
  - AI referral conversion / revenue per visit
  - ChatGPT Ads / Google AI Mode / Agentic checkout 更新
  - RWA AUM / holders / turnover / secondary liquidity
  - Stablecoin supply / payment volume
  - Perp DEX volume / OI / fees
  - 社群到店提及、UGC 真實性、AI 內容揭露規則
  - 台灣百貨 / 商圈 / 街邊店 / 展撤櫃訊號

---

## 硬檢查案例 003：AI Product Quality / ChatGPT 回覆重複使用者問題

- 狀態：候選硬檢查中
- 使用者指出時間：2026-06-25
- 漏抓事件：使用者在多個對話窗、智慧高 / Thinking 模式下遇到 ChatGPT 重複使用者問題而沒有回答；切換即時 / Instant 後較正常，但異常不是每句都發生。
- 使用者認為重要原因：AI 產品品質與 regression 會直接影響 AI 工具可用性、企業導入信任、工作流可靠性，應作為 AI 生態雷達的一部分，而不是只看功能發布。
- 應屬雷達：
  - AI 模型、Agent 與企業應用
  - AI 工作流替代
  - 科技發展過熱指標
  - 台灣企業導入 AI
  - 個人工具化學習
- 可能漏抓原因：
  - 只追官方功能發布，不追產品品質、社群 bug 回報與 rollout regression。
  - 沒有區分 Thinking / Instant、App / Web、長對話 / 新對話、工具開啟 / 工具關閉的差異。
  - 官方 Status 未公告時，未把社群大量回報列為候選訊號。
- 每日硬搜尋關鍵字：
  - ChatGPT repeats user message instead of answering
  - ChatGPT repeating prompt bug Thinking model
  - GPT-5.5 Thinking regression repeated response
  - ChatGPT app regression duplicate responses
  - OpenAI Community repeating itself bug
  - Reddit ChatGPT repeats my question
  - ChatGPT status regression response assembly streaming bug
- 必須檢查：
  - 官方 Status 是否有事件？
  - OpenAI Release Notes 是否有模型 / App rollout？
  - OpenAI Community 是否出現同類 bug 回報？
  - Reddit / X / Hacker News 是否有使用者集中回報？
  - 是否特別集中在 Thinking 模式、特定 App、特定模型或長上下文？
  - 是否影響工具呼叫、搜尋、MCP、記憶、回覆組裝？
- 證據標準：
  - 官方 Status / Release Notes：高證據。
  - OpenAI Community 多案例 + 官方人員回覆：中到高證據。
  - Reddit / X 零星案例：低證據，只能列候選。
- 下次驗證指標：
  - 同類回報數量
  - 模型 / App 版本
  - 是否跨帳號、跨裝置、跨對話
  - 是否可重現
  - 官方是否公告或修復

---

## 使用者回饋新增格式

```text
漏抓事件：___；
我認為重要原因：___；
應屬雷達：___；
你沒有抓到的原因可能是：___；
提高權重：___；
降低權重：___；
新增硬檢查：___；
我想追蹤：___。
```

收到新回饋後，必須把它整理成新的硬檢查案例，並優先更新本檔，而不是只存在對話記憶。