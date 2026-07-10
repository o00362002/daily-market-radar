from __future__ import annotations

from radar.domain.models import Event, Signal, stable_id


def classify_potential_signals(events: list[Event]) -> list[Signal]:
    signals: list[Signal] = []
    for event in events:
        lane = event.documents[0].lane if event.documents else "top_down"
        if lane != "bottom_up":
            continue
        signals.append(
            Signal(
                signal_id=stable_id("sig", [event.event_id]),
                event_id=event.event_id,
                lifecycle="seed",
                what_would_confirm="Independent adoption, funding, procurement, usage, or regulatory follow-up.",
                what_would_invalidate="No repeat evidence or credible counterevidence in the next review window.",
                next_check_at="2026-07-17T09:00:00+08:00",
            )
        )
    return signals
