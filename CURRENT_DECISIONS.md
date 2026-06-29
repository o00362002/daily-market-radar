# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-06-29

---

## 2026-06-29：小眾潛力候選訊號與歷史去重規則

### Decision

每日播報的「今日候選訊號」改為「今日小眾潛力候選訊號」。候選訊號不得只是主流新聞摘要，必須優先抓小眾、早期、地方試點、小公司、研究原型、開發者工具、特殊商業模式、產業邊緣案例或尚未被主流市場充分定價的弱訊號。

每個核心領域每日需嘗試抓 3 則小眾潛力候選訊號，並附可回查來源。若某領域今日沒有合格候選，需明確寫「無合格候選更新」，不得用大眾新聞硬補。

每日輸出前必須檢查近期歷史報告。已播過的事件不得重複重播，除非有新官方公告、新數據、新資金流、新監管進展、新企業導入、新就業證據、新台灣映射，或候選訊號升級 / 降級。

### Reason

使用者希望每日播報維持「大到小、上到下」的完整全球雷達，同時避免候選訊號被主流新聞吃掉。候選訊號的價值在於補主流雷達盲區，而不是重述大眾新聞。

### Result

後續需同步更新：

```text
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
templates/daily_report_template.md
```

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
