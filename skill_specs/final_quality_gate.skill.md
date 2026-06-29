# Skill Spec｜final_quality_gate

## Purpose

在每日市場情報送出前，檢查是否符合完整報告標準。

---

## Inputs

```text
preflight_status
indicator_tracking_status
edge_case_status
search_retry_status
recent_reports_status
taiwan_mapping_status
final_synthesis_status
```

---

## Required Checks

```text
context_loaded_or_disclosed
reports_index_attempted
recent_reports_attempted
indicator_tracking_present
edge_cases_at_least_5
edge_cases_at_least_3_domains
search_retry_for_no_data_radars
potential_frameworks_3_to_5_present
taiwan_mapping_per_major_domain
evidence_boundary_clear
post_report_review_present
```

---

## Output

```text
quality_gate_status: complete | partial | invalid
passed_checks:
failed_checks:
required_disclosure:
can_output_as_complete: true | false
```

---

## Rules

- 若 edge cases、search retry、indicator tracking、recent reports 任一缺漏，不得標示為完整報告。
- 若因工具限制無法完成，必須標示 partial 並列原因。
- 不得用「已檢查」取代 pass/fail 表。