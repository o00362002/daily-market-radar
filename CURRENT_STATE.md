# daily-market-radar｜CURRENT_STATE

<!-- 頭部只保留現在成立的事實；歷史移至 reports/ 或 archive/。 -->

## 現況摘要

```text
掛載：brain-core child mount。
定位：全球每日事件情報雷達＋多領域趨勢／潛力訊號＋產品與社群競品情報。
Contracts：RadarReportV2（事實）、AIAnalysisV1（解讀）、WebArtifactV1（網站投影）。
設定權威：config/runtime_contract.json、config/ai_analysis.json、config/source_registry.json、config/competitor_registry.json、config/production_quality_gate.json。
Runtime：src/radar/ modular monolith；外部 collaborator 經 behavior Protocols 注入，concrete implementations 只由 composition root 選擇。
Validated boundary：AIAnalysisV1 只引用已驗證 report/event ids，不得改寫 RadarReportV2 或 deterministic indicator values。
Report domains：五個 canonical domains；labor 預設 indicator-only；競品採 cross-domain projection，不新增領域或重複計數。
Core structural indicators：k_shaped_ai_productivity_economy、ai_bubble_overinvestment、brand_market_polarization_and_true_vs_fake_segmentation；三項皆為每日必出主指標。
Indicator hierarchy：三個 structural indicators 是長期主層；AI／零售／Crypto／台灣／跨域／證據六項動能分數是 auxiliary signal panel，不得互相取代。
Taiwan：direct evidence 與 implication 分離；推論不得算成台灣直接證據。
Scoring：importance、potential、confidence 分開；來源角色不得單獨決定 Major/Potential。
Language：API/Chat-assisted 受約束輸出繁中並保留原文；無 AI 時保留原文並揭露 fallback，但 production AI 頁不得以 fallback 冒充成功更新。
Profiles：定義最低地板而非上限；所有 qualified items 保留，首頁只做可讀性精選。
```

## Production reality

```text
Collection：direct RSS/Atom＋optional FreshRSS composite live collection；來源 registry／OPML／health 可驗證，未接線的 web、API、social、external discovery 必須揭露為 gap。
Durability：SQLite 保存 document/event/delta/report/indicator/state/match/source-health；UnitOfWork 原子提交，radar-state branch 保存壓縮、checksum 與 last-good state；只有 production gate 通過的 daily run 才能覆寫 durable state。
Resolution：跨日事件以 deterministic 7-strategy matching 與 material-delta taxonomy 判定；同日 re-run 取當日聯集，跨日無新增不重播。
Evaluation：deterministic／auto／api-assisted／chat-assisted 已接線；AI 只讀 bounded context，輸出需重驗證，invalid/provider failure 安全降級；降級結果可供診斷與預覽，但不得覆蓋正式 AI 解讀頁。
Chat flow：prepare-chat 從 durable live state 產生 content-addressed 封包；import-chat 驗證成功後可寫回 state、建站與部署；fixture 預設不得覆蓋正式站。
AI analysis：AIAnalysisV1 產生翻譯、五域重點判讀與跨事件全球情境；/analysis 的閱讀順序為今日統整→五域重點判讀→未來 3–6 個月趨勢→三個核心結構指標→六個輔助訊號。未來趨勢不得逐則新聞改寫，必須引用跨事件來源並固定標示 3／6 個月條件式可能性；核心指標先展開細分指標、新聞簡述、支持／反向方向，再呈現 deterministic 總分。AI 不得改寫 deterministic 指標；provider/model/time/run/hash/prompt/schema/fallback 全留痕。
Production gate：正式部署要求 live ingestion、當日日期一致、event_id 唯一、總項目／Major 數量與 Major 比例不超過 config/production_quality_gate.json；AI 解讀必須是 api-assisted 或 chat-assisted，provider/model 必須存在、fallback=false，並且與同一 report_id/date 對齊。任一失敗時保留上一版 Pages、上傳診斷 artifact 並讓 Actions 顯示失敗。
Domains：文章在 normalize 後進入 deterministic content classifier，以標題／摘要／實體與來源 domain prior 判定五個 canonical domains；labor 與 policy 舊 alias 只映射至 global_markets_macro。
Competitor：registry 依海外直接 Action 系統、海外相鄰執行平台、台灣相鄰零售平台、通用執行底座與內容競品分組；身分只從 headline／today_delta 等事實欄位辨識，並以 requires_any 排除一般行銷、CRM、電商與通用 AI 噪音。若 RadarReportV2 沒有 typed competitor audit，頁面只能標示「固定來源待查」，不得把無匹配事件當成已查無更新。
Web：Astro static、zero-JS-first、Pages-compatible；事實層與 /analysis 解讀層分開，JSON artifacts 同步發佈於 /data/。
Automation：daily-intelligence 於 23:00 UTC 排程，目標在台灣 09:00 前完成，但 GitHub schedule 可延遲；daily 與 ai-analysis 都需通過 production gate 才能部署，共同使用 radar-daily concurrency lock。
Coverage：來源數量與輸出數量不是完整性證明；coverage gaps、failures、rejection counters、matrices、structural indicators 與 backtest 固定揭露。
Legacy：reports/2026/ 人工報告投影至 /legacy/，明確標示非 validated RadarReportV2。
尚未完成：逐來源 fresh/backfill 分層、真實 AI key 線上驗證、typed competitor audit/history、AI analysis 長期 repository/history、read-only「問雷達」MCP。
```

## 入口與驗證

```text
AGENTS.md = 第一入口
README.md = 專案能力與三個核心指標快速索引
CURRENT_STATE.md = 現況
CURRENT_DECISIONS.md = 已接受決策
docs/structural-indicators.md = 三個核心結構指標的人類可讀權威入口
configs/structural_trend_indicators.yml = 支持／反向證據與待查資料規格
config/production_quality_gate.json = 正式報告與 AI 解讀部署閘門
schema/sync-matrix.json = 連動矩陣

make validate
python tools/check_production_quality.py --report <latest.json> --analysis <ai-analysis/latest.json>
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli run-daily --mode fixture --date YYYY-MM-DD
PYTHONPATH=src python -m radar.cli run-daily --mode live --date YYYY-MM-DD --database <database-path>
PYTHONPATH=src python -m radar.analysis.cli --database <database-path> --mode deterministic
cd web && npm run types:check && npm run build
```

## 歷程｜Frozen v1 behavior

```text
fixed-count completion rules
six canonical news domains
labor as a standalone news chapter
split legacy source files as canonical identity
Markdown prompt as sole execution contract
```

These remain historical references only. Active completeness is coverage and contract based.
