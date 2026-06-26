# 2026 每日市場情報報告索引

> 本索引整理目前已從對話歸檔到 GitHub 的每日播報內容。

## 2026-06

| 日期 | 檔案 | 報告序號 | 主線 | 回測／架構修正 |
|---|---|---:|---|---|
| 2026-06-02 | `2026-06-02.md` | 本週第 2 份 | AI 撐盤、油價壓力、Anthropic IPO、Gap/AEO 壓力、AI 假網紅信任污染 | DEX/OI/funding、exchange listings、GitHub developer、台灣零售分品類資料不足 |
| 2026-06-03 | `2026-06-03.md` | 本週第 3 份 | AI vs 油價、AI PC、Anthropic IPO、社群真實性 | 後續確認漏抓 Marvell 與加密潛力鏈，修正 AI second layer 與潛力鏈雷達 |
| 2026-06-04 | `2026-06-04.md` | 本週第 4 份 | Marvell / Broadcom / DriveNets、Meta Agent、Hyperliquid、Vogue social search retail | 提高 AI networking、custom silicon、Retail Media、Social Search、Perp DEX、RWA、privacy infra 權重 |
| 2026-06-05 | `2026-06-05.md` | 本週第 5 份 | Broadcom 估值壓力、Hyperliquid 真收入、Google creator search、Macy’s / PVH 分化 | 新增 AI 估值容錯率、Crypto ETF 關閉風險、搜尋型品牌入口 |
| 2026-06-06 | `2026-06-06.md` | 本週第 6 份 | 美國就業與利率、油庫存、Marvell S&P 500、加密潛力市場、Shopee × Meta 分潤架構 | 架構回測修正版：漏抓事件需回推搜尋架構，不是只補單一事件 |

## 重要架構修正摘要

### AI

固定掃 AI second layer：

```text
custom silicon / ASIC
AI networking
optical interconnect
Ethernet AI fabric
data center power
cooling
ODM / server
edge AI / AI PC
```

### 加密

固定拆成兩層：

```text
潛力市場／潛力賽道
+
潛力鏈生態動向
```

潛力市場包括 Perp DEX、RWA、stablecoin payment、privacy infra、tokenized stocks / pre-IPO、AI Crypto、DePIN、restaking、SocialFi / GameFi / meme attention markets。

潛力鏈包括 Hyperliquid、Base、Sui、TON、Monad、Berachain、Aptos、Sei、Movement、MegaETH、Eclipse、Fuel、Celestia、Near、Injective、Avalanche、BNB Chain。

### 零售／社群

固定掃：

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

### 回測方式

回測不是只補特定新聞，而是調整搜尋架構：

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
