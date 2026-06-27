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

## 硬檢查案例 004：零售全域搜尋模型 / 線上線下整合 / 百貨街邊電商共同構成零售

- 狀態：硬檢查中
- 使用者指出時間：2026-06-26
- 漏抓事件：每日市場情報的零售段落若只新增「百貨／購物中心」或「街邊門市」子段落，仍可能漏掉真正的零售結構變化；使用者希望修正的是搜尋模型本身，從零售整體出發，追蹤線上、線下與兩者整合如何共同構成未來零售。
- 使用者認為重要原因：零售是大領域，百貨、街邊店、電商、社群、會員、LBS、OMO、Retail Media、CDP/CRM、AI 導購、庫存共享、商圈與城市場域彼此高度相關。若只用單一關鍵字或單點段落，會漏掉通路型態、商業模式、資料整合與消費旅程的早期變化。
- 應屬雷達：
  - 零售、消費、社群媒體、流行與服飾
  - 真分眾 vs 假分眾
  - AI 模型、Agent 與企業應用（AI 導購、Personal Shopper、智慧商場）
  - 勞動與消費結構壓力（門市職能、店員服務、實體通路壓力）
  - 台灣關聯與產業映射（台灣百貨、街邊店、商圈、服飾品牌）
- 可能漏抓原因：
  - 只搜尋「零售新聞」「百貨新聞」「服飾品牌」，未用大領域 → 子領域 → 關聯領域 → 具體案例的雷達搜尋。
  - 百貨、街邊店、電商、社群、會員與庫存被分開看，沒有判斷通路分工與整合。
  - 只看品牌新聞，未掃商業地產、租金空置率、Retail Media、LBS、智慧商場、百貨 APP、CDP、OMO、商圈人流與城市更新。
  - 只看線下或線上單點，未追蹤線上內容導流線下體驗、線下體驗回流線上回購、BOPIS、門市出貨、退換貨整合與庫存共享。
- 每日硬搜尋關鍵字：
  - retail transformation omnichannel online offline integration
  - future of retail online offline integration
  - omnichannel retail CDP CRM LBS AI shopping assistant
  - department store future smart mall retail media loyalty app
  - shopping mall innovation foot traffic analytics tenant mix
  - high street retail street-level retail flagship store DTC physical store
  - retail real estate vacancy rent foot traffic shopping street
  - social commerce drives store visits retail
  - BOPIS ship from store return in store apparel retail
  - 台灣 百貨 數位轉型 OMO 會員 APP CDP
  - 台灣 購物中心 智慧商場 人流 LBS
  - 台灣 街邊店 商圈 店租 空置率 展店 撤店
  - 台灣 Retail Media 百貨 會員資料 廣告
  - 台灣 服飾品牌 線上線下整合 門市 官網 LINE
- 必須檢查：
  - 是否先從「零售整體」掃描，而不是只搜百貨、服飾或品牌？
  - 今日線上通路是否有變化：官網、電商平台、社群商務、直播、內容電商、APP、LINE、Retail Media？
  - 今日線下通路是否有變化：百貨、購物中心、街邊店、旗艦店、快閃店、社區店、Outlet、展會 / 市集？
  - 今日整合層是否有變化：OMO、Omni-channel、CDP/CRM、會員資料、LBS、BOPIS、門市出貨、退換貨整合、庫存共享、AI 導購、Personal Shopper？
  - 是否判斷不同通路如何分工、互補、導流、轉換與承接？
  - 是否比較對服飾零售、品牌進櫃、街邊展店、門市營運、庫存補貨、會員經營與商業化機會的影響？
  - 若無重大訊號，是否標示已掃描但無重大變化，而不是省略？
- 證據標準：
  - 官方公告、財報、百貨 / 商場公開資料、租賃數據、APP / CDP / OMO 導入案例：高證據。
  - 產業媒體、研究機構、商業地產報告、百貨主管訪談：中證據。
  - 社群討論、單一品牌觀察、未驗證商圈傳聞：低證據，列候選訊號。
- 下次驗證指標：
  - 百貨 / 商場營收、人流、餐飲占比、租戶組合、空置率、租金
  - 百貨 APP / 會員數 / 活躍率 / 票券使用 / 推播轉換
  - Retail Media 版位、品牌投放、廣告收入、第一方資料應用
  - LBS / 人流分析是否串到活動歸因、樓層轉換、招商或會員分眾
  - 街邊店展店 / 撤店 / 旗艦店 / 快閃店 / 社區型店訊號
  - 線上內容、社群、直播是否導流到實體門市或百貨場域

---

## 硬檢查案例 005：Codex token / credit / gift / promo code / AI 產品用量經濟漏抓

