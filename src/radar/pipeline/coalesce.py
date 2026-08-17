from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from radar.domain.models import Event


# Same-run coalescing is intentionally narrower than cross-day matching. Only
# event families where one named entity normally refers to one material incident
# in a short window are eligible. Generic launches/partnerships are excluded to
# avoid collapsing distinct product announcements from the same company.
_FAMILY_TERMS: dict[str, tuple[str, ...]] = {
    "security_incident": (
        "breach", "data breach", "data leak", "leak", "leaked", "exposed", "phishing", "hack", "hacked",
        "資料外洩", "資料洩漏", "個資外洩", "外洩", "釣魚", "駭客", "遭駭",
    ),
    "earnings": (
        "earnings", "quarterly results", "revenue", "profit", "net income", "財報", "營收", "獲利", "淨利",
    ),
    "acquisition": (
        "acquire", "acquires", "acquisition", "buyout", "takeover", "merger", "收購", "併購", "合併",
    ),
    "funding_round": (
        "funding round", "raises", "raised", "series a", "series b", "series c", "募資", "融資輪", "完成融資",
    ),
    "layoffs": (
        "layoff", "layoffs", "job cuts", "cuts jobs", "workforce reduction", "裁員", "減員", "人力縮減",
    ),
}

_NAMED_TOKEN_STOPWORDS = {
    "about", "after", "apple", "breaking", "business", "company", "crypto", "data", "digital", "global",
    "market", "markets", "mobile", "new", "news", "report", "reports", "retail", "security", "technology",
    "today", "update", "updates", "world",
}


def coalesce_same_run_events(events: list[Event]) -> list[Event]:
    """Merge high-confidence sibling stories from different sources in one run.

    Requirements for a merge:
    - same canonical primary domain;
    - same high-precision event family;
    - at least one shared named Latin entity token (for example ``SafePal``);
    - publication timestamps within 36 hours.

    Indicator-only measurements are excluded. The function is deterministic and
    never uses embeddings or provider-specific metadata.
    """

    ordered = sorted(events, key=lambda event: event.event_id)
    groups: list[list[Event]] = []
    for event in ordered:
        match_indexes = [
            index for index, group in enumerate(groups) if _matches_group(event, group)
        ]
        if len(match_indexes) == 1:
            groups[match_indexes[0]].append(event)
        else:
            # Ambiguous matches are not forced. This mirrors the cross-day
            # resolver's conservative ambiguity policy.
            groups.append([event])

    merged = [_merge_group(group) for group in groups]
    return sorted(merged, key=lambda event: event.event_id)


def _matches_group(event: Event, group: list[Event]) -> bool:
    # Require the candidate to agree with every member already in the group;
    # this prevents transitive A~B~C chains from over-merging unrelated stories.
    return bool(group) and all(_same_story(event, member) for member in group)


def _same_story(left: Event, right: Event) -> bool:
    if not left.documents or not right.documents:
        return False
    if all(document.lane == "indicator_only" for document in left.documents):
        return False
    if all(document.lane == "indicator_only" for document in right.documents):
        return False

    left_domains = {document.primary_domain for document in left.documents}
    right_domains = {document.primary_domain for document in right.documents}
    if len(left_domains) != 1 or left_domains != right_domains:
        return False

    left_family = _event_family(left)
    right_family = _event_family(right)
    if not left_family or left_family != right_family:
        return False

    if not (_named_tokens(left) & _named_tokens(right)):
        return False
    return _within_hours(left.last_seen_at, right.last_seen_at, hours=36)


def _event_family(event: Event) -> str:
    text = " ".join(
        part.lower()
        for document in event.documents
        for part in (document.title, document.summary, document.action, document.object)
        if part
    )
    matches = [
        family
        for family, terms in _FAMILY_TERMS.items()
        if any(term.lower() in text for term in terms)
    ]
    return matches[0] if len(matches) == 1 else ""


def _named_tokens(event: Event) -> set[str]:
    values: set[str] = set()
    for document in event.documents:
        for token in re.findall(r"(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9._-]{3,}(?![A-Za-z0-9])", document.title):
            lowered = token.lower().strip("._-")
            if lowered in _NAMED_TOKEN_STOPWORDS:
                continue
            # Named entities normally preserve an internal/leading capital or
            # are all-caps tickers/brands. This rejects ordinary sentence words.
            if token[0].isupper() or any(char.isupper() for char in token[1:]):
                values.add(lowered)
    return values


def _within_hours(left: str, right: str, *, hours: int) -> bool:
    try:
        left_dt = _parse_timestamp(left)
        right_dt = _parse_timestamp(right)
    except ValueError:
        return False
    return abs(left_dt - right_dt) <= timedelta(hours=hours)


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _merge_group(group: list[Event]) -> Event:
    if len(group) == 1:
        return group[0]
    documents = []
    seen_ids: set[str] = set()
    for event in sorted(group, key=lambda item: item.event_id):
        for document in event.documents:
            if document.document_id in seen_ids:
                continue
            seen_ids.add(document.document_id)
            documents.append(document)
    return Event(
        # Reuse the deterministic smallest constituent ID; cross-day resolution
        # still performs the authoritative historical identity match later.
        event_id=min(event.event_id for event in group),
        documents=sorted(documents, key=lambda document: document.document_id),
        first_seen_at=min(event.first_seen_at for event in group),
        last_seen_at=max(event.last_seen_at for event in group),
        last_material_delta_at=max(event.last_material_delta_at for event in group),
        status="active",
        deltas=[],
    )
