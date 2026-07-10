from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
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

CANONICAL_METRIC_NAMESPACES = {
    "adoption",
    "amount",
    "cost",
    "count",
    "demand",
    "fees",
    "flow",
    "funding",
    "hiring",
    "index",
    "inventory",
    "margin",
    "market",
    "membership",
    "oi",
    "price",
    "procurement",
    "rate",
    "ratio",
    "revenue",
    "sales",
    "supply",
    "traffic",
    "tvl",
    "volume",
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
class MeasurementFact:
    metric_id: str
    value: int | float
    unit: str = ""

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", self.metric_id):
            raise ValueError(f"invalid canonical metric_id: {self.metric_id}")
        namespace = self.metric_id.split("_", 1)[0]
        if namespace not in CANONICAL_METRIC_NAMESPACES:
            raise ValueError(f"unknown canonical metric namespace: {namespace}")


@dataclass(frozen=True)
class CanonicalFacts:
    """Allowlisted fact shape produced after provider normalization.

    Dynamic metric names are values of ``MeasurementFact.metric_id`` rather than
    provider-defined fields on a canonical model. Transport metadata and nested
    provider payloads therefore cannot be assigned to ``Document.facts``.
    """

    source_roles: tuple[str, ...] = ()
    measurements: tuple[MeasurementFact, ...] = ()

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "CanonicalFacts":
        source_roles: tuple[str, ...] = ()
        measurements: list[MeasurementFact] = []
        for key, value in values.items():
            if key == "source_roles":
                if not isinstance(value, (list, tuple)) or not all(isinstance(role, str) for role in value):
                    raise ValueError("source_roles must be a list of strings")
                source_roles = tuple(sorted(set(value)))
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"non-canonical document fact {key!r}; normalize it to source_roles or a numeric measurement"
                )
            measurements.append(MeasurementFact(metric_id=key, value=value))
        return cls(
            source_roles=source_roles,
            measurements=tuple(sorted(measurements, key=lambda fact: fact.metric_id)),
        )

    def __iter__(self) -> Iterator[str]:
        if self.source_roles:
            yield "source_roles"
        yield from (measurement.metric_id for measurement in self.measurements)

    def get(self, key: str, default: Any = None) -> Any:
        if key == "source_roles" and self.source_roles:
            return list(self.source_roles)
        for measurement in self.measurements:
            if measurement.metric_id == key:
                return measurement.value
        return default


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
    facts: CanonicalFacts = field(default_factory=CanonicalFacts)
    summary: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.facts, dict):
            object.__setattr__(self, "facts", CanonicalFacts.from_mapping(self.facts))
        elif not isinstance(self.facts, CanonicalFacts):
            raise ValueError("facts must be CanonicalFacts or a compatible legacy mapping")

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
    deltas: list["EventDelta"] = field(default_factory=list)


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
    score_explanation: dict[str, Any] = field(default_factory=dict)
    report_lane: str = "major"
    candidate_type: str | None = None
    formation_level: str | None = None

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
            "score_explanation": {
                "importance": {"base": 60},
                "potential": {"base": 50},
                "confidence": {"base": 80},
                "rationale": "Fixture scoring uses fixed deterministic defaults.",
            },
            "report_lane": "major",
            "candidate_type": None,
            "formation_level": None,
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
            "report_lane": self.report_lane,
            "candidate_type": self.candidate_type,
            "formation_level": self.formation_level,
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
            "score_explanation": self.score_explanation,
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
