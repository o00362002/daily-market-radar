# Operations

## Local Runtime

```bash
make validate
PYTHONPATH=src python -m radar.cli sources validate
PYTHONPATH=src python -m radar.cli run-daily --date 2026-07-10
```

The bundled Codex Python 3.12 path is wired into `Makefile` by default. Override
it with `PYTHON=/path/to/python3` when using a local virtual environment.

## Daily Order

```text
source health -> top-down ingest -> bottom-up ingest -> external gap discovery
-> normalize -> dedup -> event cluster -> event delta -> evidence verification
-> score -> coverage gate -> report plan -> render -> contract validation
-> post-run backtest
```

## RSS Stack Images

The RSS stack no longer uses `latest`. Image references are pinned through
`infra/rss-stack/.env.example`. Before updating a tag or digest:

```bash
cd infra/rss-stack
docker compose pull
docker compose up -d
docker compose ps
curl -f http://localhost:1200/healthz
curl -I http://localhost:8080
```

Record the validation in `reports/execution_checks/`.
