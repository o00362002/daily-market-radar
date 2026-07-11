# daily-market-radar｜CURRENT_STATE

<!-- 頭部只保留現在成立的事實；歷史移至 reports/ 或 archive/。 -->

## 現況摘要

```text
掛載：brain-core child mount。
定位：全球每日事件情報雷達＋多領域趨勢／潛力訊號掃描＋產品與社群競品情報。
Active contract：config/runtime_contract.json（v2.1）。
Canonical source registry：config/source_registry.json。
Canonical competitor registry：config/competitor_registry.json。
Runtime：src/radar/ modular monolith；application 的所有可替換／外部 collaborator 都經十個 behavior Protocols 注入，並依賴 provider-neutral contracts/domain 與 pure deterministic pipeline/validation；concrete implementations 只由 composition root 選擇。
Validated boundary：RadarReportV2 與 WebArtifactV1 為 strict typed contract；report persistence、web projection、state checkpoint 與 publisher 都只接收 validated canonical values。
Profiles：daily_push 的首頁每領域最多精選 3 筆；Potential 資料層不截斷，完整候選池全部保留。full 輸出 run budget 內所有 qualified items。Profiles 定義最低地板而非上限，數量不是完整性證明。
Report domains：五個 canonical news domains，由 runtime contract 定義；policy_geopolitics 與退役 labor domain 以 alias 相容。configs/radars.yml 是細雷達模組／指標，不新增 report-domain quota。
Competitor Intelligence：產品與社群競品是跨領域投影，不建立第六新聞領域；同一事件仍只有一個 primary domain。固定名單與別名由 config/competitor_registry.json 管理，政策由 configs/competitor_intelligence.yml 管理。
Labor boundary：勞動、招聘、裁員、薪資與消費壓力預設只進固定指標面板，不建立完整新聞章節或配額；只有事件獨立符合 AI／全球市場／零售／科技門檻時，才依該主領域輸出一次。
Source model：一個真實來源一個 source_id；RSS/API/web/RSSHub/social 為 adapters；FRESHRSS_SEEDS.opml 為 generated projection。
Taiwan：direct evidence 與 implication 分離，推論不得計入直接台灣證據。
Scoring：importance、potential、confidence 分開；Major/Potential 由事件內容特徵主導，來源 top-down/bottom-up 只作輕量輔助，不可單獨決定分流。
Language：deterministic 系統敘事使用台灣繁體中文；非中文來源標題在無 AI 時保留原文。API-assisted 受約束輸出繁中，翻譯後仍保存原文標題供查核。
固定輸出：Product/Social Competitor Watch、Retail matrix、Crypto matrix、勞動與消費壓力 indicator-only row、三個 Structural Trend Indicators、coverage gaps、rejection counters、backtest。
```

## Production reality

```text
目前可驗證：deterministic fixture runtime、direct live RSS/Atom、RSS＋optional FreshRSS composite live collection、source registry validation、OPML drift、report contract、CLI smoke、SQLite durable document/event/delta/report/indicator/state/match/source-health storage、provider-neutral 7-strategy cross-day event resolution 與 20-type material-delta taxonomy、EventResolutionAuditV1、atomic UnitOfWork run-transaction（失敗 rollback、不覆蓋 last-valid-report）、transport-seam SSRF-guarded adapters、deterministic source-health state machine、feature-traced Retail/Crypto/Structural deterministic evaluators（資料不足即 insufficient，不造假趨勢）、fake-only application flow、replaceability/import/cycle architecture gates。
四種 evaluation modes（deterministic/auto/api-assisted/chat-assisted，預設 auto）已接線；AI 只讀 bounded provider-neutral context，輸出經 deterministic revalidation（不得捏造 URL/id/數值），invalid→retry once→deterministic fallback；evaluation cache＋cost/budget（超支→ai_budget_exhausted）；prepare-chat/import-chat content-addressed byte-stable 封包＋import 守門。deterministic 與 auto-無-key 均不 import AI。
Potential：事件以試點/原型/新應用/新商業模式/跨域組合/採用擴散/material delta 等內容特徵判斷；官方來源的早期應用仍可進 Potential，bottom-up 一般新聞不會只因來源角色被列為 Potential。所有 qualified potential items 保留於 report；首頁只做 projection 精選。
Competitor：canonical registry、固定查詢配方、watchlist、coverage checker、首頁競品摘要、獨立 competitors 頁與共用 web projection helper 已建立；目前仍由 validated report items 投影，尚未新增 typed competitor payload 到 RadarReportV2。
Web projection：validated report → typed immutable artifacts；同日 re-run 依 durable write order 取最後寫入，run_id 不參與時間排序。Astro dashboard 為繁中、zero-JS、Pages-compatible，首頁區分精選與完整候選池並保留原文查核。
Daily automation：daily-intelligence 以 --mode live 執行 direct RSS/Atom＋optional FreshRSS；cron '0 23 * * *' UTC＝07:00 台灣；durable radar-state branch 保存 compressed+checksum SQLite；Pages 只部署 validated artifact，並將 JSON artifacts 一併發佈於 /data/。
Reportability：以台灣日期錨定——事件「今日首見」或「今日有實質變化」即進當日報告；同日 re-run 不縮水（聯集），跨日 replay 仍抑制。Profiles 為最低地板（精簡版每日至少 3 重大、3 潛力、1 台灣；完整版至少 5、5、2），無上限；未達地板揭露 below_minimum_* degradation＋coverage gap，不用重播湊數。
收集：69 來源／54 RSS-capable／台灣 12，per-feed-limit 50；支援 RSS 2.0、RSS 1.0/RDF、Atom 與台灣時間正規化。2026-07-11 live probe 54 路徑零失敗；明細見同日 receipt。
Legacy archive：reports/2026/ 的人工報告經 project_legacy 投影至 /legacy/（明確標示非 RadarReportV2）；機器驗證歷史自 2026-07-11 起。
FreshRSS：設定 FRESHRSS_BASE_URL / FRESHRSS_USERNAME / FRESHRSS_API_PASSWORD 後，Google Reader inbox 會依 origin stream 映回 canonical source_id；缺 credentials、讀取失敗或 stream 無法映射都轉為 coverage gap，且不阻止 direct RSS。RSS 與 FreshRSS 重複 URL 在下游 document dedup 排除。
尚未完成：web/API/social、fixed queries/coverage retry 與 external discovery 接線；逐來源 health 及 fresh/backfill 分層；真實 AI key 驗證；typed competitor payload/history。
無 AI key 時不做外部標題機器翻譯，仍保留原文並明確顯示 deterministic 模式。
未執行來源或競品固定檢查必須成為 coverage gaps；目前仍不得宣稱完整全球新聞或完整競品覆蓋。
```

## 入口與權威

```text
AGENTS.md = 第一入口
CURRENT_STATE.md = 現況
CURRENT_DECISIONS.md = 已接受決策
config/runtime_contract.json = machine execution/output contract
config/source_registry.json = source identity contract
config/competitor_registry.json = competitor identity contract
AGENT_DEFINITION_MAP.md = 任務路由
DEPENDENCY_MAP.md = 人類可讀依賴與降級說明
schema/sync-matrix.json = 連動矩陣
```

## Validation entrypoints

```text
make validate
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli run-daily --mode fixture --date YYYY-MM-DD
PYTHONPATH=src python -m radar.cli run-daily --mode live-rss --date YYYY-MM-DD --database <database-path>
PYTHONPATH=src python -m radar.cli run-daily --mode live --date YYYY-MM-DD --database <database-path>
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
