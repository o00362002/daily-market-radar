# Maintenance Manual · 維護手冊 (中英對照)

> Bilingual reference for the daily-market-radar codebase: what each file/directory does and how they
> relate. 本手冊逐一說明各檔案／目錄的功能與彼此關係。

---

## 1. Overview · 系統總覽

**EN** — daily-market-radar is a provider-neutral "Automated Global Intelligence Radar". It collects
sources → normalizes → deduplicates → resolves cross-day events → computes material deltas → evaluates
deterministically (optionally AI/chat-assisted) → validates a strict `RadarReportV2` → projects immutable
web artifacts → renders a static Astro site → deploys daily to GitHub Pages. It runs end-to-end with **no
secrets** (deterministic mode); secrets only *enhance* it.

**中** — 本專案是 provider-neutral 的「全球每日情報雷達」。資料流：來源蒐集 → 正規化 → 去重 → 跨日事件
解析 → 實質變化(material delta) → 確定性評估（可選 AI／對話加強）→ 驗證 strict `RadarReportV2` →
投影不可變 web artifacts → 產生靜態 Astro 網站 → 每日部署到 GitHub Pages。**無任何 secret 也能端到端
執行**（deterministic 模式）；secret 只是加強，不是必要。

Architecture · 架構：**Ports / Adapters**（六邊形）。`application` 只依賴 10 個 runtime-checkable
Protocol ports 與 provider-neutral 的 `contracts`／`domain`／純函式 `pipeline`；具體實作只在
`composition.py` 選擇。

---

## 2. Top-level layout · 頂層結構

| Path | Function (EN) | 功能 (中) |
|------|---------------|-----------|
| `AGENTS.md` | First entry / governance rules (brain-core mount) | 第一入口與治理規則 |
| `CLAUDE.md` | Thin Claude adapter over AGENTS.md | Claude 薄適配器 |
| `CURRENT_STATE.md` | Current accepted reality (head ≤ 8000 bytes) | 現況（頭部 ≤8000 位元組） |
| `CURRENT_DECISIONS.md` | Accepted decisions + why | 已接受決策與理由 |
| `README.md` / `PROJECT_MAP.md` / `HIGH_LEVEL_INDEX.md` | Human orientation docs | 人類導覽文件 |
| `DEPENDENCY_MAP.md` / `AGENT_DEFINITION_MAP.md` | Dependency + task-routing maps | 依賴與任務路由圖 |
| `Makefile` | `make validate` = tests + contract + cli-smoke + brain checks | 驗證入口 |
| `pyproject.toml` | Python package (py≥3.12, pydantic; dev extras) | Python 套件定義 |
| `config/` | Runtime + source + scoring configuration (JSON/YAML) | 執行期／來源／評分設定 |
| `schemas/` | JSON Schemas (report, web, document, …) — drift-tested | JSON Schema（drift 測試） |
| `schema/sync-matrix.json` | The single linkage matrix (governance) | 唯一連動矩陣 |
| `migrations/` | SQLite migrations 0001–0005 | SQLite 遷移 |
| `src/radar/` | The application (see §3) | 應用程式本體 |
| `tests/` | unit / integration / contracts / architecture | 測試 |
| `web/` | Astro static dashboard (see §5) | Astro 靜態網站 |
| `.github/workflows/` | CI + daily scheduler + Pages (see §6) | CI／排程／部署 |
| `docs/` | Design + operations docs | 設計與維運文件 |
| `reports/execution_checks/` | Per-change receipts | 每次變更的收據 |
| `tools/brain/` | Node governance checkers (check-core, doc-paths, …) | 治理檢查器 |

---

## 3. `src/radar/` — the application · 應用程式

Dependency direction is strictly downward: `application → ports/contracts/domain`; concrete infra is
chosen only in `composition.py`. 依賴方向嚴格向下；具體實作只在 composition 選擇。

### 3.1 Ports (the stable boundary) · `ports/` — 穩定邊界

