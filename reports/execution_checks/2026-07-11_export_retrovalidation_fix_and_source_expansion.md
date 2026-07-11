# Export 回溯驗證修復 + 來源大擴充

Branch: `fix/export-floor-retrovalidation`（base `main`）

## 問題（線上實際失敗）

合併 #23 後手動觸發 daily-intelligence，在 Export web artifacts 失敗：
`ValueError: taiwan items 0 below floor 1 without declared below_minimum_taiwan`。
根因：export 用今日的新地板政策回溯驗證 DB 內「地板上線前」產生的舊報告。歷史報告在
產生當下合法，不得被之後的政策改動回溯否決。

## 改了什麼

1. **回溯驗證修復**：`validate_report_contract(..., enforce_floors=)` — 建立/匯入時
   enforce（今日報告必須符合政策），投影儲存歷史時只驗結構。用**當日實際出錯的 state DB**
   重現並驗證修復（export 47 artifacts 成功）。回歸測試 ×2。
2. **來源擴充（全部本機實測）**：探測 27 個候選、**新增 21 個通過驗證的新來源**（BBC、
   Guardian、CNBC、MarketWatch、ECB、SCMP、Nikkei Asia、Ars Technica、MIT TR、Hacker News、
   HuggingFace、DeepMind、Cointelegraph、The Block、Modern Retail、arXiv cs.LG、Nature、
   IEEE Spectrum、**TechNews、iThome、INSIDE**）。實測失敗不加（BIS、FashionUnited、NRF、BLS、
   CNA mainpage）。來源 33→54、RSS-capable 17→**38**、台灣 RSS 4→**7**。
3. **首頁精選**：真實量測 976 items 後，首頁重大/台灣改精選顯示（3/領域、前 8 筆）＋
   全數保留於報告頁與 JSON；首頁 131KB（gzip 17.8KB）。

## 機器驗證

- **真實 live run：38 來源、0 失敗、events 976、items 976（745 重大/231 潛力/227 台灣）、
  全部地板達標、33 秒**——對照當日早上 3 items。
- 195 tests 綠（+2 回歸）；make validate（fresh-checkout 條件）綠；registry 驗證＋OPML
  byte-stable；types:check 同步；Astro build 46 頁。
