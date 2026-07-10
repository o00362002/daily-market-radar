from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GdeltDiscoveryStatus:
    available: bool
    role: str = "external_gap_discovery_only"
