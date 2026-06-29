# Skill Index｜daily-market-radar

本索引用來讓 AI / Codex / Claude / GPT 在執行每日市場情報前，知道應呼叫哪些 skill spec，而不是直接跳到生成報告。

---

## 1. Daily Report Skill Chain

每日市場情報報告必須依序使用：

```text
1. read_context.skill.md
2. load_recent_reports.skill.md
3. run_indicator_tracking.skill.md
4. edge_case_discovery.skill.md
5. search_retry.skill.md
6. taiwan_mapping.skill.md
7. final_quality_gate.skill.md
```

---

## 2. Skill Responsibilities

| Skill | Purpose | Hard requirement |
|---|---|---|
| `read_context.skill.md` | 讀取 repo 入口、configs、memory、templates、workflow、loop | 不得假裝已讀 |
| `load_recent_reports.skill.md` | 依 `reports/INDEX.md` 與 `reports/YYYY/YYYY-MM-DD.md` 讀近期報告 | 不得只試錯誤路徑 |
| `run_indicator_tracking.skill.md` | 依 `configs/indicator_tracking.yml` 產出固定指標追蹤 | 每大桶需有狀態、方向、異常、來源、下一步 |
| `edge_case_discovery.skill.md` | 依 `configs/edge_case_discovery.yml` 抓全球特殊應用候選 | 至少 5 則、至少 3 領域 |
| `search_retry.skill.md` | 依 `configs/search_retry_protocol.yml` 對無資料雷達換搜尋方法 | 至少 3 種 retry |
| `taiwan_mapping.skill.md` | 將每個主領域映射到台灣訊號、關聯或資料缺口 | 不可只在最後集中一句 |
| `final_quality_gate.skill.md` | 檢查是否可標示為完整報告 | fail 時只能 partial |

---

## 3. Naming Compatibility

目前 repo 主要使用以下既有 skill 名稱：

```text
read_context.skill.md
edge_case_discovery.skill.md
search_retry.skill.md
```

若外部 prompt 使用以下別名，應映射到既有 skill：

```text
load_repo_context → read_context.skill.md
run_edge_case_discovery → edge_case_discovery.skill.md
run_search_retry → search_retry.skill.md
```

---

## 4. Hard Gate

不得在未完成以下 skill 狀態檢查時輸出完整報告：

```text
context_loaded_or_disclosed
recent_reports_attempted
indicator_tracking_present
edge_cases_at_least_5
edge_cases_at_least_3_domains
search_retry_for_no_data_radars
taiwan_mapping_per_major_domain
final_quality_gate_passed
```

任一項缺漏，報告必須標示為 partial。
