# Execution Check — doc-paths 清理（2026-07-07）

```text
起因：owner 稽核兩腦治理狀況時發現 9 筆待審漂移，要求現在清。
分流：
  5 處＝規劃中/視需要才建立的路徑（memory/ 兩份日誌檔、SKILL.md 兩個範本檔）
    → 加 path-ok／規劃中尚未建立 標註（官方支援的明確豁免語法），不建空殼檔
  1 處＝rules/post_change_sync_protocol.md 引用 docs/MAINTENANCE_GUIDE.md
    → 標註為母腦舊制清單殘留，該檔本身是否仍適用已 spawn_task 交獨立任務判斷
    （retailops 同型殘留已標 Frozen History，radar 這份還沒走那一步）
結果：9 → 0，check-doc-paths 全綠；check-core 結構體檢仍綠（FAIL=0 WARN=0）。
【收據】
改了什麼：5 個檔案共 6 行加豁免標註（真正該建的檔案沒有一個是空造出來的）。
機器檢查：doc-paths 0 筆、check-core 綠。
沒做什麼：沒動 rules/post_change_sync_protocol.md 本體內容（是否整份歸檔待
  spawn_task 判斷，避免今天順手擴大成一次大改）；push 交你。
會影響誰：只有本 repo 六個檔案的行內註記；業務邏輯（訂閱源/推播）零影響。
你可以驗證：node tools/brain/check-doc-paths.js 看 FAIL=0。
```
