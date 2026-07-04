# Source Experiment Memory

本檔記錄每日市場情報推播後的來源實驗、來源保留 / 淘汰判斷，以及未來 Source Library 的累積方向。

---

## 2026-07-03 Update

### 新增固定流程

每日推播完成後，必須固定執行 `Source Experiment`：

```text
1. 至少測試 3 種以上不同來源。
2. 有效來源要儲存並保留。
3. 無效來源要記錄原因，避免每天重複踩雷。
4. 每個來源需標示適合主題、更新速度、是否第一手、是否容易重複 Reuters、RSS / API 是否可用、是否加入固定媒體庫。
5. Source Experiment 必須放在每日報告最後，接在推播後回測與模型調整面板之後。
6. Retail 類來源必須拆分為 Retail Media、Shopping Mall / Department Store、Brand Sources 三類，不能只看通路與媒體。
```

### 每日輸出格式

```text
Source Experiment

今日新增測試：

✓ Source A
用途：...
判斷：有效，保留。
原因：...

✓ Source B
用途：...
判斷：有效，保留。
原因：...

✗ Source C
用途：...
判斷：移除 / 降權。
原因：...
```

### 評分欄位

| 欄位 | 說明 |
|---|---|
| source | 來源名稱 |
| domains | 適合主題，例如 AI、Retail、Brand、Crypto、Taiwan、Geopolitics |
| freshness | 更新速度 |
| primary_source | 是否第一手來源 |
| reuters_overlap | 是否常常只是重複 Reuters |
| rss_or_api | 是否有 RSS / API / 結構化資料 |
| keep_status | 保留 / 降權 / 淘汰 |
| notes | 使用注意事項 |

---

## 2026-07-03 Experiment Results

| Source / Method | Domains | Freshness | Primary Source | Reuters Overlap | RSS/API | Keep Status | Notes |
|---|---|---|---|---|---|---|---|
| Reuters / FT / Guardian 組合 | AI、Markets、Policy、Crypto | 快 | 部分 | 中 | 部分 | 保留 | 可抓政策、公司動作與資金流新訊號，但不能讓 Reuters 重複填滿整份報告。 |
| Retail / Grocery AI 專題搜尋 | Retail、AI shopping assistant | 中快 | 否 | 低 | 未確認 | 保留 | 今日抓到 Pick n Pay「Penny」，證明零售 AI 應用不只發生在美國。 |
| 台灣產業關鍵字搜尋：AI 供應鏈 / PCB / IC 載板 / 百貨超市 | Taiwan、Semiconductor、Retail | 中 | 否 | 中 | 未確認 | 保留但需改進 | 可抓到 Unimicron 與 LOPIA，但台灣零售、勞動、加密仍不足。 |
| Brand official channels / 品牌官方來源 | Brand、Fashion、Retail、Consumer | 中快 | 是 | 低 | 部分 | 新增保留 | 必須追蹤品牌官網 Newsroom、門市公告、IG / FB / Threads / LINE 官方帳號、會員活動、聯名、價格、折扣、展店與撤店。 |
| 泛零售舊新聞搜尋 | Retail | 慢 | 否 | 高 | 未確認 | 降權 | 容易抓到舊 AI shopping 或電子價牌背景，不可計入今日大型訊號。 |
| 台灣影響推論式補位 | Taiwan mapping | 不適用 | 否 | 不適用 | 不適用 | 淘汰 | 不得用「台灣可能受影響」替代台灣新聞。 |

---

## 2026-07-04 Source Addition Archive

### Taiwan Crypto Sources

使用者指定新增台灣加密貨幣資訊來源。已歸入 `configs/source_routing_rules.yml` 的 `mandatory_source_overlays.taiwan_crypto_sources`。

| Source | Domains | Evidence Default | Keep Status | Notes |
|---|---|---|---|---|
| DA 交易者聯盟 | Taiwan crypto、trader sentiment、market narrative | medium_low | 保留 | 適合追交易者敘事與台灣社群熱點；重大 claim 必須回查官方、鏈上數據、交易所或公司公告。 |
| 邦妮區塊鏈 | Taiwan crypto education、market events、exchange discussion | medium_low | 保留 | 適合補台灣大眾加密教育與社群關注議題；不可單獨作政策或市場事實結論。 |
| 加密城市 | Taiwan crypto news、regulation、exchanges、projects | medium | 保留 | 適合台灣 crypto 日常新聞掃描；政策、交易所與項目事件需交叉驗證。 |
| 區塊勢 | Web3 trends、policy context、business models | medium | 保留 | 適合深度分析與結構判讀；若為觀點需標示，不替代官方事實。 |

固定規則：若每日報告標示「台灣加密新聞不足」，必須說明是否已檢查上述四個來源。未檢查時需明確寫：`Taiwan crypto fixed sources not checked.`

### Taiwan Brand / Management Sources

