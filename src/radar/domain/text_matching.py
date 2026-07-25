from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable


def normalize_for_matching(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").lower().strip()
    return re.sub(r"\s+", " ", normalized)


def contains_term(text: str, term: str) -> bool:
    """Match phrases without allowing short ASCII terms inside unrelated words.

    CJK phrases continue to use substring matching. ASCII terms use alphanumeric
    boundaries, so ``ai`` no longer matches ``raise`` and ``api`` no longer
    matches ``capital``.
    """

    normalized_text = normalize_for_matching(text)
    normalized_term = normalize_for_matching(term)
    if not normalized_term:
        return False
    if normalized_term.isascii():
        pattern = re.escape(normalized_term).replace(r"\ ", r"\s+")
        return re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", normalized_text) is not None
    return normalized_term in normalized_text


def matching_terms(text: str, terms: Iterable[str]) -> tuple[str, ...]:
    return tuple(term for term in terms if contains_term(text, term))
