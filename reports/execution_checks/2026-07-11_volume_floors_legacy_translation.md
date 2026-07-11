# Volume, Floors, Legacy Archive & Translation Hardening

Branch: `feat/volume-floors-translation` (base `main`)

## 問題診斷（以實際 live 資料驗證）

從 radar-state branch 還原當日 DB：2026-07-11 三次執行分別產出 12 → 7 → 3 items —— 每次
re-run 都把「上一次 run 已見過」的事件視為無實質變化而丟棄，且覆蓋當日報告（使用者看到的
「今天才 3 篇」）。另外：33 個來源只有 11 個有 RSS adapter（15 個台灣來源全部沒有 → 台灣 0 篇）；
major 每領域上限 3 導致 165 個新事件只剩 12 篇；網站 history 只有 2026-07-11（radar-state 當日
才建立），35 篇 2026-05-30 起的人工報告不在站上。

## 改了什麼

1. **同日聯集（最大資訊量修復）**：`event_is_reportable_for_date` —— 事件只要「今日首見」或
   「今日有實質變化」就進當日報告，re-run 不再縮水（驗證：7→7→7，原 12→7→3）；跨日 replay
   仍然抑制（隔日 0 篇）。日期錨定使用台灣時區（排程 07:00 TW = 前一日 23:00 UTC，UTC 比對會漏）。
2. **地板取代天花板**：profiles 改為最低數量 —— 精簡版每日至少 3 重大、3 潛力、1 台灣；完整版
   至少 5 重大、5 潛力、2 台灣；**有多的可以超過（無上限，天花板全部移除）**。未達地板不會失敗、
   不得用歷史重播湊數，而是揭露 below_minimum_* degradation + coverage gap（status=partial）。
   驗證器改為「短缺必須揭露」而非「超量即失敗」。
3. **收集量**：新增 9 條**本機實測可用**的 RSS feed（中央社×3、經濟日報×2、區塊勢、Vogue Taiwan、
   Fed press、arXiv cs.AI）→ RSS 來源 11→17，台灣 RSS 0→4；per-feed-limit 20→50、timeout 12→20。
   實測失敗者（工商時報、加密城市、金管會、TWSE RSS）誠實不加。
4. **歸檔上站**：`project_legacy` 把 reports/2026/ 的 35 篇人工報告投影為 `/legacy/` 頁面
   （33 篇有效日期檔＋index；README/INDEX 跳過；同日變體各自保留）。清楚標示「對話歸檔，
   非 validated RadarReportV2」；history 頁註明機器驗證歷史自 2026-07-11 起。build 15→47 頁。
5. **AI 翻譯**：確認 main 已實作（zh-Hant prompt、today_delta 提案、chat 指引）——設定
   `OPENAI_API_KEY` 即生效。本次補：語言守門（長敘述無 CJK → 拒收 → retry → deterministic
   fallback）、openai_provider 首個測試檔（prompt 契約鎖定）、chat INSTRUCTIONS zh-Hant 斷言。
6. **JSON artifacts 上站**：build 後複製 artifacts 到 dist/data/，修復「下載完整報告 JSON」404。

## 機器驗證

- 193 tests 綠（+14：同日 re-run 回歸、地板揭露、legacy 投影×6、openai provider×7…）。
- E2E：同日 ×3 穩定 7 篇；隔日 replay 0 篇＋三項 below_minimum 揭露；registry 驗證＋OPML
  byte-stable；export 52 artifacts；`types:check` 同步；Astro build 47 頁、0 JS、CSS 7.2KB。
- Registry diff 純新增（9 adapters，其餘 byte-identical）。

## 邊界

- 地板是揭露目標：新聞真的不夠時報告標 partial，不造假湊數（AGENTS 不變式）。
- 新 feed 標 route_status=live_probe_verified_2026_07_11；後續由 source health 持續監測。
- AI 翻譯需 owner 設定 OPENAI_API_KEY 後才會在 live 頁生效。
