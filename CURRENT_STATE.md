# daily-market-radar｜CURRENT_STATE

<!-- 頭部只保留現在成立的事實；歷史移至 reports/ 或 archive/。 -->

## 現況摘要

```text
掛載：brain-core child mount。
定位：全球每日事件情報雷達＋多領域趨勢／潛力訊號＋產品與社群競品情報。
Contracts：RadarReportV2（事實）、AIAnalysisV1（解讀）、WebArtifactV1（網站投影）。
設定權威：config/runtime_contract.json、config/ai_analysis.json、config/source_registry.json、config/competitor_registry.json。
Runtime：src/radar/ modular monolith；外部 collaborator 經 behavior Protocols 注入，concrete implementations 只由 composition root 選擇。
Validated boundary：AIAnalysisV1 只引用已驗證 report/event ids，不得改寫 RadarReportV2 或 deterministic indicator values。
Report domains：五個 canonical domains；labor 預設 indicator-only；競品採 cross-domain projection，不新增領域或重複計數。
Core structural indicators：k_shaped_ai_productivity_economy、ai_bubble_overinvestment、brand_market_polarization_and_true_vs_fake_segmentation；三項皆為每日必出主指標。
Indicator hierarchy：三個 structural indicators 是長期主層；AI／零售／Crypto／台灣／跨域／證據六項動能分數是 auxiliary signal panel，不得互相取代。
Taiwan：direct evidence 與 implication 分離；推論不得算成台灣直接證據。
Scoring：importance、potential、confidence 分開；來源角色不得單獨決定 Major/Potential。
Language：API/Chat-assisted 受約束輸出繁中並保留原文；無 AI 時保留原文並揭露 fallback。
Profiles：定義最低地板而非上限；所有 qualified items 保留，首頁只做可讀性精選。
```

## Production reality

```text
Collection：direct RSS/Atom＋optional FreshRSS composite live collection；來源 registry／OPML／health 可驗證，未接線的 web、API、social、external discovery 必須揭露為 gap。
Durability：SQLite 保存 document/event/delta/report/indicator/state/match/source-health；UnitOfWork 原子提交，radar-state branch 保存壓縮、checksum 與 last-good state。
Resolution：跨日事件以 deterministic 7-strategy matching 與 material-delta taxonomy 判定；同日 re-run 取當日聯集，跨日無新增不重播。
Evaluation：deterministic／auto／api-assisted／chat-assisted 已接線；AI 只讀 bounded context，輸出需重驗證，invalid/provider failure 安全降級。
Chat flow：prepare-chat 從 durable live state 產生 content-addressed 封包；import-chat 驗證成功後可寫回 state、建站與部署；fixture 預設不得覆蓋正式站。
AI analysis：AIAnalysisV1 產生翻譯、跨事件統整與條件式未來趨勢；/analysis 的閱讀順序為今日統整→重點判讀→未來趨勢→三個核心結構指標→六個輔助訊號。每項未來趨勢顯示 3 個月與 6 個月條件式可能性；核心指標預設只顯示一個淨趨勢分數與一句解讀，完整 signal ids、支持／反向分數、缺口與驗證點收進摺疊細節。AI 不得改寫 deterministic 指標；provider/model/time/run/hash/prompt/schema/fallback 全留痕。
Web：Astro static、zero-JS-first、Pages-compatible；事實層與 /analysis 解讀層分開，JSON artifacts 同步發佈於 /data/。
Automation：daily-intelligence 每日 07:00 台灣執行 live pipeline；ai-analysis 在 daily/import 成功後產生解讀層並重新部署；共同使用 radar-daily concurrency lock。
Coverage：來源數量與輸出數量不是完整性證明；coverage gaps、failures、rejection counters、matrices、structural indicators 與 backtest 固定揭露。
Legacy：reports/2026/ 人工報告投影至 /legacy/，明確標示非 validated RadarReportV2。
尚未完成：逐來源 fresh/backfill 分層、真實 AI key 線上驗證、typed competitor history、AI analysis 長期 repository/history、read-only「問雷達」MCP。
```

## 入口與驗證

```text
AGENTS.md = 第一入口
README.md = 專案能力與三個核心指標快速索引
CURRENT_STATE.md = 現況
CURRENT_DECISIONS.md = 已接受決策
docs/structural-indicators.md = 三個核心結構指標的人類可讀權威入口
configs/structural_trend_indicators.yml = 支持／反向證據與待查資料規格
schema/sync-matrix.json = 連動矩陣

make validate
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