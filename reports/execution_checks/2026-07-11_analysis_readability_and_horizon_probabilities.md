# 2026-07-11｜AI 解讀閱讀順序與 3／6 個月可能性

## 問題

實際頁面先顯示結構指標，且把大量 support/counter event IDs 直接鋪在卡片上。使用者尚未讀完今日內容，就先看到難以理解的機器識別碼與兩組分數。未來趨勢也只有 days/weeks/months/years 類別和 confidence，沒有直接回答未來 3 個月與 6 個月的可能性。

## 決定

```text
今日統整
→ 重點判讀
→ 未來趨勢情境
→ 三個核心結構趨勢指標
→ 六個輔助訊號
```

1. 完整 provenance 移到頁面後段摺疊區，標題下只保留 provider/model/time。
2. 每個未來趨勢顯示 3 個月與 6 個月條件式可能性。
3. 可能性不是統計校準機率，也不是投資報酬預測；以 confidence、stage、direction 為基礎，扣除 counterevidence 與 uncertainty。
4. 每個核心結構指標預設只顯示名稱、方向、一個淨趨勢分數與 one_sentence_read。
5. 淨趨勢分數只作可讀性投影：`50 + (support_score - counter_score) / 2`。50 代表正反接近；insufficient 顯示 N/A。
6. 原始 support/counter score、confidence、signal IDs、missing data、next verification 與 evaluation mode 保留在摺疊細節，沒有刪除或改寫 canonical data。

## 不變式

- RadarReportV2 與 AIAnalysisV1 JSON 契約不因此次純呈現調整而改變。
- AI 仍不得修改三個 deterministic structural indicators。
- raw event/signal IDs 仍可稽核，但不再阻塞一般閱讀。
- 六個 auxiliary signals 仍在三個核心指標之後。

## 驗證

- `tests/unit/test_analysis_page_readability.py` 固定區塊順序、3／6 個月標籤與 signal IDs 摺疊邊界。
- `runtime-check`
- `web-check`，包含 Astro build 與 bundle budget
- `mount-check`
- 合併後確認 public `/analysis/` 已部署新順序與可能性面板。
