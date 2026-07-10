"""Thin pipeline wrappers over the provider-neutral event resolution domain.

The deterministic matching cascade and delta taxonomy live in
``radar.domain.event_resolution``. These wrappers preserve the historical
pipeline API used across the codebase and tests.
"""

from __future__ import annotations

from radar.domain.event_resolution import (
    EventResolutionOutcome,
    EventResolutionService,
    classify_document_delta,
    classify_event_delta as _classify_event_delta,
)
from radar.domain.models import Document, Event, EventDelta
from radar.domain.scoring import event_has_material_delta

_DEFAULT_SERVICE = EventResolutionService()


def classify_event_delta(prior: Document, current: Document) -> EventDelta:
    """Document-level delta classification (kept for backward-compatible callers)."""

    return classify_document_delta(prior, current)


def classify_event_material_delta(prior: Event, current: Event) -> EventDelta:
    return _classify_event_delta(prior, current)


def resolve_events(
    current_events: list[Event],
    prior_events: list[Event],
    *,
    observed_at: str,
) -> EventResolutionOutcome:
    return _DEFAULT_SERVICE.resolve(current_events, prior_events, observed_at=observed_at)


def reconcile_cross_day_events(current_events: list[Event], prior_events: list[Event]) -> list[Event]:
    observed_at = current_events[0].last_seen_at if current_events else ""
    return _DEFAULT_SERVICE.resolve(current_events, prior_events, observed_at=observed_at).events


def material_events(events: list[Event]) -> list[Event]:
    return [event for event in events if event_has_material_delta(event)]
