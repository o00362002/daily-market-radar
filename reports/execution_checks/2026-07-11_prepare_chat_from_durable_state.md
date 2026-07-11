# Prepare chat from durable validated state

## 改了什麼

- `radar prepare-chat` accepts `--database` and packages the validated report for the requested date/profile from SQLite.
- The package contains only report-linked events loaded from durable state; missing reports or missing referenced events fail closed.
- `.github/workflows/prepare-chat.yml` restores `radar-state`, waits on the shared `radar-daily` lock, prepares from the restored database and uploads a date/hash-addressed artifact.
- Production preparation explicitly rejects `source_audit.ingestion_mode=fixture`.
- The fixture path remains available only when the CLI is called without `--database`, preserving local deterministic contract tests.

## 機器檢查

- Added persisted report/event package tests, missing-report and missing-event rejection tests.
- Workflow contract tests now require radar-state restore, `--database`, the fixture refusal gate, and the downstream import/deploy chain.
- PR CI must pass runtime-check, web-check and mount-check.

## 沒做什麼

- Preparation does not recollect live sources and does not call OpenAI. It packages the validated evidence already saved by `daily-intelligence`.
- This does not make the old 2026-07-11 fixture package production-safe.

## 會影響誰

- The owner can now download a genuine non-fixture chat package from Actions after a successful daily run.
- ChatGPT output from that package can enter the already merged validation, persistence, build and Pages deployment workflow.

## 你可以驗證

```text
Actions → prepare-chat → choose a persisted date → artifact ingestion_mode is non-fixture
Actions → import-chat → import and deploy jobs green → refresh GitHub Pages
```
