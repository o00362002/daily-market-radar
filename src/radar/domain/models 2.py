from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = urlencode(
        [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key not in TRACKING_PARAMS]
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


def stable_id(prefix: str, parts: list[str]) -> str:
    key = "|".join(normalize_text(part) for part in parts if part)
    return f"{prefix}_{hashlib.sha256(key.encode('utf-8')).hexdigest()[:12]}"


@dataclass(frozen=True)
class EvidenceLink:
    url: str
    source_id: str
    fetched_at: str

    def to_dict(self) -> dict[str, str]:
        return {"url": self.url, "source_id": self.source_id, "fetched_at": self.fetched_at}


@dataclass(frozen=True)
class Document:
    document_id: str
    source_id: str
    url: str
    title: str
    language: str
    macro_region: str
    published_at: str
    fetched_at: str
    entities: list[str] = field(default_factory=list)
    action: str = ""
    object: str = ""
    location: str = ""
    primary_domain: str = "ai_agents_applications"
    lane: str = "top_down"
    facts: dict[str, Any] = field(default_factory=dict)
    summary: str = ""

    @classmethod
    def fixture(cls, **kwargs: Any) -> "Document":
        data = {
            "source_id": "fixture_source",
            "url": "https://example.com/fixture",
            "title": "Fixture document",
            "language": "en",
            "macro_region": "North America",
            "published_at": "2026-07-10T08:00:00+08:00",
            "fetched_at": "2026-07-10T08:01:00+08:00",
            "entities": ["Fixture"],
            "action": "reports",
            "object": "fixture",
            "location": "Global",
            "primary_domain": "ai_agents_applications",
            "lane": "top_down",
            "facts": {},
            "summary": "",
        }
        data.update(kwargs)
        canonical = canonicalize_url(data["url"])
        data["url"] = canonical
        data["document_id"] = stable_id("doc", [data["source_id"], canonical, data["title"]])
        return cls(**data)

    @property
    def title_hash(self) -> str:
        return hashlib.sha256(normalize_text(self.title).encode("utf-8")).hexdigest()

    @property
    def content_hash(self) -> str:
        base = f"{self.title}|{self.summary}|{self.facts}"
        return hashlib.sha256(normalize_text(base).encode("utf-8")).hexdigest()

    @property
    def event_signature(self) -> tuple[str, str, str, str]:
        entity = normalize_text(self.entities[0] if self.entities else self.source_id)
        return (entity, normalize_text(self.action), normalize_text(self.object), normalize_text(self.location))

    def evidence_link(self) -> EvidenceLink:
        return EvidenceLink(url=self.url, source_id=self.source_id, fetched_at=self.fetched_at)


@dataclass(frozen=True)
class Event:
    event_id: str
    documents: list[Document]
    first_seen_at: str
    last_seen_at: str
    last_material_delta_at: str
    status: str = "active"


@dataclass(frozen=True)
class EventDelta:
    delta_type: str
    changed_fields: list[str]
    reason: str


@dataclass(frozen=True)
class Signal:
    signal_id: str
    event_id: str
    lifecycle: str
    what_would_confirm: str
    what_would_invalidate: str
    next_check_at: str


@dataclass(frozen=True)
class CoverageCell:
    domain: str
    macro_region: str
    language: str
    source_role: str
    channel: str
    time_window: str
    status: str
    observed_count: int = 0


@dataclass(frozen=True)
class ReportItem:
    item_id: str
    event_id: str
    signal_id: str | None
    primary_domain: str
    headline: str
    first_seen_at: str
    today_delta: str
    importance_score: int
    potential_score: int
    confidence_score: int
    evidence_links: list[EvidenceLink]
    direct_taiwan_evidence: list[EvidenceLink]
    taiwan_implication: str
    counterevidence: list[str]
    uncertainties: list[str]
    next_watch: str

    @classmethod
    def fixture(cls, **kwargs: Any) -> "ReportItem":
        data = {
            "item_id": "item_fixture",
            "event_id": "evt_fixture",
            "signal_id": None,
            "primary_domain": "ai_agents_applications",
            "headline": "Fixture headline",
            "first_seen_at": "2026-07-10T08:00:00+08:00",
            "today_delta": "Fixture delta.",
            "importance_score": 60,
            "potential_score": 50,
            "confidence_score": 80,
            "evidence_links": [
                EvidenceLink(
                    url="https://example.com/fixture",
                    source_id="fixture_source",
                    fetched_at="2026-07-10T08:01:00+08:00",
                )
            ],
            "direct_taiwan_evidence": [],
            "taiwan_implication": "",
            "counterevidence": [],
            "uncertainties": [],
            "next_watch": "Watch next update.",
        }
        data.update(kwargs)
        return cls(**data)

    @property
    def taiwan_direct_count(self) -> int:
        return len(self.direct_taiwan_evidence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "event_id": self.event_id,
            "signal_id": self.signal_id,
            "primary_domain": self.primary_domain,
            "headline": self.headline,
            "first_seen_at": self.first_seen_at,
            "today_delta": self.today_delta,
            "importance_score": self.importance_score,
            "potential_score": self.potential_score,
            "confidence_score": self.confidence_score,
            "evidence_links": [link.to_dict() for link in self.evidence_links],
            "direct_taiwan_evidence": [link.to_dict() for link in self.direct_taiwan_evidence],
            "taiwan_implication": self.taiwan_implication,
            "counterevidence": self.counterevidence,
            "uncertainties": self.uncertainties,
            "next_watch": self.next_watch,
        }


@dataclass(frozen=True)
class RunResult:
    run_id: str
    status: str
    degradation_reasons: list[str]
    languages_seen: list[str]
    regions_seen: list[str]
    domains_seen: list[str]
    event_ids: list[str]
    selected_item_ids: list[str]
    report: dict[str, Any]
