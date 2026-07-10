PYTHON ?= /Users/o00362002/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
PYTHONPATH := src

.PHONY: validate test unit integration contracts source-opml cli-smoke

validate: test source-opml cli-smoke
	node tools/brain/check-doc-paths.js
	node tools/brain/check-core.js
	node tools/brain/check-domain-packs.js
	node tools/brain/check-sync-matrix.js

test: unit integration contracts

unit:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests/unit -p 'test_*.py'

integration:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests/integration -p 'test_*.py'

contracts:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests/contracts -p 'test_*.py'

source-opml:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -c "from pathlib import Path; from radar.schemas.source import SourceRegistry; r=SourceRegistry.from_file(Path('config/source_registry.yaml')); r.validate(); assert r.to_opml()==Path('FRESHRSS_SEEDS.opml').read_text(encoding='utf-8')"

cli-smoke:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m radar.cli sources validate
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m radar.cli run-daily --date 2026-07-10 >/tmp/daily-market-radar-run-daily.json
