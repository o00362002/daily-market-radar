from __future__ import annotations

from radar.domain.models import Document


def deduplicate_documents(documents: list[Document]) -> list[Document]:
    seen: set[tuple[str, str]] = set()
    unique: list[Document] = []
    for document in documents:
        key = (document.url, document.title_hash)
        if key in seen:
            continue
        seen.add(key)
        unique.append(document)
    return unique
