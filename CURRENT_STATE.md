# daily-market-radar｜CURRENT_STATE

<!-- 頭部只保留現在成立的事實；歷史移至 reports/ 或 archive/。 -->

## 現況摘要

```text
掛載：brain-core child mount。
定位：全球每日事件情報雷達＋多領域趨勢與潛力訊號掃描。
Active contract：config/runtime_contract.json。
Canonical source registry：config/source_registry.json。
Runtime：src/radar/ modular monolith；application 的所有可替換／外部 collaborator 都經十個 behavior Protocols 注入，並依賴 provider-neutral contracts/domain 與 pure deterministic pipeline/validation；concrete implementations 只由 composition root 選擇。
Validated boundary：RadarReportV2 與 WebArtifactV1 為 strict typed contract；report persistence、web projection、state checkpoint 與 publisher 都只接收 validated canonical values。
Profiles：daily_push 的 Major 每領域最多 3 筆；Potential 資料層不截斷，首頁每領域精選 3 筆但完整候選池全部保留。full 輸出 run budget 內所有 qualified items。數量不是完整性證明。
Report domains：六個 canonical domains，由 runtime contract 定義；configs/radars.yml 是細雷達模組，不新增 report-domain quota。
Source model：一個真實來源一個 source_id；RSS/API/web/RSSHub/social 為 adapters；FRESHRSS_SEEDS.opml 為 generated projection。
Taiwan：direct evidence 與 implication 分離，推論不得計入直接台灣證據。
Scoring：importance、potential、confidence 分開；Major/Potential 由事件內容特徵主導，來源 top-down/bottom-up 只作輕量輔助，不可單獨決定分流。
Language：deterministic 系統敘事使用台灣繁體中文；非中文來源標題在無 AI 時保留原文。API-assisted 受約束輸出繁中，翻譯後仍保存原文標題供查核。
固定輸出：Retail matrix、Crypto matrix、三個 Structural Trend Indicators、coverage gaps、rejection counters、backtest。
```

## Production reality

```text
目前可驗證：deterministic fixture runtime、live RSS/Atom adapter、source registry validation、OPML drift、report contract、CLI smoke、SQLite durable document/event/delta/report/indicator/state/match/source-health storage、provider-neutral 7-strategy cross-day event resolution 與 20-type material-delta taxonomy、EventResolutionAuditV1、atomic UnitOfWork run-transaction（失敗 rollback、不覆蓋 last-valid-report）、transport-seam SSRF-guarded adapters（safe web / generic JSON API / FreshRSS / GDELT discovery / social direct channels / conditional RSS）、deterministic source-health state machine、feature-traced Retail/Crypto/Structural deterministic evaluators（wired；資料不足即 insufficient，不造假趨勢）、fake-only application flow、replaceability/import/cycle architecture gates（10 ports）。
四種 evaluation modes（deterministic/auto/api-assisted/chat-assisted，預設 auto）已接線；AI 只讀 bounded provider-neutral context，輸出經 deterministic revalidation（不得捏造 URL/id/數值），invalid→retry once→deterministic fallback；evaluation cache＋cost/budget（超支→ai_budget_exhausted）；prepare-chat/import-chat content-addressed byte-stable 封包＋import 守門。deterministic 與 auto-無-key 均不 import AI。
Potential：事件以試點/原型/新應用/新商業模式/跨域組合/採用擴散/material delta 等內容特徵判斷；官方來源的早期應用仍可進 Potential，bottom-up 一般新聞不會只因來源角色被列為 Potential。所有 qualified potential items 保留於 report；首頁只做 projection 精選。
Web projection：validated RadarReportV2 → typed web read-models（WebManifestV1 等，schema→TS 生成，drift-tested）→ content-addressed immutable artifacts（atomic stage-then-replace、unchanged skip、incremental、失敗不留半套）via `radar export-web`；Astro static dashboard（zero-JS、native CSS、繁中、Pages base 由 env、事實/推論/反證/不確定/缺口與 mode/status/fixture 皆 text+symbol 標示、history 分頁、SVG sparkline、空窗=insufficient）build 通過。首頁區分 Potential 精選與完整候選池，翻譯標題另列原文供查核。
Daily automation：六個 workflows（runtime-check/web-check/daily-intelligence/prepare-chat/import-chat/pages-deploy）＋保留 mount-check；daily-intelligence cron '0 23 * * *' UTC＝07:00 台灣、09:00 前部署，RADAR_EVALUATION_MODE 預設 auto；durable radar-state branch（compressed+checksum SQLite、last-good backup、atomic、concurrency lock、corruption rollback）；Pages 只部署 validated artifact（failed 不部署、fixture 僅 preview、base 由 env）；secrets contract（全部 optional，無 secret 仍可 deterministic＋建站＋部署）。
尚未完成：多 adapter 收集 stage 併入 run-daily（health 記錄／registry 選路）、以真實 API key 線上驗證 AI evaluation；GitHub Actions／Pages 需 owner 在 UI 開啟後方會真正執行部署。無 AI key 時不做外部標題機器翻譯，仍保留原文並明確顯示 deterministic 模式。
live-rss 只覆蓋 registry 內 RSS/Atom adapters；未執行來源必須成為 coverage gaps。
因此 fixture 與目前 live-rss run 均不得宣稱完整全球新聞覆蓋。
```

## 入口與權威

```text
AGENTS.md = 第一入口
CURRENT_STATE.md = 現況
CURRENT_DECISIONS.md = 已接受決策
config/runtime_contract.json = machine execution/output contract
config/source_registry.json = source identity contract
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
```

## Frozen v1 behavior

```text
fixed-count completion rules
split legacy source files as canonical identity
Markdown prompt as sole execution contract
```

These remain historical references only. Active completeness is coverage and contract based.
