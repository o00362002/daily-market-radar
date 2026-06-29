# 多語言來源策略

本檔定義每日市場情報系統的搜尋來源策略。重點不是固定來源表，而是「來源類型 + 語言覆蓋 + 交叉驗證 + 漏抓回補」。

## 1. 語言覆蓋

每日最低要求：

- 英文：全球市場、科技、AI、加密、政策、企業公告。
- 繁體中文：台灣市場、台灣產業、零售與本地政策。
- 簡體中文：中國 AI、平台、短劇、電商、消費、就業、供應鏈。

依事件區域補充：

- 日文：日本零售、消費、百貨、科技、半導體設備。
- 韓文：韓國消費、娛樂、AI、半導體、電商。
- 歐洲語系：歐盟監管、能源、品牌、奢侈品、製造業。

### 1.1 台灣繁中來源補強規則

每日涉及台灣市場、台灣產業、台灣零售、台灣企業管理、台灣消費、台灣品牌或台灣本地商業案例時，除一般新聞與官方資料外，必須把下列商業媒體納入搜尋來源候選：

- 商業周刊 / Business Weekly Taiwan
- HBR 哈佛商業評論 / Harvard Business Review 繁體中文版

使用規則：

- 若內容來自商業周刊或 HBR 哈佛商業評論，通常列為 B 級來源，適合用於產業趨勢、企業管理觀點、零售案例、消費洞察、商業模式與台灣本地管理脈絡。
- 若文章引用官方數據、財報、調查或明確受訪者，可提升為中高證據，但仍需標示原始資料來源或受訪口徑。
- 若內容屬評論、專欄、管理觀點或二手整理，不得單獨寫成已證實事實，需標示為觀點 / 產業解讀 / 待驗證推論。
- 台灣零售、百貨、服飾、商圈、品牌經營、AI 導入與管理議題若主流即時新聞不足，需使用這兩類來源做補充掃描，避免台灣本地訊號缺口過大。

## 2. 搜尋順序

每日搜尋必須從大範圍到小範圍：

```text
宏觀總體 → 資金流 → 產業 → 平台政策 → 供應鏈 → 公司/產品 → 產品用量經濟 → 社群/用戶行為 → 小型候選訊號
```

避免一開始只搜熱門新聞，導致早期弱訊號漏掉。

## 3. 來源優先級

### A 級來源：可作為高證據

- 官方公告
- 央行 / 統計局 / 監管機構
- 公司財報、新聞稿、法說會資料
- 交易所、ETF 發行商、基金公告
- 鏈上數據與交易所資料
- 權威媒體與主流財經媒體

### B 級來源：通常為中證據

- 可信產業媒體
- 研究機構與投資機構摘要
- 產業訪談
- 公司高層公開訪談
- 技術社群或開發者公告
- 台灣商業媒體與管理媒體，例如商業周刊、HBR 哈佛商業評論繁體中文版

### C 級來源：通常為低證據

- 社群平台討論
- 單一爆料
- KOL 觀察
- 未附完整來源的截圖或轉述

C 級來源只能作為候選訊號，不可直接寫成結論。

## 4. 每日硬搜尋關鍵字組

### AI 工作流替代

英文：
- AI layoffs workflow replacement
- AI video production jobs replaced
- AI agent enterprise workflow automation
- AI reduces production cost
- AI content platform monetization policy

繁中：
- AI 取代 工作流程
- AI 裁員 職缺 下降
- AI 影片 產業 替代
- AI 企業導入 營運 自動化

簡中：
- AI 替代 工作流
- AI 裁员 招聘下降
- AI 视频 影视 短剧 失业
- AI 生成视频 产业链 变化
- Seedance 2.0 短剧 影视 失业

### AI 產品用量經濟 / Token / Credit / 配額機制

此類訊號必須每天至少做一次弱訊號掃描，避免把 AI 產品商業化、用量限制、token 成本、credit 促銷、gift / transfer / promo code、usage cap、rate limit、overage pricing 誤判成小功能。

英文：
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

繁中：
- Codex token 額度 贈送 轉贈
- Codex 使用限制 token 額度
- OpenAI Codex 促銷 credits token
- ChatGPT Codex token 兌換碼
- AI coding agent 用量 成本 限制
- Claude Code Codex token 額度 比較

