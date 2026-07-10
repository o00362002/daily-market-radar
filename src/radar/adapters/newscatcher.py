from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsCatcherAdapterConfig:
    enabled: bool = False
    requires_api_key: bool = True
