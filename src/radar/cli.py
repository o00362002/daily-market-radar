from __future__ import annotations

import argparse
import json
from pathlib import Path

from radar.runtime.runs import run_daily_fixture, run_daily_live, run_daily_live_rss
from radar.schemas.source import SourceRegistry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="radar")
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    sources = sub.add_parser("sources")
    source_sub = sources.add_subparsers(dest="source_command", required=True)
    source_sub.add_parser("validate")
    source_sub.add_parser("health")

    ingest = sub.add_parser("ingest")
    ingest.add_argument("--since", default="24h")
    ingest.add_argument("--mode", choices=["fixture", "live", "live-rss"], default="fixture")

    process = sub.add_parser("process")
    process.add_argument("--since", default="72h")

    coverage = sub.add_parser("coverage")
    coverage_sub = coverage.add_subparsers(dest="coverage_command", required=True)
    audit = coverage_sub.add_parser("audit")
    audit.add_argument("--profile", default="daily_push")

    report = sub.add_parser("report")
    report.add_argument("--profile", choices=["daily_push", "full"], required=True)
    report.add_argument("--date", required=True)

    trends = sub.add_parser("trends")
    trend_sub = trends.add_subparsers(dest="trend_command", required=True)
    weekly = trend_sub.add_parser("weekly")
    weekly.add_argument("--week", required=True)

    backtest = sub.add_parser("backtest")
    backtest.add_argument("--date", required=True)

    run_daily = sub.add_parser("run-daily")
    run_daily.add_argument("--date", required=True)
    run_daily.add_argument("--profile", choices=["daily_push", "full"], default="daily_push")
    run_daily.add_argument("--mode", choices=["fixture", "live", "live-rss"], default="fixture")
    run_daily.add_argument(
        "--evaluation-mode",
        choices=["deterministic", "auto", "api-assisted", "chat-assisted"],
        default="auto",
    )
    run_daily.add_argument("--database", default="")
    run_daily.add_argument("--timeout-seconds", type=int, default=12)
    run_daily.add_argument("--per-feed-limit", type=int, default=20)
    run_daily.add_argument("--freshrss-available", action="store_true")
    run_daily.add_argument("--disable-external-discovery", action="store_true")

    prepare_chat = sub.add_parser("prepare-chat")
    prepare_chat.add_argument("--date", required=True)
    prepare_chat.add_argument("--profile", choices=["daily_push", "full"], default="daily_push")
    prepare_chat.add_argument("--output-root", default="")

    import_chat = sub.add_parser("import-chat")
    import_chat.add_argument("--package-dir", required=True)
    import_chat.add_argument("--report", required=True)
    import_chat.add_argument("--receipt", default="")

    export_web = sub.add_parser("export-web")
    export_web.add_argument("--out-dir", default=".")
    export_web.add_argument("--database", default="")
    export_web.add_argument("--input", default="")
    export_web.add_argument("--reports-dir", default="")
    export_web.add_argument("--latest", action="store_true")
    export_web.add_argument("--full-rebuild", action="store_true", help="disable incremental unchanged-skip")
    export_web.add_argument(
        "--legacy-reports-dir",
        default="",
        help="project pre-dashboard markdown reports (e.g. reports/) into a /legacy archive",
    )

    state = sub.add_parser("state")
    state_sub = state.add_subparsers(dest="state_command", required=True)
    state_pack = state_sub.add_parser("pack")
    state_pack.add_argument("--database", required=True)
    state_pack.add_argument("--state-root", required=True)
    state_pack.add_argument("--run-id", default="scheduled")
    state_pack.add_argument("--created-at", default="")
    state_restore = state_sub.add_parser("restore")
    state_restore.add_argument("--state-root", required=True)
    state_restore.add_argument("--database", required=True)
    state_verify = state_sub.add_parser("verify")
    state_verify.add_argument("--state-root", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    source_registry_path = repo_root / "config/source_registry.json"

    if args.command == "sources":
        registry = SourceRegistry.from_file(source_registry_path)
        registry.validate()
        if args.source_command == "validate":
            print(f"source registry valid: {len(registry.sources)} sources")
            return 0
        enabled = [source for source in registry.sources if source.enabled]
        runtime_test_required = [
            source.source_id for source in enabled if source.verification_status == "runtime_test_required"
        ]
        print(
            json.dumps(
                {
                    "enabled_sources": len(enabled),
                    "runtime_test_required": runtime_test_required,
                    "status": "partial" if runtime_test_required else "healthy",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "run-daily":
        database_path = Path(args.database).resolve() if args.database else None
        common = {
            "profile_name": args.profile,
            "timeout_seconds": args.timeout_seconds,
            "per_feed_limit": args.per_feed_limit,
            "database_path": database_path,
            "evaluation_mode": args.evaluation_mode,
        }
        if args.mode == "live":
            result = run_daily_live(repo_root, date=args.date, **common)
        elif args.mode == "live-rss":
            result = run_daily_live_rss(repo_root, date=args.date, **common)
        else:
            result = run_daily_fixture(
                repo_root,
                date=args.date,
                freshrss_available=args.freshrss_available,
                external_discovery_available=not args.disable_external_discovery,
                profile_name=args.profile,
                database_path=database_path,
                evaluation_mode=args.evaluation_mode,
            )
        print(json.dumps(result.report, indent=2, ensure_ascii=False))
        return 0

    if args.command == "prepare-chat":
        from radar.chat.runtime import prepare_chat

        output_root = Path(args.output_root).resolve() if args.output_root else None
        package = prepare_chat(repo_root, date=args.date, profile=args.profile, output_root=output_root)
        print(
            json.dumps(
                {
                    "status": "prepared",
                    "context_hash": package.context.context_hash,
                    "package_dir": package.relative_dir,
                    "files": sorted(package.files),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "import-chat":
        from radar.chat.runtime import import_chat

        receipt = import_chat(
            repo_root,
            Path(args.package_dir).resolve(),
            Path(args.report).resolve(),
            receipt_path=Path(args.receipt).resolve() if args.receipt else None,
        )
        print(json.dumps(receipt.as_dict(), ensure_ascii=False, indent=2))
        return 0 if receipt.valid else 1

    if args.command == "export-web":
        from radar.web.runtime import export_web

        result = export_web(
            repo_root,
            Path(args.out_dir).resolve(),
            database=Path(args.database).resolve() if args.database else None,
            input_report=Path(args.input).resolve() if args.input else None,
            reports_dir=Path(args.reports_dir).resolve() if args.reports_dir else None,
            latest=args.latest,
            incremental=not args.full_rebuild,
            legacy_reports_dir=Path(args.legacy_reports_dir).resolve() if args.legacy_reports_dir else None,
        )
        print(
            json.dumps(
                {"status": "exported", "written": len(result.written), "skipped": len(result.skipped)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "state":
        from datetime import datetime, timezone

        from radar.state.branch_store import (
            MANIFEST_ARTIFACT,
            StateManifest,
            pack_state,
            restore_last_good,
            unpack_state,
            verify_state,
            write_state_tree,
        )

        if args.state_command == "pack":
            created_at = args.created_at or datetime.now(timezone.utc).isoformat()
            compressed, manifest = pack_state(
                Path(args.database).resolve(), run_id=args.run_id, created_at=created_at
            )
            written = write_state_tree(Path(args.state_root).resolve(), compressed, manifest)
            print(json.dumps({"status": "packed", "written": written, "run_id": manifest.run_id}, ensure_ascii=False))
            return 0

        state_root = Path(args.state_root).resolve()
        manifest_path = state_root / MANIFEST_ARTIFACT
        if args.state_command == "verify":
            if not manifest_path.exists():
                print(json.dumps({"status": "empty"}, ensure_ascii=False))
                return 0
            manifest = StateManifest.from_dict(json.loads(manifest_path.read_text(encoding="utf-8")))
            try:
                verify_state((state_root / "radar.db.gz").read_bytes(), manifest)
                print(json.dumps({"status": "valid", "run_id": manifest.run_id}, ensure_ascii=False))
                return 0
            except Exception as exc:  # noqa: BLE001
                print(json.dumps({"status": "corrupt", "reason": str(exc)}, ensure_ascii=False))
                return 1

        if args.state_command == "restore":
            database = Path(args.database).resolve()
            if not manifest_path.exists():
                print(json.dumps({"status": "no_state"}, ensure_ascii=False))
                return 0
            manifest = StateManifest.from_dict(json.loads(manifest_path.read_text(encoding="utf-8")))
            try:
                unpack_state((state_root / "radar.db.gz").read_bytes(), manifest, database)
                print(json.dumps({"status": "restored", "run_id": manifest.run_id}, ensure_ascii=False))
                return 0
            except Exception:  # noqa: BLE001 - corruption rollback to last good
                restored = restore_last_good(state_root, database)
                if restored is None:
                    print(json.dumps({"status": "unrecoverable"}, ensure_ascii=False))
                    return 1
                print(json.dumps({"status": "rolled_back", "run_id": restored.run_id}, ensure_ascii=False))
                return 0

    if args.command in {"ingest", "process", "coverage", "report", "trends", "backtest"}:
        print(
            json.dumps(
                {
                    "command": args.command,
                    "status": "scaffold",
                    "message": "Use run-daily for the currently connected deterministic pipeline.",
                },
                ensure_ascii=False,
            )
        )
        return 0
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
