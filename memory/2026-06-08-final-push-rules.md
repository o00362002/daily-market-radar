# 每日市場情報推播最終規則整合

整理日期：2026-06-08  
來源：本次對話中對每日市場情報推播規則的合併修正。

---

## 1. 核心定位

每日推播不是新聞摘要，而是：

```text
趨勢雷達＋早期訊號＋指標驗證＋實務可用＋後續回測
```

固定追蹤模型：

```text
大方向
→ 上層結構
→ 子類別
→ 具體事件／公司／資產／品牌
→ 指標驗證
→ 趨勢判斷
→ 可學可用
→ 後續回測
```

重點不是堆新聞、堆公司、堆幣種、堆固定名單，而是從最重要的大方向一路追到小細節，並持續追蹤每個訊號的成果、失效條件與回測結果。

---

## 2. 固定開頭格式

```text
報告日期時間：YYYY/MM/DD（星期X）HH:mm（台灣時間）
追蹤週期：本週 YYYY/MM/DD－YYYY/MM/DD
報告序號：本週第 X 份
```

週期固定用週一到週日。

---

## 3. 固定段落

```text
0. 今日總覽
1. 全球市場與國際局勢
2. 區塊鏈／加密貨幣
3. 全球資金流補洞
4. 上次討論指標目前狀況
5. 最關鍵觀察指標
6. AI 與實際應用案例
7. AI 泡沫指標
8. 零售、消費、社群媒體、品牌／商圈型態、時尚與服飾流行趨勢
9. 真分眾 vs 假分眾
10. 勞動與消費結構壓力
11. 證據型綜合分析
12. 整合未來趨勢預測
13. 實務建議
14. 推播後回測與調整面板
```

---

## 4. 全域搜尋原則

先掃上層結構，再鑽到具體事件：

```text
市場結構
資金桶
產業鏈
政策
平台生態
消費行為
通路型態
鏈生態
→ 公司／產品／幣種／品牌／事件
```

避免把子產品或單一名詞當入口，導致上層結構漏抓。

---

## 5. 無新資訊也要顯示

固定雷達項目不可因無新新聞而消失。需明確標示：

```text
無新資訊
本次未見重大更新
資料缺口
待補驗證
```

目的：讓使用者能判斷是真的沒有新訊號、資料源不足，還是搜尋架構漏抓。

---

## 6. 全球市場雷達

不能只看美股指數或單一事件。固定掃：

```text
利率
美元
能源
地緣
信用
流動性
區域輪動
產業鏈傳導
```

---

## 7. 加密／區塊鏈雷達

固定掃：

```text
BTC／ETH／SOL baseline
ETF／fund flow
stablecoin
exchange flow
DeFi
RWA／tokenized treasury
L1／L2
Solana ecosystem
AI Crypto
restaking
Perp DEX
DePIN
gaming／social
meme／attention market
tokenized stock／pre-IPO
privacy coins／privacy infra
ZK privacy
security／hacks
token unlock
OI／funding／liquidation
developer activity
regulation
```

### 7.1 潛力賽道 vs 潛力鏈生態

加密段需分成：

```text
潛力賽道
潛力鏈生態發展
```

固定掃鏈生態：

```text
Monad
Sui
TON
Aptos
Sei
Berachain
Base
Hyperliquid
Eclipse
MegaETH
Movement
Fuel
Celestia
Near
Injective
Avalanche
BNB Chain
```

每條鏈看：

```text
TVL
DEX／Perp volume
stablecoin supply
fees／revenue
DAU
active address
developer／GitHub
生態基金
融資
空投／積分
主網／測試網
DApp
交易所
機構合作
token unlock
治理
資安
資金流
```

判斷：真生態成長需資金、用戶、收入、開發者、DApp 同步，而不是只有空投刷量。

### 7.2 BTC Treasury Companies／Corporate BTC Flow

固定新增上層雷達：

```text
BTC Treasury Companies／Corporate BTC Flow
```

固定掃：

```text
Strategy／MicroStrategy／MSTR／Michael Saylor
Metaplanet
Semler
其他企業 BTC treasury 公司
企業買賣 BTC
mNAV
可轉債
優先股
現金儲備
股息壓力
是否影響 BTC 資金流
```

### 7.3 STRC／Digital Credit 權重

STRC／Digital Credit／BTC-backed yield 僅作 Bitcoin treasury finance 背景消息，不作為固定高權重主雷達。

只有出現下列條件才升權重：

```text
明顯改變 BTC 資金流
引發系統性信用風險
帶動大規模 RWA／tokenized credit 採用
造成 MSTR／BTC treasury 公司連鎖壓力
被主要監管／大型平台／大型機構正式納入
```

---

## 8. AI 雷達

AI 段固定分兩層：

```text
AI 產業供應鏈新聞
AI 應用落地新聞
```

### 8.1 AI 產業層

固定追：

