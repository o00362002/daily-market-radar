# 2026-08-14 AGENTS budget repair

Change type: Governance entry budget repair

Affected files: `AGENTS.md`

Human confirmed: yes

Risk level: low

Mother Brain activated: yes

Rollback note: Revert the AGENTS compaction commit if any routing meaning is found to have changed. The edit only removes duplicated English restatements of two rules whose Chinese canonical wording remains unchanged.

## Decision

The repository's existing CI was red because `AGENTS.md` measured 4567 bytes against the enforced 4500-byte entry budget. The protected-file change is kept separate from PR #68 so the structural-scoring and competitor-analysis feature diff does not absorb unrelated governance maintenance.