使用者指定台灣品牌來源加入商業周刊與 HBR 哈佛商業評論。兩者原本已在 Retail Taiwan media 中，但本次進一步歸入 `configs/source_routing_rules.yml` 的 `mandatory_source_overlays.taiwan_brand_management_sources`，避免只被當成一般零售媒體。

| Source | Domains | Evidence Default | Keep Status | Notes |
|---|---|---|---|---|
| 商業周刊 / Business Weekly Taiwan | brand strategy、retail cases、consumer trends、Taiwan business context | medium | 保留 | 適合品牌經營、零售案例、消費趨勢與台灣商業脈絡。評論或案例不可直接當成已證實事實。 |
| HBR 哈佛商業評論繁體中文版 | brand management、retail strategy、AI adoption、consumer behavior、management framework | medium | 保留 | 適合管理框架、品牌策略、零售 AI 導入與消費者行為；需有原始資料才可提升證據等級。 |

固定規則：若 Retail / Brand Sources 標示不足，必須說明是否已檢查商業周刊與 HBR 哈佛商業評論。未檢查時需標示缺口。

---

## 2026-07-04 Missed Case Archive：Taiwan Crypto Legislative Trigger

### 漏抓事件

使用者指出：`虛擬資產服務法` 已三讀通過，但每日報告未抓到。

### 為什麼沒搜到

```text
1. 搜尋路由錯誤：
   系統把台灣加密優先路由到 crypto media / community sources，
   例如加密城市、ABMedia、DA 交易者聯盟、邦妮區塊鏈、區塊勢，
   但沒有先跑立法院 / 金管會 / 行政院 / 法規資料庫。

2. 關鍵字錯誤：
   原本偏向 crypto、VASP、穩定幣、金管會、虛擬資產等字，
   但沒有把「虛擬資產服務法」「三讀」「立法院議案系統」「專法」設成硬搜尋。

3. 證據閘門錯誤：
   台灣加密媒體未命中時，系統直接傾向標示台灣新聞不足，
   沒有觸發 legislative retry。

4. 來源層級錯誤：
   法案三讀屬政策 / 法規 / 立法事件，
   不應只依賴加密媒體或泛搜尋。
```

### 已更新規則

已在 `configs/source_routing_rules.yml` 新增：

```text
mandatory_source_overlays.taiwan_crypto_legislative_trigger
```

### 新規則摘要

```text
若任一條件成立：
- crypto 段需要台灣新聞
- 台灣加密新聞不足
- 出現 VASP / 虛擬資產 / 穩定幣 / 交易所監管 / 幣商 / AML / 第三方支付
- 出現法案、專法、三讀、立法院、議案系統等關鍵字

必須先查：
- 立法院
- 立法院議案系統
- 金管會
- 行政院
- 總統府
- 全國法規資料庫
- 中央社政治 / 財經

再查：
- DA 交易者聯盟
- 邦妮區塊鏈
- 加密城市
- 區塊勢
```

### 報告分類規則

```text
台灣加密法案三讀通過 = Major Signal
不可列為 candidate
不可被 Robinhood / tokenized stocks / 社群敘事取代

必須區分：
- third_reading_passed：三讀通過
- presidential_promulgation：總統公布
- effective_date：施行日期
- sublaw_stage：授權子法 / 監管細則
```

### 下次 Coverage Audit 必填

```text
Taiwan crypto legislative trigger checked: yes / partial / no
Checked official sources: 立法院 / 議案系統 / 金管會 / 行政院 / 總統府 / 全國法規資料庫 / 中央社
If no: Taiwan crypto legislative trigger not checked.
```

---

## 2026-07-04 Missed Case Archive：DA 交易者聯盟 IG Social Channel

### 漏抓事件

使用者指出：DA 交易者聯盟的 Instagram 有報導 `虛擬資產服務法` 三讀通過，但每日報告與後續補查沒有抓到。

### 為什麼沒抓到

```text
1. 來源被抽象化：
   DA 交易者聯盟只被記成「台灣加密來源」，沒有拆成具體 channel：IG / FB / Threads / YouTube / 官網 / Linktree。

2. 泛搜尋限制：
   Instagram 內容常常不會被一般搜尋引擎完整索引，尤其是貼文文字、限動、輪播圖文字與圖片內文字。
   所以「搜尋 DA 交易者聯盟 + 虛擬資產服務法」不等於「已檢查 DA IG」。

3. 社群來源閘門缺失：
   系統沒有要求 social-first source 必須做 direct channel check，導致 IG 有貼文但被視為查無。

4. 證據分級誤用：
   DA IG 對於「發現新聞」有價值，但若是法案三讀，最終證據仍必須回查立法院、金管會、中央社或法規資料庫。
```

### 已更新規則

已在 `configs/source_routing_rules.yml` 新增與修正：

```text
fetch_priority:
  - official_social_channel_or_public_post

coverage_audit_fields:
  - social_channels_checked_when_required

mandatory_source_overlays.taiwan_crypto_social_channel_trigger
```

DA 交易者聯盟新增：

```text
channel_priority: [instagram, facebook_or_threads_if_available, website_or_linktree_if_available, generic_search_fallback]
social_check_required: true
```

