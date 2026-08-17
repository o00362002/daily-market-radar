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
from radar.pipeline.indicator_deltas import (
    indicator_measurement_delta,
    promote_indicator_measurement_deltas,
)

_DEFAULT_SERVICE = EventResolutionService()


def classify_event_delta(prior: Document, current: Document) -> EventDelta:
    """Document-level delta classification (kept for backward-compatible callers)."""

    return classify_document_delta(prior, current)


def classify_event_material_delta(prior: Event, current: Event) -> EventDelta:
    promoted = indicator_measurement_delta(prior, current)
    return promoted or _classify_event_delta(prior, current)


def resolve_events(
    current_events: list[Event],
    prior_events: list[Event],
    *,
    observed_at: str,
) -> EventResolutionOutcome:
    coalesced = coalesce_same_run_events(current_events)
    outcome = _DEFAULT_SERVICE.resolve(coalesced, prior_events, observed_at=observed_at)
    return promote_indicator_measurement_deltas(
        outcome,
        current_events=coalesced,
        prior_events=prior_events,
    )


def reconcile_cross_day_events(current_events: list[Event], prior_events: list[Event]) -> list[Event]:
    observed_at = current_events[0].last_seen_at if current_events else ""
    return resolve_events(current_events, prior_events, observed_at=observed_at).events


def material_events(events: list[Event], *, report_date: str | None = None) -> list[Event]:
    """Events eligible for the deterministic evaluator.

    News events must have a current material/same-day anchor *and* at least one
    document inside the bounded Taiwan news window. That keeps archive entries
    returned by RSS feeds from becoming fresh ``new_event`` rows.

    ``indicator_only`` structured measurements use the same current material /
    same-day anchor but intentionally do not require a fresh publication date.
    A quarterly observation can therefore reach a structural indicator on the day
    the measurement is first collected or materially changes. Downstream report
    qualification still rejects indicator-only events from Major/Potential cards,
    and an unchanged quarterly measurement does not cast a new vote on later days.
    """

    if report_date is None:
        return [event for event in events if event_has_material_delta(event)]

    selected: list[Event] = []
    for event in events:
        if not event_is_reportable_for_date(event, report_date):
            continue
        if event.documents and all(document.lane == "indicator_only" for document in event.documents):
            selected.append(event)
            continue
        if any(document_is_in_report_window(document, report_date) for document in event.documents):
            selected.append(event)
    return selected