- 狀態：硬檢查中
- 使用者指出時間：2026-06-27
- 漏抓事件：今日新版 GitHub 規格播報未抓到 Codex token / credit / 可贈送或促銷類訊號；舊版長 prompt 對 token 使用量、AI coding agent 成本、AI budget、usage limits 與 OpenAI / Anthropic 競爭促銷較敏感。
- 使用者認為重要原因：這不是單純小功能，而是 AI agent 商業化與使用成本結構訊號。Token / credit / quota / promo / gift / transfer 會影響使用者遷移、工具黏著、企業導入、成本負擔與「AI agent 是否能普及」。
- 目前已驗證搜尋 loop：
  - 官方 OpenAI 網站與 Help Center 搜尋未找到明確「Codex token 可轉贈 / gift transfer」公告。
  - 一般網路搜尋可抓到 Business Insider 2026-06-04 報導 OpenAI Codex 廣告隱藏小遊戲，玩家可取得 free AI tokens / credits，且曾出現 $1,000 tokens、promo codes 用完等訊號。
  - 一般網路搜尋也可抓到 Codex 使用成長、用量成本、Claude Code / Codex 競爭與免費使用促銷相關訊號。
- 應屬雷達：
  - AI 模型、Agent 與企業應用
  - 科技發展過熱指標
  - AI 產品用量經濟
  - AI 工作流替代（若影響開發成本與工具使用）
  - 全球資金流 / AI 投資回報（若涉及補貼與成本不可持續）
  - 台灣關聯與產業映射（個人開發者、企業導入、AI 工具成本）
- 可能漏抓原因：
  - 新版 repo 把 AI 雷達重點放在模型、Agent、企業導入與工作流替代，沒有把「產品用量經濟」獨立成硬檢查。
  - 官方來源優先規則太強，若官方沒有公告，媒體 / 社群的促銷與 promo code 訊號容易被刪掉，而不是列為低到中證據候選。
  - 舊版長 prompt 有 token usage、AI budget cuts、usage limits、cloud CapEx、inference cost 等字眼，新版 repo 雖有科技過熱指標，但沒有把 token / credit / quota / overage / gift / promo 放入固定搜尋關鍵字。
  - Codex token / credits 類事件可能被分類成「促銷活動」而非市場情報，導致權重過低。
- 每日硬搜尋關鍵字：
  - OpenAI Codex token credit promo code
  - OpenAI Codex tokens gift transfer share quota
  - Codex usage limit credits overage pricing
  - ChatGPT Codex token promo Time to Fly
  - AI coding agent token usage cost limits
  - Claude Code limits OpenAI Codex free credits
  - AI agent pricing usage caps credits
  - OpenAI Codex business free usage enterprise promotion
  - OpenAI API credits promo code gift tokens
  - tokenmaxxing Codex Claude Code
  - Codex token 額度 贈送 轉贈
  - Codex 使用限制 token 額度
  - OpenAI Codex 促銷 credits token
  - ChatGPT Codex token 兌換碼
  - Codex token 额度 赠送 转赠
  - OpenAI Codex credits 促销码
  - AI 编程 Agent token 成本 限额
- 必須檢查：
  - 官方 OpenAI / Help Center / Release Notes / Status 是否有 token / credit / usage limit / gift / transfer / promo / pricing 更新？
  - 權威媒體是否報導 Codex credits、promo code、free tokens、enterprise promotion 或 usage limits？
  - Anthropic / Claude Code 是否同步調整 usage limits、pricing、free credits 或 enterprise offer？
  - 是否只是一次性活動，還是代表 AI agent 產品開始用 token / credit 經濟做獲客與留存？
  - 是否影響開發者成本、工具選擇、企業導入與 AI coding agent 普及速度？
  - 若官方未確認，是否仍列為候選訊號並標示「官方未確認」？
- 證據標準：
  - OpenAI 官方公告 / Help Center / Release Notes：高證據。
  - 權威媒體報導 + 可查公開活動頁：中證據。
  - 社群截圖、KOL、單一使用者說法：低證據，只能列候選或資料不足。
  - 官方查無資料但媒體有報導：中低證據，必須標示官方未確認。
- 下次驗證指標：
  - Codex token / credit / usage limit / promo code 官方頁面
  - ChatGPT / Codex pricing 或 plan 頁面
  - Claude Code / Cursor / Copilot usage limit 變化
  - 開發者社群對 token 成本、overage、quota 的討論量
  - AI coding agent 使用量、WAU、企業導入、用量補貼
  - 是否出現可轉贈、gift code、team sharing、quota pooling 或 enterprise credit pool

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
