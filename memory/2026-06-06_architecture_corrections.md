# 2026-06-06 搜尋架構回測修正

> 來源：2026-06-06 對話回測。此檔不是單一漏抓事件清單，而是把漏抓事件回推成搜尋架構調整。

## 核心原則

使用者修正：

```text
回測要調整的是搜尋架構，不是特定主題。
```

每日市場情報回測不得只做「事件補丁包」。正確流程：

```text
漏抓事件
↓
反推是哪一層搜尋架構沒掃到
↓
修正雷達分類
↓
補關鍵字群
↓
補資料來源類型
↓
列入下次固定檢查
```

---

## 1. 加密貨幣：潛力市場與潛力鏈必須拆兩層

### 架構問題

2026-06-06 原報告雖有 Hyperliquid，但缺少完整的「加密貨幣潛力市場／潛力賽道」總覽，且潛力鏈生態不完整。這不是漏掉某一條鏈，而是搜尋層級設計不完整。

### 固定結構

```text
2. 區塊鏈／加密貨幣／虛擬貨幣
├─ 市場基準：BTC / ETH / SOL / Total Market Cap / BTC Dominance
├─ ETF / Fund Flow / Institutional Flow
├─ Stablecoin / Exchange Flow / On-chain Capital
├─ 加密貨幣潛力市場／潛力賽道
│  ├─ Perp DEX
│  ├─ RWA / Tokenized Treasury
│  ├─ Stablecoin Payment / Tokenized Deposits
│  ├─ Privacy Infra / ZK Privacy
│  ├─ Tokenized Stocks / Pre-IPO
│  ├─ AI Crypto
│  ├─ DePIN
│  ├─ Restaking
│  └─ SocialFi / GameFi / Meme Attention Markets
├─ 潛力鏈生態動向
│  ├─ Hyperliquid
│  ├─ Base
│  ├─ Sui
│  ├─ TON
│  ├─ Monad
│  ├─ Berachain
│  ├─ Aptos / Sei / Movement / MegaETH / Eclipse
│  ├─ Near / Injective / Avalanche / BNB Chain
│  └─ 其他異常成長鏈
├─ Privacy Coins / ZK Privacy 深挖
├─ Security / Hacks / Regulation
└─ 噪音 vs 訊號
```

### 必須檢查的資料類型

- TVL
- DEX Volume
- Perp Volume
- Stablecoin Supply
- DAU / 活躍地址
- 交易數
- Protocol fees / revenue
- 開發者 / GitHub
- 生態基金與融資
- 空投 / 積分
- 主網 / 測試網
- 重點 DApp
- 交易所上架
- RWA / DeFi / GameFi / SocialFi / AI Crypto
- Token Unlock
- 治理
- 資安事件
- 交易所公告
- 資金流

### 判斷標準

每日必須區分：

```text
真生態成長
vs
空投刷量／短期炒作
```

---

## 2. 零售／社群：Shopee × Meta 不是單一事件，是 Social Affiliate Commerce 架構

### 架構問題

台灣 Shopee × Meta 分潤不應只記成特定事件。它代表零售／社群搜尋架構缺少：平台電商 × 社群平台 × 分潤／聯盟行銷 × 內容導購 × 歸因資料 × 品牌資料風險。

### 固定結構

```text
8. 零售、消費趨勢、社群媒體、流行與服飾發展
├─ 線下零售／百貨／街邊
├─ 電商平台／Marketplace
├─ Social Commerce / Live Commerce
├─ Affiliate Commerce / KOC 分潤
├─ Retail Media / In-store Media
├─ Social Search / AI Search Shopping
├─ 會員／CRM／OMO
├─ 品類／價格帶／消費分化
└─ 台灣在地平台與品牌影響
```

### 搜尋架構

```text
平台電商
×
社群平台
×
Affiliate / KOC 分潤
×
內容導購
×
歸因資料
×
品牌資料風險
×
台灣在地平台影響
```

### 關鍵字群