| File | Port(s) | 用途 |
|------|---------|------|
| `ports/sources.py` | `SourceAdapter` + fetch DTOs | 來源收集邊界 |
| `ports/evaluation.py` | `IntelligenceEvaluator` | 評估邊界 |
| `ports/repositories.py` | `DocumentRepository`, `EventRepository`, `ReportRepository`, `IndicatorRepository` | 讀取型持久化 |
| `ports/persistence.py` | `UnitOfWork` + `RunPersistenceBatch` (atomic write) | 原子寫入交易 |
| `ports/publishing.py` | `StateStore`, `WebArtifactStore`, `ReportPublisher` | 狀態／網站／發布 |

10 ports total; locked by `tests/architecture/test_ports_and_dependencies.py`. 共 10 個 port，由架構測試鎖定。

### 3.2 Contracts (typed, strict) · `contracts/` — 型別契約

| File | Function | 功能 |
|------|----------|------|
| `contracts/report.py` | `RadarReportV2` + `EventResolutionAuditV1`, `EvaluationAuditV1`, … (+ legacy migration) | 報告契約 |
| `contracts/evaluation.py` | `EvaluationRequest` / `EvaluationResult` DTOs | 評估 DTO |
| `contracts/runtime.py` | `RuntimeContract` (domains, matrix keys, indicators) | 執行契約 |
| `contracts/web.py` | `WebArtifactV1`, `PublicationReceiptV1` | web artifact |
| `contracts/web_projection.py` | `WebManifestV1`, `ReportSummaryV1`, `TrendSeriesV1`, … (→ `schemas/web.schema.json` → TS) | 網站讀模型 |

### 3.3 Domain (pure) · `domain/` — 純領域

| File | Function | 功能 |
|------|----------|------|
| `domain/models.py` | `Document`, `Event`, `EventDelta`, `CanonicalFacts`, URL/id helpers | 核心模型 |
| `domain/enums.py` | `DeltaType` (20 types), `MatchStrategy` | 列舉 |
| `domain/event_resolution.py` | **`EventResolutionService`** — 7-strategy match cascade + delta taxonomy + audit | 跨日事件解析 |
| `domain/scoring.py` | Deterministic score explanations, material-delta helper | 確定性評分說明 |
| `domain/source_health.py` | 8-status source-health state machine | 來源健康狀態機 |

### 3.4 Pipeline (pure functions) · `pipeline/`

`ingest`, `normalize`, `deduplicate`, `cluster`, `deltas` (→ delegates to `event_resolution`), `classify`,
`enrich`, `coverage`, `trends`, `verify`. 純函式資料流步驟；`deltas.py` 委派到 `event_resolution`。

### 3.5 Evaluators · `evaluators/`

| File | Function | 功能 |
|------|----------|------|
| `evaluators/deterministic.py` | `DeterministicIntelligenceEvaluator` (default) | 確定性評估器 |
| `evaluators/matrices.py` | Feature-traced Retail/Crypto matrices + structural indicators + rolling windows | 特徵溯源矩陣 |
| `evaluators/modes.py` | Resolve deterministic/auto/api-assisted/chat-assisted | 四模式解析 |
| `evaluators/ai_provider.py` | AI provider protocol + bounded context + **output revalidation** | AI 邊界與輸出驗證 |
| `evaluators/ai_assisted.py` | `AiAssistedEvaluator` (deterministic base + AI + retry/fallback) | AI 加強評估器 |
| `evaluators/cache.py` | Evaluation cache + `CostBudget` | 快取與預算 |

### 3.6 Adapters (infrastructure) · `adapters/`

