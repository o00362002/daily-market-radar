# CONTEXT_ROUTING｜daily-market-radar

## 1. Architecture Adoption

This repo is independent. It adopts `Human-AI Collaboration Brain` as an architecture method and AI collaboration pattern.

```text
Adopted architecture: Human-AI Collaboration Brain
Architecture repo: o00362002/Human-AI-Collaboration-Brain
Architecture role: project architecture method / documentation pattern / AI collaboration rules
Runtime dependency: none
Parent repo: none
Content source of truth: daily-market-radar
Repo Level: Level 2 runtime-lite
```

架構問題可參考 `Human-AI-Collaboration-Brain`；專案內容問題以本 repo 為準。

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