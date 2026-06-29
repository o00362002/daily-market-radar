# daily-market-radar｜CURRENT_DECISIONS

最後更新：2026-06-29

---

## 2026-06-29：每日訊號硬閘門，大型重要新聞 5 則 + 小眾候選 3 則

### Decision

每日正式播報必須同時滿足兩個最低量：

```text
每個核心領域至少 5 則大型重要新聞 / 主流重大訊號
每個核心領域至少 3 則小眾潛力候選訊號
6 個核心領域合計每日最低 30 則大型重要新聞 + 18 則小眾潛力候選訊號
```

此規則只可多不可少。大型重要新聞與小眾潛力候選訊號是兩個不同層級，不可互相替代：

- 不得用大型重要新聞假裝已完成小眾候選訊號。
- 不得用小眾候選訊號補足大型重要新聞最低量。
- 若任一核心領域未達 5 + 3，必須逐領域至少 retry 3 種搜尋方法。
- 若 retry 後仍不足，必須明確標示「未通過每日訊號硬閘門」，不能寫成正式完整播報。

### Reason

使用者指出前次播報不是只有「小眾候選未達標」，而是每個核心領域都沒有完整輸出 3 則小眾候選；並進一步確認每日播報基本規則應為「大型重要新聞每領域 5 則，小眾候選每領域 3 則」，只可多不可少。

此修正避免三種錯誤：

1. 報告退化成少量新聞摘要。
2. 用主流大新聞硬補小眾候選。
3. 用小眾候選取代主流重大訊號，造成覆蓋不足。

### Result

已同步或需同步檢查：

```text
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
templates/daily_report_template.md
SYSTEM_PROMPT.md
memory/missed_cases.md
reports/INDEX.md
```

---

## 2026-06-29：小眾潛力候選訊號與歷史去重規則

### Decision

每日播報的「今日候選訊號」改為「今日小眾潛力候選訊號」。候選訊號不得只是主流新聞摘要，必須優先抓小眾、早期、地方試點、小公司、研究原型、開發者工具、特殊商業模式、產業邊緣案例、失敗案例、反面成本或尚未被主流市場充分定價的弱訊號。

每個核心領域每日需嘗試抓 3 則小眾潛力候選訊號，並附可回查來源。若某領域今日沒有合格候選，需明確寫「無合格候選更新」，不得用大眾新聞硬補。

每日輸出前必須檢查近期歷史報告。已播過的事件不得重複重播，除非有新官方公告、新數據、新資金流、新監管進展、新企業導入、新就業證據、新台灣映射，或候選訊號升級 / 降級。

整體輸出必須維持「大到小、上到下」：上層結構 → 中層變化 → 具體事件 → 小眾潛力候選 → 指標驗證 → 台灣 / 使用者映射 → 下一步追蹤。

### Reason

使用者希望每日播報維持完整全球雷達，同時避免候選訊號被主流新聞吃掉。候選訊號的價值在於補主流雷達盲區，而不是重述大眾新聞。

### Result

已同步或需同步檢查：

```text
SYSTEM_PROMPT.md
configs/edge_case_discovery.yml
configs/search_retry_protocol.yml
templates/daily_report_template.md
memory/missed_cases.md
reports/INDEX.md
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