| File | Function | 功能 |
|------|----------|------|
| `adapters/transport.py` | `HttpTransport` seam (SSRF policy, size cap, conditional requests) | HTTP 傳輸接縫 |
| `adapters/fixture.py` | Deterministic fixture source | 示例來源 |
| `adapters/rss.py` / `rss_client.py` | Registry RSS + hardened conditional/backoff RSS | RSS 收集 |
| `adapters/safe_web.py` | Allowlist-only SSRF-guarded web fetcher | 安全網頁抓取 |
| `adapters/json_api.py` | Registry-driven JSON API (pagination/token) | 通用 JSON API |
| `adapters/freshrss.py` | FreshRSS Google Reader API (credential-gated) | FreshRSS |
| `adapters/gdelt_discovery.py` | GDELT discovery (resolve-to-original) | GDELT 探索 |
| `adapters/social_channels.py` | Public social feeds + official-API interface | 社群直連 |
| `adapters/openai_provider.py` | OpenAI structured-output provider (lazy import) | OpenAI 供應器 |
| `adapters/base.py` | `UrlPolicy` (SSRF) + response-size guard | SSRF 政策 |

> Note · 註：`adapters/event_registry.py`, `mediacloud.py`, `newscatcher.py`, `official_api.py`,
> `rsshub.py` are earlier discovery stubs kept for reference; the wired adapters are the ones above.
> 這幾支是較早的探索雛形，供參考；實際接線的是上表。

### 3.7 Repositories / Stores · `repositories/`, `stores/`

| File | Function | 功能 |
|------|----------|------|
| `repositories/sqlite.py` | `SqliteRunRepository` (+ atomic `commit_run`, match provenance) | SQLite 持久化 + 原子交易 |
| `repositories/memory.py` | In-memory repos + `InMemoryUnitOfWork` (snapshot rollback) | 記憶體實作 |
| `repositories/source_health.py` | Sqlite/in-memory source-health repos | 來源健康持久化 |
| `stores/memory.py` | In-memory state + web-artifact stores | 記憶體 store |
| `publishers/noop.py` | No-op publisher | 空發布器 |

### 3.8 Web export · `web/` (Python side)

| File | Function | 功能 |
|------|----------|------|
| `radar/web/projection.py` | `project_web` — RadarReportV2 → immutable typed artifacts | 網站投影 |
| `radar/web/export.py` | Atomic stage-then-replace, unchanged-skip, rollback | 原子增量匯出 |
| `radar/web/runtime.py` | Load reports (db/input/dir) + project + export | 匯出執行 |

### 3.9 Chat-assisted · `chat/`

| File | Function | 功能 |
|------|----------|------|
| `chat/context_package.py` | Build byte-stable secret-free package + `validate_chat_import` | 對話封包與匯入守門 |
| `chat/runtime.py` | `prepare_chat` / `import_chat` file I/O | 封包產生／匯入 |

### 3.10 State · `state/`, Observability · `observability/`

| File | Function | 功能 |
|------|----------|------|
| `state/branch_store.py` | `radar-state` branch store: compress/checksum/backup/rollback | 持久狀態分支 |
| `observability/redaction.py` | Scrub secrets from logs/receipts | 憑證遮蔽 |

### 3.11 Composition & entry · 組裝與入口

| File | Function | 功能 |
|------|----------|------|
| `composition.py` | **The only place concrete impls are selected** | 唯一組裝點 |
| `application/run_daily.py` | `DailyRadarApplication.run` — the orchestration | 主要編排 |
| `runtime/runs.py` | Backward-compatible façade (mode resolution, env) | 相容 façade |
| `cli.py` | `radar` CLI: run-daily / export-web / prepare-chat / import-chat / state / sources | 命令列入口 |
| `runtime/contract.py` | Re-export of `RuntimeContract` | 契約再匯出 |

---

## 4. Data flow · 資料流

```
sources → adapters(fetch/normalize) → deduplicate → cluster
        → EventResolutionService(match + delta + audit)
        → material_events → Evaluator(deterministic | ai-assisted)
        → RadarReportV2 (validated) → UnitOfWork.commit_run (atomic)
        → project_web → export_web_artifacts → Astro build → GitHub Pages
```