```text
模型
算力
GPU／ASIC
雲端
資料中心
電力
散熱
CapEx
推理成本
企業財報
台灣供應鏈
```

### 8.2 AI 應用層／AI Agent

固定掃：

```text
AI agent
agentic workflow
browser／computer use agent
coding agent
客服／銷售 agent
BI／資料分析 agent
營運自動化 agent
零售／電商 agent
社群內容 agent
個人助理
企業 SaaS agent
vertical AI agent
agent marketplace
MCP／tool use
RPA＋LLM
自動化工作流
企業導入
失敗案例
ROI
資安與權限治理
```

每個 AI 應用需回答：

```text
解決什麼流程？
是否商用？
使用者是誰？
是否降本或提高轉換？
需要什麼條件？
風險是什麼？
能不能變成可學／可測工作流？
```

### 8.3 AI 泡沫＋生產力便車

AI 泡沫段除了估值與 CapEx，還要看：

```text
AI 應用泡沫
生產力便車／紅利分配
```

固定追：

```text
OpenAI／Anthropic 收入與成長
毛利／推理成本
企業 AI ROI
AI 預算削減
cloud CapEx
GPU 租賃
Nvidia backlog
資料中心債券利差
private credit
私募估值 markdown
裁員／招募
```

生產力紅利分配需判斷 AI 生產力是擴散到大眾、中小企業、勞工、消費者，還是集中在 GPU、雲端、平台、大企業與資本端。

---

## 9. 零售、社群、品牌、商圈、時尚雷達

第 8 段需固定掃：

```text
消費與價格帶
品牌型態
通路型態
商圈型態
社群商務
時尚與服飾流行趨勢
商品企劃訊號
```

### 9.1 消費與價格帶

```text
高端
中價
低價
折扣
必需／非必需
消費分層
```

### 9.2 品牌型態

```text
品牌重定位
DTC
展店／撤店
聯名
生活風格化
品牌社群
```

### 9.3 通路與商圈型態

```text
百貨
街邊
outlet
快閃
showroom
生活型商場
複合型商場
黃金幹道
巷弄
社區型
觀光型
重劃區
租金／空置率
客流
```

### 9.4 社群商務

```text
Threads
IG
TikTok
YouTube Shorts
小紅書
Facebook
live commerce
social commerce
creator economy
KOL／KOC
UGC
community commerce
social search
社群聆聽
AI 內容飽和
信任
內容到交易漏斗
social CRM
會員社群
offline-to-online conversion
```

### 9.5 時尚與服飾流行趨勢

```text
顏色
版型
材質
品類
穿搭風格
生活場景
明星／KOL／影視訊號
社群平台穿搭訊號
```

### 9.6 商品企劃訊號

```text
搜尋
收藏
試穿
銷售
退貨
缺貨
門市回饋
```

零售段最後需連回商品企劃、補貨、陳列、門市體驗、會員經營、社群內容與 BI／營運系統。

---

## 10. 真分眾 vs 假分眾

固定比較：

```text
客群
商品
供應鏈
社群
門市
退貨／評價
競爭力
```

驗證依據：

```text
社群互動品質
UGC 真實性
community trust
social conversion
退貨率
會員回流
門市回饋
```

---

## 11. 勞動與消費結構壓力

固定掃：

```text
青年就業
初階職缺
外包低技能收入
工資中位數 vs 生產力
信用卡循環／分期
低價零售占比
中價品牌營收
大企業利潤率 vs 薪資占比
AI 對初階白領／內容／客服／行政工作的替代
台灣內需壓力
```

---

## 12. 第 14 段回測面板

固定包含：

```text
今日情報品質評分
今日漏抓風險
昨日／上次訊號回測
訊號驗證狀態
結構性漏抓檢查
今日可調整欄位
建議新增／降低權重的雷達類別
下一步驗證指標
使用者回饋格式
```

訊號驗證狀態：

```text
驗證
部分驗證
失效
待觀察
```

結構性漏抓檢查：

```text
漏抓事件
原本錯誤入口
應補上層雷達
未來固定輸出方式
升權重條件
下一步驗證指標
雷達升降權
```

使用者回饋格式：

```text
提高權重：___；
降低權重：___；
新增雷達：___；
漏抓事件：___；
無新資訊但我懷疑有漏：___；
品牌／商圈要補：___；
我想學/試：___
```

---

## 13. 最終判斷原則

```text
單一產品不是雷達入口。
單一公司不是雷達入口。
單一新聞不是雷達入口。

它們只能是上層結構雷達底下的證據。
```

```text
有新名詞 ≠ 有新主線
有金融包裝 ≠ 有結構性影響
有討論熱度 ≠ 必須升為固定高權重
```

真正升權重的條件：

```text
它開始改變資金流
改變消費行為
改變平台生態
改變產業鏈
改變政策方向
改變企業採用
改變通路型態
或被指標持續驗證
```
