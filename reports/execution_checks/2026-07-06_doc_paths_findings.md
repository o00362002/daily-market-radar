# Doc-Path 首掃發現（2026-07-06 掛載時記錄，待 owner 審）

```text
advisory 檢查器首掃「文件宣稱路徑不存在」清單——既有內容漂移，掛載方不代修。
處理選項：建檔補齊／改引用／該行加「歷史/日後/path-ok」豁免。
```

    FAIL  CURRENT_DECISIONS.md:69 引用的路徑不存在：memory/source_health_log.json
    FAIL  CURRENT_DECISIONS.md:69 引用的路徑不存在：memory/topic_coverage_log.json
    FAIL  CURRENT_DECISIONS.md:185 引用的路徑不存在：workflows/daily_execution_gate.md
    FAIL  CURRENT_DECISIONS.md:216 引用的路徑不存在：workflows/daily_execution_gate.md
    FAIL  DEPENDENCY_MAP.md:151 引用的路徑不存在：memory/source_health_log.json
    FAIL  DEPENDENCY_MAP.md:151 引用的路徑不存在：memory/topic_coverage_log.json
    FAIL  README.md:118 引用的路徑不存在：sources/configs/memory/templates/reports
    FAIL  SOURCE_LIBRARY_SPEC.md:327 引用的路徑不存在：memory/source_health_log.json
    FAIL  SOURCE_LIBRARY_SPEC.md:328 引用的路徑不存在：memory/topic_coverage_log.json
    FAIL  configs/source_routing_rules.yml:108 引用的路徑不存在：memory/source_health_log.json
    FAIL  configs/source_routing_rules.yml:109 引用的路徑不存在：memory/topic_coverage_log.json
    FAIL  rules/post_change_sync_protocol.md:52 引用的路徑不存在：docs/MAINTENANCE_GUIDE.md
    FAIL  skills/daily-broadcast-github-sync/SKILL.md:90 引用的路徑不存在：configs/search_model_adjustments.yml
    FAIL  skills/daily-broadcast-github-sync/SKILL.md:92 引用的路徑不存在：templates/post_broadcast_correction_template.md
    Result: files=75 path-refs=283 FAIL=14

Result: files=75 path-refs=283 FAIL=14
