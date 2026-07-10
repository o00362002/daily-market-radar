# Chat-assisted Workflow (PR D)

For running without an API key: a human hands a byte-stable context package to ChatGPT and imports the
result. No secrets, no full articles, no model-invented conclusions ever enter the package.

```bash
radar prepare-chat --date 2026-07-10 --output-root .
# -> artifacts/chat/v1/2026-07-10/<context-hash>/{manifest,context,events,evidence,prior-state,
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
site**. A **successful import** is `effective_mode=chat-assisted`, `evaluator=human_initiated_chat`, and
may be persisted, exported and redeployed.
