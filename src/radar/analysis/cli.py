from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from radar.analysis.builder import build_deterministic_analysis, load_analysis_config
from radar.analysis.openai_provider import OpenAiAnalysisProvider
from radar.contracts.analysis import AIAnalysisV1, ai_analysis_json_schema
from radar.contracts.report import RadarReportV2
from radar.repositories.sqlite import SqliteRunRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m radar.analysis.cli")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--database")
    source.add_argument("--input")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--date", default="")
    parser.add_argument("--profile", choices=["daily_push", "full"], default="daily_push")
    parser.add_argument("--output-dir", default="artifacts/web/v1/ai-analysis")
    parser.add_argument("--mode", choices=["deterministic", "auto", "api-assisted"], default="auto")
    parser.add_argument("--model", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    config = load_analysis_config(repo_root)
    report, previous = _load_reports(args, repo_root)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = args.model or os.environ.get("OPENAI_ANALYSIS_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4.1-mini"

    fallback_reason: str | None = None
    if args.mode != "deterministic" and not api_key:
        fallback_reason = "OPENAI_API_KEY unavailable"

    analysis = build_deterministic_analysis(
        report,
        previous,
        config,
        requested_mode=args.mode,
        fallback_reason=fallback_reason,
    )

    if args.mode in {"auto", "api-assisted"} and api_key:
        try:
            analysis = OpenAiAnalysisProvider(api_key=api_key, model=model).enhance(report, analysis, config)
        except Exception as exc:  # noqa: BLE001 - analysis must degrade without breaking deployment
            fallback_reason = f"{type(exc).__name__}: {exc}"
            analysis = build_deterministic_analysis(
                report,
                previous,
                config,
                requested_mode=args.mode,
                fallback_reason=fallback_reason,
            )

    output_dir = Path(args.output_dir).resolve()
    written = _write_analysis(output_dir, analysis)
    print(
        json.dumps(
            {
                "status": "generated",
                "date": analysis.date,
                "analysis_id": analysis.analysis_id,
                "effective_mode": analysis.provenance.effective_mode,
                "provider": analysis.provenance.provider,
                "model": analysis.provenance.model,
                "fallback_used": analysis.provenance.fallback_used,
                "written": written,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _load_reports(args: argparse.Namespace, repo_root: Path) -> tuple[RadarReportV2, RadarReportV2 | None]:
    if args.input:
        report = RadarReportV2.from_payload(json.loads(Path(args.input).read_text(encoding="utf-8")))
        return report, None

    repository = SqliteRunRepository(Path(args.database).resolve(), repo_root / "migrations")
    reports = [report for report in repository.list_reports(args.profile) if not args.date or report.date == args.date]
    if not reports:
        target = args.date or "latest"
        raise ValueError(f"no report found for {target} / {args.profile}")
    report = reports[-1]
    all_profile_reports = repository.list_reports(args.profile)
    previous_candidates = [row for row in all_profile_reports if row.date < report.date]
    previous = previous_candidates[-1] if previous_candidates else None
    return report, previous


def _write_analysis(output_dir: Path, analysis: AIAnalysisV1) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_path = output_dir / f"{analysis.date}.json"
    latest_path = output_dir / "latest.json"
    schema_path = output_dir / "schema.json"
    payload = analysis.canonical_json_bytes()
    date_path.write_bytes(payload)
    latest_path.write_bytes(payload)
    schema_path.write_text(
        json.dumps(ai_analysis_json_schema(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return [str(path) for path in (date_path, latest_path, schema_path)]


if __name__ == "__main__":
    raise SystemExit(main())
