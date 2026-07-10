from __future__ import annotations

from radar.domain.models import Event, Signal, stable_id
from radar.domain.potential import PotentialAssessment, assess_event, next_check_at


__all__ = ["PotentialAssessment", "assess_event", "classify_potential_signals"]


def classify_potential_signals(events: list[Event]) -> list[Signal]:
    signals: list[Signal] = []
    for event in events:
        assessment = assess_event(event)
        if assessment.lane != "potential":
            continue
        signals.append(
            Signal(
                signal_id=stable_id("sig", [event.event_id]),
                event_id=event.event_id,
                lifecycle=assessment.lifecycle or "seed",
                what_would_confirm="後續獨立採用、採購、使用量、資金、招聘、跨區域擴散或監管進展。",
                what_would_invalidate="後續沒有重複證據、試點終止，或出現可信反證。",
                next_check_at=next_check_at(event),
            )
        )
    return signals
