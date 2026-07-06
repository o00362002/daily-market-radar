# CONTEXT_ROUTING｜daily-market-radar

## 1. Architecture Adoption

本 repo 獨立，掛載 `brain-core` 作為治理核心（2026-07-06 起）。

```text
Core repo: o00362002/brain-core
Core role: 治理原則（P1–P5）＋ 機器層（檢查器/hook/schema）來源
Runtime dependency: none（機器層已複製進本 repo，自足）
Content source of truth: daily-market-radar
舊母腦: Human-AI-Collaboration-Brain 已退役
```

架構問題參考 `brain-core`；專案內容問題以本 repo 為準。

---

## 2. Reports Loading Rule

歷史報告正確路徑為：

```text
reports/YYYY/YYYY-MM-DD.md
```

讀取順序：

```text
1. 先讀 reports/INDEX.md
2. 依 INDEX 讀最近 3–7 份 reports/YYYY/YYYY-MM-DD.md
3. 若 INDEX 無法讀取，嘗試直接讀本週與上週日期路徑
4. 若仍失敗，才標示「近期 reports 無法讀取，歷史回測可能不完整」
```

不得直接嘗試 `reports/YYYY-MM-DD.md` 後就判定歷史資料不存在。