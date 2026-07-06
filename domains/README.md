# domains/｜領域包擴充機制

本目錄讓 daily-market-radar 在現有六大核心領域之外掛新領域,**引擎不動,領域=資料**。

```text
現有六大核心領域:住在 configs/radars.yml + sources/key_media_library.yml(維持不動,仍是 canonical)
新領域:一律用 domains/<domain_id>/ 領域包
掃描時的領域清單 = 六大核心領域 + domains/ 下所有領域包
```

---

## 1. 新增一個領域(三步,弱模型也能照做)

```text
1. 複製 domains/_template/ 成 domains/<domain_id>/
2. 填完 domain_pack.json(領域定位、範圍、必答問題、搜尋角度、產出映射)
   與 sources.json(來源分層 + 固定查詢配方)
3. commit——check-domain-packs 會驗完整性,填不完整不放行
```

不需要改 workflows、templates 或任何入口檔。

---

## 2. 領域包檔案

```text
domain_pack.json   領域定義(機器可驗):id、name、positioning、scope、
                   required_questions、mainstream_search_angles、edge_search_angles、
                   output_mapping、taiwan_mapping_rule、minimum_daily
sources.json       來源包(機器可驗):tiers(global_media / local_media / official_data /
                   social_first / discovery)+ query_recipes(固定查詢配方,照抄執行)
```

格式用 JSON 而非 YAML:檢查器(`tools/brain/check-domain-packs.js`)零依賴即可解析。

---

## 3. 領域包的執行規則(對所有掃描 route 生效)

```text
1. 掃描包含 domains/ 領域包時,照 sources.json 的 tier 順序查:
   official_data → global_media → local_media → social_first(需 direct channel check)→ discovery
2. query_recipes 是固定配方:照抄執行,不自行改寫;可加日期限定詞,不可刪核心詞。
3. 每則產出照 domain_pack.json 的 output_mapping 欄位記錄;缺資料標 unknown,不猜。
4. 蒐集階段不預篩:凡含新概念/新應用/新趨勢/新組合訊號,一律進 memory/potential_pool.md
   (見 configs/edge_case_discovery.yml capture_no_prefilter)。
5. 新領域的每日最低量由 domain_pack.json 的 minimum_daily 定義;
   核心六領域仍走 edge_case_discovery 的 5+3 硬閘門。
6. social_first tier 的來源適用既有 channel-aware 規則(SOURCE_LIBRARY_SPEC.md §4.1)。
```

---

## 4. 邊界

```text
領域包是資料,不是規則來源;通用規則(freshness、台灣新聞、證據分級、coverage audit)
仍住在 configs/ 與 SOURCE_LIBRARY_SPEC.md,對所有領域一體適用。
領域包的來源健康與成效,走既有 Source Experiment / backtest 迴圈。
把某核心領域遷移成領域包 = 架構變更,需人終審,不可順手做。
```
