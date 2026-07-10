from __future__ import annotations

from radar.domain.models import Document, canonicalize_url


def normalize_documents(documents: list[Document]) -> list[Document]:
    return [Document.fixture(**{**document.__dict__, "url": canonicalize_url(document.url)}) for document in documents]
