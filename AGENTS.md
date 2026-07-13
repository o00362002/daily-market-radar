# daily-market-radar｜AGENTS

一句話：**規則是資料＋檢查器，在 commit 關口自己出現；入口薄、按需路由。**

Control links:

```text
Parent control panel: o00362002/personal-project-brain
Local source-of-truth: this repo
Agent entry: AGENTS.md
Governance owner: o00362002/brain-core
```

## 讀取路由（按需，沒有必讀清單）

```text
現在的狀態？        → CURRENT_STATE.md（讀頭部摘要就夠）
為什麼這樣設計？    → CURRENT_DECISIONS.md
每日播報／搜尋選路？→ AGENT_DEFINITION_MAP.md（推播/完整雷達/主題搜尋/內容/回測/社群渠道）
來源與查詢怎麼跑？  → SOURCE_LIBRARY_SPEC.md、configs/query_recipes.yml、sources/
新領域怎麼加？      → domains/README.md（複製 _template 填完即掛上）
潛力項目放哪？      → memory/potential_pool.md（蒐集階段不篩選）
改連動關係？        → schema/sync-matrix.json（唯一矩陣）
治理與 checker 映射？→ brain.manifest.yaml
其他一切：直接動手。commit 時關口會接住你。
```

## Core governance 與 domain checks

```text
Core governance 定義由 brain-core 擁有；本地 consumer mapping 在 brain.manifest.yaml。
Daily Radar domain checks 只能增加，不能取代 core governance checks。
修改 protected files 前必須取得人類確認，並同一變更附 reports/change-confirmations/*.md。
```

## 完成的定義

機器檢查綠 ＋ 5 行人話收據：改了什麼／機器檢查／沒做什麼／會影響誰／你可以驗證。

## 雷達邊界（反覆踩過的坑，違反即重大品質事故）

```text
固定來源庫與固定查詢配方先跑，generic search 只是 fallback，且要在 coverage audit 揭露。
台灣新聞必須 source-backed；「台灣可能受影響」是推論，不得計入台灣新聞。
每則輸出訊號必須有今日新增點；歷史重播無新增資料不計入槽位。
social-first 來源必須 direct channel check；generic search 不算已檢查。
蒐集階段不預篩：新概念/新應用/新趨勢/新組合一律入 potential_pool；取捨只在輸出階段。
政策/法規/市場重大 claim 必須回查官方或數據來源；生成者 ≠ 判官 ≠ 簽核人。
Evidence 不經核可不成為 Memory；凍結歷史不是現況。
```

## 關聯規則（Association rule, brain-core 2026-07-07）

```text
抓到同步漂移 → 在 schema/sync-matrix.json 長一條邊（或升為生成/驗證級），
修復紀錄註明長了哪條。可機械推導的事實（數量/狀態統計）禁止手抄進散文。
Caught a sync drift → grow a matrix edge (or upgrade to generated/verified);
name it in the fix record. Never hand-copy derivable facts into prose.
```

## 新規則准入

想加規則？先答「誰、在什麼時點、用什麼機器消費它？」
答不出 → 它是說明不是規則，寫進 CURRENT_DECISIONS.md 的 why 即可。
新增檔案、規則、語彙、檢查器、schema、workflow 前，先看既有路徑能否承接；能承接就改既有。

## 本專案目標

繼承 brain-core 角色邊界、決策權與風險分級；權威見 brain-core `DECISIONS.md`。

**本專案目標＝本專案回測／架構調整的量尺，由人 owner 定，AI 不自產。**

本專案目標｜This project's goal: 蒐集全世界重要訊息與新趨勢/新應用/新話題的**潛力訊息**，藉此了解現在與未來方向。（owner 2026-07-08）｜Surface important information and potential signals to understand where things may head.

安裝關口（一次性）：`bash tools/install_hooks.sh`｜體檢：`bash check_mount_integrity.sh`

## 單一承載規則（Single-carrier rule, brain-core 2026-07-13）

```text
一個概念一個 owner 檔；其他檔案連結或路由，不抄字句。
機器投影只在 consumer 讀取時才重複資料，否則連回 owner。
One owner file per concept; others link, no copying.
Projections repeat only for a real consumer, else link back.
```