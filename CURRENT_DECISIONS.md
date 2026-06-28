# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-06-28

---

## 2026-06-28：指定 repo Level 與 thin mount 架構

### Decision

本 repo 指定為：

```text
Level 2 runtime-lite
```

並以 `Human-AI-Collaboration-Brain` 作為 framework source，採 thin mount。

### Reason

```text
具備固定 workflow、configs、memory、templates、reports 與 loop checklist，但不需要升級成 Agent Product System。
```

### Result

後續新增或升級 module / workflow / tool / provider / data contract 時，需檢查入口層是否同步。
