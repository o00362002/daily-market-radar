from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MediaCloudDiscoveryStatus:
    available: bool
    role: str = "external_benchmark_only"
