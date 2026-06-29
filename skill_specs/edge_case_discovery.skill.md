# Skill Spec｜edge_case_discovery

## Purpose

確保每日報告固定抓取全球特殊應用、非主流案例、地方試點、早期商業模式、研究原型、開發者工具與社群弱訊號。

---

## Canonical Config

```text
configs/edge_case_discovery.yml
```

---

## Minimum Output

```text
at least 5 candidates
at least 3 domains
```

每則候選必須包含：

```text
候選事件
地區 / 領域
來源類型
為什麼特別
為什麼可能重要
證據等級
不能下的結論
台灣 / 使用者映射
下一步驗證
```

---

## Search Domains

```text
AI agents and workflow
technology development
crypto / blockchain
retail / consumer / social
labor / consumption pressure
```

---

## Rules

- 低證據訊號不得刪除，只能標示為候選或未證實。
- 不能把主流大公司新聞假裝成 edge case。
- 若不足 5 則，必須啟動 `search_retry`。
- 若仍不足，報告必須標示 partial，並說明缺哪個領域。