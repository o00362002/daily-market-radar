from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from radar.state.branch_store import (
    DB_ARTIFACT,
    LAST_GOOD_DIR,
    MANIFEST_ARTIFACT,
    StateCorruptionError,
    StateManifest,
    pack_state,
    restore_last_good,
    unpack_state,
    verify_state,
    write_state_tree,
)


def _db(tmp: Path, content: bytes) -> Path:
    path = tmp / "radar.db"
    path.write_bytes(content)
    return path


class StateBranchStoreTests(unittest.TestCase):
    def test_pack_is_byte_stable_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            db = _db(tmp, b"SQLite format 3\x00 payload one")
            a, ma = pack_state(db, run_id="run_a", created_at="2026-07-10T08:00:00+00:00")
            b, _mb = pack_state(db, run_id="run_a", created_at="2026-07-10T08:00:00+00:00")
            self.assertEqual(a, b)  # deterministic (mtime=0)
            verify_state(a, ma)  # does not raise

    def test_unpack_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            payload = b"SQLite format 3\x00 durable state"
            db = _db(tmp, payload)
            compressed, manifest = pack_state(db, run_id="run_a", created_at="2026-07-10T08:00:00+00:00")
            dest = tmp / "restored.db"
            unpack_state(compressed, manifest, dest)
            self.assertEqual(dest.read_bytes(), payload)

    def test_corruption_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            db = _db(tmp, b"payload")
            compressed, manifest = pack_state(db, run_id="run_a", created_at="2026-07-10T08:00:00+00:00")
            with self.assertRaises(StateCorruptionError):
                verify_state(compressed + b"tampered", manifest)

    def test_backup_rotation_and_corruption_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            state_root = tmp / "state"

            db1 = _db(tmp, b"state one")
            c1, m1 = pack_state(db1, run_id="run_1", created_at="2026-07-09T08:00:00+00:00")
            write_state_tree(state_root, c1, m1)

            db2 = _db(tmp, b"state two")
            c2, m2 = pack_state(db2, run_id="run_2", created_at="2026-07-10T08:00:00+00:00")
            written = write_state_tree(state_root, c2, m2)
            self.assertIn(f"state/{DB_ARTIFACT}", written)

            # run_1 was rotated into last-good.
            self.assertTrue((state_root / LAST_GOOD_DIR / "run_1.db.gz").exists())

            # Corrupt the current state, then roll back to the last good backup.
            (state_root / DB_ARTIFACT).write_bytes(b"corrupted-not-gzip")
            current = StateManifest.from_dict(json.loads((state_root / MANIFEST_ARTIFACT).read_text()))
            with self.assertRaises(StateCorruptionError):
                verify_state((state_root / DB_ARTIFACT).read_bytes(), current)

            dest = tmp / "recovered.db"
            restored = restore_last_good(state_root, dest)
            self.assertIsNotNone(restored)
            assert restored is not None
            self.assertEqual(restored.run_id, "run_1")
            self.assertEqual(dest.read_bytes(), b"state one")


if __name__ == "__main__":
    unittest.main()
