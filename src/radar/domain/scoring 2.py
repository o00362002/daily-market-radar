from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreBreakdown:
    score: int
    components: dict[str, int]
    rationale: str
    counterevidence: list[str]

    def validate(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError(f"score out of range: {self.score}")
        for name, value in self.components.items():
            if not 0 <= value <= 100:
                raise ValueError(f"component {name} out of range: {value}")


def weighted_score(components: dict[str, int], weights: dict[str, float]) -> int:
    if not components:
        return 0
    total_weight = sum(weights.get(name, 1.0) for name in components)
    if total_weight <= 0:
        raise ValueError("total weight must be positive")
    total = sum(value * weights.get(name, 1.0) for name, value in components.items())
    return round(total / total_weight)
