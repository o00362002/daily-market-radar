# Workflow｜Daily Market Report Runbook

本 workflow 將 RUNBOOK 拆成可執行步驟，讓每日市場情報不是「看過規則後自由生成」，而是逐項執行。

---

## Workflow ID

```text
daily_report_runbook
```

---

## Steps

### Step 1. read_context

呼叫：`skill_specs/read_context.skill.md`

輸出：

```text
已讀取檔案清單
無法讀取檔案清單
失敗原因
fallback 動作
```

---

### Step 2. load_recent_reports

呼叫：`skill_specs/load_recent_reports.skill.md`

規則：

```text
先讀 reports/INDEX.md
再讀最近 3–7 份 reports/YYYY/YYYY-MM-DD.md
不得用 reports/YYYY-MM-DD.md 作為唯一嘗試路徑
```

---

### Step 3. run_main_radar

依 configs 執行主雷達、多語言搜尋、跨領域觸發器與證據分級。

---

### Step 4. build_indicator_table

依 `configs/indicator_tracking.yml` 輸出固定指標追蹤總表。

---

### Step 5. run_edge_case_discovery

呼叫：`skill_specs/edge_case_discovery.skill.md`

硬性輸出：

```text
至少 5 則特殊應用 / 邊緣案例候選
至少 3 個領域
```

---

### Step 6. run_search_retry

呼叫：`skill_specs/search_retry.skill.md`

觸發條件：

```text
無資料
只有主流新聞
只有英文來源
只有大公司新聞
沒有特殊應用候選
```

---

### Step 7. generate_report

使用 templates 產出報告。

---

### Step 8. final_quality_gate

呼叫：`skill_specs/final_quality_gate.skill.md` 與 `loops/daily_report_quality_loop.yml`。

若 fail，報告必須標示為 partial。