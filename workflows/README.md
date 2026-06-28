# Workflows

Workflow 是 Agent 執行每日情報任務時的一串固定流程。

## Daily Report

- `daily_radar_run.workflow`：每日情報掃描主流程
- `report_assembly.workflow`：報告組裝與段落排序
- `final_synthesis.workflow`：全指標總和彙總與最終判斷

## Search / Discovery

- `multi_language_search.workflow`：英文、繁中、簡中等多語搜尋
- `edge_case_discovery.workflow`：全球特殊應用、非主流案例與弱訊號搜尋
- `search_retry.workflow`：無資料或只抓到主流新聞時的 retry 流程

## Radar Workflows

- `crypto_radar.workflow`：加密潛力市場掃描
- `ai_application_radar.workflow`：AI 實際應用掃描
- `retail_trend_radar.workflow`：零售、品牌、消費、商圈與服飾趨勢掃描
- `technology_breakthrough_radar.workflow`：科技發展與突破掃描
- `taiwan_mapping.workflow`：台灣逐領域映射

## Review

- `cross_day_dedup.workflow`：跨日去重
- `missed_case_review.workflow`：漏抓回測
- `evidence_grading.workflow`：證據分級與來源品質判斷
