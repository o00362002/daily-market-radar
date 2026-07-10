# daily-market-radar｜CURRENT_STATE

<!-- 頭部摘要 ≤8000 字元（check-core 驗）。輪替規則：dated 段每季搬 archive/，
     頭部永遠只留「現在正在成立的事實」。歷史不是現況。 -->

## 現況摘要（讀這裡就夠）

```text
掛載：brain-core child mount（2026-07-06 起）。舊母腦 Human-AI-Collaboration-Brain 已退役。
定位：每日市場情報雷達（recurring intelligence workflow）＋ 多領域新聞趨勢掃描。
機器層：5 條不變式全數有檢查器（check-core / check-sync-matrix / check-doc-paths /
  check-domain-packs ＋ process gate）；hook 由 tools/install_hooks.sh 安裝；
  CI 與人工共用 check_mount_integrity.sh。
領域：六大核心領域住 configs/radars.yml ＋ sources/key_media_library.yml（canonical）；
  新領域用 domains/<id>/ 領域包（複製 _template 填完，檢查器驗完整性）。
搜尋方法：source-first ＋ 固定查詢配方（configs/query_recipes.yml），
  generic search 只是 fallback 且需在 coverage audit 揭露。
潛力池：蒐集階段不預篩（configs/edge_case_discovery.yml capture_no_prefilter），
  新概念/新應用/新趨勢/新組合一律入 memory/potential_pool.md；取捨只在輸出階段。
台灣新聞：必須 source-backed；推論不得計入。social-first 來源必須 direct channel check。
每日輸出：預設 Daily Push Brief；v2 走 slot cap + coverage gate，不用固定篇數證明完整。
```

## 入口邊界

```text
AGENTS.md = 第一入口（按需路由）
brain.manifest.yaml = 掛載宣告
CURRENT_STATE.md / CURRENT_DECISIONS.md = 記憶層
AGENT_DEFINITION_MAP.md = 任務路由
DEPENDENCY_MAP.md = 依賴與完成閘門
SYSTEM_PROMPT.md = 每日雷達品質政策（不取代 AGENTS.md）
```

## Frozen History

以下舊過渡檔已凍結，只保留歷史脈絡，不再作為 current routing / source of truth / active rule：

```text
AI_PROJECT_OS_ADOPTION_PLAN.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
POST_CHANGE_SYNC_ADOPTION.md
README_AGENT_MODEL_NOTE.md
CURRENT_DECISIONS_APPEND.md
ADOPTION_LEVELS.md
```

## 歷程（季度輪替區）

### 2026-07-06 換掛 brain-core ＋ 多領域擴充機制

```text
掛載：brain.manifest.yaml / AGENTS.md / CLAUDE.md / PROJECT_OS_MOUNT.md / README /
  PROJECT_MAP / HIGH_LEVEL_INDEX / CONTEXT_ROUTING 全部改為 brain-core child mount；
  check_mount_integrity.sh 改為薄包裝（CI 不用改）；新增 check-core.js /
  check-domain-packs.js / install_hooks.sh。
擴充：新增 domains/ 領域包機制（_template ＋ README spec）、configs/query_recipes.yml
  固定查詢配方、memory/potential_pool.md 潛力池（蒐集不預篩）、
  edge_case_discovery.yml capture_no_prefilter 規則。
依據：research/global_news_trend_projects_2026-07-06.md（GDELT/Event Registry/RSSHub/
  DEFRA horizon scanning/structured-output 小模型研究）。
證據：reports/execution_checks/2026-07-06_brain_core_mount_and_domain_extension.md
```

### 2026-07-05 mother-brain v2 sync（已被 2026-07-06 換掛取代，superseded）

```text
當時同步至母腦 v2.0-draft mount depth 模型（Level 2 alias）。
此掛載已於 2026-07-06 退役，僅留此紀錄。
```
