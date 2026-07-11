# Chat-assisted import auto-deploy

## 改了什麼

- `import-chat` now supports validation-only or full deployment.
- A valid deploy restores `radar-state`, persists the submitted report into SQLite, exports all durable report history and legacy pages, builds Astro, deploys GitHub Pages and writes the updated checksummed state back to `radar-state`.
- A committed `chat-imports/**/RadarReportV2.json` on `main` automatically resolves its adjacent `package/` directory and runs the pipeline.
- Manual runs retain explicit `package_dir` and `report_path` inputs and add `deploy` plus `allow_fixture_deploy` controls.
- The one-off hard-coded `validate-chat-import-pr` workflow was removed.

## Safety

- Invalid imports upload a receipt and fail without persisting state or changing Pages.
- `status=failed` is never deployable.
- Fixture reports are preview-only by default; production replacement requires an explicit manual `allow_fixture_deploy=true`.
- Push-triggered imports can never bypass the fixture gate.
- Chat import and daily intelligence share the `radar-daily` concurrency lock.

## Machine checks

PR CI must run the repository `runtime-check`, `web-check` and mount checks. The first post-merge non-fixture chat report exercises the full Pages deployment path.

## 沒做什麼

This change does not convert the existing fixture-based `prepare-chat` package into live collection. It only makes a validated, non-fixture chat result durable and deployable.

## 影響

Owners no longer need a separate export/build/deploy sequence after `import-chat`; successful imports can move from JSON to the live site in one workflow.

## 你可以驗證

```text
Actions → import-chat → successful import job → successful deploy job
```

After the deploy job is green, refresh the GitHub Pages site. CDN propagation may take one to several minutes.
