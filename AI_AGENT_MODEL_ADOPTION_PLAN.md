# Daily Market Radar｜Agent Model Adoption Plan

本檔說明 `daily-market-radar` 如何套用 Agent / Workflow / Skill / Tool / Loop 模型。

---

## 1. 新增檔案

```text
AGENT_DEFINITION_MAP.md
workflows/README.md
skill_specs/README.md
tools/README.md
loops/README.md
```

---

## 2. 目的

將每日市場情報流程從單一報告生成，拆成可檢查的情報作業系統：

```text
Radar Agents
→ Workflows
→ Skills
→ Tools
→ Loops
```

---

## 3. 不改變的原則

- 本 repo 仍以 `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` 為入口層。
- Agent model 只補充責任分層，不取代既有 configs / memory / templates / reports。
- Web search 是 Tool，不是 Agent。
- 每日報告仍需證據分級、來源、跨日去重與漏抓回測。

---

## 4. 下一步

1. 將 `AGENT_DEFINITION_MAP.md` 加入 README 與 PROJECT_MAP。
2. 將固定雷達逐步整理成 Agent spec。
3. 將漏抓回測整理成正式 loop。
4. 將常用搜尋策略整理成 reusable skills。
