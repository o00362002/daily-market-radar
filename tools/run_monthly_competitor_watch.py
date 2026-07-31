from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus


_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"[a-z0-9]+|[\u3400-\u9fff]")


@dataclass(frozen=True)
class FeedItem:
    provider_id: str
    query_id: str
    query_theme: str
    title: str
    url: str
    source: str
    summary: str
    published_at: str


@dataclass(frozen=True)
class Candidate:
    category: str
    score: int
    title: str
    url: str
    source: str
    published_at: str
    query_ids: list[str]
    matched_themes: list[str]
    matched_competitors: list[str]
    operation_signals: list[str]
    proof_signals: list[str]
    system_signals: list[str]
    benchmark_reason: str


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _clean_text(value: str | None) -> str:
    text = unescape(_TAG_RE.sub(" ", value or ""))
    return _SPACE_RE.sub(" ", text).strip()


def _normalized(value: str) -> str:
    return " ".join(_TOKEN_RE.findall(value.lower()))


def _phrase_matches(text: str, phrase: str) -> bool:
    normalized_text = _normalized(text)
    normalized_phrase = _normalized(phrase)
    if not normalized_phrase:
        return False
    if " " in normalized_phrase:
        return normalized_phrase in normalized_text
    if normalized_phrase.isascii():
        return re.search(rf"(?<![a-z0-9]){re.escape(normalized_phrase)}(?![a-z0-9])", normalized_text) is not None
    return normalized_phrase in normalized_text


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError, OverflowError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _child_text(node: ET.Element, names: set[str]) -> str:
    for child in node.iter():
        if _local_name(child.tag) in names and child.text:
            return child.text.strip()
    return ""


def _entry_link(node: ET.Element) -> str:
    for child in node.iter():
        if _local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        if href:
            return href.strip()
        if child.text:
            return child.text.strip()
    return ""


def parse_feed(payload: bytes, *, provider_id: str, query_id: str, query_theme: str) -> list[FeedItem]:
    root = ET.fromstring(payload)
    entries = [node for node in root.iter() if _local_name(node.tag) in {"item", "entry"}]
    items: list[FeedItem] = []
    for entry in entries:
        title = _clean_text(_child_text(entry, {"title"}))
        url = _entry_link(entry)
        if not title or not url:
            continue
        summary = _clean_text(_child_text(entry, {"description", "summary", "content"}))
        source = _clean_text(_child_text(entry, {"source", "author"}))
        published_raw = _child_text(entry, {"pubdate", "published", "updated", "date"})
        published = _parse_date(published_raw)
        items.append(
            FeedItem(
                provider_id=provider_id,
                query_id=query_id,
                query_theme=query_theme,
                title=title,
                url=url,
                source=source,
                summary=summary,
                published_at=published.isoformat() if published else "",
            )
        )
    return items


def fetch_bytes(url: str, *, timeout_seconds: int = 20, attempts: int = 3) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "daily-market-radar/competitor-watch (+https://github.com/o00362002/daily-market-radar)",
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
                return response.read()
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt * 1.5)
    raise RuntimeError(f"feed fetch failed after {attempts} attempts: {last_error}")


def _known_competitors(registry: dict[str, Any]) -> list[tuple[str, str, list[str]]]:
    values: list[tuple[str, str, list[str]]] = []
    for entries in registry.get("groups", {}).values():
        for entry in entries:
            aliases = [str(entry.get("name", "")), *[str(value) for value in entry.get("aliases", [])]]
            aliases = [alias for alias in aliases if alias.strip()]
            values.append((str(entry.get("id", "")), str(entry.get("name", "")), aliases))
    return values


def _matches(values: list[str], text: str) -> list[str]:
    return [value for value in values if _phrase_matches(text, value)]


def score_item(
    item: FeedItem,
    *,
    config: dict[str, Any],
    known_competitors: list[tuple[str, str, list[str]]],
) -> Candidate | None:
    text = f"{item.title} {item.summary} {item.source}"
    scoring = config["scoring"]
    hard_exclusions = _matches(scoring.get("hard_exclusions", []), text)
    if hard_exclusions:
        return None

    matched_themes = [
        theme
        for theme, keywords in config["themes"].items()
        if _matches(keywords, text)
    ]
    if item.query_theme not in matched_themes:
        matched_themes.append(item.query_theme)
    matched_themes = sorted(set(matched_themes))

    operation_hits = _matches(scoring.get("operation_keywords", []), text)
    proof_hits = _matches(scoring.get("proof_keywords", []), text)
    system_hits = _matches(scoring.get("system_keywords", []), text)
    if not matched_themes or not operation_hits or not proof_hits or not system_hits:
        return None

    competitor_names: list[str] = []
    for _competitor_id, name, aliases in known_competitors:
        if any(_phrase_matches(text, alias) for alias in aliases):
            competitor_names.append(name)

    score = 3
    score += min(2, len(matched_themes))
    score += min(2, len(operation_hits))
    score += min(2, len(proof_hits))
    score += min(2, len(system_hits))
    if competitor_names:
        score += 1
    if score < int(scoring["minimum_score"]):
        return None

    normalized = _normalized(text)
    case_signal = any(
        phrase in normalized
        for phrase in (
            "case study",
            "retailer",
            "stores",
            "rollout",
            "deployed",
            "deployment",
            "implementation",
            "roi",
        )
    )
    if competitor_names:
        category = "known_competitor_material_case"
    elif case_signal:
        category = "retailer_case"
    else:
        category = "new_system_candidate"

    reason_parts = [
        "主題=" + ", ".join(matched_themes),
        "營運訊號=" + ", ".join(operation_hits[:4]),
        "落地證據=" + ", ".join(proof_hits[:4]),
        "系統訊號=" + ", ".join(system_hits[:4]),
    ]
    if competitor_names:
        reason_parts.append("既有競品=" + ", ".join(sorted(set(competitor_names))))

    return Candidate(
        category=category,
        score=score,
        title=item.title,
        url=item.url,
        source=item.source,
        published_at=item.published_at,
        query_ids=[item.query_id],
        matched_themes=matched_themes,
        matched_competitors=sorted(set(competitor_names)),
        operation_signals=operation_hits[:6],
        proof_signals=proof_hits[:6],
        system_signals=system_hits[:6],
        benchmark_reason="；".join(reason_parts),
    )


