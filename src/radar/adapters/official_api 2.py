from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OfficialApiAdapterConfig:
    source_id: str
    endpoint: str
    usage_policy: str
