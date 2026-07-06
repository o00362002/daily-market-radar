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
import time
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
    notes: str


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/"


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


def load_source_registry() -> dict[str, dict[str, Any]]:
    # Lightweight local mapping. The canonical registry remains sources/channel_feed_sources.json.
    path = Path("sources/channel_feed_sources.json")
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = data.get("sources", []) if isinstance(data, dict) else []
    registry: dict[str, dict[str, Any]] = {}
    for item in sources:
        feed_url = item.get("feed_url")
        if feed_url:
            registry[feed_url] = item
    return registry


def feed_id_to_url(feed_id: str) -> str:
    # Google Reader style IDs often look like feed/https://example.com/feed.xml
    return feed_id.removeprefix("feed/")


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
        feed_url = feed_id_to_url(stream_id)
        sub = subscriptions.get(stream_id, {})
        source_name = origin.get("title") or sub.get("title")
        source_meta = registry.get(feed_url, {})
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
                notes="Pulled from FreshRSS Google Reader compatible API",
            )
        )

    return candidates


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
        "version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "FreshRSS Google Reader compatible API",
        "item_count": len(candidates),
        "candidates": [asdict(candidate) for candidate in candidates],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(candidates)} candidates to {output_path}")
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