Every stage that could fail is isolated; a failed run rolls back and never overwrites the last valid
report. 每個可能失敗的階段皆隔離；失敗 run 會 rollback，絕不覆蓋 last-valid report。

---

## 5. `web/` — Astro static dashboard

`web/src/pages/*` (index, reports/[date], domains/[domain], trends, retail, crypto, taiwan,
history/[page]); `web/src/lib/data.ts` (read artifacts), `format.ts` (badges/sparkline);
`web/src/generated/web-types.ts` (generated from `schemas/web.schema.json`);
`web/scripts/generate-types.mjs` (+ `--check` drift guard). Zero-JS-first, native CSS, 繁中預設,
Pages base from env. See `docs/web-architecture.md`.

---

## 6. `.github/workflows/` — CI + automation

| Workflow | Function | 功能 |
|----------|----------|------|
| `runtime-check.yml` | tests + make validate + no-secret deterministic + auto fallback | 執行期 CI |
| `web-check.yml` | export → types:check → Astro build → bundle budgets | 網站 CI |
| `daily-intelligence.yml` | scheduled pipeline (cron 23:00 UTC = 07:00 TW) + state + gated deploy | 每日排程 |
| `prepare-chat.yml` / `import-chat.yml` | chat package build / validated import | 對話流程 |
| `pages-deploy.yml` | manual redeploy of validated site | 手動重部署 |
| `mount-check.yml` | brain-core structural check | 結構體檢 |

---

## 7. Docs & receipts · 文件與收據

`docs/`: event-resolution, source-adapters, evaluation-modes, cost-control, chat-assisted-workflow,
web-architecture, state-persistence, secrets, operations, architecture, methodology, migration-v1-to-v2.
`reports/execution_checks/`: one dated receipt per change. `docs/secrets.md` lists the **owner-required
GitHub UI setup** (Pages=Actions, Actions read/write, optional secrets).

---

## 8. How to run / maintain · 如何執行與維護

```bash
# Setup (venv is py3.12; system python3 is too old)
.venv/bin/python -m pip install -e ".[dev]"

# Verify (do this before every commit)
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
make validate PYTHON=.venv/bin/python          # clear stale build outputs first to mimic a fresh CI checkout

# Full deterministic pipeline (no secrets)
PYTHONPATH=src .venv/bin/python -m radar.cli run-daily --date $(date +%F) --database data/radar.db --evaluation-mode deterministic
PYTHONPATH=src .venv/bin/python -m radar.cli export-web --out-dir . --database data/radar.db
cd web && npm ci && npm run types:check && RADAR_ARTIFACTS_DIR="$PWD/../artifacts/web/v1" npm run build
```

Maintenance rules · 維護規則：
- After changing `RadarReportV2` → regenerate `schemas/report.schema.json`; after web contracts →
  `schemas/web.schema.json` + `npm run types` (drift-tested). 改契約要重生對應 JSON schema 與 TS 型別。
- Editing `CURRENT_STATE.md`/`CURRENT_DECISIONS.md` requires a `reports/` receipt in the same commit
  (process gate). 動狀態文件要同 commit 附收據。
- Budgets: `AGENTS.md`≤4500, `CLAUDE.md`≤1200, `CURRENT_STATE` head ≤8000, root `.md`≤22 (put new docs
  in `docs/`). 入口預算與根目錄 md 數上限。
- Never commit `.venv/`, `__pycache__/`, `artifacts/`, `data/*.db`, `dist/` (all gitignored). 勿提交這些。

---

## 9. Delivered as five stacked PRs · 交付為五個 stacked PR

`feat/event-resolution-precision` (#9) → `feat/source-adapters-deterministic-evaluation` (#10) →
`feat/optional-ai-chat-assisted` (#11) → `feat/projection-first-dashboard` (#12) →
`feat/daily-scheduler-pages` (#13). See each PR body + `reports/execution_checks/` for details.
