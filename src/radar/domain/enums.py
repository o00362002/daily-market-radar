from __future__ import annotations

from enum import Enum


class FeedHealth(str, Enum):
    HEALTHY = "healthy"
    STALE = "stale"
    EMPTY = "empty"
    SILENT_ZERO = "silent_zero"
    FAILING = "failing"
    DISABLED = "disabled"
    POLICY_BLOCKED = "policy_blocked"


class DeltaType(str, Enum):
    # --- Structural lifecycle (legacy members retained for backward compatibility) ---
    NEW_EVENT = "new_event"
    DUPLICATE_DOCUMENT = "duplicate_document"
    SAME_EVENT_SAME_FACTS = "same_event_same_facts"
    SAME_EVENT_NEW_DELTA = "same_event_new_delta"
    RELATED_STORYLINE_NEW_EVENT = "related_storyline_new_event"
    SAME_TOPIC_DIFFERENT_EVENT = "same_topic_but_different_event"
    TREND_EVIDENCE_ONLY = "trend_evidence_only"

    # --- Material-delta taxonomy (PR B: provider-neutral, deterministic) ---
    NO_MATERIAL_CHANGE = "no_material_change"
    NEW_SOURCE_CONFIRMATION = "new_source_confirmation"
    NEW_ENTITY = "new_entity"
    NEW_AMOUNT_OR_METRIC = "new_amount_or_metric"
    POLICY_STAGE_CHANGE = "policy_stage_change"
    LAUNCH_OR_RELEASE = "launch_or_release"
    PILOT_TO_PRODUCTION = "pilot_to_production"
    NEW_REGION = "new_region"
    ADOPTION_EXPANSION = "adoption_expansion"
    FUNDING_CHANGE = "funding_change"
    HIRING_CHANGE = "hiring_change"
    SUPPLY_CHAIN_CHANGE = "supply_chain_change"
    COUNTEREVIDENCE = "counterevidence"
    DELAY = "delay"
    CANCELLATION = "cancellation"
    INVALIDATION = "invalidation"
    BACKGROUND_ONLY = "background_only"
    UNRESOLVED = "unresolved"


class MatchStrategy(str, Enum):
    """Ordered, deterministic cross-day matching strategies (highest confidence first)."""

    EXACT_DOCUMENT_ID = "exact_document_id"
    CANONICAL_URL = "canonical_url"
    CONTENT_HASH = "content_hash"
    EXACT_EVENT_SIGNATURE = "exact_event_signature"
    NORMALIZED_SIGNATURE = "normalized_entity_action_object_location"
    STRUCTURED_FACT_OVERLAP = "source_independent_structured_fact_overlap"
    PUBLICATION_TIME_WINDOW = "bounded_publication_time_window"
    UNRESOLVED = "unresolved"


class SignalLifecycle(str, Enum):
    SEED = "seed"
    REPEATED = "repeated"
    DIFFUSING = "diffusing"
    VALIDATED = "validated"
    ADOPTED = "adopted"
    SCALING = "scaling"
    MAINSTREAM = "mainstream"
    FADING = "fading"
    INVALIDATED = "invalidated"
