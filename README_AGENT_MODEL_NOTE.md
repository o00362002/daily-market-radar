# Daily Market Radar｜Agent Model Note

本 repo 已開始套用 Agent / Workflow / Skill / Tool / Loop 模型。

新增索引：

```text
AGENT_DEFINITION_MAP.md
AI_AGENT_MODEL_ADOPTION_PLAN.md
workflows/README.md
skill_specs/README.md
tools/README.md
loops/README.md
```

## 使用方式

原本入口層仍維持：

```text
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
README.md
```

若任務涉及每日情報流程、雷達分工、搜尋策略、漏抓回測或報告組裝，再讀 Agent model 檔案。

## 核心邊界

- Web search 是 Tool，不是 Agent。
- 雷達主題可以是 Agent，但單一指標不是 Agent。
- configs 是規則，不是 Agent。
- reports 是歷史輸出，不是 Agent。
