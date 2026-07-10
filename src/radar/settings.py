from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    timezone: str = "Asia/Taipei"
    source_registry_path: str = "config/source_registry.yaml"
    report_profile_path: str = "config/report_profiles.yaml"
    coverage_policy_path: str = "config/coverage_policy.yaml"
    taxonomy_path: str = "config/taxonomy.yaml"

    @classmethod
    def from_repo(cls, repo_root: Path | str) -> "Settings":
        return cls(repo_root=Path(repo_root).resolve())

    def path(self, relative: str) -> Path:
        return self.repo_root / relative
