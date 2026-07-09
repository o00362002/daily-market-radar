# PROJECT_OS_MOUNT｜daily-market-radar

本檔是本 repo 的掛載宣告（Projection，不是 source of truth）。

---

## 1. Mount Identity

```text
Core repo: o00362002/brain-core（蒸餾核）
Core version: v0
Mount since: 2026-07-06
Role: 每日市場情報雷達（recurring intelligence workflow）＋ 多領域新聞趨勢掃描
Previous mount: o00362002/Human-AI-Collaboration-Brain（已於 2026-07-06 退役）
```

---

## 2. 掛載的實質內容

brain-core 掛載＝繼承五原則＋複製機器層，不是複製資料夾結構：

```text
P1 規則必有機器消費者
P2 入口極薄、按需路由
P3 資料驅動（JSON/YAML＋檢查器 > 散文）
P4 模型無關層最厚；CLAUDE.md 只做薄適配
P5 記憶輪替（頭部預算＋季度歸檔）
```

機器層（本 repo 內自足，不依賴外部 repo 才能跑）：

```text
tools/install_hooks.sh               安裝 pre-commit 關口
tools/brain/check-core.js            不變式4：必備檔＋入口預算＋不變式數量鎖
tools/brain/check-sync-matrix.js     不變式2：連動提醒（advisory）
tools/brain/check-doc-paths.js       不變式3：路徑現實（advisory）
tools/brain/check-domain-packs.js    不變式5：領域包完整性
check_mount_integrity.sh             CI／人工共用體檢入口（薄包裝）
```

---

## 3. Source of Truth

```text
掛載宣告: brain.manifest.yaml
執行入口: AGENTS.md
現況: CURRENT_STATE.md
決策: CURRENT_DECISIONS.md
任務路由: AGENT_DEFINITION_MAP.md
依賴閘門: DEPENDENCY_MAP.md
連動矩陣: schema/sync-matrix.json
核心原則: o00362002/brain-core（P1–P5）
```

---

## 4. 舊母腦處置

```text
舊母腦（Human-AI-Collaboration-Brain）掛載已退役;其 adoption 檔早已列為凍結歷史
（AI_PROJECT_OS_ADOPTION_PLAN.md 等,見 CURRENT_STATE.md)。
歷史 reports / memory 中的母腦引用屬凍結歷史,不回頭改寫。
架構問題以 brain-core 為準;兩腦對照協議見 brain-core/COMPARE.md。
```

---

## 5. Sync Rule

連動關係唯一住在 `schema/sync-matrix.json`（check-sync-matrix 在 commit 時自動提醒）。
本檔不再維護散文版同步清單。
