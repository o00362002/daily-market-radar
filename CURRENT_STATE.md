# daily-market-radar｜CURRENT_STATE

<!-- 頭部只保留現在成立的事實；歷史移至 reports/ 或 archive/。 -->

## 現況摘要

```text
掛載：brain-core child mount。
定位：全球每日事件情報雷達＋多領域趨勢與潛力訊號掃描。
Active contract：config/runtime_contract.json。
Canonical source registry：config/source_registry.yaml。
Runtime：src/radar/ modular monolith，具備 fixture ingestion、URL normalization、dedup、event clustering、major/potential lane、coverage cells、report planning、contract validation 與 fixture replay。
Profiles：daily_push 使用 slot caps；full 輸出 run budget 內所有 qualified items。數量不是完整性證明。
Report domains：六個 canonical domains，由 runtime contract 定義；configs/radars.yml 是細雷達模組，不新增 report-domain quota。
Source model：一個真實來源一個 source_id；RSS/API/web/RSSHub/social 為 adapters；FRESHRSS_SEEDS.opml 為 generated projection。
Taiwan：direct evidence 與 implication 分離，推論不得計入直接台灣證據。
Scoring：importance、potential、confidence 分開。
固定輸出：Retail matrix、Crypto matrix、三個 Structural Trend Indicators、coverage gaps、rejection counters、backtest。
```

## Production reality

```text
目前可驗證：deterministic fixture runtime、source registry validation、OPML drift、report contract、CLI smoke、unit/integration/contract tests。
尚未完成：正式 live RSS/HTTP ingestion、FreshRSS API ingestion、完整 source health、外部 discovery provider、durable database repository、scheduler、production credentials、完整台灣與小眾來源 registry。
因此 fixture run 只能標 partial，不能宣稱正式全球新聞覆蓋完成。
```

## 入口與權威

```text
AGENTS.md = 第一入口
CURRENT_STATE.md = 現況
CURRENT_DECISIONS.md = 已接受決策
config/runtime_contract.json = machine execution/output contract
config/source_registry.yaml = source identity contract
AGENT_DEFINITION_MAP.md = 任務路由
DEPENDENCY_MAP.md = 人類可讀依賴與降級說明
schema/sync-matrix.json = 連動矩陣
```

## Validation entrypoints

```text
make validate
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli run-daily --date YYYY-MM-DD
```

## Frozen v1 behavior

```text
固定 3+3 / 5+5 / 48-signal / 60-signal completion rules
split legacy source files as canonical identity
Markdown prompt as sole execution contract
```

These remain historical references only. Active completeness is coverage and contract based.