### 新規則摘要

```text
若來源是 social-first，或使用者指定 IG / FB / Threads / LINE / YouTube：

不能只用 generic web search 代表已檢查。
必須：
1. 直接檢查官方社群帳號；或
2. 使用貼文 URL / 截圖 / 文字轉錄；或
3. 明確標示 social channel inaccessible / unchecked。
```

### 下次 Coverage Audit 必填

```text
social_channels_checked_when_required: yes / partial / no / not_required
DA 交易者聯盟 IG checked: yes / partial / no
If no: Social source not checked directly; generic search may miss Instagram/Facebook/Threads/LINE posts.
```

---

## 2026-07-04 Generalization Archive：Channel-aware Source Checks

### 使用者確認

使用者確認：除了 DA 交易者聯盟外，其他類似來源也要用同樣方式處理。

### 已更新規格

已在 `SOURCE_LIBRARY_SPEC.md` 將 DA IG 個案提升為通用來源規格：

```text
source name ≠ all channels checked
```

新增通用欄位：

```text
publishing_channels
channel_priority
social_first
channel_check_required
channel_access_status
```

### 通用規則

```text
任何來源
→ 讀取 publishing_channels
→ 判斷 channel_priority
→ 若 social_first = true 或 channel_check_required = true
→ 強制 direct channel check
→ 無法存取則標示 unchecked / inaccessible / partial
→ generic search 不得冒充 direct channel check
→ 重大 claim 回查官方 / 數據 / 高證據來源
```

### 適用範圍

```text
不只 DA 交易者聯盟，也包含：
- 邦妮區塊鏈 IG / YouTube / 社群
- 加密城市社群渠道
- 區塊勢 Podcast / newsletter / 社群
- 台灣加密 KOL、研究帳號、交易社群
- 品牌官方 IG / FB / Threads / TikTok / LINE OA
- 百貨、購物中心、商場官方社群
- AI 開發者社群、產品發布帳號
- 公司高層公開社群帳號
- Podcast-first / YouTube-first / newsletter-first 產業媒體
```

### 下次報告新增 audit

```text
social_channels_checked_when_required: yes / partial / no / not_required
channel_gaps: none / list
```

若沒有直接檢查 social-first / channel-first 來源，必須標示：

```text
Social/channel-first source not checked directly; generic search may miss posts or channel-native content.
```

---

## Next Source Tests

下次每日推播需優先測試下列來源，每日至少 3 種：

### Retail Media

- Retail Dive
- Retail Brew
- Chain Store Age
- Shopping Center Business
- NRF

### Shopping Mall / Department Store

- 百貨官方公告
- 商場官方 News / Event
- 商場社群：Facebook、Instagram、Threads、LINE OA
- 招商 / tenant mix 公告
- 商圈新聞與地方媒體

### Brand Sources

品牌來源必須成為 Retail 雷達獨立類別，不可只附屬於百貨或商場。

固定追蹤項目：

- 品牌官網 Newsroom / Press / Blog
- 品牌門市列表與新櫃公告
- 品牌 IG / FB / Threads / TikTok / LINE OA
- 品牌會員活動與 CRM 訊息
- 聯名、快閃、展店、撤店、改裝、升級店型
- 價格帶變化、折扣深度、出清活動、新品節奏
- 台灣服飾品牌、國際服飾品牌、運動戶外品牌、生活風格品牌
- 商業周刊 / Business Weekly Taiwan
- HBR 哈佛商業評論繁體中文版

優先品牌池需依雷達任務動態調整，初始可含：

- UNIQLO / GU
- ZARA / H&M
- MUJI
- Nike / Adidas / New Balance
- Lululemon
- Life8 / Laking / OB 嚴選 / Poly Lulu
- NET / lativ
- 主要百貨進駐品牌與近期撤櫃品牌

### Crypto

- 立法院
- 立法院議案系統
- 金管會
- 行政院
- 總統府
- 全國法規資料庫
- 中央社政治 / 財經
- DeFiLlama
- RWA.xyz
- Token Terminal
- Coinglass
- Artemis
- The Block
- DA 交易者聯盟 IG / social channel
- 邦妮區塊鏈 social channel
- 加密城市 social channel if relevant
- 區塊勢 podcast / newsletter / social if relevant

### AI

- OpenAI Blog / Release notes
- Anthropic News / Release notes
- Microsoft Blog / Azure Blog
- GitHub Trending
- Hacker News
- VentureBeat
- The Information
- Semafor

---

## Operating Principle

每日市場情報不應只是 keyword search，而應逐步演化成：

```text
Source Library
→ source-specific search
→ channel-aware source check
→ cross-domain trigger detection
→ evidence grading
→ missed-case replay
→ Taiwan mapping
→ Source Experiment
→ Source Library update
```

目標是建立一套可持續演化的 Source Intelligence Library，讓 Search Agent 依主題自動選來源與渠道，而不是每天從零開始搜尋。
