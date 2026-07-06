# daily-market-radar｜AGENTS

一句話：**規則是資料＋檢查器，在 commit 關口自己出現；入口薄、按需路由。**

核心掛載：[brain-core](https://github.com/o00362002/brain-core)（蒸餾核；P1–P5 見其 DECISIONS.md）。
舊母腦 Human-AI-Collaboration-Brain 已退役，只存在凍結歷史與舊紀錄。

## 讀取路由（按需，沒有必讀清單）

```text
現在的狀態？        → CURRENT_STATE.md（讀頭部摘要就夠）
為什麼這樣設計？    → CURRENT_DECISIONS.md
每日播報／搜尋選路？→ AGENT_DEFINITION_MAP.md（推播/完整雷達/主題搜尋/內容/回測/社群渠道）
來源與查詢怎麼跑？  → SOURCE_LIBRARY_SPEC.md、configs/query_recipes.yml、sources/
新領域怎麼加？      → domains/README.md（複製 _template 填完即掛上）
潛力項目放哪？      → memory/potential_pool.md（蒐集階段不篩選）
改連動關係？        → schema/sync-matrix.json（唯一矩陣）
其他一切：直接動手。commit 時關口會接住你。
```

## 五條不變式（每條都有機器消費者）

```text
1. 動 CURRENT_STATE/CURRENT_DECISIONS 必附 reports/ 紀錄（hook 擋；SKIP_PROCESS_GATE=1 逃生）
2. 動 X → 應檢視 Y 清單自動出現（check-sync-matrix，提醒不擋）
3. 文件宣稱的路徑必須存在（check-doc-paths，提醒不擋）
4. 入口預算：AGENTS ≤4500、CLAUDE ≤1200、CURRENT_STATE 頭部 ≤8000（check-core 驗）
5. domains/ 領域包必須完整：domain_pack.json＋sources.json 必備欄位（check-domain-packs 驗）
```

## 完成的定義

機器檢查綠 ＋ 5 行人話收據：改了什麼／機器檢查／沒做什麼／會影響誰／你可以驗證。

## 雷達邊界（反覆踩過的坑，違反即重大品質事故）

```text
固定來源庫與固定查詢配方先跑，generic search 只是 fallback，且要在 coverage audit 揭露。
台灣新聞必須 source-backed；「台灣可能受影響」是推論，不得計入台灣新聞。
每則計數訊號必須有今日新增點；歷史重播無新增資料不計入 5+3。
social-first 來源必須 direct channel check；generic search 不算已檢查。
蒐集階段不預篩：新概念/新應用/新趨勢/新組合一律入 potential_pool；取捨只在輸出階段。
政策/法規/市場重大 claim 必須回查官方或數據來源；生成者 ≠ 判官 ≠ 簽核人。
Evidence 不經核可不成為 Memory；凍結歷史不是現況。
```

## 新規則准入

想加規則？先答「誰、在什麼時點、用什麼機器消費它？」
答不出 → 它是說明不是規則，寫進 CURRENT_DECISIONS.md 的 why 即可。

安裝關口（一次性）：`bash tools/install_hooks.sh`｜體檢：`bash check_mount_integrity.sh`
