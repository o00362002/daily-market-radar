"""Provider-neutral, deterministic cross-day event resolution.

This module never imports AI, embedding, network or persistence libraries. It
matches today's clustered events against prior events using an ordered cascade of
deterministic strategies and classifies the material delta of every matched
event. Ambiguous matches are never forced: a new event is created and an
``unresolved_match`` record is emitted instead.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime, timezone

from radar.domain.enums import DeltaType, MatchStrategy
from radar.domain.models import Document, Event, EventDelta, normalize_text


# --- Material-delta taxonomy -------------------------------------------------

MATERIAL_DELTA_TYPES: frozenset[str] = frozenset(
    {
        DeltaType.NEW_EVENT.value,
        # Legacy material members retained for backward compatibility.
        DeltaType.SAME_EVENT_NEW_DELTA.value,
        DeltaType.RELATED_STORYLINE_NEW_EVENT.value,
        DeltaType.TREND_EVIDENCE_ONLY.value,
        # PR B taxonomy.
        DeltaType.NEW_SOURCE_CONFIRMATION.value,
        DeltaType.NEW_ENTITY.value,
        DeltaType.NEW_AMOUNT_OR_METRIC.value,
        DeltaType.POLICY_STAGE_CHANGE.value,
        DeltaType.LAUNCH_OR_RELEASE.value,
        DeltaType.PILOT_TO_PRODUCTION.value,
        DeltaType.NEW_REGION.value,
        DeltaType.ADOPTION_EXPANSION.value,
        DeltaType.FUNDING_CHANGE.value,
        DeltaType.HIRING_CHANGE.value,
        DeltaType.SUPPLY_CHAIN_CHANGE.value,
        DeltaType.COUNTEREVIDENCE.value,
        DeltaType.DELAY.value,
        DeltaType.CANCELLATION.value,
        DeltaType.INVALIDATION.value,
        DeltaType.UNRESOLVED.value,
    }
)

NON_MATERIAL_DELTA_TYPES: frozenset[str] = frozenset(
    {
        DeltaType.DUPLICATE_DOCUMENT.value,
        DeltaType.NO_MATERIAL_CHANGE.value,
        DeltaType.SAME_EVENT_SAME_FACTS.value,
        DeltaType.BACKGROUND_ONLY.value,
        DeltaType.SAME_TOPIC_DIFFERENT_EVENT.value,
    }
)


def is_material_delta_type(delta_type: str) -> bool:
    return delta_type in MATERIAL_DELTA_TYPES


# --- Deterministic lexicons for lifecycle detection --------------------------

_CANCELLATION = {
    "cancel", "cancels", "cancelled", "canceled", "scrap", "scraps", "scrapped",
    "halt", "halts", "halted", "terminate", "terminates", "terminated", "abandon",
    "abandons", "abandoned", "取消", "終止", "撤回", "中止", "喊停",
}
_DELAY = {
    "delay", "delays", "delayed", "postpone", "postpones", "postponed", "slip",
    "slips", "slipped", "defer", "defers", "deferred", "pushback", "延遲", "推遲",
    "延後", "延期", "跳票",
}
_INVALIDATION = {
    "retract", "retracts", "retracted", "debunk", "debunks", "debunked", "false",
    "invalidate", "invalidated", "disproven", "fabricated", "撤稿", "造假", "不實",
    "推翻", "作假",
}
_COUNTEREVIDENCE = {
    "contradict", "contradicts", "refute", "refutes", "dispute", "disputes",
    "deny", "denies", "denied", "rebut", "rebuts", "反駁", "否認", "駁斥", "質疑",
}
_LAUNCH = {
    "launch", "launches", "launched", "release", "releases", "released", "ship",
    "ships", "shipped", "unveil", "unveils", "unveiled", "debut", "推出", "發布",
    "上線", "發表", "問世",
}
_PRODUCTION = {
    "production", "nationwide", "commercial", "mass-production", "generally",
    "availability", "量產", "全面", "商用", "正式", "規模化",
}
_PILOT = {
    "pilot", "trial", "test", "beta", "prototype", "poc", "試點", "試營運",
    "測試", "原型",
}
_POLICY = {
    "approve", "approves", "approved", "pass", "passes", "passed", "enact",
    "enacted", "propose", "proposes", "proposed", "draft", "ruling", "regulation",
    "ban", "bans", "banned", "sanction", "sanctions", "審核", "通過", "立法",
    "草案", "裁定", "監管", "禁令", "制裁", "核准", "法規",
}
_ADOPTION = {
    "adopt", "adopts", "adopted", "expand", "expands", "expanded", "deploy",
    "deploys", "deployed", "integrate", "integrates", "integrated", "採用",
    "擴大", "部署", "整合", "導入", "普及",
}

# Canonical metric namespaces that map to a specific delta family.
_METRIC_NAMESPACE_DELTA = {
    "funding": DeltaType.FUNDING_CHANGE.value,
    "hiring": DeltaType.HIRING_CHANGE.value,
    "supply": DeltaType.SUPPLY_CHAIN_CHANGE.value,
    "procurement": DeltaType.SUPPLY_CHAIN_CHANGE.value,
}

_OFFICIAL_ROLES = {"official", "primary", "regulator", "government", "exchange", "issuer"}

# Aggregation priority: strongest material signal wins when several are detected.
_DELTA_PRIORITY = [
    DeltaType.INVALIDATION.value,
    DeltaType.CANCELLATION.value,
    DeltaType.COUNTEREVIDENCE.value,
    DeltaType.DELAY.value,
    DeltaType.FUNDING_CHANGE.value,
    DeltaType.HIRING_CHANGE.value,
    DeltaType.SUPPLY_CHAIN_CHANGE.value,
    DeltaType.NEW_AMOUNT_OR_METRIC.value,
    DeltaType.POLICY_STAGE_CHANGE.value,
    DeltaType.PILOT_TO_PRODUCTION.value,
    DeltaType.LAUNCH_OR_RELEASE.value,
    DeltaType.NEW_REGION.value,
    DeltaType.NEW_ENTITY.value,
    DeltaType.ADOPTION_EXPANSION.value,
    DeltaType.NEW_SOURCE_CONFIRMATION.value,
    DeltaType.NO_MATERIAL_CHANGE.value,
    DeltaType.SAME_EVENT_SAME_FACTS.value,
    DeltaType.DUPLICATE_DOCUMENT.value,
]


@dataclass(frozen=True)
class EventMatchRecord:
    strategy: str
    confidence: float
    reason: str
    prior_event_id: str | None
    current_event_id: str
    matched_fields: tuple[str, ...]
    unresolved_fields: tuple[str, ...]
    observed_at: str


@dataclass(frozen=True)
class EventResolutionOutcome:
    events: list[Event]
    match_records: list[EventMatchRecord]
    unresolved_matches: list[EventMatchRecord]
    match_strategy_counts: dict[str, int]
    delta_type_counts: dict[str, int]
    new_events: int
    matched_existing_events: int
    material_events: int
    unchanged_events: int
    duplicate_only_events: int
    title_only_changes_rejected: int
    background_only_rejected: int

    @property
    def events_observed(self) -> int:
        return len(self.events)


def _tokens(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        normalized = normalize_text(value)
        tokens.update(part for part in normalized.replace("-", " ").split(" ") if part)
        # Keep CJK phrases as whole-string membership candidates.
        tokens.add(normalized)
    return tokens


def _text_tokens(document: Document) -> set[str]:
    return _tokens(document.title, document.action, document.object, document.summary)


def _matches_any(tokens: set[str], lexicon: set[str]) -> bool:
    if tokens & lexicon:
        return True
    # CJK substring detection (no whitespace segmentation).
    joined = " ".join(tokens)
    return any(term in joined for term in lexicon if not term.isascii())


def _source_role_rank(document: Document) -> int:
    roles = set(document.facts.get("source_roles") or ())
    if roles & _OFFICIAL_ROLES:
        return 2
    if roles:
        return 1
    return 0


def _publisher(document: Document) -> str:
    from urllib.parse import urlsplit

    return urlsplit(document.url).netloc.lower() or document.source_id.lower()


def _changed_metrics(prior: Document, current: Document) -> list[str]:
    keys = {key for key in prior.facts if key != "source_roles"}
    keys |= {key for key in current.facts if key != "source_roles"}
    return sorted(key for key in keys if prior.facts.get(key) != current.facts.get(key))


def _metric_delta_type(changed_metrics: list[str]) -> str:
    for metric in changed_metrics:
        namespace = metric.split("_", 1)[0]
        if namespace in _METRIC_NAMESPACE_DELTA:
            return _METRIC_NAMESPACE_DELTA[namespace]
    return DeltaType.NEW_AMOUNT_OR_METRIC.value


def classify_document_delta(prior: Document, current: Document) -> EventDelta:
    """Classify the delta between a prior and current document of the same story."""

    if prior.url == current.url or prior.content_hash == current.content_hash:
        return EventDelta(DeltaType.DUPLICATE_DOCUMENT.value, [], "same canonical url or content hash")
    if prior.event_signature != current.event_signature:
        return EventDelta(DeltaType.SAME_TOPIC_DIFFERENT_EVENT.value, [], "different event signature")

    changed_metrics = _changed_metrics(prior, current)
    if changed_metrics:
        delta_type = _metric_delta_type(changed_metrics)
        return EventDelta(delta_type, changed_metrics, "canonical structured measurement facts changed")

    current_tokens = _text_tokens(current)
    if _matches_any(current_tokens, _INVALIDATION):
        return EventDelta(DeltaType.INVALIDATION.value, ["narrative"], "invalidation language detected")
    if _matches_any(current_tokens, _CANCELLATION):
        return EventDelta(DeltaType.CANCELLATION.value, ["narrative"], "cancellation language detected")
    if _matches_any(current_tokens, _COUNTEREVIDENCE):
        return EventDelta(DeltaType.COUNTEREVIDENCE.value, ["narrative"], "counterevidence language detected")
    if _matches_any(current_tokens, _DELAY):
        return EventDelta(DeltaType.DELAY.value, ["narrative"], "delay language detected")

    new_entities = [entity for entity in current.entities if entity not in set(prior.entities)]
    prior_tokens = _text_tokens(prior)
    if _matches_any(current_tokens, _PRODUCTION) and _matches_any(prior_tokens, _PILOT):
        return EventDelta(DeltaType.PILOT_TO_PRODUCTION.value, ["stage"], "pilot progressed to production")
    if _matches_any(current_tokens, _POLICY):
        return EventDelta(DeltaType.POLICY_STAGE_CHANGE.value, ["policy_stage"], "policy stage language detected")
    if _matches_any(current_tokens, _LAUNCH):
        return EventDelta(DeltaType.LAUNCH_OR_RELEASE.value, ["stage"], "launch or release language detected")
    if current.macro_region != prior.macro_region or current.location != prior.location:
        return EventDelta(
            DeltaType.NEW_REGION.value,
            sorted({"macro_region", "location"} & _region_fields(prior, current)),
            "new region observed for the same event",
        )
    if new_entities:
        return EventDelta(DeltaType.NEW_ENTITY.value, ["entities"], "new named entity joined the event")
    if _matches_any(current_tokens, _ADOPTION):
        return EventDelta(DeltaType.ADOPTION_EXPANSION.value, ["adoption"], "adoption or expansion language detected")

    text_changed = []
    if prior.title_hash != current.title_hash:
        text_changed.append("title")
    if normalize_text(prior.summary) != normalize_text(current.summary):
        text_changed.append("summary")
    if text_changed:
        return EventDelta(
            DeltaType.NO_MATERIAL_CHANGE.value,
            sorted(text_changed),
            "only title/summary rewrite; supporting difference only, not material",
        )
    return EventDelta(DeltaType.SAME_EVENT_SAME_FACTS.value, [], "same event without material delta")


def _region_fields(prior: Document, current: Document) -> set[str]:
    fields: set[str] = set()
    if current.macro_region != prior.macro_region:
        fields.add("macro_region")
    if current.location != prior.location:
        fields.add("location")
    return fields


def _new_source_confirmation(prior_event: Event, current_event: Event) -> bool:
    """A new, independent, higher-or-equal-role publisher confirms the event."""

    prior_publishers = {_publisher(document) for document in prior_event.documents}
    prior_best_role = max((_source_role_rank(document) for document in prior_event.documents), default=0)
    for document in current_event.documents:
        if _publisher(document) in prior_publishers:
            continue  # same publisher, different URL is not independent confirmation
        if _source_role_rank(document) >= max(prior_best_role, 1):
            return True
    return False


def classify_event_delta(prior_event: Event, current_event: Event) -> EventDelta:
    """Aggregate document-level deltas plus event-level source confirmation."""

    if not prior_event.documents:
        return EventDelta(DeltaType.NEW_EVENT.value, ["event"], "no prior documents were attached")

    baseline = _latest_documents(prior_event.documents)
    detected: list[EventDelta] = []
    for current_document in current_event.documents:
        for prior_document in baseline:
            detected.append(classify_document_delta(prior_document, current_document))

    if detected and all(delta.delta_type == DeltaType.DUPLICATE_DOCUMENT.value for delta in detected):
        return EventDelta(DeltaType.DUPLICATE_DOCUMENT.value, [], "all current evidence is duplicate")

    material = [delta for delta in detected if is_material_delta_type(delta.delta_type)]
    if material:
        best = min(material, key=lambda delta: _priority_index(delta.delta_type))
        changed_fields = sorted({field for delta in material for field in delta.changed_fields})
        reasons = sorted({delta.reason for delta in material})
        return EventDelta(best.delta_type, changed_fields, "; ".join(reasons))

    if _new_source_confirmation(prior_event, current_event):
        return EventDelta(
            DeltaType.NEW_SOURCE_CONFIRMATION.value,
            ["source_roles"],
            "new independent higher-role publisher confirmed the event",
        )

    if detected and any(delta.delta_type == DeltaType.NO_MATERIAL_CHANGE.value for delta in detected):
        return EventDelta(
            DeltaType.NO_MATERIAL_CHANGE.value,
            [],
            "only title/summary rewrites; not a material delta",
        )
    return EventDelta(DeltaType.SAME_EVENT_SAME_FACTS.value, [], "same event without material delta")


def _priority_index(delta_type: str) -> int:
    try:
        return _DELTA_PRIORITY.index(delta_type)
    except ValueError:
        return len(_DELTA_PRIORITY)


# --- Matching cascade --------------------------------------------------------

_HIGH_CONFIDENCE = 0.9
_AMBIGUITY_MARGIN = 0.15


class EventResolutionService:
    """Deterministic, provider-neutral cross-day event resolver."""

    evaluator_id = "deterministic_event_resolution_v1"

    def __init__(self, *, time_window_days: int = 3) -> None:
        self._time_window_days = time_window_days

    def resolve(
        self,
        current_events: list[Event],
        prior_events: list[Event],
        *,
        observed_at: str,
    ) -> EventResolutionOutcome:
        prior_by_id = {event.event_id: event for event in prior_events}
        reconciled: list[Event] = []
        match_records: list[EventMatchRecord] = []
        unresolved_matches: list[EventMatchRecord] = []
        strategy_counts: Counter[str] = Counter()
        delta_counts: Counter[str] = Counter()
        new_events = matched = material = unchanged = duplicate_only = 0
        title_only_rejected = background_rejected = 0

        for current in current_events:
            record = self._match(current, prior_events, observed_at=observed_at)
            match_records.append(record)
            strategy_counts[record.strategy] += 1

            prior = prior_by_id.get(record.prior_event_id) if record.prior_event_id else None
            if prior is None or record.strategy == MatchStrategy.UNRESOLVED.value:
                if record.strategy == MatchStrategy.UNRESOLVED.value:
                    unresolved_matches.append(record)
                delta = EventDelta(
                    DeltaType.NEW_EVENT.value,
                    ["event"],
                    "first confident observation in the lookback window",
                )
                reconciled.append(replace(current, deltas=[delta]))
                new_events += 1
                material += 1
                delta_counts[delta.delta_type] += 1
                continue

            matched += 1
            delta = classify_event_delta(prior, current)
            delta_counts[delta.delta_type] += 1
            if delta.delta_type == DeltaType.NO_MATERIAL_CHANGE.value:
                title_only_rejected += 1
            if delta.delta_type == DeltaType.BACKGROUND_ONLY.value:
                background_rejected += 1
            if delta.delta_type == DeltaType.DUPLICATE_DOCUMENT.value:
                duplicate_only += 1

            is_material = is_material_delta_type(delta.delta_type)
            if is_material:
                material += 1
            else:
                unchanged += 1
            reconciled.append(
                Event(
                    event_id=current.event_id,
                    documents=current.documents,
                    first_seen_at=prior.first_seen_at,
                    last_seen_at=_max_timestamp(prior.last_seen_at, current.last_seen_at),
                    last_material_delta_at=current.last_seen_at if is_material else prior.last_material_delta_at,
                    status="active",
                    deltas=[delta],
                )
            )

        reconciled.sort(key=lambda event: event.event_id)
        return EventResolutionOutcome(
            events=reconciled,
            match_records=match_records,
            unresolved_matches=unresolved_matches,
            match_strategy_counts=dict(sorted(strategy_counts.items())),
            delta_type_counts=dict(sorted(delta_counts.items())),
            new_events=new_events,
            matched_existing_events=matched,
            material_events=material,
            unchanged_events=unchanged,
            duplicate_only_events=duplicate_only,
            title_only_changes_rejected=title_only_rejected,
            background_only_rejected=background_rejected,
        )

    def _match(self, current: Event, prior_events: list[Event], *, observed_at: str) -> EventMatchRecord:
        candidates: list[tuple[float, str, Event, tuple[str, ...], str]] = []
        cur_doc_ids = {document.document_id for document in current.documents}
        cur_urls = {document.url for document in current.documents}
        cur_hashes = {document.content_hash for document in current.documents}
        cur_sig = _event_signature(current)

        for prior in prior_events:
            prior_doc_ids = {document.document_id for document in prior.documents}
            prior_urls = {document.url for document in prior.documents}
            prior_hashes = {document.content_hash for document in prior.documents}
            prior_sig = _event_signature(prior)

            if cur_doc_ids & prior_doc_ids:
                candidates.append((1.0, MatchStrategy.EXACT_DOCUMENT_ID.value, prior, ("document_id",), "shared document id"))
            elif cur_urls & prior_urls:
                candidates.append((0.98, MatchStrategy.CANONICAL_URL.value, prior, ("canonical_url",), "shared canonical url"))
            elif cur_hashes & prior_hashes:
                candidates.append((0.96, MatchStrategy.CONTENT_HASH.value, prior, ("content_hash",), "shared content hash"))
            elif prior.event_id == current.event_id:
                candidates.append(
                    (0.92, MatchStrategy.EXACT_EVENT_SIGNATURE.value, prior, ("entity", "action", "object", "location"), "identical event signature")
                )
            elif _normalized_signature_match(cur_sig, prior_sig):
                candidates.append(
                    (0.8, MatchStrategy.NORMALIZED_SIGNATURE.value, prior, ("entity", "object"), "normalized entity/object match")
                )
            elif _structured_fact_overlap(current, prior):
                candidates.append(
                    (0.6, MatchStrategy.STRUCTURED_FACT_OVERLAP.value, prior, ("measurements",), "shared structured measurement across independent sources")
                )
            elif self._within_time_window(current, prior) and cur_sig[0] and cur_sig[0] == prior_sig[0]:
                candidates.append(
                    (0.45, MatchStrategy.PUBLICATION_TIME_WINDOW.value, prior, ("entity",), "same entity within bounded publication window")
                )

        if not candidates:
            return EventMatchRecord(
                strategy=DeltaType.NEW_EVENT.value,
                confidence=0.0,
                reason="no prior event matched any strategy",
                prior_event_id=None,
                current_event_id=current.event_id,
                matched_fields=(),
                unresolved_fields=("entity", "action", "object", "location"),
                observed_at=observed_at,
            )

        candidates.sort(key=lambda item: (-item[0], item[2].event_id))
        confidence, strategy, prior, matched_fields, reason = candidates[0]

        if confidence < _HIGH_CONFIDENCE:
            competitors = [
                item
                for item in candidates
                if item[2].event_id != prior.event_id and confidence - item[0] <= _AMBIGUITY_MARGIN
            ]
            if competitors:
                return EventMatchRecord(
                    strategy=MatchStrategy.UNRESOLVED.value,
                    confidence=confidence,
                    reason="ambiguous fuzzy match to multiple prior events; not forcing a merge",
                    prior_event_id=None,
                    current_event_id=current.event_id,
                    matched_fields=matched_fields,
                    unresolved_fields=("prior_event_id",),
                    observed_at=observed_at,
                )

        return EventMatchRecord(
            strategy=strategy,
            confidence=confidence,
            reason=reason,
            prior_event_id=prior.event_id,
            current_event_id=current.event_id,
            matched_fields=matched_fields,
            unresolved_fields=(),
            observed_at=observed_at,
        )

    def _within_time_window(self, current: Event, prior: Event) -> bool:
        try:
            delta = abs((_parse_timestamp(current.last_seen_at) - _parse_timestamp(prior.last_seen_at)).days)
        except ValueError:
            return False
        return delta <= self._time_window_days


def _event_signature(event: Event) -> tuple[str, str, str, str]:
    if not event.documents:
        return ("", "", "", "")
    return event.documents[0].event_signature


def _normalized_signature_match(left: tuple[str, str, str, str], right: tuple[str, str, str, str]) -> bool:
    if not left[0] or not right[0]:
        return False
    entity_match = left[0] == right[0]
    object_match = left[2] == right[2] and bool(left[2])
    action_or_location = (left[1] == right[1] and bool(left[1])) or (left[3] == right[3] and bool(left[3]))
    return entity_match and object_match and action_or_location


def _structured_fact_overlap(current: Event, prior: Event) -> bool:
    current_metrics = {
        (metric, current.documents[0].facts.get(metric))
        for document in current.documents
        for metric in document.facts
        if metric != "source_roles"
    }
    prior_metrics = {
        (metric, prior.documents[0].facts.get(metric))
        for document in prior.documents
        for metric in document.facts
        if metric != "source_roles"
    }
    if not current_metrics or not prior_metrics:
        return False
    shared_metric_ids = {metric for metric, _ in current_metrics} & {metric for metric, _ in prior_metrics}
    if not shared_metric_ids:
        return False
    current_publishers = {_publisher(document) for document in current.documents}
    prior_publishers = {_publisher(document) for document in prior.documents}
    return bool(current_publishers - prior_publishers) or bool(prior_publishers - current_publishers)


def _max_timestamp(left: str, right: str) -> str:
    return left if _parse_timestamp(left) >= _parse_timestamp(right) else right


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _latest_documents(documents: list[Document]) -> list[Document]:
    if not documents:
        return []
    latest = max(_parse_timestamp(document.fetched_at) for document in documents)
    return [document for document in documents if _parse_timestamp(document.fetched_at) == latest]
