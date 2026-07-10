# State Persistence (PR F)

GitHub runners are ephemeral, so the SQLite database must be carried between daily runs. The default
backend is a dedicated **`radar-state` branch** (an external `DATABASE_URL` backend is the documented
alternative). The state branch **never pollutes `main`**.

## Layout (on the `radar-state` branch)

```
state/radar.db.gz            # gzip-compressed SQLite (deterministic, mtime=0)
state/manifest.json          # state/v1 manifest with checksums + run_id + created_at
state/last-good/<run>.db.gz  # rotated backups (retention: newest N)
state/last-good/<run>.manifest.json
```

## Guarantees (`radar/state/branch_store.py`)

- **Compressed + checksummed**: the manifest records both compressed and uncompressed SHA-256 and the
  uncompressed size. `verify_state` raises `StateCorruptionError` on any mismatch or bad gzip stream.
- **Atomic update**: `unpack_state` writes to a temp file and `replace`s it into place.
- **Last-good backup + corruption rollback**: `write_state_tree` rotates the previously committed valid
  state into `last-good/` before overwriting; `restore_last_good` recovers the newest valid backup when
  the current state is corrupt.
- **Retention**: old backups beyond N are pruned.
- **Concurrency lock**: the `daily-intelligence` workflow uses `concurrency: { group: radar-daily,
  cancel-in-progress: false }` so runs never race on the state branch.

## CLI

```bash
radar state pack    --database data/radar.db --state-root .state/state --run-id <id>
radar state verify  --state-root .state/state
radar state restore --state-root .state/state --database data/radar.db   # rolls back to last-good on corruption
```
