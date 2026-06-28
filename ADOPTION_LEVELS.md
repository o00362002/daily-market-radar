# daily-market-radar｜ADOPTION_LEVELS

本檔定義 `daily-market-radar` 採用 Human-AI Collaboration Brain 架構的深度。

---

## 1. Repo Level

目前指定：

```text
Level 2 runtime-lite
```

原因：

```text
具備固定 workflow、configs、memory、templates、reports 與 loop checklist，但不需要升級成 Agent Product System。
```

---

## 2. Thin Mount

本 repo 採 thin mount，不完整複製母架構。

```text
Framework source: o00362002/Human-AI-Collaboration-Brain
Source of truth: daily-market-radar
```

---

## 3. Module Level 原則

Module 不應完整複製 root 入口層。Module 應繼承 root 規則，並用局部文件記錄任務、狀態、決策與依賴。

建議 module / area：

```text
configs / memory / templates / reports / radar rules / search retry / post-report review
```
