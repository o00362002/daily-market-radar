from __future__ import annotations

from radar.domain.models import Signal


def group_weekly_signals(signals: list[Signal]) -> dict[str, list[str]]:
    return {"seed": [signal.signal_id for signal in signals if signal.lifecycle == "seed"]}
