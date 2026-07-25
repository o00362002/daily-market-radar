from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class CompetitorSourceSpec:
    source_id: str
    channel: str
    url: str
    material_similarity_threshold: float


@dataclass(frozen=True)
class CompetitorTarget:
    competitor_id: str
    group: str
    name: str
    market: str
    relationship: str
    priority: str
    sources: tuple[CompetitorSourceSpec, ...]


class CompetitorMonitoringRegistry:
    def __init__(
        self,
        *,
        competitor_registry_version: str,
        source_registry_version: str,
        state_key: str,
        timeout_seconds: int,
        max_workers: int,
        minimum_visible_characters: int,
        targets: tuple[CompetitorTarget, ...],
        excluded_registry_groups: tuple[str, ...],
    ) -> None:
        self.competitor_registry_version = competitor_registry_version
        self.source_registry_version = source_registry_version
        self.state_key = state_key
        self.timeout_seconds = timeout_seconds
        self.max_workers = max_workers
        self.minimum_visible_characters = minimum_visible_characters
        self.targets = targets
        self.excluded_registry_groups = excluded_registry_groups

    @classmethod
    def from_files(cls, competitor_registry_path: Path, source_registry_path: Path) -> "CompetitorMonitoringRegistry":
        competitors = json.loads(competitor_registry_path.read_text(encoding="utf-8"))
        source_config = json.loads(source_registry_path.read_text(encoding="utf-8"))
        excluded = tuple(source_config.get("excluded_registry_groups", ()))
        default_threshold = float(source_config.get("default_material_similarity_threshold", 0.96))
        configured_sources = source_config.get("sources", {})

        targets: list[CompetitorTarget] = []
        fixed_ids: set[str] = set()
        for group in competitors["group_order"]:
            if group in excluded:
                continue
            for entry in competitors["groups"][group]:
                competitor_id = str(entry["id"])
                fixed_ids.add(competitor_id)
                source_rows = configured_sources.get(competitor_id, [])
                sources = tuple(
                    CompetitorSourceSpec(
                        source_id=str(row["id"]),
                        channel=str(row["channel"]),
                        url=str(row["url"]),
                        material_similarity_threshold=float(
                            row.get("material_similarity_threshold", default_threshold)
                        ),
                    )
                    for row in source_rows
                )
                targets.append(
                    CompetitorTarget(
                        competitor_id=competitor_id,
                        group=group,
                        name=str(entry["name"]),
                        market=str(entry["market"]),
                        relationship=str(entry["relationship"]),
                        priority=str(entry["priority"]),
                        sources=sources,
                    )
                )

        registry = cls(
            competitor_registry_version=str(competitors["version"]),
            source_registry_version=str(source_config["version"]),
            state_key=str(source_config["state_key"]),
            timeout_seconds=int(source_config.get("default_timeout_seconds", 12)),
            max_workers=int(source_config.get("max_workers", 8)),
            minimum_visible_characters=int(source_config.get("minimum_visible_characters", 160)),
            targets=tuple(targets),
            excluded_registry_groups=excluded,
        )
        registry.validate(configured_ids=set(configured_sources), fixed_ids=fixed_ids)
        return registry

    def validate(self, *, configured_ids: set[str] | None = None, fixed_ids: set[str] | None = None) -> None:
        if not self.state_key:
            raise ValueError("competitor monitoring state_key is required")
        if self.timeout_seconds <= 0:
            raise ValueError("competitor monitoring timeout must be positive")
        if self.max_workers <= 0:
            raise ValueError("competitor monitoring max_workers must be positive")
        if self.minimum_visible_characters < 1:
            raise ValueError("minimum_visible_characters must be positive")

        target_ids = [target.competitor_id for target in self.targets]
        if len(target_ids) != len(set(target_ids)):
            raise ValueError("duplicate competitor monitoring target id")
        if configured_ids is not None and fixed_ids is not None:
            missing = fixed_ids - configured_ids
            unknown = configured_ids - fixed_ids
            if missing or unknown:
                raise ValueError(
                    f"competitor source coverage mismatch; missing={sorted(missing)}, unknown={sorted(unknown)}"
                )

        for target in self.targets:
            if not target.sources:
                raise ValueError(f"fixed competitor lacks executable official source: {target.competitor_id}")
            source_ids = [source.source_id for source in target.sources]
            if len(source_ids) != len(set(source_ids)):
                raise ValueError(f"duplicate source id for competitor: {target.competitor_id}")
            for source in target.sources:
                parts = urlsplit(source.url)
                if parts.scheme != "https" or not parts.netloc:
                    raise ValueError(f"invalid official competitor URL: {source.url}")
                if not 0.0 <= source.material_similarity_threshold <= 1.0:
                    raise ValueError(f"invalid material threshold: {source.url}")
