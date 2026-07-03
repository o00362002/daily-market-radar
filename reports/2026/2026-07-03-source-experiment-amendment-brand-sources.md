# 2026-07-03 Source Experiment Amendment：Brand Sources

本補充檔修正 2026-07-03 每日市場情報歸檔中的來源缺口：Retail 來源不應只包含零售媒體、百貨、商場與通路，也必須加入品牌來源。

---

## 修正原因

```text
原 2026-07-03 Source Experiment 已包含：
- Retail / Grocery AI 專題搜尋
- 百貨官方公告 / 商場社群 / 品牌 IG

但「品牌」只被放在商場 / 社群補充項，沒有獨立成為 Brand Sources 類別。
這會導致服飾、生活風格、運動戶外、DTC、台灣本地品牌的展店、撤店、聯名、折扣、會員活動、商品節奏被漏抓。
```

---

## 新增固定類別：Brand Sources

Brand Sources 必須成為 Retail 雷達獨立來源類別。

### 必查來源

```text
- 品牌官網 Newsroom / Press / Blog
- 品牌門市列表與新櫃公告
- 品牌 IG / FB / Threads / TikTok / LINE OA
- 品牌會員活動與 CRM 訊息
- 品牌 Email / SMS / App push 訊息，如可取得
- 品牌徵才頁與展店招募訊號
```

### 必抓事件類型

```text
- 展店
- 撤店
- 快閃
- 聯名
- 改裝
- 店型升級
- 新品節奏
- 價格帶變化
- 折扣深度
- 出清活動
- 會員制度調整
- 通路切換：百貨、街邊、電商、快閃、outlet
```

### 初始品牌池

```text
國際 / 快時尚：
- UNIQLO / GU
- ZARA / H&M
- MUJI

運動 / 戶外 / 機能：
- Nike / Adidas / New Balance
- Lululemon
- The North Face / Columbia / Arc'teryx，如有台灣訊號

台灣服飾 / 電商品牌：
- Life8
- Laking
- OB 嚴選
- Poly Lulu
- NET
- lativ

商場 tenant brands：
- 主要百貨進駐品牌
- 近期撤櫃品牌
- 新進駐與快閃品牌
```

---

## 更新後 Retail Source Priority

```text
Retail 雷達下次搜尋順序：

1. Brand Sources
   先查品牌官方與社群，抓第一手展店、撤店、折扣、聯名、會員訊號。

2. Shopping Mall / Department Store
   再查百貨、購物中心、商場公告與活動頁，確認 tenant mix 與檔期。

3. Retail Media
   查 Retail Dive、Retail Brew、Chain Store Age、Shopping Center Business、NRF 等產業媒體。

4. General News / Keyword Fallback
   最後才用泛搜尋補漏。
```

---

## 回寫規則

```text
後續每日報告的 Source Experiment 若涉及 Retail，必須至少檢查以下三類之一，若未檢查須標示缺口：

- Brand Sources
- Shopping Mall / Department Store
- Retail Media

若 Retail 段沒有品牌來源檢查，必須在 Data Gaps 明確寫：
「Brand Sources 未檢查，服飾 / 生活風格 / 運動戶外品牌訊號可能漏抓。」
```
