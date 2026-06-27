# Daily Market Radar｜AI Project OS Adoption Plan

本檔規劃 `daily-market-radar` 如何套用 `Reference-Implementation-of-AI-Project-Operating-System`。

---

## 1. 目前已具備

```text
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
README.md
configs/
memory/
templates/
reports/
archive/
```

此 repo 已具備 AI Project OS 的核心入口層。

---

## 2. 對照母架構

| AI Project OS 模組 | 本 repo 對應 | 狀態 |
|---|---|---|
| Entry Layer | 根目錄六大入口檔 | 已具備 |
| High Level Index | `HIGH_LEVEL_INDEX.md` | 已新增 |
| Rules | `SYSTEM_PROMPT.md`、`configs/` | 已具備 |
| Reports | `reports/` | 已具備 |
| Templates | `templates/` | 已具備 |
| Loops | `memory/missed_cases.md`、報告回測面板 | 可再標準化 |
| Research | 尚未獨立 | 可新增 |

---

## 3. 下一階段建議

1. 將 `HIGH_LEVEL_INDEX.md` 納入所有入口讀取順序。
2. 新增 `research/`，保存方法論研究與公開參考。
3. 規則採納後，再同步到 `SYSTEM_PROMPT.md`、`configs/`、`templates/`、`CURRENT_DECISIONS.md`。
4. 可考慮新增 `loops/`，把回測與漏抓檢查標準化。

---

## 4. 建議結構

```text
daily-market-radar/
├─ SYSTEM_PROMPT.md
├─ PROJECT_MAP.md
├─ HIGH_LEVEL_INDEX.md
├─ CURRENT_STATE.md
├─ CURRENT_DECISIONS.md
├─ README.md
├─ configs/
├─ memory/
├─ templates/
├─ reports/
├─ research/
├─ loops/
└─ archive/
```

---

## 5. 保留原則

- `reports/` 是歷史報告與回測依據。
- `configs/` 是結構化規則來源。
- `templates/` 是輸出格式來源。
- `memory/` 是漏抓與觀察清單。
- `HIGH_LEVEL_INDEX.md` 只做高階索引，不放完整細節。
