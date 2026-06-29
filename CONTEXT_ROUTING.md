# daily-market-radar｜CONTEXT_ROUTING

本檔定義每日市場情報執行時的脈絡讀取順序、讀取深度與 fallback 規則。

---

## 1. Architecture Adoption

```text
Adopted architecture: Human-AI Collaboration Brain
Architecture repo: o00362002/Human-AI-Collaboration-Brain
Architecture role: project architecture method / documentation pattern / AI collaboration rules
Runtime dependency: none
Parent repo: none
Content source of truth: daily-market-radar
Repo Level: Level 2 Runtime-Lite Brain
Mount mode: thin mount + Execution Edge
```

架構問題可參考 `Human-AI-Collaboration-Brain`；專案內容、每日雷達、搜尋規格與報告輸出以本 repo 為準。

---

## 2. Source of Truth Priority

若文件互相衝突，依以下順序判斷：

```text
1. SYSTEM_PROMPT.md
2. RUNBOOK.md
3. CHECKLIST.md
4. configs/*.yml / configs/*.md
5. memory/*.md
6. templates/*.md
7. reports/INDEX.md + recent reports/YYYY/YYYY-MM-DD.md
8. README.md / PROJECT_MAP.md / HIGH_LEVEL_INDEX.md / CURRENT_STATE.md / CURRENT_DECISIONS.md
```

README 與入口層負責導航；每日實際執行以 RUNBOOK / CHECKLIST / configs 為硬規則。

---

## 3. Required Context Loading

每日報告開始前必須讀取：

```text
SYSTEM_PROMPT.md
README.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
ADOPTION_LEVELS.md
CONTEXT_ROUTING.md
RUNBOOK.md
CHECKLIST.md
configs/radars.yml
configs/triggers.yml
configs/evidence.yml
configs/source_strategy.md
configs/indicator_tracking.yml
configs/technology_development.yml
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
memory/missed_cases.md
memory/watchlist.md
reports/INDEX.md
templates/daily_report_template.md
templates/final_synthesis_template.md
workflows/daily_report_runbook.md
loops/daily_report_quality_loop.yml
skill_specs/*.skill.md
```

---

## 4. Reports Loading Rule

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

---

## 5. Context Scope

每日報告只需讀取近期 reports，不需讀取全部歷史報告。除非使用者要求回測特定事件，才擴大讀取範圍。

---

## 6. Failure Disclosure

若任何必讀檔案無法讀取，必須在報告最上方列出：

```text
已讀取：...
無法讀取：...
影響：...
補救：使用哪個 fallback 規則
```

不得寫成籠統的「部分資料無法讀取」後不說明原因。