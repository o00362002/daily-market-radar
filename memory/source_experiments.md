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
| domains | 適合主題，例如 AI、Retail、Crypto、Taiwan、Geopolitics |
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
| 泛零售舊新聞搜尋 | Retail | 慢 | 否 | 高 | 未確認 | 降權 | 容易抓到舊 AI shopping 或電子價牌背景，不可計入今日大型訊號。 |
| 台灣影響推論式補位 | Taiwan mapping | 不適用 | 否 | 不適用 | 不適用 | 淘汰 | 不得用「台灣可能受影響」替代台灣新聞。 |

---

## Next Source Tests

下次每日推播需優先測試下列來源，每日至少 3 種：

### Retail

- Retail Dive
- Retail Brew
- Chain Store Age
- Shopping Center Business
- NRF
- 百貨官方公告
- 商場社群
- 品牌 IG / FB

### Crypto

- DeFiLlama
- RWA.xyz
- Token Terminal
- Coinglass
- Artemis
- The Block

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
→ cross-domain trigger detection
→ evidence grading
→ missed-case replay
→ Taiwan mapping
→ Source Experiment
→ Source Library update
```

目標是建立一套可持續演化的 Source Intelligence Library，讓 Search Agent 依主題自動選來源，而不是每天從零開始搜尋。