簡中：
- Codex token 额度 赠送 转赠
- OpenAI Codex credits 促销码
- Codex 使用限制 token 成本
- AI 编程 Agent token 成本 限额
- Claude Code Codex 额度 免费 使用

必須區分：
- 官方已發布功能：高證據。
- 權威媒體報導促銷 / 活動 / promo code：中證據。
- 社群截圖、KOL 或未驗證說法：低證據，列候選或資料不足。
- 若官方搜尋查無資料，但社群 / 媒體有討論，必須寫「官方未確認，低到中證據」。

### AI 產品品質 / Rollout Regression

英文：
- ChatGPT release notes Codex updates usage limits
- OpenAI status Codex outage latency regression
- ChatGPT app bug repeated answers Thinking model
- OpenAI Community Codex bug usage limit
- Codex security vulnerability token leak

繁中 / 簡中：
- ChatGPT 錯誤 回覆重複
- Codex 異常 token 被盜
- OpenAI Codex bug 使用限制
- ChatGPT Thinking 模式 異常

### 加密潛力市場

英文：
- RWA tokenization latest
- tokenized stocks pre IPO crypto
- AI agents crypto payments x402
- Perp DEX volume fees OI
- stablecoin supply exchange flows
- privacy coins ZK latest

繁中 / 簡中：
- RWA 代幣化 最新
- 代幣化股票 pre IPO
- AI Agent 加密 支付
- 永續 DEX 交易量 費用
- 穩定幣 供應 交易所流入流出
- 隱私幣 ZK 最新

### 零售、消費、社群與服飾

英文：
- retail foot traffic department store mall street retail
- social commerce platform algorithm creator monetization
- fashion retail inventory discount middle class pressure
- AI generated content trust social media

繁中：
- 百貨 商場 來客 撤櫃 展店
- 街邊店 零售 空置率
- 社群 電商 分潤 演算法 變化
- 服飾 零售 折扣 庫存 中價品牌
- 商業周刊 零售 百貨 消費 品牌 經營
- 商業周刊 服飾 零售 消費趨勢
- HBR 哈佛商業評論 零售 AI 企業管理
- HBR 哈佛商業評論 消費者 行為 品牌 經營

簡中：
- 百货 商场 客流 撤柜 开店
- 街边店 零售 空置率
- 小红书 抖音 电商 分佣 流量 政策
- 服装 零售 折扣 库存 中端品牌 压力

### 勞動與消費壓力

英文：
- youth unemployment white collar entry level jobs
- consumer credit delinquency buy now pay later stress
- middle income consumer pressure retail

繁中 / 簡中：
- 青年失業 初階白領 職缺
- 薪資 物價 消費壓力
- 信用卡 循環 分期 消費貸
- 低價零售 中價品牌 壓力
- 商業周刊 消費壓力 薪資 物價
- HBR 哈佛商業評論 人才 管理 AI 工作

## 5. 交叉驗證規則

- 重大訊號至少嘗試找 2 種以上來源類型。
- 若只有社群訊號，降級為低證據。
- 若不同來源互相矛盾，放入資料不足與不確定區。
- 若來源時間過舊但被重新討論，必須分開標示原事件時間與再發酵時間。
- OpenAI / Anthropic / Google / Microsoft 等 AI 產品功能與 pricing 類訊號，必須優先查官方公告、Help Center、Status、Release Notes；若官方未見但媒體或社群有訊號，不得刪除，應列候選並標示官方未確認。
- 台灣商業媒體與管理媒體來源若只提供觀點或案例解讀，需與官方數據、公司公告、主流新聞、財報、產業報告或實地訊號交叉驗證；不得把評論性文章單獨提升為高證據。

## 6. 來源擴充規則

每週至少檢查一次：

- 是否有新平台成為產業訊號來源？
- 是否有舊來源開始失真或農場化？
- 是否有特定語言來源比英文更早出現訊號？
- 是否需要新增硬搜尋關鍵字？
- 是否有新的 AI 產品商業化指標來源，例如 pricing page、usage limit page、promo campaign、enterprise offer、credit / token / coupon / gift code 機制、社群使用量回報？
- 台灣繁中來源是否需要補強新的商業媒體、產業媒體、百貨 / 零售專門來源、政府統計或管理觀點來源？

來源策略必須持續變動，不得固定成死表。
