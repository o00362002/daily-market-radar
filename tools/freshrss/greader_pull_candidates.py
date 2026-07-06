#!/usr/bin/env python3
"""
Pull FreshRSS items through the Google Reader compatible API and normalize them
as daily-market-radar feed candidates.

Secrets are read from environment variables only. Do not commit API passwords.

Required environment variables:
  FRESHRSS_BASE_URL       Example: http://localhost:8080
  FRESHRSS_DEFAULT_USER   Example: admin
  FRESHRSS_API_PASSWORD   FreshRSS API password, not the login password

Optional environment variables:
  FRESHRSS_LOOKBACK_HOURS Default: 48
  FRESHRSS_MAX_ITEMS      Default: 100

Output:
  data/freshrss/feed_candidates_latest.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests


@dataclass
class FeedCandidate:
    candidate_id: str
    source_id: str | None
    source_name: str | None
    freshrss_stream_id: str
    feed_url: str
    feed_category: str | None
    domain_ids: list[str]
    title: str
    url: str
    original_url: str
    published_at: str | None
    fetched_at: str
    summary: str
    evidence_default: str
    today_new_information: str
    historical_duplication_status: str
    ingestion_status: str
    mapping_status: str
    notes: str


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/"


def normalize_name(value: str | None) -> str:
    value = value or ""
    value = value.lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def greader_url(base_url: str, path: str) -> str:
    return urljoin(normalize_base_url(base_url), "api/greader.php/" + path.lstrip("/"))


def login(base_url: str, username: str, api_password: str) -> str:
    endpoint = greader_url(base_url, "accounts/ClientLogin")
    response = requests.post(
        endpoint,
        data={"Email": username, "Passwd": api_password},
        timeout=30,
    )
    response.raise_for_status()
    auth = None
    for line in response.text.splitlines():
        if line.startswith("Auth="):
            auth = line.split("=", 1)[1].strip()
            break
    if not auth:
        raise RuntimeError("FreshRSS login succeeded but no Auth token was returned")
    return auth


def api_get(base_url: str, auth: str, path: str, params: dict[str, Any] | None = None) -> Any:
    headers = {"Authorization": f"GoogleLogin auth={auth}"}
    response = requests.get(greader_url(base_url, path), headers=headers, params=params or {}, timeout=45)
    response.raise_for_status()
    return response.json()


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_registry_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    for key in ("feeds", "sources", "items", "entries"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def load_source_registry() -> dict[str, dict[str, dict[str, Any]]]:
    # Lightweight local mapping. The canonical registry remains sources/channel_feed_sources.json.
    path = Path("sources/channel_feed_sources.json")
    registry = {"by_url": {}, "by_name": {}}
    if not path.exists():
        return registry

    data = json.loads(path.read_text(encoding="utf-8"))
    items = extract_registry_items(data)
    for item in items:
        for key in ("feed_url", "xmlUrl", "rsshub_url"):
            feed_url = item.get(key)
            if feed_url:
                registry["by_url"][feed_url] = item
                registry["by_url"][feed_url.rstrip("/")] = item
        for key in ("name", "source_id"):
            name = item.get(key)
            if name:
                registry["by_name"][normalize_name(name)] = item
    return registry


def feed_id_to_url(feed_id: str, subscription: dict[str, Any]) -> str:
    # FreshRSS may return internal stream IDs like feed/4. Prefer subscription URL fields when available.
    for key in ("url", "htmlUrl", "feedUrl", "xmlUrl"):
        value = subscription.get(key)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
    return feed_id.removeprefix("feed/")


def lookup_source_meta(
    registry: dict[str, dict[str, dict[str, Any]]],
    feed_url: str,
    source_name: str | None,
) -> tuple[dict[str, Any], str]:
    by_url = registry.get("by_url", {})
    by_name = registry.get("by_name", {})

    if feed_url in by_url:
        return by_url[feed_url], "mapped_by_exact_feed_url"
    trimmed = feed_url.rstrip("/")
    if trimmed in by_url:
        return by_url[trimmed], "mapped_by_trimmed_feed_url"

    normalized_source_name = normalize_name(source_name)
    if normalized_source_name in by_name:
        return by_name[normalized_source_name], "mapped_by_source_name"

    return {}, "unmapped_feed_url_and_name"


def make_candidate_id(source_id: str | None, title: str, published_at: str | None, url: str) -> str:
    basis = "::".join([source_id or "unknown", published_at or "unknown_date", title or url])
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", basis).strip("-").lower()[:120]
    return f"feed::{slug}"


def normalize_items(items: list[dict[str, Any]], subscriptions: dict[str, dict[str, Any]]) -> list[FeedCandidate]:
    registry = load_source_registry()
    fetched_at = datetime.now(timezone.utc).isoformat()
    candidates: list[FeedCandidate] = []

    for item in items:
        title = item.get("title") or ""
        canonical = item.get("canonical") or []
        alternate = item.get("alternate") or []
        url = ""
        if canonical and isinstance(canonical, list):
            url = canonical[0].get("href", "")
        if not url and alternate and isinstance(alternate, list):
            url = alternate[0].get("href", "")

        origin = item.get("origin") or {}
        stream_id = origin.get("streamId") or ""
        sub = subscriptions.get(stream_id, {})
        feed_url = feed_id_to_url(stream_id, sub)
        source_name = origin.get("title") or sub.get("title")
        source_meta, mapping_status = lookup_source_meta(registry, feed_url, source_name)
        source_id = source_meta.get("source_id")
        domain_ids = source_meta.get("domain_ids") or source_meta.get("domains") or []
        feed_category = source_meta.get("opml_category") or None
        evidence_default = source_meta.get("evidence_default", "candidate_until_checked")

        published = item.get("published")
        published_at = None
        if isinstance(published, int):
            published_at = datetime.fromtimestamp(published, timezone.utc).isoformat()

        summary_obj = item.get("summary") or item.get("content") or {}
        summary = strip_html(summary_obj.get("content", "") if isinstance(summary_obj, dict) else str(summary_obj))

        candidates.append(
            FeedCandidate(
                candidate_id=make_candidate_id(source_id, title, published_at, url),
                source_id=source_id,
                source_name=source_name,
                freshrss_stream_id=stream_id,
                feed_url=feed_url,
                feed_category=feed_category,
                domain_ids=list(domain_ids) if isinstance(domain_ids, list) else [],
                title=title,
                url=url,
                original_url=url,
                published_at=published_at,
                fetched_at=fetched_at,
                summary=summary,
                evidence_default=evidence_default,
                today_new_information="unknown_until_checked",
                historical_duplication_status="unknown_until_checked",
                ingestion_status="new",
                mapping_status=mapping_status,
                notes="Pulled from FreshRSS Google Reader compatible API",
            )
        )

    return candidates


def summarize_mapping(candidates: list[FeedCandidate]) -> dict[str, Any]:
    by_feed: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        key = candidate.feed_url or candidate.freshrss_stream_id or "unknown"
        if key not in by_feed:
            by_feed[key] = {
                "feed_url": candidate.feed_url,
                "freshrss_stream_id": candidate.freshrss_stream_id,
                "source_name": candidate.source_name,
                "source_id": candidate.source_id,
                "mapping_status": candidate.mapping_status,
                "count": 0,
            }
        by_feed[key]["count"] += 1
    return {
        "mapped_count": sum(1 for c in candidates if c.source_id),
        "unmapped_count": sum(1 for c in candidates if not c.source_id),
        "feeds": sorted(by_feed.values(), key=lambda x: x["count"], reverse=True),
    }


def main() -> int:
    base_url = env_required("FRESHRSS_BASE_URL")
    username = env_required("FRESHRSS_DEFAULT_USER")
    api_password = env_required("FRESHRSS_API_PASSWORD")
    max_items = int(os.getenv("FRESHRSS_MAX_ITEMS", "100"))

    auth = login(base_url, username, api_password)
    subscription_data = api_get(base_url, auth, "reader/api/0/subscription/list", {"output": "json"})
    subscriptions_list = subscription_data.get("subscriptions", [])
    subscriptions = {sub.get("id", ""): sub for sub in subscriptions_list if sub.get("id")}

    stream = api_get(
        base_url,
        auth,
        "reader/api/0/stream/contents/reading-list",
        {"output": "json", "n": max_items},
    )
    items = stream.get("items", [])
    candidates = normalize_items(items, subscriptions)

    output_dir = Path("data/freshrss")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "feed_candidates_latest.json"
    payload = {
        "version": "0.4",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "FreshRSS Google Reader compatible API",
        "item_count": len(candidates),
        "mapping_summary": summarize_mapping(candidates),
        "candidates": [asdict(candidate) for candidate in candidates],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(candidates)} candidates to {output_path}")
    print(json.dumps(payload["mapping_summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.HTTPError as exc:
        print(f"FreshRSS API HTTP error: {exc}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"FreshRSS API pull failed: {exc}", file=sys.stderr)
        raise
