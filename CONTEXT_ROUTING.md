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

## 2. Default Minimal Read

```text
PROJECT_OS_MOUNT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
ADOPTION_LEVELS.md
CONTEXT_ROUTING.md
```

---

## 3. Task Routing

| Task Type | Task Level | Read First | Read If Needed | Do Not Read By Default |
|---|---:|---|---|---|
| quick_answer | T0 | README.md, PROJECT_OS_MOUNT.md | HIGH_LEVEL_INDEX.md | archive/ |
| status_check | T1 | CURRENT_STATE.md, ADOPTION_LEVELS.md | PROJECT_MAP.md | archive/ |
| decision_trace | T2 | CURRENT_DECISIONS.md, ADOPTION_LEVELS.md | reports/, research/ | full modules |
| architecture_change | T3 | PROJECT_MAP.md, CURRENT_STATE.md, CURRENT_DECISIONS.md, ADOPTION_LEVELS.md | adopted architecture specs | archive/ |
| module_work | T2 | PROJECT_MAP.md, CURRENT_STATE.md | target module docs | unrelated modules |
| tool_or_provider | T3 | ADOPTION_LEVELS.md, tools/, data_contracts/ | related module docs | unrelated reports |
| runtime_execution | T4 | workflow / agent / loop docs | templates / approval / reports | archive/ |

---

## 4. Module Routing

```text
每日報告：SYSTEM_PROMPT.md, configs/, memory/, templates/, reports/
雷達設定：configs/
漏抓與 watchlist：memory/
歷史報告：reports/
輸出格式：templates/
```

---

## 5. Escalation Rule

```text
資訊不足 → 加讀 CURRENT_DECISIONS.md
涉及架構 → 加讀 PROJECT_MAP.md / ADOPTION_LEVELS.md
涉及 module → 只讀目標 module
涉及工具 → 加讀 tools / data_contracts
涉及執行 → 加讀 workflow / loop / approval
仍不足 → 明確說明缺口，不要自行假設
```

---

## 6. Human Maintenance Rule

人類可以調整任務類型、任務等級、讀取清單與升級規則。調整後需同步檢查：

```text
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
ADOPTION_LEVELS.md
PROJECT_OS_MOUNT.md
```
