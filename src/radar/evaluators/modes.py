"""Deterministic resolution of the four evaluation modes."""

from __future__ import annotations

from dataclasses import dataclass

DETERMINISTIC = "deterministic"
AUTO = "auto"
API_ASSISTED = "api-assisted"
CHAT_ASSISTED = "chat-assisted"

VALID_MODES = (DETERMINISTIC, AUTO, API_ASSISTED, CHAT_ASSISTED)
DEFAULT_MODE = AUTO


@dataclass(frozen=True)
class ResolvedMode:
    effective_mode: str
    use_ai: bool
    degradation_reasons: tuple[str, ...]


def resolve_evaluation_mode(
    requested_mode: str,
    *,
    api_key_available: bool,
    budget_exhausted: bool = False,
) -> ResolvedMode:
    """Map a requested mode + environment to the effective evaluator behaviour.

    - deterministic: never uses AI.
    - auto: uses the API when a key is available, else falls back to deterministic
      with degradation=ai_evaluation_unavailable.
    - api-assisted: requires a key; without one it degrades to deterministic.
    - chat-assisted: the run stays deterministic; the human chat import is a
      separate step (radar import-chat).
    """

    if requested_mode not in VALID_MODES:
        raise ValueError(f"unknown evaluation mode: {requested_mode}")

    if requested_mode == DETERMINISTIC:
        return ResolvedMode(DETERMINISTIC, False, ())

    if requested_mode == CHAT_ASSISTED:
        # The run itself is deterministic; chat enhancement arrives via import-chat.
        return ResolvedMode(DETERMINISTIC, False, ("chat_assisted_pending_import",))

    if budget_exhausted:
        return ResolvedMode(DETERMINISTIC, False, ("ai_budget_exhausted",))

    if not api_key_available:
        return ResolvedMode(DETERMINISTIC, False, ("ai_evaluation_unavailable",))

    return ResolvedMode(requested_mode if requested_mode == API_ASSISTED else AUTO, True, ())
