# Web UI — GitHub-style sidebar redesign

Branch: `feat/web-sidebar-redesign` (base `main`)

## 改了什麼 (What changed)

- **左側選單**：導覽從頂部橫列改為固定左側 sidebar（264px、sticky、獨立捲動），品牌區＋
  6 個選單項（符號＋中文＋英文副標），active 狀態以 GitHub 式左側藍色豎條＋粗體標示，
  由 build-time pathname 推導（reports/* 歸 History）。行動版（≤900px）自動收合為頂部
  水平捲動列——純 CSS，維持 zero-JS。
- **GitHub Primer 風格重製**（時尚簡約）：淺色為預設、`prefers-color-scheme` 自動深色；
  Primer 色票（#f6f8fa/#d0d7de/#0969da…、dark #0d1117/#30363d/#4493f8…）；卡片改
  Primer Box（1px 邊框、6px 圓角）；badge 改 GitHub label 藥丸（色文字＋色邊框，仍保留
  文字＋符號、不只靠顏色）；表格加表頭底色與 hover；KPI 磁磚化；空狀態虛線框。
- **只動視覺層**：僅 `web/src/layouts/Base.astro` 與 `web/src/styles/global.css`（外加
  Base 內一行 pathname 正規化修正）；所有 class 名不變，頁面零改動；資料層／契約／
  pipeline／workflow 全部未動。

## 機器驗證 (Verified)

- `npm run build`：15 頁全數建置成功；`types:check` 同步。
- Budgets：client JS **0 bytes**（zero-JS 不變）、CSS 6.8KB ≤ 40KB。
- 每頁恰好一個 `aria-current="page"`（含首頁與 reports/* 深層頁）。
- Preview 實測截圖：light／dark／desktop（sidebar）／mobile（頂部收合列）皆正常。
- Python 測試 176 綠（未動、僅 sanity）。

## 沒做什麼 (Out of scope)

- 未改任何頁面內容結構、資料契約、pipeline 或 workflow。
