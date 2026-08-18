# Change Confirmation｜Local-first GitHub Actions gates

Change type: consolidate protected static CI triggers so routine development runs local validation first and GitHub retains only the PR/main confirmation gate.

Affected files: `.github/workflows/mount-check.yml`, `.github/workflows/single-owner-check.yml`, `.github/workflows/runtime-check.yml`, `.github/workflows/web-check.yml`, and this confirmation record.

Human confirmed: yes — the owner explicitly directed that each usage-report project move to a local-first validation structure while retaining minimal GitHub PR/main gates.

Risk level: medium — this reduces automatic GitHub-hosted execution, but preserves the full runtime gate, the specialized web gate, manual diagnostics, scheduled intelligence, and production workflows.

Mother Brain activated: no — no governance definition, checker semantics, mount identity, or child-registry assignment changes; only workflow dispatch scope changes.

Rollback note: restore the prior push and pull-request triggers in the four workflow files. The check commands and production/scheduled workflows remain unchanged, so rollback does not require data migration or runtime repair.
