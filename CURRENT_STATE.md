# daily-market-radar｜CURRENT_STATE

<!-- 頭部只保留現在成立的事實；歷史移至 reports/ 或 archive/。 -->

## 現況摘要

```text
掛載：brain-core child mount。
定位：全球每日事件情報雷達＋多領域趨勢與潛力訊號掃描。
Active contract：config/runtime_contract.json。
Canonical source registry：config/source_registry.json。
Runtime：src/radar/ modular monolith；application 的所有可替換／外部 collaborator 都經九個 behavior Protocols 注入，並依賴 provider-neutral contracts/domain 與 pure deterministic pipeline/validation；concrete implementations 只由 composition root 選擇。
Validated boundary：RadarReportV2 與 WebArtifactV1 為 strict typed contract；report persistence、web projection、state checkpoint 與 publisher 都只接收 validated canonical values。
Profiles：daily_push 使用 slot caps；full 輸出 run budget 內所有 qualified items。數量不是完整性證明。
Report domains：六個 canonical domains，由 runtime contract 定義；configs/radars.yml 是細雷達模組，不新增 report-domain quota。
Source model：一個真實來源一個 source_id；RSS/API/web/RSSHub/social 為 adapters；FRESHRSS_SEEDS.opml 為 generated projection。
Taiwan：direct evidence 與 implication 分離，推論不得計入直接台灣證據。
Scoring：importance、potential、confidence 分開。
固定輸出：Retail matrix、Crypto matrix、三個 Structural Trend Indicators、coverage gaps、rejection counters、backtest。
```

## Production reality

```text
目前可驗證：deterministic fixture runtime、live RSS/Atom adapter、source registry validation、OPML drift、report contract、CLI smoke、SQLite durable document/event/delta/report/indicator/state/match storage、provider-neutral 7-strategy cross-day event resolution 與 20-type material-delta taxonomy、EventResolutionAuditV1、atomic UnitOfWork run-transaction（失敗 rollback、不覆蓋 last-valid-report）、fake-only application flow、replaceability/import/cycle architecture gates（10 ports）。
尚未完成：web/API/social/FreshRSS adapters、完整 source health、外部 discovery provider、AI-assisted semantic scorer、結構指標 evaluator、scheduler、production credentials。
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
