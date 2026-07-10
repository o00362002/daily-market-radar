from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProfileContract:
    major_slot_cap_per_domain: int | None
    potential_slot_cap_per_domain: int | None
    slot_caps_are_completeness_proof: bool


@dataclass(frozen=True)
class RuntimeContract:
    report_domains: list[str]
    domain_aliases: dict[str, str]
    profiles: dict[str, ProfileContract]
    completion_requires: list[str]
    structural_indicator_ids: list[str]
    retail_matrix_keys: list[str]
    crypto_matrix_keys: list[str]
    required_backtest_counters: list[str]

    @classmethod
    def from_file(cls, path: Path) -> "RuntimeContract":
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        profiles = {name: ProfileContract(**profile) for name, profile in data["profiles"].items()}
        contract = cls(
            report_domains=list(data["report_domains"]),
            domain_aliases=dict(data.get("domain_aliases", {})),
            profiles=profiles,
            completion_requires=list(data["completion_requires"]),
            structural_indicator_ids=list(data["structural_indicator_ids"]),
            retail_matrix_keys=list(data["retail_matrix_keys"]),
            crypto_matrix_keys=list(data["crypto_matrix_keys"]),
            required_backtest_counters=list(data["required_backtest_counters"]),
        )
        contract.validate()
        return contract

    def validate(self) -> None:
        if len(self.report_domains) != len(set(self.report_domains)):
            raise ValueError("report_domains must be unique")
        if set(self.domain_aliases.values()) - set(self.report_domains):
            raise ValueError("domain aliases must map to report_domains")
        if not {"daily_push", "full"}.issubset(self.profiles):
            raise ValueError("daily_push and full profiles are required")
        if not self.structural_indicator_ids:
            raise ValueError("structural indicators are required")
        if not self.retail_matrix_keys or not self.crypto_matrix_keys:
            raise ValueError("retail and crypto matrix keys are required")

    def canonical_domain(self, domain: str) -> str:
        canonical = self.domain_aliases.get(domain, domain)
        if canonical not in self.report_domains:
            raise ValueError(f"unknown report domain: {domain}")
        return canonical

    def profile(self, name: str) -> ProfileContract:
        try:
            return self.profiles[name]
        except KeyError as exc:
            raise ValueError(f"unknown profile: {name}") from exc
