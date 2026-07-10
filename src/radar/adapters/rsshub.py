from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RsshubAdapterConfig:
    base_url: str
    enabled: bool = False
    policy_note: str = "Adapter route only; final evidence must resolve to original source."
