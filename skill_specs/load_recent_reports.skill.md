# Skill Spec｜load_recent_reports

## Purpose

正確讀取近期歷史報告，支援跨日去重、漏抓回測與歷史脈絡延續。

---

## Required Path Rule

```text
reports/YYYY/YYYY-MM-DD.md
```

不得只嘗試：

```text
reports/YYYY-MM-DD.md
```

---

## Steps

1. 讀取 `reports/INDEX.md`。
2. 從 INDEX 取得最近 3–7 份報告路徑。
3. 依 `reports/YYYY/YYYY-MM-DD.md` 讀取近期報告。
4. 若 INDEX 不存在，依今天日期推算本週與上週路徑。
5. 若仍失敗，標示歷史資料讀取不完整。

---

## Output

```text
reports_index_loaded: true | false
recent_reports_attempted:
recent_reports_loaded:
missing_report_paths:
history_context_status: complete | partial | unavailable
impact_on_backtest:
```

---

## Rules

- 找不到近期 reports 時，不得說 repo 沒有歷史報告，除非已嘗試 INDEX 與年份路徑。
- 歷史讀取失敗時，報告中的跨日去重與漏抓回測必須標示可能不完整。