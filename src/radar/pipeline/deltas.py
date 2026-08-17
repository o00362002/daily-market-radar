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
from radar.domain.scoring import event_has_material_delta, event_is_reportable_for_date
from radar.pipeline.coalesce import coalesce_same_run_events
from radar.pipeline.freshness import document_is_in_report_window

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
    coalesced = coalesce_same_run_events(current_events)
    return _DEFAULT_SERVICE.resolve(coalesced, prior_events, observed_at=observed_at)


def reconcile_cross_day_events(current_events: list[Event], prior_events: list[Event]) -> list[Event]:
    observed_at = current_events[0].last_seen_at if current_events else ""
    coalesced = coalesce_same_run_events(current_events)
    return _DEFAULT_SERVICE.resolve(coalesced, prior_events, observed_at=observed_at).events


def material_events(events: list[Event], *, report_date: str | None = None) -> list[Event]:
    """Fresh daily-news events worth reporting.

    Without ``report_date``: pure delta materiality (legacy semantics). With
    ``report_date``: keep the same-day union behavior, but require at least one
    document published inside the bounded Taiwan report window. This prevents
    archive entries returned by RSS feeds from becoming fresh ``new_event`` rows.

    Structured measurements intentionally do not use this function as their sole
    evaluator gate; see ``indicator_events_for_date`` below.
    """

    if report_date is None:
        return [event for event in events if event_has_material_delta(event)]
    return [
        event
        for event in events
        if event_is_reportable_for_date(event, report_date)
        and any(document_is_in_report_window(document, report_date) for document in event.documents)
    ]


def indicator_events_for_date(events: list[Event], *, report_date: str) -> list[Event]:
    """Return indicator-only events with a material anchor in this Taiwan day.

    Quarterly/monthly datasets describe an observation period and therefore may
    legitimately have ``published_at`` outside the daily-news freshness window.
    They should still reach matrices/structural indicators when the event is new,
    materially changed, or retained by a same-day rerun. On later days an
    unchanged measurement is excluded, so one quarterly release cannot cast a
    fresh structural vote every morning.
    """

    return [
        event
        for event in events
        if event.documents
        and all(document.lane == "indicator_only" for document in event.documents)
        and event_is_reportable_for_date(event, report_date)
    ]
