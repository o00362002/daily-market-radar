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
    DUPLICATE_DOCUMENT = "duplicate_document"
    SAME_EVENT_SAME_FACTS = "same_event_same_facts"
    SAME_EVENT_NEW_DELTA = "same_event_new_delta"
    RELATED_STORYLINE_NEW_EVENT = "related_storyline_new_event"
    SAME_TOPIC_DIFFERENT_EVENT = "same_topic_but_different_event"
    TREND_EVIDENCE_ONLY = "trend_evidence_only"


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
