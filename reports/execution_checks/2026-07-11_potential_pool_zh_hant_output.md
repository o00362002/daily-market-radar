# Potential pool + zh-Hant output execution receipt

Date: 2026-07-11
Branch: `feat/potential-pool-zh-hant-output`

1. 改了什麼：Major/Potential 改為內容特徵主導；daily_push 保留全部潛力候選，首頁每領域只精選 3 筆；deterministic 說明文字改繁中，API-assisted 強制繁中並保存原文標題。
2. 機器檢查：新增 content-driven potential、候選不截斷、繁中 deterministic copy、AI 翻譯保留原文的單元測試；PR CI 為最終驗證來源。
3. 沒做什麼：沒有加入離線機器翻譯模型；無 AI key 時外部標題仍可能保留原文；沒有改變 evidence、event resolution 或 material-delta 邊界。
4. 影響誰：daily_push JSON 會包含全部合格 potential items；Astro 首頁新增精選與完整候選池；API/Chat 使用者看到繁中敘事並可回查原文。
5. 你可以驗證：執行 `make validate`、`python -m unittest tests.unit.test_potential_pool_and_translation`、`web/npm run build`，並檢查首頁候選池數量是否大於或等於精選數量。
