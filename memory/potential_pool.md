# 潛力池｜potential_pool

蒐集階段**全收不預篩**的潛力項目池。規則來源:`configs/edge_case_discovery.yml` 的
`capture_no_prefilter`;方法依據:`research/global_news_trend_projects_2026-07-06.md` §2(DEFRA 模式)。

```text
入池標準(任一即入池,不做價值判斷):
新概念 / 新應用 / 新場景 / 新商業模式 / 新組合(舊技術×新領域)/ 新趨勢苗頭 /
監管沙盒 / 研究原型 / 開發者工具 / 失敗與反面成本 / 社群弱訊號

不得以下列理由拒收:太小、證據弱、看起來不重要、主流媒體已報導(有新應用角度即收)、
與現有領域無關(跨領域正是潛力來源)。

篩選與計數只發生在輸出階段(5+3 閘門照舊);被輸出淘汰的項目仍留在池中,只改狀態。
```

## 欄位

| 欄位 | 說明 |
|---|---|
| date_added | 入池日期 |
| item | 一句話描述 |
| type | 新概念 / 新應用 / 新趨勢 / 新組合 / 其他 |
| domain | 所屬或最接近領域(可寫 cross_domain) |
| source | 可回查來源 |
| evidence | high / medium / low / unverified |
| status | new / watching / upgraded(升入正式訊號)/ faded(多週無後續)/ merged(併入他項) |
| last_review | 最後回顧日期 |

## 回顧規則

```text
每雙週(或每 10 份日報)做一次池內聚類回顧:
1. 重複出現的主題 → 聚成一條,狀態 upgraded 候選
2. 連續 4 週無新訊號 → faded(不刪除,保留紀錄)
3. 回顧結果記入 reports/backtests/
```

---

## 池

| date_added | item | type | domain | source | evidence | status | last_review |
|---|---|---|---|---|---|---|---|
