# Execution Check｜2026-07-06 換掛 brain-core ＋ 多領域擴充機制

流程證據紀錄（不變式 1 的消費對象）。對應決策：CURRENT_DECISIONS.md 2026-07-06 兩條。

## 改了什麼

```text
掛載切換（母腦 → brain-core）：
  brain.manifest.yaml、AGENTS.md（7955→約4200 字元）、CLAUDE.md、PROJECT_OS_MOUNT.md、
  README.md、PROJECT_MAP.md、HIGH_LEVEL_INDEX.md、CONTEXT_ROUTING.md、
  CURRENT_STATE.md（改為頭部摘要＋歷程輪替結構）、schema/sync-matrix.json（v2）、
  check_mount_integrity.sh（改薄包裝，CI workflow 檔不用動）
新增機器層：
  tools/brain/check-core.js（不變式4）、tools/brain/check-domain-packs.js（不變式5）、
  tools/install_hooks.sh（覆蓋舊母腦 hook）
新增擴充機制：
  domains/README.md、domains/_template/{domain_pack.json,sources.json}、
  configs/query_recipes.yml、memory/potential_pool.md、
  configs/edge_case_discovery.yml capture_no_prefilter、
  SOURCE_LIBRARY_SPEC.md §5.1、AGENT_DEFINITION_MAP.md 兩段 boundary
研究依據：
  research/global_news_trend_projects_2026-07-06.md
```

## 沒做什麼（明確不在本次範圍）

```text
1. 沒把六大核心領域遷移成 domains/ 領域包（radars.yml 仍 canonical;遷移=架構變更需人終審）
2. 沒改 workflows/ 與 templates/ 的內容規則（雷達行為不變,只加了配方與池的接點）
3. 沒動 DEPENDENCY_MAP.md（內容級依賴鏈仍有效）
4. 沒寫 selftest.js（檢查器的檢查器;brain-core 有,child 暫缺,列為後續 observe）
5. 沒刪任何凍結歷史檔
6. 沒 commit（等 owner 檢視）
```

## 會影響誰

```text
所有掃描 route（推播/完整雷達/主題搜尋）:多了固定查詢配方先行＋潛力池入池義務。
commit 流程:pre-commit 關口改為 brain-core 五不變式(舊 hook 被覆蓋)。
CI:mount-check.yml 不用改,check_mount_integrity.sh 行為改為跑 node 檢查器。
```

## 機器檢查

```text
bash check_mount_integrity.sh → 見本次執行輸出(目標 complete)
node tools/brain/check-core.js . → 必備檔/入口預算/不變式數量
node tools/brain/check-domain-packs.js . → _template 結構
```

## 你可以驗證

```text
1. bash check_mount_integrity.sh 應輸出 Result: complete
2. 故意在 domains/ 建一個缺欄位的包再跑檢查器,應被擋
3. AGENTS.md 字元數 ≤4500:wc -c AGENTS.md
4. 動 CURRENT_STATE.md 不附 reports/ 就 commit,hook 應擋下
```
