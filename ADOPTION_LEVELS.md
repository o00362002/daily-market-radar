# Daily Market Radar｜ADOPTION_LEVELS

本檔定義 `daily-market-radar` 套用 GitHub AI Project Framework 的深度。

---

## 1. Repo Level

目前指定：

```text
Repo Level 2：Long-term AI Project
```

原因：本 repo 是長期維護的每日市場情報系統，重點是穩定入口層、固定雷達、記憶、模板、報告與回測，不需要預設升級成 Agent / Product System。

---

## 2. Level 2 適用範圍

Level 2 用於 root repo 的長期治理，包括：

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
research/
archive/
```

---

## 3. Module Level 規則

本 repo 目前不預設建立 Agent module。

若未來把某個雷達、報告產出流程或回測流程拆成 module，應先判斷 Module Level，而不是直接升級整個 repo。

建議：

| Module | 建議 Module Level | 備註 |
|---|---:|---|
| 單一 radar config | Module Level 1 | 多數只需設定檔與說明 |
| 搜尋 retry / 回測流程 | Module Level 2 | 若規則長期維護，可建立局部文件 |
| Agent 化市場情報系統 | 另行評估 Level 3 | 目前不做 |

---

## 4. Root 連動規則

若新增或調整 module，需檢查是否同步：

```text
README.md
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
configs/
memory/
templates/
reports/INDEX.md
```

---

## 5. 升級與降級影響

目前維持 Level 2。

升級到 Level 3 不應自動建立 Agent runtime、MCP server、SaaS backend 或產品化結構。若未來要升級，必須先確認是否真的有可委派 Agent、固定 Workflow、Skill、Tool 與 Loop。