- affiliate commerce
- creator affiliate
- social commerce Taiwan
- Shopee affiliate Meta
- Facebook affiliate partnership
- Instagram shopping link
- KOC 分潤
- 聯盟行銷 分潤 電商
- 平台歸因 7日購買窗
- content-to-commerce
- retail media Taiwan
- momo 分潤
- LINE 購物 分潤
- TikTok Shop Taiwan creator affiliate
- YouTube Shorts shopping affiliate
- 小紅書 跨境導購

### 資料源類型

- 平台官方說明
- 賣家中心
- 創作者工具公告
- 社群平台更新
- 電商產業媒體
- 台灣品牌案例
- 廣告產品文件
- 追蹤歸因規則

### 品牌判斷問題

1. 這是導購工具，還是品牌資產？
2. 這是 KOC 真推薦，還是分潤垃圾流量？
3. 這會強化真分眾，還是製造假分眾？

### 必須追蹤指標

- 留言品質
- 收藏率
- 點擊率
- 成交率
- 退貨率
- 回購率
- 會員回流率
- 平台歸因窗
- 分潤成本
- 官網 / LINE / 門市回流

---

## 3. AI：Marvell 不是單一補抓，是 AI Second Layer Infrastructure

### 架構問題

Marvell 漏抓代表 AI 搜尋不能只掃 Nvidia、AMD、Intel、OpenAI、Anthropic、Microsoft。需要固定掃 AI 基礎設施第二層。

### 固定結構

```text
AI Compute
├─ GPU：Nvidia、AMD
├─ ASIC / Custom Silicon：Broadcom、Marvell、Google TPU、Amazon Trainium
├─ Networking：Marvell、Broadcom、Arista、Cisco
├─ Optical / Interconnect：Marvell、Coherent、Lumentum、Credo
├─ Ethernet / AI Fabric：Ultra Ethernet、NVLink Fusion、InfiniBand 替代
├─ Data Center Power：台達電、Vertiv、Schneider
├─ Cooling：液冷、散熱模組、台灣散熱鏈
├─ ODM / Server：鴻海、廣達、緯創、緯穎、英業達
└─ Edge / AI PC：Nvidia、AMD、Intel、Microsoft ecosystem
```

### 必須檢查的事件類型

- 股價異常
- 財報與財測
- 訂單與 backlog
- CEO 評論
- 產品發表
- 供應鏈變化
- index inclusion
- 資本支出與 data center financing
- 台灣供應鏈映射

---

## 4. 回測面板新版格式

每日推播後，回測面板應包含：

| 欄位 | 說明 |
|---|---|
| 漏抓事件 | 使用者指出或模型自檢發現的事件 |
| 對應大領域 | 全球市場 / AI / 加密 / 零售 / 勞動 / 台灣等 |
| 漏掉的搜尋層 | 例如 Social Commerce → Affiliate Commerce → Platform Attribution |
| 不應只補什麼 | 避免變成單一公司、單一事件、單一幣種補丁 |
| 應修正的搜尋架構 | 大領域 → 子領域 → 機制 → 平台／公司／資產 → 指標驗證 |
| 新增關鍵字群 | 中文、英文、區域語言與上層結構詞 |
| 新增資料源類型 | 官方、資料庫、產業媒體、研究報告、平台公告、社群趨勢等 |
| 下次固定檢查 | 明確寫入下一次報告前的硬檢查項目 |

---

## 5. 下次硬檢查

下次每日播報前必須確認：

```text
1. 加密段落是否有「潛力市場／潛力賽道」？
2. 加密段落是否有「潛力鏈生態動向」？
3. 零售段落是否掃平台電商？
4. 零售段落是否掃社群平台？
5. 零售段落是否掃分潤／聯盟行銷？
6. 零售段落是否掃 KOC / creator monetization？
7. 零售段落是否掃內容導購漏斗？
8. 零售段落是否掃歸因資料？
9. 零售段落是否掃品牌資料風險？
10. 零售段落是否掃台灣在地平台？
11. AI 段落是否掃 second layer infrastructure？
12. 回測是否以搜尋架構修正呈現，而不是只補單一主題？
```
