# domains/｜領域包擴充機制

本目錄讓 daily-market-radar 在 canonical report domains 之外掛主題包，**引擎不動，領域包＝資料**。

```text
現行 canonical news domains：由 config/runtime_contract.json 定義，目前為五個。
細雷達模組：住在 configs/radars.yml，不自行建立 report-domain quota。
新主題包：一律用 domains/<domain_id>/，並映射到既有 canonical domain。
競品情報：使用 config/competitor_registry.json＋configs/competitor_intelligence.yml，
           屬跨領域 projection，不建立新 report domain。
勞動與消費壓力：indicator-only，不建立 domain pack 或新聞配額。
```

---

## 1. 新增一個領域包（三步，弱模型也能照做）

```text
1. 複製 domains/_template/ 成 domains/<domain_id>/
2. 填完 domain_pack.json（領域定位、範圍、必答問題、搜尋角度、產出映射、canonical_domain）
   與 sources.json（來源分層＋固定查詢配方）
3. commit——check-domain-packs 會驗完整性，填不完整不放行
```

新增主題包不代表新增 canonical report domain。預設必須映射到 `config/runtime_contract.json` 中既有領域；真的要改 runtime contract，屬架構變更，需人終審並同步測試、workflow、template 與 memory。

---

## 2. 領域包檔案

```text
domain_pack.json   領域定義（機器可驗）：id、name、positioning、canonical_domain、scope、
                   required_questions、mainstream_search_angles、edge_search_angles、
                   output_mapping、taiwan_mapping_rule、rendering_policy
sources.json       來源包（機器可驗）：tiers(global_media / local_media / official_data /
                   social_first / discovery)＋query_recipes（固定查詢配方）
```

格式用 JSON 而非 YAML：檢查器（`tools/brain/check-domain-packs.js`）零依賴即可解析。

---

## 3. 領域包的執行規則（對所有掃描 route 生效）

```text
1. 掃描包含 domains/ 領域包時，照 sources.json 的 tier 順序查：
   official_data → global_media → local_media → social_first（需 direct channel check）→ discovery。
2. query_recipes 是固定配方：照抄執行，不自行改寫；可加日期限定詞，不可刪核心詞。
3. 每則產出照 domain_pack.json 的 output_mapping 欄位記錄；缺資料標 unknown，不猜。
4. 蒐集階段不預篩：凡含新概念／新應用／新趨勢／新組合訊號，一律進 memory/potential_pool.md
   （見 configs/edge_case_discovery.yml capture_no_prefilter）。
5. 領域包本身不設定可偽造的固定新聞數量；profile floors 只由 config/runtime_contract.json 定義，
   缺口由 coverage audit 揭露，不得用歷史重播湊數。
6. social_first tier 的來源適用既有 channel-aware 規則（SOURCE_LIBRARY_SPEC.md §4.1）。
7. projection-only 或 indicator-only 主題必須明確標記 consumes_news_slot=false。
```

---

## 4. 邊界

```text
領域包是資料，不是規則來源；通用規則（freshness、台灣新聞、證據分級、coverage audit）
仍住在 configs/ 與 SOURCE_LIBRARY_SPEC.md，對所有領域一體適用。
領域包的來源健康與成效，走既有 Source Experiment / backtest 迴圈。
把主題升為 canonical report domain、把 canonical domain 降級、或改變 indicator/projection 邊界
都是架構變更，需人終審，不可順手做。
```
