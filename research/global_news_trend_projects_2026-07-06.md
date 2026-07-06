# 全球新聞蒐集／趨勢偵測／潛力發掘專案研究｜2026-07-06

研究目的：為 daily-market-radar 的三項改造提供外部依據——
(a) 弱模型也能穩定執行的固定新聞搜尋流程；(b) 領域可擴充架構；(c) 潛力項目蒐集階段不預篩。

---

## 1. 全球新聞聚合／話題偵測專案

| 專案 | 架構要點 | 對本 repo 的借鑑 |
|---|---|---|
| GDELT Project | 監測 100+ 語言全球媒體，即時抽取人物/地點/組織/主題/情緒;免費 API/BigQuery | 已在 `sources/` external_discovery。適合覆蓋缺口掃描與多語言發現,不當作證據來源 |
| Event Registry | 30 萬+ 來源,把文章「聚類成事件」而非單篇列表 | 事件聚類=歷史去重的正確單位;本 repo 的 7 日去重規則同方向,聚類鍵應是「事件」不是「標題」 |
| NewsCatcher | 7 萬+ 來源、5 年歷史檔、NLP 主題分類/實體抽取 | 深搜與回測資料源候選;付費 |
| Media Cloud | 開源媒體研究資料庫,來源發現與媒體分析 | 已在 external_discovery;適合新來源 discovery |
| RSSHub(開源) | 「萬物皆可 RSS」:5000+ 路由,把 IG/Threads/YouTube/TikTok/Telegram 等轉成結構化 feed;可自架 | **直接解決本 repo 的 social-first 渠道檢查痛點**(DA 交易者聯盟 IG 漏抓案)。可自架一套,把 channel_check 從人工翻帳號變成固定 feed 抓取 |

來源:
- [GDELT vs Event Registry 比較(arXiv 1603.01979)](https://arxiv.org/pdf/1603.01979)
- [GDELT Project for News Data 2026](https://dataresearchtools.com/gdelt-project-for-news-data-2026-free-alternative-to-newsapi/)
- [Best News APIs 比較](https://dataresearchtools.com/best-news-apis-comparison/)
- [RSSHub GitHub](https://github.com/DIYgod/RSSHub)、[RSSHub 自架指南](https://www.self-host.app/services/rsshub)

## 2. 弱訊號偵測／Horizon Scanning 成熟方法

英國政府(DEFRA)Horizon Scanning 實務——與本 repo 的潛力候選訊號機制直接對應:

```text
每日捕捉弱訊號 → 蒐集階段刻意涵納邊緣與非主流來源、不做價值過濾
→ 之後才用「使用案例標籤」triage(僅供參考/機會或風險指標/研究優先化)
→ 訊號持續聚類、標記重複主題
→ 每兩週選 6 個最新穎訊號深入分析;每 6 個月聚類產出趨勢報告
```

關鍵原則:**過濾發生在輸出與分析階段,不發生在蒐集階段**;蒐集階段的偏見會系統性漏掉早期訊號(本 repo 的虛擬資產服務法漏抓即為此類)。

來源:
- [GOV.UK Weak signals and trend analysis](https://www.gov.uk/government/publications/weak-signals-and-trend-analysis-horizon-scanning/weak-signals-and-trend-analysis-horizon-scanning)
- [ITONICS: 6 Advances in Automated Horizon Scanning](https://www.itonics-innovation.com/blog/weak-signals)
- [Envisioning: Weak Signals Methodology](https://www.envisioning.com/methodology/weak-signals)

## 3. 弱模型可穩定執行的 deterministic 管線

業界共識(2025-2026):

```text
1. LLM 當「語意處理引擎」而非自主 agent:固定管線、固定步驟,模型只做每步的語意工作。
2. Structured Output + schema 驗證作為第一道閘:欄位齊不齊用程式驗,不靠模型自律。
3. 小模型在固定 schema 管線下,每正確欄位成本低 6-11 倍,準確率僅損失約 2%。
4. 判斷規則寫成資料+檢查器(query recipes、必填欄位、允許值),模型換強換弱行為不變。
```

對本 repo:radars.yml/edge_case_discovery.yml 已是固定欄位輸出;缺的是**固定查詢配方層**(弱模型不會自己想出好查詢)→ 新增 `configs/query_recipes.yml` 與領域包內 query_recipes。

來源:
- [LLM Structured Outputs: Schema Validation for Real Pipelines](https://collinwilkins.com/articles/structured-output)
- [Structured Output Benchmark(arXiv 2604.25359)](https://arxiv.org/html/2604.25359v1)

## 4. 多領域可擴充的監測架構

商業媒體監測業(Meltwater/Brandwatch/Mention,1 億-10 億來源)的共同架構:**引擎領域無關,領域=配置**(來源清單+關鍵字+警報規則)。開源側沒有完整替代品,但組合可行:RSSHub(渠道)+ FreshRSS/自架聚合(收)+ GDELT/Media Cloud(發現)。

對本 repo 的落地:**domain pack 機制**——引擎(workflows+configs 通用規則)不動,一個領域一個包(`domains/<id>/domain_pack.json + sources.json`),新領域=複製 `_template` 填完,完整性由檢查器把關(`tools/brain/check-domain-packs.js`),填不完整 commit 關口就擋下。這正是「規則=資料+檢查器」的 brain-core P3 原則。

來源:
- [Meltwater Alternatives 2026(Trends MCP)](https://www.trendsmcp.ai/blog/best-meltwater-alternatives-2026)
- [Top Meltwater Alternatives(Wizikey)](https://wizikey.com/blog/top-meltwater-alternatives-in-2026-media-monitoring-tools-for-modern-pr-teams)

## 5. 結論 → 本 repo 的三項落地

```text
1. domains/ 領域包機制(新領域可插拔,檢查器驗完整性)——見 domains/README.md
2. configs/query_recipes.yml 固定查詢配方(弱模型照抄執行,不自行發明查詢)
3. memory/potential_pool.md 潛力池:蒐集階段全收不預篩(新概念/新應用/新趨勢/新組合),
   triage 與計數只在輸出階段;池內項目定期聚類回顧(DEFRA 模式)
```

本檔為證據層研究紀錄,不是 active rule;規則落點見 CURRENT_DECISIONS.md 2026-07-06 條目。
