PYTHON ?= python3
PYTHONPATH := src

.PHONY: validate test unit integration contracts runtime-contract source-opml cli-smoke live-rss-smoke

validate: test runtime-contract source-opml cli-smoke
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

runtime-contract:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -c "from pathlib import Path; from radar.runtime.contract import RuntimeContract; RuntimeContract.from_file(Path('config/runtime_contract.json')); print('runtime contract valid')"

source-opml:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -c "from pathlib import Path; from radar.schemas.source import SourceRegistry; r=SourceRegistry.from_file(Path('config/source_registry.json')); r.validate(); assert r.to_opml()==Path('FRESHRSS_SEEDS.opml').read_text(encoding='utf-8'); print('source registry and OPML projection valid')"

cli-smoke:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m radar.cli sources validate
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m radar.cli run-daily --mode fixture --date 2026-07-10 >/tmp/daily-market-radar-run-daily.json

live-rss-smoke:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m radar.cli run-daily --mode live-rss --date 2026-07-10 --per-feed-limit 1 --timeout-seconds 5
