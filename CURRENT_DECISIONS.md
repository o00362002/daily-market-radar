# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-07-07

---

## 2026-07-07：零售領域加入時尚 / 流行，小眾候選新增類型與形成程度

### Decision

```text
1. 品牌零售領域正式擴充為：零售 / 消費 / 社群 / 服飾 / 時尚 / 流行。
2. Retail domain 不只看通路、展店、百貨、電商，也必須掃描時尚、流行、穿搭風格、顏色、材質、版型、品類、商品組合、品牌 merchandising 與消費者審美變化。
3. 小眾候選新增 candidate_type：新領域 / 新應用 / 新概念 / 新趨勢。
4. 小眾候選新增 formation_level：弱訊號 / 話題形成 / 趨勢形成 / 主流化中。
5. 很多報導、很多討論、詞彙或敘事開始擴散 = 話題形成。
6. 很多品牌、公司、平台、地區開始應用、試點、投資、招聘或數據同步出現 = 趨勢形成。
7. 已廣泛商業化且有明確數據 = 主流化中，應評估是否升級為大型訊號。
```

### Why

小眾候選原本容易被寫成空泛趨勢感想。這次把候選拆成「新領域、新應用、新概念、新趨勢」與「弱訊號、話題形成、趨勢形成、主流化中」，讓每日雷達能區分：

```text
只有人在講 = 話題形成
很多開始做 = 趨勢形成
已經廣泛商業化 = 可能升級大型訊號
```

零售領域若只看百貨、電商與通路，會漏掉服飾與品牌真正重要的上游：流行風格、穿搭語言、商品組合、材質與審美遷移。

### Result

```text
更新：configs/niche_candidate_policy.yml
更新：workflows/daily_push_brief_workflow.md
更新：workflows/daily_radar_workflow.md
更新：templates/daily_push_brief_template.md
更新：templates/daily_report_template_v2.md
```

---

## 2026-07-07：小眾候選與大型訊號等量；精簡 3+3、完整 5+5

### Decision

```text
1. 小眾候選數量必須與大型訊號數量相同。
2. Daily Push Brief：每領域 3 大型訊號 + 3 小眾候選。
3. Full Daily Radar：每領域至少 5 大型訊號 + 至少 5 小眾候選（when available）。
4. 舊 3+1 與 5+3 規則退役。
5. 小眾候選必須是具體早期弱訊號，不得用空泛趨勢句、模型感想或大型新聞改寫補位。
6. 候選不足時必須先 retry / external discovery；仍不足才標 gap，不得捏造。
```

### Candidate quality

每則候選至少需要一個具體錨點：公司、產品、論文、數據、融資、招聘、開源採用、鏈上指標、社群事件、pilot、patent、clinical trial、prototype 或 supply-chain anomaly。

每則候選必須回答：

```text
為何小眾 / 早期
為何可能放大
不能下的結論
下一步驗證
```

### Result

```text
新增：configs/niche_candidate_policy.yml
更新：SYSTEM_PROMPT.md
更新：workflows/daily_push_brief_workflow.md
更新：workflows/daily_radar_workflow.md
更新：templates/daily_push_brief_template.md
更新：templates/daily_report_template_v2.md
```

---

## 2026-07-07：Technology anti-AI-overcapture + Taiwan crypto source audit

### Decision

```text
1. AI domain 不得重複佔用 Technology quota。
2. Technology 至少掃描 6 個非 AI 技術子域；不足標 partial。
3. Taiwan crypto 若未檢查固定來源，不得宣稱無新台灣加密新聞。
4. 固定來源包含 DA 交易者聯盟、邦妮區塊鏈、加密城市、區塊勢。
```

### Result

```text
更新：configs/technology_development.yml
新增：memory/missed_cases/2026-07-07_technology_ai_overcapture_and_taiwan_crypto_sources.md
歸檔：reports/2026/2026-07-07.md
```

---

## 2026-07-07：RSSHub + FreshRSS + GDELT / Media Cloud feed discovery stack

### Decision

```text
1. 新增 feed discovery stack 作為 source-library-first 的收集與發現擴充層。
2. RSSHub = public channel-to-feed adapter；FreshRSS = self-hosted feed inbox / aggregator。
3. GDELT / Media Cloud = external discovery providers，只做缺口發現與來源發現。
4. RSSHub / FreshRSS 不提升證據等級；GDELT / Media Cloud 不可當最終事實來源。
5. OPML 只可匯入 sources/channel_feed_sources.json 中 route_status = verified 且 enabled_for_opml = true 的項目。
6. Feed/discovery 發現的新概念、新應用、新組合、新趨勢苗頭仍先進 memory/potential_pool.md，輸出階段才篩選。
```

### Runtime validation still pending

```text
1. 啟動 RSSHub + FreshRSS。
2. 匯入 FRESHRSS_SEEDS.opml。
3. 確認 FreshRSS 能 refresh enabled feeds。
4. 後續再把 smoke-test seed 換成真正 market-radar 來源。
```

---

## 2026-07-06：換掛 brain-core（舊母腦退役）

本 repo 的治理掛載從 `Human-AI-Collaboration-Brain` 換成 `brain-core`（蒸餾核）。不再使用 Level / capability 散文模型；改為五原則（P1–P5）＋五條不變式。

---

## 2026-07-06：多領域擴充機制＋潛力池不預篩＋固定查詢配方

```text
1. 新領域一律用 domains/<domain_id>/ 領域包掛載。
2. 蒐集階段不做預先篩選：新概念/新應用/新場景/新商業模式/新組合/新趨勢苗頭一律入 memory/potential_pool.md。
3. 弱模型可執行固定查詢配方：configs/query_recipes.yml 與領域包內 query_recipes。
```

---

## 2026-07-02：Search Agent adopts source-library-first method

每日市場雷達與指定主題新聞搜尋的 Search Agent 方法，從 keyword-first 調整為 source-library-first。

```text
固定來源庫
→ 來源內關鍵字與主題過濾
→ 外部關鍵字 fallback
→ 新來源 discovery
→ coverage audit
```

---

## Older active decisions

詳見 git history before 2026-07-07。舊 `3+1` / `5+3` quota 決策已由 2026-07-07 的 `3+3` / `5+5` 決策取代。