def _dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    best: dict[str, Candidate] = {}
    for candidate in candidates:
        key = _normalized(candidate.title)
        if not key:
            key = candidate.url
        current = best.get(key)
        if current is None or candidate.score > current.score:
            best[key] = candidate
        elif candidate.score == current.score:
            best[key] = Candidate(
                **{
                    **asdict(current),
                    "query_ids": sorted(set(current.query_ids + candidate.query_ids)),
                    "matched_themes": sorted(set(current.matched_themes + candidate.matched_themes)),
                }
            )
    return sorted(best.values(), key=lambda value: (value.score, value.published_at, value.title), reverse=True)


def build_report(
    *,
    config: dict[str, Any],
    registry: dict[str, Any],
    now: datetime,
    fetcher=fetch_bytes,
) -> dict[str, Any]:
    cutoff = now.astimezone(timezone.utc) - timedelta(days=int(config["lookback_days"]))
    known = _known_competitors(registry)
    feed_items: list[FeedItem] = []
    failures: list[dict[str, str]] = []
    successful_checks = 0

    for query in config["queries"]:
        for provider in config["providers"]:
            query_suffix = str(provider.get("query_suffix", "")).format(
                lookback_days=int(config["lookback_days"])
            )
            encoded_query = quote_plus(f"{query['query']}{query_suffix}")
            url = str(provider["url_template"]).format(
                query=encoded_query,
                lookback_days=int(config["lookback_days"]),
            )
            try:
                payload = fetcher(url)
                successful_checks += 1
                feed_items.extend(
                    parse_feed(
                        payload,
                        provider_id=str(provider["id"]),
                        query_id=str(query["id"]),
                        query_theme=str(query["theme"]),
                    )
                )
            except Exception as exc:  # one provider/query must not collapse monthly monitoring
                failures.append(
                    {
                        "provider_id": str(provider["id"]),
                        "query_id": str(query["id"]),
                        "url": url,
                        "error": str(exc)[:500],
                    }
                )

    recent_items = []
    for item in feed_items:
        published = _parse_date(item.published_at)
        if published is not None and published < cutoff:
            continue
        recent_items.append(item)

    candidates = [
        candidate
        for item in recent_items
        if (candidate := score_item(item, config=config, known_competitors=known)) is not None
    ]
    candidates = _dedupe_candidates(candidates)[: int(config["max_candidates"])]
    category_counts: dict[str, int] = {}
    for candidate in candidates:
        category_counts[candidate.category] = category_counts.get(candidate.category, 0) + 1

    total_checks = len(config["queries"]) * len(config["providers"])
    if successful_checks == 0:
        status = "failed"
    elif failures:
        status = "partial"
    else:
        status = "complete"

    return {
        "schema_version": config["schema_version"],
        "owner": config["owner"],
        "generated_at": now.astimezone(timezone.utc).isoformat(),
        "lookback_days": int(config["lookback_days"]),
        "status": status,
        "query_count": len(config["queries"]),
        "provider_count": len(config["providers"]),
        "source_check_count": total_checks,
        "successful_source_check_count": successful_checks,
        "failed_source_check_count": len(failures),
        "feed_item_count": len(feed_items),
        "recent_item_count": len(recent_items),
        "candidate_count": len(candidates),
        "category_counts": category_counts,
        "candidates": [asdict(candidate) for candidate in candidates],
        "failures": failures,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# 國際 RetailOps 每月競品對標追蹤",
        "",
        f"- 產生時間：{report['generated_at']}",
        f"- 狀態：`{report['status']}`",
        f"- 查詢／來源成功：{report['successful_source_check_count']} / {report['source_check_count']}",
        f"- 候選數：{report['candidate_count']}",
        "- 範圍：自主補貨、Agentic RetailOps、閉環營運",
        "",
    ]
    if not report["candidates"]:
        lines.extend(["本期沒有通過對標門檻的新系統或落地案例。", ""])
    for index, candidate in enumerate(report["candidates"], start=1):
        lines.extend(
            [
                f"## {index}. {candidate['title']}",
                "",
                f"- 類型：`{candidate['category']}`｜分數：{candidate['score']}",
                f"- 來源：{candidate['source'] or '未標示'}｜日期：{candidate['published_at'] or '未知'}",
                f"- 對標理由：{candidate['benchmark_reason']}",
                f"- 證據：{candidate['url']}",
                "",
            ]
        )
    if report["failures"]:
        lines.extend(["## 來源缺口", ""])
        for failure in report["failures"]:
            lines.append(
                f"- `{failure['provider_id']}/{failure['query_id']}`：{failure['error']}"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/competitor_monthly_watch.json"))
    parser.add_argument("--registry", type=Path, default=Path("config/competitor_registry.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args(argv)

    config = json.loads(args.config.read_text(encoding="utf-8"))
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    report = build_report(config=config, registry=registry, now=datetime.now(timezone.utc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "candidate_count": report["candidate_count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
