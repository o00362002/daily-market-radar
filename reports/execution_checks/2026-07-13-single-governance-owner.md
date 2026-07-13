# Execution Check｜Single Governance Owner

## Changed

- active governance route reduced to `brain-core` only
- AGENTS reduced to an owner-routing adapter
- manifest converted to machine-readable core/domain checker mappings
- protected-file confirmation gate added
- derived runtime counts removed from CURRENT_STATE prose
- core governance and domain-pack checks separated

## Not changed

- runtime report-domain membership or aliases
- profile floors
- source registry and query recipes
- report, AI-analysis, or web schemas
- collection, scoring, scheduling, persistence, or deployment behavior

## Validation

```bash
bash check_mount_integrity.sh
```

Expected: core mappings resolve, runtime-domain count is derived from `report_domains.length`, domain packs validate, and no active Mother Brain governance route remains.
