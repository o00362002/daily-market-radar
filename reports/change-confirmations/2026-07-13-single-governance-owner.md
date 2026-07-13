# Change Confirmation

Change type: single governance owner and owner-routing convergence
Affected files: AGENTS.md, CURRENT_STATE.md, brain.manifest.yaml, schema/protected-files.json, tools/brain/check-core.js, tools/brain/check-pre-change-confirmation.js, tools/install_hooks.sh, check_mount_integrity.sh
Human confirmed: yes
Risk level: full
Mother Brain activated: no
Rollback note: revert this branch; report logic, runtime contracts, domain membership, source registries, and output schemas were not changed.

## Owner decisions

- Daily Market Radar has one governance owner: `o00362002/brain-core`.
- Active files do not retain an alternate Mother Brain route.
- `AGENTS.md` is routing only.
- Canonical counts are derived from their config arrays and are not copied into State or routing prose.
- Core governance checks and Daily Radar domain checks are separate capability groups.
