from __future__ import annotations

import argparse
import json
from pathlib import Path

from radar.runtime.runs import run_daily_fixture
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.command == "sources":
        registry = SourceRegistry.from_file(repo_root / "config/source_registry.yaml")
        registry.validate()
        if args.source_command == "validate":
            print("source registry valid")
            return 0
        print("source health static checks valid")
        return 0
    if args.command == "run-daily":
        result = run_daily_fixture(repo_root, date=args.date, freshrss_available=False)
        print(json.dumps(result.report, indent=2, ensure_ascii=False))
        return 0
    if args.command in {"ingest", "process", "coverage", "report", "trends", "backtest"}:
        print(f"{args.command} fixture command accepted")
        return 0
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
