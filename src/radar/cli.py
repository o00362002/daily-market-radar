from __future__ import annotations

import argparse
import json
from pathlib import Path

from radar.runtime.runs import run_daily_fixture, run_daily_live_rss
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
    ingest.add_argument("--mode", choices=["fixture", "live-rss"], default="fixture")

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
    run_daily.add_argument("--mode", choices=["fixture", "live-rss"], default="fixture")
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
        if args.mode == "live-rss":
            result = run_daily_live_rss(
                repo_root,
                date=args.date,
                profile_name=args.profile,
                timeout_seconds=args.timeout_seconds,
                per_feed_limit=args.per_feed_limit,
                database_path=database_path,
                evaluation_mode=args.evaluation_mode,
            )
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
