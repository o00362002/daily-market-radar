from __future__ import annotations

from radar.domain.models import Document
from radar.pipeline.domain_classification import classify_documents


def enrich_documents(
    documents: list[Document],
    *,
    canonical_domains: tuple[str, ...] | list[str] | None = None,
    domain_aliases: dict[str, str] | None = None,
) -> list[Document]:
    """Reclassify each article from content, retaining source domain as a weak prior."""

    return classify_documents(
        documents,
        canonical_domains=canonical_domains,
        domain_aliases=domain_aliases,
    )
