# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-07-07

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

### Why

研究檔 `research/global_news_trend_projects_2026-07-06.md` 已指出：RSSHub 可解決 social-first / channel-first 漏抓；FreshRSS 可作為自架聚合收件箱；GDELT / Media Cloud 適合做來源與事件缺口 discovery。此組合補的是「固定來源庫之外的渠道與發現層」，不是新增重型 agent product。

### Result

```text
已新增或更新：
configs/feed_discovery_stack.yml
sources/channel_feed_sources.json
sources/discovery_providers.yml
infra/rss-stack/docker-compose.yml
infra/rss-stack/.env.example
infra/rss-stack/README.md
FRESHRSS_SEEDS.md
FRESHRSS_SEEDS.opml
SOURCE_LIBRARY_SPEC.md
DEPENDENCY_MAP.md
AGENT_DEFINITION_MAP.md
reports/feed_stack_sync_status_2026-07-07.md

已驗證：
/youtube/channel/:id
/telegram/channel/:username
/threads/:user
/picnob.info/user/:id（保留 disabled，需要 runtime support 與具體帳號測試）

修正：
原 /github/repos/DIYgod/RSSHub/releases 未驗證為有效 RSSHub releases route，改用 GitHub 官方 releases.atom。
```

### Runtime validation still pending

```text
SOURCE_LIBRARY_SPEC.md、DEPENDENCY_MAP.md、AGENT_DEFINITION_MAP.md 已完成 source-of-truth 同步。
尚未完成的是 RSSHub / FreshRSS runtime 驗證：
1. 啟動 RSSHub + FreshRSS。
2. 匯入 FRESHRSS_SEEDS.opml。
3. 確認 FreshRSS 能 refresh enabled feeds。
4. 後續再把 smoke-test seed 換成真正 market-radar 來源。
```

---

## 2026-07-06：換掛 brain-core（舊母腦退役）

### Decision

本 repo 的治理掛載從 `Human-AI-Collaboration-Brain`（母腦 v2.0-draft thin mount）換成 `brain-core`（蒸餾核）。不再使用 Level / capability 散文模型；改為五原則（P1–P5）＋ 五條不變式，每條不變式都有機器消費者。

### Why

母腦終局檢驗（2026-07-06，見 brain-core/DECISIONS.md）量化證明散文治理失效：入口稅 38.8K tokens、23 條規則 13 條零消費。brain-core 把規則寫成資料＋檢查器，在 commit 關口自動出現，不靠人記、不靠 AI 自律讀。本 repo 是 brain-core 第一個真實掛載專案。

### Result

```text
改：brain.manifest.yaml / AGENTS.md / CLAUDE.md / PROJECT_OS_MOUNT.md / README.md /
    PROJECT_MAP.md / HIGH_LEVEL_INDEX.md / CONTEXT_ROUTING.md / CURRENT_STATE.md /
    schema/sync-matrix.json / check_mount_integrity.sh
增：tools/brain/check-core.js / tools/brain/check-domain-packs.js / tools/install_hooks.sh
證據：reports/execution_checks/2026-07-06_brain_core_mount_and_domain_extension.md
```

---

## 2026-07-06：多領域擴充機制＋潛力池不預篩＋固定查詢配方

### Decision

```text
1. 新領域一律用 domains/<domain_id>/ 領域包掛載（domain_pack.json + sources.json）。
2. 蒐集階段不做預先篩選：新概念/新應用/新場景/新商業模式/新組合/新趨勢苗頭一律入 memory/potential_pool.md。
3. 弱模型可執行的固定查詢配方：configs/query_recipes.yml（核心六領域）與領域包內 query_recipes。
```

### Why

外部研究證明蒐集階段的價值過濾會系統性漏掉早期訊號；structured-output 研究證明小模型在固定管線＋固定 schema 下可穩定執行；商業媒體監測業的共同架構是「引擎領域無關、領域＝配置」。

### Result

```text
增：domains/README.md / domains/_template/{domain_pack.json,sources.json} /
    configs/query_recipes.yml / memory/potential_pool.md /
    research/global_news_trend_projects_2026-07-06.md
改：configs/edge_case_discovery.yml / SOURCE_LIBRARY_SPEC.md / AGENT_DEFINITION_MAP.md
```

---

## 2026-07-02：Search Agent adopts source-library-first method

### Decision

每日市場雷達與指定主題新聞搜尋的 Search Agent 方法，從「keyword-first」調整為「source-library-first」。

Active source-library files:

```text
SOURCE_LIBRARY_SPEC.md
configs/source_routing_rules.yml
sources/key_media_library.yml
sources/official_and_data_sources.yml
```

New execution order:

```text
固定來源庫
→ 來源內關鍵字與主題過濾
→ 外部關鍵字 fallback
→ 新來源 discovery
→ coverage audit
```

### Rules

```text
1. AGENT_RADAR_REPORT、AGENT_DAILY_PUSH_BRIEF、AGENT_NEWS_SEARCH 必須先檢查固定來源庫，再使用 generic keyword search。
2. 關鍵字搜尋保留，但降級為來源內過濾、事件補查、缺口 retry、外部 discovery。
3. 每個核心領域要能回溯已查來源、命中來源、未命中來源、是否使用 fallback。
4. 台灣新聞仍必須是 source-backed Taiwan event / data / company action / policy / market news，不得用台灣推論補位。
5. 官方 / 數據 / 公司公告來源應用於高風險 claim 與指標變化交叉驗證。
6. source library 是可維護的活表，不是死表；來源健康需透過後續回測與使用紀錄調整。
```

### Result

```text
SOURCE_LIBRARY_SPEC.md
configs/source_routing_rules.yml
sources/README.md
sources/key_media_library.yml
sources/official_and_data_sources.yml
configs/source_strategy.md
workflows/daily_radar_workflow.md
workflows/daily_push_brief_workflow.md
workflows/news_search_content_workflow.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
```

---

## Older active decisions

詳見 git history before 2026-07-07 for:

```text
2026-07-01 Adopt mother Brain Post-Execution Backtest-to-Memory Flow
2026-06-29 外部模型回測紀錄，不調整架構
2026-06-29 每日執行最小閘門測試版
2026-06-29 台灣新聞與商業觀點來源補強
2026-06-29 每日訊號硬閘門，大型重要新聞 5 則 + 小眾候選 3 則
```
