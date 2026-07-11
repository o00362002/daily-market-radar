# Chat-assisted Workflow (PR D)

For running without an API key: a human hands a byte-stable context package to ChatGPT and imports the
result. No secrets, no full articles, no model-invented conclusions ever enter the package.

```bash
radar prepare-chat --date 2026-07-10 --output-root .
# -> artifacts/chat/v1/YYYY-MM-DD/<context-hash>/{manifest,context,events,evidence,prior-state,
#    deterministic-evaluation,runtime-contract,report-schema,expected-output.schema}.json + INSTRUCTIONS.md
radar import-chat --package-dir <dir> --report chatgpt-output.json --receipt receipt.json
```

## Package properties

Deterministic · content-addressed · byte-stable · no secrets · no full articles · no duplicate content ·
no model-invented conclusions. The `context_hash` is the SHA-256 over the sorted content files; the
manifest carries it.

## Import guards (`validate_chat_import`)

The import re-validates everything deterministically and rejects any drift:

- context hash, package version, report contract, date, profile, run_id
- every event id / document id / source id / evidence URL / numeric fact must be in the package
- domains, matrix keys, indicator ids must match the runtime contract
- Taiwan direct evidence must come from the listed Taiwan sources only
- Major and Potential lanes must not share an event

A **failed import produces a validation receipt and does not overwrite the last valid report or the
site**. A **successful import** is `effective_mode=chat-assisted`, `evaluator=human_initiated_chat`.

## GitHub Actions deployment

`.github/workflows/import-chat.yml` supports two paths:

1. **Automatic on main:** committing exactly one
   `chat-imports/**/RadarReportV2.json` file to `main` resolves the adjacent `package/` directory,
   validates the import, persists it into the durable SQLite state, rebuilds Astro and deploys Pages.
2. **Manual:** Actions → `import-chat` → Run workflow, then provide `package_dir` and `report_path`.
   `deploy=false` performs validation only.

The deployment sequence is:

```text
validate bounded import
→ restore radar-state
→ persist validated report to SQLite
→ export all durable report history + legacy archive
→ Astro typecheck/build
→ upload and deploy GitHub Pages
→ write checksummed state back to radar-state
```

### Safety gates

- Invalid imports fail after uploading `import-receipt.json`; state and Pages remain untouched.
- `status=failed` reports are never deployed.
- `source_audit.ingestion_mode=fixture` is validation/preview-only by default.
- A fixture report can replace production only through a manual run with
  `allow_fixture_deploy=true`. Do not enable this for a real daily site.
- `import-chat` and `daily-intelligence` share the `radar-daily` concurrency lock, preventing state or
  Pages deployment races.

After the deploy job is green, refresh the Pages site. GitHub Pages/CDN propagation can take roughly
one to several minutes; a hard refresh may be needed if the browser has cached the previous page.
